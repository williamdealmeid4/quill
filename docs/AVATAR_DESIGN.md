# Avatar e interface do Quill

Especificação v1 — 2026-11-11. Design planejado; esta entrega não inclui imagens, sprites nem aplicativo.

## Direção visual

Quill é um furão expressivo, com corpo alongado, focinho curto, patas pequenas e cauda visível. Referências fornecidas: Cyndaquil e Quilava, combinando silhueta compacta, postura ágil e chamas nas costas. Produzir desenho próprio coerente entre frames; não usar screenshots/arquivos extraídos de jogos como assets distribuídos.

Dorso azul-petróleo escuro, ventre creme, olhos escuros com brilho e chamas coral/âmbar. Chamas comunicam energia, sem piscar agressivamente ou significar que o computador está em risco. Escala de cinzas deve manter silhueta e expressões distinguíveis. Erro/aprovação são também texto/ícone, nunca só cor.

Uma direção de arte, uma vista principal em três quartos e poses compatíveis. Alternar avatars é futuro, mas renderer não contém nome Quill hardcoded: seleciona manifest por ID validado.

## Formato e organização

```text
assets/avatars/quill/
  manifest.json
  atlas-0.png
  atlas-1.png
  preview.png
  ATTRIBUTION.md
```

PNG RGBA sRGB, frame 256×256, atlas máximo 2048×2048 e até quatro atlas (64 MiB RGBA decodificados no máximo). Margem transparente 2 px entre células; frameWidth/frameHeight excluem padding. Âncora fixa em todas as poses. Fontes editáveis e arquivos de criação ficam fora do pacote runtime e entram depois de produção artística aprovada.

schema_version=1; caminhos relativos dentro do diretório selecionado, sem URLs ou traversal. Manifest inclui id, display_name, author, license, frame_size, anchor, hit_region, atlases e states. Cada frame referencia atlas, x, y, width e height. states mapeia nome para frames, fps, loop, next_state. Obrigatórios: idle, listening, thinking, working, awaiting_approval, success, confused, error, speaking.

Contrato AvatarPresentation: state:AvatarState, visible:bool, size_px:int, bubble:str|None, reduced_motion:bool, revision:int. Estado só vem do Animation State Manager; renderer não interpreta texto do modelo.

Exemplo de entrada de estado, não um manifesto completo:

```json
{"idle":{"frames":[{"atlas":"atlas-0.png","x":2,"y":2,"width":256,"height":256}],"fps":12,"loop":true,"next_state":null}}
```

Q010 usa um fixture técnico original e visivelmente provisório, criado como desenho geométrico simples; não afirma que é arte final. Se não houver arte de produção aprovada em Q035, MVP pode ser testado com fixture, mas release visual é bloqueada até substituir por produção com os mesmos contratos.

## Estados e tempo

| Estado | Frames alvo | FPS | Loop/transição |
|---|---:|---:|---|
| idle | 12 | 12 | Respiração/chama suave, loop |
| listening | 8 | 12 | Atenção, loop |
| thinking | 12 | 12 | Olhar/cabeça suave, loop |
| working | 18 | 18 | Movimento discreto, loop |
| awaiting_approval | 8 | 8 | Pose de espera, loop; sinal persiste |
| success | 12 | 18 | Uma execução, depois idle ou estado ativo |
| confused | 8 | 12 | Uma execução; dúvida textual persiste |
| error | 8 | 12 | Uma execução, depois pose estática; erro persiste |
| speaking | 8 | 12 | Ciclo de boca; futuro envelope de áudio |

Prioridade: error > awaiting_approval > working/thinking > speaking/listening > success/confused > idle. Uma tarefa não pode ser considerada concluída porque terminou uma animação. Sucesso dura no máximo 1 s antes de seguir estado atual. Chamada on_event tem relógio injetável e não usa random global em testes.

Piscar a cada 3–7 s com gerador injetado; não precisa de tracking global do mouse. Head/eye movement inicialmente pré-animado. Oculto, sessão bloqueada ou desktop sem apresentação: parar timer de frames, não apenas reduzir opacidade. Movimento reduzido usa primeiro frame/pose e texto.

## Renderers

Qt: Avatar.qml usa AnimatedSprite quando o atlas permitir sequência regular; manifest loader normaliza frames irregulares para uma sequência de recortes sem carregar imagem por frame. Não interpolar entre poses diferentes; smooth para escala. Sem shaders customizados na v1.

GNOME: GJS carrega texturas uma vez, desenha atores com recorte de frame e um único timer por mascote. Não embutir QML/WebView no Shell. A tarefa Q015 valida APIs Clutter/St disponíveis no GNOME 50; se a API de recorte/texture for incompatível, registrar impedimento antes de inventar renderer alternativo.

Só um renderer de mascote ativo: extensão GNOME disponível → esconder AvatarWindow Qt; desconectada → fallback Qt. Painel de chat continua QML em ambos. Handshake bridge_version=1, heartbeat a cada 2 s, fallback após 6 s sem resposta. Reconectar não duplica mascote, timer ou eventos.

## Janela, interação e posição

Tamanho padrão 160 px lógicos; aceitar 96–256. Frame transparente e sem borda. Região interativa segue hit_region, sem janela transparente que capture tela inteira. Drag exige botão principal pressionado; clique curto abre conversa. Menu: conversar, tarefas, tamanho, ocultar, configurações, sair. Não exigir double-click.

GNOME move ator dentro da workarea, por monitor; salva posição normalizada, ID de monitor e tamanho. Windows usa Qt/Win32 e coordenadas DPI-aware. Backend Qt Wayland genérico usa system move do compositor; não promete recuperar posição absoluta.

Clamp posição quando monitor sumir; restaurar dentro da workarea do monitor principal se não houver correspondência. Não roubar foco ao animar/notificar. Não sobrepor tela de bloqueio, autenticação/UAC nem prometer aparecer acima de fullscreen exclusivo. Hide/minimize mantém tarefa ativa com indicação no launcher/indicador; Sair cancela e encerra conforme lifecycle.

## Layout e tokens

Painel padrão 440×620 unidades lógicas; mínimo 360×420; máximo limitado à área disponível. Histórico virtualizado, entrada multilinha, enviar/cancelar, estado da tarefa e projeto visíveis. Histórico de execuções e logs são painis navegáveis, não janelas que crescem indefinidamente.

Fonte do sistema, corpo 14 px lógico, secundário 12, título 18; respeitar escala do SO. Espaçamento 4/8/12/16/24, raio 12, botão principal altura mínima 36. Cor de acento #D86542; fundo claro #FAF8F4, texto #20262B; fundo escuro #192126, texto #F3EFE7. Validar contraste de cada combinação real; ajustar tons se insuficiente, preservando esses papéis sem aceitar contraste ruim por fidelidade ao hex.

Tema system/light/dark. Qt Quick Controls Fusion com tokens comuns; não criar todos os controles do zero. Texto principal contraste >=4.5:1; foco visível e navegação de teclado integral. Botões só com ícone têm Accessible.name. Plano de permissões não tem botão de aceite preselecionado por Enter ao abrir.

Balão contextual: até 160 caracteres visíveis, sem credenciais, sem perguntas de autorização executável. “Preciso da sua aprovação” abre painel seguro. Aviso simples some após 6 s; aprovação/erro persistem no painel.

## Conversa, revisão e personalidade

Mensagens externas como texto/Markdown restrito: sem HTML executável, imagem remota automática ou links executados ao renderizar. Abrir URL é intenção explícita e validada. Explicar progresso com etapas reais; não inventar porcentagem.

Personalidade inicial: português, curiosa, prática e breve; humor leve sem atrapalhar erro/aprovação. Durante trabalho: uma frase por marco, sem narrar cada comando. Explicação detalhada quando solicitada. Configuração futura altera estilo, nunca política de segurança.

Permissão: resumo, tool/argv completo, cwd, recursos, rede, impacto, expiração e aceitar/negar/cancelar. Diff mostra arquivos, adições/remoções/binários, testes, conflitos e botão aplicar com aprovação vinculada. Verificado, não verificado e teste falhou são estados diferentes.

## Voz futura

Push-to-talk primeiro; mic desligado por padrão e indicador persistente durante captura. Nova captura interrompe playback. TTS pode ser silenciado sem cancelar tarefa. Envelope de amplitude a cada 50 ms aciona speaking; lip sync fonético não é requisito. Não repetir áudio do próprio TTS no STT; pausar ativação por frase durante playback.

## Critérios visuais

Validar GNOME/Wayland e Windows em 100%, 150% e 200% de escala, tema claro/escuro, monitores com DPI diferente, ausência de extensão, bloqueio de sessão e movimento reduzido. Screenshots de evidência usam dados fixture, não desktop pessoal. Medir 100 ciclos abrir/fechar, timers ativos e RSS; metas detalhadas em TESTING.md.

## Fontes

Consultadas em 2026-11-11: [AnimatedSprite](https://doc.qt.io/qt-6.12/qml-qtquick-animatedsprite.html), [GJS extensões](https://gjs.guide/extensions/development/creating.html), [janelas Qt](https://doc.qt.io/QT-6/application-windows.html), [SetWindowPos](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos). Paleta, dimensões e estados são decisões do Quill.


## Revisão autorizada — avanço Linux com Windows pendente

O usuário pediu passar à próxima fase e confirmou a implementação. Q009 depende de Q007 validada, sem esperar Q008. O critério de conclusão desta etapa passa a ser bootstrap/worker no Linux, com teste automático e smoke Wayland; certificação Windows permanece em Q008/Q016/Q035 e não é inferida de testes Linux. Q010–Q015 podem prosseguir pelas dependências locais. Não habilitar execução Codex Windows nem anunciar suporte Windows antes dos gates nativos. O MVP/release multiplataforma mantém as exigências originais.

Instalar PySide6-Essentials 6.12.0 (mesmo namespace PySide6 e módulos QtCore/Gui/Qml/Quick/Controls/Network/DBus) para não puxar WebEngine/PDF sem uso. Addons entram somente quando uma fase precisar. Contratos e desenho Qt permanecem os aprovados. Uma prévia artística por imagegen foi tentada e rejeitada pela ferramenta; não foi produzida nem incorporada. Fixture técnico de Q010 não significa aprovação da arte final.
