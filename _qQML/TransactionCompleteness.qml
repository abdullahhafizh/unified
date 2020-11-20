import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0


Base{
    id:transactionCompleteness
//    color: "silver"

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    isBoxNameActive: false
    property var mainTitle: 'Transaksi Sukses'
    property var textFirst: 'Transaksi Kembalian akan dimasukkan ke Whatsapp Voucher.'
    property var textSecond: 'Silakan masukkan nomor Whatsapp Anda untuk transaksi kembalian.'
    property var textThird: 'Anda bisa melakukan transaksi Topup dan Beli Kartu melalui Whatsapp.'
    property var textFourth: 'Silakan Scan QR untuk melihat Voucher pengembalian Anda di Whatsapp.'
    property bool showWhatAppQR: true
    property int textSize: (globalScreenType == '1') ? 40 : 35
    property int boxPadding: 400
    property int imageSize: 300
    property url imageSource: "source/whatsapp_logo.jpeg"

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
        width: 1200
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 150 : 125
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: mainTitle
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"

    }

    AnimatedImage  {
        id: mainImage
        visible: showWhatAppQR
        width: imageSize
        height: imageSize
        anchors.verticalCenterOffset: 275
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        scale: 1
        source: imageSource
        fillMode: Image.PreserveAspectFit
    }

    Text{
        text: "*Pastikan Anda memiliki Aplikasi Scan Barcode"
        visible: showWhatAppQR
        anchors.top: mainImage.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 20
        horizontalAlignment: Text.AlignLeft
        font.bold: false
        color: 'white'
        verticalAlignment: Text.AlignVCenter
        font.family: "Ubuntu"
    }

    Column{
        id: rowDetailText
        spacing: 50
        width: parent.width - boxPadding
        height: parent.height - boxPadding
        anchors.verticalCenterOffset: 75
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        Text{
            id: firstText
            text: " - " + textFirst
            font.pixelSize: 40
            width: parent.width
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignLeft
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }


        Text{
            id: secondText
            text: " - " + textSecond
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: 40
            width: parent.width
            wrapMode: Text.WordWrap
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }

        Text{
            id: thirdText
            visible: textThird.length > 0
            text: " - " + textThird
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: 40
            width: parent.width
            wrapMode: Text.WordWrap
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }

        Text{
            id: fourthText
            visible: textFourth.length > 0
            text: " - " + textFourth
            horizontalAlignment: Text.AlignLeft
            font.pixelSize: 40
            width: parent.width
            wrapMode: Text.WordWrap
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }

    }



    function open(){
        transactionCompleteness.visible = true
    }

    function close(){
        transactionCompleteness.visible = false
    }
}
