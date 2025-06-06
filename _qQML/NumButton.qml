import QtQuick 2.2
import QtQuick.Controls 1.2

Rectangle{
    id: rec
    width:88
    height:88
    radius: 15
    color: "silver"
    property var show_text:""
    Text{
        text:show_text
        color:"black"
        font.family:"Ubuntu"
        font.pixelSize:24
        anchors.centerIn: rec;
        font.bold: true
    }
    MouseArea {
        anchors.fill: rec
        onClicked: {
            full_numpad.strButtonClick(show_text);
        }
        onEntered:{
            rec.color = "gray";
        }
        onExited:{
            rec.color = "silver";
        }
    }
}
