import QtQuick 2.0
import QtGraphicalEffects 1.0

Rectangle {
    id: rectangle
    property var sourceImage:"source/qr_dana.png"
    property bool modeReverse: true
    property bool imageMaxMode: false
    property var itemName: 'QRIS Shopeepay'
    property bool isSelected: false

    width: 359
    height: 183
    color: 'transparent'
    visible: true

    Rectangle {
        visible: !isSelected
        anchors.fill: parent
        color: (modeReverse) ? "white" : "black"
        opacity: .2
    }

    Rectangle {
        visible: isSelected
        anchors.fill: parent
        color: "black"
        opacity: .8
    }

    Image{
        id: raw_image
        width: (imageMaxMode) ? 230 : 120
        anchors.topMargin: (imageMaxMode) ? 10 : 15
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: sourceImage
        fillMode: Image.PreserveAspectFit
    }

    ColorOverlay {
        visible: !modeReverse
        anchors.fill: raw_image
        source: raw_image
        scale: raw_image.scale
        color: "#ffffff"
    }

    Text{
        color: "white"
        text: itemName
        style: Text.Sunken
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        font.bold: true
        font.pixelSize: 28
        verticalAlignment: Text.AlignBottom
        horizontalAlignment: Text.AlignHCenter
        font.family: "Ubuntu"
    }

    function set_active(){
        isSelected = true;
    }

    function do_release(){
        isSelected = false;
    }



}

