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
    minimumHeight: 420
    title: "Quill"
    color: "#FAF8F4"
    onClosing: quillBridge.requestExit()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: "Quill"
                font.pixelSize: 26
                font.weight: Font.DemiBold
                color: "#20262B"
            }
            Item { Layout.fillWidth: true }
            Label {
                text: "Prévia local"
                font.pixelSize: 12
                color: "#67564D"
            }
        }
        Item { Layout.fillHeight: true }
        Label {
            text: "Um pequeno companheiro.\nUm espaço para criar."
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pixelSize: 26
            font.weight: Font.DemiBold
            color: "#20262B"
        }
        Label {
            objectName: "statusText"
            text: quillBridge.status
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pixelSize: 14
            color: "#67564D"
        }
        Item { Layout.fillHeight: true }
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: quillBridge.busy ? "Testando…" : "Testar resposta"
                enabled: !quillBridge.busy
                Layout.fillWidth: true
                Accessible.name: "Testar resposta local do Quill"
                onClicked: quillBridge.preview()
            }
            Button {
                text: "Interromper"
                visible: quillBridge.busy
                onClicked: quillBridge.cancel()
            }
        }
        Label {
            text: "Nenhum projeto autorizado · Voz desligada"
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pixelSize: 12
            color: "#67564D"
        }
    }
}
