import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
import "config.js" as CONF

Base{
    id: global_input_number
    mode_: "reverse"
    isPanelActive: false
    isHeaderActive: true
    isBoxNameActive: false
    textPanel: 'Pilih Produk'
    property int timer_value: 150
    property int max_count: 24
    property int min_count: 10
    property var press: "0"
    property var textInput: ""
    property var mode: undefined
    property var selectedProduct: undefined
    property var wording_text: ''
    property bool checkMode: false
    property bool frameWithButton: false

    property bool cashEnable: false
    property bool cardEnable: false
    property bool qrOvoEnable: false
    property bool qrDanaEnable: false
    property bool qrGopayEnable: false
    property bool qrLinkajaEnable: false
    property var totalPaymentEnable: 0

    property bool isConfirm: false

    signal get_payment_method_signal(string str)
    signal set_confirmation(string str)


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            console.log('mode', mode);
            abc.counter = timer_value
            my_timer.start()
            define_wording()
            press = '0'

        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop()
            loading_view.close()
        }
    }

    Component.onCompleted:{
        set_confirmation.connect(do_set_confirm);
        get_payment_method_signal.connect(process_selected_payment);
        base.result_check_trx.connect(get_trx_check_result);
        base.result_get_device.connect(get_device_status);
        base.result_check_ppob.connect(get_check_ppob_result);
        base.result_check_voucher.connect(get_check_voucher);
        base.result_use_voucher.connect(get_use_voucher);

    }

    Component.onDestruction:{
        set_confirmation.disconnect(do_set_confirm);
        get_payment_method_signal.disconnect(process_selected_payment);
        base.result_check_trx.disconnect(get_trx_check_result);
        base.result_get_device.disconnect(get_device_status);
        base.result_check_ppob.disconnect(get_check_ppob_result);
        base.result_check_voucher.disconnect(get_check_voucher);
        base.result_use_voucher.disconnect(get_use_voucher);

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
                abc.counter = timer_value
            }
        }

        Timer{
            id:my_timer
            interval:1000
            repeat:true
            running:true
            triggeredOnStart:true
            onTriggered:{
                abc.counter -= 1
                if(abc.counter < 0){
                    my_timer.stop()
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }))
                }
            }
        }
    }

    CircleButton{
        id:back_button
        anchors.left: parent.left
        anchors.leftMargin: 100
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50
        button_text: 'BATAL'
        modeReverse: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                my_layer.pop()
            }
        }
    }


    function get_use_voucher(v){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_use_voucher', now, v);
        var res = v.split('|')[1];
        if (['ERROR', 'MISSING_VOUCHER_NUMBER', 'MISSING_REFF_NO'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Menggunakan Kode Voucher Anda', 'backToPrevious', res);
            return;
        }
        //TODO: Do we need to Handle End Process?

    }


    function get_check_voucher(v){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_check_voucher', now, v);
        var res = v.split('|')[1];
        if (['ERROR', 'MISSING_VOUCHER_NUMBER', 'MISSING_PRODUCT_ID'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Kode Voucher Anda', 'backToPrevious', res);
            return;
        }
        //TODO: Parse Voucher Result Into Confirmation Page, Handle End Process

    }

    function get_check_ppob_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        console.log('get_check_ppob_result', now, r);
        var res = r.split('|')[1];
        if (['ERROR', 'MISSING_MSISDN', 'MISSING_PRODUCT_ID'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Nomor Tagihan Anda', 'backToPrevious', res);
            return;
        }
        var i = JSON.parse(res);
        console.log('get_check_ppob_result', now, res);
        //TODO: Check PPOB Parsing Result
        var rows = [
            {label: 'Tanggal', content: now},
            {label: 'Kategori', content: selectedProduct.category.toUpperCase()},
            {label: 'Produk', content: selectedProduct.product_id},
            {label: 'Deskripsi', content: selectedProduct.description},
            {label: 'Biaya Admin', content: '1'},
            {label: 'Harga', content: selectedProduct.rs_price.toString()},
            {label: 'Total', content: selectedProduct.rs_price.toString()}
        ]
        generateConfirm(rows, true);
    }


    function do_set_confirm(_mode){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('Confirmation Flagged By', _mode, now)
        global_confirmation_frame.close()
        isConfirm = true;
    }


    function get_trx_check_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        console.log('get_trx_check_result', now, r);
        popup_loading.close();
        var res = r.split('|')[1]
        if (['ERROR', 'MISSING_REFF_NO'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Nomor Order Anda', 'backToPrevious', res);
            return;
        }
        var i = JSON.parse(res);
        console.log('get_trx_check_result', now, res);
        var trx_name = i.category;
        if (i.category == 'TOPUP'){
            trx_name = 'TOPUP ' + FUNC.get_value(i.remarks.raw.provider) + ' - ' + FUNC.get_value(i.remarks.raw.card_no)
        }
        var rows = [
            {label: 'No Transaksi', content: FUNC.get_value(i.product_id)},
            {label: 'Tanggal', content: FUNC.get_value(i.date)},
            {label: 'Nama Transaksi', content: trx_name},
            {label: 'Nilai Bayar', content: FUNC.insert_dot(i.amount.toString())},
            {label: 'Nilai Diterima', content: FUNC.insert_dot(i.receipt_amount.toString())},
            {label: 'Metode Bayar', content: i.remarks.payment.toUpperCase()},
            {label: 'Status', content: i.status}
        ]
        generateConfirm(rows, false, 'backToMain');
    }

    function generateConfirm(rows, isConfirm, closeMode, timer){
        if (rows==undefined || rows.length == 0) return;
        if (isConfirm==undefined) isConfirm = false;
        if (closeMode==undefined) closeMode = 'closeWindow';
        if (timer!==undefined){
            global_confirmation_frame.withTimer = true;
            global_confirmation_frame.timerDuration = parseInt(timer);
        }
        global_confirmation_frame.modeConfirm = isConfirm;
        global_confirmation_frame.closeMode = closeMode;
        for (var i=0;i<rows.length;i++){
            if (i==0){
                global_confirmation_frame.label1 = rows[i].label;
                global_confirmation_frame.data1 = rows[i].content;
            }
            if (i==1){
                global_confirmation_frame.label2 = rows[i].label;
                global_confirmation_frame.data2 = rows[i].content;
            }
            if (i==2){
                global_confirmation_frame.label3 = rows[i].label;
                global_confirmation_frame.data3 = rows[i].content;
            }
            if (i==3){
                global_confirmation_frame.label4 = rows[i].label;
                global_confirmation_frame.data4 = rows[i].content;
            }
            if (i==4){
                global_confirmation_frame.label5 = rows[i].label;
                global_confirmation_frame.data5 = rows[i].content;
            }
            if (i==5){
                global_confirmation_frame.label6 = rows[i].label;
                global_confirmation_frame.data6 = rows[i].content;
            }
            if (i==6){
                global_confirmation_frame.label7 = rows[i].label;
                global_confirmation_frame.data7 = rows[i].content;
            }
        }
        global_confirmation_frame.open();
    }

    function define_wording(){
        if (mode=='WA_REDEEM'){
            wording_text = 'Masukkan Nomor Invoice Dari WhatsApp Anda';
            min_count = 8;
            return;
        }
        if (mode=='SEARCH_TRX'){
            wording_text = 'Masukkan Minimal 6 Digit (Dari Belakang) Nomor Transaksi Anda';
            min_count = 6;
            return;
        }
        if (mode=='PPOB' && selectedProduct==undefined){
            false_notif('Pastikan Anda Telah Memilih Product Untuk Transaksi', 'backToPrevious');
            return
        }
        _SLOT.start_get_device_status();
        var category = selectedProduct.category.toLowerCase()
        switch(category){
            case 'listrik': case 'tagihan': case 'tagihan air':
                wording_text = 'Masukkan Nomor Meter/ID Pelanggan Anda';
                checkMode = true;
                min_count = 19;
            break;
            case 'pulsa': case 'paket data': case 'ojek online':
                wording_text = 'Masukkan Nomor Telepon Tujuan';
                min_count = 10;
            break;
            case 'uang elektronik':
                wording_text = 'Masukkan Nomor Kartu Prabayar Anda';
                min_count = 15;
            break;
            default:
                wording_text = 'Masukkan Nomor Pelanggan Anda';
                min_count = 15;
        }
    }

    function false_notif(message, closeMode, textSlave){
        if (closeMode==undefined) closeMode = 'backToMain';
        if (textSlave==undefined) textSlave = '';
        press = '0';
        switch_frame('source/smiley_down.png', message, textSlave, closeMode, false )
        return;
    }

    function switch_frame(imageSource, textMain, textSlave, closeMode, smallerText){
        frameWithButton = false;
        if (closeMode.indexOf('|') > -1){
            closeMode = closeMode.split('|')[0];
            var timer = closeMode.split('|')[1];
            global_frame.timerDuration = parseInt(timer);
        }
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.closeMode = closeMode;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.withTimer = true;
        global_frame.open();
    }

    function switch_frame_with_button(imageSource, textMain, textSlave, closeMode, smallerText){
        frameWithButton = true;
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.closeMode = closeMode;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.withTimer = false;
        global_frame.open();
    }


    function process_selected_payment(channel){
        var globalDetails = get_cart_details(channel);
        my_layer.push(mandiri_payment_process, {details: globalDetails});
    }

    function get_cart_details(channel){
        var details = {
            payment: channel,
            shop_type: 'ppob',
            time: new Date().toLocaleTimeString(Qt.locale("id_ID"), "hh:mm:ss"),
            date: new Date().toLocaleDateString(Qt.locale("id_ID"), Locale.ShortFormat),
            epoch: new Date().getTime()
        }
        details.qty = '1';
        details.value = selectedProduct.rs_price.toString();
        details.provider = selectedProduct.operator;
        details.admin_fee = '0';
        details.status = selectedProduct.status;
        details.raw = selectedProduct;
        return details;
    }

    function get_device_status(s){
        console.log('get_device_status', s);
        var device = JSON.parse(s);
        if (device.MEI == 'AVAILABLE' || device.GRG == 'AVAILABLE'){
            cashEnable = true;
            totalPaymentEnable += 1;
        }
        if (device.EDC == 'AVAILABLE') {
            cardEnable = true;
            totalPaymentEnable += 1;
        }
        if (device.QR_LINKAJA == 'AVAILABLE') {
            qrLinkajaEnable = true;
            totalPaymentEnable += 1;
        }
        if (device.QR_DANA == 'AVAILABLE') {
            qrDanaEnable = true;
            totalPaymentEnable += 1;
        }
        if (device.QR_GOPAY == 'AVAILABLE') {
            qrGopayEnable = true;
            totalPaymentEnable += 1;
        }
        if (device.QR_OVO == 'AVAILABLE') {
            qrOvoEnable = true;
            totalPaymentEnable += 1;
        }

    }

    //==============================================================
    //PUT MAIN COMPONENT HERE

    MainTitle{
        anchors.top: parent.top
        anchors.topMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: wording_text
        visible: !popup_loading.visible
        size_: 50
        color_: "white"

    }

    TextRectangle{
        id: textRectangle
        width: 650
        height: 110
        color: "white"
        radius: 0
        anchors.top: parent.top
        anchors.topMargin: 325
        border.color: CONF.text_color
        anchors.horizontalCenter: parent.horizontalCenter
    }

    TextInput {
        id: inputText
        height: 60
        anchors.centerIn: textRectangle;
        text: textInput
        cursorVisible: true
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: 50
        color: CONF.text_color
        clip: true
        visible: true
        focus: true
    }


    NumKeyboardCircle{
        id:virtual_keyboard
        width:320
        height:420
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 130
        anchors.horizontalCenter: parent.horizontalCenter
        visible: true
        property int count:0

        Component.onCompleted: {
            virtual_keyboard.strButtonClick.connect(typeIn)
            virtual_keyboard.funcButtonClicked.connect(functionIn)
        }

        function functionIn(str){
            if(str=="Back"){
                count--;
                textInput=textInput.substring(0,textInput.length-1);
            }
            if(str=="Clear"){
                textInput = "";
                max_count = 24;
                press = "0";
            }
        }

        function typeIn(str){
            if (str == "" && count > 0){
                if(count>=max_count){
                    count=max_count
                }
                count--
                textInput=textInput.substring(0,count);
            }
            if (str!=""&&count<max_count){
                count++
            }
            if (count>=max_count){
                str=""
            } else {
                textInput += str
            }
            abc.counter = timer_value
            my_timer.restart()
        }
    }


    CircleButton{
        id:next_button
        anchors.right: parent.right
        anchors.rightMargin: 100
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50
        button_text: 'LANJUT'
        modeReverse: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                console.log('button "LANJUT" is pressed..!')
                if(press != "0") return;
                if (max_count+1 > textInput.length){
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    press = "1"
                    console.log('number input', now, textInput);
                    popup_loading.open()
                    switch(mode){
                    case 'PPOB':
                        if (checkMode){
                            var msisdn = textInput;
                            var product_id = selectedProduct.product_id;
                            _SLOT.start_check_ppob_product(msisdn, product_id);
                            popup_loading.open();
                            return;
                        } else {
                            var rows = [
                                {label: 'Tanggal', content: now},
                                {label: 'Kategori', content: selectedProduct.category.toUpperCase()},
                                {label: 'Produk', content: selectedProduct.product_id},
                                {label: 'Deskripsi', content: selectedProduct.description},
                                {label: 'Jumlah', content: '1'},
                                {label: 'Harga', content: selectedProduct.rs_price},
                                {label: 'Total', content: selectedProduct.rs_price}
                            ]
                            generateConfirm(rows, true);
                            return;
                        }
                    case 'SEARCH_TRX':
                        console.log('Checking Transaction Number : ', textInput);
                        _SLOT.start_check_trx_online(textInput);
                        return
                    case 'WA_REDEEM':
                        // TODO: Check SLOT Function Check WA Payment
                        console.log('Checking WA Invoice Number : ', textInput);
                        _SLOT.start_check_voucher(textInput);
                        return;
                    default:
                        false_notif('No Handle Set For This Action', 'backToMain');
                        return
                    }
                }
            }
        }
    }


    //==============================================================


    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }

    LoadingView{
        id:loading_view
        z: 99
        show_text: "Finding Flight..."
    }


    GlobalConfirmationFrame{
        id: global_confirmation_frame
        calledFrom: 'global_input_number'

    }


    SelectPaymentPopupNotif{
        id: select_payment
        visible: isConfirm
        calledFrom: 'global_input_number'
        _cashEnable: cashEnable
        _cardEnable: cardEnable
        _qrOvoEnable: qrOvoEnable
        _qrDanaEnable: qrDanaEnable
        _qrGopayEnable: qrGopayEnable
        _qrLinkAjaEnable: qrLinkajaEnable
        totalEnable: totalPaymentEnable
    }




}

