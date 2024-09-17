import QtQuick 2.2
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
//import "screen.js" as SCREEN
//import "config.js" as CONF


Rectangle{
    id:popup_confirmation
    width: parseInt(SCREEN_WIDTH)
    height: parseInt(SCREEN_HEIGHT)

//    property var globalScreenType: '2'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    color: 'transparent'
    property var colorMode: "#293846"
    property bool withBackground: true

    property var calledFrom
    property var handleButtonVisibility

    property var escapeFunction: 'closeWindow' //['closeWindow', 'backToMain', 'backToPrevious']
    property var press: "0"
    property var showDuration: ""

    property var channelName: "WHATSAPP"
    property var phoneNumber: "085710157057"

    property string mainTitle: "Konfirmasi"
    property string mainDescription: "Pengembalian Transaksi Melalui " + channelName + " Ke Nomor Tujuan " + phoneNumber + " ?"

    visible: false
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: base_overlay
        visible: false
        anchors.fill: parent
        color: VIEW_CONFIG.background_color
//        color: 'black'
        opacity: 0.6
    }

    Rectangle{
        id: notif_rec
        width: parent.width
        y: 125
        height: parent.height - y
//        color: VIEW_CONFIG.frame_color
        color: colorMode
        anchors.horizontalCenter: parent.horizontalCenter
//        anchors.verticalCenter: parent.verticalCenter

        MainTitle{
            id: main_title
            width: parent.width - 400
            anchors.top: parent.top
            anchors.topMargin: 45
            anchors.horizontalCenter: parent.horizontalCenter
            show_text: mainTitle
            size_: (popup_confirmation.width==1920) ? 40 : 30
            color_: VIEW_CONFIG.text_color
        }

        Text {
            id: main_desc
            width: parent.width - 400
            height: 400
            color: VIEW_CONFIG.text_color
            text: mainDescription
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            font.bold: true
            font.italic: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.family:"Ubuntu"
            font.pixelSize: (popup_confirmation.width==1920) ? 35 : 25
        }

    }

    AnimatedImage  {
        width: 100
        height: 100
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: 'source/blue_gradient_circle_loading.gif'
        fillMode: Image.PreserveAspectFit
        Text{
            id: text_timer_show
            anchors.fill: parent
            text: showDuration
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 25
            color: 'yellow'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
    }

    function open(msg){
        if (msg!=undefined) mainDescription = msg;
        popup_confirmation.visible = true;
    }

    function close(){
        popup_confirmation.visible = false;
    }

}
