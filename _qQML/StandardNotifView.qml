import QtQuick 2.2
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN

Rectangle{
    id:notification_standard
    visible: false
    property var show_img: "source/promo_black.png"
    property var show_text: qsTr("Congratulation")
    property var show_detail: qsTr("Your Order is Successfully processed")
    property bool withBackground: true
    property bool buttonEnabled: true
    property bool modeReverse: true
    property alias _button_text: close_button.button_text
    color: 'transparent'
    width: parseInt(SCREEN_WIDTH)
    height: parseInt(SCREEN_HEIGHT)
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: base_overlay
        visible: withBackground
        anchors.fill: parent
        color: "black"
        opacity: 0.6
    }

    Rectangle{
        id: notif_rec
        width: 1200
        height: 600
        color: (modeReverse) ? "white" : "black"
        opacity: .8
        radius: 25
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        Image  {
            id: image
            x: 20
            y: 20
            width: 100
            height: 100
            anchors.left: parent.left
            anchors.leftMargin: 10
            anchors.top: parent.top
            anchors.topMargin: 10
            scale: 0.8
            source: show_img
            fillMode: Image.PreserveAspectFit
            visible: (modeReverse) ? true : false
        }
        ColorOverlay {
            visible: !image.visible
            anchors.fill: image
            source: image
            scale: 0.8
            color: "#ffffff"
        }

    }

    Text {
        id: main_text
        color: (modeReverse) ? "black" : "white"
        text: show_text
        font.bold: true
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        anchors.top: notif_rec.top
        anchors.topMargin: 30
        anchors.horizontalCenterOffset: 5
        font.family:"Ubuntu"
        anchors.horizontalCenter: notif_rec.horizontalCenter
        font.pixelSize: 30
    }
    Text {
        id: detail_text
        x: 0
        y: 0
        width: 900
        height: 350
        color: (modeReverse) ? "black" : "white"
        text: show_detail
//        font.weight: Font.Medium
        anchors.verticalCenterOffset: -30
        anchors.verticalCenter: parent.verticalCenter
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.bold: true
        font.family:"Ubuntu"
        anchors.horizontalCenter: notif_rec.horizontalCenter
        font.pixelSize: 30
    }

    NextButton{
        id: close_button
        button_text: 'lanjut'
        visible: buttonEnabled
        anchors.verticalCenterOffset: 200
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: notif_rec.horizontalCenter
        MouseArea{
            anchors.fill: parent
            onClicked: close();
        }

    }

    function open(){
        notification_standard.visible = true
    }

    function close(){
        notification_standard.visible = false
    }
}
