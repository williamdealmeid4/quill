# Integração com Codex

Especificação v1 — 2026-11-11. CLI observada localmente: 0.167.1. Ajuda local confirmou exec, app-server, login status e geração de JSON Schema. Nenhuma tarefa de agente foi iniciada na preparação destes documentos.

## Backend e contrato de compatibilidade

App Server via stdio é o único backend de execução interativa do MVP. CLI exec é uma alternativa documental para jobs pontuais; não implementar fallback automático, especialmente se faltar sandbox/aprovação no backend principal.

Contrato externo pertence ao Codex; contrato interno pertence a [ARCHITECTURE.md](ARCHITECTURE.md). Q006 deve gerar schema, guardar versão/digest e mapear os campos realmente presentes. Não escrever mensagens só a partir de exemplos de internet. Atualização do Codex exige repetir testes de contrato e segurança antes de aceitar a nova versão.

Comandos confirmados pela ajuda instalada:

```text
codex --version
codex login status
codex app-server --listen stdio://
codex app-server generate-json-schema --out <diretório-controlado>
codex exec --json --sandbox read-only -C <workspace> -
```

O último exemplo demonstra execução não interativa de leitura; '-' recebe prompt por stdin. Não é a receita completa de perfil seguro do Quill. exec também documenta output-schema e resume; validar help da suboperação antes de usá-los. Não presumir que exec fornece callbacks de aprovação equivalentes ao App Server.

## Gate Q006

Criar schemas/codex/<versão>/ a partir do gerador estável, sem --experimental, e manifest.json com cli_version, generator_argv, generated_at, hashes e tabela de métodos/campos exigidos. Armazenar fixtures JSON redigidas, sem conversas pessoais. Comparar mudanças de schema, não só número da versão.

Matriz mínima a validar: initialize/initialized, modelo disponível com low, estado de autenticação, criar/retomar thread, iniciar/interromper turno, eventos de texto/itens/terminal, requests de aprovação e política de leitura/escrita/rede. Provar que configurações pessoais de plugins/MCP/hooks não ficam habilitadas sem autorização. Não editar config global para conseguir isso.

Se método/campo necessário não existir, encerrar Q006 como blocked com versão, evidência e requisito. Não escolher transporte experimental nem inventar flag. Mudança de arquitetura exige atualizar documentos antes de retomar execução.

## Lifecycle

1. Localizar executável com shutil.which; validar arquivo executável, versão e path canônico.
2. Consultar login status; não abrir auth.json. Falha → AUTH_REQUIRED com instrução para login pelo terminal próprio.
3. Preparar perfil por invocação documentado, preservando auth e requisitos gerenciados, sem herdar ferramentas externas não autorizadas.
4. Iniciar processo supervisionado com argv, cwd controlado, stdio pipes e env allowlist. Não usar PTY para protocolo.
5. Enviar initialize identificando quill e capabilities estáveis; aguardar resposta, então initialized.
6. Consultar catálogo de modelos; UI escolhe Sol disponível que suporte low e persiste ID. Múltiplos Sol exigem seleção explícita na configuração; não escolher por substring e não substituir silenciosamente.
7. Criar thread vinculada a workspace, modo e perfil; retomar apenas thread compatível, nunca a “última” global.
8. Iniciar turno e ler stdout continuamente, enquanto stderr é drenado e redigido em canal separado.
9. Resolver requests de aprovação pelo Permission Manager.
10. Aguardar estado terminal e verificar resultado por diff/testes; exit code do processo não representa sucesso da tarefa.
11. Encerrar na saída/cancelamento; guardar referências necessárias ao histórico.

Mapear execution_id interno para thread_id/turn_id externo; nunca aceitar evento de outra execução como conclusão. Thread retomada não muda workspace silenciosamente. Sem auto-resume após crash: primeiro reconciliar estado e pedir nova instrução.

## Transporte

Mensagens são JSON por linha em stdio; separar requests com id, responses e notifications. Usar buffer incremental UTF-8 que suporte fragmentação entre bytes de caractere e múltiplas linhas por read. stdout não é log. stderr não pode bloquear o leitor.

IDs de request inteiros crescentes por conexão; mapa Future por id. Respostas podem chegar fora de ordem. Linha máxima 8 MiB e parsing estrito; mensagem inválida fecha transporte com PROTOCOL_INCOMPATIBLE. IDs desconhecidos são erro de protocolo registrado, não nova execução. Notificação desconhecida pode ser ignorada com metadado redigido; request desconhecido recebe resposta de erro compatível, sem efeito.

Timeout inicial 15 s; controle RPC 30 s. Turno pode durar até deadline de 20 min. Timeout em start depois do envio pode ter criado turno: reconciliar ou marcar interrupted, nunca reenviar automaticamente. Desconexão durante side effect deixa resultado incerto.

## Políticas por execução

| Modo Quill | Intenção de política Codex |
|---|---|
| read | Leitura restrita de snapshot + runtime; nenhuma escrita em origem/workspace |
| assisted | Escrita limitada a snapshot/tmp privado; leitura restrita; rede de comandos negada |
| restricted_auto | Mesmos limites; grants não ampliam o sandbox automaticamente |

Os nomes exatos de campos vêm do schema da CLI. A documentação atual descreve restricted read access; a implementação precisa comprovar sua aplicação real às ferramentas habilitadas. Defaults full read não atendem ao projeto. Escalada de sandbox é negada no MVP; nova necessidade pede uma nova tarefa/escopo aprovado, nunca accept incondicional.

Não passar dangerFullAccess ou externalSandbox para evitar erro. Não habilitar auto-review ou acceptForSession como política do Quill. Aprovação de ferramenta desktop e aprovação Codex são namespaces diferentes e não se autorizam mutuamente.

## Aprovações e tool plans

Eventos de pedido são associados a connection/thread/turn/item/request. Normalizar ActionRequest com recursos, digest e expiração. UI mostra comando/cwd/efeitos ou diff, conforme tipo. Resposta tardia de execução encerrada é descartada; expiração/cancelamento resulta em decisão de negação/cancelamento suportada pelo schema. Não aprovar rede por confundir host com comando.

Para automação do desktop, um turno de planejamento de leitura produz JSON final validado pelo schema local:

```json
{
  "schema_version": 1,
  "summary": "Criar a pasta Relatorios",
  "actions": [
    {"tool": "files.mkdir", "arguments": {"root_id": "<uuid>", "relative_path": "Relatorios"}}
  ],
  "done": false
}
```

Plano aceita no máximo cinco ações propostas; executa uma por vez com política e recursos atuais. ToolRegistry define schemas concretos por nome; additionalProperties=false em todos os níveis. Root ID é escolhido pelo usuário, não caminho livre inferido pelo modelo. Dados de ações jamais são avaliados como Python/shell.

Resultado é enviado ao turno seguinte como dado de ferramenta por campo suportado pelo schema; quando não houver tal campo estável, envelope de texto rotulado como dado, sem instrução adicional e sem ampliar privilégio. Limite oito ciclos e detecção de repetição; plano inválido falha VALIDATION_FAILED, sem “consertar” comando por heurística. Não depender de dynamicTools experimental.

## Normalização de eventos

| Entrada do adaptador | Evento interno | Regra |
|---|---|---|
| Texto incremental | execution.output | Coalescer para UI, manter sequência |
| Item/progresso | execution.progress | Identificar ferramenta sem expor segredo |
| Pedido de aprovação | approval.requested | Esperar decisão específica da execução |
| Item terminal | tool.completed | Estado do item não conclui turno |
| Turno terminal positivo | execution.completed | Só inicia verificação; não prova testes |
| Erro terminal | execution.failed | ErrorInfo com código seguro |
| Interrupção confirmada | task.state_changed | cancelled após reconciliar processos |

Resultado final interno inclui execution_id, terminal_status, summary, changeset_id opcional e VerificationEvidence. Esquema final do modelo pode listar hipóteses/testes, mas arquivos alterados e exit codes são coletados independentemente. Não confiar em “corrigido” na narrativa.

## Cancelamento, processos e loops

Q024/Q025 usam transportes fake/injetados. Q027 introduz supervisor nativo. Nenhum fluxo real que inicie comandos fica disponível na UI antes de Q027/Q028, mesmo que adaptador passe em fake.

Cancelar: interromper turno pelo método confirmado → esperar até 5 s → encerrar processo supervisionado → até 3 s → forçar árvore. Drain de stdout/stderr até EOF ou limite. Marcar interrupted se estado final não foi confirmado. Preservar workspace e journal para inspeção.

POSIX: start_new_session e grupo de processo; Windows: Job Object com kill-on-close e criação/associação antes de permitir filhos. Testar executores auxiliares do Codex; não assumir que grupos do processo pai abrangem automaticamente todo daemon. Se o Codex usar daemon fora da árvore, impedir esse caminho ou bloquear até comprovar controle.

Proibir Codex recursivo, Quill recursivo e delegação automática. Perfil de ferramentas e sandbox precisam tornar essa regra efetiva. Variável QUILL_EXECUTION_ID auxilia correlação, mas não é controle de segurança. Não registrar tokens nem copiar ambiente inteiro.

## Falhas e recuperação

- Executável ausente: chat local/mascote/histórico permanecem; execução desabilitada.
- Auth expirada/modelo indisponível: mostrar ação necessária, sem login automático por captura de senha.
- Sandbox/versão incompatível: fail closed, sem modo degradado irrestrito.
- Usage limit/503: registrar erro e permitir nova tentativa explícita após reconciliar; não duplicar submissão.
- Crash/timeout: preservar execução interrompida e workspace; não relançar comandos.
- Schema novo: rodar contrato e testes negativos em ambiente fixture antes de atualizar manifest aceito.

## Fontes

Consultadas em 2026-11-11: [App Server](https://learn.chatgpt.com/docs/app-server), [modo não interativo](https://learn.chatgpt.com/docs/non-interactive-mode), [segurança e aprovações](https://learn.chatgpt.com/docs/agent-approvals-security), [sandbox Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox). A ajuda local da versão disponível é a confirmação de flags; a captura de schemas em Q006 é requisito antes de implementar wire payloads.


## Evidência da primeira execução — Q006 bloqueada

Captura real do Codex 0.167.1: 322 arquivos JSON gerados sem --experimental em schemas/codex/0.167.1; manifest.json registra hashes e métodos. Inspeção de versão/login confirmou autenticação ativa, sem iniciar thread/turno, copiar tokens ou alterar configuração global.

| Controle do contrato planejado | Resultado da captura |
|---|---|
| readOnly.access | Ausente: variante expõe apenas type/networkAccess |
| workspaceWrite.readOnlyAccess | Ausente: variante expõe type/networkAccess/writableRoots e exclusões tmp |
| readableRoots/readable_roots nas definições exportadas | Nenhuma ocorrência |
| Metodologia de perfil estável prevista no plano | Não comprovada para restrição de leitura |
| Alternativa por permission profiles | CLI sandbox oferece -P/--permission-profile; documentação oficial classifica o recurso como beta |

Essa evidência não significa que o Codex não possua nenhuma proteção de leitura: significa que **o contrato estável escolhido para o Quill não expõe os controles previstos**. A configuração livre por thread não é prova de que uma chave inventada será suportada. Os perfis beta não foram ativados porque o planejamento proíbe dependência experimental no MVP.

O inspector devolve sandbox.available=false e motivo explícito; não inicia agente nem consulta catálogo live enquanto esse gate estiver fechado. Os modelos nos testes são sintéticos, não uma lista de acesso da conta.

Procedimento de desbloqueio revisável: escolher entre (A) revisar Q006–Q008 para usar permission profiles beta com configuração apenas por processo, manter proibição de bypass e executar os mesmos probes negativos; (B) certificar uma versão do Codex cujo schema estável implemente o contrato, sem atualização global automática; ou (C) desenhar isolamento externo específico por SO. Nenhuma dessas alternativas está implementada/autorizada como mudança arquitetural nesta execução. Até a decisão, Q006 permanece blocked e Q007–Q043 não são iniciadas conforme ordem estrita do plano.

Fonte verificada em 2026-11-11: [Permissions — beta permission profiles](https://learn.chatgpt.com/docs/permissions). Não atribuir capacidades da documentação mais recente à CLI instalada sem teste.
