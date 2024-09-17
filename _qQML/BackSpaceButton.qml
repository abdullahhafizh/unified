import QtQuick 2.5
import QtQuick.Controls 1.5

Rectangle{
    id: rec
    width:75
    height:62
    color:"orange"
    radius: 10
    property var chars: "Back"
//    Text{
//        text: chars
//        color:"white"
//        font.family:"Ubuntu"
//        font.pixelSize:30
//        anchors.centerIn: rec;
//        font.bold: true
//    }
    Image{
        scale: 0.7
        source: "source/back_space.png";
        anchors.fill: rec;
        fillMode: Image.PreserveAspectFit;
    }
    MouseArea {
        anchors.fill: parent
        onClicked: {
            full_keyboard.funcButtonClicked(chars);
        }
        onEntered: {
            rec.color = "gray";
        }
        onExited: {
            rec.color = "orange";
        }
    }
}
