import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0

Base{
    id:preload_combo_sakti
    property var textMain: 'Dapatkan Kode Pemesanan Produk dengan langkah-langkah berikut :'
    property var textSlave: 'Cara 1 : Pelanggan mengakses *363*369# untuk memilih paket yang diinginkan.'
    property var textRebel: 'Cara 2 : Scan QR Di Atas dengan smartphone Anda, dan buka tautan link untuk memilih Produk.'
    property var textQuard: 'Jika Telah Mendapatkan Kode Pemesanan, Silakan Tekan Tombol LANJUT.'
    property var imageSource: "source/tsel-combo-sakti-qr-code.png"
    property bool smallerSlaveSize: true
    property int textSize: (globalScreenType == '1') ? 40 : 35
    
    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false
    
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
        anchors.topMargin: (globalScreenType == '1') ? 150 : (smallHeight) ? 30 : 120
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Special Offer : Telkomsel Paket Murah'
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "yellow"

    }

    Column{
        id: column
        width: parent.width
        height: 500
        anchors.verticalCenterOffset: -20
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20
        AnimatedImage  {
            width: 400
            height: 400
            scale: 1
            anchors.horizontalCenter: parent.horizontalCenter
            source: imageSource
            fillMode: Image.PreserveAspectFit
        }
//        Text{
//            text: textMain
//            font.pixelSize: textSize
//            wrapMode: Text.WordWrap
//            horizontalAlignment: Text.AlignHCenter
//            width: parent.width - 180
//            anchors.horizontalCenter: parent.horizontalCenter
//            font.bold: false
//            color: 'white'
//            verticalAlignment: Text.AlignVCenter
//            font.family: "Ubuntu"
//        }
        Text{
            text: textSlave
            horizontalAlignment: Text.AlignLeft
            width: parent.width - 250
            wrapMode: Text.WordWrap
            font.pixelSize: (smallerSlaveSize) ? textSize-5: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }
        Text{
            text: textRebel
            horizontalAlignment: Text.AlignLeft
            width: parent.width - 250
            wrapMode: Text.WordWrap
            font.pixelSize: (smallerSlaveSize) ? textSize-5: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }
        Text{
            text: textQuard
            horizontalAlignment: Text.AlignLeft
            width: parent.width - 250
            wrapMode: Text.WordWrap
            font.pixelSize: (smallerSlaveSize) ? textSize-5: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }

    }

//    Image{
//        width: 210
//        height: 80
//        visible: false
//        anchors.left: parent.left
//        anchors.leftMargin: 565
//        anchors.top: parent.top
//        anchors.topMargin: 280
//        source: "source/emoney_logo.png"
//        fillMode: Image.PreserveAspectFit
//    }

    function open(){
        preload_combo_sakti.visible = true;
        _SLOT.start_play_audio('open_app_scan_qr');
    }

    function close(){
        preload_combo_sakti.visible = false;
    }
}
