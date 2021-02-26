import QtQuick 2.0
import QtGraphicalEffects 1.0

Rectangle {
    id: rectangle
    property var sourceImage:"source/ppob_category/pulsa.png"
    property bool modeReverse: true
    property var operatorName: 'Pulsa'
    width: 200
    height: 300
    color: 'transparent'
    visible: true

    Rectangle {
        anchors.fill: parent
        color: (modeReverse) ? "white" : "black"
        opacity: .2
    }

    Image{
        anchors.verticalCenterOffset: -20
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        scale: 1.2
        source: sourceImage
        fillMode: Image.PreserveAspectFit
    }

    Text{
        color: "white"
        text: operatorName
        style: Text.Sunken
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        font.bold: true
        font.pixelSize: 28
        verticalAlignment: Text.AlignBottom
        horizontalAlignment: Text.AlignHCenter
        font.family: "Ubuntu"

    }

}

