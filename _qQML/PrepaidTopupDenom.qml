import QtQuick 2.4
import QtQuick.Controls 1.3
//import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
//import "config.js" as CONF

Base{
    id: prepaid_topup_denom

//        property var globalScreenType: '2'
//        height: (globalScreenType=='2') ? 1024 : 1080
//        width: (globalScreenType=='2') ? 1280 : 1920
    property int timer_value: (VIEW_CONFIG.page_timer * 2)
    property var press: '0'
    idx_bg: 0
    property var denomTopup: undefined
    property var provider: 'e-Money Mandiri'
    property bool emoneyAvailable: false
    property bool tapcashAvailable: false
    property bool brizziAvailable: false
    property bool flazzAvailable: false
    property bool jakcardAvailable: false
    property var adminFee: 1500
    property var mandiriTopupWallet: 0
    property var bniTopupWallet: 0
    property var topupData: undefined
    property var cardData: undefined
    property int cardBalance: 0
    property var selectedDenom: 0
    property var globalCart
    property var selectedPayment: undefined
    property var globalDetails
    property var shopType: 'topup'

    property bool mainVisible: false
    property var activePayment: []

    property var paymentFeeSetting

    property var bniWallet1: 0
    property var bniWallet2: 0

    property int totalPay: 0

    property bool frameWithButton: false
    property var modeButtonPopup

    property var tinyDenomTopup: ''
    property var smallDenomTopup: ''
    property var midDenomTopup: ''
    property var highDenomTopup: ''

    //Redefine Denom Row Space and Button Denom
    property var rowDenomSpacing: 50
    property var buttonDenomWidth: 359

    property variant allowedBank: []
    property variant activeQRISProvider: []

    // By Default Only Can Show 3 Denoms, Adjusted with below properties
    property int miniDenomValue: 10000
    property bool miniDenomActive: true
    // ----------------------------------
    property int maxBalance: 1000000

    property var cashboxFull
    property bool onProgressTask

    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false

    signal topup_denom_signal(string str)
    signal get_payment_method_signal(string str)
    signal set_confirmation(string str)
    imgPanel: 'source/topup_kartu.png'
    textPanel: 'Isi Ulang Saldo Kartu Prabayar'


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            abc.counter = timer_value;
            my_timer.start();
            _SLOT.start_get_payments();
            _SLOT.start_get_price_setting();
            mainVisible = false;
            press = '0';
            cardBalance = 0;
            totalPay = 0;
            denomTopup = undefined;
            provider = undefined;
            selectedPayment = undefined;
            onProgressTask = false;
            activeQRISProvider = [];
            activePayment = [];
            globalDetails = undefined;
            frameWithButton = false;
            if (cardData==undefined){
                if (VIEW_CONFIG.ui_simplify){
                    console.log('Direct Call Check Balance');
                    var textMain = 'Letakkan kartu prabayar Anda di alat pembaca kartu yang bertanda';
                    var textSlave = 'Pastikan kartu Anda tetap berada di alat pembaca kartu sampai transaksi selesai';
                    check_user_card(textMain, textSlave);
                } else {
                    open_preload_notif();
                }
            } else {
                parse_cardData(cardData);
            }
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop();
        }
    }

    Component.onCompleted:{
        set_confirmation.connect(do_set_confirm);
        get_payment_method_signal.connect(process_selected_payment);
        topup_denom_signal.connect(set_selected_denom);
        base.result_get_payment.connect(get_payments);
        base.result_balance_qprox.connect(get_balance);
        base.result_topup_readiness.connect(topup_readiness);
        base.result_price_setting.connect(define_price);
    }

    Component.onDestruction:{
        set_confirmation.disconnect(do_set_confirm);
        get_payment_method_signal.disconnect(process_selected_payment);
        topup_denom_signal.disconnect(set_selected_denom);
        base.result_get_payment.disconnect(get_payments);
        base.result_balance_qprox.disconnect(get_balance);
        base.result_topup_readiness.disconnect(topup_readiness);
        base.result_price_setting.disconnect(define_price);

    }

    function check_user_card(textMain, textSlave){
        switch_frame('source/reader_sign.png', textMain, textSlave, 'closeWindow|10', false );
        _SLOT.start_check_card_balance();
    }

    function get_payment_fee(p, d){
        if (p === undefined || paymentFeeSetting[p] === undefined) return 0;
        var fee = paymentFeeSetting[p];
        var init_price = d;
        if (parseInt(fee) < 1) fee = (fee * 100 * parseInt(init_price));
        return fee;
    }

    function get_payments(s){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_payments', s, now);
        var device = JSON.parse(s);
        // if (device.PRINTER_STATUS != 'OK'){
        //     popup_loading.close();
        //     switch_frame('source/smiley_down.png', 'Mohon Maaf, Struk Habis.', 'Saat Ini mesin tidak dapat mengeluarkan bukti transaksi.', 'backToMain|'+VIEW_CONFIG.failure_page_timer.toString(), false );
        //     my_timer.stop();
        //     return;
        // }
        paymentFeeSetting = device.PAYMENT_FEE;

        if (device.BILL == 'CASHBOX_FULL'){
            cashboxFull = true;
        }
        if (device.MEI == 'AVAILABLE' || device.BILL == 'AVAILABLE'){
            cashboxFull = false;
            activePayment.push('cash');
        }
        if (device.EDC == 'AVAILABLE') {
            activePayment.push('debit');
        }
        if (device.QR_GOPAY == 'AVAILABLE') {
            activeQRISProvider.push('gopay');
            activePayment.push('gopay');
        }
        if (device.QR_LINKAJA == 'AVAILABLE') {
            activePayment.push('linkaja');
            activeQRISProvider.push('linkaja')
        }
        if (device.QR_DANA == 'AVAILABLE') {
            activePayment.push('dana');
            activeQRISProvider.push('dana')
        }
        if (device.QR_DUWIT == 'AVAILABLE') {
            activePayment.push('duwit');
            activeQRISProvider.push('duwit')
        }
        if (device.QR_OVO == 'AVAILABLE') {
            activePayment.push('ovo');
            activeQRISProvider.push('ovo')
        }
        if (device.QR_SHOPEEPAY == 'AVAILABLE') {
            activePayment.push('shopeepay');
            activeQRISProvider.push('shopeepay')
        }
        if (device.QR_JAKONE == 'AVAILABLE') {
            activePayment.push('jakone');
            activeQRISProvider.push('jakone')
        }
        if (device.QR_BCA == 'AVAILABLE') {
            activePayment.push('bca-qris');
            activeQRISProvider.push('bca-qris')
        }
        if (device.QR_BNI == 'AVAILABLE') {
            activePayment.push('bni-qris');
            activeQRISProvider.push('bni-qris')
        }
        if (device.QR_MDR == 'AVAILABLE') {
            activeQRISProvider.push('mdr-qris');
            activePayment.push('mdr-qris');
        }
        if (device.QR_NOBU == 'AVAILABLE') {
            activeQRISProvider.push('nobu-qris');
            activePayment.push('nobu-qris');
        }
        if (device.QR_BRI == 'AVAILABLE') {
            activeQRISProvider.push('bri-qris');
            activePayment.push('bri-qris');
        }
    }

    function disable_qr_payment(){
        // Set Active Payment Only Cash
        var debit_active = activePayment.indexOf('debit');
        activePayment = ['cash'];
        if (debit_active > -1) activePayment.push('debit');
        // Disable All QRIS Provider
        activeQRISProvider = [];
    }

    function do_set_confirm(triggered){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('do_set_confirm', now, triggered);
        if (onProgressTask ){
            console.log('do_set_confirm', now, 'ALREADY_ON_PROGRESS_TASK');
            return;
        }
        onProgressTask = true;
        var details = {
            payment: selectedPayment,
            shop_type: 'topup',
            time: new Date().toLocaleTimeString(Qt.locale("id_ID"), "hh:mm:ss"),
            date: new Date().toLocaleDateString(Qt.locale("id_ID"), Locale.ShortFormat),
            epoch: (new Date().getTime() * 1000) + (Math.floor(Math.random() * (987 - 101)) + 101)
        }
        globalCart = {
            value: selectedDenom.toString(),
            provider: provider,
            admin_fee: adminFee,
            card_no: cardData.card_no,
            prev_balance: cardData.balance,
            bank_type: cardData.bank_type,
            bank_name: cardData.bank_name,
            timestamp: cardData.timestamp
        }
        var topup_amount = parseInt(selectedDenom) - parseInt(adminFee);
        var final_balance = parseInt(cardData.balance) + topup_amount;
        details.qty = 1;
        details.value = selectedDenom.toString();
        details.provider = provider;
        details.admin_fee = adminFee;
        details.raw = globalCart;
        details.status = '1';
        details.final_balance = final_balance.toString();
        details.denom = topup_amount.toString();
        details.init_total = details.qty * parseInt(selectedDenom);
        // Add Service Charge Based On Payment
        details.service_charge = get_payment_fee(selectedPayment, details.init_total);
        globalDetails = details;
        my_layer.push(general_payment_process, {details: globalDetails, cardNo: cardData.card_no});

    }

    function process_selected_payment(method){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('process_selected_payment', now, method);

        if (method=='MULTI_QR'){
            press = '0';
            if (activeQRISProvider.length == 1){
                method = activeQRISProvider[0];
            } else {
                select_payment.close();
                select_qr_provider.open();
                notice_topup_single_denom.visible = false;
                return;
            }            
        }
        if (method=='cash' && cashboxFull){
            console.log('Cashbox Full Detected', method);
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf, Pembayaran Tunai tidak dapat dilakukan saat ini.', ' Silakan Pilih Metode Pembayaran lain yang tersedia.', 'closeWindow|3', false );
            return;
        }
        //This Var Will be used for Revalidation Card Number
        selectedPayment = method;
        //===

        totalPay = parseInt(selectedDenom) + parseInt(adminFee);

        //Auto Payment Process Base on UI Simplification
        if (VIEW_CONFIG.ui_simplify) {
            var textMain = 'Memeriksa kembali kartu prabayar Anda';
            var textSlave = 'Pastikan kartu yang ditempel adalah kartu yang sama pada saat awal transaksi';
            check_user_card(textMain, textSlave);
        }
        //Must Press Flagging Here To Avoid Multi Trigger
        press = '0';
    }


    function do_validate_payment_rules(amount){
        console.log('do_validate_payment_rules', amount, VIEW_CONFIG.payment_rules);
        // VIEW_CONFIG.payment_rules = 'cash:>:10000,qr:<:100000';
        if (amount === undefined) amount = 0;
        var existing_payment = activePayment;
        if (VIEW_CONFIG.payment_rules !== undefined || VIEW_CONFIG.payment_rules.length > 3){
            if (VIEW_CONFIG.payment_rules.indexOf(':') > -1){
                var rules = VIEW_CONFIG.payment_rules.split(',');
                for (var r in rules){
                    var removeChannel = false;
                    var channel = r.split(':')[0];
                    var opr = r.split(':')[1];
                    var limit = r.split(':')[2];
                    switch (opr){
                        case '>':
                            if (parseInt(amount) < parseInt(limit)) removeChannel = true;
                        break;
                        case '<':
                            if (parseInt(amount) > parseInt(limit)) removeChannel = true;
                        break;
                        case '=':
                            if (parseInt(amount) != parseInt(limit)) removeChannel = true;
                        break;
                        case '<>':
                            if (parseInt(amount) == parseInt(limit)) removeChannel = true;
                        break;
                    }
                    if (removeChannel){
                        if (channel == 'qr'){
                            activePayment = [];
                            if (existing_payment.indexOf('cash')) activePayment.push('cash');
                            if (existing_payment.indexOf('debit')) activePayment.push('debit');
                        } else if (activePayment.indexOf(channel) > -1){
                            activePayment = activePayment.filter(function(value, index, arr){ return value != channel });
                        }
                        console.log('Removing Channel', channel, activePayment);
                    }
                }
            }
        }
        if (activePayment.length == 0){
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Semua channel pembayaran untuk transaksi ini tidak aktif.', 'backToMain', false );
            return;
        }
    }

    function define_price(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('define_price', p, now);
        var price = JSON.parse(p);
        adminFee = parseInt(price.adminFee);
        console.log('adminFee', adminFee);
    }

    function topup_readiness(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('topup_readiness', r, now);
        if (topupData==undefined) topupData = r;
        var ready = JSON.parse(r)
        mandiriTopupWallet = parseInt(ready.balance_mandiri);
        bniTopupWallet = parseInt(ready.balance_bni);
        if (ready.mandiri=='AVAILABLE' && mandiriTopupWallet > 0) {
            emoneyAvailable = true;
            allowedBank.push('MANDIRI');
        }
        if (ready.bni=='AVAILABLE' && bniTopupWallet > 0) {
            tapcashAvailable = true;
            allowedBank.push('BNI');
        }
        if (ready.bri=='AVAILABLE') {
            brizziAvailable = true;
            allowedBank.push('BRI');
        }
        if (ready.dki=='AVAILABLE') {
            jakcardAvailable = true;
            allowedBank.push('DKI');
        }
        if (ready.bca=='AVAILABLE') {
            flazzAvailable = true;
            allowedBank.push('BCA');
        }

        if (allowedBank.indexOf(cardData.bank_name) == -1){
            var extra_message = '\nNO_CONNECTION';
            if (['MANDIRI', 'BNI'].indexOf(cardData.bank_name) > -1) extra_message = '';
            switch_frame('source/smiley_down.png', 'Mohon Maaf, Layanan isi ulang kartu prabayar bank '+cardData.bank_name, ' tidak dapat digunakan. Mohon coba lagi dalam beberapa saat.'+extra_message, 'backToMain', false );
            return;
        }

        switch(cardData.bank_name){
        case 'MANDIRI':
            highDenomTopup = ready.emoney[0]
            midDenomTopup = ready.emoney[1]
            smallDenomTopup = ready.emoney[2]
            tinyDenomTopup = ready.emoney[3]
            break;
        case 'BNI':
            highDenomTopup = ready.tapcash[0]
            midDenomTopup = ready.tapcash[1]
            smallDenomTopup = ready.tapcash[2]
            tinyDenomTopup = ready.tapcash[3]
            break;
        case 'DKI':
            highDenomTopup = ready.jakcard[0]
            midDenomTopup = ready.jakcard[1]
            smallDenomTopup = ready.jakcard[2]
            tinyDenomTopup = ready.jakcard[3]
            break;
        case 'BCA':
            highDenomTopup = ready.flazz[0]
            midDenomTopup = ready.flazz[1]
            smallDenomTopup = ready.flazz[2]
            tinyDenomTopup = ready.flazz[3]
            break;
        case 'BRI':
            highDenomTopup = ready.brizzi[0]
            midDenomTopup = ready.brizzi[1]
            smallDenomTopup = ready.brizzi[2]
            tinyDenomTopup = ready.brizzi[3]
            break;
        }

        tiny_denom.buttonActive = (tinyDenomTopup!=undefined && parseInt(tinyDenomTopup) > 0);
        small_denom.buttonActive = (smallDenomTopup!=undefined && parseInt(smallDenomTopup) > 0);
        mid_denom.buttonActive = (midDenomTopup!=undefined && parseInt(midDenomTopup) > 0);
        high_denom.buttonActive = (highDenomTopup!=undefined && parseInt(highDenomTopup) > 0);

        // Existing Property Size Config
        rowDenomSpacing = (globalScreenType == '1') ? 50 : 30;
        buttonDenomWidth = 359;
        // Enhancement By tinyDenom button
        if (tiny_denom.buttonActive) {
            if (globalScreenType != '1'){
                rowDenomSpacing = 20;
                buttonDenomWidth = 289;
            }
        }
        popup_loading.close();
    }

    function check_denom_topup(){
        if (FUNC.empty(highDenomTopup) && FUNC.empty(midDenomTopup) && FUNC.empty(smallDenomTopup) && FUNC.empty(tinyDenomTopup)){
            return false;
        }
        return true;
    }

    function set_selected_denom(d){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('set_selected_denom', d, now);
        selectedDenom = d;

        totalPay = parseInt(selectedDenom) + parseInt(adminFee);

        // Add Payment Rules Validation
        do_validate_payment_rules(totalPay);

        press = '0';
        //No Payment Selection Needed If Only 1 Available
        if (activePayment.length==1){
            console.log('direct process_selected_payment', activePayment[0]);
            process_selected_payment(activePayment[0]);
            return;
        }
        if (!select_payment.visible){
            select_payment._qrMultiEnable = is_multi_qr_provider();
            select_payment.open();
            notice_topup_single_denom.visible = false;
            _SLOT.start_play_audio('choose_payment_press_proceed');
        }
    }

    function is_multi_qr_provider(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        if (activeQRISProvider.length == 0) return false;
        var singleQRISProvider = (activeQRISProvider.length > 0 && activeQRISProvider.length == 1);
        console.log('QRIS Provider', activeQRISProvider, !singleQRISProvider, now);
        return !singleQRISProvider;
    }

    function get_balance(text){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_balance', text, now);
        press = '0';
        if (VIEW_CONFIG.ui_simplify) global_frame.close();
        popup_loading.close();
        var result = text.split('|')[1];
        if (result == 'ERROR'){
            switch_frame('source/insert_card_new.png', 'Kartu Tidak Terdeteksi', 'Angkat dan tempelkan kembali kartu Anda pada reader', 'backToMain', false );
            _SLOT.start_play_audio('card_not_detected');
            // switch_frame('source/insert_card_new.png', 'Anda tidak meletakkan kartu', 'atau kartu Anda tidak dapat digunakan untuk Isi Ulang', 'backToMain', false );
            return;
        } else {
            var info = JSON.parse(result);
            var bankName = info.bank_name;
            var ableTopupCode = info.able_topup;

            //Put Extra Validation Here Before Go To Payment Layer
            if (selectedPayment !== undefined){
                if (cardData.card_no !== info.card_no){
                    switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Kartu Prabayar Tidak Sama, Silakan Ulangi Transaksi Isi Ulang Anda', 'backToMain', false );
                    return;
                } else {
                    do_set_confirm(selectedPayment);
                    return;
                }
            }

            cardBalance = parseInt(info.balance);
            cardData = {
                balance: info.balance,
                card_no: info.card_no,
                bank_type: info.bank_type,
                bank_name: info.bank_name,
                timestamp: info.timestamp,
            }
            //Define Data Card, Amount Button, Topup Availability
            if (ableTopupCode == "1008"){
                switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Kartu Prabayar '+bankName+' Anda Telah Kadaluarsa', 'backToMain', false );
                return;
            }
            if (ableTopupCode == "1031"){
                switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Kartu Prabayar Anda Tidak Dapat Dilakukan Isi Ulang Saat Ini', 'backToMain', false );
                return;
            }
            if (ableTopupCode == "DISABLED"){
                switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Layanan Isi Ulang Kartu Prabayar '+bankName+' Tidak Aktif Saat Ini', 'backToMain', false );
                return;
            }
            if (ableTopupCode == "BLOCKED"){
                switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Kartu Prabayar Anda Tidak Dapat Melakukan Isi Ulang Pada Mesin Ini', 'backToMain', false );
                return;
            }
            if (ableTopupCode == "9999"){
                switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Topup Online '+bankName+' Sedang Terkendala Saat ini', 'backToMain', false );
                return;
            }
            if (ableTopupCode != "0000"){
                switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Kartu ini melebihi batas topup bank '+bankName, 'backToMain', false );
                return;
            }
            parse_cardData(cardData);
        }
    }

    function parse_cardData(o){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('parse_cardData', now, JSON.stringify(o));
        var card_no = o.card_no;
        var last_balance = o.balance;
        var bank_name = o.bank_name;
        cardBalance = parseInt(last_balance);
        press = '0';
        shopType = 'topup';
        //Set Provider Based On Bank Name And Maximum Prepaid Balance
        if (bank_name=='MANDIRI'){
            provider = 'e-Money Mandiri';
            maxBalance = 2000000;

            // Enable Reader Dump in Mandiri Only
            _SLOT.start_enable_reader_dump();
        }
        if (bank_name=='BCA'){
            provider = 'Flazz BCA';
            maxBalance = 2000000;
            //Flazz BCA Only Allowed Topup With Cash in VM BCA Only
            if (VIEW_CONFIG.theme_name.toLowerCase() == 'bca') disable_qr_payment();
        }
        if (bank_name=='BNI') provider = 'Tapcash BNI';
        if (bank_name=='DKI') provider = 'JakCard DKI';
        if (bank_name=='BRI') provider = 'Brizzi BRI';
        mainVisible = true;
        _SLOT.start_play_audio('choose_topup_denom');
        if (topupData!=undefined) topup_readiness(topupData);
        else _SLOT.start_get_topup_readiness();
        popup_loading.close();
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
            repeat:true
            interval:1000
            running:true
            triggeredOnStart:true
            onTriggered:{
                abc.counter -= 1;
                notice_topup_single_denom.modeReverse = (abc.counter % 2 == 0) ? true : false;
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
        visible: !popup_loading.visible
        modeReverse: true

        MouseArea{
            anchors.fill: parent
            onClicked: {
                _SLOT.user_action_log('Press Back Button "TopUp Denom"');
                my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }))
            }
        }
    }

    CircleButton{
        id: next_button
        anchors.right: parent.right
        anchors.rightMargin: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'LANJUT'
//        visible: (selectedDenom > 0 && selectedPayment != undefined)
        visible: (selectedDenom > 0 && selectedPayment != undefined && !VIEW_CONFIG.ui_simplify)
        modeReverse: true
        blinkingMode: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press!='0') return;
                press = '1';
                _SLOT.user_action_log('Press "LANJUT"');
                disable_all_next_button();
                do_set_confirm('button_LANJUT_trigger');
            }
        }
    }

    //==============================================================
    //PUT MAIN COMPONENT HERE

    function disable_all_next_button(){
        console.log('Disable All "LANJUT" button');
        next_button.visible = false;
        next_button_global.visible = false;
        next_button_preload.visible = false;
    }

    function open_preload_notif(){
        preload_check_card.open();
    }

    function false_notif(closeMode, textSlave){
        if (closeMode==undefined) closeMode = 'backToMain';
        if (textSlave==undefined) textSlave = '';
        press = '0';
        switch_frame('source/smiley_down.png', 'Maaf Sementara Mesin Tidak Dapat Digunakan', textSlave, closeMode, false )
        return;
    }

    function switch_frame(imageSource, textMain, textSlave, closeMode, smallerText){
        frameWithButton = false;
        global_frame.closeMode = closeMode;
        global_frame.timerDuration = 5;
        if (closeMode.indexOf('|') > -1){
            var selectedCloseMode = closeMode.split('|')[0];
            var frame_timer = closeMode.split('|')[1];
            global_frame.timerDuration = parseInt(frame_timer);
            global_frame.closeMode = selectedCloseMode;
        }
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
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

    function exceed_balance(denom){
        if ((parseInt(cardData.balance) + parseInt(denom)) > maxBalance){
            console.log('[VALIDATE] BALANCE AFTER TOPUP VS MAX_BALANCE', (parseInt(cardData.balance) + parseInt(denom)), maxBalance);
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf Saldo Akan Melebihi Limit', 'Silakan Pilih Denom Yang Lebih Kecil', 'closeWindow', false )
            return true;
        } else if (parseInt(denom) <= adminFee) {
            console.log('[VALIDATE] DENOM VS ADMINFEE', denom, adminFee);
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf Biaya Admin Melebihi/Sama Dengan Nominal', 'Silakan Pilih Denom Yang Lebih Besar', 'closeWindow', false )
            return true;
        } else {
            return false;
        }
    }

    function minus_sam_balance(denom){
        var sam_balance = 0;
        var topup_amount = parseInt(denom) - parseInt(adminFee);
        switch(cardData.bank_name){
            case 'MANDIRI':
                if (VIEW_CONFIG.c2c_mode==1) topup_amount = parseInt(denom);
                sam_balance = parseInt(mandiriTopupWallet);
                break;
            case 'BNI':
                sam_balance = parseInt(bniTopupWallet);
                break;
            case 'BRI': case 'DKI': case 'BCA':
                sam_balance = parseInt(denom);
                break;
        }
        console.log('[VALIDATE] DEPOSIT BALANCE VS DENOM', sam_balance, topup_amount);
        if (topup_amount > sam_balance){
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf Saldo Mesin Tidak Mencukupi', 'Silakan Pilih Denom Yang Lebih Kecil', 'closeWindow', false )
            return true;
        } else {
            return false;
        }
    }

    function generateConfirm(rows, confirmation, closeMode, timer){
        press = '0';
        global_confirmation_frame.open(rows, confirmation, closeMode, timer);
    }


    MainTitle{
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 150 : (smallHeight) ? 30 : 120
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Pilih nominal topup ('+provider+')'
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"
        visible: mainVisible
    }


    Text {
        id: label_current_balance
        color: "white"
        text: "Saldo Anda sekarang"
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType=='1') ? 250 : 200
        anchors.left: parent.left
        anchors.leftMargin: (globalScreenType=='1') ? 350 : 150
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.family:"Ubuntu"
        font.pixelSize:(globalScreenType=='1') ? 50 : 40
        visible: mainVisible
    }

    Text {
        id: content_current_balance
        color: "white"
        text: (cardBalance==0) ? 'Rp 0' : 'Rp ' + FUNC.insert_dot(cardBalance.toString())
        anchors.right: parent.right
        anchors.rightMargin: (globalScreenType=='1') ? 350 : 150
        anchors.top: parent.top
        anchors.topMargin: label_current_balance.anchors.topMargin
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignRight
        font.family:"Ubuntu"
        font.pixelSize: (globalScreenType=='1') ? 50 : 40
        visible: mainVisible
    }


    function release_denom_selection(id){
        tiny_denom.do_release();
        small_denom.do_release();
        mid_denom.do_release();
        high_denom.do_release();
        id.set_active();
    }

    Row{
        id: denom_button
        height: 200
        layoutDirection: Qt.LeftToRight
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 350 : 320
        spacing: rowDenomSpacing
        visible: mainVisible
        SmallSimplyNumber{
            id: tiny_denom
            itemName: FUNC.insert_dot(FUNC.divide_thousand(tinyDenomTopup).toString())
            buttonActive: false
            buttonWidth: buttonDenomWidth
            MouseArea{
                anchors.fill: parent
                enabled: parent.buttonActive
                onClicked: {
                    if (exceed_balance(tinyDenomTopup)) return;
                    if (minus_sam_balance(tinyDenomTopup)) return;
                    if (press!='0') return;
                    press = '1';
                    _SLOT.user_action_log('Choose tinyDenom "'+tinyDenomTopup+'"');;
                    release_denom_selection(tiny_denom);
                    set_selected_denom(tinyDenomTopup);
                }
            }
        }
        SmallSimplyNumber{
            id: small_denom
            itemName: FUNC.insert_dot(FUNC.divide_thousand(smallDenomTopup).toString())
            buttonActive: false
            buttonWidth: buttonDenomWidth
            MouseArea{
                anchors.fill: parent
                enabled: parent.buttonActive
                onClicked: {
                    if (exceed_balance(smallDenomTopup)) return;
                    if (minus_sam_balance(smallDenomTopup)) return;
                    if (press!='0') return;
                    press = '1';
                    _SLOT.user_action_log('Choose smallDenom "'+smallDenomTopup+'"');;
                    release_denom_selection(small_denom);
                    set_selected_denom(smallDenomTopup);
                }
            }
        }
        SmallSimplyNumber{
            id: mid_denom
            itemName: FUNC.insert_dot(FUNC.divide_thousand(midDenomTopup).toString())
            buttonActive: false
            buttonWidth: buttonDenomWidth
            MouseArea{
                anchors.fill: parent
                enabled: parent.buttonActive
                onClicked: {
                    if (exceed_balance(midDenomTopup)) return;
                    if (minus_sam_balance(midDenomTopup)) return;
                    if (press!='0') return;
                    press = '1';
                    _SLOT.user_action_log('Choose midDenom "'+midDenomTopup+'"');
                    release_denom_selection(mid_denom);
                    set_selected_denom(midDenomTopup);
                }
            }
        }
        SmallSimplyNumber{
            id: high_denom
            itemName: FUNC.insert_dot(FUNC.divide_thousand(highDenomTopup).toString())
            buttonActive: false
            buttonWidth: buttonDenomWidth
            MouseArea{
                anchors.fill: parent
                enabled: parent.buttonActive
                onClicked: {
                    if (exceed_balance(highDenomTopup)) return;
                    if (minus_sam_balance(highDenomTopup)) return;
                    if (press!='0') return;
                    press = '1';
                    _SLOT.user_action_log('Choose highDenom "'+highDenomTopup+'"');
                    release_denom_selection(high_denom);
                    set_selected_denom(highDenomTopup);
                }
            }
        }
    }

    BoxTitle{
        id: notice_topup_single_denom
        width: 1300
        height: 120
        visible: (!select_payment.visible && VIEW_CONFIG.single_denom_trx.indexOf('topup') > -1)
        radius: 50
        fontSize: 30
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        title_text: 'MOHON PERHATIAN\nMESIN INI HANYA DAPAT MELAKUKAN TOPUP DENGAN 1 UANG KERTAS SESUAI DENGAN PILIHAN DI ATAS'
        boxColor: VIEW_CONFIG.frame_color
    }

    SelectPaymentInline{
        id: select_payment
        anchors.bottom: parent.bottom
        anchors.bottomMargin: (globalScreenType=='1') ? 125 : 100
        anchors.horizontalCenter: parent.horizontalCenter
        calledFrom: 'prepaid_topup_denom'
        listActivePayment: activePayment
        _qrMultiEnable: false
        totalEnable: activePayment.length
    }

    SelectPaymentQR{
        id: select_qr_provider
        anchors.bottom: parent.bottom
        anchors.bottomMargin: (globalScreenType=='1') ? 125 : 100
        anchors.horizontalCenter: parent.horizontalCenter
        visible: false
        calledFrom: 'prepaid_topup_denom'
        listActivePayment: activePayment
        _qrMultiEnable: false
        totalEnable: activePayment.length
    }


    //==============================================================


    StandardNotifView{
        id: standard_notif_view
//        withBackground: false
        modeReverse: true
        show_text: "Dear Customer"
        show_detail: "Please Ensure You have set Your plan correctly."
        z: 99
        MouseArea{
            enabled: !parent.buttonEnabled
            width: 180
            height: 90
            anchors.horizontalCenterOffset: 150
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 295
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: {
                _SLOT.user_action_log('Press Notif Button "Check Balance"');
                console.log('alternative button is pressed..!')
                popup_loading.open();
                _SLOT.start_check_card_balance();
                parent.visible = false;
                parent.buttonEnabled = true;
            }
        }
    }

//    SelectDenomTopupNotif{
//        id: select_denom
//        visible: (stepMode==1) ? true : false
//        _provider: provider
//        bigDenomAmount: 100
//        smallDenomAmount: 50
//        _adminFee: adminFee
//        tinyDenomAmount: 0
//        miniDenomAmount: (miniDenomActive) ? miniDenomValue : 0
//        withBackground: false
//    }


//    SelectPaymentPopupNotif{
//        id: select_payment
//        visible: isConfirm
//        calledFrom: 'prepaid_topup_denom'
//        _cashEnable: cashEnable
//        _cardEnable: cardEnable
//        _qrOvoEnable: qrOvoEnable
//        _qrDanaEnable: qrDanaEnable
//        _qrDuwitEnable: qrDuwitEnable
//        _qrLinkAjaEnable: qrLinkajaEnable
//        totalEnable: activePayment.length
//        z: 99
//    }

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
        CircleButton{
            id: cancel_button_global
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            visible: frameWithButton
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "BATAL"');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }

        CircleButton{
            id: next_button_global
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'LANJUT'
            modeReverse: true
            visible: frameWithButton
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    if (press!='0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "LANJUT"');
                    switch(modeButtonPopup){
                    case 'retrigger_bill':
                        _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString());
                        break;
//                    case 'do_topup':
//                        perform_do_topup();
//                        break;
                    case 'reprint':
                        _SLOT.start_reprint_global();
                        break;
                    case 'check_balance':
                        _SLOT.start_check_card_balance();
                        break;
                    }
                    popup_loading.open();
                }
            }
        }
    }

    PreloadCheckCard{
        id: preload_check_card
        CircleButton{
            id: cancel_button_preload
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "BATAL"');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }

        CircleButton{
            id: next_button_preload
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'LANJUT'
            modeReverse: true
            blinkingMode: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    preload_check_card.close();
                    if (press!='0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "LANJUT"');
                    popup_loading.open();
                    _SLOT.start_check_card_balance();
                }
            }
        }
    }

    GlobalConfirmationFrame{
        id: global_confirmation_frame
        calledFrom: 'prepaid_topup_denom'

    }




}

