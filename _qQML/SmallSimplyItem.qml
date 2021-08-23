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

    width: 300
    height: 170
    color: 'transparent'
    visible: true

    Rectangle {
        visible: !isSelected
        anchors.fill: parent
        color: (modeReverse) ? "white" : "black"
        opacity: .2
    }

    Rectangle {
        width: 325
        height: 183
        visible: isSelected
        anchors.fill: parent
        color: "black"
        opacity: .8
    }

    Image{
        id: raw_image
        width: 100
        height: 70
        anchors.topMargin: (imageMaxMode) ? 25 : 10
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: sourceImage
        fillMode: Image.PreserveAspectFit
    }

    ColorOverlay {
        width: 100
        height: 70
        visible: modeReverse
        anchors.fill: raw_image
        source: raw_image
        anchors.rightMargin: 0
        anchors.bottomMargin: 0
        scale: raw_image.scale
        color: "#ffffff"
    }

    Text{
        y: 132
        color: "white"
        text: itemName
        style: Text.Sunken
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        font.bold: true
        font.pixelSize: 20
        verticalAlignment: Text.AlignBottom
        anchors.horizontalCenterOffset: 0
        horizontalAlignment: Text.AlignHCenter
        font.family: "Ubuntu"
    }

    Rectangle {
        id: closed_rectangle
        height: 30
        width: parent.width
        visible: !isActivated
        color: "white"
        anchors.verticalCenterOffset: 21
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenterOffset: 0
        opacity: .8
    }

    Text {
        visible: closed_rectangle.visible
        anchors.fill: closed_rectangle
        text: qsTr("CLOSED")
        font.pixelSize: 20
        color: "black"
        font.bold: true
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0
        anchors.bottomMargin: 0
        horizontalAlignment: Text.AlignHCenter
    }

    function set_active(){
        isSelected = true;
    }

    function do_release(){
        isSelected = false;
    }



}


/*##^##
Designer {
    D{i:0;formeditorZoom:0.75}
}
##^##*/
