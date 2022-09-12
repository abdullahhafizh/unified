import QtQuick 2.0
import QtGraphicalEffects 1.0

Rectangle {
    id: rectangle
    property var sourceImage
    property var itemName: 'AVAILABLE'

    width: 200
    height: 160
    color: 'transparent'
    visible: true

    Image{
        id: raw_image
        width: parent.width
        height: parent.height - 25
        anchors.top: parent.top
        anchors.topMargin: 0
        source: sourceImage
        scale: 1
        fillMode: Image.PreserveAspectFit
        opacity: (itemName=='AVAILABLE') ? 1 : 0.5
    }


    Text{
        color: "white"
        text: (itemName=='AVAILABLE') ? 'AKTIF' : 'TIDAK AKTIF'
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        style: Text.Sunken
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: true
        font.pixelSize: 22
        verticalAlignment: Text.AlignBottom
        horizontalAlignment: Text.AlignHCenter
        font.family: "Ubuntu"
    }


}

