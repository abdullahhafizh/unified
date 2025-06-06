import QtQuick 2.2
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
//import "config.js" as CONF

Base{
    id: global_input_number
//                property var globalScreenType: '1'
//                height: (globalScreenType=='2') ? 1024 : 1080
//                width: (globalScreenType=='2') ? 1280 : 1920
    mode_: "reverse"

    textPanel: 'Pilih Produk'
    property int timer_value: (VIEW_CONFIG.page_timer * 3)
    property int max_count: 24
    property int min_count: 10
    property var press: "0"
    property var textInput: ""
    property var mode: undefined
    property var selectedProduct
    property var wording_text: ''
    property bool checkMode: false
    property bool frameWithButton: false

    property var paymentFeeSetting
    property bool retryAbleTransaction: false

    property var cardData: undefined
    property int cardBalance: 0

    property bool isConfirm: false
    property var ppobMode
    property var ppobTagihanData
    property var ppobDetails
    property var vCollectionMode
    property var vCollectionData

    property var retryCategory
    property var retryDetails
    property int receivedPayment: 0
    property int pendingPayment: 0

    property bool transactionInProcess: false

    property var cashboxFull
    property var lastPPOBDataCheck

    property var adminFee: 1500

    property variant activeQRISProvider: []
    property var activePayment: []

    signal get_payment_method_signal(string str)
    signal set_confirmation(string str)

    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false
    
    property alias next_button: next_button


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
//            console.log('mode', mode, JSON.stringify(selectedProduct));
            define_wording();
            isConfirm = false;
            retryCategory = undefined;
            vCollectionMode = undefined;
            vCollectionData = undefined;
            lastPPOBDataCheck = undefined;
            retryAbleTransaction = false;
            transactionInProcess = false;
            receivedPayment = 0;
            pendingPayment = 0;
            cardData = undefined;
            cardBalance = 0;
            activeQRISProvider = [];
            press = '0';
            abc.counter = timer_value;
            my_timer.start();
            if (ppobDetails==undefined){
                ppobDetails = {
                    shop_type: 'ppob',
                    time: new Date().toLocaleTimeString(Qt.locale("id_ID"), "hh:mm:ss"),
                    date: new Date().toLocaleDateString(Qt.locale("id_ID"), Locale.ShortFormat),
                    epoch: (new Date().getTime() * 1000) + (Math.floor(Math.random() * (987 - 101)) + 101)
                }
            }

        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop();
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
        base.result_balance_qprox.connect(get_balance);
        base.result_ppob_check_customer.connect(get_ppob_check);
        base.result_scanner_read.connect(get_scanner_result);
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
        base.result_balance_qprox.disconnect(get_balance);
        base.result_ppob_check_customer.disconnect(get_ppob_check);
        base.result_scanner_read.disconnect(get_scanner_result);
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
                // console.log('[GLOBAL-INPUT]', abc.counter);
                abc.counter -= 1;
                notice_retry_able.modeReverse = (abc.counter % 2 == 0) ? true : false;
                if(abc.counter == 0){
                    my_timer.stop();
                    console.log('[GLOBAL-INPUT]', 'TIMER-TIMEOUT', 'BACK-TO-HOMEPAGE');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
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
                if (mode=='WA_VOUCHER'){
                    if (transactionInProcess){
                        console.log('[WARNING] Transaction In Process Not Allowed Cancellation');
                        return;
                    }
                }
                my_layer.pop();
            }
        }
    }

    function get_ppob_check(r){
        //Result from _SLOT.start_do_check_customer(payload, mode)
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_ppob_check', now, r);
        popup_loading.close();

        if (r=='CHECK_CUSTOMER|ERROR'){
            switch_frame('source/smiley_down.png', 'Gagal Memeriksa Nomor Anda', 'Pastikan nomor Anda benar dan coba lagi dalam beberapa saat.', 'backToMain', false );
            return;
        }

        var data = JSON.parse(r.replace('CHECK_CUSTOMER|', ''));
        if (data.customer === undefined){
            var message = data.response.message;
            switch_frame('source/smiley_down.png', 'Gagal Memeriksa Nomor Anda', message, 'backToMain', false );
            return;
        }
        var customer_name = 'OVO User';
        if (data.details.custName !== undefined) customer_name = data.details.custName;
        var product_name = selectedProduct.category.toUpperCase() + ' ' + selectedProduct.description;
        var topup_denom = parseInt(selectedProduct.rs_price) - parseInt(adminFee);
        var rows = [
            {label: 'Tanggal', content: now},
            {label: 'Produk', content: product_name},
            {label: 'Pelanggan', content: customer_name},
            {label: 'No Tujuan', content: data.customer},
//            {label: 'Jumlah', content: '1'},
            {label: 'Harga/Unit', content: FUNC.insert_dot(topup_denom.toString())},
            {label: 'Biaya Admin', content: FUNC.insert_dot(adminFee.toString())},
            {label: 'Total Harga', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
        ]
        if (selectedProduct.operator=='CASHIN OVO'){
            rows = [
            {label: 'Tanggal', content: now},
            {label: 'Produk', content: product_name},
            {label: 'Pelanggan', content: customer_name},
            {label: 'No Tujuan', content: data.customer},
//            {label: 'Jumlah', content: '1'},
            // {label: 'Harga/Unit', content: FUNC.insert_dot(topup_denom.toString())},
            // {label: 'Biaya Admin', content: FUNC.insert_dot(adminFee.toString())},
            {label: 'Total Harga', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
            {label: 'Deskripsi', content: 'Saldo OVO Cash Anda Akan Dipotong\nBiaya Admin Rp. '+FUNC.insert_dot(adminFee.toString())},
            ]
        }
        ppobMode = 'non-tagihan';
        generateConfirm(rows, true);
    }

    function get_scanner_result(text){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_scanner_result', text, now);
        var result = text.split('|')[1];
        if (mode=='PARKING'){
            if (result.indexOf('http') > -1 && result.indexOf('?') > -1){
                result = result.split('?')[1];
                var queryData = FUNC.parse_query_string(result);
                console.log('parse_query_string', result, JSON.stringify(queryData));
                result = queryData.p1;
            }
            result = FUNC.alphanum_only(result);
            console.log('final_scanner', result);
            textInput = result;
        }
    }

    function get_balance(text){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_balance', text, now);
        press = '0';
        popup_loading.close();
        var result = text.split('|')[1];
        if (result == 'ERROR'){
            switch_frame('source/insert_card_new.png', 'Anda tidak meletakkan kartu', 'atau kartu Anda tidak dapat digunakan untuk Isi Ulang', 'backToMain', false );
            return;
        } else {
            var info = JSON.parse(result);
            var bankName = info.bank_name;
            var ableTopupCode = info.able_topup;
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
            cardBalance = parseInt(info.balance);
            cardData = {
                balance: info.balance,
                card_no: info.card_no,
                bank_type: info.bank_type,
                bank_name: info.bank_name,
            }
            var provider = '';
            switch(info.bank_name){
            case 'MANDIRI':
                provider = 'e-Money Mandiri';
                break;
            case 'BNI':
                provider = 'Tapcash BNI';
                break;
            case 'BRI':
                provider = 'Brizzi BRI';
                break;
            case 'BCA':
                provider = 'Flazz BCA';
                break;
            case 'DKI':
                provider = 'JakCard DKI';
                break;
            }
            //Define Data Card, Amount Button, Topup Availability
            var prev_admin_fee = retryDetails.raw.admin_fee;
            var prev_topup_denom = retryDetails.raw.value;
            var prev_card_no = retryDetails.raw.card_no;
            // Add Check Validity Prev Card No Must Be Same With New Card
            if (prev_card_no !== cardData.card_no){
                console.log('Card No Mismatch', prev_card_no, cardData.card_no);
                switch_frame('source/insert_card_new.png', 'Nomor Kartu Berbeda', 'Silakan Gunakan Kartu Dengan Nomor '+prev_card_no, 'backToMain', false );
                return;
            }
            // Adjusting Promo Data if Exist
            if (retryDetails.promo !== undefined && retryDetails.promo !== null ){
                console.log('prev_promo', JSON.stringify(retryDetails.promo));
                console.log('Promo Data Found, Validating New Card Data VS Prev Card Data');
                console.log(cardData.bank_name, retryDetails.raw.bank_name);
                if (cardData.bank_name == retryDetails.raw.bank_name){
                    var trx_id = retryDetails.shop_type + retryDetails.epoch.toString();
                    console.log('Promo Code Re-Applied', trx_id, retryDetails.promo.code)
                    prev_admin_fee = retryDetails.admin_fee;
                    prev_topup_denom = retryDetails.denom;
                    retryDetails.denom = prev_topup_denom;
                    retryDetails.admin_fee = prev_admin_fee;
                    retryDetails.promo_code_active = true;
                    retryDetails.receive_discount = retryDetails.receive_discount;
                    // retryDetails.promo = retryDetails.promo;
                } else {
                    var init_denom = parseInt(prev_topup_denom) - parseInt(retryDetails.receive_discount);
                    // if (provider == 'e-Money Mandiri') retryDetails.value = prev_topup_denom;
                    prev_topup_denom = init_denom.toString();
                    prev_admin_fee = retryDetails.receive_discount;
                    retryDetails.denom = prev_topup_denom;
                    retryDetails.admin_fee = prev_admin_fee;
                    retryDetails.promo_code_active = false;
                    retryDetails.receive_discount = 0;
                    delete retryDetails.promo;
                }
                delete retryDetails.promo_data;
                // Do Manipulation Data Topup
                // {
                //     "raw": {
                //         "bank_type": "2",
                //         "bank_name": "BNI",
                //         "prev_balance": "106997",
                //         "value": "2000",
                //         "provider": "Tapcash BNI",
                //         "card_no": "7546885001469081",
                //         "admin_fee": 0
                //     },
                //     "admin_fee": 0,
                //     "denom": "2000",
                //     "payment": "bni-qris",
                //     "status": "1",
                //     "value": "2000",
                //     "final_balance": "107497",
                //     "epoch": 1632480451835161,
                //     "date": "24/09/21",
                //     "qty": 1,
                //     "shop_type": "topup",
                //     "receive_discount": 1500,
                //     "promo": {
                //         "mid": "f6f5ff767cc2dbcfac876aa863b20513",
                //         "tid": "17092001",
                //         "type": "TOPUP",
                //         "code": "FREEADMINTAPCASH",
                //         "name": "Topup Tapcash Free Admin",
                //         "priority": 1,
                //         "payment": "bni-qris",
                //         "bid": "2",
                //         "pid": null,
                //         "admin_fee": 1,
                //         "discount": 0,
                //         "max_discount": 0,
                //         "min_amount": 1000,
                //         "percent": 1,
                //         "quota": 10,
                //         "limit_usage": "day",
                //         "override_payment": null,
                //         "start_at": "2022-02-07 00:00:00",
                //         "end_at": "2022-03-07 23:55:59",
                //         "status": 1,
                //         "remarks": "Topup Tapcash Free Admin Fee With BNI QRIS",
                //         "created_at": "2021-07-31 17:00:00",
                //         "updated_at": "2022-02-08 11:25:55",
                //         "use_id": 60
                //     }
                // }
            }
            retryDetails.provider = provider;
            retryDetails.prev_card_no = prev_card_no;
            retryDetails.raw = {
                value: prev_topup_denom,
                provider: provider,
                admin_fee: prev_admin_fee,
                card_no: cardData.card_no,
                prev_balance: cardData.balance,
                bank_type: cardData.bank_type,
                bank_name: cardData.bank_name,
            }
            global_confirmation_frame.close();
            my_timer.stop();
            my_layer.push(retry_payment_process, {details: retryDetails, cardNo: cardData.card_no, pendingPayment: pendingPayment, receivedPayment: receivedPayment});
        }
    }

    function card_eject_result(r){
        if (vCollectionData!=undefined){
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
                if (vCollectionData!=undefined){
                    switch_frame('source/thumb_ok.png', 'Silakan Ambil Kartu Prabayar Anda', 'Terima Kasih', 'backToMain', false )
                    //NOTICE: Dont Change Below Reff No
                    var reff_no_voucher = new Date().getTime().toString() + '-' + vCollectionData.product.toString() + '-' + vCollectionData.slot.toString()
                    _SLOT.start_use_voucher(textInput, reff_no_voucher);
                }
                return;
            }
        }
    }

    function get_use_voucher(v){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_use_voucher', now, v);
        var res = v.split('|')[1];
        if (['ERROR', 'MISSING_VOUCHER_NUMBER', 'MISSING_REFF_NO'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Menggunakan Kode Ulang Anda', 'backToPrevious', res);
            return;
        }
    }

    function get_check_voucher(v){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        console.log('get_check_voucher', now, v);
        var res = v.split('|')[1];
        if (['ERROR', 'MISSING_VOUCHER_NUMBER', 'MISSING_PRODUCT_ID', 'EMPTY'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Kode Ulang Anda', 'backToPrevious', res);
            return;
        }
        console.log('get_check_voucher', now, res);
        popup_loading.close();
        var i = JSON.parse(v.replace('CHECK_VOUCHER|', ''));
        vCollectionData = i;
        vCollectionMode = i.mode;
        if (i.qty==0){
            false_notif('Kode Ulang Tersebut Sudah Pernah Digunakan', 'backToMain', '');
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
        popup_loading.close();
        ppobTagihanData = {
            customer: i.customer,
            value: i.total.toString(),
            admin_fee: i.admin_fee,
            msisdn: i.msisdn,
            provider: 'Tagihan ' + i.category,
            billing_check: i,
        }
        var detail_label = 'Pelanggan';
        var detail_content = i.customer;
        if (detail_content.length > 45) detail_content = detail_content.substring(0, 45) + '...';
        var biaya = i.ori_amount;
        var total = i.total;
        if (i.product_id == 'OMNITSEL'){
            detail_label = 'Produk';
            biaya = i.amount;
            total = parseInt(biaya) + parseInt(i.admin_fee);
        }
        var rows = [
            {label: 'Tanggal', content: now},
            {label: 'Tagihan', content: i.category.toUpperCase() + ' ' + i.msisdn},
            {label: detail_label, content: detail_content},
            {label: 'Biaya', content: FUNC.insert_dot(biaya.toString())},
            {label: 'Biaya Admin', content: FUNC.insert_dot(i.admin_fee.toString())},
            {label: 'Total', content: FUNC.insert_dot(total.toString())}
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
                console.log('Card WA Redeem Collection...');
                switch_frame('source/sand-clock-animated-2.gif', 'Memproses Kartu Baru Anda', 'Mohon Tunggu Beberapa Saat', 'closeWindow', true );
                var attempt = vCollectionData.slot.toString();
                var multiply = vCollectionData.qty.toString();
                var voucher = vCollectionData.voucher.toString();
                _SLOT.start_card_validate_redeem(attempt, multiply, voucher);
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

    function set_pending_trx_data(details, promo){
        if (details != undefined){
            retryDetails = details;
            if (promo !== undefined) retryDetails.promo_data = promo;
            delete retryDetails.payment_error;
            delete retryDetails.process_error;
            console.log('set_pending_trx_data', JSON.stringify(retryDetails));
        }
    }

    function parse_parking_inquiry_status(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('parse_parking_inquiry_status', now, r);
        popup_loading.close();
        var result = r.split('|')[1];
        if (result=='ERROR'){
            switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Terjadi Kesalahan Saat Memeriksa Tiket Parkir Anda. Silakan Coba Lagi.', 'backToMain', false );
            return;
        } 
        var data = JSON.parse(result);
        var rows = [
                        {label: 'Tanggal', content: now},
                        {label: 'No Tiket', content: data.ticket},
                        {label: 'Lokasi', content: data.location},
                        {label: 'Kendaraan', content: data.vehicletype + ' ' + data.platenumber},
                        {label: 'Waktu Masuk', content: data.intime},
                        {label: 'Durasi', content: data.duration_hour},
                        {label: 'Biaya', content: FUNC.insert_dot(data.tarif)},
                    ]
        // Assign to SelectedProduct
        selectedProduct.rs_price = parseInt(data.tarif);
        selectedProduct.amount = parseInt(data.tarif);
        selectedProduct.description = 'Parking Ticket';
        selectedProduct.ticket = data.ticket;
        selectedProduct.ticketstatus = data.ticketstatus;
        selectedProduct.intime = data.intime;
        selectedProduct.duration = data.duration;
        selectedProduct.duration_hour = data.duration_hour;
        selectedProduct.tarif = data.tarif;
        selectedProduct.vehicletype = data.vehicletype;
        selectedProduct.location = data.location;
        selectedProduct.paymentstatus = data.paymentstatus;
        selectedProduct.platenumber = data.platenumber;
        selectedProduct.address = data.address;
        selectedProduct.outtime = data.outtime;
        selectedProduct.timenow = data.timenow;
        selectedProduct.graceperiod = data.graceperiod;
        ppobMode = 'payment-parking';
        generateConfirm(rows, true);
    }

    function parse_ppob_inquiry_status(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('parse_ppob_detail_status', now, r);
        popup_loading.close();
        var result = r.split('|')[1];
        if (result=='ERROR'){
            switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Terjadi Kesalahan Saat Memeriksa Transaksi Anda. Silakan Coba Lagi.', 'backToMain', false );
            return;
        } 
        var res = r.split('|')[2];
        var data = JSON.parse(res);
        var product_name = selectedProduct.category.toUpperCase() + ' ' + selectedProduct.description;
        if (result == 'OK'){
            var rows = [
                            {label: 'Tanggal', content: now},
                            {label: 'Produk', content: product_name},
                            {label: 'No Tujuan', content: data.msisdn},
                            {label: 'Jumlah', content: '1'},
                            {label: 'Harga', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
                            {label: 'Total', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
                        ]
            ppobMode = 'non-tagihan';
            generateConfirm(rows, true);
            return;
        } else {
            product_name = selectedProduct.category.toUpperCase() + ' ' + selectedProduct.description;
            var msisdn = data.payload.msisdn;
            var limit_daily = data.suspect.limit;
            switch_frame('source/smiley_down.png', 'Mohon Maaf', 'Transaksi '+product_name+' Ke Nomor '+msisdn+' Maksimal ' + limit_daily + 'X Per Hari.', 'backToMain', false );
            return;
        }       
    }

    function parse_ppob_detail_status(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log('parse_ppob_detail_status', now, r);
        popup_loading.close();
        if (r == 'CHECK_TRX_STATUS|ERROR') return;
        var res = r.replace('CHECK_TRX_STATUS|', '')
        var data = JSON.parse(res);
        var new_status = data.status;
        for (var i=0;i < lastPPOBDataCheck.length; i++){
            var payment_method = 'CASH';
            if (lastPPOBDataCheck[i].label == 'Metode Bayar'){
                payment_method = lastPPOBDataCheck[i].content;
                lastPPOBDataCheck.splice(i,1);
            }
            if (lastPPOBDataCheck[i].label == 'Status'){
                lastPPOBDataCheck[i].content = data.status;
            }
            if (lastPPOBDataCheck[i].label == 'Uang Diterima'){
                lastPPOBDataCheck[i].content = payment_method + ' ' + lastPPOBDataCheck[i].content;
            }
        }
        if (data.details !== undefined){
            if (data.details.error.message !== undefined){
                lastPPOBDataCheck.push({
                                       label: 'Notes',
                                       content: data.details.error.message
                                       });
            }
        }

        generateConfirm(lastPPOBDataCheck, false, 'backToMain');
        // Reset PPOB Data Check
        lastPPOBDataCheck = undefined;
    }

    function get_trx_check_result(r){
        if (r.indexOf('CHECK_TRX_STATUS|') > -1){
            parse_ppob_detail_status(r);
            return;
        }
        if (r.indexOf('TRX_INQUIRY|') > -1){
            parse_ppob_inquiry_status(r);
            return;
        }
        if (r.indexOf('PARKING_INQUIRY|') > -1){
            parse_parking_inquiry_status(r);
            return;
        }
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        popup_loading.close();
        console.log('get_trx_check_result', now, r);
        var res = r.replace('TRX_CHECK|', '')
        if (['ERROR', 'MISSING_REFF_NO', 'TRX_NOT_FOUND'].indexOf(res) > -1){
            false_notif('Terjadi Kesalahan Saat Memeriksa Nomor Order Anda', 'backToPrevious', 'Data Transaksi Tidak Ditemukan');
            return;
        }
//        console.log('get_trx_check_result', now, res);
        var i = JSON.parse(res);
        var trx_name = '';
        var prev_card_no = '';
        var trx_id = FUNC.get_value(i.product_id);
        if (trx_id=='') trx_id = FUNC.get_value(i.remarks.shop_type) + FUNC.get_value(i.remarks.epoch.toString());
        retryCategory = i.category;
        var total_payment = i.amount.toString();

        switch (i.category){
            case 'PPOB':
                trx_name = i.category + ' ' + i.remarks.product_id;
            break;
            case 'TOPUP':
                trx_name = i.category + ' ' + FUNC.get_value(i.remarks.raw.provider) + ' ' + FUNC.get_value(i.remarks.raw.card_no);
                prev_card_no = i.remarks.raw.card_no;
            break;
            case 'SHOP':
                trx_name = i.category + ' ' + i.remarks.provider;
                total_payment = i.remarks.value.toString();
            break;
        }

        if (i.remarks.payment_received==undefined) i.remarks.payment_received = i.receipt_amount;
        var amount = FUNC.insert_dot(i.remarks.payment_received.toString());
        // if (i.status!='PAID' || i.status=='FAILED' || i.status=='PENDING') amount = FUNC.insert_dot(i.remarks.payment_received.toString());
        // Build Remarks Object : shop_type, epoch, product_id, raw.provider, raw.card_no, provider, value, payment_received
        if (i.payment_method=='MEI' || i.payment_method=='cash') i.payment_method = "CASH";
        var rows = [
                    {label: 'No Transaksi', content: trx_id},
                    {label: 'Tanggal', content: FUNC.get_value(i.date)},
                    {label: 'Jenis Transaksi', content: trx_name},
                    {label: 'Total Bayar', content: FUNC.insert_dot(total_payment)},
                    {label: 'Metode Bayar', content: i.payment_method.toUpperCase()},
                    {label: 'Uang Diterima', content: amount},
                    {label: 'Status', content: i.status}
                ]
        if (i.remarks.product_channel !== undefined){
            if (i.remarks.product_channel == 'MDD'){
                rows = [
                    {label: 'No Transaksi', content: trx_id},
                    {label: 'Tanggal', content: FUNC.get_value(i.date)},
                    {label: 'Jenis Transaksi', content: trx_name},
                    {label: 'Total Bayar', content: amount},
                    {label: 'Metode Bayar', content: i.payment_method.toUpperCase()},
                    {label: 'Uang Diterima', content: amount},
                    {label: 'Status', content: i.status}
                ]
                if (i.remarks.operator == 'CASHIN OVO'){
                    popup_loading.open('Memeriksa Data Transaksi...');
                    var payload = {
                                    reff_no: trx_id,
                                    operator: i.remarks.operator,
                                }
                    _SLOT.start_check_detail_trx_status(JSON.stringify(payload), i.remarks.operator);
                    lastPPOBDataCheck = rows;
                    return;
                }
            }
        }
        if (i.status == 'PAID' && i.category == 'PPOB' ){
            if (i.remarks.product_category == 'Listrik'){
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
            } else {
                rows = [
                            {label: 'No Transaksi', content: trx_id},
                            {label: 'Tanggal', content: FUNC.get_value(i.date)},
                            {label: 'Jenis Transaksi', content: trx_name},
                            {label: 'Total Bayar', content: FUNC.insert_dot(total_payment)},
                            {label: 'Metode Bayar', content: i.payment_method.toUpperCase()},
                            {label: 'Status', content: i.status}
                        ]
            }
            
        }
        generateConfirm(rows, false, 'backToMain');
        // Set Value For Retry Transaction If Status Pending
        if (i.status=='PENDING') {
            receivedPayment = parseInt(i.receipt_amount);
            pendingPayment = parseInt(i.remarks.value) - receivedPayment;
            set_pending_trx_data(i.remarks, i.promo_data);
            if (i.retry_able == 1) {
                retryAbleTransaction = true;
                if (i.category == 'TOPUP'){
                    notice_retry_able.title_text = 'TRANSAKSI ANDA DAPAT DILANJUTKAN DENGAN KARTU YANG SAMA\nSILAKAN TEKAN TOMBOL LANJUT'
                }
                global_confirmation_frame.no_button();
            }
        }
        if (i.show_info_cs !== undefined && i.show_info_cs === 1){
            notice_retry_able.title_text = 'SILAKAN AKSES LAYANAN PELANGGAN https://bit.ly/CSMultidaya';
            if (VIEW_CONFIG.theme_name.toLowerCase() == 'bca') notice_retry_able.title_text = 'SILAKAN HUBUNGI CS DI HALO BCA';
            notice_retry_able.visible = true;
        }

        // ---
    }

    function generateConfirm(rows, confirmation, closeMode, timer){
        press = '0';
        global_confirmation_frame.open(rows, confirmation, closeMode, timer);
    }

    function define_wording(){
        // if (mode=='PARKING'){
        //     wording_text = 'Scan Tiket Parkir Anda Pada Reader';
        //     min_count = 12;
        //     return;
        // }
        if (mode=='WA_VOUCHER'){
            wording_text = 'Masukkan Kode Voucher (VCODE) Dari WhatsApp Anda';
            min_count = 8;
            _SLOT.start_play_audio('please_input_voucher_code');
            return;
        }
        if (mode=='SEARCH_TRX'){
            wording_text = 'Masukkan 9 Digit Kode Ulang Transaksi Anda';
            min_count = 6;
            _SLOT.start_play_audio('please_input_retry_code');
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
            case 'parking':
                _SLOT.start_simple_read_scanner();
                wording_text = 'Scan Tiket Parkir Anda Pada Reader';
                // checkMode = true;
                min_count = 12;
            break;
            case 'combo sakti':
                wording_text = 'Masukkan Kode Bayar Telkomsel Paket Murah';
                checkMode = true;
                min_count = 9;
            break;
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
                } else if (['TCASH LINKAJA', 'OVO', 'CASHIN OVO', 'CASHIN LINKAJA', 'DANA', 'BUKADANA', 'TIXID'].indexOf(operator) > -1) {
                    operator = operator.split(' ')
                    if (operator.length == 1) var selectedOperator = operator[0];
                    else selectedOperator = operator[1];
                    console.log('selected_operator', selectedOperator);
                    wording_text = 'Masukkan Nomor HP Terdaftar Pada Aplikasi ' + selectedOperator;
                    min_count = 15;
                    _SLOT.start_play_audio('please_input_register_no_press_proceed');
                } else {
                    wording_text = 'Masukkan Nomor Kartu Prabayar Anda';
                    min_count = 15;
                    _SLOT.start_play_audio('please_input_register_no_press_proceed');
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
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('process_selected_payment', now, channel);
        if (channel=='MULTI_QR'){
            press = '0';
            if (activeQRISProvider.length > 1){
                select_payment.close();
                select_qr_provider.open();
                return;
            }
            channel = activeQRISProvider[0];
        }
        if (channel=='cash' && cashboxFull){
            console.log('Cashbox Full Detected', channel);
            press = '0';
            switch_frame('source/smiley_down.png', 'Mohon Maaf, Pembayaran Tunai tidak dapat dilakukan saat ini.', ' Silakan Pilih Metode Pembayaran lain yang tersedia.', 'closeWindow|3', false );
            return;
        }
        var details = ppobDetails;
        details.payment = channel;
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
        details.product_channel = selectedProduct.product_channel;

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
            if (details.product_channel == 'MDD'){
                details.provider = selectedProduct.description + ' (Admin 1500)';
                details.value = (parseInt(selectedProduct.rs_price) - 1500).toString();
                details.admin_fee = '1500';
            }
        } else if (ppobMode=='payment-parking'){
            details.shop_type = selectedProduct.operator;
            details.customer = textInput;
            details.value = selectedProduct.rs_price.toString();
            details.admin_fee = '0';
            details.msisdn = textInput;
            details.provider = selectedProduct.category;
        }

        details.init_total = details.qty * parseInt(details.value);
//        _SLOT.python_dump(JSON.stringify(details));
        my_timer.stop();
        // Add Service Charge Based On Payment
        details.service_charge = get_payment_fee(channel, details.init_total);
        my_layer.push(general_payment_process, {details: details});
    }

    function get_payment_fee(p, d){
        if (p === undefined || paymentFeeSetting[p] === undefined) return 0;
        // Validate Fee Based On Transaction Type
        if (VIEW_CONFIG.include_fee_trx.indexOf('ppob') === false) return 0;

        var fee = paymentFeeSetting[p];
        var init_price = d;
        if (parseInt(fee) < 1) fee = (fee * 100 * parseInt(init_price));
        return fee;
    }

    function get_payments(s){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_payments', now, s);
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
        if (device.QR_LINKAJA == 'AVAILABLE') {
            activeQRISProvider.push('linkaja')
            activePayment.push('linkaja');
        }
        if (device.QR_DANA == 'AVAILABLE') {
            activeQRISProvider.push('dana')
            activePayment.push('dana');
        }
        if (device.QR_DUWIT == 'AVAILABLE') {
            activeQRISProvider.push('duwit')
            activePayment.push('duwit');
        }
        if (device.QR_OVO == 'AVAILABLE') {
            activeQRISProvider.push('ovo')
            activePayment.push('ovo');
        }
        if (device.QR_SHOPEEPAY == 'AVAILABLE') {
            activeQRISProvider.push('shopeepay')
            activePayment.push('shopeepay');
        }
        if (device.QR_JAKONE == 'AVAILABLE') {
            activeQRISProvider.push('jakone')
            activePayment.push('jakone');
        }
        if (device.QR_GOPAY == 'AVAILABLE') {
            activeQRISProvider.push('gopay');
            activePayment.push('gopay');
        }
        if (device.QR_BCA == 'AVAILABLE') {
            activeQRISProvider.push('bca-qris')
            activePayment.push('bca-qris');
        }
        if (device.QR_BNI == 'AVAILABLE') {
            activeQRISProvider.push('bni-qris')
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

        if (selectedProduct !== undefined && selectedProduct.category.toLowerCase() == 'parking'){
            // Remove Cash Payment For Parking Payment
            console.log('Active Category', selectedProduct.category);
            activePayment = activeQRISProvider;
            console.log('Active Payment Channel', JSON.stringify(activePayment));
        }
        //================================
//        isConfirm = true;

    }

    //==============================================================
    //PUT MAIN COMPONENT HERE

    MainTitle{
        anchors.top: parent.top
        anchors.topMargin: (smallHeight) ? 30 : 200
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: wording_text
        visible: !popup_loading.visible
        size_: (smallHeight) ? 40 : 50
        color_: "white"

    }


    TextRectangle{
        id: textRectangle
        width: 650
        height: 110
        color: "white"
        radius: 0
        anchors.top: parent.top
        anchors.topMargin: (smallHeight) ? 100 : 325
        border.color: VIEW_CONFIG.text_color
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
        color: "black"
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
            virtual_keyboard.strButtonClick.connect(typeIn);
            virtual_keyboard.funcButtonClicked.connect(functionIn);
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
            abc.counter = timer_value;
            my_timer.restart();
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
                var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
                console.log('button "LANJUT" is pressed..!');
                if(press != "0") return;
                press = "1"
                _SLOT.user_action_log('press "LANJUT" In Input Number Page');
                transactionInProcess = true;
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
                        if (selectedProduct.operator=='CASHIN OVO'){
                            console.log('Customer Check', selectedProduct.operator, textInput);
                            var payload = {
                                msisdn: textInput,
                                amount: selectedProduct.rs_price.toString(),
                                reff_no: ppobDetails.shop_type + ppobDetails.epoch.toString(),
                                operator: selectedProduct.operator,
                            }
                            _SLOT.start_do_check_customer(JSON.stringify(payload), selectedProduct.operator);
                            popup_loading.open('Memeriksa Nomor Anda...')
                            return;
                        } else {
                            // 'product_id' => 'required',
                            // 'product_category' => 'required',
                            // 'operator' => 'required',
                            // 'msisdn' => 'required',
                            // 'amount' => 'required:numeric',
                            console.log('Transaction Check', selectedProduct.operator, textInput);
                            var payload = {
                                msisdn: textInput,
                                amount: selectedProduct.rs_price.toString(),
                                reff_no: ppobDetails.shop_type + ppobDetails.epoch.toString(),
                                operator: selectedProduct.operator,
                                product_id: selectedProduct.product_id,
                                product_category: selectedProduct.category,
                            }
                            _SLOT.start_do_inquiry_trx(JSON.stringify(payload));
                            popup_loading.open('Memeriksa Transaksi Anda...')
                            return;
                        }
                        // var product_name = selectedProduct.category.toUpperCase() + ' ' + selectedProduct.description;
                        // var rows = [
                        //     {label: 'Tanggal', content: now},
                        //     {label: 'Produk', content: product_name},
                        //     {label: 'No Tujuan', content: textInput},
                        //     {label: 'Jumlah', content: '1'},
                        //     {label: 'Harga', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
                        //     {label: 'Total', content: FUNC.insert_dot(selectedProduct.rs_price.toString())},
                        // ]
                        // ppobMode = 'non-tagihan';
                        // generateConfirm(rows, true);
                        // return;
                    }
                case 'PARKING':
                    console.log('Checking Transaction Number : ', now, textInput);
                    popup_loading.open('Memeriksa Tiket Parkir Anda...');
                    _SLOT.start_do_parking_inquiry(textInput);
                    return
                case 'SEARCH_TRX':
                    console.log('Checking Transaction Number : ', now, textInput);
                    popup_loading.open('Memeriksa Transaksi Anda...');
                    _SLOT.start_check_status_trx(textInput);
                    return
                case 'WA_VOUCHER':
                    console.log('Checking WA Invoice Number : ', now, textInput);
                    popup_loading.open('Memeriksa Voucher Code (VCODE) Anda...');
                    _SLOT.start_check_voucher(textInput);
                    return;
                default:
                    false_notif('No Handle Set For This Action', 'backToMain');
                    return
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

    function exit_with_message(second){
        popup_loading.open();
        popup_loading.textMain = 'Membatalkan Transaksi Ulang';
        popup_loading.textSlave = 'Anda Masih Dapat Melanjutkan Transaksi Dari Voucher Tertera';
        delay(second*1000, function(){
            popup_loading.close();
            my_timer.stop();
            console.log('[GLOBAL-INPUT]', 'EXIT-MESSAGE-FUNCTION', 'BACK-TO-HOMEPAGE');
            my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
        });
    }


    //==============================================================

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
            boxColor: VIEW_CONFIG.frame_color
        }

        CircleButton{
            id: cancel_button_confirmation
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "BATAL" For Retry Transaction');
                    console.log('Press "BATAL" For Retry Transaction');
                    if (retryAbleTransaction){
                        global_confirmation_frame.close();
                        exit_with_message(VIEW_CONFIG.failure_page_timer);
                        return;
                    } else {
                        console.log('[GLOBAL-INPUT]', 'CANCEL-BUTTON', 'BACK-TO-HOMEPAGE');
                        my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                    }
                }
            }
        }


        CircleButton{
            id: proceed_button
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'LANJUT'
            modeReverse: true
            blinkingMode: true
            visible: retryAbleTransaction
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    console.log('Press "LANJUT" For Retry Transaction');
                    if (press != '0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "LANJUT" For Retry Transaction');
                    proceed_button.visible = false;
                    if (retryCategory == 'TOPUP'){
                        press = '0';
                        preload_check_card.open();
                        return;
                    }
                    global_confirmation_frame.close();
                    my_timer.stop();
                    my_layer.push(retry_payment_process, {details: retryDetails, pendingPayment: pendingPayment, receivedPayment: receivedPayment});
                }
            }
        }
    }

    SelectPaymentPopupNotif{
        id: select_payment
        visible: isConfirm
        calledFrom: 'global_input_number'
        listActivePayment: activePayment
        _qrMultiEnable: true
        totalEnable: activePayment.length
        z: 99
    }

    SelectQRProviderPopupNotif{
        id: select_qr_provider
        visible: false
        calledFrom: 'global_input_number'
        listActivePayment: activePayment
        _qrMultiEnable: false
        totalEnable: activePayment.length
        z: 99
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
                    console.log('[GLOBAL-INPUT]', 'CANCEL-BUTTON-CHECK-CARD', 'BACK-TO-HOMEPAGE');
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

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }
}

