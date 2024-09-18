import QtQuick 2.2
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN
//import "config.js" as CONF
import "base_function.js" as FUNC

Base{
    id: base_page

//     property var globalScreenType: '1'
//     height: (globalScreenType=='2') ? 1024 : 1080
//     width: (globalScreenType=='2') ? 1280 : 1920
    property var press: "0"
    property int tvc_timeout: parseInt(VIEW_CONFIG.tvc_waiting_time)
    property bool isMedia: true
    property bool kioskStatus: false
    property var productData: undefined
    property var productCountAll: 0
    property var productCount1: 0
    property var productCount2: 0
    property var productCount3: 0
    property var productCount4: 0
    property var productCount5: 0
    property var productCount6: 0
    property var mandiriTopupWallet: 0
    property bool mandiriTopupActive: false
    property bool bniTopupActive: false
    property var bniTopupWallet: 0
    property bool kalogButton: false
    property bool withSlider: true
    property var mandiri_update_schedule: VIEW_CONFIG.mandiri_update_schedule
    property var edc_settlement_schedule: VIEW_CONFIG.edc_settlement_schedule
    property var last_money_insert: 'N/A'

    property bool showCardStock: false

    property var selectedMenu: ''
    property bool uiSimplification: VIEW_CONFIG.ui_simplify
    property bool showingTNC: VIEW_CONFIG.show_tnc

    property bool spvButton: false
    property bool comboSaktiFeature: false
    property var randomPad: 200

    property var cardStockTreshold: 25

    property var lastTopupTime: 0
    property var lastShopTime: 0
    property var lastPPOBTime: 0

    property var cdReadiness: undefined

    width: globalWidth
    height: globalHeight
    isPanelActive: false

    Stack.onStatusChanged:{
        if(Stack.status == Stack.Activating){
            // _SLOT.start_idle_mode();
            console.log('OS & Theme Check L|W|S', IS_LINUX, IS_WINDOWS, uiSimplification, showingTNC);
            if (!VIEW_CONFIG.support_multimedia)  mediaOnPlaying = false;
            resetPopup();
            // Set Idle Mode Here
            _SLOT.user_action_log('[Homepage] Standby Mode');

            press = "0";
            resetMediaTimer();
            kalogButton = false;
            productCount1 = 0;
            productCount2 = 0;
            productCount3 = 0;
            productCount4 = 0;
            productCount5 = 0;
            productCount6 = 0;
            selectedMenu = '';
            if (globalBoxName !== ""){
                _SLOT.start_disable_reader_dump();
                _SLOT.start_get_kiosk_status();
                _SLOT.start_play_audio('homepage_greeting');
            }
        }
        if(Stack.status==Stack.Deactivating){
            show_tvc_loading.stop();
            preload_customer_info.close();
        }
    }

    Component.onCompleted: {
        base.result_get_gui_version.connect(get_gui_version);
        base.result_product_stock.connect(get_product_stock);
        base.result_generate_pdf.connect(get_pdf);
        base.result_general.connect(handle_general);
        base.result_kiosk_status.connect(get_kiosk_status);
        base.result_topup_readiness.connect(topup_readiness);
        base.result_auth_qprox.connect(ka_login_status);
        base.result_get_ppob_product.connect(get_ppob_product);
        base.result_cd_readiness.connect(get_cd_readiness);

    }

    Component.onDestruction: {
//        slider.close();
        base.result_get_gui_version.disconnect(get_gui_version);
        base.result_product_stock.connect(get_product_stock);
        base.result_generate_pdf.disconnect(get_pdf);
        base.result_general.disconnect(handle_general);
        base.result_kiosk_status.disconnect(get_kiosk_status);
        base.result_topup_readiness.disconnect(topup_readiness);
        base.result_auth_qprox.disconnect(ka_login_status);
        base.result_get_ppob_product.disconnect(get_ppob_product);
        base.result_cd_readiness.disconnect(get_cd_readiness);
    }

    function validate_operational_hours(t){
        // Not Full Day TRX
        console.log('full_day_trx', VIEW_CONFIG.full_day_trx, VIEW_CONFIG.full_day);
        if (!VIEW_CONFIG.full_day){
            // Check Operational Hours
            var hour_time = parseInt(Qt.formatDateTime(new Date(), "HHmm"));
            var open_time = (VIEW_CONFIG.open_hour==0) ? hour_time : VIEW_CONFIG.open_hour;
            var close_time = (VIEW_CONFIG.close_hour==0) ? hour_time : VIEW_CONFIG.close_hour;
            console.log('validate_operational_hours', t, hour_time, open_time, close_time);
            // If Not Force Full Day TRX, Do Operational Hour Validation
            if (VIEW_CONFIG.full_day_trx !== undefined){
                if (VIEW_CONFIG.full_day_trx.indexOf(t) === -1) {
                    if (hour_time < open_time || hour_time > close_time){
                        show_message_notification('Mohon Maaf|Tipe Transaksi Ini Tidak Dapat Dilakukan Di luar Jam Operational Mesin');
                        return false;
                    }
                } 
            }
        }
        return true;
    }

    function validate_duration_last_transaction(t){
        var epoch = new Date().getTime() * 1000;
        var next_transaction_time = 0;
        switch(t){
            case 'topup':
                if (VIEW_CONFIG.duration_topup_trx > 0 && last_topup_time > 0)
                    next_transaction_time = VIEW_CONFIG.duration_topup_trx + last_topup_time;
            break;
            case 'shop':
                if (VIEW_CONFIG.duration_shop_trx > 0 && last_shop_time > 0)
                    next_transaction_time = VIEW_CONFIG.duration_shop_trx + last_shop_time;
            break;
            case 'ppob':
                if (VIEW_CONFIG.duration_ppob_trx > 0 && last_ppob_time > 0)
                    next_transaction_time = VIEW_CONFIG.duration_ppob_trx + last_ppob_time;
            break;
        }
        if (epoch < next_transaction_time){
            show_message_notification('Mohon Maaf|Silakan Tunggu Beberapa Saat Untuk Melanjutkan Transaksi Ini');
            return false;
        }
        return true;
    }

    function get_cd_readiness(c){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_cd_readiness', c, now);
        cdReadiness = JSON.parse(c);
        _SLOT.kiosk_get_product_stock();
    }

    function resetPopup(){
        popup_loading.close();
        preload_whatasapp_voucher.close();
        preload_customer_info.close();
    }

    function get_ppob_product(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_ppob_product', now);
        press = '0';
        popup_loading.close();
        my_layer.push(ppob_category, {ppobData: p});
    }

    function resetMediaTimer(){
//        if (tvc_timeout > 300) return;
        if(isMedia){
            tvc_loading.counter = tvc_timeout;
            show_tvc_loading.start();
        }
    }

    function ka_login_status(t){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('ka_login_status', now, t);
        popup_loading.close()
        var result = t.split('|')[1]
        if (result == 'ERROR'){
            show_message_notification();
            kalogButton = false;
        } else if (result == 'SUCCESS'){
            show_message_notification('Selamat|Login KA Mandiri Berhasil');
            kalogin_notif_view._button_text = 'tutup';
            kalogButton = false;
        } else {
            show_message_notification('Mohon Maaf|Login KA Mandiri Gagal, Kode Error ['+result+'], Silakan Coba Lagi');
            kalogButton = true;
        }
    }

    function topup_readiness(t){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        console.log('topup_readiness', now, t);
        if (t=='TOPUP_READY|ERROR'){
            show_message_notification();
            return;
        }
        var tr = JSON.parse(t);
        mandiriTopupWallet = parseInt(tr.balance_mandiri);
        bniTopupWallet = parseInt(tr.balance_bni);

        var topup_active = [];
        if (tr.mandiri == 'AVAILABLE' || tr.mandiri == 'TEST_MODE') {
            if (mandiriTopupWallet > 0) {
                mandiriTopupActive = true;
                topup_active.push('MANDIRI');
            }
        }
        if (tr.bni == 'AVAILABLE') {
            if (bniTopupWallet > 0) {
                bniTopupActive = true;
                topup_active.push('BNI');
            }
        }

        var topupOnlineAvailable = false;
        box_connection.text = 'OFFLINE';
        box_connection.color = 'red';
        kioskStatus = false;
        
        if (tr.bri == 'AVAILABLE') {
            topupOnlineAvailable = true;
            topup_active.push('BRI');
        }
        if (tr.bca == 'AVAILABLE') {
            topupOnlineAvailable = true;
            topup_active.push('BCA');
        }
        if (tr.dki == 'AVAILABLE') {
            topupOnlineAvailable = true;
            topup_active.push('DKI');
        }
        if (topupOnlineAvailable) {
            kioskStatus = true;
            box_connection.color = 'green';
            box_connection.text = 'ONLINE';
        }

        topup_status_comp.statusMandiri = tr.mandiri;
        topup_status_comp.statusBni = tr.bni;
        topup_status_comp.statusBri = tr.bri;
        topup_status_comp.statusBca = tr.bca;
        topup_status_comp.statusDki = tr.dki;

        topup_saldo_button.visible = false;
        if (topup_active.length > 0 && globalBoxName !== "") topup_saldo_button.visible = true;

    }

    function get_product_stock(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_product_stock', now, p);
        productData = JSON.parse(p);
        if (productData.length > 0) {
            if (productData[0].status==101 && parseInt(productData[0].stock) > 0 && cdReadiness.cd1 !== 'N/A') productCount1 = parseInt(productData[0].stock);
            if (productData[0].status==102 && parseInt(productData[0].stock) > 0 && cdReadiness.cd2 !== 'N/A') productCount2 = parseInt(productData[0].stock);
            if (productData[0].status==103 && parseInt(productData[0].stock) > 0 && cdReadiness.cd3 !== 'N/A') productCount3 = parseInt(productData[0].stock);
        }
        if (productData.length > 1) {
            if (productData[1].status==101 && parseInt(productData[1].stock) > 0 && cdReadiness.cd1 !== 'N/A') productCount1 = parseInt(productData[1].stock);
            if (productData[1].status==102 && parseInt(productData[1].stock) > 0 && cdReadiness.cd2 !== 'N/A') productCount2 = parseInt(productData[1].stock);
            if (productData[1].status==103 && parseInt(productData[1].stock) > 0 && cdReadiness.cd3 !== 'N/A') productCount3 = parseInt(productData[1].stock);
        }
        if (productData.length > 2) {
            if (productData[2].status==101 && parseInt(productData[2].stock) > 0 && cdReadiness.cd1 !== 'N/A') productCount1 = parseInt(productData[2].stock);
            if (productData[2].status==102 && parseInt(productData[2].stock) > 0 && cdReadiness.cd2 !== 'N/A') productCount2 = parseInt(productData[2].stock);
            if (productData[2].status==103 && parseInt(productData[2].stock) > 0 && cdReadiness.cd3 !== 'N/A') productCount3 = parseInt(productData[2].stock);
        }
        //TODO: Add 3 More Card Dispenser Indicator
        productCountAll = productCount1 + productCount2 + productCount3;
        product_stock_status1.color = get_card_stock_color(productCount1);
        product_stock_status2.color = get_card_stock_color(productCount2);
        product_stock_status3.color = get_card_stock_color(productCount3);
//        console.log('product stock count : ', productCount1, productCount2, productCount3, productCountAll);
    }

    function get_cd_type(no){
        if (cdReadiness == undefined) return '';
        switch(no){
            case '1':
            return cdReadiness.cd1_type;
            case '2':
            return cdReadiness.cd2_type;
            case '3':
            return cdReadiness.cd3_type;
            case '4':
            return cdReadiness.cd4_type;
            case '5':
            return cdReadiness.cd5_type;
            case '6':
            return cdReadiness.cd6_type;
            default:
            return '';
        }
    }

    function get_kiosk_status(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log("get_kiosk_status", now, r);

        spvButton = false;

        var kiosk = JSON.parse(r);
        globalBoxName = kiosk.name;
        box_version.text = kiosk.version;
        box_tid.text = kiosk.tid;
        last_money_insert = kiosk.last_money_inserted;
        if (last_money_insert.indexOf('000') > -1) last_money_insert = FUNC.insert_dot(last_money_insert);

        //Handle Feature Button From Kiosk Status
        check_saldo_button.visible = (kiosk.feature.balance_check == 1)
        topup_saldo_button.visible = (kiosk.feature.top_up_balance == 1)
        buy_card_button.visible = (kiosk.feature.buy_card == 1)
        ppob_button.visible = (kiosk.feature.ppob == 1)
        search_trx_button.visible = (kiosk.feature.search_trx == 1)
        wa_voucher_button.visible = (kiosk.feature.whatsapp_voucher == 1)
        printerAvailable = (kiosk.printer_status == 'OK')

        lastTopupTime = kiosk.last_topup_time //time() * 1000
        lastShopTime = kiosk.last_shop_time
        lastPPOBTime = kiosk.last_ppob_time

        //Telkomsel Paket Murah Feature Handle
        comboSaktiFeature = (kiosk.feature.tsel_combo_sakti == 1)

        if (kiosk.status == "ONLINE" || kiosk.status == "AVAILABLE") {
            kioskStatus = true;
            box_connection.color = 'green';
            box_connection.text = kiosk.status;
        } else {
            box_connection.text = kiosk.status;
            box_connection.color = 'red';
            kioskStatus = false;
        }

        //Set WhatsApp Config Here
        if (VIEW_CONFIG.whatsapp_qr !== undefined) preload_whatasapp_voucher.imageSource = VIEW_CONFIG.whatsapp_qr;
        if (VIEW_CONFIG.whatsapp_no !== undefined && VIEW_CONFIG.whatsapp_no.length > 3){
            preload_whatasapp_voucher.whatsappNo = VIEW_CONFIG.whatsapp_no;
            preload_customer_info.whatsappNo = VIEW_CONFIG.whatsapp_no;
        }

        if (VIEW_CONFIG.parking_payment){
            parking_button.visible = true;
            ppob_button.visible = false;
        }

        // if (kiosk.refund_feature == '0') uiSimplification = true;
        // else uiSimplification = false;

        // Call CD Readiness & Product Stock
        _SLOT.kiosk_get_cd_readiness();

        maintenance_mode.visible = (kiosk.maintenance_mode == '1')

        main_title.show_text = 'Selamat Datang, Silakan Pilih Menu Berikut : ';
    }

    function not_authorized(){
        press = '0';
//        slider.close();
        false_notif('Mohon Maaf|Mesin Tidak Dapat Digunakan, Silakan Periksa Koneksi Internet');
    }

    function handle_general(result){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log("handle_general : ", now, result);
        if (result=='') return;
        if (result=='REBOOT'){
            switch_frame('source/loading_static.png', 'Mohon Tunggu Mesin Akan Dimuat Ulang', 'Dalam 30 Detik', 'closeWindow', false )
            return;
        }
        if (result.indexOf('STARTUP|') > -1){
            var message = result.split('|')[1];
            startup_process.show_text = message;
        }
        if (result=='MAINTENANCE_MODE_ON'){
            maintenance_mode.open();
            return;
        }
        if (result=='MAINTENANCE_MODE_OFF'){
            maintenance_mode.close();
            return;
        }
    }

    function get_pdf(pdf){
        console.log("get_pdf : ", pdf);
    }

    function get_gui_version(result){
        console.log("get_gui_version : ", result);
    }

    function false_notif(){
        press = '0';
        switch_frame('source/smiley_down.png', 'Maaf Sementara Mesin Tidak Dapat Digunakan', '', 'backToMain', false )
        return;
    }

    function show_message_notification(fm, sm){
        press = '0';
        var mainMessage = fm.split('|')[0];
        var slaveMessage = fm.split('|')[1];
        if (slaveMessage === undefined || slaveMessage.length < 1) slaveMessage = '';
        switch_frame('source/smiley_down.png', mainMessage, slaveMessage, 'closeWindow', false )
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
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.withTimer = true;
        global_frame.open();
    }


    MainTitle{
        id: main_title
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 280 : (smallHeight) ? 200 : 230
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: "Please Wait, Initiating Machine Setting..."
        visible: !popup_loading.visible
        size_: (globalScreenType == '1') ? 50 : 40
        color_: "white"

    }

    Row{
        id: row_button
        anchors.verticalCenterOffset: (VIEW_CONFIG.topup_status) ? 30 : 75
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: (globalScreenType == '1') ? 60 : 30
        visible: (!standard_notif_view.visible && !kalogin_notif_view.visible && !popup_loading.visible) ? true : false;

        AnimatedImage  {
            width: (globalScreenType == '1') ? 350 : 250
            height: (globalScreenType == '1') ? 350 : 250
            anchors.verticalCenter: parent.verticalCenter
            source: "source/sand-clock-animated-2.gif"
            fillMode: Image.PreserveAspectFit
            visible: (globalBoxName == "")
        }

        MasterButtonNew {
            id: check_saldo_button
            size: (globalScreenType == '1') ? 350 : 260
            x: 150
            anchors.verticalCenter: parent.verticalCenter
            img_: "source/cek_saldo.png"
            text_: qsTr("Cek/Update Saldo")
            text2_: qsTr("Check/Update Balance")
            modeReverse: false
            visible: false
            rounded: true
//            mode3d: 'gray'
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    if (press!="0" || maintenance_mode.visible) return;
                    press = "1";
                    _SLOT.user_action_log('Press "Cek Saldo"');
                    resetMediaTimer();
                    _SLOT.stop_idle_mode();
                    show_tvc_loading.stop();
                    selectedMenu = 'CHECK_BALANCE';
                    my_layer.push(check_balance, {uiSimplification: uiSimplification});
                }
            }
        }

        MasterButtonNew {
            id: topup_saldo_button
            size: (globalScreenType == '1') ? 350 : 260
            x: 150
            anchors.verticalCenter: parent.verticalCenter
            img_: "source/topup_kartu.png"
            text_: qsTr("Topup/Isi Saldo")
            text2_: qsTr("Topup Balance")
            modeReverse: false
            visible: false
            rounded: true
//            mode3d: 'gray'
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "TopUp Saldo"');
                    if (press!="0" || maintenance_mode.visible) return;
                    // Add Validation Operational Hours
                    if (!validate_operational_hours('topup')) return;
                    // Add Validation Duration Transaction
                    if (!validate_duration_last_transaction('topup')) return;
                    press = "1";
                    resetMediaTimer();
                    _SLOT.stop_idle_mode();
                    show_tvc_loading.stop();
                    selectedMenu = 'TOPUP_PREPAID';
                    if (showingTNC){
                        preload_customer_info.open(selectedMenu, VIEW_CONFIG.tnc_timer);
                        return;
                    }
                    my_layer.push(topup_prepaid_denom, {shopType: 'topup'});
                }
            }
        }

        MasterButtonNew {
            id: buy_card_button
            size: (globalScreenType == '1') ? 350 : 260
            x: 150
            anchors.verticalCenter: parent.verticalCenter
            img_: "source/beli_kartu.png"
            text_: qsTr("Beli Kartu")
            text2_: qsTr("Buy Card")
            modeReverse: false
            color_: (productCountAll > 0) ? 'white' : 'gray'
            opacity: 1
            visible: false
            rounded: true
//            mode3d: 'gray'
            MouseArea{
                enabled: (productCountAll > 0 && !maintenance_mode.visible) ? true : false
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "Beli Kartu"');
                    if (press!="0") return;
                    // Add Validation Operational Hours
                    if (!validate_operational_hours('shop')) return;
                    // Add Validation Duration Transaction
                    if (!validate_duration_last_transaction('shop')) return;
                    press = "1";
                    resetMediaTimer();
                    _SLOT.stop_idle_mode();
                    show_tvc_loading.stop();
                    selectedMenu = 'SHOP_PREPAID';
                    if (showingTNC){
                        preload_customer_info.open(selectedMenu, VIEW_CONFIG.tnc_timer);
                        return;
                    }
                    my_layer.push(general_shop_card, {productData: productData, shop_type: 'shop', productCount: productCountAll});
                }
            }
            Rectangle{
                id: oos_overlay
                y: 0
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 0
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 25
                anchors.horizontalCenter: parent.horizontalCenter
                opacity: 0.8
                visible: (productCountAll > 0) ? false : true
                Text {
                    id: text_oos
                    text: qsTr("HABIS")
                    anchors.fill: parent
                    font.pixelSize: 25
                    color: "#000000"
                    font.bold: false
                    font.family:"Ubuntu"
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        MasterButtonNew {
            id: ppob_button
            size: (globalScreenType == '1') ? 350 : 260
            x: 150
            anchors.verticalCenter: parent.verticalCenter
            img_: "source/shop_cart.png"
            text_: qsTr("Bayar/Beli")
            text2_: qsTr("Pay/Buy")
            modeReverse: false
            visible: false
            rounded: true
//            mode3d: 'gray'
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "Bayar/Beli"');
                    if (press!="0" || maintenance_mode.visible) return;
                    // Add Validation Operational Hours
                    if (!validate_operational_hours('ppob')) return;
                    // Add Validation Duration Transaction
                    if (!validate_duration_last_transaction('ppob')) return;
                    press = "1";
                    resetMediaTimer();
    //                    my_layer.push(topup_prepaid_denom, {shopType: 'topup'});
                    _SLOT.stop_idle_mode();
                    show_tvc_loading.stop();
                    selectedMenu = 'SHOP_PPOB';
                    if (showingTNC){
                        preload_customer_info.open(selectedMenu, VIEW_CONFIG.tnc_timer);
                        return;
                    }
                    popup_loading.open();
                    _SLOT.start_get_ppob_product();
                }
            }
        }

        MasterButtonNew {
            id: parking_button
            size: (globalScreenType == '1') ? 350 : 260
            x: 150
            anchors.verticalCenter: parent.verticalCenter
            img_: "source/parking.png"
            text_: qsTr("Bayar Parkir")
            text2_: qsTr("Pay Parking")
            modeReverse: false
            visible: false
            rounded: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "Bayar Parkir"');
                    if (press!="0" || maintenance_mode.visible) return;
                    press = "1";
                    resetMediaTimer();
                    _SLOT.stop_idle_mode();
                    show_tvc_loading.stop();
                    selectedMenu = 'PARKOUR';
                    // if (showingTNC){
                    //     preload_customer_info.open(selectedMenu, VIEW_CONFIG.tnc_timer);
                    //     return;
                    // }
                    // popup_loading.open();
                    var details = {
                        category: 'Parking',
                        operator: 'parkour',
                        description: 'Pembayaran Tiket Parking}',
                        product_id: 'PARKOUR',
                        rs_price: 1,
                        amount: 1,
                        product_channel: 'MDD',
                    }
                    console.log('Parking Payment: ', JSON.stringify(details));
                    my_layer.push(global_input_number, {selectedProduct: details, mode: 'PARKING'});
                }
            }
        }
    }

    TopupStatus{
        id:topup_status_comp
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: (smallHeight) ? 20 : 100
        visible: VIEW_CONFIG.topup_status && (globalBoxName !== "")
		width: globalWidth
    }

//    BoxTitle{
//        id: notice_single_denom
//        width: globalWidth
//        height: 40
//        visible: (VIEW_CONFIG.single_denom_trx.length > 0) && (globalBoxName !== "")
//        fontSize: 30
//        anchors.bottom: parent.bottom
//        anchors.bottomMargin: (smallHeight) ? 0 : 50
//        anchors.horizontalCenter: parent.horizontalCenter
//        title_text: 'METODE BAYAR TUNAI DENGAN SATU LEMBAR UANG'
//        boxColor: VIEW_CONFIG.frame_color
//    }

    MainTitle{
        id: startup_process
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 150
        show_text: ""
        visible: (globalBoxName == "")
        size_: 30
        color_: "yellow"
        setItalic: true
    }


    MouseArea {
        id: buttonSpvActivation
        x: 8
        y: 8
        width: 100
        height: 100
        onDoubleClicked: {
            console.log('SPV Button Activated');
            randomPad = FUNC.get_random(100, 600);
            spvButton = true;
        }
    }

    Rectangle{
        id: timer_tvc
        width: 10
        height: 10
        x:0
        y:0
        visible: false
        QtObject{
            id:tvc_loading
            property int counter
            Component.onCompleted:{
                tvc_loading.counter = tvc_timeout;
            }
        }
        Timer{
            id:show_tvc_loading
            interval:1000
            repeat:true
            running:false
            triggeredOnStart:true
            onTriggered:{
                if (globalBoxName == ""){
                    _SLOT.start_startup_task();
                    _SLOT.start_play_audio('welcome');
                }
                //Mandiri Auto Settlement Timer Trigger
                if (mandiri_update_schedule != undefined){
                    var hm = Qt.formatDateTime(new Date(), "HH:mm");
                    if (hm == mandiri_update_schedule && tvc_loading.counter%5==0) {
                        console.log('MANDIRI_UPDATE_SCHEDULE_IDLE', hm, mandiri_update_schedule);
                        _SLOT.start_mandiri_update_schedule();
                    }
                }
                //EDC Auto Settlement Timer Trigger
                if (edc_settlement_schedule != undefined){
                    var hm = Qt.formatDateTime(new Date(), "HH:mm");
                    if (hm == edc_settlement_schedule && tvc_loading.counter%5==0) {
                        console.log('EDC_SETTLEMENT_SCHEDULE_IDLE', hm, edc_settlement_schedule);
                        _SLOT.start_trigger_edc_settlement();
                    }
                }
                // Handle Simultane Check Topup Status Every 3 seconds
                if (tvc_loading.counter % VIEW_CONFIG.ping_interval==0) _SLOT.start_check_topup_readiness();

                //Handle Button Blinking
                tvc_loading.counter -= 1
                if (tvc_loading.counter%2==0){
                    search_trx_button.color = 'white';
                    wa_voucher_button.color = '#4FCE5D';
                    info_topup_single_denom.color = 'orange';
                    text_info_topup_single_denom.color = 'black';
                } else {
                    search_trx_button.color = 'orange';
                    wa_voucher_button.color = 'white';
                    info_topup_single_denom.color = 'black';
                    text_info_topup_single_denom.color = 'orange';
                }
                if(tvc_loading.counter == 0 && tvc_timeout < 300){
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
                    if (!mediaOnPlaying) {
                        if (VIEW_CONFIG.support_multimedia){
                            console.log("Starting TVC Player...", now);
                            my_layer.push(media_page, {mode: 'mediaPlayer',
                                            mandiri_update_schedule: mandiri_update_schedule,
                                            edc_settlement_schedule: edc_settlement_schedule
                                        });
                        } else {
                            my_layer.push(no_media_page, {mode: 'standbyMode',
                                            mandiri_update_schedule: mandiri_update_schedule,
                                            edc_settlement_schedule: edc_settlement_schedule
                                        });
                        }
                    }
                    tvc_loading.counter = tvc_timeout;
                    show_tvc_loading.restart();
                }
            }
        }


    }

    Rectangle{
        id: login_button_rec
        color: 'white'
        radius: 20
        anchors.top: parent.top
        anchors.topMargin: randomPad + 200
        anchors.left: parent.left
        anchors.leftMargin: -30
        width: 100
        height: 80
        visible: spvButton
        Image{
            id: login_button_img
            width: 80
            height: 90
            anchors.horizontalCenterOffset: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.horizontalCenter: parent.horizontalCenter
            scale: 0.75
            source: 'source/adult-male.png'
            fillMode: Image.PreserveAspectFit
        }

        MouseArea{
            anchors.fill: parent
            onDoubleClicked: {
                if (maintenance_mode.visible) return;
                _SLOT.user_action_log('Press "Admin" Button');
                console.log('Admin Button is Pressed..!');
                // _SLOT.set_tvc_player("STOP");
                _SLOT.stop_idle_mode();
                resetMediaTimer();
                my_layer.push(admin_login);
            }
        }
    }

    Rectangle{
        id: reset_printer_spooler
        color: 'white'
        radius: 20
        anchors.top: parent.top
        anchors.topMargin: randomPad + 300
        anchors.left: parent.left
        anchors.leftMargin: -30
        width: 100
        height: 80
        visible: spvButton
        Image{
            width: 80
            height: 90
            anchors.horizontalCenterOffset: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.horizontalCenter: parent.horizontalCenter
            scale: 0.75
            source: 'source/print_ticket.png'
            fillMode: Image.PreserveAspectFit
        }

        MouseArea{
            anchors.fill: parent
            onDoubleClicked: {
                if (maintenance_mode.visible) return;
                _SLOT.user_action_log('Press "Reset Printer" Button');
                console.log('Reset Printer is Pressed..!');
                resetMediaTimer();
                spvButton = false;
                _SLOT.start_reset_receipt_count('0');
                _SLOT.start_get_kiosk_status();
            }
        }
    }

    Rectangle{
        id: search_trx_button
        color: 'white'
        radius: 20
        anchors.right: parent.right
        anchors.rightMargin: (globalScreenType == '1') ? -15 : -5
        anchors.top: parent.top
        anchors.topMargin: (smallHeight) ? 150 : 200
        width: (globalScreenType == '1') ? 100 : 85
        height: (globalScreenType == '1') ? 300 : 225
        visible: false
        Text{
            text: 'CEK/LANJUT\nTRANSAKSI'
            font.pixelSize: (globalScreenType == '1') ? 30 : 20
            anchors.horizontalCenterOffset: -10
            anchors.bottom: parent.bottom
            anchors.bottomMargin: (globalScreenType == '1') ? 80 : 50
            anchors.horizontalCenter: parent.horizontalCenter
            font.family:"Ubuntu"
            font.bold: true
            rotation: 270
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
        Image{
            width: 80
            height: 90
            anchors.top: parent.top
            anchors.topMargin: 5
            anchors.horizontalCenterOffset: 0
            anchors.horizontalCenter: parent.horizontalCenter
            scale: 0.75
            source: "source/find.png"
            fillMode: Image.PreserveAspectFit
        }
        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press!="0" || maintenance_mode.visible) return;
                press = "1";
                _SLOT.user_action_log('Press "SEARCH_TRX" Button');
                console.log('Search Trx Button is Pressed..!');
                // _SLOT.set_tvc_player("STOP");
                _SLOT.stop_idle_mode();
                resetMediaTimer();
                my_layer.push(global_input_number, {mode: 'SEARCH_TRX'});
            }
        }
    }

    Rectangle{
        id: wa_voucher_button
        color: 'white'
        radius: 20
        anchors.bottom: parent.bottom
        anchors.bottomMargin: (smallHeight) ? 150 : 200
        anchors.right: parent.right
        anchors.rightMargin:  (globalScreenType == '1') ? -15 : -5
        width: (globalScreenType == '1') ? 100 : 85
        height: (globalScreenType == '1') ? 300 : 225
        visible: false
        Text{
            text: "WHATSAPP\nVOUCHER"
            font.pixelSize: (globalScreenType == '1') ? 28 : 20
            anchors.horizontalCenterOffset: -10
            anchors.bottom: parent.bottom
            anchors.bottomMargin: (globalScreenType == '1') ? 80 : 50
            anchors.horizontalCenter: parent.horizontalCenter
            font.family:"Ubuntu"
            font.bold: true
            rotation: 270
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
        Image{
            y: 0
            width: 100
            height: 100
            anchors.horizontalCenterOffset: 0
            anchors.horizontalCenter: parent.horizontalCenter
            scale: 0.75
            source: "source/whatsapp_transparent_black.png"
            fillMode: Image.PreserveAspectCrop
        }

        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press!="0" || maintenance_mode.visible) return;
                press = "1";
                _SLOT.user_action_log('Press "WA_VOUCHER" Button');
                console.log('WA Voucher Button is Pressed..!');
                // _SLOT.set_tvc_player("STOP");
                _SLOT.stop_idle_mode();
                resetMediaTimer();
//                my_layer.push(global_input_number, {mode: 'WA_VOUCHER'});
                preload_whatasapp_voucher.open()
            }
        }
    }

    Rectangle{
        id: info_last_money
        color: "#ffffff"
        anchors.left: parent.left
        anchors.leftMargin: 50
        opacity: 0.75
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        width: 150
        height: 30
        Row{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top
            spacing: 20
            Image{
                id: img_money
                height: parent.height
                source: 'source/cash black.png'
                fillMode: Image.PreserveAspectFit
                scale: .8
                verticalAlignment: Text.AlignVCenter
            }
            Text{
                id: last_money_text
                font.bold: true
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                color: 'black'
                text: last_money_insert
                font.pixelSize: 14
                font.family:"Ubuntu"
            }
        }

    }

    Rectangle{
        id: info_topup_single_denom
        visible: (VIEW_CONFIG.single_denom_trx.length > 0) && (globalBoxName !== "")
        color: "black"
        anchors.left: info_last_money.right
        opacity: 0.75
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        width: 450
        height: 30
        Row{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top
            spacing: 20
            Text{
                id: text_info_topup_single_denom
                font.bold: true
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                color: (info_topup_single_denom.color == 'orange') ? 'black' : 'orange'
                text: "TOPUP HANYA MENERIMA 1 LEMBAR UANG SESUAI DENOM"
                font.pixelSize: 14
                font.family:"Ubuntu"
            }
        }

    }

    Rectangle{
        id: machine_status_rec
        color: "#ffffff"
        anchors.right: parent.right
        anchors.rightMargin: 300
        opacity: 0.75
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        width: 300
        height: 30
        Row{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top
            spacing: 10
            Text{
                id: box_tid
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                color: "#000000"
                font.family:"Ubuntu"
            }
            Text{
                id: box_version
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                color: "#000000"
                font.family:"Ubuntu"
            }
            Image{
                id: img_kiosk
                height: parent.height
                source: 'source/icon/kiosk.png'
                fillMode: Image.PreserveAspectFit
                scale: .8
                verticalAlignment: Text.AlignVCenter
            }
            Text{
                id: box_connection
                font.bold: true
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                color: 'white'
                font.family:"Ubuntu"
            }
        }

    }

    Rectangle{
        id: product_stock_status1
        color: "silver"
        anchors.leftMargin: 0
        opacity: 0.75
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.left: machine_status_rec.right
        width: 75
        height: 30
        Row{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top
            spacing: 10
            Image{
                id: img_product
                height: parent.height
                source: 'source/icons-cards-2.png'
                fillMode: Image.PreserveAspectFit
                scale: .8
                verticalAlignment: Text.AlignVCenter
            }
            Text{
                id: product_count
                height: parent.height
                text: (showCardStock) ? productCount1 : get_cd_type('1')
                font.bold: true
                color: 'blue'
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Rectangle{
        id: product_stock_status2
        color: "silver"
        anchors.leftMargin: 0
        opacity: 0.75
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.left: product_stock_status1.right
        width: 75
        height: 30
        Row{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top
            spacing: 10
            Image{
                id: img_product2
                height: parent.height
                source: 'source/icons-cards-2.png'
                fillMode: Image.PreserveAspectFit
                scale: .8
                verticalAlignment: Text.AlignVCenter
            }
            Text{
                id: product_count2
                height: parent.height
                text: (showCardStock) ? productCount2 : get_cd_type('2')
                font.bold: true
                color: 'white'
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Rectangle{
        id: product_stock_status3
        color: "silver"
        anchors.leftMargin: 0
        opacity: 0.75
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.left: product_stock_status2.right
        width: 75
        height: 30
        Row{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top
            spacing: 10
            Image{
                id: img_product3
                height: parent.height
                source: 'source/icons-cards-2.png'
                fillMode: Image.PreserveAspectFit
                scale: .8
                verticalAlignment: Text.AlignVCenter
            }
            Text{
                id: product_count3
                height: parent.height
                text: (showCardStock) ? productCount3 : get_cd_type('3')
                font.bold: true
                color: 'white'
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    function get_card_stock_color(i){
        if (i==undefined) return 'silver';
        if (parseInt(i) > cardStockTreshold) return '#00f00f';
        // if (10 > parseInt(i) > 20) return '#fff000';
        if (parseInt(i) <= cardStockTreshold) return '#ff0000';
        return 'silver';
    }


    StandardNotifView{
        id: standard_notif_view
//        withBackground: false
        modeReverse: true
        show_text: "Dear Customer"
        show_detail: "Please Ensure You have set Your plan correctly."
        z: 99
    }

    StandardNotifView{
        id: kalogin_notif_view
        withBackground: false
        buttonEnabled: false
        modeReverse: true
        show_text: "Dear Customer"
        show_detail: "Please Ensure You have set Your plan correctly."
        z: 999
        MouseArea{
            id: kalog_button
            enabled: kalogButton
            x: 550; y: 666
            width: 180
            height: 90
            onClicked: {
                popup_loading.open();
                _SLOT.start_auth_ka_mandiri();
                parent.visible = false;
            }
        }
    }

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }

    PreloadComboSakti{
        id: preload_combo_sakti
        CircleButton{
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    preload_combo_sakti.close();
                    _SLOT.start_idle_mode();
                    _SLOT.start_get_kiosk_status();
                    press = "0";
                    resetMediaTimer();
                }
            }
        }

        CircleButton{
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
                    preload_combo_sakti.close();
                    _SLOT.user_action_log('Press "LANJUT" Button For Combo Sakti Product');
                    var details = {
                        category: 'Combo Sakti',
                        operator: 'Telkomsel',
                        description: 'Telkomsel Paket Murah',
                        product_id: 'OMNITSEL',
                        rs_price: 1,
                        amount: 1,
                        product_channel: 'DIVA',
                    }
                    console.log('Set Combo Sakti Product Into Input Layer: ', JSON.stringify(details));
                    my_layer.push(global_input_number, {selectedProduct: details, mode: 'PPOB'});

                }
            }
        }
    }

    PreloadWhatsappVoucher{
        id: preload_whatasapp_voucher
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
//                    _SLOT.user_action_log('Press "BATAL"');
                    preload_whatasapp_voucher.close();
                    _SLOT.start_idle_mode();
//                    _SLOT.kiosk_get_product_stock();
                    _SLOT.start_get_kiosk_status();
                    press = "0";
                    resetMediaTimer();
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
//                    _SLOT.user_action_log('Press "LANJUT" From WHATSAPP_INFO Frame');
                    preload_whatasapp_voucher.close()
                    my_layer.push(global_input_number, {mode: 'WA_VOUCHER'});

                }
            }
        }
    }

    PreloadCustomerInfo{
        id: preload_customer_info

//        CircleButton{
//            id: cancel_button_preload_info
//            anchors.left: parent.left
//            anchors.leftMargin: 30
//            anchors.bottom: parent.bottom
//            anchors.bottomMargin: 30
//            button_text: 'BATAL'
//            modeReverse: true
//            MouseArea{
//                anchors.fill: parent
//                onClicked: {
//                    preload_customer_info.close();
//                    selectedMenu = '';
//                    _SLOT.start_idle_mode();
////                    _SLOT.kiosk_get_product_stock();
//                    _SLOT.start_get_kiosk_status();
//                    press = "0";
//                    resetMediaTimer();
//                }
//            }
//        }

//        BoxTitle{
//            id: printer_paper_status_info
//            width: 900
//            height: 60
//            visible: false
//            modeReverse: true
//            radius: 30
//            fontSize: 25
//            border.width: 0
//            anchors.bottom: parent.bottom
//            anchors.bottomMargin: 15
//            anchors.horizontalCenter: parent.horizontalCenter
//            title_text: 'KERTAS HABIS, SAAT INI TRANSAKSI ANDA TIDAK MENGELUARKAN STRUK'
//            boxColor: VIEW_CONFIG.frame_color
//        }

//        CircleButton{
//            id: next_button_preload_info
//            anchors.right: parent.right
//            anchors.rightMargin: 30
//            anchors.bottom: parent.bottom
//            anchors.bottomMargin: 30
//            button_text: 'LANJUT'
//            modeReverse: true
//            blinkingMode: true
//            MouseArea{
//                anchors.fill: parent
//                onClicked: {
//                    switch(selectedMenu){
//                    case 'CHECK_BALANCE':
//                        my_layer.push(check_balance);
//                        break;
//                    case 'TOPUP_PREPAID':
//                        my_layer.push(topup_prepaid_denom, {shopType: 'topup'});
//                        break;
//                    case 'SHOP_PREPAID':
//                        my_layer.push(general_shop_card, {productData: productData, shop_type: 'shop', productCount: productCountAll});
//                        break;
//                    case 'SHOP_PPOB':
//                        popup_loading.open();
//                        _SLOT.start_get_ppob_product();
//                        break;
//                    }
//                }
//            }
//        }

    }

    MaintenanceMode{
        id: maintenance_mode
        z: 999999
    }

}
