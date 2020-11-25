import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0

import "base_function.js" as FUNC
import "config.js" as CONF


Base{
    id:ereceipt_view

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    property var press: '0'
    property int timer_value: 60
    property var whatsappNo: 'tersebut'
    property var textMain: 'Pada Android, Tekan Tombol Icon CAMERA di Pojok Kiri Atas'
    property var textSlave: 'Pada IOS, Tekan Tombol Icon CAMERA di Tengah Bawah'
    property var textRebel: ''
    property var textQuard: ''
    property var imageSource: "source/sand-clock-animated-2.gif"
    property var details
    property int textSize: (globalScreenType == '1') ? 38 : 33
    property var showDuration: ''
    property bool retryMode: false

    imgPanel: 'source/cek_saldo.png'
    textPanel: 'Cek Saldo Kartu Prabayar'

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            popup_loading.open('Transaksi Anda Berhasil\nMempersiapkan eReceipt Anda...');
            abc.counter = timer_value;
            my_timer.start();
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
                if(abc.counter < 0){
                    my_timer.stop();
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }
    }

    function print_result(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('print_result', now, p);
        popup_loading.close();
        var result = p.split('|')[1];
        var info = p.split('|')[2];
        if (result == 'DONE') return;
        if (result == 'ERECEIPT_DONE'){
            if (info != undefined){
                var data = JSON.parse(info);
                var whatsappNo = CONF.whatsapp_no;
                whatsappNo = '62' + whatsappNo.substring(1);
    //            imageSource = 'http://mac.local:5050/whatsapp-ereceipt/'+whatsappNo+'/'+data.trxid;
                imageSource = 'http://apiv2.mdd.co.id:10107/whatsapp-ereceipt/'+whatsappNo+'/'+data.trxid;
                console.log('ereceipt_qr', imageSource);
                return;
            }
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
            if (details.shop_type == 'topup') msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Anda Dari Reader';
            if (details.shop_type == 'shop') msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Baru Anda';
            switch_frame('source/take_receipt.png', title, msg, 'backToMain|5', true );
        }
    }


    //==============================================================
    //PUT MAIN COMPONENT HERE

    MainTitle{
        y: 150
        width: 1198
        anchors.top: parent.top
        anchors.topMargin: 150
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Scan QR Berikut di Aplikasi Whatsapp Anda'
        size_: 50
        color_: "white"
    }


    Column{
        id: column
        y: 250
        width: parent.width
        height: 500
        anchors.verticalCenterOffset: -50
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 30
        AnimatedImage  {
            id: imageQr
            width: 350
            height: 350
            scale: 1
            anchors.horizontalCenter: parent.horizontalCenter
            source: imageSource
            fillMode: Image.PreserveAspectFit
        }
        AnimatedImage  {
            id: instructionQr
            width: 800
            height: 450
            scale: 1
            anchors.horizontalCenter: parent.horizontalCenter
            source: 'source/scan_qr_receipt_instruction.jpg'
            fillMode: Image.PreserveAspectFit
        }
        Text{
            text: textMain
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
        anchors.leftMargin: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'CETAK\nSTRUK'
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
                var title = 'Transaksi Berhasil';
                var msg = '';
                if (details.shop_type == 'topup') msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Anda Dari Reader';
                if (details.shop_type == 'shop') msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Baru Anda';
                switch_frame('source/take_receipt.png', title, msg, 'backToMain|5', true );
            }
        }
    }

    CircleButton{
        id: ok_button
        anchors.right: parent.right
        anchors.rightMargin: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'O K\n( ' + showDuration + ' )'
        modeReverse: true
        blinkingMode: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press != '0') return;
                press = '1';
                _SLOT.user_action_log('Press "OK" in e-Receipt Activity');
                var title = 'Transaksi Berhasil';
                var msg = 'Silakan Cek eReceipt Anda di Whatsapp';
                switch_frame('source/take_receipt.png', title, msg, 'backToMain|5', true );
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

    ConfirmView{
        id: confirm_view
        show_text: "Dear Customer"
        show_detail: "Proceed This ?."
        z: 99
        MouseArea{
            id: ok_confirm_view
            x: 668; y:691
            width: 190; height: 50;
            onClicked: {
            }
        }
    }

    NotifView{
        id: notif_view
        isSuccess: false
        show_text: "Dear Customer"
        show_detail: "Please Ensure You have set Your plan correctly."
        z: 99
    }

    LoadingView{
        id:loading_view
        z: 99
        show_text: "Finding Flight..."

    }

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }

}
