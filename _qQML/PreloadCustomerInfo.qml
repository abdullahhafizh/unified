import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0


Base{
    id:preload_customer_info
//    color: "silver"

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    property var whatsappNo: ''
    property var textMain: 'Selain Transaksi Topup, Mesin ini tidak mengembalikan uang. Proses pengembalian uang akan dilakukan melalui Whatsapp Voucher.'
    property var textSlave: 'Anda dapat melakukan transaksi ulang untuk transaksi yang gagal/batal setelah uang masuk ke dalam Bill Acceptor dengan memasukkan kode ulang.'
    property var textThird: 'Mesin ini akan menggunakan bukti elektronik via WhatsApps dan tidak mengeluarkan Struk Pembelian/Transaksi.'
    property bool smallerSlaveSize: true
    property int textSize: (globalScreenType == '1') ? 37 : 32
    property int boxSize: (globalScreenType == '1') ? 200 : 160

    property int showDuration: 3
    property bool autoDismiss: true
    property var selectedMenu: ''

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
            _width: globalWidth
            _boxSize: boxSize
            _textSize: textSize
            textContent: textMain
            imageSource: "source/whatsapp_icon_tnc.png"
        }

        InfographBox{
            id: info2
            _width: globalWidth
            _boxSize: boxSize
            _textSize: textSize
            textContent: textSlave
            imageSource: "source/inputcode_icon_tnc.png"
        }

        InfographBox{
            id: info3
            _width: globalWidth
            _boxSize: boxSize
            _textSize: textSize
            textContent: textThird
            imageSource: "source/receipt_qr_icon_tnc.png"
        }

    }

    Timer {
        id: show_timer
        interval: 1000
        repeat: true
        running: parent.visible && autoDismiss
        onTriggered: {
            showDuration -= 1;
            if (showDuration==0) {
                show_timer.stop();
                switch(selectedMenu){
                case 'CHECK_BALANCE':
                    my_layer.push(check_balance);
                    break;
                case 'TOPUP_PREPAID':
                    my_layer.push(topup_prepaid_denom, {shopType: 'topup'});
                    break;
                case 'SHOP_PREPAID':
                    my_layer.push(general_shop_card, {productData: productData, shop_type: 'shop', productCount: productCountAll});
                    break;
                case 'SHOP_PPOB':
                    popup_loading.open();
                    _SLOT.start_get_ppob_product();
                    break;
                }
            }
        }
    }

    AnimatedImage  {
        width: 100
        height: 100
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
        scale: 1
        anchors.horizontalCenter: parent.horizontalCenter
        source: 'source/blue_gradient_circle_loading.gif'
        fillMode: Image.PreserveAspectFit
        visible: autoDismiss
        Text{
            id: text_timer_show
            anchors.fill: parent
            text: showDuration
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 20
            color: 'yellow'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
    }

    function delay(duration, callback) {
        timer_delay.interval = duration;
        timer_delay.repeat = false;
        timer_delay.triggered.connect(callback);
        timer_delay.start();
    }



    function open(menu, timer){
        selectedMenu = menu;
        if (timer !== undefined && parseInt(timer) > 0){
            autoDismiss = true;
            showDuration = parseInt(timer);
            show_timer.start();
        }
        preload_customer_info.visible = true;
        _SLOT.start_play_audio('read_tnc_press_proceed');
    }

    function close(){
        preload_customer_info.visible = false;
        show_timer.stop();
    }
}
