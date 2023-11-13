import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0

import "base_function.js" as FUNC
//import "config.js" as CONF


Base{
    id:ereceipt_view

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    property var press: '0'
    property int timer_value: (VIEW_CONFIG.success_page_timer)
    property var whatsappNo: 'tersebut'
    property var textMain: 'Scan QR diatas dengan Aplikasi Whatsapp untuk mendapatkan e-receipt'
    property var textSlave: 'Pada IOS, Tekan Tombol Icon CAMERA di Tengah Bawah'
    property var textSuggestion1: 'Kami menyarankan Anda untuk menggunakan e-receipt'
    property var textSuggestion2: 'demi menjaga kelestarian alam dengan tidak menggunakan kertas'
    property var imageSource: "source/sand-clock-animated-2.gif"
    property var details
    property int textSize: (globalScreenType == '1') ? 35 : 33
    property var showDuration: ''
    property var trxNotes: ''
    property bool retryMode: false
    property bool manualButtonVisible: false
    property int showManualPrintButton: 5
    property int delayExecution: 3000

    property int receivedPayment: 0
    property var totalPrice: 0

    imgPanel: 'source/cek_saldo.png'
    textPanel: 'Cek Saldo Kartu Prabayar'

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            popup_loading.open('Mempersiapkan Struk Transaksi Anda...');
            abc.counter = timer_value;
            my_timer.start();
//            if (VIEW_CONFIG.delay_manual_print != undefined){
//                showManualPrintButton = parseInt(VIEW_CONFIG.delay_manual_print);
//                console.log('Delay Manual Print', showManualPrintButton);
//            }
            define_trx_notes();
            if (VIEW_CONFIG.theme_name.toLowerCase() == 'bca' || VIEW_CONFIG.printer_type.toLowerCase() == 'default' ){
                print_result('SALEPRINT|ERECEIPT_ERROR');
            } else {
                _SLOT.start_direct_sale_print_ereceipt(JSON.stringify(details));
            }
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop();
        }
    }

    Component.onCompleted:{
        base.result_sale_print.connect(print_result);

    }

    Component.onDestruction:{
        base.result_sale_print.disconnect(print_result);
    }

    Rectangle{
        id: rec_timer
        width:10
        height:10
        y:10
        color:"transparent"
        QtObject{
            id:abc
            property int counter
            Component.onCompleted:{
                abc.counter = timer_value;
            }
        }

        Timer{
            id:my_timer
            interval:1000
            repeat:true
            running:true
            triggeredOnStart:true
            onTriggered:{
                abc.counter -= 1;
                showDuration = abc.counter.toString();
                if (abc.counter < 0) showDuration = '0';
                if(abc.counter == (timer_value-showManualPrintButton)){
                    console.log('Show Manual Print Button', abc.counter);
                    manualButtonVisible = true;
                }
                if(abc.counter < 0){
                    // Check Exceed Payment, If Found Keep Print The TRX Receipt
                    var exceed = validate_cash_refundable();
                    if (exceed !== false && parseInt(exceed) > 0) _SLOT.start_direct_sale_print_global(JSON.stringify(details));
                    my_timer.stop();
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }
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

    function define_trx_notes(){
        switch(details.shop_type){
        case 'topup':
            trxNotes = 'Saldo Anda Rp. '+FUNC.insert_dot(details.final_balance.toString());
            break;
        case 'shop': case 'ppob':
            trxNotes = details.provider;
            break;
//        case 'ppob':
//            trxNotes = 'Pastikan Anda mendapatkan konfirmasi dari layanan pembayaran/pembelian Anda.';
//            break;
        }
    }

    function validate_cash_refundable(){
        var result = false;
        if (details.payment == 'cash' && receivedPayment > totalPrice){
            result = parseInt(receivedPayment - totalPrice);
        }
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('validate_cash_refundable', now, result);
        return result;
    }

    function ereceipt_show(data){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('ereceipt_show', now, JSON.stringify(data));
        var whatsappNo = VIEW_CONFIG.whatsapp_no;
        whatsappNo = '62' + whatsappNo.substring(1);
//            imageSource = 'http://mac.local:5050/whatsapp-ereceipt/'+whatsappNo+'/'+data.trxid;
        imageSource = 'http://apiv2.mdd.co.id:10107/whatsapp-ereceipt/'+whatsappNo+'/'+data.trxid;
        if (VIEW_CONFIG.host_qr_generator !== '---') imageSource = VIEW_CONFIG.host_qr_generator + '/whatsapp-ereceipt/'+whatsappNo+'/'+data.trxid;
        imageQr.source = imageSource;
        console.log('ereceipt_qr', imageSource);
        popup_loading.close();
        _SLOT.start_play_audio('scan_qr_ereceipt');
    }

    function print_result(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('print_result', now, p);
        var result = p.split('|')[1];
        popup_loading.close();
        if (result == 'ERECEIPT_DONE'){
            var info = p.split('|')[2];
            var data = JSON.parse(info);
            delay(delayExecution, function(){
                ereceipt_show(data);
            });
            return;
        }
        if (result == 'ERECEIPT_ERROR'){
            textMain = '';
            textSlave = '';
            imageSource = 'source/smiley_down.png';
            false_notif('closeWindow|3', 'Mohon Maaf, Terjadi Kesalahan Dalam Menampilkan QR eReceipt');
            console.log('print_result_force_manual');
            _SLOT.start_direct_sale_print_global(JSON.stringify(details));
            var title = 'Transaksi Berhasil';
            if (retryMode) title = 'Pengulangan ' + title;
            var msg = '';
            if (details.shop_type == 'topup'){
                msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Anda Dari Reader';
            }
            if (details.shop_type == 'shop'){
                msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Baru Anda';
                _SLOT.start_play_audio('please_take_new_card_with_receipt');
            }
            switch_frame('source/take_receipt.png', title, msg, 'backToMain|'+VIEW_CONFIG.success_page_timer.toString(), true );
            return;
        }
        if (result == 'DONE') return;
    }


    //==============================================================
    //PUT MAIN COMPONENT HERE


    AnimatedImage  {
        id: image_success
        width: 160
        height: 160
        anchors.top: parent.top
        anchors.topMargin: 150
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: 'source/success.png'
        fillMode: Image.PreserveAspectFit
    }

    MainTitle{
        y: 150
        width: 1198
        height: 100
        anchors.top: parent.top
        anchors.topMargin: 350
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Transaksi Anda telah selesai. Silahkan ambil kartu Anda\n'+ trxNotes
        size_: 40
        color_: "white"
    }


    Column{
        id: column
        y: 250
        width: parent.width
        height: 500
        anchors.verticalCenterOffset: 200
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 15
        AnimatedImage  {
            id: imageQr
            width: 180
            height: 180
            scale: 1
            anchors.horizontalCenter: parent.horizontalCenter
            source: imageSource
            fillMode: Image.PreserveAspectFit
        }
//        AnimatedImage  {
//            id: instructionQr
//            width: 800
//            height: 450
//            scale: 1
//            visible: false
//            anchors.horizontalCenter: parent.horizontalCenter
//            source: 'source/scan_qr_receipt_instruction.jpg'
//            fillMode: Image.PreserveAspectFit
//        }
        Text{
            text: textSuggestion1 + '\n' + textSuggestion2
            font.pixelSize: textSize
            horizontalAlignment: Text.AlignHCenter
            width: parent.width - 250
            wrapMode: Text.WordWrap
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }
        Text{
            text: textMain
            font.pixelSize: textSize
            horizontalAlignment: Text.AlignHCenter
            width: parent.width - 250
            wrapMode: Text.WordWrap
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }
        Text{
            text: textSlave
            visible: false
            horizontalAlignment: Text.AlignLeft
            width: parent.width - 250
            wrapMode: Text.WordWrap
            font.pixelSize: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family: "Ubuntu"
        }

    }

    CircleButton{
        id: manual_button
        anchors.left: parent.left
        anchors.leftMargin: 50
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50
        button_text: 'PRINT'
        modeReverse: true
        forceColorButton: 'orange'
        scale: 0.75
        MouseArea{
            anchors.fill: parent
            onClicked: {
                parent.visible = false;
                enabled = false;
                var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                if (press != '0') return;
                press = '1';
                _SLOT.user_action_log('Press "CETAK STRUK" in e-Receipt Activity');
                _SLOT.start_direct_sale_print_global(JSON.stringify(details));
                var title = 'Terima Kasih';
                var msg = '';
                if (details.shop_type == 'topup'){
                    msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Anda Dari Reader';
                }
                if (details.shop_type == 'shop'){
                    msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Baru Anda';
                    _SLOT.start_play_audio('please_take_new_card_with_receipt');
                }
                switch_frame('source/take_receipt.png', title, msg, 'backToMain|3', true );
            }
        }
    }

    CircleButton{
        id: ok_button
        button_text: 'SELESAI\n( ' + showDuration + ' )'
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 75
        anchors.horizontalCenter: parent.horizontalCenter
        modeReverse: true
        blinkingMode: true
        baseSize: 150
        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press != '0') return;
                press = '1';
                _SLOT.user_action_log('Press "OK" in e-Receipt Activity');
                var title = 'Terima Kasih';
                var msg = 'Silakan Cek eReceipt Anda di Whatsapp';
                if (details.shop_type == 'topup'){
                    msg = 'Silakan Cek eReceipt Anda di Whatsapp Dan Ambil Kartu Prepaid Anda Dari Reader';
                }
                if (details.shop_type == 'shop'){
                    msg = 'Silakan Cek eReceipt Anda di Whatsapp Dan Ambil Kartu Prepaid Baru Anda';
                    _SLOT.start_play_audio('please_take_new_card_with_receipt');
                }
                // Check Exceed Payment, If Found Keep Print The TRX Receipt
                var exceed = validate_cash_refundable();
                if (exceed !== false && parseInt(exceed) > 0) _SLOT.start_direct_sale_print_global(JSON.stringify(details));
                switch_frame('source/take_receipt.png', title, msg, 'backToMain|3', true );
            }
        }
    }


    function false_notif(closeMode, textSlave){
        if (closeMode==undefined) closeMode = 'backToMain';
        if (textSlave==undefined) textSlave = '';
        press = '0';
        switch_frame('source/smiley_down.png', 'Maaf Gagal Mendapatkan QR eReceipt', textSlave, closeMode, false )
        return;
    }

    function switch_frame(imageSource, textMain, textSlave, closeMode, smallerText){
        press = '0';
        global_frame.modeAction = "";
        global_frame.closeMode = closeMode;
        global_frame.timerDuration = 5;
        if (closeMode.indexOf('|') > -1){
            var selectedCloseMode = closeMode.split('|')[0];
            var frame_timer = closeMode.split('|')[1];
            global_frame.timerDuration = parseInt(frame_timer);
            global_frame.closeMode = selectedCloseMode;
        }
//        if (closeMode == 'closeWindow|30'){
//            global_frame.closeMode = 'closeWindow';
//            global_frame.timerDuration = 30;
//        }
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.withTimer = true;
        global_frame.open();
    }



    //==============================================================

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }

}
