# Quill

Assistente pessoal desktop com um furão 2D animado, chat em linguagem natural e integração com o Codex instalado no computador.

**Estado: fundação implementada; interface desktop ainda não disponível.** Q001–Q007 concluídas, incluindo contrato Codex beta autorizado e isolamento Linux validado. Q008 aguarda testes nativos no Windows 11. Consulte TASKS.md para evidências e impedimentos.

## Objetivo

Receber pedidos como “investigue o erro 401, corrija e verifique”, trabalhar em um snapshot isolado e apresentar diagnóstico, testes e diff antes de aplicar mudanças ao projeto original. Também abrir aplicativos cadastrados, organizar arquivos em diretórios autorizados e consultar processos.

Quill terá uma identidade visual de furão inspirado na silhueta e nas chamas de Cyndaquil e Quilava. O personagem terá arte própria, animações, expressões e voz opcional. Não existem assets de produção nesta entrega.

## Plataformas

| Plataforma | Compromisso |
|---|---|
| Manjaro x86_64, GNOME 50, Wayland | MVP completo com extensão GNOME; validação nativa obrigatória |
| Windows 11 x86_64 | MVP completo com janela Qt e adaptador nativo; validação nativa obrigatória |
| Linux X11 e outros compositores Wayland | Backend Qt por capacidades; recursos não validados não são anunciados como suportados |
| macOS | Arquitetura preparada; implementação e release posteriores |
| Mobile, BSD e sistemas sem Qt/Codex compatíveis | Fora da versão inicial |

Portabilidade do núcleo não significa igualdade de recursos em qualquer sistema operacional. A extensão GNOME não será usada no Windows; o aplicativo Windows não exige extensão do Explorer.

## Tecnologias e requisitos planejados

- Python 3.13 gerenciado pelo uv; não modificar o Python do sistema.
- PySide6 6.12 e QML; dependências e patches resolvidos por fase e fixados em uv.lock.
- Codex CLI compatível, autenticação configurada pelo próprio Codex e acesso ao modelo selecionado.
- Git para projetos de código e SQLite para histórico local.
- GNOME Shell 50 para a primeira extensão certificada.
- Ferramentas nativas de build por plataforma somente na fase de distribuição.

O aplicativo é local; o raciocínio pelo Codex pode enviar conteúdo autorizado ao provedor e requer rede. Voz local funcionará offline depois de baixar os modelos. Não há promessa de assistente completamente offline.

## Segurança

Leitura, assistido e automático restrito terão políticas diferentes. Snapshot não substitui sandbox. Falta de isolamento bloqueia execução; jamais habilita acesso irrestrito. Mudanças no projeto original exigem revisão e aprovação. Exclusão permanente e operações privilegiadas não fazem parte do MVP.

Veja [SECURITY.md](docs/SECURITY.md) antes de executar qualquer tarefa que interaja com o computador.

## Documentação

- [Arquitetura e contratos](docs/ARCHITECTURE.md)
- [Plano de implementação](docs/IMPLEMENTATION_PLAN.md)
- [Backlog executável](docs/TASKS.md)
- [Segurança](docs/SECURITY.md)
- [Avatar e interface](docs/AVATAR_DESIGN.md)
- [Integração Codex](docs/CODEX_INTEGRATION.md)
- [Testes e conclusão](docs/TESTING.md)
- [Instruções para agentes](AGENTS.md)

## Roadmap

1. Q001–Q005: fundação, configuração, logs, contratos e persistência.
2. Q006–Q009: protocolo, sandbox Linux/Windows e janela Qt.
3. Q010–Q017: avatar Qt, extensão GNOME e integração Windows.
4. Q018–Q020: conversa e permissões.
5. Q021–Q029: snapshots, Codex, cancelamento, recuperação e revisão.
6. Q030–Q035: ferramentas do desktop e aceitação do MVP nas duas plataformas.
7. Q036–Q038: refinamento, notificações, autostart e navegador.
8. Q039–Q041: voz local opcional.
9. Q042–Q043: empacotamento e distribuição verificável.

Para validar a fundação (ainda sem janela desktop):

```text
uv sync --frozen --group dev
uv run python -m quill --version
uv run pytest -q
```

O comando de versão imprime 0.1.0. O avatar/chat será introduzido nas próximas fases; não há assistente desktop completo nesta versão.

## Próxima execução

Desbloquear **Q008 — probes Windows nativos** conforme [instruções](docs/CODEX_INTEGRATION.md). Após aprovação do gate, continuar Q009 por etapas validadas, conforme autorização vigente registrada em AGENTS.md.

## Repositório e publicação

Destino autorizado: [williamdealmeid4/quill](https://github.com/williamdealmeid4/quill), público. Nunca publicar configurações pessoais, tokens, workspaces ou histórico. Licenciamento do código e dos assets deve ser definido antes de distribuir binários; a publicação deste planejamento não concede licença sobre personagens de terceiros.

Especificação v1, 2026-11-11.
