import QtQuick 2.2
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC

Base{
    id: general_shop_card
    property int timer_value: VIEW_CONFIG.page_timer
    property var press: '0'
    property var cart: undefined
    property var shop_type: 'shop' // 'shop', 'topup', 'ppob'
    property var productData: undefined
    property var productCount: 0
    property var itemCount: 1
    property var itemMax: 10
    property var itemPrice: 0
    property var totalFee: 0
    property var adminFee: 1500
    property bool isConfirm: false
    property bool multipleEject: false
    property int productIdx: -1

    property var cdReadiness: undefined

    property variant availItems: []
    property variant activeQRISProvider: []

    property bool frameWithButton: false
    property var modeButtonPopup: 'check_balance';

    property var defaultItemPrice: 50000
    property int boxSize: 80
    property var selectedPayment: undefined

    property bool mainVisible: false

    property var cashboxFull
    property var activePayment: []
    property var paymentFeeSetting

    property bool onProgressTask

    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false

    idx_bg: 0
    imgPanel: 'source/beli_kartu.png'
    textPanel: 'Pembelian Kartu Prabayar'

    signal get_payment_method_signal(string str)
    signal set_confirmation(string str)


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            console.log('shop_type', shop_type);
            mainVisible = true;
            cdReadiness = undefined;
            onProgressTask = false;
            popup_loading.open();
            _SLOT.kiosk_get_cd_readiness();
            _SLOT.start_get_payments();
//            _SLOT.start_get_multiple_eject_status();
            if (cart != undefined) {
                console.log('cart', JSON.stringify(cart));
                adminFee = cart.admin_fee;
//                _provider.labelContent = cart.provider;
//                _nominal.labelContent =  'Rp. ' + FUNC.insert_dot(cart.value) + ',-';
//                _biaya_admin.labelContent =  'Rp. ' + FUNC.insert_dot(cart.admin_fee) + ',-';
//                small_notif.text = '*Biaya Admin sebesar Rp. 1.500,- Dikenakan Untuk Tiap Transaksi Isi Ulang.';
//                small_notif.visible = true;
            }
//            if (productData != undefined) {
//                console.log('productData', JSON.stringify(productData));
//                parseDataProduct(productData);
//            }
            abc.counter = timer_value;
            my_timer.start();
            press = '0';
            productIdx = -1;
            selectedPayment = undefined;
            isConfirm = false;
            availItems = [];
            activePayment = [];
            activeQRISProvider = [];
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop();
        }
    }

    Component.onCompleted:{
        set_confirmation.connect(do_set_confirm);
        get_payment_method_signal.connect(process_selected_payment);
        base.result_get_payment.connect(get_payments);
        base.result_balance_qprox.connect(get_balance);
        base.result_multiple_eject.connect(get_status_multiple);
        base.result_cd_readiness.connect(get_cd_readiness);
    }

    Component.onDestruction:{
        set_confirmation.disconnect(do_set_confirm);
        get_payment_method_signal.disconnect(process_selected_payment);
        base.result_get_payment.disconnect(get_payments);
        base.result_balance_qprox.disconnect(get_balance);
        base.result_multiple_eject.disconnect(get_status_multiple);
        base.result_cd_readiness.disconnect(get_cd_readiness);
    }


    function do_set_confirm(_mode){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('Confirmation Flagged By', _mode, now)
        global_confirmation_frame.no_button();
        popup_loading.close();
        press = '0';
        isConfirm = true;
    }

    function get_cd_readiness(c){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_cd_readiness', c, now);
        cdReadiness = JSON.parse(c);
        if (productData != undefined) {
            console.log('productData', JSON.stringify(productData));
            parseDataProduct(productData);
            _SLOT.start_play_audio('choose_prepaid_card');
        }
    }

    function get_payments(s){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_payments', s, now);
        var device = JSON.parse(s);
//        if (device.PRINTER_STATUS != 'OK'){
//            popup_loading.close();
//            switch_frame('source/smiley_down.png', 'Mohon Maaf, Struk Habis.', 'Saat Ini mesin tidak dapat mengeluarkan bukti transaksi.', 'backToMain|'+VIEW_CONFIG.failure_page_timer.toString(), false );
//            my_timer.stop();
//            return;
//        }
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
        if (device.QR_LINKAJA == 'AVAILABLE') {
            activeQRISProvider.push('linkaja');
            activePayment.push('linkaja');
        }
        if (device.QR_DANA == 'AVAILABLE') {
            activeQRISProvider.push('dana');
            activePayment.push('dana');
        }
        if (device.QR_DUWIT == 'AVAILABLE') {
            activeQRISProvider.push('duwit');
            activePayment.push('duwit');
        }
        if (device.QR_OVO == 'AVAILABLE') {
            activeQRISProvider.push('ovo');
            activePayment.push('ovo');
        }
        if (device.QR_SHOPEEPAY == 'AVAILABLE') {
            activeQRISProvider.push('shopeepay');
            activePayment.push('shopeepay');
        }
        if (device.QR_JAKONE == 'AVAILABLE') {
            activeQRISProvider.push('jakone');
            activePayment.push('jakone');
        }
        if (device.QR_GOPAY == 'AVAILABLE') {
            activeQRISProvider.push('gopay');
            activePayment.push('gopay');
        }
        if (device.QR_BCA == 'AVAILABLE') {
            activeQRISProvider.push('bca-qris');
            activePayment.push('bca-qris');
        }
        if (device.QR_BNI == 'AVAILABLE') {
            activeQRISProvider.push('bni-qris');
            activePayment.push('bni-qris');
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

    function is_multi_qr_provider(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        if (activeQRISProvider.length == 0) return false;
        var singleQRISProvider = (activeQRISProvider.length > 0 && activeQRISProvider.length == 1);
        console.log('QRIS Provider', activeQRISProvider, !singleQRISProvider, now);
        return !singleQRISProvider;
    }

    function get_payment_fee(p, d){
        if (p === undefined || paymentFeeSetting[p] === undefined) return 0;
        // Validate Fee Based On Transaction Type
        if (VIEW_CONFIG.include_fee_trx.indexOf('shop') === false) return 0;

        var fee = paymentFeeSetting[p];
        var init_price = d;
        if (parseInt(fee) < 1) fee = (fee * 100 * parseInt(init_price));
        return fee;
    }

    function process_selected_payment(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('process_selected_payment', p, now);
        if (onProgressTask){
            console.log('process_selected_payment', now, p, 'ALREADY_ON_PROGRESS_TASK');
            return;
        }
        onProgressTask = true;
        if (p=='MULTI_QR'){
            press = '0';
            if (activeQRISProvider.length == 1){
                p = activeQRISProvider[0];
            } else {
                select_payment.close();
                select_qr_provider.open();
                notice_card_purchase.visible = false;
                onProgressTask = false;
                return;
            }
        }
        if (p=='cash' && cashboxFull){
            console.log('Cashbox Full Detected', p);
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf, Pembayaran Tunai tidak dapat dilakukan saat ini.', ' Silakan Pilih Metode Pembayaran lain yang tersedia.', 'closeWindow|3', false );
            return;
        }
        selectedPayment = p;
        //Auto Payment Process Base on UI Simplification
        if (VIEW_CONFIG.ui_simplify) {
            var get_details = get_cart_details(p);
            // Add Service Charge
            get_details.service_charge = get_payment_fee(selectedPayment, get_details.init_total);
            my_layer.push(general_payment_process, {details: get_details});
        }
        //Must Press Flagging Here To Avoid Multi Trigger
        press = '0';
    }

    function get_status_multiple(m){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_status_multiple', m, now);
        if (m == 'AVAILABLE'){
            multipleEject = true;
        } else {
            itemCount = 1;
        }
    }

    function get_balance(text){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_balance', text, now);
    }

    function get_wording(i){
        if (i=='shop') return 'Pembelian Kartu';
        if (i=='topup') return 'TopUp Kartu';
        if (i=='ppob') return 'Pembayaran/Pembelian Item';
    }

    function adjust_count(t){
        if (t == 'plus'){
            if (itemCount == productData[productIdx].stock) return;
            if (itemCount == itemMax) return;
            itemCount++;
        }
        if (t == 'minus'){
            if (itemCount == 1) return;
            itemCount--;
        }
    }

    function parseDataProduct(products){
        var items = products;
        for(var x in items) {
            var item_name = items[x].name;
            var item_price = items[x].sell_price;
            var item_stock = items[x].stock;
            var item_desc = items[x].remarks;
            var item_status = items[x].status;
            var item_image = items[x].image;
            var item_id = items[x].pid;
            if (item_image=='') item_image = 'source/card/bni_tapcash_card.png';
            if (item_status==101){
                card_show_1.visible = parseInt(item_stock) > 0;
                card_show_1.itemName = item_name;
                card_show_1.itemImage = item_image;
                card_show_1.itemPrice = item_price.toString();
                card_show_1.itemStock =  parseInt(item_stock);
                card_show_1.outOfService = (cdReadiness.cd1 == 'N/A')
            }
            if (item_status==102){
                card_show_2.visible = parseInt(item_stock) > 0;
                card_show_2.itemName = item_name;
                card_show_2.itemImage = item_image;
                card_show_2.itemPrice = item_price.toString();
                card_show_2.itemStock =  parseInt(item_stock);
                card_show_2.outOfService = (cdReadiness.cd2 == 'N/A')
            }
            if (item_status==103){
                card_show_3.visible = parseInt(item_stock) > 0;
                card_show_3.itemName = item_name;
                card_show_3.itemImage = item_image;
                card_show_3.itemPrice = item_price.toString();
                card_show_3.itemStock =  parseInt(item_stock);
                card_show_3.outOfService = (cdReadiness.cd3 == 'N/A')
            }
            // TODO: Add 3 More Product Card (4,5,6)
            if (item_stock!='0') availItems.push(item_id);
        }

        popup_loading.close();
        if (availItems.length == 0){
            console.log('available_items', availItems.length);
            switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Tidak Ada Kartu Tersedia', 'backToMain', false )
            return;
        }
    }

    function defineProductIndex(products){
        var items = products;
        for(var x in items) {
            var item_stock = items[x].stock;
            var item_status = items[x].status;
            var item_price = items[x].sell_price;
            if (cdReadiness != undefined){
                if (item_status==101 && cdReadiness.cd1 == 'N/A') item_stock = '0';
                if (item_status==102 && cdReadiness.cd2 == 'N/A') item_stock = '0';
                if (item_status==103 && cdReadiness.cd3 == 'N/A') item_stock = '0';
                if (item_status==104 && cdReadiness.cd4 == 'N/A') item_stock = '0';
                if (item_status==105 && cdReadiness.cd5 == 'N/A') item_stock = '0';
                if (item_status==106 && cdReadiness.cd6 == 'N/A') item_stock = '0';
            }
            if (parseInt(item_stock) > 0) availItems.push({index: x, stock: parseInt(item_stock), price: parseInt(item_price)});
        }

        if (availItems.length == 0){
            switch_frame('source/smiley_down.png', 'Maaf Sementara Mesin Tidak Dapat Untuk', 'Melakukan Pembelian Kartu', 'backToMain', false )
            return;
        }

        var max = availItems.reduce(function (prev, current) {
            return (prev.stock > current.stock) ? prev : current
        });
//        productIdx = parseInt(max);
        productIdx = availItems.indexOf(max);
        defaultItemPrice = availItems[productIdx].price;
        console.log('defined_index', JSON.stringify(max), productIdx, defaultItemPrice);
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
                abc.counter -= 1;
                notice_card_purchase.modeReverse = (abc.counter % 2 == 0) ? true : false;
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
        visible: !popup_loading.visible && !global_frame.visible
        modeReverse: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
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
        visible: !popup_loading.visible && !global_frame.visible && itemCount > 0 && selectedPayment != undefined
        modeReverse: true
        blinkingMode: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press!='0') return;
                press = '1';
                _SLOT.user_action_log('Press "LANJUT"');
                var get_details = get_cart_details(selectedPayment);
                get_details.service_charge = get_payment_fee(selectedPayment, get_details.init_total);
                my_layer.push(general_payment_process, {details: get_details});
//                popup_loading.close();
//                var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
//                var unit_price = parseInt(productData[productIdx].sell_price);
//                var total_price = itemCount * unit_price;
//                var rows = [
//                    {label: 'Tanggal', content: now},
//                    {label: 'Produk', content: productData[productIdx].name},
//                    {label: 'Deskripsi', content: productData[productIdx].remarks},
//                    {label: 'Jumlah', content: itemCount.toString()},
//                    {label: 'Harga', content: FUNC.insert_dot(unit_price.toString())},
//                    {label: 'Total', content: FUNC.insert_dot(total_price.toString())},
//                ]
//                generateConfirm(rows, true);
            }
        }
    }

    function define_card(idx){
        //Validate Product Stock
        if (productData[idx].stock == 0) return;
        defaultItemPrice = parseInt(productData[idx].sell_price);
//        var selected_stock = parseInt(productData[idx].stock);
//        if (selected_stock < 4) count4.visible = false;
//        if (selected_stock < 3) count3.visible = false;
//        if (selected_stock < 2) count2.visible = false;
        switch(idx){
        case 0:
            if (card_show_1.outOfService) return;
            card_show_1.set_select();
            card_show_2.release_select();
            card_show_3.release_select();
            break;
        case 1:
            if (card_show_2.outOfService) return;
            card_show_1.release_select();
            card_show_2.set_select();
            card_show_3.release_select();
            break;
        case 2:
            if (card_show_3.outOfService) return;
            card_show_1.release_select();
            card_show_2.release_select();
            card_show_3.set_select();
            break;
        }
        // RECHECK: Validate Payment Rules
        do_validate_payment_rules(defaultItemPrice);

        //No Payment Selection Needed If Only 1 Available
        if (activePayment.length==1){
            console.log('direct process_selected_payment', activePayment[0]);
            process_selected_payment(activePayment[0]);
            return;
        }
        if (!select_payment.visible){
            select_payment._qrMultiEnable = is_multi_qr_provider();
            select_payment.open();
            notice_card_purchase.visible = false;
            _SLOT.start_play_audio('choose_payment_press_proceed');
        }
    }


    function do_validate_payment_rules(amount){
        // VIEW_CONFIG.payment_rules = 'cash:>:10000,qr:<:100000';
        if (amount == undefined) amount = 0;
        var existing_payment = activePayment;
        if (VIEW_CONFIG.payment_rules !== undefined){
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
        

    //==============================================================
    //PUT MAIN COMPONENT HERE

    MainTitle{
        id: main_title
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 150 : (smallHeight) ? 30 : 120
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Pilih Kartu Tersedia'
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"
        visible: !global_frame.visible && !popup_loading.visible && mainVisible

    }

    Row{
        id: rec_card_images
//        width: (availItems.length * 420)
        height: 400
        anchors.verticalCenterOffset: -100
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20
        visible: main_title.visible
        PrepaidProductItemLite{
            id: card_show_1
//            visible: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    if (parent.itemStock < 1) return;
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
                    productIdx = 0;
                    var selected_product = productData[productIdx];
                    console.log('select_product_1', now, productIdx, JSON.stringify(selected_product));
                    define_card(productIdx);
                }
            }
        }
        PrepaidProductItemLite{
            id: card_show_2
//            visible: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    if (parent.itemStock < 1) return;
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
                    productIdx = 1;
                    var selected_product = productData[productIdx];
                    console.log('select_product_2', now, productIdx, JSON.stringify(selected_product));
                    define_card(productIdx);
                }
            }
        }
        PrepaidProductItemLite{
            id: card_show_3
//            visible: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    if (parent.itemStock < 1) return;
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
                    productIdx = 2;
                    var selected_product = productData[productIdx];
                    console.log('select_product_3', now, productIdx, JSON.stringify(selected_product));
                    define_card(productIdx);
                }
            }
        }

    }


    BoxTitle{
        id: notice_card_purchase
        width: 1200
        height: 120
        visible: !select_payment.visible && (['transjakarta','bca'].indexOf(VIEW_CONFIG.theme_name.toLowerCase()) !== false ) && !smallHeight
        radius: 50
        fontSize: 30
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        title_text: (VIEW_CONFIG.theme_name.toLowerCase() == 'transjakarta') ? 
        'MOHON PERHATIAN\nPEMBELIAN KARTU MAKSIMAL 1 KARTU PER ORANG' : (VIEW_CONFIG.theme_name.toLowerCase() == 'bca') ? 
        'MOHON PERHATIAN\nPEMBELIAN KARTU MAKSIMAL 3 KARTU PER ORANG' : ""
        boxColor: VIEW_CONFIG.frame_color
    }


    function open_preload_notif(){
        press = '0';
        switch_frame('source/insert_money.png', 'Masukkan Uang Anda', '', 'closeWindow', false )
        return;
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

    function get_cart_details(channel){
        var details = {
            payment: channel,
            shop_type: shop_type,
            time: new Date().toLocaleTimeString(Qt.locale("id_ID"), "hh:mm:ss"),
            date: new Date().toLocaleDateString(Qt.locale("id_ID"), Locale.ShortFormat),
            epoch: (new Date().getTime() * 1000) + (Math.floor(Math.random() * (987 - 101)) + 101)
        }
        var unit_price = parseInt(productData[productIdx].sell_price);
        var total_price = itemCount * unit_price;
        details.qty = itemCount;
        details.value = total_price.toString();
        details.init_total = total_price;
        details.provider = productData[productIdx].name;
        details.admin_fee = '0';
        details.status = productData[productIdx].status;
        details.raw = productData[productIdx];
        return details;
    }

    function reset_button_color(){
        count1.modeReverse = true;
        count2.modeReverse = true;
        count3.modeReverse = true;
        count4.modeReverse = true;
        var selected_stock = parseInt(productData[productIdx].stock);
        if (selected_stock < 4) count4.visible = false;
        if (selected_stock < 3) count3.visible = false;
        if (selected_stock < 2) count2.visible = false;
        if (selected_stock == 1) {
            label_choose_qty.visible = false;
            itemCount = 1;
        }
    }

    function generateConfirm(rows, confirmation, closeMode, timer){
        press = '0';
        global_confirmation_frame.open(rows, confirmation, closeMode, timer);
    }

    SelectPaymentInline{
        id: select_payment
        anchors.bottom: parent.bottom
        anchors.bottomMargin: (smallHeight) ? 30 : 100
        anchors.horizontalCenter: parent.horizontalCenter
//        visible: (productIdx > -1)
//        visible: true
        calledFrom: 'general_shop_card'
        _qrMultiEnable: false
        listActivePayment: activePayment
        totalEnable: activePayment.length
    }

    SelectPaymentQR{
        id: select_qr_provider
        anchors.bottom: parent.bottom
        anchors.bottomMargin: (smallHeight) ? 30 : 100
        anchors.horizontalCenter: parent.horizontalCenter
        visible: false
//        visible: true
        calledFrom: 'general_shop_card'
        _qrMultiEnable: false
        listActivePayment: activePayment
        totalEnable: activePayment.length
    }


    Text {
        id: label_choose_qty
        color: "white"
        text: "Pilih jumlah kartu"
        anchors.top: parent.top
        anchors.topMargin: 700
        anchors.left: parent.left
        anchors.leftMargin: 250
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.family:"Ubuntu"
        font.pixelSize: 45
        visible: !global_frame.visible && !popup_loading.visible && mainVisible && multipleEject
    }

    Row{
        id: button_item
        width: 500
        height: 100
        anchors.top: parent.top
        anchors.topMargin: 775
        anchors.left: parent.left
        anchors.leftMargin: 250
        spacing: 20
        visible: label_choose_qty.visible

        BoxTitle{
            id: count1
            boxColor: '#1D294D'
            modeReverse: true
            radius: boxSize/2
            width: boxSize
            height: boxSize
            title_text: '1'
            fontBold: true
            fontSize: 40
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    itemCount = 1;
                    reset_button_color();
                    count1.modeReverse = false;
                }
            }
        }

        BoxTitle{
            id: count2
            boxColor: '#1D294D'
            modeReverse: true
            radius: boxSize/2
            width: boxSize
            height: boxSize
            title_text: '2'
            fontBold: true
            fontSize: 40
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    itemCount = 2;
                    reset_button_color();
                    count2.modeReverse = false;
                }
            }
        }

        BoxTitle{
            id: count3
            boxColor: '#1D294D'
            modeReverse: true
            radius: boxSize/2
            width: boxSize
            height: boxSize
            title_text: '3'
            fontBold: true
            fontSize: 40
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    itemCount = 3;
                    reset_button_color();
                    count3.modeReverse = false;
                }
            }
        }

        BoxTitle{
            id: count4
            boxColor: '#1D294D'
            modeReverse: true
            radius: boxSize/2
            width: boxSize
            height: boxSize
            title_text: '4'
            fontBold: true
            fontSize: 40
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    itemCount = 4;
                    reset_button_color();
                    count4.modeReverse = false;
                }
            }
        }

    }

    Text {
        id: label_total_qty
        color: "white"
        text: "Total Kartu"
        anchors.right: parent.right
        anchors.rightMargin: 350
        anchors.top: parent.top
        anchors.topMargin: 700
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        font.family:"Ubuntu"
        font.pixelSize: 45
        visible: label_choose_qty.visible
    }

//    Text {
//        id: label_total_pay
//        color: "white"
//        text: "Total Bayar"
//        anchors.right: parent.right
//        anchors.rightMargin: 350
//        anchors.top: parent.top
//        anchors.topMargin: 875
//        wrapMode: Text.WordWrap
//        verticalAlignment: Text.AlignVCenter
//        horizontalAlignment: Text.AlignLeft
//        font.family:"Ubuntu"
//        font.pixelSize: 45
//        visible: !global_frame.visible && !popup_loading.visible && mainVisible
//    }

    BoxTitle{
        id: content_item_count
        boxColor: '#1D294D'
        modeReverse: true
        anchors.top: parent.top
        anchors.topMargin: 775
        anchors.right: parent.right
        anchors.rightMargin: 500
        radius: boxSize/2
        width: boxSize
        height: boxSize
        title_text: itemCount
        fontBold: true
        fontSize: 40
        visible: label_choose_qty.visible

    }

    NextButton{
        id: reset_button
        width: boxSize*2
        height: boxSize
        radius: 20
        anchors.right: parent.right
        anchors.rightMargin: 300
        anchors.top: parent.top
        anchors.topMargin: 775
        button_text: 'RESET'
        modeReverse: true
        visible: label_choose_qty.visible
        MouseArea{
            anchors.fill: parent
            onClicked: {
                reset_button_color();
                itemCount = 1;
                count1.modeReverse = false;
            }
        }
    }

//    Text {
//        id: content_total_pay
//        color: "white"
//        text: 'Rp ' + FUNC.insert_dot((itemCount * defaultItemPrice).toString())
//        anchors.right: parent.right
//        anchors.rightMargin: 350
//        anchors.top: parent.top
//        anchors.topMargin: 850
//        wrapMode: Text.WordWrap
//        verticalAlignment: Text.AlignVCenter
//        horizontalAlignment: Text.AlignLeft
//        font.family:"Ubuntu"
//        font.pixelSize: 50
//        visible: !global_frame.visible && !popup_loading.visible && mainVisible
//    }

    //==============================================================


    StandardNotifView{
        id: standard_notif_view
        withBackground: false
        modeReverse: true
        show_text: "Dear Customer"
        show_detail: "Please Ensure You have set Your plan correctly."
        z: 99
    }

//    SelectPaymentPopupNotif{
//        id: select_payment
//        visible: isConfirm
//        calledFrom: 'general_shop_card'
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
                    default:
                        break;
                    }
                    popup_loading.open();
                }
            }
        }
    }

    PreloadShopCard{
        id: preload_shop_card
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
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "LANJUT"');
                    mainVisible = true;
                    preload_shop_card.close();
                }
            }
        }
    }

    GlobalConfirmationFrame{
        id: global_confirmation_frame
        calledFrom: 'general_shop_card'

    }






}

