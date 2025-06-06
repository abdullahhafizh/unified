import QtQuick 2.2
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "config.js" as CONF


Base{
    id: qr_payment_frame

                //    property var globalScreenType: '1'
                //    height: (globalScreenType=='2') ? 1024 : 1080
                //    width: (globalScreenType=='2') ? 1280 : 1920
    isBoxNameActive: false
    property var modeQR: "linkaja"
    property var textMain: 'Scan QR Berikut Dengan Aplikasi ' + modeQR
    property var textSlave: 'Menunggu Pembayaran...'
    property var imageSource: "source/sand-clock-animated-2.gif"
    property bool successPayment: false
    property bool smallerSlaveSize: true
    property bool withTimer: true
    property int textSize: (globalScreenType == '1') ? 40 : 35
    property int timerDuration: 300
    property int waitAfterSuccess: 10
    property var qr_payment_id
    property int showDuration: timerDuration
    property var closeMode: 'closeWindow' // 'closeWindow', 'backToMain', 'backToPrev'

    property variant qrisProvider: allQRProvider

    property alias qrTimer: show_timer
    property var calledFrom

    visible: false
    opacity: visible ? 1.0 : 0.0
    Behavior on opacity {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutQuad  }
    }

    AnimatedImage  {
        id: qris_logo
        width: 300
        height: 200
        anchors.left: parent.left
        anchors.leftMargin: (smallHeight) ? 100 : 200
        anchors.top: parent.top
        anchors.topMargin: 100
        scale: (smallHeight) ? .7 : 1
        visible: (qrisProvider.indexOf(modeQR))
        source: "source/qr_logo/qris_logo_white.png"
        fillMode: Image.PreserveAspectFit
    }

    AnimatedImage  {
        id: gpn_logo
        width: 300
        height: 200
        anchors.right: parent.right
        anchors.rightMargin: (smallHeight) ? 100 : 200
        anchors.top: parent.top
        anchors.topMargin: 100
        scale: (smallHeight) ? .7 : 1
        visible: (qrisProvider.indexOf(modeQR))
        source: "source/qr_logo/gpn_white_logo.png"
        fillMode: Image.PreserveAspectFit
    }

    Column{
        width: parent.width
        height: 500
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 200 : 150
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: (globalScreenType == '1') ? 30 : 25
        visible: !successPayment
        AnimatedImage  {
            width: 400
            height: 400
            scale: 1
            anchors.horizontalCenter: parent.horizontalCenter
            source: imageSource
            fillMode: Image.PreserveAspectFit
        }
        Text{
            text: textMain
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
            font.pixelSize: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: VIEW_CONFIG.text_color
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
        Text{
            text: textSlave
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
            wrapMode: Text.WordWrap
            font.pixelSize: (smallerSlaveSize) ? textSize-5: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: VIEW_CONFIG.text_color
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }

    }

    Text{
        text: 'Dapat Dibayar Dengan Lebih Dari 50 Channel Bayar QRIS'
        font.pixelSize: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 225
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
        width: parent.width
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: false
        color: VIEW_CONFIG.text_color
        verticalAlignment: Text.AlignVCenter
        font.family:"Ubuntu"
        visible: (VIEW_CONFIG.general_qr=='1' && !successPayment) && !smallHeight
    }

    Row{
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 125
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        spacing: 10
        visible: (VIEW_CONFIG.general_qr=='1' && !successPayment) && !smallHeight
        Image{
            scale: 0.65
            source: "source/ovo_logo.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            scale: 0.9
            source: "source/linkaja_logo.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            scale: 1
            source: "source/gopay_logo.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            scale: 0.9
            source: "source/dana_logo.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            scale: 1
            source: "source/shopeepay_logo.png"
            fillMode: Image.PreserveAspectFit
        }
        // Image{
        //     scale: 0.9
        //     source: "source/jakone_logo.png"
        //     fillMode: Image.PreserveAspectFit
        // }

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
        visible: !successPayment
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

    Column{
        id: rec_payment_success
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: (globalScreenType == '1') ? 30 : 25
        width: parent.width - 100
        visible: successPayment

        Text{
            text: 'Pembayaran QRIS sedang diproses'
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
            font.pixelSize: textSize
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
        Text{
            text: 'Untuk transaksi topup, Pastikan Kartu Anda tetap berada di reader.'
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
            font.pixelSize: textSize
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
    }


    Timer {
        id: show_timer
        interval: 1000
        repeat: true
        running: parent.visible && withTimer
        onTriggered: {
            // console.log('[QR-PAYMENT]', showDuration);
            showDuration -= 1;
            if (showDuration < 30) textSlave = 'Waktu Pembayaran Anda Akan Habis Dalam...';
            if (showDuration <= 7) {
//                if (showDuration == 7) cancel('TIMER_TIMEOUT');
                imageSource = 'source/smiley_down.png';
                textSlave = 'Waktu Pembayaran Anda Telah Habis';
            }
            if (showDuration <= 3) text_timer_show.text = '0';
            if (showDuration==0) {
                show_timer.stop();
                switch(closeMode){
                case 'backToMain':
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                    break;
                case 'backToPrev': case 'backToPrevious':
                    my_layer.pop();
                    break;
                default: close();
                    break;
                }
            }
        }
    }


    function cancel(event){
        _SLOT.start_cancel_qr_global('['+event+'] '+details.shop_type+details.epoch.toString());
        successPayment = false;
    }

    function open(msg, trx_id){
        if (msg!=undefined) textMain = msg;
        if (trx_id!=undefined) qr_payment_id = trx_id;
        qr_payment_frame.visible = true;
        successPayment = false;
        showDuration = timerDuration;
        show_timer.start();
    }

    function close(){
        if (calledFrom!=undefined) {
            if (!successPayment){
                switch(calledFrom){
                case 'general_payment_process':
                    general_payment_process.framingSignal('CALLBACK_ACTION|PRINT_QR_TIMEOUT_RECEIPT')
                    break;
                case 'retry_payment_process':
                    retry_payment_process.framingSignal('CALLBACK_ACTION|PRINT_QR_TIMEOUT_RECEIPT')
                    break;
                }
            }
        }
        qr_payment_frame.visible = false;
        successPayment = false;
        show_timer.stop();
    }

    function hide(){
        qr_payment_frame.visible = false;
        successPayment = false;
        show_timer.stop();
    }

    function success(waitTime){
        closeMode = 'backToMain' // 'closeWindow', 'backToMain', 'backToPrev'
        if (waitTime==undefined) waitTime = waitAfterSuccess;
        successPayment = true;
        delay(waitTime*1000, function(){
            hide();
        });
    }

    Timer {
        id: timer_delay
    }

    function delay(duration, callback) {
        timer_delay.interval = duration;
        timer_delay.repeat = false;
        timer_delay.triggered.connect(callback);
        timer_delay.start();
    }
}
