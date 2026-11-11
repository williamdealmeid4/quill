import QtQuick
import QtQuick.Controls

Window {
    id: floating
    objectName: "avatarWindow"
    title: "Quill — mascote"
    width: quillBridge.avatarSize
    height: Math.ceil(width * quillBridge.avatar.height / quillBridge.avatar.width)
    color: "transparent"
    flags: Qt.FramelessWindowHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
    visible: quillBridge.avatarVisible
    onWidthChanged: quillBridge.applyAvatarMask(floating, width, height)
    onHeightChanged: quillBridge.applyAvatarMask(floating, width, height)
    Component.onCompleted: quillBridge.applyAvatarMask(floating, width, height)

    Avatar {
        anchors.fill: parent
        surfaceId: "floating"
    }
    TapHandler {
        acceptedButtons: Qt.LeftButton
        onTapped: quillBridge.showPanel()
    }
    TapHandler {
        acceptedButtons: Qt.RightButton
        onTapped: menu.popup()
    }
    DragHandler {
        target: null
        acceptedButtons: Qt.LeftButton
        onActiveChanged: if (active) floating.startSystemMove()
    }
    Menu {
        id: menu
        popupType: Popup.Window
        MenuItem { text: "Abrir painel"; onTriggered: quillBridge.showPanel() }
        MenuItem { text: "Ver imagem original"; onTriggered: quillBridge.openArtwork() }
        Menu {
            title: "Tamanho"
            MenuItem { text: "Pequeno"; onTriggered: quillBridge.setAvatarSize(128) }
            MenuItem { text: "Médio"; onTriggered: quillBridge.setAvatarSize(192) }
            MenuItem { text: "Grande"; onTriggered: quillBridge.setAvatarSize(256) }
        }
        MenuSeparator {}
        MenuItem { text: "Ocultar personagem"; onTriggered: quillBridge.hideAvatar() }
        MenuItem { text: "Sair do Quill"; onTriggered: quillBridge.requestExit() }
    }
}
