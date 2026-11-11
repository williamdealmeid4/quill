import QtQuick

Item {
    id: avatar
    required property string surfaceId
    property var presentation: quillBridge.avatar
    readonly property bool renderActive: visible && Window.window !== null && Window.window.visible
    readonly property bool animationRunning: breathing.running
    property int frameIndex: 0
    readonly property var frame: presentation.frames[frameIndex % presentation.frames.length]
    readonly property real factor: width / presentation.width
    implicitWidth: 256
    implicitHeight: implicitWidth * presentation.height / presentation.width
    onRenderActiveChanged: quillBridge.setSurfaceActive(surfaceId, renderActive)
    Component.onCompleted: quillBridge.setSurfaceActive(surfaceId, renderActive)
    onPresentationChanged: frameIndex = 0

    Item {
        id: art
        anchors.fill: parent
        clip: true
        transformOrigin: Item.Bottom
        Image {
            objectName: "avatarImage"
            source: avatar.presentation.source
            x: -avatar.frame.x * avatar.factor
            y: -avatar.frame.y * avatar.factor
            width: avatar.presentation.atlasWidth * avatar.factor
            height: avatar.presentation.atlasHeight * avatar.factor
            smooth: false
            mipmap: false
            cache: true
            asynchronous: true
        }
    }
    SequentialAnimation {
        id: breathing
        running: avatar.renderActive && !avatar.presentation.reducedMotion
        loops: Animation.Infinite
        onRunningChanged: if (!running) art.scale = 1
        NumberAnimation {
            target: art
            property: "scale"
            from: 1
            to: 1.012
            duration: avatar.presentation.state === "working" ? 850 : 1600
            easing.type: Easing.InOutSine
        }
        NumberAnimation {
            target: art
            property: "scale"
            from: 1.012
            to: 1
            duration: avatar.presentation.state === "working" ? 850 : 1600
            easing.type: Easing.InOutSine
        }
    }
    Timer {
        interval: 1000 / avatar.presentation.fps
        running: avatar.renderActive && !avatar.presentation.reducedMotion
                 && avatar.presentation.frames.length > 1
        repeat: true
        onTriggered: avatar.frameIndex = (avatar.frameIndex + 1) % avatar.presentation.frames.length
    }
}
