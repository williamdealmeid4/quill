import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    objectName: "mainWindow"
    visible: true
    width: 440
    height: 620
    minimumWidth: 360
    minimumHeight: 520
    title: "Quill"
    readonly property bool dark: Qt.styleHints.colorScheme === Qt.ColorScheme.Dark
    readonly property color ink: dark ? "#F3EFE7" : "#202A22"
    readonly property color muted: dark ? "#C1CCBC" : "#53604E"
    color: dark ? "#19221C" : "#FAF8F4"
    palette.windowText: ink
    palette.text: ink
    palette.buttonText: ink
    palette.button: dark ? "#2C392D" : "#E8EDE1"
    palette.highlight: "#49753A"
    onClosing: quillBridge.requestExit()

    AvatarWindow {}

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 12
        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Quill"
                font.pixelSize: 28
                font.weight: Font.DemiBold
                color: window.ink
            }
            Item { Layout.fillWidth: true }
            Button {
                text: quillBridge.avatarVisible ? "Ocultar mascote" : "Mostrar mascote"
                flat: true
                onClicked: quillBridge.avatarVisible ? quillBridge.hideAvatar() : quillBridge.showAvatar()
            }
        }
        Label {
            text: "Seu companheiro de mesa."
            font.pixelSize: 14
            color: window.muted
        }
        Item { Layout.fillHeight: true }
        Avatar {
            objectName: "panelAvatar"
            surfaceId: "panel"
            Layout.fillWidth: true
            Layout.preferredHeight: width * presentation.height / presentation.width
            Layout.maximumHeight: 280
        }
        Item { Layout.fillHeight: true }
        Label {
            objectName: "statusText"
            text: quillBridge.status
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pixelSize: 14
            color: window.ink
        }
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: quillBridge.busy ? "Testando…" : "Testar resposta"
                enabled: !quillBridge.busy
                Layout.fillWidth: true
                implicitHeight: 40
                Accessible.name: "Testar resposta local do Quill"
                onClicked: quillBridge.preview()
                contentItem: Text {
                    text: parent.text
                    color: "#FAF8F4"
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.enabled ? (parent.hovered ? "#2C512A" : "#365F31") : "#66795D"
                    radius: 8
                    border.width: parent.activeFocus ? 2 : 0
                    border.color: window.ink
                }
            }
            Button {
                text: "Interromper"
                visible: quillBridge.busy
                onClicked: quillBridge.cancel()
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "Ver imagem original"
                flat: true
                onClicked: quillBridge.openArtwork()
            }
            Item { Layout.fillWidth: true }
            CheckBox {
                text: "Menos movimento"
                checked: quillBridge.reducedMotion
                onToggled: quillBridge.setReducedMotion(checked)
            }
        }
        Label {
            text: "Arte selecionada por você · Movimento de repouso"
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pixelSize: 12
            color: window.muted
        }
    }
}
