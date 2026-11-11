# Plano de implementação do Quill

**Execução:** uma tarefa por solicitação, pelo modelo Sol disponível com esforço low. Não usar execução automática de ondas nem delegação paralela como default.

**Objetivo:** entregar assistente desktop com mascote, programação isolada e ferramentas consentidas em Linux GNOME/Wayland e Windows 11.

**Arquitetura:** monólito modular Python/PySide6, QML, extensão GNOME de apresentação, Codex App Server stdio, SQLite e adaptadores nativos.

**Stack:** Python 3.13, uv, PySide6 6.12, sqlite3, jsonschema, psutil, pytest, Ruff e mypy. Dependências entram na tarefa consumidora.

**Especificação:** [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [AVATAR_DESIGN.md](AVATAR_DESIGN.md), [CODEX_INTEGRATION.md](CODEX_INTEGRATION.md).

Versão 1 — 2026-11-11. O aplicativo não existe nesta entrega. O backlog canônico é [TASKS.md](TASKS.md).

## Restrições globais

- MVP suporta Manjaro x86_64 GNOME 50/Wayland e Windows 11 x86_64, ambos com validação nativa.
- Núcleo portátil não significa garantia em todos os sistemas. macOS é posterior.
- Código de projeto executa em snapshot e sandbox; origem só muda após revisão/aprovação.
- Somente uma tarefa ativa, uma execução por submissão, um turno por thread.
- Nenhuma credencial ou dado real dentro do repositório público.
- Nenhum shell=True, sudo, bypass de sandbox ou mudança de configuração global do Codex.
- Qt main thread só apresenta; execução e armazenamento fora dela.
- Texto do modelo e arquivos de terceiros não são autoridade de permissão.
- Não adicionar dependências, caminhos ou subsistemas fora da tarefa sem registrar mudança de plano.
- Toda conclusão depende de evidência; skip e teste fake não certificam plataforma real.

## Pontos de revisão obrigatória

| Falha previsível | Tarefa proprietária e evidência |
|---|---|
| Arquivo muda enquanto diff aguarda aprovação | Q023: hash atual divergente bloqueia, sem escrita |
| Approval chega depois do cancelamento | Q020/Q026: decisão tardia sem efeito e request resolvida |
| Codex mantém executor auxiliar após fechar | Q027: teste de árvore real nas duas plataformas |
| Manifest/arquivo tenta sair do diretório | Q010/Q021/Q032: containment, links e reparse points |
| Extensão desabilita durante tarefa | Q013/Q015/Q017: fallback sem cancelar execução/duplicar mascot |

## Sequência, dependências e entregas

Os IDs são estáveis. Cada tarefa no backlog enumera dependências explícitas. A ordem operacional é numérica: não iniciar Q009 enquanto Q008 estiver bloqueada sem alteração autorizada do plano. Trabalho manual Windows é parte real da sequência, não substituível por mocks Linux.

| Fase | Tarefas | Resultado testável / gate |
|---|---|---|
| 1 — Fundação | Q001–Q005 | CLI reproduzível, config, logs redigidos, contratos e banco temporário |
| 2 — Viabilidade | Q006–Q009 | Wire schema registrado, isolamento negativo Linux/Windows e janela Qt funcional |
| 3 — Avatar | Q010–Q017 | Mascote renderizado por Qt/GNOME, posição, menu e backend por capacidades |
| 4 — Chat | Q018–Q020 | Histórico fixture, submissão única e permissões determinísticas |
| 5 — Codex/orquestração | Q021–Q029 | Snapshot, diff aprovado, Codex normalizado, cancelamento e recuperação |
| 6 — Ferramentas/MVP | Q030–Q035 | Código e desktop com segurança e teste completo nas duas plataformas |
| 7 — Refinamento | Q036–Q038 | Acessibilidade, configurações, histórico, notificações, autostart e navegador isolado |
| 8 — Voz | Q039–Q041 | Captura consentida, voz offline e ativação opcional |
| 9 — Distribuição | Q042–Q043 | Builds nativos, checksums, licenças e atualização manual verificável |

## Receita de cada tarefa

1. Ler os quatro documentos obrigatórios por inteiro e as referências da tarefa.
2. Inspecionar Git; preservar alterações anteriores. Registrar base e caminhos da tarefa.
3. Checar dependências e recursos nativos; marcar in_progress.
4. Para lógica backend, escrever os testes especificados, observar falha esperada e implementar o mínimo para passar. Para UI, usar fixture e verificar comportamento real sem criar testes que só repetem props.
5. Introduzir dependência somente quando indicada; atualizar pyproject e lockfile juntos.
6. Rodar teste específico, Ruff, formato, mypy e suíte aplicável. Não repetir/broaden sem motivo.
7. Fazer revisão do diff contra contrato, segurança e cenários de falha.
8. Registrar resultados em TASKS.md. Se concluída, um commit focado; não fazer push futuro sem autorização da sessão.
9. Informar próxima tarefa e parar.

Unidades muito grandes descobertas durante execução não podem ser improvisadas: dividir documentalmente preservando dependências, revisar a mudança e só depois implementar a subunidade autorizada.

## Fase 1: detalhes e baseline

Q001 cria pacote quill 0.1.0 com Hatchling, Python >=3.13,<3.14 e .python-version=3.13. Não instalar Qt, Codex SDK ou dependências de fase futura. Dev group: pytest, ruff e mypy, versões resolvidas e fixadas pelo uv.lock. Mypy strict; Ruff target py313, line-length=100, select E/F/I/UP/B/SIM; formatador Ruff. Testes subprocesso validam --version/help/argumento inválido. Sem CLI que cria pastas ao consultar versão.

Q002 introduz platformdirs e AppConfig do contrato; limites de avatar/task_timeout, modo read default e grants vazios. Q003 logging redigido antes de handler. Q004 fecha DTOs, protocolos, erros e transições; não implementar serviço futuro sob pretexto de scaffolding. Q005 cria migração inicial única e store com transações/compare-and-set.

## Fase 2: interromper cedo incompatibilidades

Q006 é inspeção técnica e fixtures de protocolo, sem tarefa agente real. Gerar schema com CLI instalada e registrar metadados. Perfil por invocação, auth e ferramentas habilitadas precisam de evidência. Se algum controle só existir em API experimental, bloquear e descrever a lacuna.

Q007 e Q008 executam probes explícitos em ambientes descartáveis com opt-in. Confirmar restrições de leitura, escrita e rede, inclusive rotas de ferramentas que não usem shell, e controle sobre filhos/recursão. Até Q027, o probe usa harness temporário com finally e cleanup; não habilita execução real na UI. Um sandbox indisponível não causa instalação administrativa automática.

Q009 cria aplicação Qt e ExecutionWorker sem executar Codex real. Qt 6.12/Python 3.13 precisam instalar e abrir em Linux e Windows; resolver patch compatível no lock e registrar versão. Sem pin não verificado.

## Fases 3–4: interação sem autoridade implícita

Q010 introduz asset fixture técnico e schemas; arte final é uma dependência de release visual, não de desenho da arquitetura. Q011 produz estados previsíveis. Q012 usa renderer Qt. Q013 define D-Bus e QtDBus; Q014/Q015 adicionam extensão, callbacks e renderer GJS. Q016 valida Win32; Q017 seleciona backend. Toda ferramenta de shell da extensão é proibida.

Q018 conecta conversa a fila fake, não Codex real. Q019/Q020 aplicam os três modos com decisões determinísticas. UI nunca deriva grant de um texto “sim” em histórico que não esteja associado ao pedido de aprovação atual.

## Fase 5: cadeia de programação

Q021 faz snapshot sem compartilhar .git e preserva conteúdo local. Q022 produz ChangeSet independente da narrativa do agente. Q023 aplica somente manifesto aprovado com revalidação/journal. Q024/Q025 implementam transporte e executor com fake. Q026 integra requests de aprovação. Q027 supervisiona processos nativos; Q028 liga fila, executor, políticas e recuperação. Q029 disponibiliza execução real no painel somente após esses gates.

Código de teste fixture de erro 401 deve ser local e determinístico: cabeçalho Authorization omitido por adaptador de cliente, transporte HTTP fake que exige Bearer de teste. Não iniciar serviço público nem usar credencial real. Teste mostra falha, correção e regressão sem rede externa.

## Fase 6: desktop e MVP

Q030 plano JSON com registry fechado; Q031 consulta processos; Q032 arquivos com operações seguras; Q033 apps cadastrados; Q034 logs/terminal delimitados. Terminal usa sandbox do executor em workspace, não comando host genérico.

Q035 testa narrativa completa: pedido → escopo → snapshot → Codex → verificação → diff → aprovação → origem. Separadamente, automatiza mkdir/move e abrir app cadastrado com confirmação, além de consulta de processos. O mesmo fluxo exige Linux e Windows reais. Somente resultado fixture fake não conclui MVP.

## Fases 7–9 e compatibilidade

Refinamento não pode relaxar controles para reduzir cliques. Autostart é opt-in e não executa tarefas antigas. Navegador tem perfil isolado, sem cookies pessoais. Voice é dependência externa opcional; licença/download/checksum documentados antes de distribuir. Build nativo inclui QML/assets/metadata da extensão, nunca dados de usuário.

Atualização v1 é manual: manifest/checksum e aviso de versão, download iniciado pelo usuário e instalação documentada. Não criar self-updater privilegiado. Migração de banco tem backup e bloqueio em erro; manter pacote anterior permite rollback de binário, sem downgrade automático de schema. Builds não assinados aparecem como não assinados; não prometer remover SmartScreen sem assinatura.

macOS requer desenho específico de permissões, janela, sandbox Codex, notarização e CI/hardware antes de receber status supported. Criar esse planejamento somente quando solicitado após MVP.

## Recuperação e evidências

| Situação | Procedimento |
|---|---|
| Dependência/version incompatível | Marcar blocked, registrar comando/erro redigido; não atualizar major automaticamente |
| Sandbox/protocolo falha | Bloquear execução; manter UI/consulta de histórico |
| Config inválida | Mostrar caminho/chave, preservar arquivo, não resetar sem confirmação |
| Disco cheio/migração falha | Rollback transação; preservar dados; desabilitar novas tarefas |
| Cancelamento/queda | Marcar interrupted/cancelled conforme confirmação; preservar workspace; sem replay |
| Conflito de aplicação | Não escrever; oferecer novo snapshot/revisão |
| Recuperação parcial conflita | Preservar backups/journal e exigir intervenção explícita |
| Extensão quebra | Desativar renderer GNOME, fallback Qt e aviso com limitação |
| Teste nativo indisponível | Registrar pendência; não marcar tarefa que exige gate como done |

Cada fase registra versões, comandos, exit codes, contagem de testes, plataforma e evidências manuais redigidas na própria tarefa; artefatos de runtime não entram automaticamente no Git público.

## Entrega documental e primeira tarefa

Esta execução cria apenas os nove documentos, valida referências/IDs/dependências/segredos, inicializa main e publica o repositório público autorizado. Q001 permanece pending. Depois, a primeira execução de código implementa apenas Q001; Q002 é a próxima tarefa subsequente.


## Revisão autorizada — perfis de permissão beta

Em 2026-11-11, o usuário autorizou revisar Q006–Q008 para perfis beta, mantendo configuração apenas por processo e todos os testes de isolamento. A exceção é restrita a initialize.capabilities.experimentalApi, permissions/runtimeWorkspaceRoots em thread/start, thread/resume e turn/start, além de command/exec.permissionProfile. Demais APIs experimentais continuam proibidas.

O contrato beta é capturado com hashes em schemas/codex/0.167.1/permissions-beta. Contrato aprovado não comprova sandbox: available/restricted_read/bounded_write continuam falsos até probes nativos. Não combinar permissions com sandbox/sandboxPolicy legados. Perfil tem nome único por execução: :minimal e runtime canônico read, somente workspace read/write conforme modo, network.enabled=false. Config global e credenciais não são copiadas nem alteradas.

Probe documentado: codex sandbox -P <perfil> --include-managed-config -C <workspace>, com permissions.<perfil> via -c. Seleção explícita será verificada por sentinelas, sem presumir que default_permissions sobrepõe sandbox_mode antigo. App Server seleciona perfil no request e não envia política legada no mesmo request. Q008 continua exigindo Windows nativo.

O usuário também autorizou etapas sucessivas, cada uma validada e commitada separadamente, substituindo a parada inicial após uma tarefa. Os gates de segurança e plataforma permanecem. O bloqueio anterior é histórico e será atualizado com evidências. Fonte: [Permissions](https://learn.chatgpt.com/docs/permissions), consultada nesta revisão.


## Revisão autorizada — avanço Linux com Windows pendente

O usuário pediu passar à próxima fase e confirmou a implementação. Q009 depende de Q007 validada, sem esperar Q008. O critério de conclusão desta etapa passa a ser bootstrap/worker no Linux, com teste automático e smoke Wayland; certificação Windows permanece em Q008/Q016/Q035 e não é inferida de testes Linux. Q010–Q015 podem prosseguir pelas dependências locais. Não habilitar execução Codex Windows nem anunciar suporte Windows antes dos gates nativos. O MVP/release multiplataforma mantém as exigências originais.

Instalar PySide6-Essentials 6.12.0 (mesmo namespace PySide6 e módulos QtCore/Gui/Qml/Quick/Controls/Network/DBus) para não puxar WebEngine/PDF sem uso. Addons entram somente quando uma fase precisar. Contratos e desenho Qt permanecem os aprovados. Uma prévia artística por imagegen foi tentada e rejeitada pela ferramenta; não foi produzida nem incorporada. Fixture técnico de Q010 não significa aprovação da arte final.


## Direção visual canônica — imagem escolhida pelo usuário

A orientação vigente é pixel art. O usuário rejeitou o fixture geométrico, cancelou o 3D e forneceu a imagem canônica de um furão marrom/creme com olhos e chamas verdes. Usar exatamente o PNG aprovado, preservando transparência e pixels; não redesenhar nem trocar por versões anteriores. A dimensão nativa é 1536×1024; “64 bits” descreve a estética pedida, não autoriza reduzir arbitrariamente o original a 64×64.

Manifesto agora aceita dimensões nativas até 2048 por eixo, com bounds/alpha/orçamento de 64 MiB mantidos. Frame precisa coincidir com frame_size. São permitidas transformações QML de respiração no renderer, sem recodificar a arte. Há uma pose aprovada, não nove animações: blink/fala/poses específicas ficam pendentes até produzir assets fiéis à referência. AvatarPresentation.blinking é um campo aditivo do motor; sua existência não significa que há frames de olhos prontos.

Q012 pode alterar o manifesto/schema/loader/testes de assets e a atribuição para incorporar esta escolha explícita; pode ajustar bootstrap para conectar a janela flutuante e encerrá-la corretamente. A UI deve mostrar a arte aprovada e permitir vê-la em tamanho maior. Os assets antes gerados como prova técnica não são a identidade final.
