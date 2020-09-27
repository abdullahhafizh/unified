import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0


Base{
    id:preload_customer_info
    // color: "silver"

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    isBoxNameActive: false
    property var whatsappNo: ''
    property var textMain: 'Saat Ini Transaksi Gagal/Batal Dapat Diulang Kembali Pada Menu "CEK/LANJUT TRANSAKSI" Dengan Memasukkan Kode Voucher Yang Tertera Pada Struk Anda.'
    property var textSlave: 'Pengembalian Dana Transaksi Lebih Bayar Akan Dikembalikan Melalui WhatsApp Chat ' + whatsappNo
    property bool smallerSlaveSize: true
    property int textSize: (globalScreenType == '1') ? 40 : 35
    property int boxSize: 240

    visible: false
    opacity: visible ? 1.0 : 0.0
    Behavior on opacity {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutQuad  }
    }

//    Rectangle{
//        anchors.fill: parent
//        color: "gray"
//        opacity: 0.5
//    }

    MainTitle{
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 150 : 125
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Pelanggan YTH.'
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"

    }

    AnimatedImage  {
        id: mainImage
        width: boxSize
        height: boxSize
        anchors.horizontalCenterOffset: -500
        anchors.verticalCenterOffset: -150
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: "source/key_in_pincode.png"
        fillMode: Image.PreserveAspectFit
    }

    Text{
        id: mainText
        text: textMain
        anchors.horizontalCenterOffset: 200
        anchors.verticalCenterOffset: -150
        anchors.verticalCenter: parent.verticalCenter
        font.pixelSize: textSize
        width: 900
        height: width/4
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignRight
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: false
        color: 'white'
        verticalAlignment: Text.AlignVCenter
        font.family: "Ubuntu"
    }

    AnimatedImage  {
        id: slaveImage
        width: boxSize
        height: boxSize
        anchors.horizontalCenterOffset: 500
        anchors.verticalCenterOffset: 200
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: "source/whatsapp_logo.jpeg"
        fillMode: Image.PreserveAspectFit
    }

    Text{
        id: slaveText
        text: textSlave
        anchors.horizontalCenterOffset: -200
        anchors.verticalCenterOffset: 200
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.pixelSize: textSize
        width: 900
        height: width/4
        wrapMode: Text.WordWrap
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: false
        color: 'white'
        verticalAlignment: Text.AlignVCenter
        font.family: "Ubuntu"
    }

    function open(){
        preload_customer_info.visible = true
    }

    function close(){
        preload_customer_info.visible = false
    }
}
