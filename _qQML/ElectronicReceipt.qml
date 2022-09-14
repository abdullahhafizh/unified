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
    property var textMain: 'Scan QR Diatas untuk mendapatkan resi Whatsapp'
    property var textSlave: 'Pada IOS, Tekan Tombol Icon CAMERA di Tengah Bawah'
    property var textRebel: ''
    property var textQuard: ''
    property var imageSource: "source/sand-clock-animated-2.gif"
    property var details
    property int textSize: (globalScreenType == '1') ? 38 : 33
    property var showDuration: ''
    property var trxNotes: ''
    property bool retryMode: false
    property bool manualButtonVisible: false
    property int showManualPrintButton: 10
    property int delayExecution: 3000

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
            _SLOT.start_direct_sale_print_ereceipt(JSON.stringify(details));
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
                if(abc.counter == (timer_value-showManualPrintButton)){
                    console.log('Show Manual Print Button', abc.counter);
                    manualButtonVisible = true;
                }
                if(abc.counter < 0){
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
            trxNotes = 'Saldo Kartu Anda saat ini Rp. '+FUNC.insert_dot(details.final_balance.toString());
            break;
        case 'shop':
            trxNotes = 'Pastikan Anda mendapatkan '+details.provider;
            break;
        case 'ppob':
            trxNotes = 'Pastikan Anda mendapatkan konfirmasi dari layanan pembayaran/pembelian Anda.';
            break;
        }
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
        if (result == 'ERECEIPT_DONE'){
            var info = p.split('|')[2];
            var data = JSON.parse(info);
            delay(delayExecution, function(){
                ereceipt_show(data);
            });
            return;
        }
        popup_loading.close();
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
            switch_frame('source/take_receipt.png', title, msg, 'backToMain|10', true );
            return;
        }
        if (result == 'DONE') return;
    }


    //==============================================================
    //PUT MAIN COMPONENT HERE

    MainTitle{
        y: 150
        width: 1198
        anchors.top: parent.top
        anchors.topMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Transaksi Anda Berhasil\n'+ trxNotes
        size_: 40
        color_: "white"
    }


    Column{
        id: column
        y: 250
        width: parent.width
        height: 500
        anchors.verticalCenterOffset: 100
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20
        AnimatedImage  {
            id: imageQr
            width: 300
            height: 300
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
            text: textMain
            font.pixelSize: 35
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
        anchors.horizontalCenterOffset: -200
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 175
        anchors.horizontalCenter: parent.horizontalCenter
        button_text: 'PRINT'
        modeReverse: true
        forceColorButton: 'orange'
        MouseArea{
            anchors.fill: parent
            onClicked: {
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
        anchors.horizontalCenterOffset: 200
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 175
        button_text: 'SELESAI\n( ' + showDuration + ' )'
        modeReverse: true
        blinkingMode: true
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
