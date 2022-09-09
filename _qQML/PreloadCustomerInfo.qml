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
    property int textSize: (globalScreenType == '1') ? 37 : 32
    property int boxSize: 200

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
        show_text: 'Syarat dan Ketentuan'
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"

    }

    Column{
        id: box_cust_info
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 50

        InfographBox{
            id: info1
            _boxSize: boxSize
            _textSize: textSize
            textContent: textMain
            imageSource: "source/whatsapp_icon_tnc.png"
            visible: (VIEW_CONFIG.bill_type !== 'MEI')
        }

        InfographBox{
            id: info2
            _boxSize: boxSize
            _textSize: textSize
            textContent: textSlave
            imageSource: "source/inputcode_icon_tnc.png"
        }

        InfographBox{
            id: info3
            _boxSize: boxSize
            _textSize: textSize
            textContent: textThird
            imageSource: "source/receipt_qr_icon_tnc.png"
        }

    }



    function open(){
        preload_customer_info.visible = true;
        _SLOT.start_play_audio('read_tnc_press_proceed');
    }

    function close(){
        preload_customer_info.visible = false;
    }
}
