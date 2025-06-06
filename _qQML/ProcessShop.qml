import QtQuick 2.2
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC

Base{
    id: base_page
    property int timer_value: (VIEW_CONFIG.page_timer * 3)
    property var press: '0'
    property var details: undefined
    property var notif_text: 'Masukkan Uang Tunai Anda Pada Bill Acceptor di bawah'
    property bool isPaid: false
    property int receivedCash: 0
    property var lastBalance: '999000'
    property var cardNo: '6024123443211234'
    property var totalPrice: 0
    property var getDenom: 0
    property var adminFee: 0
    property var modeButtonPopup: 'check_balance';
    property bool topupSuccess: false
    property int reprintAttempt: 0
    property var uniqueCode: ''
    idx_bg: 3
    imgPanel: 'source/cash black.png'
    textPanel: 'Proses Pembayaran'
    imgPanelScale: .8

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            if (details != undefined) console.log('details', JSON.stringify(details));
            abc.counter = timer_value;
            my_timer.start();
            press = '0';
            uniqueCode = ''
            receivedCash = 0;
            isPaid = false;
            modeButtonPopup = 'check_balance'
            topupSuccess = false;
            reprintAttempt = 0;
            define_first_notif();
            //TEST_ONLY
            //payment_complete('DEBUG_TEST')
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop()
        }
    }

    Component.onCompleted:{
        base.result_balance_qprox.connect(get_balance);
        base.result_sale_edc.connect(edc_payment_result);
        base.result_cd_move.connect(card_eject_result);
        base.result_store_transaction.connect(store_result);
        base.result_sale_print.connect(print_result);
        base.result_topup_qprox.connect(topup_result);
        base.result_store_topup.connect(store_result);
        base.result_bill_receive.connect(bill_payment_result);
        base.result_bill_stop.connect(bill_payment_result);
        base.result_bill_status.connect(bill_payment_result);
    }

    Component.onDestruction:{
        base.result_balance_qprox.disconnect(get_balance);
        base.result_sale_edc.disconnect(edc_payment_result);
        base.result_cd_move.disconnect(card_eject_result);
        base.result_store_transaction.disconnect(store_result);
        base.result_sale_print.disconnect(print_result);
        base.result_topup_qprox.disconnect(topup_result);
        base.result_store_topup.disconnect(store_result);
        base.result_bill_receive.disconnect(bill_payment_result);
        base.result_bill_stop.disconnect(bill_payment_result);
        base.result_bill_status.disconnect(bill_payment_result);
    }

    function topup_result(t){
        console.log('topup_result', t);
        popup_loading.close();
        abc.counter = 30;
        my_timer.restart();
        if (t.indexOf('TOPUP_SAM_REQUIRED')> -1){
            var slot_topup = t.split('|')[1]
            _SLOT.start_do_topup_deposit_bni(slot_topup);
            console.log('do topup action for slot : ', slot_topup)
        } else if (t==undefined||t.indexOf('ERROR') > -1||t=='TOPUP_ERROR'){
            slave_title.text = 'Silakan Ambil Struk Anda Di Bawah.\nJika Saldo Kartu Prabayar Anda Gagal Terisi, Silakan Hubungi Layanan Pelanggan.';
            slave_title.visible = true;
        } else {
            var output = t.split('|')
            var topupResponse = output[0]
            var result = JSON.parse(output[1]);
            if (topupResponse=='0000'){
                topupSuccess = true;
                details.topup_details = result;
                cardNo = result.card_no;
                lastBalance = result.last_balance;
                card_no_prepaid.text = FUNC.insert_space_four(cardNo);
                image_prepaid_card.source = "source/tapcash-card.png";
                notif_saldo.text = "Isi Ulang Berhasil.\nSaldo Kartu TapCash Anda\nRp. "+FUNC.insert_dot(lastBalance)+",-\nAmbil Struk Anda di Bawah."
                _SLOT.start_store_topup_transaction(JSON.stringify(details));
                //if (cardNo.substring(0, 4) == '6032'){
                //  image_prepaid_card.source = "source/emoney-card.png";
                //  notif_saldo.text = "Isi Ulang Berhasil.\nSaldo Kartu e-Money Anda\nRp. "+FUNC.insert_dot(lastBalance)+",-\nAmbil Struk Anda di Bawah."
                //} else if (cardNo.substring(0, 4) == '7546'){
                //  image_prepaid_card.source = "source/tapcash-card.png";
                //  notif_saldo.text = "Isi Ulang Berhasil.\nSaldo Kartu TapCash Anda\nRp. "+FUNC.insert_dot(lastBalance)+",-\nAmbil Struk Anda di Bawah."
                //}
            } else if (topupResponse=='5106'||topupResponse=='5103'){
                slave_title.text = 'Terdeteksi Kegagalan Pada Proses Isi Ulang Karena Kartu Tidak Sesuai.\nSilakan Ambil Struk Anda Di Bawah dan Hubungi Layanan Pelanggan.';
                slave_title.visible = true;
            } else if (topupResponse=='1008'){
                slave_title.text = 'Terdeteksi Kegagalan Pada Proses Isi Ulang Karena Kartu Sudah Tidak Aktif.\nSilakan Ambil Struk Anda Di Bawah dan Hubungi Layanan Pelanggan.';
                slave_title.visible = true;
            } else if (topupResponse=='FFFE'){
                slave_title.text = 'Terjadi Kegagalan Pada Proses Isi Ulang Karena Kartu Tidak Terdeteksi.\nSilakan Ambil Struk Anda Di Bawah dan Hubungi Layanan Pelanggan.';
                slave_title.visible = true;
            } else {
                slave_title.text = 'Silakan Ambil Struk Anda Di Bawah.\nJika Saldo Kartu Prabayar Anda Gagal Terisi, Silakan Hubungi Layanan Pelanggan.';
                slave_title.visible = true;
            }
        }
        _SLOT.start_sale_print_global();
        // Check Manual Update SAM Saldo Here
        // if (topupSuccess) _SLOT.start_manual_topup_bni();
    }

    function print_result(p){
        console.log('print_result', p)
//        if (p!='SALEPRINT|DONE'){
//            abc.counter = 10;
//            my_timer.restart();
//            false_notif('Dear User|Jika Struk Tidak Keluar, Silakan Tekan Tombol Berikut');
//            modeButtonPopup = 'reprint';
//            standard_notif_view._button_text = 'cetak lagi';
//            standard_notif_view.buttonEnabled = false;
//        }
    }

    function store_result(r){
        console.log('store_result', r)
        if (r.indexOf('ERROR') > -1 || r.indexOf('FAILED|STORE_TRX') > -1){
            _SLOT.retry_store_transaction_global()
            console.log('Retry To Store The Data into DB')
        }
    }

    function print_failed_transaction(channel){
        if (channel=='cash'){
            details.payment_error = 'BILL_ERROR';
            details.payment_received = receivedCash.toString();
            console.log('print_failed_transaction', channel, JSON.stringify(details));
            _SLOT.start_store_transaction_global(JSON.stringify(details));
            _SLOT.start_sale_print_global();
        }
    }

    function card_eject_result(r){
        console.log('card_eject_result', r)
        popup_loading.close();
        abc.counter = 10;
        my_timer.restart();
        if (r.indexOf('ERROR') > -1) {
            slave_title.text = 'Silakan Ambil Struk Anda Di Bawah.\nJika Kartu Tidak Keluar, Silakan Hubungi Layanan Pelanggan.';
        }
        if (r.indexOf('SUCCESS') > -1) {
            var unit = details.qty.toString()
            slave_title.text = 'Silakan Ambil Struk dan ' + unit + ' pcs Kartu Prabayar Baru Anda Di Bawah.';
        }
        _SLOT.start_sale_print_global();
    }

    function payment_complete(mode){
    //        popup_loading.close();
        if (mode != undefined){
            console.log('payment_complete', mode)
            details.notes = mode + ' - ' + new Date().getTime().toString();
        }
        console.log('payment_complete', JSON.stringify(details))
        _SLOT.start_store_transaction_global(JSON.stringify(details))
        isPaid = true;
//        abc.counter = 15;
//        my_timer.restart();
        arrow_down.visible = false;
//        arrow_down.anchors.rightMargin = 900;
        back_button.button_text = 'selesai';
        back_button.visible = true;
        switch(details.shop_type){
            case 'shop':
//                var unit = details.qty.toString() change to details.status
                var unit = details.status.toString()
                // _SLOT.start_multiple_eject(unit)
                slave_title.text = 'Sedang Memproses Kartu Prabayar Baru Anda Dalam Beberapa Saat...'
                break;
            case 'topup':
//                open_preload_notif();
//                modeButtonPopup = 'do_topup';
//                standard_notif_view._button_text = 'lanjut';
//                standard_notif_view.buttonEnabled = false;
                perform_do_topup();
                slave_title.text = 'Sedang Memproses Isi Ulang Kartu Prabayar Anda...\nPastikan Kartu Prabayar Anda Masih Menempel Di Reader.'
                break;
        }
    }

    function bill_payment_result(r){
        console.log("bill_payment_result : ", r)
        var billFunction = r.split('|')[0]
        var billResult = r.split('|')[1]
        if (billFunction == 'RECEIVE_BILL'){
            if (billResult == "ERROR" || billResult == 'TIMEOUT' || billResult == 'JAMMED'){
                false_notif();
                if (receivedCash > 0){                    
                    print_failed_transaction('cash');
                }
                return;
            } else if (billResult == 'COMPLETE'){
//                _SLOT.start_dis_accept_mei();
//                _SLOT.start_store_es_mei();
                _SLOT.stop_bill_receive_note()
                back_button.visible = false;
                popup_loading.open();
                notif_text = qsTr('Mohon Tunggu, Memproses Penyimpanan Uang Anda.');
            } else if (billResult == 'EXCEED'){
                false_notif('Mohon Maaf|Silakan Hanya Masukkan 1 Lembar Uang Dengan Nilai Yang Sesuai Dengan Nominal Transaksi.\n(Ambil Terlebih Dahulu Uang Anda Sebelum Menekan Tombol)');
                modeButtonPopup = 'retrigger_bill';
                standard_notif_view.buttonEnabled = false;
                standard_notif_view._button_text = 'coba lagi';
                return;
            } else if (billResult == 'BAD_NOTES'){
                false_notif('Mohon Maaf|Pastikan Uang Anda Dalam Kondisi Baik Dan Tidak Lusuh.\n(Ambil Terlebih Dahulu Uang Anda Sebelum Menekan Tombol)');
                modeButtonPopup = 'retrigger_bill';
                standard_notif_view.buttonEnabled = false;
                standard_notif_view._button_text = 'coba lagi';
                return;
            } else {
                receivedCash = parseInt(billResult);
                abc.counter = timer_value;
                my_timer.restart();
//                _SLOT.start_bill_receive_note();
            }
        } else if (billFunction == 'STOP_BILL'){
            if(billResult.indexOf('SUCCESS') > -1 && receivedCash >= totalPrice) {
                var cashResponse = JSON.parse(r.replace('STOP_BILL|SUCCESS-', ''))
                details.payment_details = cashResponse;
                details.payment_received = cashResponse.total;
                payment_complete();
            }
        } else if (billFunction == 'STATUS_BILL'){
            if(billResult=='ERROR') {
                false_notif();
                return;
            }
        }
    }

    function edc_payment_result(r){
        console.log("edc_payment_result : ", r)
        if (r==undefined||r==""||r.indexOf("ERROR") > -1){
            false_notif();
            return;
        }
        var edcFunction = r.split('|')[0]
        var edcResult = r.split('|')[1]
        if (edcFunction == "SUCCESS") {
            receivedCash = totalPrice;
            details.payment_details = JSON.parse(r.replace('SUCCESS|', ''));
            details.payment_received = totalPrice;
            payment_complete();
            popup_loading.open();
            return;
        }
        if (edcFunction == 'SALE'){
            switch(edcResult){
            case 'SR':
                notif_text = qsTr('Mohon Tunggu, Sedang Mensinkronisasi Ulang.');
                arrow_down.visible = false;
                break;
            case 'CI':
                notif_text  = qsTr('Silakan Masukkan Kartu Anda Di Slot Tersedia.');
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            case 'PI':
                notif_text = qsTr('Kartu Terdeteksi, Silakan Masukkan Kode PIN.');
                back_button.visible = false;
                arrow_down.visible = false;
                break;
            case 'DO':
                notif_text = qsTr('Kode Pin Diterima, Menunggu Balasan Sistem.');
                back_button.visible = false;
                arrow_down.visible = false;
                break;
            case 'TC':
                notif_text = qsTr('Mohon Maaf, Terjadi Pembatalan Pada Proses Pembayaran.');
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            case 'CO':
                notif_text = qsTr('Silakan Ambil Kembali Kartu Anda Dari Slot.');
                back_button.visible = false;
                arrow_down.visible = true;
                break;
            case 'CR#EXCEPTION': case 'CR#UNKNOWN':
                notif_text = qsTr('Terjadi Suatu Kesalahan, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            case 'CR#CARD_ERROR':
                notif_text = qsTr('Terjadi Kesalahan Pada Kartu, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            case 'CR#PIN_ERROR':
                notif_text = qsTr('Terjadi Kesalahan Pada PIN, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            case 'CR#SERVER_ERROR':
                notif_text = qsTr('Terjadi Kesalahan Pada Sistem, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            case 'CR#NORMAL_CASE':
                notif_text = qsTr('Silakan Ambil Kembali Kartu Anda untuk Melanjutkan Transaksi.');
                back_button.visible = true;
                arrow_down.visible = false;
                break;
            default:
                back_button.visible = true;
                arrow_down.visible = true;
                break;
            }
        }
    }

    function get_balance(text){
        console.log('get_balance', text);
        press = '0';
        standard_notif_view.buttonEnabled = true;
        popup_loading.close();
        var result = text.split('|')[1];
        if (result == 'ERROR'){
            false_notif('Mohon Maaf|Gagal Mendapatkan Saldo, Pastikan Kartu Prabayar Anda sudah ditempelkan pada Reader');
            return;
        } else {
            var info = JSON.parse(result);
            var balance = info.balance
            cardNo = info.card_no;
            var bankName = info.bank_name;
            var bankType = info.bank_type;
            if (cardNo.substring(0, 4) == '6032'){
                false_notif('Pelanggan YTH|Nomor Kartu e-Money Anda ['+cardNo+']\nSisa Saldo Rp. '+ FUNC.insert_dot(balance));
            } else if (cardNo.substring(0, 4) == '7546'){
                false_notif('Pelanggan YTH|Nomor Kartu TapCash Anda ['+cardNo+']\nSisa Saldo Rp. '+ FUNC.insert_dot(balance));
            } else {
                false_notif('Pelanggan YTH|Nomor Kartu Prabayar Anda ['+cardNo+']\nSisa Saldo Rp. '+ FUNC.insert_dot(balance));
            }
            modeButtonPopup = 'do_topup';
            standard_notif_view._button_text = 'topup';
            standard_notif_view.buttonEnabled = false;
        }
    }

    function perform_do_topup(){
        var provider = details.provider;
        var amount = getDenom.toString();
        var structId = details.shop_type + details.epoch.toString();
        if (provider.indexOf('Mandiri') > -1 || cardNo.substring(0, 4) == '6032'){
            _SLOT.start_topup_offline_mandiri(amount);
        } else if (provider.indexOf('BNI') > -1 || cardNo.substring(0, 4) == '7546'){
            _SLOT.start_topup_offline_bni(amount, structId);
        }
    }

    function get_wording(i){
        if (i=='shop') return 'Pembelian Kartu';
        if (i=='topup') return 'TopUp Kartu';
        if (i=='cash') return 'Tunai';
        if (i=='debit') return 'Kartu Debit';

    }

    function define_first_notif(){
        _SLOT.start_set_payment(details.payment);
        adminFee = parseInt(details.admin_fee);
        var epoch_string = details.epoch.toString();
        uniqueCode = epoch_string.substring(epoch_string.length-6);
        if (details.payment == 'cash') {
            totalPrice = parseInt(details.value)
            getDenom = totalPrice - adminFee;
            notif_text = 'Masukkan Uang Tunai Anda Pada Bill Acceptor Di Bawah';
            _SLOT.start_set_direct_price(totalPrice.toString());
//            _SLOT.start_accept_mei();
            _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString())
        }
        if (details.payment == 'debit') {
            getDenom = parseInt(details.value);
            totalPrice = getDenom + adminFee;
            var structId = details.shop_type + details.epoch.toString();
            _SLOT.create_sale_edc_with_struct_id(totalPrice.toString(), structId);
            notif_text = 'Masukkan Kartu Debit dan Kode PIN Pada EDC Di Bawah';
        }
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
                    if (details.payment=='cash' && !isPaid) {
                        _SLOT.stop_bill_receive_note();
                        if (receivedCash > 0){
                            print_failed_transaction('cash');
    //                        _SLOT.start_return_es_mei();
                        }
    //                    _SLOT.start_dis_accept_mei();
                    }
                    my_timer.stop()
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }))
                }
            }
        }
    }

    BackButton{
        id:back_button
        anchors.left: parent.left
        anchors.leftMargin: 120
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        z: 10
        visible: !popup_loading.visible
        modeReverse: true

        MouseArea{
            anchors.fill: parent
            onClicked: {
                if (press != '0') return;
                press = '1';
                _SLOT.user_action_log('Press Cancel Button "Payment Process"');
                if (details.payment=='cash' && !isPaid) {
                    _SLOT.stop_bill_receive_note();
                    if (receivedCash > 0){
                        print_failed_transaction('cash');
//                        _SLOT.start_return_es_mei();
                    }
//                    _SLOT.start_dis_accept_mei();
                }
                my_timer.stop()
                my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
            }
        }
    }

    //==============================================================
    //PUT MAIN COMPONENT HERE

    function open_preload_notif(){
        false_notif('Mohon Pastikan|Kartu Prabayar Anda Masih Ditempelkan Pada Reader Sebelum Melanjutkan');
    }

    function false_notif(param){
        press = '0';
        standard_notif_view.z = 100;
        standard_notif_view.buttonEnabled = true ;
        standard_notif_view._button_text = 'tutup';
        if (param==undefined){
            standard_notif_view.show_text = "Mohon Maaf";
            standard_notif_view.show_detail = "Terjadi Kesalahan Pada Sistem, Mohon Coba Lagi Beberapa Saat";
        } else {
            standard_notif_view.show_text = param.split('|')[0];
            standard_notif_view.show_detail = param.split('|')[1];
        }
        standard_notif_view.open();
    }


    Rectangle{
        id: main_base
        color: '#1D294D'
        radius: 50
        border.width: 0
        anchors.verticalCenterOffset: 50
        anchors.horizontalCenterOffset: 150
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        opacity: .97
        width: 1100
        height: 900
        visible: !standard_notif_view.visible

    }


    Text {
        id: main_title
        height: 100
        color: "white"
        visible: !standard_notif_view.visible
        text: (isPaid==true) ? "Pembayaran Berhasil" : "Pembayaran " + get_wording(details.payment)
        anchors.top: parent.top
        anchors.topMargin: 150
        wrapMode: Text.WordWrap
        font.bold: false
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        anchors.horizontalCenterOffset: 150
        font.family: "Ubuntu"
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 45
    }


    Text {
        id: slave_title
        width: 900
        height: 300
        color: "white"
        visible: (isPaid && details.shop_type=='shop') ? true : false;
        text: "Silakan Ambil Struk Anda Di Bawah.\nJika Kartu Tidak Keluar, Silakan Hubungi Layanan Pelanggan."
        anchors.top: parent.top
        anchors.topMargin: 300
        wrapMode: Text.WordWrap
        font.bold: false
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        anchors.horizontalCenterOffset: 150
        font.family: "Ubuntu"
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 30
    }

    Text {
        id: sub_slave_title
        width: 900
        height: 300
        color: "white"
        visible: isPaid
        text: "Simpan Kode Unik Anda ("+uniqueCode+"). Jika Struk Gagal Keluar, Tekan Tombol Berikut."
        anchors.top: parent.top
        anchors.topMargin: 425
        wrapMode: Text.WordWrap
        font.bold: false
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        anchors.horizontalCenterOffset: 150
        font.family: "Ubuntu"
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: 30
    }

    BackButton{
        id:reprint_button
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 355
        anchors.horizontalCenterOffset: 150
        anchors.horizontalCenter: parent.horizontalCenter
        z: 10
        visible: isPaid
        modeReverse: true
        button_text: 'cetak lagi'
        MouseArea{
            anchors.fill: parent
            enabled: (reprintAttempt<3) ? true : false
            onClicked: {
                _SLOT.user_action_log('Press Button "Cetak Lagi"');
                reprintAttempt += 1;
                parent.visible = false;
                _SLOT.start_reprint_global();
//                _SLOT.start_sale_print_global();
            }
        }
    }

    AnimatedImage{
        id: arrow_down2
        visible: isPaid
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 100
        anchors.horizontalCenterOffset: 150
        anchors.horizontalCenter: parent.horizontalCenter
        source: "source/arrow_down.gif"
    }

    GroupBox{
        id: group_box_topup_success
        anchors.horizontalCenterOffset: 150
        anchors.verticalCenterOffset: -150
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        flat: true
        width: 1066
        height: 400
        visible: (isPaid && details.shop_type=='topup' && topupSuccess) ? true : false;
        Text {
            id: notif_saldo
            width: 600
            height: 200
            color: "white"
            visible: !standard_notif_view.visible
            text: "Isi Ulang Berhasil.\nSaldo Kartu Prabayar Anda\nRp. 0, -\nAmbil Struk Anda di Bawah."
            wrapMode: Text.WordWrap
            anchors.verticalCenter: parent.verticalCenter
            font.bold: false
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenterOffset: 200
            font.family: "Ubuntu"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 30
        }
        Image{
            id: image_prepaid_card
            source: "source/card_tj_original.png"
            width: 400
            height: 250
            anchors.horizontalCenterOffset: -300
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            Text{
                id: card_no_prepaid
                font.pixelSize: 16
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 25
                anchors.left: parent.left
                anchors.leftMargin: 30
                color: 'white'
//                text: FUNC.insert_space_four('6123321441233214')
            }
        }
    }

    Column{
        id: row_texts
        anchors.horizontalCenterOffset: 150
        visible: !isPaid
        anchors.verticalCenterOffset: -50
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 25
        TextDetailRow{
            id: _shop_type
            labelName: qsTr('Tipe Pembelian')
            labelContent: get_wording(details.shop_type)
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }
        TextDetailRow{
            id: _provider
            labelName: qsTr('Tipe Kartu')
            labelContent: details.provider
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }
        TextDetailRow{
            id: _nominal
            labelName: qsTr('Nominal')
            labelContent: 'Rp. ' +  FUNC.insert_dot(getDenom.toString()) + ',-';
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }
        TextDetailRow{
            id: _jumlahUnit
            labelName: qsTr('Jumlah Unit')
            labelContent: details.qty;
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }
        TextDetailRow{
            id: _biaya_admin
            visible: (details.shop_type=='topup') ? true : false;
            labelName: qsTr('Biaya Admin')
            labelContent: 'Rp. ' +  FUNC.insert_dot(adminFee.toString()) + ',-';
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }
        TextDetailRow{
            id: _total_biaya
            labelName: qsTr('Total')
            labelContent: 'Rp. ' +  FUNC.insert_dot(totalPrice.toString()) + ',-';
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }
        TextDetailRow{
            id: _uang_tunai
            labelName: qsTr('Uang Diterima')
            labelContent: 'Rp. ' + FUNC.insert_dot(receivedCash.toString()) + ',-';
            contentSize: 30
            labelSize: 30
            theme: 'white'
        }

    }

    Row{
        id: row_edc
        anchors.horizontalCenterOffset: 150
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 150
        visible: (details.payment=='debit' && !isPaid) ? true : false
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 25
        AnimatedImage{
            width: 300; height: 200;
            source: "source/insert_card_realistic.jpg"
            fillMode: Image.PreserveAspectFit
        }
        AnimatedImage{
            width: 300; height: 200;
            source: "source/input_card_pin_realistic.jpeg"
            fillMode: Image.PreserveAspectFit
        }
    }

    Row{
        id: row_note_cash
        property int adjust_point: 75
        width: 500
        height: 100
        layoutDirection: Qt.LeftToRight
        anchors.horizontalCenterOffset: 150
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 175
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 30
        visible: (details.payment=='cash' && !isPaid && !standard_notif_view.visible) ? true : false
        Image{
            id: img_count_100
            width: 100; height: 100
            source: "source/denom_100k.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            id: img_count_50
            width: 100; height: 100;
            source: "source/denom_50k.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            id: img_count_20
           width: 100; height: 100;
            source: "source/denom_20k.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            id: img_count_10
            width: 100; height: 100;
            source: "source/denom_10k.png"
            fillMode: Image.PreserveAspectFit
        }
//        Image{
//            id: img_count_5
//            width: 100; height: 50;
//            rotation: 30
//            source: "source/5rb.png"
//            fillMode: Image.PreserveAspectFit
//        }
//        Image{
//            id: img_count_2
//            width: 100; height: 50;
//            rotation: 30
//            source: "source/2rb.png"
//            fillMode: Image.PreserveAspectFit
//        }

    }

    AnimatedImage{
        id: arrow_down
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
        anchors.right: parent.right
        anchors.rightMargin: 50
        source: "source/arrow_down.gif"
    }

    Rectangle{
        id: rec_notif
        visible: (!isPaid && details.shop_type=='shop') ? true : false;
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40
        anchors.horizontalCenter: parent.horizontalCenter
        color: "transparent"
        radius: 30
        anchors.horizontalCenterOffset: 150
        border.width: 0
        opacity: 0.7
        width: 1000
        height: 100
        Text {
            id: process_notif
            anchors.fill: parent
            color: "#ffffff"
            text: "*" + notif_text
            wrapMode: Text.WordWrap
            font.italic: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.horizontalCenterOffset: 0
            font.family:"Ubuntu"
            font.pixelSize: 30
        }

    }


    //==============================================================

    StandardNotifView{
        id: standard_notif_view
        withBackground: false
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
                if (modeButtonPopup=='check_balance'){
                    popup_loading.open();
                    _SLOT.start_check_card_balance();
                }
                if (modeButtonPopup=='do_topup'){
                    popup_loading.open();
                    perform_do_topup();
                }
                if (modeButtonPopup=='retrigger_bill') {
                    _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString());
                }
                if (modeButtonPopup=='reprint') {
                    _SLOT.start_reprint_global();
                }
                parent.visible = false;
            }
        }
    }

    PopupLoading{
        id: popup_loading
    }



}

