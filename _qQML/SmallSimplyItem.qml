import QtQuick 2.0
import QtGraphicalEffects 1.0

Rectangle {
    id: rectangle
    property var sourceImage:"source/qr_logo/linkaja_white_logo.png"
    property bool modeReverse: true
    property bool imageMaxMode: false
    property var itemName: 'QRIS Payment'
    property bool isSelected: false
    property bool isActivated: true
    property var aliasName: ''

    width: 359
    height: 183
    color: 'transparent'
    visible: true

    Rectangle {
        // visible: !isSelected
        visible: false
        anchors.fill: parent
        color: (modeReverse) ? "white" : "black"
        opacity: .2
    }

    Rectangle {
//        visible: isSelected
        anchors.fill: parent
        color: "white"
        opacity: 1
    }

    Image{
        id: raw_image
        width: (imageMaxMode) ? 200 : 120
        anchors.topMargin: (imageMaxMode) ? 25 : 10
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: sourceImage
        fillMode: Image.PreserveAspectFit
    }

    ColorOverlay {
//        visible: modeReverse
        anchors.fill: raw_image
        source: raw_image
        scale: raw_image.scale
        color: "black"
    }

    Text{
        color: "black"
        text: itemName
        style: Text.Sunken
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        font.bold: true
        font.pixelSize: 25
        verticalAlignment: Text.AlignBottom
        horizontalAlignment: Text.AlignHCenter
        font.family: "Ubuntu"
    }

    Rectangle {
        id: closed_rectangle
        height: 50
        width: parent.width
        visible: !isActivated
        color: "white"
        anchors.verticalCenterOffset: 25
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        opacity: .8
    }

    Text {
        visible: closed_rectangle.visible
        anchors.fill: closed_rectangle
        text: qsTr("")
        font.pixelSize: 35
        color: "black"
        font.bold: true
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

    function set_active(){
        isSelected = true;
    }

    function do_release(){
        isSelected = false;
    }



}

