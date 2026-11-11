# Estratégia de testes do Quill

Versão 1 — 2026-11-11. Testes aqui descritos são planejados, não resultados de execução do aplicativo. Evidências reais pertencem a [TASKS.md](TASKS.md).

## Pirâmide e ferramentas

pytest para lógica/integração; pytest-qt para lifecycle Qt e fixtures de UI; Ruff para lint/formato; mypy strict para contratos. Não instalar ferramentas de fase futura na fundação. Tests unit não fazem rede, não lançam Codex, não abrem apps do usuário e não usam microfone.

Estrutura: tests/unit, integration, ui, security e fixtures. Arquivo tests/conftest.py entra em Q002 quando houver fixture compartilhada; tests/ui/conftest.py entra em Q009 para Qt. Marcar unit/integration/ui/security/live_codex/manual; registrar marcadores em Q001, com --strict-markers. Native sandbox usa marcador security+live_codex. Testes manuais não são “pass” automático do pytest.

Regra default: live_codex e manual são desabilitados por addopts `-m "not live_codex and not manual"`. O executor só habilita testes reais explicitamente, sobrescrevendo addopts e selecionando arquivos concretos. `--basetemp` deve apontar a diretório descartável, nunca pasta de usuário com dados.

## Comandos básicos

Após Q001, a partir da raiz:

```text
uv sync --frozen --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src/quill
uv run pytest -q
```

Por tarefa: `uv run pytest tests/<categoria>/<arquivo>.py -q`, seguido dos comandos gerais. No ambiente sem display, Qt usa QT_QPA_PLATFORM=offscreen nos testes de modelo/lifecycle, configurado por fixture antes de criar QApplication. Isso não comprova Wayland, transparência, janelas nativas ou renderização do Shell.

Exemplo de probe real Linux, somente após opt-in e fixture pronta:

```text
uv run pytest -o addopts='' -m live_codex tests/security/test_sandbox_linux.py -q
```

No Windows usar o arquivo test_sandbox_windows.py no PowerShell nativo. Comandos de probe e limpeza devem constar na evidência. Falta de backend resulta falha/gate bloqueado, não skip aceito como aprovação.

## Fases e critérios

| Fase | Testes mínimos | Gate |
|---|---|---|
| Q001–Q005 | CLI, TOML, redaction, DTOs, migrações, transações, paginação | Todos passam sem Qt/Codex/rede |
| Q006–Q009 | schema, capabilities, sentinelas sandbox, startup Qt | Versão registrada; isolamento comprovado nos dois SOs |
| Q010–Q017 | assets, estados, D-Bus, lifecycle extensão, DPI/foco | Avatar real em GNOME 50/Wayland e Windows 11 |
| Q018–Q020 | conversa, duplicação, grants, timeout e UI de aprovação | Nenhum efeito sem decisão válida |
| Q021–Q029 | snapshot, hashes, journal, JSONL, executor fake, cleanup/recovery | Programação real só após sandbox+supervisor+política |
| Q030–Q035 | plano JSON, arquivos, apps, logs/terminal e cenário 401 | MVP completo nas duas máquinas |
| Q036–Q038 | teclado/contraste/config, autostart, browser isolado | Refinamento não amplia privilégios |
| Q039–Q041 | captura/STT/TTS fake e reais consentidos | Mic opt-in, áudio sem retenção, interrupção funcional |
| Q042–Q043 | builds nativos, install/uninstall, hashes e licenças | Pacotes verificáveis sem ambiente dev |

## Fixtures e determinismo

- Clock fake controla UTC/monotonic/deadlines/piscar.
- Servidor Codex falso em subprocesso Python fala JSONL e possui scripts: happy path, malformed, EOF, late approval, duplicate, out-of-order e stalled.
- Paths temporários incluem espaços, Unicode, prefixos parecidos e nomes com metacaracteres.
- Fixture Git contém staged/unstaged, tracked deleted, untracked selecionado, secrets falsos, binário, modo executável e link externo.
- Fixture SQLite em arquivo temporário, não apenas :memory:, para WAL/restart.
- Apps fake escrevem somente sentinela temporária; testes de lançamento não abrem navegador/editor reais automaticamente.
- Process tree fixture cria pai/filho/neto com identificadores próprios e timeout de autolimpeza.
- Validar instância única: segundo processo só solicita reabertura e não cria novo worker/fila.

Nenhum teste imprime secret fixture inteira; assert por ausência no destino.

Fixture auth401: cliente omite Authorization; fake server/transport exige “Bearer fixture-token”. Teste de contrato falha antes e passa com cabeçalho correto; token é claramente sintético, nunca autorização real. Verificar também token ausente continua falhando e autorização inválida não é aceita. Não corrigir o erro desligando autenticação.

## Matriz de segurança negativa

| Caso | Prova esperada |
|---|---|
| Read fora das raízes por shell e ferramentas alternativas | Falha e arquivo sentinela não aparece no resultado |
| Write fora do workspace | Conteúdo/hash original permanece idêntico |
| Rede de comando | Listener local de teste não recebe conexão; teste não depende da internet |
| Credenciais/config herdadas | Plugin/MCP/hook fixture não inicia; auth legítima não é copiada |
| Approve tardio/expirado | Tool não executa; estado terminal não reabre |
| Argumentos mudaram após consentimento | Digest inválido, nova aprovação necessária |
| Traversal/symlink/junction/reparse | Negação antes do efeito; nenhuma fuga de diretório |
| Prompt injection em README/log | Proposta de ferramenta proibida é negada; texto não amplia grants |
| Diff com origem concorrente | Zero escrita antes de revalidar todos os hashes |
| Falha parcial + edição externa | Recuperação não sobrescreve alteração externa |
| Codex/Quill recursivo | Caminho bloqueado por controle efetivo, não só instrução |
| Cancelamento/fechamento | Todos os processos de ownership conhecido encerram, sem kill por nome |
| Disk full/migração inválida | Estado anterior íntegro, erro explícito e novas execuções bloqueadas |
| Dados sensíveis no log/export | Redigidos antes de persistência e exibição |

## Manual GNOME/Wayland

Registrar versão GNOME, Qt, GPU/backend e escala, sem dados pessoais. Usar usuário/sessão de teste quando precisar reiniciar Shell; Wayland não suporta presumir restart por Alt+F2 r.

Ativar extensão; arrastar entre monitores; abrir chat; right-click; ocultar/reabrir; alterar escala; bloquear/desbloquear; desativar extensão durante tarefa; reativar e confirmar um mascote/timer; sair e confirmar zero atores/conexões. Conferir logs do Shell sem copiá-los integralmente. Validar teclado, foco, clicks fora da região e fallback sem extensão. Shell crash é falha impeditiva.

## Manual Windows 11

Registrar build, Qt, Codex e backend de sandbox. Rodar PowerShell nativo. Validar transparência, hit testing, não roubar foco, posição após sleep, monitores com 100/150/200%, remoção de monitor, esconder/reabrir, cancelamento e Job Object. UAC/tela segura não precisam exibir mascote. Não exigir administrador para uso normal; setup de sandbox privilegiado, se necessário, deve ser ação separada explícita.

## Interface e acessibilidade

Tema claro/escuro/system, textos longos, 0/1/1000 mensagens, erros, aguardando aprovação, rede indisponível e sem Codex. Contraste texto >=4.5:1; foco visível; nomes acessíveis; tab order; Enter não aprova automaticamente um diálogo recém-aberto; Escape não apaga histórico. Renderizar permissões completas sem truncar args que mudam o sentido da ação. Snapshot visual é evidência complementar, não teste de segurança.

## Performance

Medir com executor/voz desligados, janela estabilizada, 60 s de amostragem e identificar hardware. Metas: idle RSS <250 MiB e CPU média <2% de um núcleo; resposta visual <=150 ms; bloqueio da UI <100 ms em cenário fake. Desvio exige investigar/registrar, não mascarar amostra. Qualquer freeze recorrente é impeditivo ao MVP.

Rodar 100 ciclos abrir/fechar; comparar RSS após warmup e fim, investigar crescimento sustentado >10% ou >20 MiB. Confirmar contagem de timers/handlers estável. Oculto/locked não mantém frame timer. Capturar p50/p95 e duração, sem extrapolar métricas a todo hardware.

## CI e release

Q001–Q041 são verificados localmente em cada execução. Q042 adiciona CI ubuntu-latest e windows-latest com Python 3.13 e uv sync --frozen; runners não certificam extensão GNOME ou sandbox nativo real quando indisponíveis. Sem credenciais Codex na CI padrão.

Build/release em máquinas nativas. Instalar pacote num ambiente limpo, abrir, executar fixture consentida e desinstalar preservando dados do usuário. Inventariar plugins QML, Qt platform plugins, atlas e extensão. Validar checksum de cada artefato e declarar assinatura ausente. Atualização manual não ignora erro de migração; binário antigo não abre schema novo sem compatibilidade documentada.

## Validação documental desta entrega

Sem executar pytest de aplicativo inexistente. Validar: nove documentos presentes, links relativos existentes, fences fechadas, IDs Q001–Q043 únicos/ordenados, dependências sem ciclo, dez campos por tarefa, estados pending e nenhuma dependência futura. Buscar segredos e arquivos não documentais antes do commit/push. Registrar resultados concretos no changelog de TASKS.md.

## Definição de conclusão

Uma tarefa só é done com critérios e testes próprios passando, verificações gerais pertinentes e evidências nativas quando exigidas. O MVP só é aceito em Q035 com Linux e Windows reais; fixtures/fakes não substituem isso. Release só em Q043 com arte final, licenças, build, instalação/desinstalação e integridade comprovadas.


## Revisão autorizada — perfis de permissão beta

Em 2026-11-11, o usuário autorizou revisar Q006–Q008 para perfis beta, mantendo configuração apenas por processo e todos os testes de isolamento. A exceção é restrita a initialize.capabilities.experimentalApi, permissions/runtimeWorkspaceRoots em thread/start, thread/resume e turn/start, além de command/exec.permissionProfile. Demais APIs experimentais continuam proibidas.

O contrato beta é capturado com hashes em schemas/codex/0.167.1/permissions-beta. Contrato aprovado não comprova sandbox: available/restricted_read/bounded_write continuam falsos até probes nativos. Não combinar permissions com sandbox/sandboxPolicy legados. Perfil tem nome único por execução: :minimal e runtime canônico read, somente workspace read/write conforme modo, network.enabled=false. Config global e credenciais não são copiadas nem alteradas.

Probe documentado: codex sandbox -P <perfil> --include-managed-config -C <workspace>, com permissions.<perfil> via -c. Seleção explícita será verificada por sentinelas, sem presumir que default_permissions sobrepõe sandbox_mode antigo. App Server seleciona perfil no request e não envia política legada no mesmo request. Q008 continua exigindo Windows nativo.

O usuário também autorizou etapas sucessivas, cada uma validada e commitada separadamente, substituindo a parada inicial após uma tarefa. Os gates de segurança e plataforma permanecem. O bloqueio anterior é histórico e será atualizado com evidências. Fonte: [Permissions](https://learn.chatgpt.com/docs/permissions), consultada nesta revisão.


## Revisão autorizada — avanço Linux com Windows pendente

O usuário pediu passar à próxima fase e confirmou a implementação. Q009 depende de Q007 validada, sem esperar Q008. O critério de conclusão desta etapa passa a ser bootstrap/worker no Linux, com teste automático e smoke Wayland; certificação Windows permanece em Q008/Q016/Q035 e não é inferida de testes Linux. Q010–Q015 podem prosseguir pelas dependências locais. Não habilitar execução Codex Windows nem anunciar suporte Windows antes dos gates nativos. O MVP/release multiplataforma mantém as exigências originais.

Instalar PySide6-Essentials 6.12.0 (mesmo namespace PySide6 e módulos QtCore/Gui/Qml/Quick/Controls/Network/DBus) para não puxar WebEngine/PDF sem uso. Addons entram somente quando uma fase precisar. Contratos e desenho Qt permanecem os aprovados. Uma prévia artística por imagegen foi tentada e rejeitada pela ferramenta; não foi produzida nem incorporada. Fixture técnico de Q010 não significa aprovação da arte final.
