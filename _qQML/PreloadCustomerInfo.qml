import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0


Base{
    id:preload_customer_info
//    color: "silver"

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    isBoxNameActive: false
    property var whatsappNo: ''
    property var textMain: 'Mesin ini tidak dapat mengembalikan uang, Proses pengembalian uang akan dilakukan melalui Whatsapp Voucher.'
    property var textSlave: 'Anda dapat melakukan transaksi ulang untuk transaksi yang gagal/batal setelah uang masuk ke dalam Bill Acceptor dengan memasukkan kode ulang.'
    property var textThird: 'Mesin ini akan menggunakan bukti elektronik via WhatsApps dan tidak mengeluarkan Struk Pembelian/Transaksi.'
    property bool smallerSlaveSize: true
    property int textSize: 25
    property int boxSize: 200

    visible: true
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
        anchors.horizontalCenterOffset: 0
        anchors.topMargin: 120
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Syarat dan Ketentuan'
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"

    }

    AnimatedImage  {
        id: mainImage
        width: 150
        height: 150
        anchors.horizontalCenterOffset: -500
        anchors.verticalCenterOffset: -133
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: "source/whatsapp_icon_tnc.png"
        fillMode: Image.PreserveAspectFit
    }

    Text{
        id: mainText
        text: textMain
        anchors.horizontalCenterOffset: 160
        anchors.verticalCenterOffset: -133
        anchors.verticalCenter: parent.verticalCenter
        font.pixelSize: textSize
        width: 1000
        height: 100
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignLeft
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: false
        color: 'white'
        verticalAlignment: Text.AlignVCenter
        font.family: "Ubuntu"
    }

    AnimatedImage  {
        id: slaveImage
        width: 150
        height: 150
        anchors.horizontalCenterOffset: -500
        anchors.verticalCenterOffset: 38
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: "source/inputcode_icon_tnc.png"
        fillMode: Image.PreserveAspectFit
    }

    Text{
        id: slaveText
        text: textSlave
        anchors.horizontalCenterOffset: 160
        anchors.verticalCenterOffset: 38
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.pixelSize: textSize
        width: 1000
        height: 100
        wrapMode: Text.WordWrap
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: false
        color: 'white'
        verticalAlignment: Text.AlignVCenter
        font.family: "Ubuntu"
    }

    AnimatedImage  {
        id: thirdImage
        width: 150
        height: 150
        anchors.horizontalCenterOffset: -500
        anchors.verticalCenterOffset: 212
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: "source/receipt_qr_icon_tnc.png"
        fillMode: Image.PreserveAspectFit
    }

    Text{
        id: thirdText
        text: textThird
        anchors.horizontalCenterOffset: 160
        anchors.verticalCenterOffset: 212
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.pixelSize: textSize
        width: 1000
        height: 100
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

/*##^##
Designer {
    D{i:0;formeditorZoom:0.66}
}
##^##*/
