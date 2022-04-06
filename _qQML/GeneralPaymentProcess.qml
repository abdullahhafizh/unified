import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
import "screen.js" as SCREEN
import "config.js" as CONF

Base{
    id: general_payment_process

//                property var globalScreenType: '2'
//                height: (globalScreenType=='2') ? 1024 : 1080
//                width: (globalScreenType=='2') ? 1280 : 1920
    property int timer_value: 600
    property var press: '0'
    property var details
    property var notif_text: 'Masukan Uang Tunai Anda Pada Bill Acceptor di bawah'
    property bool successTransaction: false
    property int receivedPayment: 0
    property var lastBalance: '999000'
    property var cardNo: '6024123443211234'
    property var totalPrice: 0
    property var getDenom: 0
    property var adminFee: 0
    property var modeButtonPopup
    property int reprintAttempt: 0
    property var uniqueCode: ''

    property bool frameWithButton: false
    property bool centerOnlyButton: false
    property bool proceedAble: false
    property int attemptCD: 0

    property int refundAmount: 0
    property var refundMode: 'payment_cash_exceed'
    property var refundChannel: 'DIVA'
    property var refundData
    property bool refundFeature: true
    property bool transactionInProcess: false

    property var qrPayload
    property var preloadNotif
    property var customerPhone: ''

    property var notifTitle: ''
    property var notifMessage: ''

    //Handling Refund Confirmation
    property bool useRefundConfirmation: true
    //Handling New Transaction Status Frame
    property bool useTransactionStatusFrame: true
    //Handle Cancel Confirmation
    property bool useCancelConfirmation: true

    property bool closeTrxSession: false

    property bool promoCodeActive: false
    property var promoData


    signal framingSignal(string str)

    idx_bg: 0
    imgPanel: 'source/cash black.png'
    textPanel: 'Proses Pembayaran'
    imgPanelScale: .8

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            reset_variables_to_default();
//            if (details != undefined) console.log('product details', JSON.stringify(details));
            if (preloadNotif==undefined){
//                initial_process();
                do_check_promo();
            } else {
                popup_refund.open('Silakan Masukkan No HP Anda', refundAmount);
                cancel_button_input_number.visible = true;
            }
            modeButtonPopup = 'check_balance';
            abc.counter = timer_value;
            my_timer.start();
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop()
        }
    }

    Component.onCompleted:{
        base.result_balance_qprox.connect(get_balance);
        base.result_sale_edc.connect(edc_payment_result);
        base.result_accept_mei.connect(mei_payment_result);
        base.result_dis_accept_mei.connect(mei_payment_result);
        base.result_stack_mei.connect(mei_payment_result);
        base.result_return_mei.connect(mei_payment_result);
        base.result_store_es_mei.connect(mei_payment_result);
        base.result_cd_move.connect(shop_card_result);
        base.result_store_transaction.connect(store_result);
        base.result_sale_print.connect(print_result);
        base.result_topup_qprox.connect(topup_result);
        base.result_store_topup.connect(store_result);
        base.result_bill_receive.connect(bill_payment_result);
        base.result_bill_stop.connect(bill_payment_result);
        base.result_bill_status.connect(bill_payment_result);
        base.result_get_qr.connect(qr_get_result);
        base.result_check_qr.connect(qr_check_result);
        base.result_trx_ppob.connect(ppob_trx_result);
        base.result_pay_qr.connect(qr_check_result);
        base.result_global_refund_balance.connect(transfer_balance_result);
        base.result_get_refund.connect(get_refund_result);
        base.result_general_payment.connect(execute_transaction);
        base.result_check_trx.connect(get_promo_result);
        framingSignal.connect(get_signal_frame);
    }

    Component.onDestruction:{
        base.result_balance_qprox.disconnect(get_balance);
        base.result_sale_edc.disconnect(edc_payment_result);
        base.result_accept_mei.disconnect(mei_payment_result);
        base.result_dis_accept_mei.disconnect(mei_payment_result);
        base.result_stack_mei.disconnect(mei_payment_result);
        base.result_return_mei.disconnect(mei_payment_result);
        base.result_store_es_mei.disconnect(mei_payment_result);
        base.result_cd_move.disconnect(shop_card_result);
        base.result_store_transaction.disconnect(store_result);
        base.result_sale_print.disconnect(print_result);
        base.result_topup_qprox.disconnect(topup_result);
        base.result_store_topup.disconnect(store_result);
        base.result_bill_receive.disconnect(bill_payment_result);
        base.result_bill_stop.disconnect(bill_payment_result);
        base.result_bill_status.disconnect(bill_payment_result);
        base.result_get_qr.disconnect(qr_get_result);
        base.result_check_qr.disconnect(qr_check_result);
        base.result_trx_ppob.disconnect(ppob_trx_result);
        base.result_pay_qr.disconnect(qr_check_result);
        base.result_global_refund_balance.disconnect(transfer_balance_result);
        base.result_get_refund.disconnect(get_refund_result);
        base.result_general_payment.disconnect(execute_transaction);
        base.result_check_trx.disconnect(get_promo_result);
        framingSignal.disconnect(get_signal_frame);

    }


    function do_check_promo(){
        popup_loading.open('Memeriksa Kode Promo...');
        if (details === undefined) {
            console.log('Failed To Get TRX Product Details');
            initial_process('do_check_promo');
        } else {
            console.log('do_check_promo', JSON.stringify(details));
        }
        var data = JSON.stringify(details);
        _SLOT.start_do_inquiry_promo(data);
    }


    function get_promo_result(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_promo_result', now, p);
        var result = p.split('|')[1];
        var trx_data =  JSON.parse(p.split('|')[2]);
        //Store To Temp Promo Data
        promoData = trx_data;
        var closeTime = 5;
        if (result == 'AVAILABLE'){
            // Promo Only Direct Impact With Cash Payment
            // Otherwise will be impacted after payment for further validation on payment_channel
            if (details.payment == 'cash'){
                details = trx_data;
                details.promo_code_active = true;
            }
            popup_loading.imageSource = "source/success.png";
            popup_loading.textMain = 'Yeay, Kode Promo Aktif Ditemukan';
            popup_loading.textSlave = promoData.promo.remarks;
            info_promo.visible = true;
            info_promo.labelContent = promoData.promo.name;
            promoCodeActive = true;
            console.log("Active Promo :", promoData.promo.name, promoData.promo.remarks);
        } else {
            closeTime = 1;
            // popup_loading.imageSource = "source/smiley_down.png";
            // popup_loading.textMain = 'Mohon Maaf, Tidak Ditemukan Kode Promo Aktif';
        }
        delay((closeTime*1000), function(){
            popup_loading.close();
            initial_process('get_promo_result');
        });
    }

    function set_refund_channel(channel){
        popup_refund.manualEnable = false;
        popup_refund.customerServiceEnable = false;
        popup_refund.divaEnable = false;
        popup_refund.linkajaEnable = false;
        popup_refund.ovoEnable = false;
        popup_refund.gopayEnable = false;
        popup_refund.shopeepayEnable = false;
        popup_refund.danaEnable = false;
        switch(channel){
        case 'CS_ONLY':
            popup_refund.customerServiceEnable = true;
            break;
        case 'WHATSAPP_ONLY':
            popup_refund.divaEnable = true;
            break;
        case 'LINKAJA_ONLY':
            popup_refund.linkajaEnable = true;
            break;
        case 'OVO_ONLY':
            popup_refund.ovoEnable = true;
            break;
        case 'GOPAY_ONLY':
            popup_refund.gopayEnable = true;
            break;
        case 'SHOPEE_ONLY':
            popup_refund.shopeepayEnable = true;
            break;
        case 'DANA_ONLY':
            popup_refund.danaEnable = true;
            break;
        }
    }

    function get_refund_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_refund_result', now, r);
        refundFeature = true;
        if (r=='REFUND_DISABLED'){
            refundFeature = false;
            console.log('refund_status', refundFeature);
            return;
        }
        var refund = JSON.parse(r);
        if (refund.MANUAL == 'AVAILABLE'){
            var now_hour =  parseInt(Qt.formatDateTime(new Date(), "HH"));
            var over_night = parseInt(CONF.over_night);
            if (now_hour < over_night){
                popup_refund.manualEnable = true;
            }
        }
        if (refund.CS == 'AVAILABLE') popup_refund.customerServiceEnable = true;
        if (refund.DIVA == 'AVAILABLE') popup_refund.divaEnable = true;
        if (refund.LINKAJA == 'AVAILABLE') popup_refund.linkajaEnable = true;
        if (refund.OVO == 'AVAILABLE') popup_refund.ovoEnable = true;
        if (refund.GOPAY == 'AVAILABLE') popup_refund.gopayEnable = true;
        if (refund.SHOPEEPAY == 'AVAILABLE') popup_refund.shopeepayEnable = true;
        if (refund.DANA == 'AVAILABLE') popup_refund.danaEnable = true;
        if (refund.DETAILS.length > 0) popup_refund.availableRefund = refund.DETAILS;
        if (refund.MIN_AMOUNT != undefined && parseInt(refund.MIN_AMOUNT) > 0) popup_refund.minRefundAmount = parseInt(refund.MIN_AMOUNT);
    }

    function reset_variables_to_default(){
        proceedAble = false;
        press = '0';
        uniqueCode = '';
        customerPhone = '';
        notifTitle = '';
        notifMessage = ''
        receivedPayment = 0;
        successTransaction = false;
        reprintAttempt = 0;
        qrPayload = undefined;
        attemptCD = 0;
        frameWithButton = false;
        centerOnlyButton = false;
        refundAmount = 0;
        refundMode = '';
        modeButtonPopup = undefined;
        refundFeature = true;
        transactionInProcess = false;
        closeTrxSession = false;
        promoCodeActive = false;
        promoData = undefined;
    }

    function do_refund_or_print(error){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        var message_case_refund = 'Terjadi Kegagalan Transaksi, ';
        refundMode = error;
        abc.counter = 120;
        my_timer.restart();
        // Validation To Get This Condition, payment received, refund feature disabled and not a success trx
        // While success trx must keep using refund, NAHLOH..!
        //                if (receivedPayment > 0 && !refundFeature && !successTransaction){
        //                    details.pending_trx_code = details.epoch.toString().substr(-6);
        //                    details.pending_trx_code = uniqueCode;
        //                    console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
        //                    release_print('Terjadi Kesalahan/Pembatalan Transaksi', 'Silakan Ambil Struk Transaksi Anda Dan Ulangi Transaksi');
        //                    return;
        //                }
        // Handle Success Transaction With Exceed Payment
        if (!refundFeature){
            if (details.payment=='cash') set_refund_channel('WHATSAPP_ONLY');
        }
        switch(error){
        case undefined:
            //Success Transaction With Exceed Payment
            var exceed = validate_cash_refundable();
            if (exceed == false){
                // Cash Exceed Payment Not Found, Just Print Put Receipt
                release_print();
                return;
            }
            // If Cash Exceed Payment Detected
            refundMode = 'payment_cash_exceed';
            refundAmount = exceed;
            message_case_refund = 'Transaksi Sukses, Terjadi Lebih Bayar [Rp. '+FUNC.insert_dot(exceed.toString())+'], ';
            break;
        case 'user_payment_timeout':
        case 'user_cancellation':
            // Doing Nothing In Cancellation Not Cash
            if (details.payment != 'cash') return;
            refundAmount = receivedPayment;
            details.process_error = error;
            details.payment_received = receivedPayment.toString();
            message_case_refund = 'Terjadi Pembatalan Transaksi, ';
            if (error=='user_payment_timeout') message_case_refund = 'Waktu Transaksi Habis, ';
            break;
        case 'user_cancellation_qr':
        case 'user_payment_timeout_qr':
            // Doing Nothing In Cancellation Not Cash
            refundAmount = receivedPayment;
            details.process_error = error;
            details.payment_received = receivedPayment.toString();
            message_case_refund = 'Terjadi Pembatalan/Kegagalan Transaksi, ';
            if (error=='user_payment_timeout_qr') message_case_refund = 'Waktu Transaksi Habis, ';
            break;
        case 'user_cancellation_debit':
        case 'user_payment_timeout_debit':
            // Doing Nothing In Cancellation Not Cash
            refundAmount = receivedPayment;
            details.process_error = error;
            details.payment_received = receivedPayment.toString();
            message_case_refund = 'Terjadi Pembatalan/Kegagalan Transaksi, ';
            break;
        case 'cash_device_error':
            if (receivedPayment == 0) {
                press = '0';
                switch_frame('source/smiley_down.png', 'Terjadi Kesalahan Mesin, Membatalkan Transaksi Anda', '', 'backToMain|10', false);
                _SLOT.system_action_log('BILL_DEVICE_ERROR_PAYMENT_NOT_RECEIVED');
                abc.counter = 5;
                return;
            }
            details.payment_error = error;
            // details_error_history_push(error)
            details.payment_received = receivedPayment.toString();
            refundAmount = receivedPayment;
            message_case_refund = 'Terjadi Kesalahan Mesin,';
            break;
        case 'cash_device_timeout':
            if (receivedPayment == 0) {
                press = '0';
                switch_frame('source/smiley_down.png', 'Waktu Pembayaran Habis, Membatalkan Transaksi Anda', '', 'backToMain|10', false);
                _SLOT.system_action_log('BILL_DEVICE_TIMEOUT_PAYMENT_NOT_RECEIVED')
                abc.counter = 5;
                return;
            }
            details.payment_error = error;
            // details_error_history_push(error)
            details.payment_received = receivedPayment.toString();
            refundAmount = receivedPayment;
            message_case_refund = 'Waktu Pembayaran Habis,';
            break;
        case 'ppob_error':
        case 'card_eject_error':
        case 'topup_prepaid_error':
            refundAmount = totalPrice;
            if (details.payment=='cash') refundAmount = receivedPayment;
            break;
        }
        // Add History Here, Perhaps Get Duplicate Message
        if (error !== undefined) details_error_history_push(error)
        press = '0';
        popup_refund.open(message_case_refund, refundAmount);
        // Set Waiting Time To IDLE
//        my_timer.stop();
        console.log('do_refund_or_print', now, refundMode, refundAmount, message_case_refund);

    }

    function release_print_with_refund(refund_amount, title, message){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
//        set_refund_number(customerPhone);
        popup_loading.open();
        if (refund_amount==undefined) {
            console.log('release_print_with_refund', now, 'MISSING_REFUND_AMOUNT');
            return;
        }
        details.refund_amount = refund_amount;
        var refundPayload = {
            amount: refund_amount.toString(),
            customer: customerPhone,
            reff_no: details.shop_type + details.epoch.toString(),
            remarks: details,
            channel: refundChannel,
            mode: refundMode,
            payment: details.payment
        }
        if (title!=undefined) notifTitle = title;
        if (message!=undefined) notifMessage = message;
        console.log('release_print_with_refund', now, JSON.stringify(refundPayload));
        _SLOT.start_global_refund_balance(JSON.stringify(refundPayload))
    }

    function transfer_balance_result(transfer){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('transfer_balance_result', now, transfer);
        popup_loading.close();
        var result = transfer.split('|')[1];
        if (['MISSING_REFF_NO','MISSING_AMOUNT','MISSING_CUSTOMER', 'ERROR', 'PENDING', 'MISSING_CHANNEL', 'TOPUP_REFF_NO_PENDING_SUCCESS'].indexOf(result) > -1){
            details.refund_status = 'PENDING';
        }
        if (result=='SUCCESS'){
            details.refund_status = 'SUKSES';
        }
        release_print(notifTitle, notifMessage);
    }

    function hide_all_cancel_button(){
        cancel_button_global.visible = false;
        back_button.visible = false;
        // cancel_button_input_number.visible = false;
        cancel_button_confirmation.visible = false;
        cancel_button_qr.visible = false;
    }

    function release_print(title, msg){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        popup_loading.close();
        my_timer.stop();
        if (title==undefined || title.length == 0) title = 'Terima Kasih';
        if (msg==undefined || msg.length == 0) msg = 'Silakan Ambil Struk Transaksi Anda';
//        if (allQRProvider.indexOf(details.payment) > -1){
//            if (CONF.general_qr=='1') details.payment = 'QRIS PAYMENT';
//        }
        if (successTransaction) {
            // Delete Duplication Promo Data Record
            if (details.promo_data !== undefined) delete details.promo_data;
            //Trigger Confirm Promo Here
            if (details.promo_code_active == true){
                var payload = {
                        pid: details.shop_type + details.epoch.toString(),
                        promo: details.promo,
                    }
                _SLOT.start_do_confirm_promo(JSON.stringify(payload));
            }
            if (CONF.printer_type=='whatsapp'){
                hide_all_cancel_button();
                reset_variables_to_default();
                // Trigger Deposit Update Balance Check
                if (cardNo.substring(0, 4) == '6032'){
                    if (CONF.c2c_mode == 1) _SLOT.start_check_mandiri_deposit();
                } else if (cardNo.substring(0, 4) == '7546'){
                    _SLOT.start_check_bni_deposit();
                }
                my_layer.push(ereceipt_view, {details:details});
                return;
            }
            title = 'Transaksi Berhasil';
            if (details.shop_type == 'topup') msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Anda Dari Reader';
            if (details.shop_type == 'shop'){
                msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Baru Anda';
                _SLOT.start_play_audio('please_take_new_card_with_receipt');
            }
        }
        _SLOT.start_direct_sale_print_global(JSON.stringify(details));
        console.log('release_print', now, title, msg);
        switch_frame('source/take_receipt.png', title, msg, 'backToMain|10', true );
        hide_all_cancel_button();
//        abc.counter = 3;
        reset_variables_to_default();
        // Trigger Deposit Update Balance Check
        if (cardNo.substring(0, 4) == '6032'){
            if (CONF.c2c_mode == 1) _SLOT.start_check_mandiri_deposit();
        } else if (cardNo.substring(0, 4) == '7546'){
            _SLOT.start_check_bni_deposit();
        }
    }

    function ppob_trx_result(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('ppob_trx_result', now, p);
        popup_loading.close();
        transactionInProcess = false;
        var result = p.split('|')[1];
        if (allQRProvider.indexOf(details.payment) > -1) qr_payment_frame.hide();
        if (['MISSING_MSISDN', 'MISSING_PRODUCT_ID','MISSING_AMOUNT','MISSING_OPERATOR', 'MISSING_PAYMENT_TYPE', 'MISSING_PRODUCT_CATEGORY', 'MISSING_REFF_NO', 'ERROR'].indexOf(result) > -1){
            details.process_error = 1;
            details_error_history_push(p)
            details.payment_error = 1;
            details.receipt_title = 'Transaksi Anda Gagal';
            _SLOT.start_play_audio('transaction_failed');
            if (!refundFeature){
            // details.pending_trx_code = details.epoch.toString().substr(-6);
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
                console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
                release_print('Transaksi Anda Gagal', 'Silakan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                return;
            }
            //PPOB Not Be able for pending trx retry
            do_refund_or_print('ppob_error');
            // Must return here to avoid double refund
            return;
        }
        var info = JSON.parse(result);
        successTransaction = true;
        details.ppob_details = info;
        details.receipt_title = 'Transaksi Sukses';
        if (useTransactionStatusFrame){
            validate_transaction_success('Transaksi Sukses');
            return;
        }
        do_refund_or_print();
    }

    function validate_cash_refundable(){
        if (details.payment == 'cash' && receivedPayment > totalPrice){
            return parseInt(receivedPayment - totalPrice);
        }
        return false;
    }

    function qr_check_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        // TODO Ignore Signal When Session is ended
        if (qrPayload == undefined) return;
        console.log('qr_check_result', now, r);
        var mode = r.split('|')[1]
        var result = r.split('|')[2]
        popup_loading.close();
        if (['NOT_AVAILABLE', 'MISSING_AMOUNT', 'MISSING_TRX_ID', 'ERROR'].indexOf(result) > -1){
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Silakan Coba Lagi Dalam Beberapa Saat', 'backToMain|10', true )
            return;
        }
        if (['TIMEOUT'].indexOf(result) > -1){
            if (!refundFeature){
//              details.pending_trx_code = details.epoch.toString().substr(-6);
                details.process_error = 1;
                details_error_history_push(r)
                details.payment_error = 1;
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
                console.log('User Cancellation Without Refund, Generate Pending Code', uniqueCode);
                release_print('Waktu Transaksi Habis', 'Silakan Ambil Struk Transaksi Anda Dan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                return;
            }
            switch_frame('source/smiley_down.png', 'Waktu Pembayaran QR Habis', 'Silakan Coba Lagi Dalam Beberapa Saat', 'closeWindow|3', true )
            set_refund_channel('CS_ONLY');
            do_refund_or_print('user_payment_timeout_qr');
            return;
        }
        if (result=='SUCCESS'){
            var info = JSON.parse(r.split('|')[3]);
            now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
            console.log('qr_check_result', now, mode, result, JSON.stringify(info));
            qr_payment_frame.success(3)
            details.payment_details = info;
            details.init_payment = info.provider;
            details.payment = info.provider;
            if (info.payment_channel !== undefined) details.payment = info.payment_channel;
            details.payment_received = details.value.toString();
            receivedPayment = totalPrice;
            payment_complete('qr');
            var qrMode = mode;
            _SLOT.start_do_print_qr_receipt(qrMode);
//            var qrMode = mode.toLowerCase();
//            switch(qrMode){
//            case 'ovo':
//                _SLOT.start_confirm_ovo_qr(JSON.stringify(qrPayload));
//                break;
//            }
        }
    }

    function qr_get_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('qr_get_result', now, r);
        var mode = r.split('|')[1]
        var result = r.split('|')[2]
        popup_loading.close();
        if (['NOT_AVAILABLE', 'MISSING_AMOUNT', 'MISSING_TRX_ID', 'ERROR', 'MODE_NOT_FOUND'].indexOf(result) > -1){
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Silakan Coba Lagi Dalam Beberapa Saat', 'backToMain|10', true );
            return;
        }
        if (['TIMEOUT'].indexOf(result) > -1){
            switch_frame('source/smiley_down.png', 'Waktu Proses Pembuatan QR Habis', 'Silakan Coba Lagi Dalam Beberapa Saat', 'closeWindow|5', true );
            return;
        }
        var info = JSON.parse(result);
        var qrMode = mode.toUpperCase();
        qr_payment_frame.modeQR = (CONF.general_qr == '1') ? 'QR Wallet Anda' : qrMode;
        qr_payment_frame.imageSource = info.qr;
//        if (qrMode=='ovo') _SLOT.start_do_pay_ovo_qr(JSON.stringify(qrPayload));
//        if (qrMode=='gopay') _SLOT.start_do_check_gopay_qr(JSON.stringify(qrPayload));
//        if (qrMode=='linkaja') _SLOT.start_do_check_linkaja_qr(JSON.stringify(qrPayload));
        var msg = '*' + details.shop_type.toUpperCase() + ' ' + details.provider + ' Rp. ' + FUNC.insert_dot(details.value);
        if (details.shop_type=='topup') msg = '*Isi Ulang Kartu Prabayar '+ details.provider + ' Rp. ' + FUNC.insert_dot(details.denom) + ' + Biaya Admin Rp. ' + FUNC.insert_dot(adminFee.toString());
        if (promoCodeActive) msg = msg +'\nPromo Aktif '+promoData.promo.code+' '+promoData.promo.name;
        press = '0'
        if (info.payment_time != undefined) qr_payment_frame.timerDuration = parseInt(info.payment_time);
        var qr_payment_id = details.shop_type+details.epoch.toString();
        qr_payment_frame.open(msg, qr_payment_id);
        _SLOT.start_check_payment_status(qrMode);
    }

    function topup_result(t){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('topup_result', now, t);
        global_frame.close();
        popup_loading.close();
        transactionInProcess = false;
        if (allQRProvider.indexOf(details.payment) > -1) qr_payment_frame.hide();
        abc.counter = 60;
        my_timer.restart();
        //========
        if (t=='TOPUP_ERROR'||t=='MANDIRI_SAM_BALANCE_EXPIRED'||
                t=='BRI_UPDATE_BALANCE_ERROR'||t.indexOf('BNI_SAM_BALANCE_NOT_SUFFICIENT')> -1){
            if (t=='MANDIRI_SAM_BALANCE_EXPIRED' && CONF.c2c_mode == 0) _SLOT.start_reset_mandiri_settlement();
//            if (t.indexOf('BNI_SAM_BALANCE_NOT_SUFFICIENT')> -1) {
//                var slot_topup = t.split('|')[1]
//                _SLOT.start_do_topup_deposit_bni(slot_topup);
//                console.log('Trigger Manual Topup BNI By Failed TRX : ', now, slot_topup)
//            }
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Pada Proses Isi Ulang Saldo Prabayar Anda', 'closeWindow|3', true )
        } else if (t=='TOPUP_FAILED_CARD_NOT_MATCH'){
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Terdeteksi Perbedaan Kartu Saat Isi Ulang', 'closeWindow|3', true )
        }  else if (t=='MANDIRI_C2C_PARTIAL_ERROR'){
            // Define View And Set Button Continue Mode
            modeButtonPopup = 'c2c_correction';
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t=='BCA_PARTIAL_ERROR') {
            modeButtonPopup = 'bca_correction';
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t=='BRI_PARTIAL_ERROR') {
            modeButtonPopup = 'bri_correction';
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t=='DKI_PARTIAL_ERROR') {
            modeButtonPopup = 'dki_correction';
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t=='MDR_C2C_FORCE_SETTLEMENT') {
            details.force_settlement = 1;
            // Must Return Here to Stop Executing Receipt
            return
        } else {
            var output = t.split('|')
            var topupResponse = output[0]
            var result = JSON.parse(output[1]);
            if (topupResponse=='0000'){
                successTransaction = true;
                details.topup_details = result;
                cardNo = result.card_no;
                lastBalance = result.last_balance;
                if (parseInt(lastBalance) > 0) details.final_balance = lastBalance.toString();
                // Move TRX Success Store Here
                _SLOT.start_store_transaction_global(JSON.stringify(details))
//                _SLOT.start_store_topup_transaction(JSON.stringify(details));
//                _SLOT.start_do_mandiri_topup_settlement();
                if (useTransactionStatusFrame){
                    validate_transaction_success('Transaksi Sukses');
                    return;
                }
                do_refund_or_print();
                return;
            }
            // Do not return here to handle refund for failed topup response
        }
        details.process_error = 1;
        details_error_history_push(t)
        details.payment_error = 1;
        details.receipt_title = 'Transaksi Anda Gagal';
        _SLOT.start_play_audio('transaction_failed');
        if (!refundFeature){
        // details.pending_trx_code = details.epoch.toString().substr(-6);
            details.payment_received = receivedPayment.toString();
            details.pending_trx_code = uniqueCode;
            console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
            release_print('Transaksi Anda Gagal', 'Silakan Ambil Struk Transaksi Anda Dan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
            return;
        }
        do_refund_or_print('topup_prepaid_error');
        // Check Manual Update SAM Saldo Here
    }

    function print_result(p){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('print_result', now, p)
    }

    function store_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('store_result', now, r)
        if (r.indexOf('ERROR') > -1 || r.indexOf('FAILED|STORE_TRX') > -1){
//            _SLOT.retry_store_transaction_global()
            console.log('Retry To Store The Data into DB')
        }
    }

    function print_failed_transaction(channelPayment, issue){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('print_failed_transaction', now, channelPayment, issue, receivedPayment, customerPhone, JSON.stringify(details));
        if (issue==undefined) issue = 'BILL_ERROR';
        if (channelPayment=='cash'){
            details.payment_error = issue;
            details_error_history_push(issue)
            details.payment_received = receivedPayment.toString();
            if (customerPhone!=''){
//                switch_frame('source/smiley_down.png', 'Terjadi Kesalahan/Pembatalan', 'Memproses Pengembalian Dana Anda', 'closeWindow', true );
                var refund_amount = receivedPayment.toString();
                release_print_with_refund(refund_amount, 'Terjadi Kesalahan/Pembatalan', 'Silakan Ambil Struk Sebagai Bukti');
            } else {
                release_print();
            }
        }
    }

    function shop_card_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('shop_card_result', now, r);
        global_frame.close();
        popup_loading.close();
        transactionInProcess = false;
        if (allQRProvider.indexOf(details.payment) > -1) qr_payment_frame.hide();
        abc.counter = 60;
        my_timer.restart();
        var result = r.split('|')[1]
        if (result == 'PARTIAL'){
            press = '0';
            attemptCD -= 1;
            switch_frame('source/take_card.png', 'Silakan Ambil Kartu Anda', 'Kemudian Tekan Tombol Lanjut', 'closeWindow|25', true );
            centerOnlyButton = true;
            modeButtonPopup = 'retrigger_card';
            return;
        }
        if (result == 'ERROR') {
            details.process_error = 1;
            details_error_history_push(r.split('|')[2])
            details.payment_error = 1;
            details.receipt_title = 'Transaksi Anda Gagal';
            _SLOT.start_play_audio('transaction_failed');
            if (!refundFeature){
            // details.pending_trx_code = details.epoch.toString().substr(-6);
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
                console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
                release_print('Transaksi Anda Gagal', 'Silakan Ambil Struk Transaksi Anda Dan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                return;
            }
            do_refund_or_print('card_eject_error');
            return;
        }
        if (result == 'SUCCESS') {
            // Move TRX Success Store Here
            successTransaction = true;
            _SLOT.start_store_transaction_global(JSON.stringify(details));
            if (useTransactionStatusFrame){
                validate_transaction_success('Transaksi Sukses');
                return;
            }
            do_refund_or_print();
            return;
//            switch_frame('source/thumb_ok.png', 'Silakan Ambil Kartu dan Struk Transaksi Anda', 'Terima Kasih', 'backToMain', false )
        }
    }

    function do_promo_data_adjustment(mode){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        if (promoCodeActive) {
            // Adjustment For QR Payment
            if (mode=='qr'){
                var issuer_provider = FUNC.serialize_qris_provider(details.init_payment);
                var acquirer_provider = details.payment.toUpperCase();
                acquirer_provider = acquirer_provider.replace('BANK', 'QRIS');
                console.log("Validate QRIS Provider :", issuer_provider, acquirer_provider);
                // Acquirer And Issuer have to be match
                if (issuer_provider == acquirer_provider){
                    var prevData = details;
                    // Rewrite Details TRX Data From Previous Captured Promo
                    details = promoData;
                    details.payment_details = prevData.payment_details ;
                    details.init_payment = prevData.init_payment;
                    details.payment = prevData.payment;
                    details.payment_received = prevData.payment_received;
                    details.promo_code_active = true;
                    adminFee = parseInt(details.admin_fee);
                    getDenom = parseInt(details.value) * parseInt(details.qty);
                }
            }
        }
    }


    function payment_complete(mode){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        // popup_loading.close();
        var trx_type = details.shop_type;
        console.log('PAYMENT_COMPLETE', now, mode.toUpperCase(), trx_type.toUpperCase());
        //Re-Overwrite receivedPayment into totalPrice for non-cash transaction
        if (details.payment != 'cash') receivedPayment = totalPrice;
        //Put Promo Data Adjustment Here
        do_promo_data_adjustment(mode);
        // Send TRX Shop Data Pending To Host
        if (trx_type == 'shop') _SLOT.start_push_pending_trx_global(JSON.stringify(details));
        transactionInProcess = true;
        // Force Disable All Cancel Button
        hide_all_cancel_button();
        abc.counter = 300;
        my_timer.restart();
        // _SLOT.system_action_log('PAYMENT_TRANSACTION_COMPLETE | ' + mode.toUpperCase(), 'debug')
    }


    function execute_transaction(channel){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
    //        popup_loading.close();
        if (receivedPayment == 0){
            console.log('EMPTY_PAYMENT', now);
            return;
        }
        transactionInProcess = true;
        // Force Disable All Cancel Button
        hide_all_cancel_button();
        var trx_type = details.shop_type;
        switch(trx_type){
            case 'ppob':
                var payload = {
                    msisdn: details.msisdn,
                    product_id: details.product_id,
                    amount: details.value.toString(),
                    reff_no: details.shop_type + details.epoch.toString(),
                    product_category: details.category,
                    payment_type: details.payment,
                    operator: details.operator,
                    product_channel: details.product_channel,
                }
                if (details.ppob_mode=='tagihan'){
                    _SLOT.start_do_pay_ppob(JSON.stringify(payload));
                } else {
                    _SLOT.start_do_topup_ppob(JSON.stringify(payload));
                }
                console.log('DO_PPOB_TRX', now, channel, details.ppob_mode, JSON.stringify(payload))
            break;
            case 'shop':
                attemptCD = details.qty;
                var attempt = details.status.toString();
                var multiply = details.qty.toString();
                _SLOT.start_multiple_eject(attempt, multiply);
                console.log('DO_SHOP_TRX', now, channel, attempt, multiply)
                break;
            case 'topup':
                var provider = details.provider;
                var amount = getDenom.toString();
                var structId = details.shop_type + details.epoch.toString();
                var textMain2 = 'Letakkan kartu prabayar Anda di alat pembaca kartu yang bertanda';
                var textSlave2 = 'Pastikan kartu Anda tetap berada di alat pembaca kartu sampai transaksi selesai';
                var trx_counter_notif = abc.counter.toString();
                switch_frame('source/reader_sign.png', textMain2, textSlave2, 'closeWindow|'+trx_counter_notif, false );
                _SLOT.start_play_audio('keep_card_in_reader_untill_finished');
                console.log('DO_TOPUP_TRX', now, channel, provider, amount, structId);
                perform_do_topup();
                break;
        }
        _SLOT.system_action_log('EXECUTE_TRANSACTION | ' +
                                channel.toUpperCase()  + ' | ' +
                                trx_type.toUpperCase()  + ' | ' +
                                JSON.stringify(details), 'debug')
    }


    function bill_payment_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log("bill_payment_result : ", now, r, receivedPayment, totalPrice, proceedAble);
        var grgFunction = r.split('|')[0]
        var grgResult = r.split('|')[1]
        modeButtonPopup = undefined;
        global_frame.modeAction = "";
        press = '0';
        if (grgFunction == 'RECEIVE_BILL'){
            if (grgResult == 'RECEIVE_BILL|SHOW_BACK_BUTTON') return;
            if (grgResult == "ERROR" || grgResult == "TIMEOUT" || grgResult == "JAMMED"){
                details.process_error = 1;
                do_refund_or_print('cash_device_error');
                return;
            } else if (grgResult == 'COMPLETE'){
                back_button.visible = false;
                _SLOT.stop_bill_receive_note();
                popup_loading.textMain = 'Harap Tunggu Sebentar';
                popup_loading.textSlave = 'Memproses Penyimpanan Uang Anda';
                popup_loading.smallerSlaveSize = true;
                popup_loading.open();
                return;
            } else if (grgResult == 'SERVICE_TIMEOUT'){
                if (receivedPayment > 0){
                    back_button.visible = false;
                    modeButtonPopup = 'retrigger_bill';
                    switch_frame_with_button('source/insert_money.png', 'Masukan Nilai Uang Yang Sesuai Dengan Nominal Transaksi', '(Pastikan Lembar Uang Anda Dalam Keadaan Baik)', 'closeWindow|30', true );
                    return;
                } else {
                    _SLOT.stop_bill_receive_note();
                    exit_with_message(3);
                    return;
                }
            } else if (grgResult == 'EXCEED'){
                modeButtonPopup = 'retrigger_bill';
                _SLOT.start_play_audio('insert_cash_with_good_condition');
                switch_frame_with_button('source/insert_money.png', 'Masukan Nilai Uang Yang Sesuai Dengan Nominal Transaksi', '(Ambil Terlebih Dahulu Uang Anda Sebelum Menekan Tombol)', 'closeWindow|30', true );
                return;
            } else if (grgResult == 'BAD_NOTES'){
                back_button.visible = false;
                modeButtonPopup = 'retrigger_bill';
                _SLOT.start_play_audio('insert_cash_with_good_condition');
                switch_frame_with_button('source/insert_money.png', 'Masukan Nilai Uang Yang Sesuai Dengan Nominal Transaksi', '(Ambil Terlebih Dahulu Uang Anda Sebelum Menekan Tombol)', 'closeWindow|30', true );
                return;
            } else {
// TODO: Back Button
//                back_button.visible = true;
                back_button.visible = true;
                global_frame.close();
                receivedPayment = parseInt(grgResult);
                abc.counter = 300;
                my_timer.restart();
//                _SLOT.start_bill_receive_note();
            }
        } else if (grgFunction == 'STOP_BILL'){
            if(grgResult.indexOf('SUCCESS') > -1){
                if (receivedPayment >= totalPrice){
                    var cashResponse = JSON.parse(r.replace('STOP_BILL|SUCCESS-', ''))
                    details.payment_details = cashResponse;
                    details.payment_received = cashResponse.total;
                    // Overwrite receivedPayment from STOP_BILL result
                    receivedPayment = parseInt(cashResponse.total);
                    console.log("bill_payment_result STOP_SUCCESS : ", now, 'receivedPayment', receivedPayment, 'totalPrice', totalPrice, 'proceedAble', proceedAble);
                    if (proceedAble) payment_complete('bill_acceptor');
                }
            }
        } else if (grgFunction == 'STATUS_BILL'){
            if(grgResult=='ERROR') {
                false_notif('backToMain|10', 'Terjadi Kegagalan Pada Bill Acceptor');
                return;
            }
        }
    }

    function mei_payment_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log("mei_payment_result : ", now, r)
        var meiFunction = r.split('|')[0]
        var meiResult = r.split('|')[1]
        if (meiFunction == 'STACK'){
            if (meiResult == "ERROR"||meiResult == "REJECTED"||meiResult == "OSERROR"){
//                false_notif();
                if (receivedPayment > 0){
                    _SLOT.start_return_es_mei();
                }
            } if (meiResult == 'COMPLETE'){
                _SLOT.start_dis_accept_mei();
                _SLOT.start_store_es_mei();
                back_button.visible = false;
                popup_loading.textMain = 'Harap Tunggu Sebentar'
                popup_loading.textSlave = 'Memproses Penyimpanan Uang Anda'
                popup_loading.open();
//                notif_text = qsTr('Mohon Tunggu, Memproses Penyimpanan Uang Anda.');
            } else {
                receivedPayment = parseInt(meiResult);
            }
        } else if (meiFunction == 'STORE_ES'){
            if(meiResult.indexOf('SUCCESS') > -1) {
                var cashResponse = JSON.parse(r.replace('STORE_ES|SUCCESS-', ''))
                details.payment_details = cashResponse;
                details.payment_received = cashResponse.total;
                if (proceedAble) payment_complete('mei');
            }
        } else if (meiFunction == 'ACCEPT'){
            if(meiResult=='ERROR') {
//                false_notif();
                return;
            }
        }
    }

    function edc_payment_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log("edc_payment_result : ", now, r)
        var edcFunction = r.split('|')[0]
        var edcResult = r.split('|')[1]
        global_frame.close();
        popup_loading.close();
        if (['ERROR'].indexOf(edcResult) > -1){
            next_button_global.visible = false;
            switch_frame_with_button('source/insert_card_dc.png', 'Pembayaran Debit Gagal', 'Mohon Ulangi Transaksi Dalam Beberapa Saat', 'closeWindow|10', true );
            abc.counter = 8;
            return;
        }
        if (edcResult=='SUCCESS') {
            details.payment_details = JSON.parse(r.replace('SALE|SUCCESS|', ''));
            details.payment_received = totalPrice;
            receivedPayment = totalPrice;
            payment_complete('edc');
//            popup_loading.open();
            return;
        }
        if (edcFunction == 'SALE'){
            switch(edcResult){
            case 'SR':
                notif_text = qsTr('Mohon Tunggu, Sedang Mensinkronisasi Ulang.');
                break;
            case 'CI':
                notif_text  = qsTr('Silakan Masukan Kartu Anda Di Slot Tersedia.');
                back_button.visible = true;
                break;
            case 'PI':
                notif_text = qsTr('Kartu Terdeteksi, Silakan Masukkan Kode PIN.');
                back_button.visible = false;
                break;
            case 'DO':
                notif_text = qsTr('Kode Pin Diterima, Menunggu Balasan Sistem.');
                back_button.visible = false;
                break;
            case 'TC':
                notif_text = qsTr('Mohon Maaf, Terjadi Pembatalan Pada Proses Pembayaran.');
                back_button.visible = true;
                break;
            case 'CO':
                notif_text = qsTr('Silakan Ambil Kembali Kartu Anda Dari Slot.');
                back_button.visible = false;
                break;
            case 'CR#EXCEPTION': case 'CR#UNKNOWN':
                notif_text = qsTr('Terjadi Suatu Kesalahan, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                break;
            case 'CR#CARD_ERROR':
                notif_text = qsTr('Terjadi Kesalahan Pada Kartu, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                break;
            case 'CR#PIN_ERROR':
                notif_text = qsTr('Terjadi Kesalahan Pada PIN, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                break;
            case 'CR#SERVER_ERROR':
                notif_text = qsTr('Terjadi Kesalahan Pada Sistem, Transaksi Anda Dibatalkan.');
                back_button.visible = true;
                break;
            case 'CR#NORMAL_CASE':
                notif_text = qsTr('Silakan Ambil Kembali Kartu Anda untuk Melanjutkan Transaksi.');
                back_button.visible = true;
                break;
            default:
                back_button.visible = true;
                break;
            }
        }
    }

    function get_balance(text){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_balance', now, text);
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
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        var provider = details.provider;
        var amount = getDenom.toString();
        var structId = details.shop_type + details.epoch.toString();
        // Only Open Mandiri Denom For Bin-Range 6032 Only
        if (provider.indexOf('Mandiri') > -1 || cardNo.substring(0, 4) == '6032'){
            //Re-define topup amount for C2C Mode
            if (CONF.c2c_mode == 1) amount = details.value;
            _SLOT.start_topup_offline_mandiri(amount, structId);
        } else if (provider.indexOf('BNI') > -1 || cardNo.substring(0, 4) == '7546'){
            _SLOT.start_topup_offline_bni(amount, structId);
        } else if (provider.indexOf('DKI') > -1){
//            _SLOT.start_fake_update_dki(cardNo, amount);
            _SLOT.start_topup_online_dki(cardNo, amount, structId)
        } else if (provider.indexOf('BRI') > -1){
            _SLOT.start_topup_online_bri(cardNo, amount, structId);
        } else if (provider.indexOf('BCA') > -1){
            _SLOT.start_topup_online_bca(cardNo, amount, structId);
        }
    }

    function get_wording(i){
        if (i=='shop') return 'Pembelian Kartu';
        if (i=='topup') return 'TopUp Kartu';
        if (i=='cash') return 'Tunai';
        if (i=='debit') return 'Kartu Debit';
        if (i=='ppob') return 'Pembayaran/Pembelian';
    }

    function details_error_history_push(e){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        details.error_history = details.error_history + "#" + e;
        console.log('Error History', now, details.error_history);
    }

    function initial_process(whoami){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        if (closeTrxSession){
            console.log('initial_process session', closeTrxSession, now, whoami);
            return;
        }
        console.log('initial_process', details.payment, now, whoami);
        proceedAble = true;
        // Add New Bucket to store history error in detail trx data
        details.error_history = '';
        adminFee = parseInt(details.admin_fee);
        getDenom = parseInt(details.value) * parseInt(details.qty);
        // Row 2 Confirmation Content
        info_trx_type.labelContent = details.provider
        if (details.shop_type=='topup') {
            getDenom = parseInt(details.denom);
            info_trx_type.labelContent = details.provider + ' - ' + details.value;
            info_trx_amount.labelContent = 'Rp ' + FUNC.insert_dot(getDenom.toString());
        }
        if (details.shop_type=='ppob') {
            info_trx_price.labelName = 'Nilai Denom';
            if (details.product_channel == 'MDD' && details.operator == 'CASHIN OVO') info_trx_price.visible = false;
        }
        totalPrice = parseInt(getDenom) + parseInt(adminFee);
        var epoch_string = details.epoch.toString();
        uniqueCode = epoch_string.substring(epoch_string.length-9);
        // Unnecessary
//        _SLOT.start_set_payment(details.payment);
        // Change To Get Refunds Details
        _SLOT.start_get_refunds();
        //Validate Action By Payment
        if (allQRProvider.indexOf(details.payment) > -1){
            console.log('generating_qr', details.payment);
            main_title.show_text = 'Ringkasan Transaksi Anda';
            var msg = 'Persiapkan Aplikasi Pembayaran QRIS Pada Gawai Anda!';
            open_preload_notif_qr(msg, 'source/phone_qr_white.png');
//            getDenom = parseInt(details.value) * parseInt(details.qty);
//            totalPrice = getDenom + adminFee;
            qrPayload = {
                trx_id: details.shop_type + details.epoch.toString(),
                amount: totalPrice.toString(),
                mode: details.payment
            }
            _SLOT.start_get_qr_global(JSON.stringify(qrPayload));
//            _SLOT.python_dump(JSON.stringify(qrPayload));
            popup_loading.open();
            return;
        } else if (details.payment == 'cash') {
            open_preload_notif();
//            totalPrice = parseInt(details.value) * parseInt(details.qty);
//            getDenom = totalPrice - adminFee;
            _SLOT.start_set_direct_price(totalPrice.toString());
//            _SLOT.start_accept_mei();
            _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString());
            _SLOT.start_play_audio('insert_cash_with_good_condition');
            back_button.visible = false;
            return;
        } else if (details.payment == 'debit') {
            main_title.show_text = 'Ringkasan Transaksi Anda';
            var edc_waiting_time = '150';
            if (CONF.edc_waiting_time != undefined) edc_waiting_time = CONF.edc_waiting_time;
//            open_preload_notif('Masukkan Kartu Debit dan PIN Anda Pada EDC', 'source/insert_card_new.png');
            switch_frame('source/insert_card_dc.png', 'Masukkan Kartu Debit dan PIN Anda Pada EDC', 'Posisi Mesin EDC Tepat Di Tengah Bawah Layar', 'closeWindow|'+edc_waiting_time, false )
//            getDenom = parseInt(details.value) * parseInt(details.qty);
//            totalPrice = getDenom + adminFee;
            var structId = details.shop_type + details.epoch.toString();
            _SLOT.create_sale_edc_with_struct_id(totalPrice.toString(), structId);
            //Disable general back button for EDC Debit Payment
            back_button.visible = false;
            return;
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
                // console.log('[GLOBAL-PAYMENT]', abc.counter);
                abc.counter -= 1;
                //Force Allowed Back Button For Cash after 240 seconds
                if (details.payment=='cash'){
                    if (abc.counter < (timer_value-240)){
                        back_button.visible = true;
                    }
                }
                notice_no_change.modeReverse = (abc.counter % 2 == 0) ? true : false;
                if (abc.counter == 30 && modeButtonPopup == 'c2c_correction'){
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
                    var amount = getDenom.toString();
                    var structId = details.shop_type + details.epoch.toString();
                    details.timeout_case = 'c2c_correction_timeout'
                    console.log('C2C Auto Force Settlement By Timeout', now, amount, structId);
                    _SLOT.start_mandiri_c2c_force_settlement(amount, structId)
                    modeButtonPopup = undefined;
                    popup_loading.open();
                    return;
                }
                if (popup_refund.visible) popup_refund.showDuration = abc.counter.toString();
                if (popup_confirm.visible) popup_confirm.showDuration = abc.counter.toString();
//                if (abc.counter == 7 && receivedPayment > 0 && !successTransaction){
                // Assumming Only In-Completed Transaction Reach Here
                if (abc.counter == 7){
                    details.receipt_title = 'Transaksi Anda Batal';
                    if (details.payment=='debit') {
                        console.log('[TIMEOUT] Debit Method Payment Detected..!')
//                        refundChannel = 'NONE';
//                        details.refund_channel = refundChannel;
//                        details.refund_status = 'N/A';
//                        details.refund_number = '';
//                        details.refund_amount = '0';
//                        details.timeout_case = 'user_payment_timeout';
//                        details.process_error = 'user_payment_timeout';
//                        details.payment_received = '0';
//                        release_print();
                        if (!refundFeature){
//                            details.pending_trx_code = details.epoch.toString().substr(-6);
                            details.process_error = 1;
                            details_error_history_push('user_payment_timeout_debit')
                            details.payment_error = 1;
                            details.payment_received = receivedPayment.toString();
                            details.pending_trx_code = uniqueCode;
                            console.log('Disable Auto Manual Refund, Generate Pending Code', uniqueCode);
                            release_print('Waktu Transaksi Habis', 'Silakan Ambil Struk Transaksi Anda Dan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                            return;
                        }
                        set_refund_channel('CS_ONLY');
                        do_refund_or_print('user_payment_timeout_debit');
                        return;
                    } else if (details.payment=='cash') {
                        proceedAble = false;
                        _SLOT.stop_bill_receive_note();
                    }
                    if (receivedPayment > 0){
                        //Disable Auto Manual Refund
                        if (!successTransaction){
                            details.process_error = 1;
                            details_error_history_push('user_payment_timeout')
                            details.payment_error = 1;
                            if (!refundFeature){
    //                            details.pending_trx_code = details.epoch.toString().substr(-6);
                                details.payment_received = receivedPayment.toString();
                                details.pending_trx_code = uniqueCode;
                                console.log('Disable Auto Manual Refund, Generate Pending Code', uniqueCode);
                                release_print('Waktu Transaksi Habis', 'Silakan Ambil Struk Transaksi Anda Dan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                                return;
                            }
                        } else {
                            details.receipt_title = 'Transaksi Sukses';
                        }
                        var exceed = validate_cash_refundable();
                        if (exceed == false){
                            details.refund_amount = receivedPayment.toString();
                        } else {
                            details.refund_amount = exceed.toString();
                        }
                        refundChannel = 'CUSTOMER-SERVICE';
                        details.refund_channel = refundChannel;
                        details.refund_status = 'PENDING';
                        details.refund_number = '';
                        details.timeout_case = 'insert_refund_number_timeout'
                        var refundPayload = {
                            amount: details.refund_amount,
                            customer: 'NO_PHONE_NUMBER',
                            reff_no: details.shop_type + details.epoch.toString(),
                            remarks: details,
                            channel: refundChannel,
                            mode: 'not_having_phone_no_for_refund',
                            payment: details.payment
                        }
                        _SLOT.start_trigger_global_refund(JSON.stringify(refundPayload));
                        if (popup_refund.visible) popup_refund.close();
                        console.log('start_trigger_global_refund caused by timeout', JSON.stringify(refundPayload));
                        release_print('Waktu Transaksi Habis', 'Silakan Ambil Struk Transaksi Anda Dan Lapor Petugas');
                    }
                }
                if (abc.counter == 0){
                    console.log('[GLOBAL-PAYMENT]', 'TIMER-TIMEOUT', 'BACK-TO-HOMEPAGE');
                    my_timer.stop();
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
        z: 10
//        visible: !popup_loading.visible && !global_frame.visible && !qr_payment_frame.visible && !popup_refund.visible
        visible: false

        MouseArea{
            anchors.fill: parent
            onClicked: {
                _SLOT.user_action_log('Press Cancel Button "Payment Process"');
                if (press != '0') return;
                press = '1';
                if (useCancelConfirmation){
                    cancel_confirmation.open();
                    press = '0';
                    my_timer.stop();
                    return;
                }
                cancel_transaction('MAIN_FRAME');
            }
        }
    }

    //==============================================================
    //PUT MAIN COMPONENT HERE

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
        closeTrxSession = true;
        popup_loading.open();
        popup_loading.textMain = 'Harap Tunggu Sebentar';
        popup_loading.textSlave = 'Menutup Sesi Bayar Anda';
        back_button.visible = false;
        cancel_button_global.visible = false;
        delay(second*1000, function(){
            popup_loading.close();
            my_timer.stop();
            console.log('[GLOBAL-PAYMENT]', 'WAIT-EXIT-FUNCTION', 'BACK-TO-HOMEPAGE');
            my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
        });
    }

    function open_preload_notif(msg, img){
        press = '0';
        if (msg==undefined) msg = 'Siapkan Uang Anda, Tunggu Hingga Bill Acceptor Siap';
        if (img==undefined) img = 'source/insert_money.png';
        switch_frame(img, msg, 'Lembar Uang Yang Diterima', 'closeWindow', false )
        return;
    }

    function open_preload_notif_qr(msg, img){
        press = '0';
        if (msg==undefined) msg = 'Masukkan Uang Anda Pada Bill Acceptor';
        if (img==undefined) img = 'source/insert_money.png';
        switch_frame(img, msg, '', 'closeWindow', false )
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
        press = '0';
        global_frame.modeAction = "";
        if (modeButtonPopup == 'retrigger_bill') global_frame.modeAction = "RETRIGGER_BILL";
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

    function switch_frame_with_button(imageSource, textMain, textSlave, closeMode, smallerText){
        frameWithButton = true;
        press = '0';
        global_frame.withTimer = false;
        global_frame.modeAction = "";
        if (modeButtonPopup == 'retrigger_bill') global_frame.modeAction = "RETRIGGER_BILL";
        if (closeMode.indexOf('|') > -1){
            var selectedCloseMode = closeMode.split('|')[0];
            var frame_timer = closeMode.split('|')[1];
            global_frame.closeMode = selectedCloseMode;
            global_frame.timerDuration = parseInt(frame_timer);
            global_frame.withTimer = true;
        }
//        if (closeMode == 'closeWindow|30'){
//            global_frame.closeMode = 'closeWindow';
//            global_frame.timerDuration = 30;
//            global_frame.withTimer = true;
//        }
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.open();
    }

    function get_signal_frame(s){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('get_signal_frame', s, now);
        var mode = s.split('|')[0];
        if (mode == 'SELECT_REFUND'){
            refundData = JSON.parse(s.split('|')[1])
        } else if (mode == 'CALLBACK_ACTION'){
            var action = s.split('|')[1];
            switch(action){
            case 'RETRIGGER_BILL':
                if (details.payment=='cash'){
                    _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString());
                    back_button.visible = false;
                }
                modeButtonPopup = undefined;
                global_frame.modeAction = "";
                break;
            case 'PRINT_QR_TIMEOUT_RECEIPT':
                // _SLOT.start_play_audio('transaction_failed');
                if (!refundFeature){
//                            details.pending_trx_code = details.epoch.toString().substr(-6);
                    details.process_error = 1;
                    details_error_history_push('user_payment_timeout_qr')
                    details.payment_error = 1;
                    details.payment_received = receivedPayment.toString();
                    details.pending_trx_code = uniqueCode;
                    details.receipt_title = 'Transaksi Anda Gagal';
                    console.log('User Cancellation Without Refund, Generate Pending Code', uniqueCode);
                    release_print('Waktu Transaksi Habis', 'Silakan Ambil Struk Transaksi Anda Dan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                    return;
                }
                set_refund_channel('CS_ONLY');
                do_refund_or_print('user_payment_timeout_qr');
                qr_payment_frame.cancel(mode);
                break;
            }
        }
    }

    function set_refund_number(n){
       var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
       customerPhone = n;
       details.refund_number = customerPhone;
       console.log('customerPhone as refund_number', customerPhone, now);
   }

    function validate_transaction_success(mode){
        if (mode == undefined) mode = 'Transaksi Sukses';
        details.receipt_title = mode;
        var exceed = validate_cash_refundable();
        if (exceed == false){
            // Cash Exceed Payment Not Found, Just Print Put Receipt
            release_print();
            return;
        }
        refundAmount = exceed;
//        if (message != undefined && message.length > 0){
//            transaction_completeness.textFirst = message[0];
//            transaction_completeness.textSecond = (message[1] != undefined) ? message[1]  : '';
//            transaction_completeness.textThird = (message[2] != undefined) ? message[2]  : '';
//            transaction_completeness.textFourth = (message[3] != undefined) ? message[3]  : '';
//        }
        press = '0';
        my_timer.stop();
        transaction_completeness.mainTitle = mode;
        transaction_completeness.open();
        _SLOT.start_play_audio('please_input_wa_no');
    }

    function cancel_transaction(t){
        if (transactionInProcess){
            console.log('[WARNING] Transaction In Process Not Allowed Cancellation', t);
            return;
        }
        details.receipt_title = 'Transaksi Anda Batal';
        if (details.payment=='cash') {
            console.log('[CANCELLATION] Cash Method Payment Detected..!', t);
            proceedAble = false;
            _SLOT.stop_bill_receive_note();
            if (receivedPayment > 0){
                console.log('[CANCELLATION] User Payment', receivedPayment);
                details.process_error = 1;
                details_error_history_push('user_cancellation')
                details.payment_error = 1;
                if (!refundFeature){
//                            details.pending_trx_code = details.epoch.toString().substr(-6);
                    details.payment_received = receivedPayment.toString();
                    details.pending_trx_code = uniqueCode;
                    console.log('User Cancellation Without Refund, Generate Pending Code', uniqueCode);
                    release_print('Anda Telah Membatalkan Transaksi', 'Silakan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                    return;
                }
                do_refund_or_print('user_cancellation');
                return;
            } else {
                exit_with_message(3);
                return;
            }
        }
        if (details.payment=='debit') {
            console.log('[CANCELLATION] Debit Method Payment Detected..!', t)
//                    refundChannel = 'NONE';
//                    details.refund_channel = refundChannel;
//                    details.refund_status = 'N/A';
//                    details.refund_number = '';
//                    details.refund_amount = '0'
//                    details.timeout_case = 'user_cancellation'
//                    details.process_error = 'user_cancellation';
//                    details.payment_received = '0';
//                    release_print();
//                    console.log('[CANCELLATION] User Payment Debit', receivedPayment);
            details.process_error = 1;
            details_error_history_push('user_cancellation_debit')
            details.payment_error = 1;
            if (!refundFeature){
//                            details.pending_trx_code = details.epoch.toString().substr(-6);
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
                console.log('User Cancellation Without Refund, Generate Pending Code', uniqueCode);
                release_print('Anda Telah Membatalkan Transaksi', 'Silakan Lakukan Transaksi Ulang Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                return;
            }
            set_refund_channel('CS_ONLY');
            do_refund_or_print('user_cancellation_debit');
            return;
        }
        if (allQRProvider.indexOf(details.payment) > -1){
            qr_payment_frame.cancel('USER_CANCEL');
        }
        my_timer.stop();
        console.log('[GLOBAL-PAYMENT]', 'CANCEL-TRANSACTION-FUNCTION', 'BACK-TO-HOMEPAGE', t);
        my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
    }

    MainTitle{
        id: main_title
        anchors.top: parent.top
        anchors.topMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: (totalPrice > receivedPayment) ? 'Silakan Masukkan Uang Anda' : 'Pembayaran Selesai'
        size_: 50
        color_: "white"
        visible: !global_frame.visible && !popup_loading.visible && !qr_payment_frame.visible
    }

    Column{
        width: 900
        height: 500
        anchors.horizontalCenterOffset: 50
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 17

        TextDetailRow{
            id: info_date
            labelName: 'Tanggal'
            labelContent: Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        }

        TextDetailRow{
            id: info_trx_type
            labelName: (details.shop_type=='topup') ? 'Isi Ulang' : 'Pembelian'
        }

        TextDetailRow{
            id: info_trx_amount
            visible: (details.shop_type=='topup')
            labelName: 'Nilai Topup'
            labelContent: 'Rp ' + FUNC.insert_dot(getDenom.toString());
        }

        TextDetailRow{
            id: info_trx_price
            labelName: (details.shop_type=='topup') ? 'Biaya Admin' : 'Harga Satuan'
            labelContent: (details.shop_type=='topup') ? 'Rp ' + FUNC.insert_dot(adminFee.toString()) :  'Rp ' + FUNC.insert_dot(details.value);
        }


        TextDetailRow{
            id: info_promo
            labelName: 'Promo Aktif'
            visible: false
            labelContent: ''
        }

        TextDetailRow{
            id: info_total_payment
            labelName: 'Total Bayar'
            labelContent: 'Rp ' + FUNC.insert_dot(totalPrice.toString())
        }

        TextDetailRow{
            id: info_payment_receive
            labelName: (details.payment=='cash') ? 'Uang Masuk' : 'Jumlah'
            labelContent: (details.payment=='cash') ? 'Rp ' + FUNC.insert_dot(receivedPayment.toString()) : details.qty
        }

    }

    BoxTitle{
        id: notice_no_change
        width: 1200
        height: 120
        visible: (details.payment == 'cash' && !global_frame.visible && (totalPrice > receivedPayment))
        radius: 50
        fontSize: 30
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        title_text: 'SILAKAN MASUKKAN UANG ANDA PADA BILL ACCEPTOR\nPASTIKAN GUNAKAN LEMBAR UANG YANG BAIK'
//        modeReverse: (abc.counter %2 == 0) ? true : false
        boxColor: CONF.frame_color

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
                    back_button.visible = false;
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

    GlobalFrame{
        id: global_frame
        calledFrom: 'general_payment_process'

        CircleButton{
            id: cancel_button_global
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            z:99
//            visible: frameWithButton && (details.payment != 'debit')
            visible: false
            MouseArea{
                anchors.fill: parent
                onClicked: {
//                    console.log('GLOBAL_FRAME_CANCEL_BUTTON', press);
                    _SLOT.user_action_log('Press "BATAL" in Payment Notification');
                    if (press != '0') return;
                    press = '1';
                    if (useCancelConfirmation){
                        press = '0';
                        cancel_confirmation.open();
                        my_timer.stop();
                        return;
                    }
                    cancel_transaction('GLOBAL_FRAME');
                }
            }
        }

        CircleButton{
            id: next_button_global
            anchors.right: parent.right
            anchors.rightMargin: (centerOnlyButton) ? 825 : 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'LANJUT'
            modeReverse: true
            visible: frameWithButton || centerOnlyButton
            blinkingMode: true
            z:99
            MouseArea{
                anchors.fill: parent
                onClicked: {
//                    console.log('GLOBAL_FRAME_NEXT_BUTTON', press);
                    _SLOT.user_action_log('Press "LANJUT"');
                    if (press!='0') return;
                    press = '1'
                    switch(modeButtonPopup){
                    case 'retrigger_bill':                      
                        _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString());
                        back_button.visible = false;
                        modeButtonPopup = undefined;
                        global_frame.modeAction = "";
                        global_frame.close();
//                        open_preload_notif();
                        break;
                    case 'do_topup':
                        perform_do_topup();
                        popup_loading.open();
                        break;
                    case 'reprint':
                        _SLOT.start_reprint_global();
                        popup_loading.open();
                        break;
                    case 'retrigger_card':
                        var attempt = details.status.toString();
                        _SLOT.start_multiple_eject(attempt, attemptCD.toString());
                        centerOnlyButton = false;
                        popup_loading.open();
                        break;
                    case 'check_balance':
                        _SLOT.start_check_card_balance();
                        popup_loading.open();
                        break;
                    case 'c2c_correction':
                        var amount = getDenom.toString();
                        if (CONF.c2c_mode == 1) amount = details.value;
                        var structId = details.shop_type + details.epoch.toString();
                        _SLOT.start_topup_mandiri_correction(amount, structId);
                        popup_loading.open();
                        break;
                    case 'bca_correction':
                        var bca_topup_amount = getDenom.toString();
                        var bca_trxid = details.shop_type + details.epoch.toString();
                        _SLOT.start_retry_topup_online_bca(bca_topup_amount, bca_trxid);
                        popup_loading.open();
                        break;
                    case 'bri_correction':
                        var bri_topup_amount = getDenom.toString();
                        var bri_trxid = details.shop_type + details.epoch.toString();
                        _SLOT.start_retry_topup_online_bri(bri_topup_amount, bri_trxid);
                        popup_loading.open();
                        break;
                    case 'dki_correction':
                        var dki_topup_amount = getDenom.toString();
                        var dki_trxid = details.shop_type + details.epoch.toString();
                        _SLOT.start_retry_topup_online_dki(dki_topup_amount, dki_trxid);
                        popup_loading.open();
                        break;
                    }
                }
            }
        }
    }

    QRPaymentFrame{
        id: qr_payment_frame
        calledFrom: 'general_payment_process'

        CircleButton{
            id: cancel_button_qr
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            visible: parent.visible
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "BATAL" in QR Payment Frame');
                    if (press != '0') return;
                    press = '1';
                    if (useCancelConfirmation){
                        press = '0';
                        cancel_confirmation.open();
                        qr_payment_frame.qrTimer.stop();
                        my_timer.stop();
                        return;
                    }
                    cancel_transaction('QR_FRAME');
//                    _SLOT.start_cancel_qr_global('CANCEL_'+details.shop_type+details.epoch.toString());
//                    qr_payment_frame.cancel('USER_CANCEL');
//                    my_timer.stop();
//                    console.log('[GLOBAL-PAYMENT]', 'CANCEL-BUTTON-QR-FRAME', 'BACK-TO-HOMEPAGE');
//                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }
    }

    PopupInputNoRefund{
        id: popup_refund
        calledFrom: 'general_payment_process'
        handleButtonVisibility: next_button_input_number
//        externalSetValue: refundData
//        visible: true
        z: 99

        CircleButton{
            id: cancel_button_input_number
            visible: popup_refund.visible
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'CUSTOMER\nSERVICE'
            modeReverse: true
            forceColorButton: 'orange'
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    _SLOT.user_action_log('Press "CUSTOMER SERVICE" in Input HP Number');
                    popup_refund.close();
                    details.refund_status = 'AVAILABLE';
                    details.refund_number = '';
                    refundChannel = 'CUSTOMER-SERVICE';
                    details.refund_channel = refundChannel;
                    details.refund_amount = refundAmount.toString();
                    var refundPayload = {
                        amount: details.refund_amount,
                        customer: 'NO_PHONE_NUMBER',
                        reff_no: details.shop_type + details.epoch.toString(),
                        remarks: details,
                        channel: 'CUSTOMER-SERVICE',
                        mode: 'not_having_phone_no_for_refund',
                        payment: details.payment
                    }
                    _SLOT.start_trigger_global_refund(JSON.stringify(refundPayload));
                    console.log('start_trigger_global_refund', now, JSON.stringify(refundPayload));
                    release_print('Pengembalian Dana Tertunda', 'Silakan Ambil Struk Transaksi Anda Dan Lapor Petugas');
                }
            }
        }

        CircleButton{
            id: next_button_input_number
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'SETUJU'
            modeReverse: true
            visible: false
            blinkingMode: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    if (press != '0') return;
                    press = '1';
                    if (refundData==undefined){
                        console.log('MISSING REFUND_DATA', refundData);
                        return;
                    }
                    console.log('REFUND_DATA', JSON.stringify(refundData));
                    refundChannel = refundData.code;
                    refundAmount = refundData.total;
                    details.refund_channel = refundChannel;
                    details.refund_details = refundData;
                    if (['MANUAL'].indexOf(refundChannel) > -1){
                        popup_refund.close();
                        details.refund_status = 'AVAILABLE';
                        details.refund_number = '';
                        details.refund_amount = refundAmount.toString();
                        var refundPayload = {
                            amount: details.refund_amount,
                            customer: 'NO_PHONE_NUMBER',
                            reff_no: details.shop_type + details.epoch.toString(),
                            remarks: details,
                            channel: refundChannel,
                            mode: 'not_having_phone_no_for_refund',
                            payment: details.payment
                        }
                        _SLOT.start_trigger_global_refund(JSON.stringify(refundPayload));
                        console.log('start_trigger_global_refund', now, JSON.stringify(refundPayload));
                        release_print('Pengembalian Dana Tertunda', 'Silakan Ambil Struk Transaksi Anda Dan Lapor Petugas');
                        return;
                    }
                    if (useRefundConfirmation) {
                        press = '0';
                        popup_confirm.phoneNumber = popup_refund.numberInput;
                        popup_confirm.channelName = refundData.name;
                        if (refundData.name == 'C S') popup_confirm.channelName = 'Customer Service';
                        popup_confirm.open()
                        return;
                    }
                    // If Not MANUAL(Cash)
                    customerPhone = popup_refund.numberInput;
                    details.refund_number = customerPhone;
                    _SLOT.user_action_log('Press "LANJUT" Input Number ' + customerPhone + ' For Refund Channel ' + refundChannel);
                    switch(refundMode){
                    case 'payment_cash_exceed':
                        release_print_with_refund(refundAmount.toString());
                        break;
                    case 'user_cancellation':
                        release_print_with_refund(refundAmount.toString(), 'Terjadi Pembatalan Transaksi', 'Silakan Ambil Struk Sebagai Bukti');
                        break;
                    default:
                        release_print_with_refund(refundAmount.toString(), 'Terjadi Kesalahan', 'Silakan Ambil Struk Sebagai Bukti');
                        break;
                    }
                     popup_refund.close();
                    // proceedAble = true;
                    // initial_process();
                }
            }
        }
    }

    PopupConfirmation{
        id: popup_confirm
        calledFrom: 'general_payment_process'
//        handleButtonVisibility: next_button_input_number
//        externalSetValue: refundData
//        visible: true
        z: 100

        CircleButton{
            id: cancel_button_confirmation
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'GANTI'
            modeReverse: true
            visible: parent.visible
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    _SLOT.user_action_log('Press "GANTI" in Refund Confirmation');
                    press = '0';
                    popup_confirm.close();
                }
            }
        }

        CircleButton{
            id: next_button_confirmation
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'SETUJU'
            modeReverse: true
            blinkingMode: true
            visible: parent.visible
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    if (press != '0') return;
                    press = '1';
                    if (refundData==undefined){
                        console.log('MISSING REFUND_DATA', refundData);
                        return;
                    }
                    console.log('REFUND_DATA', JSON.stringify(refundData));
                    refundChannel = refundData.code;
                    refundAmount = refundData.total;
                    details.refund_channel = refundChannel;
                    details.refund_details = refundData;
//                    if (['MANUAL'].indexOf(refundChannel) > -1){
//                        popup_refund.close();
//                        details.refund_status = 'AVAILABLE';
//                        details.refund_number = '';
//                        details.refund_amount = refundAmount.toString();
//                        var refundPayload = {
//                            amount: details.refund_amount,
//                            customer: 'NO_PHONE_NUMBER',
//                            reff_no: details.shop_type + details.epoch.toString(),
//                            remarks: details,
//                            channel: refundChannel,
//                            mode: 'not_having_phone_no_for_refund',
//                            payment: details.payment
//                        }
//                        _SLOT.start_trigger_global_refund(JSON.stringify(refundPayload));
//                        console.log('start_trigger_global_refund', now, JSON.stringify(refundPayload));
//                        release_print('Pengembalian Dana Tertunda', 'Silakan Ambil Struk Transaksi Anda Dan Lapor Petugas');
//                        return;
//                    }
                    // If Not MANUAL(Cash)
                    customerPhone = popup_refund.numberInput;
                    details.refund_number = customerPhone;
                    _SLOT.user_action_log('Press "SETUJU" In Refund Confirmation For ' + customerPhone + ' With Refund Channel ' + refundChannel);
                    switch(refundMode){
                    case 'payment_cash_exceed':
                        release_print_with_refund(refundAmount.toString());
                        break;
                    case 'user_cancellation':
                        release_print_with_refund(refundAmount.toString(), 'Terjadi Pembatalan Transaksi', 'Silakan Ambil Struk Sebagai Bukti');
                        break;
                    default:
                        release_print_with_refund(refundAmount.toString(), 'Terjadi Kesalahan', 'Silakan Ambil Struk Sebagai Bukti');
                        break;
                    }
                    popup_refund.close();
                    popup_confirm.close();
                    hide_all_cancel_button();
                    // proceedAble = true;
                    // initial_process();
                }
            }
        }
    }

    TransactionCompleteness{
        id: transaction_completeness
        z: 101
        textFirst: 'Transaksi Kembalian akan dimasukkan ke Whatsapp Voucher.'
        textSecond: 'Silakan masukkan nomor Whatsapp Anda untuk transaksi kembalian.'
        textThird: 'Anda bisa melakukan transaksi Topup dan Beli Kartu melalui Whatsapp.'
        textFourth: 'Silakan Scan QR untuk melihat Voucher pengembalian Anda di Whatsapp.'
        showWhatAppQR: (CONF.whatsapp_qr !== undefined)
        imageSource: CONF.whatsapp_qr


        CircleButton{
            id: cancel_button_transaction_completeness
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    if (press != '0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "BATAL" in Transaction Completeness');
                    refundChannel = 'CUSTOMER-SERVICE';
                    details.refund_channel = refundChannel;
                    details.refund_status = 'AVAILABLE';
                    details.refund_number = '';
                    details.refund_amount = refundAmount.toString();
//                    _SLOT.start_direct_store_transaction_data(JSON.stringify(details));
                    var refundPayload = {
                        amount: details.refund_amount,
                        customer: 'NO_PHONE_NUMBER',
                        reff_no: details.shop_type + details.epoch.toString(),
                        remarks: details,
                        channel: refundChannel,
                        mode: 'not_having_phone_no_for_refund',
                        payment: details.payment
                    }
                    _SLOT.start_trigger_global_refund(JSON.stringify(refundPayload));
                    console.log('start_trigger_global_refund', now, JSON.stringify(refundPayload));
                    transaction_completeness.close();
                    release_print('Pelanggan YTH.', 'Silakan Ambil Struk Transaksi Anda Dan Periksa Transaksi Anda Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                }
            }
        }

        CircleButton{
            id: next_button_transaction_completeness
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
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    if (press != '0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "LANJUT" in Transaction Completeness');
                    transaction_completeness.close();
                    do_refund_or_print();
                    // proceedAble = true;
                    // initial_process();
                }
            }
        }
    }

    CancelConfirmation{
        id: cancel_confirmation
        z: 102

        CircleButton{
            id: cancel_button_cancel_confirmation
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'TIDAK'
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    _SLOT.user_action_log('Press "TIDAK" in Cancel Confirmation');
                    cancel_confirmation.close();
                    press = '0';
                    my_timer.start();
                    if (allQRProvider.indexOf(details.payment) > -1){
                        qr_payment_frame.qrTimer.start();
                    }
                }
            }
        }

        CircleButton{
            id: next_button_cancel_confirmation
            anchors.right: parent.right
            anchors.rightMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'Y A'
            modeReverse: true
            blinkingMode: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
                    if (press != '0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "Y A" in Cancel Confirmation');
                    cancel_confirmation.close();
                    cancel_transaction('CONFIRM_FRAME');
                }
            }
        }
    }

}

