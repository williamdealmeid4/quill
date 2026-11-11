# Backlog executável do Quill

Versão 1 — 2026-11-11. **Estado real: somente documentação. Q001 é a primeira tarefa pendente. Nenhuma tarefa de aplicativo foi implementada.**

Documentos canônicos: [arquitetura](ARCHITECTURE.md), [plano](IMPLEMENTATION_PLAN.md), [segurança](SECURITY.md), [avatar](AVATAR_DESIGN.md), [Codex](CODEX_INTEGRATION.md) e [testes](TESTING.md).

## Regras de execução

Uma tarefa por solicitação. Ordem numérica estrita; dependências explícitas abaixo são cumulativas. Marcar in_progress antes de editar. Se faltar plataforma, controle de segurança ou decisão relevante, registrar blocked e requisito de desbloqueio; não continuar automaticamente. Não modificar arquivos preexistentes de outra finalidade.

Caminhos são relativos à raiz. Pacotes Python introduzidos recebem __init__.py; fora dessa exceção, somente caminhos enumerados, esta entrada do backlog e documentos explicitamente enumerados podem mudar. Diretório com / indica escopo delimitado no texto da tarefa. Testes e contratos são parte da entrega, não atividade opcional.

Toda tarefa executa o teste específico indicado e os checks gerais definidos em TESTING. Tarefas que adicionam dependência listam pyproject.toml e uv.lock; não instalar nada de fase futura. Teste nativo skip não comprova plataforma. Para lógica de backend: teste falha com motivo esperado, implementação mínima e teste passa; não adicionar teste que só repete implementação.

Conclusão comum C0: critérios e testes próprios passam, checks gerais pertinentes passam, diff revisado sem segredo, segurança preservada e evidências registradas (data UTC, SO/versões, comandos, exit codes, quantidade de testes, validação manual). Sem evidência, manter pending/blocked. Um commit focado por tarefa concluída; push não é automático.

## Índice

| ID | Tarefa | Estado |
|---|---|---|
| Q001 | Fundação Python | done |
| Q002 | Configuração tipada e caminhos | pending |
| Q003 | Logs estruturados e redação | pending |
| Q004 | Modelos, interfaces e erros | pending |
| Q005 | SQLite e migração inicial | pending |
| Q006 | Contrato real do Codex e capabilities | pending |
| Q007 | Probes de isolamento Linux | pending |
| Q008 | Probes de isolamento Windows 11 | pending |
| Q009 | Bootstrap Qt e worker assíncrono | pending |
| Q010 | Manifesto e fixture de avatar | pending |
| Q011 | Máquina de estados da animação | pending |
| Q012 | Mascote e janela Qt | pending |
| Q013 | Bridge D-Bus limitada | pending |
| Q014 | Lifecycle da extensão GNOME | pending |
| Q015 | Renderer e interações GNOME | pending |
| Q016 | Janelas e adaptador Windows | pending |
| Q017 | Seleção de backend e fallback | pending |
| Q018 | Conversa e submissão única | pending |
| Q019 | Política e grants | pending |
| Q020 | Serviço e painel de aprovações | pending |
| Q021 | Snapshot do projeto atual | pending |
| Q022 | Comparação e changeset | pending |
| Q023 | Aplicação e recuperação de diff | pending |
| Q024 | Transporte JSONL e RPC | pending |
| Q025 | Executor, sessões e eventos Codex | pending |
| Q026 | Aprovações do protocolo Codex | pending |
| Q027 | Supervisor de processos e cancelamento | pending |
| Q028 | Orquestrador, fila e recuperação | pending |
| Q029 | Painel de execução e revisão | pending |
| Q030 | Registro de ferramentas e planejador | pending |
| Q031 | Consultas de sistema e processos | pending |
| Q032 | Ferramentas de arquivos | pending |
| Q033 | Catálogo e abertura de aplicativos | pending |
| Q034 | Logs delimitados e terminal sandboxed | pending |
| Q035 | Aceitação completa do MVP | pending |
| Q036 | Configurações, histórico e acessibilidade | pending |
| Q037 | Notificações e autostart opt-in | pending |
| Q038 | Automação de navegador isolada | pending |
| Q039 | Captura e reconhecimento local | pending |
| Q040 | Síntese local e sincronização | pending |
| Q041 | Ativação opcional por frase | pending |
| Q042 | Builds e CI por plataforma | pending |
| Q043 | Release e atualização manual verificável | pending |

## Registro da entrega documental

- D000: done — entrega documental revisada em 2026-11-11T19:11:47+00:00. Nove arquivos Markdown, 74 links relativos válidos, fences fechadas, 43 tarefas únicas/ordenadas com 430 campos e dependências acíclicas. Scanner local de padrões não encontrou tokens/chaves privadas nem caminhos pessoais alheios ao projeto. Zero arquivos de runtime. Validação por Python/stdlib, exit 0; não há testes pytest de aplicativo nesta entrega. Publicação autorizada em williamdealmeid4/quill; URL, commit e confirmação remota são informados no relatório final da execução.
- Q001–Q043 permanecem pending; publicar documentos não conclui tarefa de implementação.

## Tarefas

## Fase — Fundação

### Q001 — Fundação Python

1. **Identificador:** Q001. **Estado:** done.
2. **Objetivo:** Fundação Python; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Nove documentos presentes/revisados, commit documental publicado e estado Git inspecionado; nenhum código prévio presumido.
4. **Arquivos envolvidos:**
   - Criar: `pyproject.toml`
   - Criar: `uv.lock`
   - Criar: `.python-version`
   - Criar: `.gitignore`
   - Criar: `src/quill/__init__.py`
   - Criar: `src/quill/__main__.py`
   - Criar: `tests/unit/test_cli.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Criar pacote quill 0.1.0 via Hatchling, Python >=3.13,<3.14 e .python-version=3.13. CLI argparse aceita --version e --help; não inicializa UI, config ou banco. Dev group inclui pytest, ruff e mypy; registrar marcadores e default sem live_codex/manual. Ruff py313/100 colunas/E,F,I,UP,B,SIM e mypy strict. Gitignore cobre venv, caches, logs, bancos, workspaces e builds. Fixar resolução em uv.lock, sem dependências runtime futuras.
   **Entradas e saídas / interfaces:** Produz python -m quill --version -> stdout 0.1.0, exit 0; argumento inválido -> exit 2. __init__ expõe __version__:str. Não depende de serviço interno.
6. **Critérios de aceitação:** CLI funciona após uv sync --frozen --group dev; lint/formato/tipagem/suíte passam; consultar versão não cria janela nem arquivos de usuário.
7. **Testes necessários:** test_version_subprocess: exit 0, stdout 0.1.0 e nenhum stderr; test_help_without_side_effects: help exit 0 sem criar dados; test_unknown_argument: exit 2. Testar em cwd temporário com env de dados temporário.
   **Comando específico:** `uv run pytest tests/unit/test_cli.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** CLI funciona após uv sync --frozen --group dev; lint/formato/tipagem/suíte passam; consultar versão não cria janela nem arquivos de usuário. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** 2026-11-11T19:16:09+00:00, Linux x86_64, Python 3.13.15, uv 0.12.19. RED: três testes falharam por módulo ausente. GREEN: `uv run pytest tests/unit/test_cli.py -q` e `uv run pytest -q`: 3 passed, exit 0. `uv sync --frozen --group dev`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src/quill`, `git diff --check`: exit 0. CLI --version imprime 0.1.0. Ruff inclui apenas Python/TOML para preservar exemplos documentais. Sem validação Windows nesta tarefa de fundação; gates nativos continuam pendentes.
10. **Dependências para a próxima tarefa:** Q002 (além das demais dependências listadas nela).

### Q002 — Configuração tipada e caminhos

1. **Identificador:** Q002. **Estado:** pending.
2. **Objetivo:** Configuração tipada e caminhos; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q001=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/config/models.py`
   - Criar: `src/quill/config/service.py`
   - Criar: `tests/conftest.py`
   - Criar: `tests/unit/test_config.py`
   - Modificar: `pyproject.toml`
   - Modificar: `uv.lock`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Adicionar platformdirs. Implementar AppConfig v1 e defaults da arquitetura. Validar theme, tamanho 96–256, timeout 60–3600 s, retenções >=1 dia, effort low e campos desconhecidos. ConfigService recebe diretório/Clock por injeção. Gravação em temporário no mesmo volume + replace; tomllib lê e serializador do subconjunto suportado escreve. Config ausente retorna defaults sem criar arquivo até save.
   **Entradas e saídas / interfaces:** ConfigService.load()->AppConfig; save(config:AppConfig)->None. Produz caminhos config/data/cache/log via platformdirs; grants vazios e voz/autostart false.
6. **Critérios de aceitação:** Arquivo inválido não é resetado; roundtrip preserva valores; falha antes de replace mantém original byte a byte.
7. **Testes necessários:** test_missing_uses_defaults; test_invalid_toml_preserved; test_unknown_key_rejected; test_roundtrip_unicode; test_atomic_save_failure_preserves_original. monkeypatch platformdirs para tmp_path.
   **Comando específico:** `uv run pytest tests/unit/test_config.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Arquivo inválido não é resetado; roundtrip preserva valores; falha antes de replace mantém original byte a byte. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q003 (além das demais dependências listadas nela).

### Q003 — Logs estruturados e redação

1. **Identificador:** Q003. **Estado:** pending.
2. **Objetivo:** Logs estruturados e redação; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q002=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/observability/logging.py`
   - Criar: `src/quill/observability/redaction.py`
   - Criar: `tests/security/test_redaction.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Criar setup_logging(log_dir:Path)->None e redact(value:JsonValue)->JsonValue provisoriamente com alias local que Q004 moverá ao core. JSONL UTC/task/execution/code; handler rotativo 10 MiB, 5 backups. Redigir antes de formatar, persistir ou mostrar. Evitar log de prompt/argv/env completos. Não capturar tokens reais nos testes.
   **Entradas e saídas / interfaces:** Produz redact e configuração idempotente; duas chamadas setup não duplicam handlers. Q004 padroniza o alias sem mudar assinatura semântica.
6. **Critérios de aceitação:** Secret sintético não aparece em nenhum arquivo/erro; JSON de cada linha é válido; rotação e correlação funcionam.
7. **Testes necessários:** test_authorization_token_redacted; test_nested_cookie_and_url_secret; test_no_raw_secret_in_file; test_handler_not_duplicated; test_rotation_retains_five_backups. Usar limite menor injetado só no teste de rotação.
   **Comando específico:** `uv run pytest tests/security/test_redaction.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Secret sintético não aparece em nenhum arquivo/erro; JSON de cada linha é válido; rotação e correlação funcionam. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q004 (além das demais dependências listadas nela).

### Q004 — Modelos, interfaces e erros

1. **Identificador:** Q004. **Estado:** pending.
2. **Objetivo:** Modelos, interfaces e erros; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q003=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/core/models.py`
   - Criar: `src/quill/core/ports.py`
   - Criar: `src/quill/core/errors.py`
   - Criar: `src/quill/core/events.py`
   - Modificar: `src/quill/observability/redaction.py`
   - Criar: `tests/unit/test_models.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar todos os DTOs/enums e Protocol de ARCHITECTURE. Validar UUID/UTC/limites sem bibliotecas adicionais. ErrorInfo não aceita exceção bruta. Centralizar JsonValue e atualizar import de redaction. EventKind e tabela de transições são fechados; funções puras validate_transition(old:TaskState,new:TaskState)->None e validate_event(event:DomainEvent)->None.
   **Entradas e saídas / interfaces:** Produz contratos canônicos, Clock e CancellationToken. Estados terminais não transitam para running/queued. Transição inválida gera VALIDATION_FAILED.
6. **Critérios de aceitação:** Todos os nomes/tipos da arquitetura existem; core não importa Qt, banco, psutil ou código de plataforma.
7. **Testes necessários:** test_reject_naive_datetime; test_json_reject_nan; test_terminal_cannot_restart; test_approval_cycle_allowed; test_dto_immutable; test_error_has_safe_details. Mypy checa importação de todos os Protocol.
   **Comando específico:** `uv run pytest tests/unit/test_models.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Todos os nomes/tipos da arquitetura existem; core não importa Qt, banco, psutil ou código de plataforma. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q005 (além das demais dependências listadas nela).

### Q005 — SQLite e migração inicial

1. **Identificador:** Q005. **Estado:** pending.
2. **Objetivo:** SQLite e migração inicial; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q004=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/memory/store.py`
   - Criar: `src/quill/memory/migrations/001_initial.sql`
   - Criar: `tests/integration/test_store.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Criar todas as tabelas/índices da arquitetura. Worker SQLite com uma conexão, WAL/FK/busy_timeout. Migração transacional com checksum. MemoryStore implementado e transition(task_id,expected_state,next_state,event) atômica com compare-and-set. Paginação por created_at/id, limite 1–100. Future retornada ao caller, sem conexão compartilhada com UI.
   **Entradas e saídas / interfaces:** MemoryStore e operação transition; migrate()->None; close()->None (async). Execuções e aprovações possuem estado persistido, não só log.
6. **Critérios de aceitação:** Reabrir banco mantém dados/versão; falha não deixa migração pela metade; queries parametrizadas e ownership de thread comprovados.
7. **Testes necessários:** test_migration_restart; test_failed_migration_rolls_back; test_fk_enforced; test_state_event_atomic; test_duplicate_submission_rejected; test_page_cursor_no_duplicates; test_disk_full_reports_storage_error. Usar arquivo tmp real.
   **Comando específico:** `uv run pytest tests/integration/test_store.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Reabrir banco mantém dados/versão; falha não deixa migração pela metade; queries parametrizadas e ownership de thread comprovados. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q006 (além das demais dependências listadas nela).

## Fase — Viabilidade e segurança

### Q006 — Contrato real do Codex e capabilities

1. **Identificador:** Q006. **Estado:** pending.
2. **Objetivo:** Contrato real do Codex e capabilities; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q004=done, Q005=done
4. **Arquivos envolvidos:**
   - Criar: `schemas/codex/`
   - Criar: `src/quill/codex/capabilities.py`
   - Criar: `tests/fixtures/codex/`
   - Criar: `tests/unit/test_capabilities.py`
   - Modificar: `docs/CODEX_INTEGRATION.md`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Escopo dos diretórios: schema da versão instalada, manifest com versão/hash/métodos e fixtures redigidas de handshake/catálogo/erro; sem dados pessoais. Executar somente help/version/login status/gerador de schema, sem turno agente. Confirmar flags de perfil por invocação, auth, ferramentas herdadas, políticas e API estável. Preencher matriz concreta em CODEX_INTEGRATION sem inventar campos. Se faltar controle, blocked.
   **Entradas e saídas / interfaces:** inspect_cli(executable:Path)->ExecutorCapabilities (async); validate_schema_manifest(path:Path)->None; choose_model(catalog:tuple[ModelCapability,...],selected_id:str|None)->ModelCapability. Vários Sol sem seleção -> MODEL_UNAVAILABLE com opções, não escolha silenciosa.
6. **Critérios de aceitação:** Schema versionado e matriz documentada; auth não é lida de arquivo; modelo low é resolvido pela conta; nenhuma API experimental adotada.
7. **Testes necessários:** test_supported_manifest; test_missing_required_method_blocks; test_model_missing_low_blocks; test_multiple_sol_requires_selection; test_unsupported_version_blocks. Fixtures não iniciam Codex.
   **Comando específico:** `uv run pytest tests/unit/test_capabilities.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Schema versionado e matriz documentada; auth não é lida de arquivo; modelo low é resolvido pela conta; nenhuma API experimental adotada. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q007 (além das demais dependências listadas nela).

### Q007 — Probes de isolamento Linux

1. **Identificador:** Q007. **Estado:** pending.
2. **Objetivo:** Probes de isolamento Linux; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q006=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/codex/sandbox.py`
   - Criar: `tests/security/test_sandbox_linux.py`
   - Modificar: `docs/CODEX_INTEGRATION.md`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar SandboxPolicyBuilder para políticas exatas confirmadas em Q006. Harness live_codex opt-in em tmp, com finally/timeout e autolimpeza. Testar read restrito, write só workspace, rede local bloqueada, rotas de tools sem shell, hooks/MCP/plugins herdados e prevenção efetiva de recursão. Não habilitar comandos reais na UI. Se backend não contiver qualquer rota, registrar blocked.
   **Entradas e saídas / interfaces:** build_policy(mode:PermissionMode,workspace:Path,runtime_roots:tuple[Path,...])->dict[str,JsonValue]; probe_sandbox()->SandboxCapabilities (async). Não usar defaults full-read.
6. **Critérios de aceitação:** Todos os testes negativos reais passam no Linux; nenhum recurso pessoal usado; evidência registra versão, policy digest e cleanup.
7. **Testes necessários:** test_read_sentinel_denied; test_write_sentinel_unchanged; test_command_network_denied; test_alternate_tool_cannot_read_origin; test_inherited_hook_not_run; test_recursive_executor_blocked. Marcar probes live_codex/security.
   **Comando específico:** `uv run pytest tests/security/test_sandbox_linux.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Todos os testes negativos reais passam no Linux; nenhum recurso pessoal usado; evidência registra versão, policy digest e cleanup. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q008 (além das demais dependências listadas nela).

### Q008 — Probes de isolamento Windows 11

1. **Identificador:** Q008. **Estado:** pending.
2. **Objetivo:** Probes de isolamento Windows 11; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q006=done, Q007=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/platforms/windows/sandbox.py`
   - Criar: `tests/security/test_sandbox_windows.py`
   - Modificar: `docs/CODEX_INTEGRATION.md`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Executar em Windows 11/PowerShell nativo. Detectar readiness/backend disponível conforme schema real. Repetir sentinelas de Q007 incluindo junction/reparse e subprocessos. Não iniciar setup administrativo automaticamente; not-ready bloqueia. Registrar backend e limites efetivos; não converter falha em WSL automaticamente.
   **Entradas e saídas / interfaces:** WindowsSandboxAdapter.probe()->SandboxCapabilities (async). Mesmo contrato de capacidade Q007, sem import Windows no módulo Linux.
6. **Critérios de aceitação:** Gate comprovado em Windows real; mocks não concluem; nenhuma elevação silenciosa.
7. **Testes necessários:** test_windows_read_denied; test_windows_write_denied; test_windows_network_denied; test_windows_reparse_escape_denied; test_windows_recursive_executor_blocked; test_unavailable_blocks. live_codex/security.
   **Comando específico:** `uv run pytest tests/security/test_sandbox_windows.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Gate comprovado em Windows real; mocks não concluem; nenhuma elevação silenciosa. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q009 (além das demais dependências listadas nela).

### Q009 — Bootstrap Qt e worker assíncrono

1. **Identificador:** Q009. **Estado:** pending.
2. **Objetivo:** Bootstrap Qt e worker assíncrono; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q002=done, Q003=done, Q005=done, Q008=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/bootstrap.py`
   - Criar: `src/quill/ui/bridge.py`
   - Criar: `src/quill/ui/qml/Main.qml`
   - Modificar: `src/quill/__main__.py`
   - Criar: `tests/ui/conftest.py`
   - Criar: `tests/ui/test_startup.py`
   - Modificar: `pyproject.toml`
   - Modificar: `uv.lock`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Adicionar PySide6 6.12.x e pytest-qt; resolver patch compatível com Python 3.13 nos dois SOs. Preservar --version sem import Qt. bootstrap monta QApplication/QML e ExecutionWorker com event loop asyncio em thread própria; façade Qt em ui/bridge encaminha intenções por queued signals. Ainda sem Codex real. Fechamento encerra thread/loop com prazo. Implementar instância única com QLockFile/QLocalServer; segunda abertura só mostra o painel da primeira, sem nova fila.
   **Entradas e saídas / interfaces:** bootstrap.main()->int; UiBridge com submit/cancel/settings slots; ExecutionWorker executa coroutine e retorna DTO por sinal. Contexto QML chama somente bridge.
6. **Critérios de aceitação:** Janela abre/fecha nas duas máquinas, sem thread/processo residual e sem I/O lento na main thread.
7. **Testes necessários:** test_window_opens_and_closes; test_slow_fake_does_not_freeze_ui; test_shutdown_stops_worker; test_version_still_headless; test_second_instance_reopens_first_without_worker. Offscreen automático e abertura manual nativa Linux/Windows.
   **Comando específico:** `uv run pytest tests/ui/test_startup.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Janela abre/fecha nas duas máquinas, sem thread/processo residual e sem I/O lento na main thread. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q010 (além das demais dependências listadas nela).

## Fase — Avatar e plataformas

### Q010 — Manifesto e fixture de avatar

1. **Identificador:** Q010. **Estado:** pending.
2. **Objetivo:** Manifesto e fixture de avatar; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q009=done
4. **Arquivos envolvidos:**
   - Criar: `schemas/avatar.schema.json`
   - Criar: `src/quill/avatar/assets.py`
   - Criar: `assets/avatars/quill/manifest.json`
   - Criar: `assets/avatars/quill/atlas-0.png`
   - Criar: `assets/avatars/quill/preview.png`
   - Criar: `assets/avatars/quill/ATTRIBUTION.md`
   - Criar: `tests/unit/test_avatar_assets.py`
   - Modificar: `pyproject.toml`
   - Modificar: `uv.lock`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Adicionar jsonschema. Definir manifesto conforme AVATAR_DESIGN: atlas bounds, frame/padding/âncora/hit_region e nove estados. Criar fixture geométrico técnico original RGBA, identificado como provisório, sem usar assets de jogos. PNG fixture pode ser produzido com QImage/QPainter já disponíveis; não adicionar biblioteca de imagem. Arte final não é implementada nesta tarefa.
   **Entradas e saídas / interfaces:** load_avatar(root:Path)->AvatarManifest; validate_manifest(value:JsonValue,root:Path)->AvatarManifest. Manifesto validado não tem URL/traversal e memória decodificada <=64 MiB.
6. **Critérios de aceitação:** Fixture renderizável com todos os estados; autoria/estado provisório claros; arquivos externos ao avatar nunca carregados.
7. **Testes necessários:** test_all_required_states; test_missing_frame_rejected; test_out_of_bounds_rejected; test_path_escape_rejected; test_atlas_budget_rejected; test_png_alpha_present.
   **Comando específico:** `uv run pytest tests/unit/test_avatar_assets.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Fixture renderizável com todos os estados; autoria/estado provisório claros; arquivos externos ao avatar nunca carregados. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q011 (além das demais dependências listadas nela).

### Q011 — Máquina de estados da animação

1. **Identificador:** Q011. **Estado:** pending.
2. **Objetivo:** Máquina de estados da animação; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q004=done, Q010=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/avatar/state.py`
   - Criar: `tests/unit/test_avatar_state.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar AvatarStateManager com Clock e RNG injetados, prioridades da spec, piscar 3–7s, sucesso <=1s e error/approval persistentes. visible=false/reduced_motion suspende frames conforme política. State manager não conhece ferramentas nem interpreta texto livre.
   **Entradas e saídas / interfaces:** on_event(event:DomainEvent)->AvatarPresentation; tick()->AvatarPresentation; set_visible(bool)->None; set_reduced_motion(bool)->None. AvatarState/Presentation tipados.
6. **Critérios de aceitação:** Transições determinísticas e renderer recebe somente estado/visibilidade/balão; terminar animação não conclui tarefa.
7. **Testes necessários:** test_approval_overrides_working; test_error_persists; test_success_returns_to_current_state; test_blink_interval_with_fake_clock; test_hidden_has_no_frame_ticks; test_reduced_motion_static.
   **Comando específico:** `uv run pytest tests/unit/test_avatar_state.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Transições determinísticas e renderer recebe somente estado/visibilidade/balão; terminar animação não conclui tarefa. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q012 (além das demais dependências listadas nela).

### Q012 — Mascote e janela Qt

1. **Identificador:** Q012. **Estado:** pending.
2. **Objetivo:** Mascote e janela Qt; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q009=done, Q010=done, Q011=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/ui/qml/Avatar.qml`
   - Criar: `src/quill/ui/qml/AvatarWindow.qml`
   - Modificar: `src/quill/ui/qml/Main.qml`
   - Modificar: `src/quill/ui/bridge.py`
   - Criar: `tests/ui/test_avatar.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Renderizar fixture via manifesto validado, sem carregar PNG por frame. Janela transparente/sem borda; menu e clique abrem painel; escala 96–256. Região interativa limitada, pausa ao ocultar. Wayland genérico usa system move e não força coordenada global. Qt é único renderer até extensão pronta.
   **Entradas e saídas / interfaces:** Avatar.qml consome AvatarPresentation e AvatarManifest; signals openChatRequested/hideRequested/sizeRequested. UiBridge traduz intenção, sem shell.
6. **Critérios de aceitação:** Mascote não captura tela inteira, não rouba foco ao animar e oculta/reabre sem duplicar janela.
7. **Testes necessários:** test_avatar_frame_source; test_size_bounds; test_hidden_timer_stops; test_menu_intents; test_panel_opens_without_new_task. Verificação manual de transparência e clique nativo.
   **Comando específico:** `uv run pytest tests/ui/test_avatar.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Mascote não captura tela inteira, não rouba foco ao animar e oculta/reabre sem duplicar janela. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q013 (além das demais dependências listadas nela).

### Q013 — Bridge D-Bus limitada

1. **Identificador:** Q013. **Estado:** pending.
2. **Objetivo:** Bridge D-Bus limitada; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q009=done, Q011=done, Q012=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/desktop/bridge.py`
   - Criar: `schemas/desktop-bridge.xml`
   - Modificar: `src/quill/bootstrap.py`
   - Criar: `tests/integration/test_desktop_bridge.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Usar QtDBus do PySide, nome org.quill.Desktop, objeto /org/quill/Desktop e interface org.quill.Desktop1. Métodos Handshake(u version)->u, GetPresentation()->s JSON, SendIntent(s JSON)->b; sinais PresentationChanged(s JSON). Intents fechados open_chat/hide/show/set_size/set_position com revision/limites; sem aprovação/comando/path livre. Heartbeat 2s/fallback 6s. Registrar apenas em Linux com session bus.
   **Entradas e saídas / interfaces:** DesktopBridge.start()/stop(); apresentação segue AvatarPresentation. D-Bus executa callback rápido na main thread e envia DTO validado ao worker.
6. **Critérios de aceitação:** Extensão pode controlar apresentação, nunca execução/permissão; Windows inicia sem QtDBus registrado.
7. **Testes necessários:** test_handshake_version; test_unknown_intent_rejected; test_no_shell_or_approval_intent; test_disconnect_fallback; test_late_revision_ignored. Bus fake automático e session bus teste nativo.
   **Comando específico:** `uv run pytest tests/integration/test_desktop_bridge.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Extensão pode controlar apresentação, nunca execução/permissão; Windows inicia sem QtDBus registrado. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q014 (além das demais dependências listadas nela).

### Q014 — Lifecycle da extensão GNOME

1. **Identificador:** Q014. **Estado:** pending.
2. **Objetivo:** Lifecycle da extensão GNOME; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q013=done
4. **Arquivos envolvidos:**
   - Criar: `extensions/gnome/quill@quill.local/metadata.json`
   - Criar: `extensions/gnome/quill@quill.local/extension.js`
   - Criar: `tests/integration/test_extension_manifest.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** ESModules GJS, UUID quill@quill.local, shell-version somente 50. enable cria container/indicador e conexão limitada; disable remove timers, sinais e atores em ordem idempotente. Não registrar versão não testada, não executar subprocessos pelo Shell. Instalação de teste por usuário, sem alterar outras extensões.
   **Entradas e saídas / interfaces:** Default export Extension com enable()/disable(); container é ponto de montagem de avatar.js da próxima tarefa.
6. **Critérios de aceitação:** GNOME 50 mantém sessão estável; desativar remove tudo; teste estrutural sozinho não conclui.
7. **Testes necessários:** test_uuid_and_shell_version; test_no_privileged_manifest_actions. Manual GNOME: enable/disable 20 vezes, registrar ausência de atores/timers duplicados e erros Shell.
   **Comando específico:** `uv run pytest tests/integration/test_extension_manifest.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** GNOME 50 mantém sessão estável; desativar remove tudo; teste estrutural sozinho não conclui. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q015 (além das demais dependências listadas nela).

### Q015 — Renderer e interações GNOME

1. **Identificador:** Q015. **Estado:** pending.
2. **Objetivo:** Renderer e interações GNOME; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q010=done, Q013=done, Q014=done
4. **Arquivos envolvidos:**
   - Criar: `extensions/gnome/quill@quill.local/avatar.js`
   - Criar: `extensions/gnome/quill@quill.local/bridge.js`
   - Criar: `extensions/gnome/quill@quill.local/stylesheet.css`
   - Modificar: `extensions/gnome/quill@quill.local/extension.js`
   - Criar: `tests/integration/test_gnome_renderer.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Ler atlas/manifest de diretório instalado da própria extensão, cópia empacotada dos assets; nunca caminho arbitrário recebido por D-Bus. Carregar textura uma vez e um timer. Recortar frames, drag/clamp por workarea, menu e lock pause. Conectar Desktop1 e tratar reconexão por revision. Validar APIs St/Clutter reais GNOME50; incompatibilidade bloqueia antes de trocar renderer.
   **Entradas e saídas / interfaces:** AvatarActor.applyPresentation(presentation)->void; destroy()->void. bridge GJS só usa o contrato XML e intents permitidos.
6. **Critérios de aceitação:** Apenas um mascote, sem timer após hide/disable; UI Python continua funcionando após extensão desconectar.
7. **Testes necessários:** test_packaged_assets_match_manifest; test_bridge_contract_version. Manual: todos os estados, drag multimonitor, hide, lock, reconnect e disable durante tarefa fake.
   **Comando específico:** `uv run pytest tests/integration/test_gnome_renderer.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Apenas um mascote, sem timer após hide/disable; UI Python continua funcionando após extensão desconectar. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q016 (além das demais dependências listadas nela).

### Q016 — Janelas e adaptador Windows

1. **Identificador:** Q016. **Estado:** pending.
2. **Objetivo:** Janelas e adaptador Windows; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q009=done, Q012=done, Q015=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/platforms/windows/desktop.py`
   - Criar: `src/quill/platforms/windows/window.py`
   - Modificar: `src/quill/ui/qml/AvatarWindow.qml`
   - Criar: `tests/unit/test_windows_window.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Usar ctypes/Win32 só no módulo Windows, topmost sem ativar, máscara de hit testing e DPI awareness compatível com Qt. Persistir posição normalizada/monitor; clamp após hotplug. Não usar hooks Explorer ou DLL injection. Notificações podem declarar unavailable até Q037.
   **Entradas e saídas / interfaces:** WindowsDesktopAdapter implementa DesktopAdapter; WindowsWindowController.apply_position/size/topmost->None e close()->None. get capabilities informa limites reais.
6. **Critérios de aceitação:** Mascote funcional em Windows nativo sem administrador; não aparece por promessa sobre UAC/fullscreen seguro.
7. **Testes necessários:** test_win32_flags_do_not_activate; test_coordinates_clamped; test_missing_monitor_fallback; test_linux_import_does_not_load_user32. Manual Windows: DPI 100/150/200, foco, transparent hits, sleep/hotplug.
   **Comando específico:** `uv run pytest tests/unit/test_windows_window.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Mascote funcional em Windows nativo sem administrador; não aparece por promessa sobre UAC/fullscreen seguro. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q017 (além das demais dependências listadas nela).

### Q017 — Seleção de backend e fallback

1. **Identificador:** Q017. **Estado:** pending.
2. **Objetivo:** Seleção de backend e fallback; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q013=done, Q015=done, Q016=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/platforms/base.py`
   - Criar: `src/quill/platforms/generic/desktop.py`
   - Criar: `src/quill/platforms/linux/desktop.py`
   - Modificar: `src/quill/bootstrap.py`
   - Criar: `tests/unit/test_desktop_selection.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Fábrica seleciona Linux GNOME bridge quando handshake válido, Windows adapter em win32 e fallback Qt por capacidades. Garantir um único renderer. Sem extensão: avisar limitação de Wayland e manter painel. Não instalar extensão automaticamente nem fingir suporte macOS.
   **Entradas e saídas / interfaces:** select_desktop(environment:Mapping[str,str])->DesktopAdapter; GenericDesktopAdapter.capabilities informa posição/topmost indisponíveis quando não comprovados.
6. **Critérios de aceitação:** Troca/falha do renderer não cancela tarefa; interface continua acessível sem depender de tray.
7. **Testes necessários:** test_gnome_prefers_extension; test_bridge_loss_enables_one_qt_avatar; test_windows_selects_native; test_unknown_backend_limits_capabilities; test_no_cross_platform_import.
   **Comando específico:** `uv run pytest tests/unit/test_desktop_selection.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Troca/falha do renderer não cancela tarefa; interface continua acessível sem depender de tray. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q018 (além das demais dependências listadas nela).

## Fase — Chat e permissões

### Q018 — Conversa e submissão única

1. **Identificador:** Q018. **Estado:** pending.
2. **Objetivo:** Conversa e submissão única; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q005=done, Q009=done, Q017=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/conversation/service.py`
   - Criar: `src/quill/ui/models.py`
   - Criar: `src/quill/ui/qml/ChatPanel.qml`
   - Modificar: `src/quill/ui/qml/Main.qml`
   - Modificar: `src/quill/ui/bridge.py`
   - Modificar: `src/quill/bootstrap.py`
   - Criar: `tests/ui/test_chat.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** ConversationService persiste mensagens/tasks e envia a port de fila fake nesta fase. Texto até 32KiB UTF-8, projeto escolhido explicitamente. Histórico QAbstractListModel paginado/virtualizado. Entrada multiline; submit UUID criado uma vez e reutilizado em clique repetido. Texto/Markdown restrito sem HTML ou imagem remota automática.
   **Entradas e saídas / interfaces:** submit(conversation_id,text,project,mode,submission_id)->TaskRecord (async) conforme arquitetura. UI mostra queued com executor fake e não inicia Codex real.
6. **Critérios de aceitação:** Chat envia uma tarefa por intenção, recarrega histórico e comunica projeto/estado sem bloquear UI.
7. **Testes necessários:** test_double_click_one_submission; test_history_survives_restart; test_oversize_prompt_rejected; test_external_content_not_executed; test_project_required_for_code_request.
   **Comando específico:** `uv run pytest tests/ui/test_chat.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Chat envia uma tarefa por intenção, recarrega histórico e comunica projeto/estado sem bloquear UI. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q019 (além das demais dependências listadas nela).

### Q019 — Política e grants

1. **Identificador:** Q019. **Estado:** pending.
2. **Objetivo:** Política e grants; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q004=done, Q005=done, Q018=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/permissions/models.py`
   - Criar: `src/quill/permissions/policy.py`
   - Criar: `tests/security/test_permission_policy.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar PermissionGrant/ApprovalRequest com os campos de SECURITY e avaliação pura. Canonicalizar recursos/argumentos em JSON determinístico para SHA256. Modo read não permite write; assisted pede aprovação concreta; restricted_auto exige grant válido, quota e efeito. Ações privilegiadas/exclusão permanente sempre deny no MVP.
   **Entradas e saídas / interfaces:** evaluate_policy(action:ActionRequest,grants:tuple[PermissionGrant,...],mode:PermissionMode,now:datetime)->PermissionDecision; canonical_action_digest(action)->str.
6. **Critérios de aceitação:** Mesma entrada/tempo produz mesma decisão; nenhuma palavra do modelo ou permission annotation externa concede autoridade.
7. **Testes necessários:** test_three_modes; test_expired_or_revoked_grant_denied; test_arguments_change_invalidates; test_scope_prefix_escape_denied; test_auto_quota_exceeded; test_privileged_always_denied.
   **Comando específico:** `uv run pytest tests/security/test_permission_policy.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Mesma entrada/tempo produz mesma decisão; nenhuma palavra do modelo ou permission annotation externa concede autoridade. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q020 (além das demais dependências listadas nela).

### Q020 — Serviço e painel de aprovações

1. **Identificador:** Q020. **Estado:** pending.
2. **Objetivo:** Serviço e painel de aprovações; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q005=done, Q018=done, Q019=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/permissions/service.py`
   - Criar: `src/quill/ui/qml/ApprovalPanel.qml`
   - Modificar: `src/quill/ui/bridge.py`
   - Modificar: `src/quill/bootstrap.py`
   - Criar: `tests/ui/test_approval.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar PermissionService com store, Clock e espera cancelável; expirar em 5min para deny. UI exibe efeito/args completos/cwd/recursos/rede/risco, aceitar/negar/cancelar. Grant vinculado ao digest e tarefa; resolver exatamente uma vez. Enter não aceita popup recém-aberto.
   **Entradas e saídas / interfaces:** evaluate/resolve do Protocol. Serviço publica approval.requested/resolved; decisão tardia de tarefa terminal não reabre execução.
6. **Critérios de aceitação:** Decisão persistida e auditada; sem efeito quando pedido não está pendente e atual.
7. **Testes necessários:** test_explicit_accept; test_decline_no_effect; test_timeout_denies; test_cancel_races_late_accept; test_changed_args_need_new_approval; test_enter_not_default_accept.
   **Comando específico:** `uv run pytest tests/ui/test_approval.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Decisão persistida e auditada; sem efeito quando pedido não está pendente e atual. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q021 (além das demais dependências listadas nela).

## Fase — Workspaces e Codex

### Q021 — Snapshot do projeto atual

1. **Identificador:** Q021. **Estado:** pending.
2. **Objetivo:** Snapshot do projeto atual; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q005=done, Q019=done, Q020=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/workspaces/snapshot.py`
   - Criar: `src/quill/workspaces/manifest.py`
   - Criar: `tests/security/test_snapshot.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Exigir Git, enumerar tracked com NUL e flags sem hooks/fsmonitor, copiar bytes atuais e deleções, incluir untracked só selecionados. Validar links/paths/limites/exclusões antes de confirmar escopo. Criar Git independente sem .git compartilhado/remotes/hooks. Guardar baseline hashes fora da visão agente. Submódulo/LFS ausente bloqueia.
   **Entradas e saídas / interfaces:** snapshot(request:SnapshotRequest)->WorkspaceSnapshot (async); FileFingerprint/ExcludedFile conforme core. Nenhuma escrita na origem nem em seu índice.
6. **Critérios de aceitação:** Snapshot reproduz estado autorizado e relatório de exclusões; origem/índice permanecem byte a byte intactos.
7. **Testes necessários:** test_dirty_tracked_preserved; test_tracked_deleted_stays_deleted; test_untracked_selection_only; test_secrets_excluded; test_symlink_junction_escape_denied; test_case_collision_blocks; test_limits_and_cancel_cleanup; test_git_index_unchanged.
   **Comando específico:** `uv run pytest tests/security/test_snapshot.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Snapshot reproduz estado autorizado e relatório de exclusões; origem/índice permanecem byte a byte intactos. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q022 (além das demais dependências listadas nela).

### Q022 — Comparação e changeset

1. **Identificador:** Q022. **Estado:** pending.
2. **Objetivo:** Comparação e changeset; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q021=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/workspaces/changes.py`
   - Criar: `tests/integration/test_changes.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Comparar workspace atual com manifesto baseline, não confiar apenas em git diff/modelo. Enumerar novos arquivos/deleções e hashes, tratar rename como delete+add, binários com resumo. Recusar links/modes perigosos. Gerar artifact de diff redigido e digest canônico do manifesto para aprovação.
   **Entradas e saídas / interfaces:** compare(workspace_id:UUID)->ChangeSet (async); attach_verification(changeset:ChangeSet,evidence:tuple[VerificationEvidence,...])->ChangeSet.
6. **Critérios de aceitação:** Lista real de efeitos independente de narrativa e Git; changeset identifica exatamente bytes aprováveis.
7. **Testes necessários:** test_added_modified_deleted; test_new_binary_not_text_diff; test_unicode_and_metachar_names; test_model_claim_does_not_change_manifest; test_hash_changes_digest; test_dangerous_link_rejected.
   **Comando específico:** `uv run pytest tests/integration/test_changes.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Lista real de efeitos independente de narrativa e Git; changeset identifica exatamente bytes aprováveis. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q023 (além das demais dependências listadas nela).

### Q023 — Aplicação e recuperação de diff

1. **Identificador:** Q023. **Estado:** pending.
2. **Objetivo:** Aplicação e recuperação de diff; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q019=done, Q020=done, Q021=done, Q022=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/workspaces/apply.py`
   - Criar: `src/quill/workspaces/journal.py`
   - Criar: `tests/security/test_apply.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Verificar aprovação/digest, revalidar todos os hashes e condições de ausência antes de escrever. Journal/backups fora do sandbox, staging por volume, replace por arquivo e log de etapas. Falha parcial recupera somente conteúdo ainda igual ao escrito pelo Quill. Conflito preserva journal/backups e retorna recovery_required. Não mudar índice Git.
   **Entradas e saídas / interfaces:** apply(changeset_id:UUID,approval_id:UUID)->ApplyResult (async); recover(journal_id:UUID)->ApplyResult (async). Journal é durável antes do primeiro efeito.
6. **Critérios de aceitação:** Origem só recebe conteúdo aprovado; não existe rollback que apague edição externa; falha parcial é recuperável/explicitamente bloqueada.
7. **Testes necessários:** test_no_approval_no_write; test_origin_changed_zero_writes; test_add_collision_blocks; test_partial_failure_restores; test_recovery_preserves_external_edit; test_crash_journal_replay; test_index_unchanged.
   **Comando específico:** `uv run pytest tests/security/test_apply.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Origem só recebe conteúdo aprovado; não existe rollback que apague edição externa; falha parcial é recuperável/explicitamente bloqueada. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q024 (além das demais dependências listadas nela).

### Q024 — Transporte JSONL e RPC

1. **Identificador:** Q024. **Estado:** pending.
2. **Objetivo:** Transporte JSONL e RPC; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q006=done, Q009=done, Q023=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/codex/transport.py`
   - Criar: `src/quill/codex/protocol.py`
   - Criar: `tests/integration/test_codex_transport.py`
   - Criar: `tests/fixtures/codex/fake_server.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar transporte com factory de processo injetada; default real permanece desabilitado nesta tarefa. Parser incremental UTF8/JSONL, map de requests/Futures, timeout controle 30s e limite 8MiB. Drenar stderr redigido em paralelo. Diferenciar response/notification/server request conforme schemas reais. Fake server determinístico não acessa rede.
   **Entradas e saídas / interfaces:** JsonlTransport.request(method:str,params:dict[str,JsonValue])->JsonValue (async); notifications()->AsyncIterator[dict[str,JsonValue]]; respond(request_id:int,result:JsonValue)->None; close()->None (async).
6. **Critérios de aceitação:** Mensagens não se perdem ou misturam; nenhum log contamina stdout; timeout não reenvia request.
7. **Testes necessários:** test_fragmented_unicode; test_multiple_lines; test_out_of_order_responses; test_stderr_drained; test_oversize_or_invalid_json_closes; test_eof_fails_pending; test_unknown_request_safe_error.
   **Comando específico:** `uv run pytest tests/integration/test_codex_transport.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Mensagens não se perdem ou misturam; nenhum log contamina stdout; timeout não reenvia request. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q025 (além das demais dependências listadas nela).

### Q025 — Executor, sessões e eventos Codex

1. **Identificador:** Q025. **Estado:** pending.
2. **Objetivo:** Executor, sessões e eventos Codex; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q005=done, Q006=done, Q007=done, Q008=done, Q024=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/codex/executor.py`
   - Criar: `src/quill/codex/session.py`
   - Criar: `tests/integration/test_codex_executor.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Implementar CodexExecutor sobre transport injetado, matriz Q006 e policy builder; handshake, seleção explícita do Sol/low, thread por workspace/política e normalização dos eventos. Persistir execution/thread/turn. Fazer run em async generator. Até Q027/Q028 usar fake em todos os caminhos acionáveis da UI.
   **Entradas e saídas / interfaces:** inspect/run/cancel do Protocol; SessionKey(workspace_id,mode,profile_digest,model) impede retomada incompatível. Conclusão turno só inicia verificação independente.
6. **Critérios de aceitação:** Eventos internos completos/ordenados, sem fallback exec irrestrito e sem retomar sessão global por --last.
7. **Testes necessários:** test_initialize_once; test_catalog_low_required; test_wrong_thread_event_ignored; test_resume_only_matching_workspace; test_turn_terminal_not_process_exit; test_timeout_start_not_resubmitted; test_auth_and_usage_errors.
   **Comando específico:** `uv run pytest tests/integration/test_codex_executor.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Eventos internos completos/ordenados, sem fallback exec irrestrito e sem retomar sessão global por --last. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q026 (além das demais dependências listadas nela).

### Q026 — Aprovações do protocolo Codex

1. **Identificador:** Q026. **Estado:** pending.
2. **Objetivo:** Aprovações do protocolo Codex; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q019=done, Q020=done, Q025=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/codex/approvals.py`
   - Modificar: `src/quill/codex/executor.py`
   - Criar: `tests/security/test_codex_approvals.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Mapear apenas requests estáveis documentados na matriz Q006. Vincular request/thread/turn/item a ActionRequest e PermissionService. Negar escalada de sandbox no MVP. Tratar network approval como host/protocolo e não comando shell. Unknown request sem efeito; não acceptForSession ou auto-review.
   **Entradas e saídas / interfaces:** CodexApprovalRouter.handle(request:dict[str,JsonValue],execution_id:UUID)->dict[str,JsonValue] (async). Retorno usa decisão exata suportada pelo schema, não string inventada.
6. **Critérios de aceitação:** Nenhum request externo amplia escopo; resposta só libera item associado e decisão fica auditada.
7. **Testes necessários:** test_allowed_scoped_decision; test_escalation_denied; test_network_request_labeled; test_unknown_request_denied; test_expired_request_declined; test_late_accept_after_interrupt_ignored.
   **Comando específico:** `uv run pytest tests/security/test_codex_approvals.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Nenhum request externo amplia escopo; resposta só libera item associado e decisão fica auditada. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q027 (além das demais dependências listadas nela).

### Q027 — Supervisor de processos e cancelamento

1. **Identificador:** Q027. **Estado:** pending.
2. **Objetivo:** Supervisor de processos e cancelamento; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q007=done, Q008=done, Q024=done, Q025=done, Q026=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tasks/process_supervisor.py`
   - Criar: `src/quill/platforms/windows/jobs.py`
   - Modificar: `src/quill/codex/transport.py`
   - Criar: `tests/integration/test_process_cleanup.py`
   - Modificar: `pyproject.toml`
   - Modificar: `uv.lock`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Adicionar psutil para monitor/ownership. ProcessSupervisor usa start_new_session em POSIX e Job Object kill-on-close no Windows; associar antes de permitir filhos. Injetar supervisor no transporte real. Cancelamento: interrupt, 5s, terminate, 3s, kill; drenar pipes. Verificar auxiliares do Codex e impedir daemon fora de controle. PID+creation time/handles, nunca kill por nome.
   **Entradas e saídas / interfaces:** spawn(argv:tuple[str,...],cwd:Path,env:Mapping[str,str])->ManagedProcess; terminate_tree(handle:ManagedProcess)->None; close()->None (async). Capabilities informam quotas rígidas realmente disponíveis.
6. **Critérios de aceitação:** Zero processos de ownership da execução após cancelamento/fechamento; um daemon inacessível bloqueia integração real.
7. **Testes necessários:** test_parent_child_grandchild_exit; test_force_kill_stalled_tree; test_close_kills_owned_processes; test_pid_reuse_not_killed; test_codex_auxiliary_cleanup. Testes fake/fixture e probe real opt-in nos dois SOs.
   **Comando específico:** `uv run pytest tests/integration/test_process_cleanup.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Zero processos de ownership da execução após cancelamento/fechamento; um daemon inacessível bloqueia integração real. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q028 (além das demais dependências listadas nela).

### Q028 — Orquestrador, fila e recuperação

1. **Identificador:** Q028. **Estado:** pending.
2. **Objetivo:** Orquestrador, fila e recuperação; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q005=done, Q019=done, Q020=done, Q021=done, Q022=done, Q023=done, Q025=done, Q026=done, Q027=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tasks/orchestrator.py`
   - Criar: `src/quill/tasks/recovery.py`
   - Modificar: `src/quill/bootstrap.py`
   - Criar: `tests/integration/test_task_lifecycle.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Compor store/policy/workspace/executor/supervisor. Uma tarefa ativa global, fila 20, submission UUID UNIQUE e locks por projeto para aplicação. Persistir cada transição com evento; deadlines/approval pause não removem limite global. Recuperação startup marca não terminal interrupted e reconcilia journal, sem replay. Orquestrador expõe port para tools introduzida Q030.
   **Entradas e saídas / interfaces:** TaskOrchestrator.submit(task:TaskRecord)->None e cancel(task_id:UUID)->None (async); recover_on_startup()->tuple[TaskRecord,...]. Nenhuma execução real sem gates Q007/Q008/Q027.
6. **Critérios de aceitação:** Estados refletem trabalho real e sobrevivem restart; ação com efeito incerto nunca é reenviada automaticamente.
7. **Testes necessários:** test_single_active_and_queue; test_duplicate_submission_once; test_queue_limit; test_deadline_cancels; test_restart_marks_interrupted_no_replay; test_journal_pending_blocks_apply; test_disk_full_disables_submission.
   **Comando específico:** `uv run pytest tests/integration/test_task_lifecycle.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Estados refletem trabalho real e sobrevivem restart; ação com efeito incerto nunca é reenviada automaticamente. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q029 (além das demais dependências listadas nela).

### Q029 — Painel de execução e revisão

1. **Identificador:** Q029. **Estado:** pending.
2. **Objetivo:** Painel de execução e revisão; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q018=done, Q020=done, Q023=done, Q028=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/ui/qml/TaskPanel.qml`
   - Criar: `src/quill/ui/qml/DiffPanel.qml`
   - Modificar: `src/quill/ui/qml/Main.qml`
   - Modificar: `src/quill/ui/models.py`
   - Modificar: `src/quill/ui/bridge.py`
   - Modificar: `src/quill/bootstrap.py`
   - Criar: `tests/ui/test_task_review.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Conectar UI ao orquestrador real só após gates. Mostrar task ativa/fila, etapa real, cancelar, arquivos/diff/binários, evidências pass/fail/not verified. Aplicar cria aprovação vinculada; conflitos mostram recurso e mantêm original. Agregar deltas a 50ms sem perder terminais; não inventar porcentagem.
   **Entradas e saídas / interfaces:** Viewmodel consome ExecutionEvent/ChangeSet/VerificationEvidence; slots cancelTask(task_id), requestApply(changeset_id). Clique não executa shell nem contorna PermissionService.
6. **Critérios de aceitação:** Usuário acompanha/cancela e distingue diagnóstico de mudança aplicada; pipeline real permanece limitado ao workspace.
7. **Testes necessários:** test_progress_and_cancel; test_failed_test_not_success; test_diff_requires_approval; test_binary_summary; test_conflict_blocks_apply; test_terminal_not_lost_under_delta_load.
   **Comando específico:** `uv run pytest tests/ui/test_task_review.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Usuário acompanha/cancela e distingue diagnóstico de mudança aplicada; pipeline real permanece limitado ao workspace. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q030 (além das demais dependências listadas nela).

## Fase — Ferramentas e MVP

### Q030 — Registro de ferramentas e planejador

1. **Identificador:** Q030. **Estado:** pending.
2. **Objetivo:** Registro de ferramentas e planejador; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q019=done, Q020=done, Q025=done, Q028=done, Q029=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tools/registry.py`
   - Criar: `src/quill/tools/planner.py`
   - Criar: `schemas/tool-plan.schema.json`
   - Modificar: `src/quill/tasks/orchestrator.py`
   - Criar: `tests/security/test_tool_plans.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Registro estático sem imports por nome recebido. JSON schema v1 summary/actions/done, até 5 propostas; uma execução por vez, no máximo 8 ciclos/tarefa. Validar cada argumento pelo ToolSpec, recursos pelo policy e resultado pelo output schema. Segunda ação idêntica sem progresso bloqueia. Tool output retorna ao modelo como dado não confiável.
   **Entradas e saídas / interfaces:** ToolRegistry.register(tool:Tool)->None/get(name:str)->Tool; ToolPlanner.next(context:PlanningContext)->ToolPlan (async). PlanningContext contém task_id, pedido, specs permitidos e resultados redigidos, sem grants secretos.
6. **Critérios de aceitação:** Modelo só propõe ferramentas cadastradas; nenhuma ferramenta futura existe por string arbitrária.
7. **Testes necessários:** test_unknown_tool_denied; test_extra_properties_rejected; test_action_count_limit; test_no_eval_or_shell_conversion; test_repeat_without_progress_blocks; test_eight_cycles_limit; test_output_not_instruction.
   **Comando específico:** `uv run pytest tests/security/test_tool_plans.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Modelo só propõe ferramentas cadastradas; nenhuma ferramenta futura existe por string arbitrária. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q031 (além das demais dependências listadas nela).

### Q031 — Consultas de sistema e processos

1. **Identificador:** Q031. **Estado:** pending.
2. **Objetivo:** Consultas de sistema e processos; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q027=done, Q030=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tools/system.py`
   - Criar: `src/quill/tools/processes.py`
   - Modificar: `src/quill/tools/registry.py`
   - Criar: `tests/unit/test_system_tools.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Registrar system.info e processes.list; saída de psutil resumida/paginada (até 100 por chamada), PID/nome/status/cpu/memória. Tratar NoSuchProcess/AccessDenied individualmente. Não retornar env, memória, cmdline sensível nem ferramenta kill.
   **Entradas e saídas / interfaces:** ToolSpec version1 input/output fechados conforme tabela de contratos da arquitetura (unidades e paginação fixadas). system.info args vazios; processes.list cursor opcional/limit 1–100. Efeito read, timeout 5s.
6. **Critérios de aceitação:** Consulta nas duas plataformas sem privilégios, dados sensíveis ou erro global por processo isolado inacessível.
7. **Testes necessários:** test_process_disappears; test_access_denied_summarized; test_no_environment_or_cmdline; test_process_pagination; test_system_output_schema.
   **Comando específico:** `uv run pytest tests/unit/test_system_tools.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Consulta nas duas plataformas sem privilégios, dados sensíveis ou erro global por processo isolado inacessível. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q032 (além das demais dependências listadas nela).

### Q032 — Ferramentas de arquivos

1. **Identificador:** Q032. **Estado:** pending.
2. **Objetivo:** Ferramentas de arquivos; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q019=done, Q021=done, Q023=done, Q030=done, Q031=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tools/files.py`
   - Modificar: `src/quill/tools/registry.py`
   - Criar: `tests/security/test_file_tools.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Registrar files.list(root_id,relative_path), files.mkdir e files.move(root_id,source,destination). root_id resolve grant do usuário; campos e unidades seguem a tabela de contratos da arquitetura. Sem overwrite/remoção permanente, sem mover entre volumes no MVP. Operações por handles/no-follow, negar reparse/links inseguros. list até 100 resultados; não seguir árvore automaticamente.
   **Entradas e saídas / interfaces:** Tool implementations do Protocol; effect read/create/move com schemas separados. Digest e recursos revalidados na execução, não só ao planejar.
6. **Critérios de aceitação:** Somente diretório aprovado muda; colisão/ambiguidade bloqueia sem efeitos parciais ou fuga de escopo.
7. **Testes necessários:** test_traversal_and_prefix_escape; test_symlink_escape; test_windows_junction_rejected; test_existing_destination_not_overwritten; test_cross_volume_denied; test_revalidate_path_race; test_auto_grant_only_scoped_operations.
   **Comando específico:** `uv run pytest tests/security/test_file_tools.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Somente diretório aprovado muda; colisão/ambiguidade bloqueia sem efeitos parciais ou fuga de escopo. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q033 (além das demais dependências listadas nela).

### Q033 — Catálogo e abertura de aplicativos

1. **Identificador:** Q033. **Estado:** pending.
2. **Objetivo:** Catálogo e abertura de aplicativos; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q017=done, Q019=done, Q030=done, Q032=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tools/applications.py`
   - Criar: `src/quill/platforms/linux/applications.py`
   - Criar: `src/quill/platforms/windows/applications.py`
   - Modificar: `src/quill/tools/registry.py`
   - Criar: `tests/security/test_app_launch.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Registrar applications.open(application_id). Catálogo explícito por seleção do usuário: Linux desktop ID validado/launcher nativo, Windows executable path canônico + argv fixo. Não interpretar nome de app como comando nem aceitar args arbitrários do modelo. DesktopAdapter recebe catálogo injetado.
   **Entradas e saídas / interfaces:** open_application(application_id:str)->LaunchResult (async). accepted significa lançamento aceito, não confirmação de que a aplicação terminou sua tarefa. Tool timeout 10s.
6. **Critérios de aceitação:** Aplicativo permitido abre com consentimento; binário inexistente/alterado não ganha fallback para shell.
7. **Testes necessários:** test_only_registered_application; test_metacharacters_not_shell; test_changed_executable_requires_review; test_missing_application_reports_error; test_fake_app_sentinel_only. Manual abrir app escolhido nos dois SOs.
   **Comando específico:** `uv run pytest tests/security/test_app_launch.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Aplicativo permitido abre com consentimento; binário inexistente/alterado não ganha fallback para shell. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q034 (além das demais dependências listadas nela).

### Q034 — Logs delimitados e terminal sandboxed

1. **Identificador:** Q034. **Estado:** pending.
2. **Objetivo:** Logs delimitados e terminal sandboxed; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q007=done, Q008=done, Q019=done, Q027=done, Q030=done, Q033=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tools/logs.py`
   - Criar: `src/quill/tools/terminal.py`
   - Modificar: `src/quill/tools/registry.py`
   - Criar: `tests/security/test_terminal_tools.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Registrar logs.read(file_id,offset,limit<=1MiB) para arquivo selecionado e redigido; terminal.run(argv,cwd_workspace_id,timeout<=120s) com aprovação por comando e sandbox. Terminal não executa no host/na origem e nunca entra em restricted_auto. Limitar stdout/stderr redigidos, retornar exit code/evidência.
   **Entradas e saídas / interfaces:** logs.read effect read; terminal.run effect execute/risk high. argv lista não vazia de strings, sem shell=True; scripts/intérpretes continuam código não confiável isolado.
6. **Critérios de aceitação:** Terminal não amplia fronteira de código; logs não vazam segredo nem fazem leitura ilimitada.
7. **Testes necessários:** test_log_limit_and_redaction; test_terminal_approval_required; test_terminal_not_allowed_in_auto; test_shell_metachar_literal; test_outside_workspace_denied; test_timeout_tree_cleanup.
   **Comando específico:** `uv run pytest tests/security/test_terminal_tools.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Terminal não amplia fronteira de código; logs não vazam segredo nem fazem leitura ilimitada. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q035 (além das demais dependências listadas nela).

### Q035 — Aceitação completa do MVP

1. **Identificador:** Q035. **Estado:** pending.
2. **Objetivo:** Aceitação completa do MVP; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q015=done, Q016=done, Q023=done, Q028=done, Q029=done, Q030=done, Q031=done, Q032=done, Q033=done, Q034=done
4. **Arquivos envolvidos:**
   - Criar: `tests/integration/test_mvp.py`
   - Criar: `tests/fixtures/projects/auth401/`
   - Modificar: `docs/TESTING.md`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Escopo fixture: cliente Python com Authorization omitido, transporte fake e testes de regressão descritos em TESTING. Cenário integrado fake automático + Codex real opt-in em Linux/Windows. Registrar estado anterior, falha reproduzida, correção, teste posterior, diff, aprovação e aplicação. Exercitar mkdir/move/app/processes consentidos. Não alterar produção para fazer fixture passar.
   **Entradas e saídas / interfaces:** Consome todos os contratos Q001–Q034; produz relatório de aceitação em TESTING com plataforma/versões/comandos/evidências. Arte final provisória deve ser declarada e bloqueia release visual, não inventar aprovação artística.
6. **Critérios de aceitação:** MVP aceito somente com Linux GNOME/Wayland e Windows11 reais; testes pass/fail e origem preservada antes de aprovação documentados.
7. **Testes necessários:** test_auth401_snapshot_fix_review_apply; test_denied_apply_preserves_original; test_source_changes_during_review; test_desktop_permissions_end_to_end; test_cancel_then_restart_no_duplicate. Testes reais marcados live_codex.
   **Comando específico:** `uv run pytest tests/integration/test_mvp.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** MVP aceito somente com Linux GNOME/Wayland e Windows11 reais; testes pass/fail e origem preservada antes de aprovação documentados. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q036 (além das demais dependências listadas nela).

## Fase — Refinamento

### Q036 — Configurações, histórico e acessibilidade

1. **Identificador:** Q036. **Estado:** pending.
2. **Objetivo:** Configurações, histórico e acessibilidade; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q035=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/ui/qml/SettingsPanel.qml`
   - Criar: `src/quill/ui/qml/HistoryPanel.qml`
   - Criar: `src/quill/ui/qml/Theme.qml`
   - Modificar: `src/quill/ui/qml/Main.qml`
   - Modificar: `src/quill/ui/models.py`
   - Modificar: `src/quill/ui/bridge.py`
   - Criar: `tests/ui/test_settings.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Centralizar tokens de AVATAR_DESIGN, theme system/light/dark, fonte/escala e reduced motion. Config visual não amplia grants. Histórico/logs paginados redigidos, limpeza com confirmação para dados não aplicados. Teclado/Accessible.name e foco visível. Contraste >=4.5:1 medido; ajustar tons por papel se necessário.
   **Entradas e saídas / interfaces:** Settings slots usam ConfigService; History model usa MemoryStore e cursor. Sem leitura de arquivo/banco no QML.
6. **Critérios de aceitação:** UI consistente, acessível e sem crescimento sustentado de memória; não reduzir passos de permissão por estética.
7. **Testes necessários:** test_theme_persistence; test_reduced_motion; test_history_pagination; test_cleanup_preserves_unapplied; test_keyboard_approval_not_accidental. Manual tema/escala/contraste e 100 ciclos painel.
   **Comando específico:** `uv run pytest tests/ui/test_settings.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** UI consistente, acessível e sem crescimento sustentado de memória; não reduzir passos de permissão por estética. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q037 (além das demais dependências listadas nela).

### Q037 — Notificações e autostart opt-in

1. **Identificador:** Q037. **Estado:** pending.
2. **Objetivo:** Notificações e autostart opt-in; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q017=done, Q028=done, Q036=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/desktop/notifications.py`
   - Criar: `src/quill/desktop/autostart.py`
   - Modificar: `src/quill/ui/qml/SettingsPanel.qml`
   - Modificar: `src/quill/ui/bridge.py`
   - Modificar: `src/quill/platforms/linux/desktop.py`
   - Modificar: `src/quill/platforms/windows/desktop.py`
   - Criar: `tests/integration/test_desktop_lifecycle.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Notificações nativas por backend disponível; Linux D-Bus notifications/portal, Windows backend validado Qt/Win32 sem exigir tray para reabrir. Autostart opt-in: entrada XDG por usuário ou Windows Startup shortcut. Desativar remove só entrada do Quill; nunca alterar política global. Startup não repete tarefa interrompida.
   **Entradas e saídas / interfaces:** set_autostart(enabled:bool)->None (async); DesktopAdapter.notify. Capabilities refletem suporte de sessão, não só presença da biblioteca.
6. **Critérios de aceitação:** Notificação abre tarefa correta; usuário consegue sair/reabrir; autostart reversível e consentido.
7. **Testes necessários:** test_autostart_disabled_by_default; test_toggle_idempotent; test_disable_only_own_entry; test_notification_no_secret; test_restart_no_task_replay; test_reopen_without_tray. Manual login nos dois SOs.
   **Comando específico:** `uv run pytest tests/integration/test_desktop_lifecycle.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Notificação abre tarefa correta; usuário consegue sair/reabrir; autostart reversível e consentido. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q038 (além das demais dependências listadas nela).

### Q038 — Automação de navegador isolada

1. **Identificador:** Q038. **Estado:** pending.
2. **Objetivo:** Automação de navegador isolada; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q019=done, Q027=done, Q030=done, Q037=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/tools/browser.py`
   - Modificar: `src/quill/tools/registry.py`
   - Criar: `tests/security/test_browser_tools.py`
   - Modificar: `pyproject.toml`
   - Modificar: `uv.lock`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Adicionar Playwright em extra browser, não core. Perfil temporário sem cookies do usuário, download do browser consentido/checksum de pacote oficial. Ferramentas navigate/read e ações explícitas submit/download com grants separados; negar file:// e rede não aprovada. Browser fechado pelo supervisor no cancelamento.
   **Entradas e saídas / interfaces:** BrowserTool Protocols com contexto por tarefa; saída redigida e páginas como dados não confiáveis. Nenhuma extensão de navegador global.
6. **Critérios de aceitação:** Navegador não reutiliza sessão pessoal e não envia formulário/download sem política específica.
7. **Testes necessários:** test_isolated_profile; test_file_url_denied; test_form_submit_requires_approval; test_download_scoped; test_prompt_injection_does_not_grant; test_browser_closed_on_cancel. Servidor HTTP local fixture apenas.
   **Comando específico:** `uv run pytest tests/security/test_browser_tools.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Navegador não reutiliza sessão pessoal e não envia formulário/download sem política específica. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q039 (além das demais dependências listadas nela).

## Fase — Voz

### Q039 — Captura e reconhecimento local

1. **Identificador:** Q039. **Estado:** pending.
2. **Objetivo:** Captura e reconhecimento local; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q009=done, Q027=done, Q038=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/voice/capture.py`
   - Criar: `src/quill/voice/stt.py`
   - Modificar: `src/quill/ui/qml/SettingsPanel.qml`
   - Modificar: `src/quill/ui/bridge.py`
   - Criar: `tests/integration/test_stt.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Push-to-talk com QtMultimedia; desativado por default. whisper.cpp externo com modelo base multilíngue/idioma pt, path/checksum configurados após download consentido. Capturar mono 16kHz quando suportado, converter explicitamente; buffer máximo 30s e sem persistência padrão. Subprocesso supervisionado cancelável, sem dependência ML no core.
   **Entradas e saídas / interfaces:** VoiceCapture.start/stop/cancel->AudioBuffer; SttService.transcribe(buffer)->str (async). AudioBuffer contém bytes PCM/sample_rate/channels, não arquivo pessoal.
6. **Critérios de aceitação:** Sem captura ao abrir app; texto reconhecido é editável antes do envio e não autoriza ações por voz automaticamente.
7. **Testes necessários:** test_microphone_opt_in; test_buffer_limit; test_cancel_discards_audio; test_fake_stt_portuguese; test_missing_model_clear_error. Teste real consentido com gravação curta e evidência de não retenção.
   **Comando específico:** `uv run pytest tests/integration/test_stt.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Sem captura ao abrir app; texto reconhecido é editável antes do envio e não autoriza ações por voz automaticamente. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q040 (além das demais dependências listadas nela).

### Q040 — Síntese local e sincronização

1. **Identificador:** Q040. **Estado:** pending.
2. **Objetivo:** Síntese local e sincronização; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q011=done, Q027=done, Q039=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/voice/tts.py`
   - Criar: `src/quill/voice/playback.py`
   - Modificar: `src/quill/ui/bridge.py`
   - Modificar: `src/quill/avatar/state.py`
   - Criar: `tests/integration/test_tts.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Piper externo opcional com modelo pt selecionado/licença registrada. Entrada de texto por stdin, saída áudio para memória ou temporário privado apagado em finally. Playback QtMultimedia; envelope 50ms aciona speaking. Nova captura/interrupção silencia playback e cancela processo, sem cancelar tarefa de código.
   **Entradas e saídas / interfaces:** TtsService.speak(text:str)->None e stop()->None (async); PlaybackService.play(buffer)/stop. Personalidade afeta texto, nunca grants.
6. **Critérios de aceitação:** Voz desativável a qualquer momento, sem arquivo de áudio permanente ou loop STT/TTS.
7. **Testes necessários:** test_missing_piper_optional; test_stop_interrupts_playback; test_new_capture_stops_tts; test_no_audio_retention; test_envelope_updates_avatar; test_license_manifest_required. Real offline após download consentido.
   **Comando específico:** `uv run pytest tests/integration/test_tts.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Voz desativável a qualquer momento, sem arquivo de áudio permanente ou loop STT/TTS. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q041 (além das demais dependências listadas nela).

### Q041 — Ativação opcional por frase

1. **Identificador:** Q041. **Estado:** pending.
2. **Objetivo:** Ativação opcional por frase; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q039=done, Q040=done
4. **Arquivos envolvidos:**
   - Criar: `src/quill/voice/activation.py`
   - Modificar: `src/quill/ui/qml/SettingsPanel.qml`
   - Modificar: `src/quill/ui/bridge.py`
   - Criar: `tests/unit/test_activation.py`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Usar mesma infraestrutura STT em janelas curtas, frase padrão “Quill, pode ouvir”, opt-in separado de voz. Processar localmente com buffer circular máximo 5s; ativação abre captura, nunca executa comando diretamente. Pausar durante TTS e lock; cooldown 3s. Se hardware não sustentar carga, manter push-to-talk e registrar limitação.
   **Entradas e saídas / interfaces:** ActivationService.enable/disable/on_transcript; evento activation_detected apenas abre estado listening. No cloud fallback.
6. **Critérios de aceitação:** Nenhuma gravação persistida nem envio automático após wake; resultado de desempenho/privacidade documentado.
7. **Testes necessários:** test_disabled_never_captures; test_phrase_exact_normalized; test_cooldown; test_paused_during_tts_and_lock; test_activation_does_not_submit_command. Medir falso acionamento/cpu em sessão consentida.
   **Comando específico:** `uv run pytest tests/unit/test_activation.py -q`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Nenhuma gravação persistida nem envio automático após wake; resultado de desempenho/privacidade documentado. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q042 (além das demais dependências listadas nela).

## Fase — Distribuição

### Q042 — Builds e CI por plataforma

1. **Identificador:** Q042. **Estado:** pending.
2. **Objetivo:** Builds e CI por plataforma; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q035=done, Q036=done, Q037=done, Q038=done, Q039=done, Q040=done, Q041=done
4. **Arquivos envolvidos:**
   - Criar: `packaging/linux/`
   - Criar: `packaging/windows/`
   - Criar: `.github/workflows/ci.yml`
   - Modificar: `pyproject.toml`
   - Modificar: `uv.lock`
   - Modificar: `docs/TESTING.md`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Escopo diretórios: specs pyside6-deploy, scripts build e recursos de instalação por plataforma, sem binários rastreados. Adicionar dependências de build em grupo próprio. CI ubuntu/windows Python3.13 executa sync frozen/lint/type/tests fake. Builds nativos incluem QML/Qt plugins/assets e extensão GNOME separada. Não incluir banco/workspaces/config pessoal. Licença de código/arte precisa estar definida antes de binário público; ausência é blocked, sem inventar licença.
   **Entradas e saídas / interfaces:** Build command documentado por SO produz diretório standalone e manifest de conteúdo. CI não usa credenciais Codex e não certifica GNOME real.
6. **Critérios de aceitação:** Artefatos nativos abrem sem ambiente dev; arte provisória/licença não resolvida bloqueia release, assinatura ausente declarada.
7. **Testes necessários:** test_packaged_resource_manifest via verificação de build; smoke install/open/version/uninstall em ambiente limpo Linux/Windows; CI gates passam e arquivos sensíveis ausentes.
   **Comando específico:** `Checks de build/release nativos descritos acima, mais a suíte geral; registrar cada comando concreto usado.`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Artefatos nativos abrem sem ambiente dev; arte provisória/licença não resolvida bloqueia release, assinatura ausente declarada. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Q043 (além das demais dependências listadas nela).

### Q043 — Release e atualização manual verificável

1. **Identificador:** Q043. **Estado:** pending.
2. **Objetivo:** Release e atualização manual verificável; produzir a capacidade descrita abaixo, sem implementar tarefas seguintes.
3. **Pré-requisitos:** Q042=done
4. **Arquivos envolvidos:**
   - Criar: `docs/RELEASING.md`
   - Criar: `packaging/release_manifest.json`
   - Modificar: `README.md`
   - Modificar somente o progresso desta entrada em `docs/TASKS.md`.
5. **Instruções técnicas:** Documentar versionamento, changelog, hashes SHA256, licenças de dependências/modelos/assets, instalação/desinstalação, backup de banco e atualização manual. Manifest descreve versão/OS/arquitetura/hash/local do artefato sem segredos. Não implementar auto-updater privilegiado. Publicar release somente com autorização específica da sessão e todos os gates; esta tarefa pode preparar candidato sem publicá-lo.
   **Entradas e saídas / interfaces:** Procedimento reproduzível de release candidate e rollback de binário compatível; schema novo nunca é aberto pelo binário antigo sem verificação.
6. **Critérios de aceitação:** Candidato documentado verificável; nenhuma promessa de assinatura inexistente, licença presumida ou atualização automática; publicação separada quando autorizada.
7. **Testes necessários:** Verificar hashes independentes, instalar candidato em ambos SOs, preservar dados na desinstalação, simular migração falha/rollback e testar instruções desde ambiente limpo. Registrar comandos exatos em RELEASING.
   **Comando específico:** `Checks de build/release nativos descritos acima, mais a suíte geral; registrar cada comando concreto usado.`
   Rodar também os checks gerais pertinentes de [TESTING.md](TESTING.md); opt-in explícito para live_codex e evidência nativa onde exigida.
8. **Comportamento esperado:** Candidato documentado verificável; nenhuma promessa de assinatura inexistente, licença presumida ou atualização automática; publicação separada quando autorizada. Em falha, emitir ErrorInfo compatível e preservar recursos fora do escopo; não ampliar permissão, reenviar efeito incerto ou substituir arquitetura.
9. **Condição de conclusão:** C0 e todos os critérios acima. **Recuperação:** preservar alterações anteriores; interromper/limpar recursos da própria tarefa com finally; se requisito nativo/contrato falhar, registrar blocked com evidência e procedimento necessário, sem workaround inseguro.
   **Evidências:** ainda não executada; nenhum teste de aplicativo atribuído a esta tarefa.
10. **Dependências para a próxima tarefa:** Nenhuma tarefa adicional autorizada; release público exige autorização específica..
