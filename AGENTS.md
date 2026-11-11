# Instruções permanentes para o executor do Quill

## Leitura obrigatória e autoridade

Leia integralmente este arquivo, [ARCHITECTURE.md](docs/ARCHITECTURE.md), [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) e [TASKS.md](docs/TASKS.md) antes de modificar código. Leia também os documentos canônicos citados pela tarefa. Não substitua leitura por busca de trechos.

O pedido atual do usuário prevalece. Não transforme um pedido de planejamento em implementação do aplicativo. A entrega inicial é documental; Q001 continua pendente até uma execução dedicada. O plano será executado com Sol disponível na conta e esforço low, confirmado pela plataforma; não há identificador de modelo fixo presumido.

## Unidade de trabalho

1. Inspecione diretório, branch, git status --short --branch, git diff e git diff --cached.
2. Se houver mudanças preexistentes, preserve-as. Não faça stash, reset, clean ou checkout forçado.
3. Selecione somente a primeira tarefa pending cuja lista completa de dependências esteja done.
4. Marque a tarefa in_progress, registrando início e escopo. Trabalhe somente nos caminhos enumerados; diretórios enumerados têm limites definidos na tarefa.
5. Quando introduzir pacote Python, crie seu __init__.py. Essa é a única inclusão de scaffolding implícita permitida.
6. Implemente, rode os testes previstos e corrija erros introduzidos.
7. Atualize status e evidências; informe arquivos alterados, comandos, resultados e próxima tarefa.
8. Pare. Não execute a próxima tarefa na mesma solicitação.

Estados: pending, in_progress, blocked, done. Falha de ambiente ou ambiguidade relevante exige blocked com motivo, evidência e requisito de desbloqueio; nunca improvisar uma solução arquitetural.

## Arquitetura

- Python 3.13, layout src, PySide6/QML, SQLite e adaptadores por plataforma.
- Dependências entram somente na tarefa que as utiliza, com atualização do lockfile e justificativa.
- O contrato canônico é ARCHITECTURE.md; protocolo externo pertence a CODEX_INTEGRATION.md.
- Nenhuma operação de rede, disco demorada, SQLite ou subprocesso na thread da UI.
- QML só apresenta estado e emite intenções. Não executa shell nem decide permissões.
- A extensão GNOME só apresenta o avatar e envia intenções limitadas ao Python.
- Não adicionar servidor HTTP, microsserviços, frameworks de agentes ou ORM.
- Não importar bibliotecas Windows no Linux ou dependências GNOME no Windows.

## Padrões

Código e nomes técnicos em inglês; documentação e mensagens ao usuário em português. Funções públicas tipadas, DTOs dataclass frozen/slots e Protocol nos limites. Use Path internamente, UUID para IDs, datetime UTC para eventos e relógio monotônico para deadlines. Não usar Any como escape de tipagem; JSON externo tem alias recursivo e validação antes do cast.

Ruff check e format, mypy strict, pytest. Documente propósito e invariantes; evite comentários que apenas repetem código. Capture exceções específicas. Converter falhas externas em DomainError com código, descrição redigida, retryable e detalhes seguros. Não engolir CancelledError.

## Segurança inegociável

- Nunca usar danger-full-access, bypass de sandbox, sudo, execução administrativa ou shell=True.
- Nunca executar texto do modelo, arquivo ou página como comando.
- Snapshot não é sandbox. Recusar execução se o isolamento exigido falhar.
- Codex escreve somente no workspace; aplicação na origem exige aprovação de changeset e hashes atuais.
- Diretórios e argumentos devem ser validados no momento da execução, não apenas ao planejar.
- Não herdar credenciais, plugins, MCPs ou hooks pessoais sem inventário e autorização.
- Não ler auth.json ou copiar tokens; usar o fluxo de autenticação do Codex.
- Testes usam diretórios temporários e projetos fixture, jamais repositórios pessoais.
- Não reduzir segurança para fazer um teste passar.
- Não criar automação recursiva de agentes; uma tarefa ativa global no MVP.

## Verificação e evidências

Após Q001, comandos padrão, a partir da raiz:

```text
uv sync --frozen --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src/quill
uv run pytest -q
```

Rode ainda os testes específicos da tarefa e gates nativos aplicáveis. Tests skipped não validam outra plataforma. Integrações reais com Codex/rede/microfone exigem opt-in. Informe falhas e limitações, sem declarar conclusão por inferência.

Cada registro done em TASKS.md contém: data UTC, comandos, exit codes, contagem de testes e evidência manual quando necessária. Código de retorno zero de processo não comprova que o problema de produto foi corrigido.

## Git e publicações

Um commit focado por tarefa concluída, usando feat:, fix:, test:, docs: ou chore:. Stage apenas arquivos relacionados. Não incluir alterações preexistentes de outra finalidade. Sem force push.

A autorização inicial cobre criar e publicar o repositório público williamdealmeid4/quill com os nove documentos. Não cobre futuros pushes de implementação, merge, release ou publicação de credenciais. Para futuras ações, usar a autorização aplicável à sessão. Não criar PR ou merge sem verificação fresca.

## Handoff para Sol Low

> Leia integralmente AGENTS.md, docs/ARCHITECTURE.md, docs/IMPLEMENTATION_PLAN.md e docs/TASKS.md. Inspecione o Git e preserve alterações preexistentes. Execute somente Q001 conforme arquivos, contratos e critérios documentados. Rode as verificações previstas, registre resultados em docs/TASKS.md e informe a próxima tarefa. Se houver ambiguidade relevante ou pré-requisito ausente, registre o impedimento e pare. Não implemente Q002.


## Autorização vigente da sessão — 2026-11-11

O usuário autorizou continuar por etapas sucessivas e usar permission profiles beta para desbloquear Q006–Q008. Isso substitui a parada automática após uma tarefa: validar/commitar cada unidade antes de avançar, preservando dependências e gates. A exceção beta é somente a seleção de perfil descrita na revisão de CODEX_INTEGRATION.md. Não pedir novamente a mesma autorização nem reduzir proteção para contornar novo impedimento.


## Revisão autorizada — avanço Linux com Windows pendente

O usuário pediu passar à próxima fase e confirmou a implementação. Q009 depende de Q007 validada, sem esperar Q008. O critério de conclusão desta etapa passa a ser bootstrap/worker no Linux, com teste automático e smoke Wayland; certificação Windows permanece em Q008/Q016/Q035 e não é inferida de testes Linux. Q010–Q015 podem prosseguir pelas dependências locais. Não habilitar execução Codex Windows nem anunciar suporte Windows antes dos gates nativos. O MVP/release multiplataforma mantém as exigências originais.

Instalar PySide6-Essentials 6.12.0 (mesmo namespace PySide6 e módulos QtCore/Gui/Qml/Quick/Controls/Network/DBus) para não puxar WebEngine/PDF sem uso. Addons entram somente quando uma fase precisar. Contratos e desenho Qt permanecem os aprovados. Uma prévia artística por imagegen foi tentada e rejeitada pela ferramenta; não foi produzida nem incorporada. Fixture técnico de Q010 não significa aprovação da arte final.
