import QtQuick
import QtQuick.Window

Window {
    id: root
    visible: true
    color: "#10151f"
    title: "ThorDS Touch Calibration"

    property real touchX: width / 2
    property real touchY: height / 2
    property bool touched: false

    Text {
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 32
        color: "white"
        font.pixelSize: 36
        text: root.touched
              ? "Reported touch: " + Math.round(root.touchX) + ", " + Math.round(root.touchY)
              : "Tap the corners and centre"
    }

    Rectangle {
        visible: root.touched
        x: root.touchX - width / 2
        y: root.touchY - height / 2
        width: 72
        height: 72
        radius: 36
        color: "#ef3340"
        border.color: "white"
        border.width: 5
    }

    Repeater {
        model: [[40, 40], [root.width - 40, 40], [40, root.height - 40],
                [root.width - 40, root.height - 40], [root.width / 2, root.height / 2]]
        delegate: Rectangle {
            x: modelData[0] - 12
            y: modelData[1] - 12
            width: 24
            height: 24
            radius: 12
            color: "white"
        }
    }

    MouseArea {
        anchors.fill: parent
        onPressed: mouse => {
            root.touchX = mouse.x
            root.touchY = mouse.y
            root.touched = true
        }
        onPositionChanged: mouse => {
            root.touchX = mouse.x
            root.touchY = mouse.y
        }
    }
}
