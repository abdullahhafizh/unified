import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
import "screen.js" as SCREEN
import "config.js" as CONF


Base{
    id:cancel_confirmation
    width: parseInt(SCREEN.size.width)
    height: parseInt(SCREEN.size.height)

//    property var globalScreenType: '2'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    color: 'transparent'
    property var colorMode: "#293846"
    property bool withBackground: true

    property var calledFrom
    property var handleButtonVisibility

    property var press: "0"

    property string mainTitle: "Konfirmasi Pembatalan"
    property string mainDescription: "Anda akan Membatalkan Transaksi, Apakah Anda Yakin ?"

    visible: false
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: base_overlay
        visible: false
        anchors.fill: parent
        color: CONF.background_color
//        color: 'black'
        opacity: 0.6
    }

    Rectangle{
        id: notif_rec
        width: parent.width
        y: 125
        height: parent.height - y
//        color: CONF.frame_color
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
            size_: (cancel_confirmation.width==1920) ? 40 : 30
            color_: CONF.text_color
        }

        Text {
            id: main_desc
            width: parent.width - 400
            height: 400
            color: CONF.text_color
            text: mainDescription
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            font.bold: true
            font.italic: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.family:"Ubuntu"
            font.pixelSize: (cancel_confirmation.width==1920) ? 35 : 25
        }

    }

    function open(msg){
        if (msg!=undefined) mainDescription = msg;
        cancel_confirmation.visible = true;
    }

    function close(){
        cancel_confirmation.visible = false;
    }

}
