import QtQuick 2.0
import QtGraphicalEffects 1.0

Rectangle {
    property bool isActivated: true
    property bool modeReverse: false
    property var color_: (modeReverse) ? "white" : "black"
    property var img_:"source/phone_qr.png"
    property var text_:"Tiket Pesawat"
    property var text2_:"Flight Ticket"
    property var text_color: (modeReverse) ? "black" : "white"
    property var mode3d: undefined
    property int size: 350
    width: size
    height: size
    color: 'transparent'
    Rectangle{
        id: background_base
        anchors.fill: parent
        color: 'white'
        opacity: .3
        visible: (mode3d==undefined)
    }
    Image{
        id: base_3d_button
        anchors.fill: parent
        source: "source/3d_button/__"+mode3d+".png"
        fillMode: Image.PreserveAspectFit
        visible: !background_base.visible
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
        visible: !modeReverse
        anchors.fill: button_image
        source: button_image
        scale: 0.4
        color: "#ffffff"
    }
    Text{
        id: text_button
        color: 'white'
//        text: text_.toUpperCase()
        text: text_
        font.pixelSize: 30
        anchors.bottomMargin: 30
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

