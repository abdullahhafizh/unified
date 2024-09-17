import QtQuick 2.2
import QtQuick.Controls 1.2

Rectangle{
    width:86
    height:80
    color:"#3b8f23"
    radius: 10
//    radius: 25
    property var chars: "OK"
    property bool mouseEnable: true
    property var textColor: 'black'

    Text{
        id: text_button
        text: chars
        font.bold: true
        font.family:"Ubuntu"
        font.pixelSize:30
        anchors.centerIn: parent
        color: textColor
    }

    MouseArea {
        visible: mouseEnable
        anchors.fill: parent
        onClicked: {
            full_keyboard.funcButtonClicked(chars)
        }
        onEntered: {
            parent.color = "black"
        }
        onExited: {
            parent.color = "#3b8f23"
        }
    }
}

//recommit to fix anomaly
