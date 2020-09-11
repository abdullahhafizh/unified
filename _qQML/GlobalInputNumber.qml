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
    property var selectedProduct
    property var wording_text: ''
    property bool checkMode: false
    property bool frameWithButton: false

    property bool cashEnable: false
    property bool cardEnable: false
    property bool qrOvoEnable: false
    property bool qrDanaEnable: false
    property bool qrGopayEnable: false
    property bool qrLinkajaEnable: false
    property bool qrShopeeEnable: false
    property bool qrJakoneEnable: false
    property var totalPaymentEnable: 0

    property bool retryAbleTransaction: false

    property bool isConfirm: false
    property var ppobMode
    property var ppobTagihanData
    property var vCollectionMode
    property var vCollectionData

    property var retryDetails
    property int receivedPayment: 0
    property int pendingPayment: 0

    signal get_payment_method_signal(string str)
    signal set_confirmation(string str)


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
//            console.log('mode', mode, JSON.stringify(selectedProduct));
            abc.counter = timer_value;
            my_timer.start();
            define_wording();
            isConfirm = false;
            vCollectionMode = undefined;
            vCollectionData = undefined;
            retryAbleTransaction = false;
            receivedPayment = 0;
            pendingPayment = 0;
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
        base.result_get_payment.connect(get_payments);
        base.result_check_ppob.connect(get_check_ppob_result);
        base.result_check_voucher.connect(get_check_voucher);
        base.result_use_voucher.connect(get_use_voucher);
        base.result_cd_move.connect(card_eject_result);

    }

    Component.onDestruction:{
        set_confirmation.disconnect(do_set_confirm);
        get_payment_method_signal.disconnect(process_selected_payment);
        base.result_check_trx.disconnect(get_trx_check_result);
        base.result_get_payment.disconnect(get_payments);
        base.result_check_ppob.disconnect(get_check_ppob_result);
        base.result_check_voucher.disconnect(get_check_voucher);
        base.result_use_voucher.disconnect(get_use_voucher);
        base.result_cd_move.disconnect(card_eject_result);

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
                notice_retry_able.modeReverse = (abc.counter % 2 == 0) ? true : false;
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
        anchors.leftMargin: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'BATAL'
        modeReverse: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                _SLOT.user_action_log('press "BATAL" In Input Number Page');
                my_layer.pop()
            }
        }
    }

    function card_eject_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('card_eject_result', now, r);
        popup_loading.close();
        abc.counter = 30;
        my_timer.restart();
//        if (r=='EJECT|PARTIAL'){
//            press = '0';
//            attemptCD -= 1;
//            switch_frame('source/take_card.png', 'Silakan Ambil Kartu Anda', 'Kemudian Tekan Tombol Lanjut', 'closeWindow|25', true );
//            centerOnlyButton = true;
//            modeButtonPopup = 'retrigger_card';
//            return;
//        }
        if (r == 'EJECT|ERROR') {
            switch_frame('source/smiley_down.png', 'Mohon Maaf Terjadi Kesalahan', 'Transaksi Pengambilan Kartu Digagalkan', 'backToMain', true )
            return;
        }
        if (r == 'EJECT|SUCCESS') {
            switch_frame('source/thumb_ok.png', 'Silakan Ambil Kartu dan Struk Transaksi Anda', 'Terima Kasih', 'backToMain', false )
            var reff_no_voucher = new Date().getTime().toString() + '-' + vCollectionData.product.toString() + '-' + vCollectionData.slot.toString()
            _SLOT.start_use_voucher(textInput, reff_no_voucher);
            return;
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
    }

    function get_check_voucher(v){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        console.log('get_check_voucher', now, v);
        var res = v.split('|')[1];
        if (['ERROR', 'MISSING_VOUCHER_NUMBER', 'MISSING_PRODUCT_ID', 'EMPTY'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Kode Voucher Anda', 'backToPrevious', res);
            return;
        }
        console.log('get_check_voucher', now, res);
        var i = JSON.parse(v.replace('CHECK_VOUCHER|', ''));
        vCollectionData = i;
        vCollectionMode = i.mode;
        if (i.qty==0){
            false_notif('Kode Voucher Tersebut Sudah Pernah Digunakan', 'backToMain', '');
            return;
        }
        var rows = [
            {label: 'Tanggal', content: now},
            {label: 'No Voucher', content: i.product},
        ]
        if (i.mode=='card_collection'){
            var desc = i.card.remarks.split('|')[0];
            rows.push({label: 'Produk', content: i.card.name});
            rows.push({label: 'Deskripsi', content: desc});
            rows.push({label: 'Jumlah', content: i.qty.toString()});
            var unit_price = parseInt(i.card.sell_price);
            rows.push({label: 'Harga', content: FUNC.insert_dot(unit_price.toString())});
            var total_price = parseInt(i.qty) * unit_price;
            rows.push({label: 'Total', content: FUNC.insert_dot(total_price.toString())});
        }
        generateConfirm(rows, true);
    }

    function get_check_ppob_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        console.log('get_check_ppob_result', now, r);
        var res = r.split('|')[1];
        if (['ERROR', 'MISSING_MSISDN', 'MISSING_PRODUCT_ID'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Nomor Tagihan Anda', 'backToPrevious', res);
            return;
        }
        console.log('get_check_ppob_result', now, res);
        var i = JSON.parse(res);
        if (i.payable == 0){
            false_notif('Tagihan Anda Tidak Ditemukan/Belum Tersedia Saat Ini', 'backToPrevious', 'NOT_AVAILABLE');
            return;
        }
        ppobTagihanData = {
            customer: i.customer,
            value: i.total.toString(),
            admin_fee: i.admin_fee,
            msisdn: i.msisdn,
            provider: 'Tagihan ' + i.category,
            billing_check: i,
        }
        var rows = [
            {label: 'Tanggal', content: now},
            {label: 'Tagihan', content: i.category.toUpperCase() + ' ' + i.msisdn},
            {label: 'Pelanggan', content: i.customer},
            {label: 'Biaya', content: FUNC.insert_dot(i.ori_amount.toString())},
            {label: 'Biaya Admin', content: FUNC.insert_dot(i.admin_fee.toString())},
            {label: 'Total', content: FUNC.insert_dot(i.total.toString())}
        ]
        generateConfirm(rows, true);
    }

    function do_set_confirm(_mode){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('Confirmation Flagged By', _mode, now)
        global_confirmation_frame.no_button()
        if (vCollectionData==undefined){
            popup_loading.close();
            isConfirm = true;
        } else {
            popup_loading.open();
            switch(vCollectionMode){
            case 'card_collection':
                console.log('Card Collection...')
                switch_frame('source/sand-clock-animated-2.gif', 'Memproses Kartu Baru Anda', 'Mohon Tunggu Beberapa Saat', 'closeWindow', true )
                var attempt = vCollectionData.slot.toString();
                var multiply = vCollectionData.qty.toString();
                _SLOT.start_multiple_eject(attempt, multiply);
                break;
            case 'mandiri_topup':
                console.log('Mandiri Topup...')
                break;
            case 'bni_topup':
                console.log('BNI Topup...')
                break;
            case 'dki_topup':
                console.log('DKI Topup...')
                break;
            }
        }
    }


    function set_pending_trx_data(obj){
        if (obj != undefined){
            retryDetails = obj;
            delete retryDetails.payment_error;
            delete retryDetails.process_error;
            console.log('set_pending_trx_data', JSON.stringify(retryDetails));
        }
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
        var trx_name = '';
        if (i.category == 'PPOB') trx_name = i.category + ' ' + i.remarks.product_id;
        if (i.category == 'TOPUP')
            trx_name = i.category + ' ' + FUNC.get_value(i.remarks.raw.provider) + ' ' + FUNC.get_value(i.remarks.raw.card_no);
        var total_payment = i.amount.toString()
        if (i.category == 'SHOP'){
            trx_name = i.category + ' ' + i.remarks.provider;
            total_payment = i.remarks.value.toString();
        }
        var amount = FUNC.insert_dot(i.receipt_amount.toString());
        if (i.remarks.payment_received==undefined) i.remarks.payment_received = i.receipt_amount;
        if (i.status!='PAID' || i.status=='FAILED' || i.status=='PENDING') amount = FUNC.insert_dot(i.remarks.payment_received.toString());
        if (i.payment_method=='MEI' || i.payment_method=='cash') i.payment_method = "CASH";
        var trx_id = FUNC.get_value(i.product_id);
        if (trx_id=='') trx_id = FUNC.get_value(i.remarks.shop_type) + FUNC.get_value(i.remarks.epoch.toString());
        var rows = [
                    {label: 'No Transaksi', content: trx_id},
                    {label: 'Tanggal', content: FUNC.get_value(i.date)},
                    {label: 'Jenis Transaksi', content: trx_name},
                    {label: 'Nilai Bayar', content: FUNC.insert_dot(total_payment)},
                    {label: 'Nilai Diterima', content: amount},
                    {label: 'Metode Bayar', content: i.payment_method.toUpperCase()},
                    {label: 'Status', content: i.status}
                ]
        if (i.remarks.product_category == 'Listrik' && i.status == 'PAID' && i.category == 'PPOB' ){
            var add_info = i.remarks.remarks;
            console.log('get add_info', JSON.stringify(add_info.data.sn));
            var sn = add_info.data.sn.split('*')[0];
            rows = [
                        {label: 'No Transaksi', content: FUNC.get_value(i.product_id)},
                        {label: 'Tanggal', content: FUNC.get_value(i.date)},
                        {label: 'Jenis Transaksi', content: trx_name},
                        {label: 'Pembayaran', content: FUNC.insert_dot(i.amount.toString())},
                        {label: 'Metode Bayar', content: i.payment_method.toUpperCase()},
                        {label: 'Status', content: i.status},
                        {label: 'Token/SN', content: sn}
                    ]
        }
        generateConfirm(rows, false, 'backToMain');
        // Set Value For Retry Transaction If Status Pending
        if (i.status=='PENDING') {
            receivedPayment = parseInt(amount);
            pendingPayment = parseInt(i.remarks.value) - receivedPayment;
            set_pending_trx_data(i.remarks);
            if (i.retry_able == 1) {
                retryAbleTransaction = true;
                global_confirmation_frame.no_button();
            }
        }
        // ---
    }

    function generateConfirm(rows, confirmation, closeMode, timer){
        press = '0';
        global_confirmation_frame.open(rows, confirmation, closeMode, timer);
    }

    function define_wording(){
        if (mode=='WA_VOUCHER'){
            wording_text = 'Masukkan Kode Voucher (VCODE) Dari WhatsApp Anda';
            min_count = 8;
            return;
        }
        if (mode=='SEARCH_TRX'){
            wording_text = 'Masukkan Minimal 6 Digit (Dari Belakang)/Kode Voucher Transaksi Anda';
            min_count = 6;
            return;
        }
//        if (mode=='PPOB' && selectedProduct==undefined){
//            false_notif('Pastikan Anda Telah Memilih Product Untuk Transaksi', 'backToPrevious');
//            return
//        }
        _SLOT.start_get_payments();
        var category = selectedProduct.category.toLowerCase();
        var operator = selectedProduct.operator;
        switch(category){
            case 'tagihan': case 'tagihan air':
                wording_text = 'Masukkan Nomor Meter/ID Pelanggan Anda';
                checkMode = true;
                min_count = 19;
            break;
            case 'pulsa': case 'paket data': case 'ojek online':
                wording_text = 'Masukkan Nomor Telepon Seluler Tujuan';
                min_count = 10;
            break;
            case 'uang elektronik':
                if (['DISABLE>>>TCASH LINKAJA'].indexOf(operator) > -1){
                    wording_text = 'Masukkan 10 Digit User Token LinkAja (99XXXXXXXX)';
                    min_count = 10;
                } else if (['TCASH LINKAJA', 'OVO', 'DANA', 'BUKADANA', 'TIXID'].indexOf(operator) > -1) {
                    wording_text = 'Masukkan Nomor Terdaftar Pada Aplikasi';
                    min_count = 15;
                }  else {
                    wording_text = 'Masukkan Nomor Kartu Prabayar Anda';
                    min_count = 15;
                }
            break;
            case 'voucher':
                wording_text = 'Masukkan Nomor Telepon Seluler Anda';
                min_count = 10;
            break;
            default:
                wording_text = 'Masukkan Nomor Pelanggan/Tagihan Anda';
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
        press = '0';
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
        press = '0';
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.closeMode = closeMode;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.withTimer = false;
        global_frame.open();
    }

    function process_selected_payment(channel){
        var details = {
            payment: channel,
            shop_type: 'ppob',
            time: new Date().toLocaleTimeString(Qt.locale("id_ID"), "hh:mm:ss"),
            date: new Date().toLocaleDateString(Qt.locale("id_ID"), Locale.ShortFormat),
            epoch: new Date().getTime()
        }
        details.qty = 1;
        details.status = '1';
        details.raw = selectedProduct;
        details.category = selectedProduct.category;
        details.operator = selectedProduct.operator;
        details.description = selectedProduct.description;
        details.product_id = selectedProduct.product_id;
        details.rs_price = selectedProduct.rs_price;
        details.amount = selectedProduct.amount;
        details.ppob_mode = ppobMode;
        if (ppobTagihanData!==undefined && ppobMode=='tagihan'){
            details.customer = ppobTagihanData.customer;
            details.value = ppobTagihanData.value;
            details.admin_fee = ppobTagihanData.admin_fee;
            details.msisdn = ppobTagihanData.msisdn;
            details.provider = ppobTagihanData.provider;
            details.billing_check = ppobTagihanData.billing_check;
        } else if (ppobMode=='non-tagihan'){
            details.customer = textInput;
            details.value = selectedProduct.rs_price.toString();
            details.admin_fee = '0';
            details.msisdn = textInput;
//            details.provider = selectedProduct.category + ' ' + selectedProduct.description;
            details.provider = selectedProduct.description;
        }
        _SLOT.python_dump(JSON.stringify(details));
        my_layer.push(general_payment_process, {details: details});
    }

    function get_payments(s){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_payments', now, s);
        var device = JSON.parse(s);
        if (device.MEI == 'AVAILABLE' || device.BILL == 'AVAILABLE'){
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
        if (device.QR_SHOPEEPAY == 'AVAILABLE') {
            qrShopeeEnable = true;
            totalPaymentEnable += 1;
        }
        if (device.QR_JAKONE == 'AVAILABLE') {
            qrJakoneEnable = true;
            totalPaymentEnable += 1;
        }
        //================================
//        isConfirm = true;

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
        // Use Frame Color
        color: CONF.frame_color
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
        anchors.rightMargin: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'LANJUT'
        modeReverse: true
        visible: !global_confirmation_frame.visible && !isConfirm && !popup_loading.visible && (textInput.length >= 6)
        blinkingMode: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                console.log('button "LANJUT" is pressed..!')
                _SLOT.user_action_log('press "LANJUT" In Input Number Page');
                if(press != "0") return;
                var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                press = "1"
//                    console.log('number input', now, textInput);
                switch(mode){
                case 'PPOB':
                    popup_loading.open()
                    if (checkMode){
                        var msisdn = textInput;
                        var product_id = selectedProduct.product_id;
                        ppobMode = 'tagihan';
                        _SLOT.start_check_ppob_product(msisdn, product_id);
                        return;
                    } else {
                        var product_name = selectedProduct.category.toUpperCase() + ' ' + selectedProduct.description;
                        var rows = [
                            {label: 'Tanggal', content: now},
                            {label: 'Produk', content: product_name},
                            {label: 'No Tujuan', content: textInput},
                            {label: 'Jumlah', content: '1'},
                            {label: 'Harga', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
                            {label: 'Total', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
                        ]
                        ppobMode = 'non-tagihan';
                        generateConfirm(rows, true);
                        return;
                    }
                case 'SEARCH_TRX':
                    console.log('Checking Transaction Number : ', now, textInput);
                    popup_loading.open('Memeriksa Transaksi Anda...')
                    _SLOT.start_check_status_trx(textInput);
                    return
                case 'WA_VOUCHER':
                    console.log('Checking WA Invoice Number : ', now, textInput);
                    popup_loading.open('Memeriksa Kode Voucher Anda Anda...')
                    _SLOT.start_check_voucher(textInput);
                    return;
                default:
                    false_notif('No Handle Set For This Action', 'backToMain');
                    return
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

        BoxTitle{
            id: notice_retry_able
            width: 1200
            height: 120
            visible: retryAbleTransaction
            radius: 50
            fontSize: 30
            border.width: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 150
            anchors.horizontalCenter: parent.horizontalCenter
            title_text: 'TRANSAKSI ANDA DAPAT DILANJUTKAN\nSILAKAN TEKAN TOMBOL LANJUT'
    //        modeReverse: (abc.counter %2 == 0) ? true : false
            boxColor: CONF.frame_color

        }

        CircleButton{
            id: proceed_button
            anchors.right: parent.right
            anchors.rightMargin: 100
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 50
            button_text: 'LANJUT'
            modeReverse: true
            blinkingMode: true
            visible: retryAbleTransaction
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "LANJUT" For Retry Transaction');
                    console.log('Press "LANJUT" For Retry Transaction');
                    if (press != '0') return;
                    press = '1';
                    my_layer.push(retry_payment_process, {details: retryDetails, pendingPayment: pendingPayment, receivedPayment: receivedPayment});
                }
            }
        }

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
        _qrShopeeEnable: qrShopeeEnable
        _qrJakoneEnable: qrJakoneEnable
        totalEnable: totalPaymentEnable
        z: 99
    }




}

