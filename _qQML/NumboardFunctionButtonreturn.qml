import QtQuick 2.2
import QtQuick.Controls 1.2

Rectangle{
    width:88
    height:88
    color:"#ffc125"
    radius: 22
    property var slot_text:""

    Text{
        text:slot_text
        color:"#ffffff"
        font.family:"Ubuntu"
        font.pixelSize:20
        anchors.centerIn: parent;
        font.bold: true

    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            full_numpad.funcButtonClicked(slot_text)
        }
    }

}
