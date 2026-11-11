# Segurança do Quill

Especificação v1 — 2026-11-11. Política canônica; controles planejados ainda não implementados. [Arquitetura](ARCHITECTURE.md), [integração Codex](CODEX_INTEGRATION.md) e [testes](TESTING.md) complementam este documento.

## Modelo de ameaças

Proteger projetos originais, diretórios pessoais, credenciais, histórico, desktop e aplicações contra ações indevidas do agente ou conteúdo malicioso lido por ele. Fontes não confiáveis: prompts, repositórios, arquivos de instruções, logs, páginas, nomes de arquivos, respostas de ferramentas e resultados do modelo.

O usuário local e os binários instalados de Quill/Codex/Qt são a base confiável. Malware já executando como o mesmo usuário, sistema comprometido, extensão GNOME maliciosa e provedor comprometido estão fora da garantia. D-Bus da sessão não isola processos igualmente privilegiados do usuário. Esses limites devem constar na documentação de release.

Prompt injection pode induzir propostas ruins mesmo com filtros. A proteção é limitar o que uma proposta consegue executar e quais dados o processo consegue ler; não afirmar prevenção completa por mensagem de sistema.

## Fronteiras

1. Texto do modelo → schema → política Python → recurso validado → execução.
2. Codex/comandos de projeto → sandbox com leitura/escrita/rede delimitadas.
3. Snapshot → diff → aprovação vinculada → journal fora do sandbox → origem.
4. Extensão GNOME → D-Bus limitado → intenção sem autoridade.
5. UI → consentimento explícito → grant persistido e revogável.
6. Histórico/logs → redação, diretório privado e retenção.

Níveis de risco: low=consulta delimitada; medium=efeito reversível/lançamento; high=execução de código, envio externo ou alteração de projeto original. Tipo de ferramenta é um piso: argumentos e recursos podem elevar o risco, nunca reduzi-lo.

## Modos e consentimento

| Modo | Codex | Ferramentas desktop | Origem |
|---|---|---|---|
| read | Snapshot somente leitura, raízes restritas; sem comandos que precisem escrever | Consultas em recursos autorizados | Não modifica |
| assisted | Escopo aprovado permite escrita só no workspace; escaladas rejeitadas por padrão | Cada efeito concreto pede aprovação | Aplicação de changeset exige aprovação própria |
| restricted_auto | Mesmo sandbox; orçamento e escopo explicitamente concedidos | Somente grants exatos/pré-autorizados, dentro de quotas | Não aplica código automaticamente no MVP |

Leitura não impede persistência interna do Quill. Rodar pytest geralmente escreve cache: propor migração para assisted com workspace em vez de relaxar read sem consentimento.

Grant inclui id, tarefa, modo, ferramenta/efeito, recursos canônicos, hash dos argumentos quando aplicável, prazo, contador e limite. No automático: prazo máximo padrão 30 min, até 20 ações, encerrando no fim da tarefa. Grants de diretório para listar/criar/mover são diferentes. Não autorizar uma árvore pessoal inteira como default.

Aprovação mostra efeito, recursos, argumentos completos e normalizados, cwd, rede e consequência conhecida. Sempre oferecer negar/cancelar. Timeout 5 min nega. Alterar qualquer argumento/resource/digest exige nova aprovação. Não responder acceptForSession por conveniência. Consentimento para código de projeto inclui executar código não confiável no sandbox e possíveis comandos de teste; não inclui sair do sandbox, ler segredos ou habilitar rede.

Operações privilegiadas, exclusão permanente, alteração de ACL e segurança do sistema ficam indisponíveis no MVP, mesmo quando propostas. Deploy, publicação, envio de e-mail, compras e compartilhamento externo não são ferramentas iniciais.

## Sandbox e configurações herdadas

Q006 confirma a versão e campos do protocolo. Q007/Q008 comprovam leitura externa negada, escrita externa negada, rede de comando bloqueada e limpeza dos processos filhos. Se qualquer requisito falhar, retornar SANDBOX_UNAVAILABLE e impedir início de comandos; chat/histórico/avatar continuam disponíveis.

Não usar danger-full-access, bypass, externalSandbox sem isolamento externo implementado, sudo ou prompt como substituto de limite do SO. Não considerar workspace-write seguro para leitura sem restringir readable roots. Incluir só runtime/ferramentas necessários e o workspace; diretórios pessoais, credenciais e origem não são readable roots de comandos.

Sandbox de comandos e processo hospedeiro do Codex são fronteiras distintas. Desabilitar caminhos alternativos de leitura, plugins, MCP, ferramentas de filesystem fora da política e serviços herdados. Q006 deve demonstrar como a versão instalada aplica a política a todas as ferramentas habilitadas. Se leitura fora da política continuar possível, bloquear e registrar necessidade de isolamento adicional em vez de declarar segurança com apenas um teste de shell.

Antes de iniciar integração: inventariar config efetiva e requisitos gerenciados, sobrepor apenas configuração suportada por processo para desabilitar ferramentas externas não autorizadas e registrar digest do perfil. Não carregar config do projeto de origem nem copiar .codex, .agents ou .git para o snapshot. Instruções versionadas relevantes podem ser exibidas como dados, nunca autoridade para ampliar privilégios. Config gerenciada do administrador não é contornada.

Autenticação é do Codex; não copiar auth.json, tokens ou CODEX_HOME. Perfil por invocação deve usar recursos documentados da versão sem quebrar autenticação. Se não for possível isolar ferramentas herdadas mantendo auth legítima, interromper em Q006. Não inventar uma flag inexistente.

Rede para o provedor Codex é diferente da rede de subprocessos. A primeira precisa estar disponível e ser informada ao usuário; a segunda é negada por padrão. Instalar dependências/downloads é uma ação separada com destino e escopo aprovados. O usuário não concede rede irrestrita por pedir diagnóstico.

## Paths, links e arquivos

- Usar operações com Path e validação de containment por componentes; nunca startswith textual.
- Revalidar raiz e pais imediatamente antes da ação.
- POSIX: lstat, descritores relativos e no-follow para operações mutantes onde disponíveis.
- Windows: rejeitar reparse points/junctions em recursos mutáveis não comprovadamente seguros; detectar UNC, device paths, ADS e diferenças de case. MVP não organiza caminhos de rede.
- Negar symlink ou hardlink externo; não preservar hardlinks na cópia.
- Recusar sockets, dispositivos, FIFO e diretórios .git/.codex/.agents, além de exclusões sensíveis.
- Arquivos novos usam criação exclusiva; mover não sobrescreve destino e não atravessa volumes no MVP.
- Detectar normalização/case collision ao preparar snapshot e changeset; bloquear antes da execução/aplicação.

Validação de caminho sozinha tem TOCTOU. Operações mutantes devem usar handles seguros na plataforma; quando não for possível eliminar a janela de corrida, negar aquela operação em vez de fazer fallback inseguro.

Excluir do snapshot: .env e .env.*, *.pem, *.key, *.p12, *.pfx, credenciais conhecidas, auth.json, diretórios .ssh/.gnupg, caches de build e dependências. A lista é defesa auxiliar, não detector perfeito de segredos. Rastreado no Git não significa não sensível. Mostrar relatório de exclusões e obter escopo de envio; permitir inclusão manual somente de arquivos não secretos, com nova revisão. Arquivos sem extensão podem conter segredos: usuário deve revisar o escopo, e redação não garante detecção total.

Limites: 20.000 arquivos/1 GiB por snapshot, 20 MiB por arquivo; exceder limites agregados bloqueia, arquivo individual excluído aparece no relatório. Arquivos não rastreados só entram por seleção explícita. Submódulos e Git LFS não materializados geram impedimento, sem fetch implícito. Projetos não Git são futuros.

## Snapshot e aplicação segura

Não usar worktree compartilhando .git da origem. Enumerar arquivos com Git em modo sem hooks/fsmonitor externos, caminhos delimitados por NUL, argumentos como lista e ambiente saneado. Copiar bytes do estado atual, incluindo staged e unstaged como conteúdo de trabalho; não preservar o índice como estado a ser alterado pelo agente. Arquivo rastreado ausente representa deleção na baseline e não é recriado.

Criar Git independente no snapshot com configuração neutra, sem remotes/hooks/assinatura, e commit de baseline com identidade técnica local. Isso não é um commit no projeto do usuário. Registrar hashes fora da área visível ao agente.

Changeset compara bytes finais com baseline; rastrear novos arquivos e deleções. Diff é apresentação; manifesto de hashes define o conteúdo aprovado. Renomes são deleção+adição na v1. Binários exigem aprovação com tamanho/hash e indicação de ausência de diff textual. Não criar chmod perigoso, setuid ou links pelo changeset.

Aplicação em duas fases:

1. Validar autorização, digest, recursos, hashes atuais e ausência de colisões.
2. Criar journal e backups de todos os afetados fora do workspace.
3. Preparar temporários no mesmo volume do destino e fsync quando disponível.
4. Substituir por arquivo, registrando cada etapa; não prometer transação atômica de múltiplos arquivos.
5. Se falhar, recuperar somente quando o arquivo atual ainda corresponde ao conteúdo aplicado pelo Quill.
6. Divergência durante recuperação vira RECOVERY_REQUIRED, com lista de conflitos e backups preservados.

Original ausente precisa continuar ausente para adição; arquivo removido precisa manter o hash aprovado. Origem alterada pede novo snapshot/revisão. Nunca usar reset --hard, clean, checkout forçado ou aplicar patch com fuzz silencioso. Índice Git do usuário permanece intocado.

## Ferramentas e terminal

Registro fechado, schemas com additionalProperties=false, limites e IDs versionados. Modelo produz proposta, não autorização. Toda tool call gera audit start/decision/result com digest e resources; args sensíveis não são logados.

Consultas de processo não coletam env, cmdline com tokens nem memória. Matar processo não integra a ferramenta inicial. Abrir aplicativo resolve ID cadastrado em runtime; não aceitar “nome” como comando shell. No Linux usar desktop ID validado e launcher do ambiente; Windows executável cadastrado/canonicalizado com argv fixo. Catálogo de apps é dado não confiável até validado pelo usuário.

Terminal executa argv revisável via sandbox e sem shell=True; interpretadores e scripts são execução de código e seguem o mesmo sandbox. Denylist de rm/sudo é insuficiente e não será a fronteira. Análise de logs tem limite 1 MiB por consulta e redação antes de enviar ao modelo.

Browser futuro usa perfil descartável sem cookies pessoais. Envio de formulários, login, download e acesso a arquivo local exigem permissões específicas. Não instalar extensão de navegador com acesso global como atalho.

## Segredos, logs e retenção

Não armazenar senhas/tokens no SQLite, TOML, repositório ou logs. O Quill não precisa de segredo próprio no MVP. Se surgir credencial de integração futura, usar credential store nativo via serviço dedicado e bloquear se indisponível, sem fallback para texto puro.

Filtrar redaction antes de persistir, exibir, exportar e enviar resultados de ferramentas. Tests incluem padrões de token, Authorization, cookies, URLs com segredo e variáveis; não registrar segredos reais durante validação. Redação é best effort; coletar o mínimo é o controle primário. Conversas são dados pessoais em diretório privado, não criptografia em repouso garantida. Recomendar uso do disco criptografado no guia operacional, sem afirmar criptografia SQLite.

Auditoria local é operacional e não à prova de adulteração por processo do mesmo usuário. Logs rotacionam 10 MiB × 5, expiram em 14 dias; histórico 90 dias; workspaces concluídos 7 dias. Preservar changesets não aplicados, backups com conflito e investigações em andamento. Exportação de logs é sempre explícita e redigida.

## Loops, recursos e processos

Uma tarefa ativa; 8 ciclos de planejamento; segunda proposta idêntica sem progresso encerra blocked. Não usar retries automáticos após ação incerta. Ferramentas não podem lançar Codex como subagente, importar o próprio orquestrador nem iniciar instância do Quill. PID e variável de ambiente são defesa auxiliar, não contenção.

Q007/Q008 verificam a prevenção efetiva de executores recursivos e rotas alternativas de ferramenta. Falha exige impedimento de segurança; não basta escrever “não execute Codex” no prompt. Restrições de executáveis devem considerar interpretadores/cópias, não apenas o nome codex.

Processos do Quill são supervisionados em grupos POSIX/Job Objects Windows. Testes precisam abranger o app-server e os subprocessos de executor que ele inicia. Nunca varrer/matar por nome de processo; usar ownership, PID+creation time e handles mantidos pelo supervisor. Recuperação no startup não mata PID reaproveitado.

Sem hard cap universal de RAM anunciado: detectar cgroups/limites nativos disponíveis, monitorar via psutil e cancelar por RESOURCE_LIMIT ao exceder orçamento configurado. Monitoramento não protege de todo pico de RAM. Sessão não pode reivindicar quota rígida se o kernel não a aplicou.

## Checklist de aceitação

- Q007/Q008: recursos sentinela externos inacessíveis e rede local de teste bloqueada.
- Q019/Q020/Q026: negação, timeout, revogação, argumento alterado e request desconhecido não executam efeito.
- Q021/Q032: links, junctions, traversal, arquivos especiais e corrida de path tratados.
- Q023: origem concorrente e recuperação parcial preservam dados.
- Q027/Q028: cancelar, fechar e reiniciar não deixam trabalho executando/repetido.
- Q030: ferramenta desconhecida e loop não ampliam o registro.
- Q035: nenhum fluxo contorna essas verificações no MVP.

## Fontes

Consultadas em 2026-11-11: [Codex approvals/security](https://learn.chatgpt.com/docs/agent-approvals-security), [sandbox Windows](https://learn.chatgpt.com/docs/windows/windows-sandbox), [XDG RemoteDesktop](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html). Políticas e limites numéricos acima são decisões do Quill, não garantias fornecidas por essas bibliotecas.


## Revisão autorizada — perfis de permissão beta

Em 2026-11-11, o usuário autorizou revisar Q006–Q008 para perfis beta, mantendo configuração apenas por processo e todos os testes de isolamento. A exceção é restrita a initialize.capabilities.experimentalApi, permissions/runtimeWorkspaceRoots em thread/start, thread/resume e turn/start, além de command/exec.permissionProfile. Demais APIs experimentais continuam proibidas.

O contrato beta é capturado com hashes em schemas/codex/0.167.1/permissions-beta. Contrato aprovado não comprova sandbox: available/restricted_read/bounded_write continuam falsos até probes nativos. Não combinar permissions com sandbox/sandboxPolicy legados. Perfil tem nome único por execução: :minimal e runtime canônico read, somente workspace read/write conforme modo, network.enabled=false. Config global e credenciais não são copiadas nem alteradas.

Probe documentado: codex sandbox -P <perfil> --include-managed-config -C <workspace>, com permissions.<perfil> via -c. Seleção explícita será verificada por sentinelas, sem presumir que default_permissions sobrepõe sandbox_mode antigo. App Server seleciona perfil no request e não envia política legada no mesmo request. Q008 continua exigindo Windows nativo.

O usuário também autorizou etapas sucessivas, cada uma validada e commitada separadamente, substituindo a parada inicial após uma tarefa. Os gates de segurança e plataforma permanecem. O bloqueio anterior é histórico e será atualizado com evidências. Fonte: [Permissions](https://learn.chatgpt.com/docs/permissions), consultada nesta revisão.
