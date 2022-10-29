import QtQuick 2.0
import QtGraphicalEffects 1.0

Rectangle {
    property bool isActivated: true
    property bool modeReverse: false
    property var color_: (modeReverse) ? "white" : "black"
    property var img_:"source/shop_cart.png"
    property var text_:"Tiket Pesawat"
    property var text2_:"Flight Ticket"
    property var text_color: (modeReverse) ? "black" : "white"
    property var mode3d: undefined
    property int size: 350
    property bool rounded: false
    width: size
    height: size
    color: 'transparent'
    radius: (rounded) ? width/2 : 0
    Rectangle{
        id: background_base
        anchors.fill: parent
        color: 'white'
        opacity: 1
        radius: (rounded) ? width/2 : 0
    }
    Image{
        id: button_image
        anchors.topMargin: -100
        anchors.fill: parent
        scale: 0.4
        source: img_
        fillMode: Image.PreserveAspectFit
        visible: modeReverse
    }
    ColorOverlay {
        anchors.fill: button_image
        source: button_image
        scale: 0.4
        color: "black"
    }
    Text{
        id: text_button
        color: 'black'
        text: text_
        font.pixelSize: 27
        anchors.bottomMargin: 50
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
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
        radius: (rounded) ? width/2 : 0
    }

    Text {
        visible: closed_rectangle.visible
        anchors.fill: closed_rectangle
        text: qsTr("CLOSED")
        font.pixelSize: 35
        color: "black"
        font.bold: true
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
    }

}

