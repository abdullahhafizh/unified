import QtQuick 2.2
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
//import "screen.js" as SCREEN
//import "config.js" as CONF


Base{
    id: retry_payment_process

//                property var globalScreenType: '2'
//                height: (globalScreenType=='2') ? 1024 : 1080
//                width: (globalScreenType=='2') ? 1280 : 1920
    property int timer_value: (VIEW_CONFIG.page_timer * 3)
    property var press: '0'
    property var details
    property var notif_text: 'Masukkan Uang Tunai Anda Pada Bill Acceptor di bawah'
    property bool successTransaction: false

    property int receivedPayment: 0
    property int pendingPayment: 0
    property int initialPayment: 0

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

    property var pendingCode: ''

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


    signal framingSignal(string str)

    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false

    idx_bg: 0
    imgPanel: 'source/cash black.png'
    textPanel: 'Proses Pembayaran'
    imgPanelScale: .8

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            reset_variables_to_default();
            if (details != undefined) console.log('product details', JSON.stringify(details));
            if (preloadNotif==undefined){
                initial_process('stack_activation');
            } else {
                popup_refund.open('Silakan Masukkan No HP Anda', refundAmount);
                cancel_button_input_number.visible = true;
            }
            modeButtonPopup = 'check_balance';
            abc.counter = timer_value;
            my_timer.start();
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop();
        }
    }

    Component.onCompleted:{
        base.result_balance_qprox.connect(get_balance);
        base.result_sale_edc.connect(edc_payment_result);
        base.result_cd_move.connect(shop_card_result);
        base.result_store_transaction.connect(store_result);
        base.result_sale_print.connect(print_result);
        base.result_topup_qprox.connect(topup_result);
        base.result_store_topup.connect(store_result);
        base.result_bill_receive.connect(bill_payment_result);
        base.result_bill_stop.connect(bill_payment_result);
        base.result_bill_store.connect(bill_payment_result);
        base.result_bill_status.connect(bill_payment_result);
        base.result_get_qr.connect(qr_get_result);
        base.result_check_qr.connect(qr_check_result);
        base.result_trx_ppob.connect(ppob_trx_result);
        base.result_pay_qr.connect(qr_check_result);
        base.result_global_refund_balance.connect(transfer_balance_result);
        base.result_get_refund.connect(get_refund_result);
        base.result_general_payment.connect(execute_transaction);
        framingSignal.connect(get_signal_frame);
    }

    Component.onDestruction:{
        base.result_balance_qprox.disconnect(get_balance);
        base.result_sale_edc.disconnect(edc_payment_result);
        base.result_cd_move.disconnect(shop_card_result);
        base.result_store_transaction.disconnect(store_result);
        base.result_sale_print.disconnect(print_result);
        base.result_topup_qprox.disconnect(topup_result);
        base.result_store_topup.disconnect(store_result);
        base.result_bill_receive.disconnect(bill_payment_result);
        base.result_bill_stop.disconnect(bill_payment_result);
        base.result_bill_store.disconnect(bill_payment_result);
        base.result_bill_status.disconnect(bill_payment_result);
        base.result_get_qr.disconnect(qr_get_result);
        base.result_check_qr.disconnect(qr_check_result);
        base.result_trx_ppob.disconnect(ppob_trx_result);
        base.result_pay_qr.disconnect(qr_check_result);
        base.result_global_refund_balance.disconnect(transfer_balance_result);
        base.result_get_refund.disconnect(get_refund_result);
        base.result_general_payment.disconnect(execute_transaction);
        framingSignal.disconnect(get_signal_frame);

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
            return;
        }
        var refund = JSON.parse(r);
        if (refund.MANUAL == 'AVAILABLE'){
            var now_hour =  parseInt(Qt.formatDateTime(new Date(), "HH"));
            var over_night = parseInt(VIEW_CONFIG.over_night);
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
        initialPayment = 0;
//        receivedPayment = 0;
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
    }

    function do_refund_or_print(error){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        var message_case_refund = 'Terjadi Kegagalan Transaksi, ';
        refundMode = error;
        abc.counter = 120;
        my_timer.restart();
        global_frame.exit_stop();
        // Validation To Get This Condition, payment received, refund feature disabled and not a success trx
//                if (receivedPayment > initialPayment && !refundFeature && !successTransaction){
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
            if (receivedPayment == initialPayment) {
                press = '0';
                switch_frame('source/smiley_down.png', 'Terjadi Kesalahan Mesin, Membatalkan Transaksi Anda', '', 'backToMain', false);
                _SLOT.system_action_log('BILL_DEVICE_ERROR_PAYMENT_NOT_RECEIVED', 'warning');
                abc.counter = 5;
                return;
            }
            details.payment_error = error;
            details.payment_received = receivedPayment.toString();
            refundAmount = receivedPayment;
            message_case_refund = 'Terjadi Kesalahan Mesin,';
            break;
        case 'cash_device_timeout':
            if (receivedPayment == initialPayment) {
                press = '0';
                switch_frame('source/smiley_down.png', 'Waktu Pembayaran Habis, Membatalkan Transaksi Anda', '', 'backToMain', false);
                _SLOT.system_action_log('BILL_DEVICE_TIMEOUT_PAYMENT_NOT_RECEIVED', 'warning');
                abc.counter = 5;
                return;
            }
            details.payment_error = error;
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
        hide_all_cancel_button();
        console.log('release_print', now, title, msg, successTransaction, receivedPayment, initialPayment, totalPrice);
        if (allQRProvider.indexOf(details.payment) > -1){
            if (VIEW_CONFIG.general_qr=='1') details.payment = 'QRIS PAYMENT';
        }
        if (title==undefined || title.length == 0) title = 'Terima Kasih';
        if (msg==undefined || msg.length == 0) msg = 'Silakan Ambil Struk Transaksi Anda';
        if (successTransaction) {
            //Trigger Confirm Promo Here
            if (details.promo_code_active == true){
                var payload = {
                        pid: details.shop_type + details.epoch.toString(),
                        promo: details.promo,
                    }
                _SLOT.start_do_confirm_promo(JSON.stringify(payload));
            }
            if (VIEW_CONFIG.printer_type=='whatsapp'){
                hide_all_cancel_button();
                reset_variables_to_default();
                // Trigger Deposit Update Balance Check
                if (cardNo.substring(0, 4) == '6032'){
                    if (VIEW_CONFIG.c2c_mode == 1) _SLOT.start_check_mandiri_deposit();
                } else if (cardNo.substring(0, 4) == '7546'){
                    _SLOT.start_check_bni_deposit();
                }
                my_layer.push(ereceipt_view, {details:details, retryMode:true});
                return;
            }
            title = 'Pengulangan Transaksi Berhasil';
            if (details.shop_type == 'topup') msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Anda Dari Reader';
            if (details.shop_type == 'shop'){
                msg = 'Silakan Ambil Struk Transaksi Dan Kartu Prepaid Baru Anda';
                _SLOT.start_play_audio('please_take_new_card_with_receipt');
            }
            _SLOT.start_direct_sale_print_global(JSON.stringify(details));
            console.log('release_print', now, title, msg);
            switch_frame('source/take_receipt.png', title, msg, 'backToMain|3', true );
            // Trigger Deposit Update Balance Check
            if (cardNo.substring(0, 4) == '6032'){
                if (VIEW_CONFIG.c2c_mode == 1) _SLOT.start_check_mandiri_deposit();
            } else if (cardNo.substring(0, 4) == '7546'){
                _SLOT.start_check_bni_deposit();
            }
        } else {
            //Do Print If Only Status Payment is Changed Or Force Settlement
            if (parseInt(receivedPayment) > parseInt(initialPayment))
                _SLOT.start_direct_sale_print_global(JSON.stringify(details));
            switch_frame('source/smiley_down.png', title, msg, 'backToMain|'+VIEW_CONFIG.failure_page_timer.toString(), true );
        }
        my_timer.stop();
        reset_variables_to_default();
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
            details.payment_error = 1;
            details.receipt_title = 'Transaksi Anda Gagal';
            _SLOT.start_play_audio('transaction_failed');
            if (!refundFeature){
            // details.pending_trx_code = details.epoch.toString().substr(-6);
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
//                console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
                release_print('Terjadi Kesalahan/Pembatalan Transaksi', 'Silakan Ulangi Transaksi Dalam Beberapa Saat');
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

    function details_error_history_push(e){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        details.error_history = details.error_history + "#" + e;
        console.log('Error History', now, details.error_history);
    }

    function validate_cash_refundable(){
        if (details.payment == 'cash' && receivedPayment > totalPrice){
            return parseInt(receivedPayment - totalPrice);
        }
        return false;
    }

    function qr_check_result(r){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('qr_check_result', now, r);
        var mode = r.split('|')[1]
        var result = r.split('|')[2]
        popup_loading.close();
        if (['NOT_AVAILABLE', 'MISSING_AMOUNT', 'MISSING_TRX_ID', 'ERROR'].indexOf(result) > -1){
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Silakan Coba Lagi Dalam Beberapa Saat', 'backToMain', true )
            return;
        }
        if (['TIMEOUT'].indexOf(result) > -1){
//            switch_frame('source/smiley_down.png', 'Waktu Pembayaran QR Habis', 'Silakan Coba Lagi Dalam Beberapa Saat', 'closeWindow|3', true )
//            set_refund_channel('CS_ONLY');
//            do_refund_or_print('user_payment_timeout_qr');
            return;
        }
        if (result=='SUCCESS'){
            var info = JSON.parse(r.split('|')[3]);
            now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
            console.log('qr_check_result', now, mode, result, JSON.stringify(info));
            qr_payment_frame.success(3)
            details.payment_details = info;
            details.payment = info.provider;
            details.payment_received = details.value.toString();
            receivedPayment = totalPrice;
            payment_complete('QR_PAYMENT');
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
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Silakan Coba Lagi Dalam Beberapa Saat', 'backToMain', true );
            return;
        }
        if (['TIMEOUT'].indexOf(result) > -1){
            switch_frame('source/smiley_down.png', 'Waktu Proses Pembuatan QR Habis', 'Silakan Coba Lagi Dalam Beberapa Saat', 'closeWindow|5', true );
            return;
        }
        var info = JSON.parse(result);
        var qrMode = mode.toUpperCase();
        qr_payment_frame.modeQR = (VIEW_CONFIG.general_qr == '1') ? 'QR Wallet Anda' : qrMode;
        qr_payment_frame.imageSource = info.qr;
//        if (qrMode=='ovo') _SLOT.start_do_pay_ovo_qr(JSON.stringify(qrPayload));
//        if (qrMode=='gopay') _SLOT.start_do_check_gopay_qr(JSON.stringify(qrPayload));
//        if (qrMode=='linkaja') _SLOT.start_do_check_linkaja_qr(JSON.stringify(qrPayload));
        var msg = '*' + details.shop_type.toUpperCase() + ' ' + details.provider + ' Rp. ' + FUNC.insert_dot(details.value)
        if (details.shop_type=='topup') msg = '*Isi Ulang Kartu Prabayar '+ details.provider + ' Rp. ' + FUNC.insert_dot(details.denom) + ' + Biaya Admin Rp. ' + FUNC.insert_dot(adminFee.toString())
        if (details.shop_type=='ppob') {
            msg = msg + ' + Biaya Admin Rp. ' + FUNC.insert_dot(adminFee.toString());
            if (details.ppob_mode=='tagihan') msg = '*' + details.provider + ' Rp. ' + FUNC.insert_dot(details.value) + ' + Biaya Admin Rp. ' + FUNC.insert_dot(adminFee.toString());
        }
        press = '0'
        if (info.payment_time != undefined) qr_payment_frame.timerDuration = parseInt(info.payment_time);
        var qr_payment_id = details.shop_type+details.epoch.toString();
        qr_payment_frame.open(msg, qr_payment_id);
    }

    function topup_result(t){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('topup_result', now, t);
        global_frame.close();
        popup_loading.close();
        transactionInProcess = false;
        if (allQRProvider.indexOf(details.payment) > -1) qr_payment_frame.hide();
//        abc.counter = 60;
//        my_timer.restart();
        //========
        if (t.indexOf('TOPUP_ERROR') > -1 || t=='MANDIRI_SAM_BALANCE_EXPIRED'||
                t=='BRI_UPDATE_BALANCE_ERROR'||t.indexOf('BNI_SAM_BALANCE_NOT_SUFFICIENT')> -1){
            if (t=='MANDIRI_SAM_BALANCE_EXPIRED' && VIEW_CONFIG.c2c_mode == 0) _SLOT.start_reset_mandiri_settlement();
//            if (t.indexOf('BNI_SAM_BALANCE_NOT_SUFFICIENT')> -1) {
//                var slot_topup = t.split('|')[1]
//                _SLOT.start_do_topup_deposit_bni(slot_topup);
//                console.log('Trigger Manual Topup BNI By Failed TRX : ', now, slot_topup)
//            }
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Pada Proses Isi Ulang Saldo Prabayar Anda', 'closeWindow|3', true );
        } else if (t=='TOPUP_FAILED_CARD_NOT_MATCH'){
            switch_frame('source/smiley_down.png', 'Terjadi Kesalahan', 'Terdeteksi Perbedaan Kartu Saat Isi Ulang', 'closeWindow|3', true );
        }  else if (t.indexOf('MDR_TOPUP_CORRECTION') > -1){
            // Define View And Set Button Continue Mode
            modeButtonPopup = 'mdr_correction';
            details_error_history_push(t.split('#')[1]);
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow|30', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t.indexOf('BNI_TOPUP_CORRECTION') > -1){
            modeButtonPopup = 'bni_correction';
            details_error_history_push(t.split('#')[1]);
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi/Sesuai', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t.indexOf('BCA_TOPUP_CORRECTION') > -1) {
            modeButtonPopup = 'bca_correction';
            details_error_history_push(t.split('#')[1]);
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t.indexOf('BRI_TOPUP_CORRECTION') > -1) {
            modeButtonPopup = 'bri_correction';
            details_error_history_push(t.split('#')[1]);
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t.indexOf('DKI_TOPUP_CORRECTION') > -1) {
            modeButtonPopup = 'dki_correction';
            details_error_history_push(t.split('#')[1]);
//            console.log('c2c_special_handler', modeButtonPopup);
            switch_frame_with_button('source/smiley_down.png', 'Kartu Tidak Terdeteksi', 'Silakan Angkat dan Tempelkan Kembali Kartu Yang Sama Dengan Sebelumnya', 'closeWindow', true );
            _SLOT.start_play_audio('please_pull_retap_card');
            return
        } else if (t=='MDR_FORCE_SETTLEMENT') {
            details.force_settlement = 1;
            // Must Return Here to Stop Executing Receipt
            return
        } else {
            var output = t.split('|')
            var topupResponse = output[0]
            var result = JSON.parse(output[1]);
            if (topupResponse=='0000'){
                details.receipt_title = 'Transaksi Sukses';
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
        details.receipt_title = 'Transaksi Anda Gagal';
        _SLOT.start_play_audio('transaction_failed');
        details_error_history_push(t);
        details.process_error = 1;
        details.payment_error = 1;
        if (!refundFeature){
        // details.pending_trx_code = details.epoch.toString().substr(-6);
            details.payment_received = receivedPayment.toString();
            details.pending_trx_code = uniqueCode;
//            console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
            release_print('Terjadi Kesalahan/Pembatalan Transaksi', 'Silakan Ulangi Transaksi Dalam Beberapa Saat');
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
//            console.log('Retry To Store The Data into DB')
        }
    }

    function print_failed_transaction(channelPayment, issue){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('print_failed_transaction', now, channelPayment, issue, receivedPayment, customerPhone, JSON.stringify(details));
        if (issue==undefined) issue = 'BILL_ERROR';
        if (channelPayment=='cash'){
            details.payment_error = issue;
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
//        abc.counter = 60;
//        my_timer.restart();
        if (r=='EJECT|PARTIAL'){
            press = '0';
            attemptCD -= 1;
            switch_frame('source/take_card.png', 'Silakan Ambil Kartu Anda', 'Kemudian Tekan Tombol Lanjut', 'closeWindow|25', true );
            centerOnlyButton = true;
            modeButtonPopup = 'retrigger_card';
            return;
        }
        if (r == 'EJECT|ERROR') {
            details.process_error = 1;
            details.payment_error = 1;
            details.receipt_title = 'Transaksi Anda Gagal';
            _SLOT.start_play_audio('transaction_failed');
            if (!refundFeature){
            // details.pending_trx_code = details.epoch.toString().substr(-6);
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
//                console.log('Release Print Without Refund, Generate Pending Code', uniqueCode);
                release_print('Terjadi Kesalahan/Pembatalan Transaksi', 'Silakan Ulangi Transaksi Dalam Beberapa Saat');
                return;
            }
            do_refund_or_print('card_eject_error');
            return;
        }
        if (r == 'EJECT|SUCCESS') {
            // Move TRX Success Store Here
            successTransaction = true;
            _SLOT.start_store_transaction_global(JSON.stringify(details))
            details.receipt_title = 'Transaksi Sukses';
            if (useTransactionStatusFrame){
                validate_transaction_success('Transaksi Sukses');
                return;
            }
            do_refund_or_print();
            return;
//            switch_frame('source/thumb_ok.png', 'Silakan Ambil Kartu dan Struk Transaksi Anda', 'Terima Kasih', 'backToMain', false )
        }
    }

    function payment_complete(mode){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
    //        popup_loading.close();
        var trx_type = details.shop_type;
        console.log('PAYMENT_COMPLETE', now, mode.toUpperCase(), trx_type.toUpperCase());
        //Re-Overwrite receivedPayment into totalPrice for non-cash transaction
        if (details.payment != 'cash') receivedPayment = totalPrice;
        details.use_pending_code = 1;
        pendingCode = details.pending_trx_code;
        delete details.pending_trx_code;
        delete details.payment_error;
        delete details.process_error;
        // Force Disable All Cancel Button
        hide_all_cancel_button();
        abc.counter = 90;
        my_timer.restart();
//        _SLOT.system_action_log('PAYMENT_TRANSACTION_COMPLETE | ' + mode.toUpperCase(), 'debug')
    }

    function execute_transaction(channel){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
    //        popup_loading.close();
        if (receivedPayment == 0){
            console.log('EMPTY_PAYMENT', now);
            return;
        }
        if (transactionInProcess){
            console.log('Transaction_In_Process', transactionInProcess);
            return;
        }
        transactionInProcess = true;
        // Log Usage Pending Code
        var reff_no = details.shop_type + details.epoch.toString();
        _SLOT.start_use_pending_code(pendingCode, reff_no);
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
                    operator: details.operator
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
                var trxId = details.shop_type + details.epoch.toString();
                _SLOT.start_multiple_eject(trxId, attempt, multiply);
                console.log('DO_SHOP_TRX', now, channel, attempt, multiply)
                break;
            case 'topup':
                var provider = details.provider;
                var amount = getDenom.toString();
                var structId = details.shop_type + details.epoch.toString();
                var textMain2 = 'Pastikan kartu Anda tetap berada di alat pembaca kartu yang bertanda';
                var textSlave2 = 'dan tunggu hingga transaksi isi ulang selesai';
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
        var billFunction = r.split('|')[0]
        var billResult = r.split('|')[1]
        modeButtonPopup = undefined;
        global_frame.modeAction = "";
        press = '0';
        if (billFunction == 'RECEIVE_BILL'){
            if (billResult == 'RECEIVE_BILL|SHOW_BACK_BUTTON') return;
            if (billResult == "ERROR" || billResult == 'JAMMED'){
                details.process_error = 1;
                do_refund_or_print('cash_device_error');
                return;
            } else if (billResult == 'COMPLETE'){
                popup_loading.textMain = 'Harap Tunggu Sebentar';
                popup_loading.textSlave = 'Memproses Penyimpanan Uang Anda';
                back_button.visible = false;
                popup_loading.smallerSlaveSize = true;
                popup_loading.open();
                _SLOT.stop_bill_receive_note(details.shop_type + details.epoch.toString());
                return;
            } else if (billResult == 'SERVICE_TIMEOUT' || billResult == 'TIMEOUT'){
                if (receivedPayment > initialPayment){
                    back_button.visible = false;
                    modeButtonPopup = 'retrigger_bill';
                    switch_frame_with_button('source/insert_money.png', 'Masukkan 1 Lembar Uang Dengan Nilai Yang Sesuai Dengan Nominal Transaksi', '(Pastikan Lembar Uang Anda Dalam Keadaan Baik)', 'closeWindow|30', true );
                    return;
                } else {
                    _SLOT.stop_bill_receive_note(details.shop_type + details.epoch.toString());
                    exit_with_message(VIEW_CONFIG.bill_failure_page_timer);
                    return;
                }
            } else if (billResult == 'EXCEED'){
                modeButtonPopup = 'retrigger_bill';
                switch_frame_with_button('source/insert_money.png', 'Masukkan 1 Lembar Uang Dengan Nilai Yang Sesuai Dengan Nominal Transaksi', '(Ambil Terlebih Dahulu Uang Anda Sebelum Menekan Tombol)', 'closeWindow|30', true );
                return;
            } else if (billResult == 'BAD_NOTES'){
                back_button.visible = false;
                modeButtonPopup = 'retrigger_bill';
                switch_frame_with_button('source/insert_money.png', 'Masukkan 1 Lembar Uang Dengan Nilai Yang Sesuai Dengan Nominal Transaksi', '(Ambil Terlebih Dahulu Uang Anda Sebelum Menekan Tombol)', 'closeWindow|30', true );
                return;
            } else {
                back_button.visible = true;
                global_frame.close();
                receivedPayment = parseInt(billResult);
                abc.counter = 90;
                my_timer.restart();
//                _SLOT.start_bill_receive_note();
            }
        } else if (billFunction == 'STOP_BILL'){
            if(billResult.indexOf('SUCCESS') > -1){
                if (receivedPayment >= totalPrice){
                    details.payment_received = receivedPayment;
                    details.payment_details = receivedPayment.toString();
                    if (r!='STOP_BILL|SUCCESS'){
                        var cashResponse = JSON.parse(r.replace('STOP_BILL|SUCCESS-', ''))
                        details.payment_details = cashResponse;
                        details.payment_received = cashResponse.total;
                        // Overwrite receivedPayment from STOP_BILL result
                        receivedPayment = parseInt(cashResponse.total);
                    }
                    console.log("bill_payment_result STOP_SUCCESS : ", now, 'receivedPayment', receivedPayment, 'totalPrice', totalPrice, 'proceedAble', proceedAble);
                    if (proceedAble) payment_complete('bill_acceptor');
                }
            }
        } else if (billFunction == 'STATUS_BILL'){
            if(billResult=='ERROR') {
                false_notif('backToMain', 'Terjadi Kegagalan Pada Bill Acceptor');
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
            abc.counter = 10;
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
                notif_text  = qsTr('Silakan Masukkan Kartu Anda Di Slot Tersedia.');
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

    function adjust_topup_value(base_amount){
        var free_amount = (VIEW_CONFIG.free_admin_value!==undefined) ? VIEW_CONFIG.free_admin_value : '0';
        var final_amount = parseInt(base_amount) + parseInt(free_amount);
        return final_amount.toString();
    }

    function perform_do_topup(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        var provider = details.provider;
        var amount = getDenom.toString();
        var structId = details.shop_type + details.epoch.toString();
        // Only Open Mandiri Denom For Bin-Range 6032 Only
        if (provider.indexOf('Mandiri') > -1 || cardNo.substring(0, 4) == '6032'){
            //Re-define topup amount for C2C Mode
            if (VIEW_CONFIG.c2c_mode == 1) amount = details.value;
            _SLOT.start_topup_offline_mandiri( adjust_topup_value(amount), structId);
        } else if (provider.indexOf('BNI') > -1 || cardNo.substring(0, 4) == '7546'){
            _SLOT.start_topup_offline_bni( adjust_topup_value(amount), structId);
        } else if (provider.indexOf('DKI') > -1){
            // _SLOT.start_fake_update_dki(cardNo, adjust_topup_value(amount));
            _SLOT.start_topup_online_dki(cardNo, adjust_topup_value(amount), structId)
        } else if (provider.indexOf('BRI') > -1){
            _SLOT.start_topup_online_bri(cardNo, adjust_topup_value(amount), structId);
        } else if (provider.indexOf('BCA') > -1){
            _SLOT.start_topup_online_bca(cardNo, adjust_topup_value(amount), structId);
        }
    }

    function get_wording(i){
        if (i=='shop') return 'Pembelian Kartu';
        if (i=='topup') return 'TopUp Kartu';
        if (i=='cash') return 'Tunai';
        if (i=='debit') return 'Kartu Debit';
        if (i=='ppob') return 'Pembayaran/Pembelian';
    }

    function initial_process(whoami){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        if (closeTrxSession){
            console.log('initial_process session', closeTrxSession, now, whoami);
            return;
        }
        console.log('initial_process', details.payment, now, whoami);
        proceedAble = true;
        adminFee = parseInt(details.admin_fee);
        getDenom = parseInt(details.value) * parseInt(details.qty);
        // Row 2 Confirmation Content
        row2.labelContent = details.provider
        if (details.shop_type=='topup') {
            getDenom = parseInt(details.denom);
            row2.labelContent = details.provider + ' - ' + details.value;
            row6.labelContent = 'Rp ' + FUNC.insert_dot(getDenom.toString());
        }
        initialPayment = receivedPayment;
        totalPrice = parseInt(getDenom) + parseInt(adminFee);
        var epoch_string = details.epoch.toString();
        uniqueCode = epoch_string.substring(epoch_string.length-9);
        // Change To Get Refunds Details
        _SLOT.start_get_refunds();
        // Handle if Payment is completely done before
        console.log('Check Received Payment', receivedPayment, totalPrice);
        //Handle Check Promo active
        if (details.promo_code_active === true) promoCodeActive = true;
        if (initialPayment >= totalPrice){
//            _SLOT.start_set_direct_price_with_current(receivedPayment.toString(), totalPrice.toString());
            payment_complete(details.payment);
            if (details.payment_details == undefined){
                var payment_details = {
                    total: initialPayment.toString(),
                    history: initialPayment.toString()
                };
                details.payment_details = payment_details;
                details.payment_received = initialPayment.toString();
            }
            execute_transaction('RETRY_TRANSACTION');
            return;
        }
        //Validate Action By Payment
        if (allQRProvider.indexOf(details.payment) > -1){
            console.log('generating_qr', details.payment);
            main_title.show_text = 'Ringkasan Transaksi Anda';
            var msg = 'Persiapkan Aplikasi Pembayaran QRIS Pada Gawai Anda!';
            open_preload_notif_qr(msg, 'source/phone_qr.png');
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
            // open_preload_notif();
//            totalPrice = parseInt(details.value) * parseInt(details.qty);
//            getDenom = totalPrice - adminFee;
            init_denom_available_show();
            _SLOT.start_set_direct_price_with_current(receivedPayment.toString(), totalPrice.toString());
            _SLOT.start_bill_receive_note(details.shop_type + details.epoch.toString());
            _SLOT.start_play_audio('insert_cash_with_good_condition');
            back_button.visible = false;
            return;
        } else if (details.payment == 'debit') {
            main_title.show_text = 'Ringkasan Transaksi Anda';
            var edc_waiting_time = '150';
            if (VIEW_CONFIG.edc_waiting_time != undefined) edc_waiting_time = VIEW_CONFIG.edc_waiting_time;
//            open_preload_notif('Masukkan Kartu Debit dan PIN Anda Pada EDC', 'source/insert_card_new.png');
            switch_frame('source/insert_card_dc.png', 'Masukkan Kartu Debit dan PIN Anda Pada EDC', 'Posisi Mesin EDC Tepat Di Tengah Bawah Layar', 'closeWindow|'+edc_waiting_time, false )
            _SLOT.start_play_audio('follow_payment_instruction');
//            getDenom = parseInt(details.value) * parseInt(details.qty);
//            totalPrice = getDenom + adminFee;
            var structId = details.shop_type + details.epoch.toString();
            _SLOT.create_sale_edc_with_struct_id(totalPrice.toString(), structId);
            //Disable general back button for EDC Debit Payment
            back_button.visible = false;
            return;
        }

    }

    function init_denom_available_show(){
        img_denom_100K.visible = (totalPrice >= 100000);
        img_denom_50K.visible = (totalPrice == 50000);
        img_denom_20K.visible = (totalPrice == 20000);
        img_denom_10K.visible = (totalPrice == 10000);
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
                // console.log('[RETRY-PAYMENT]', 'receivedPayment', receivedPayment, 'initialPayment', initialPayment);
                // console.log(' --> totalPrice', totalPrice, 'successTransaction', successTransaction, abc.counter);
                abc.counter -= 1;
                //Force Allowed Back Button For Cash after 240 seconds
                if (details.payment=='cash'){
                    if (abc.counter < (timer_value-240)){
                        back_button.visible = true;
                    }
                }
                notice_cash_payment.modeReverse = (abc.counter % 2 == 0) ? true : false;
                if (abc.counter == 30 && modeButtonPopup == 'mdr_correction'){
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
                // Assumming Only In-Completed Transaction Reach Here
                if (abc.counter == 7){
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
//                        set_refund_channel('CS_ONLY');
//                        do_refund_or_print('user_payment_timeout_debit');
                        return;
                    } else if (details.payment=='cash') {
                        proceedAble = false;
                        if (initialPayment < totalPrice) _SLOT.stop_bill_receive_note();
                    }
                    if (receivedPayment == initialPayment){
                        exit_with_message(VIEW_CONFIG.bill_failure_page_timer);
                        return;
                    } else if (receivedPayment >= initialPayment){
                        //Disable Auto Manual Refund
                        if (!successTransaction){
                            details.process_error = 1;
                            details.payment_error = 1;
                            if (!refundFeature){
    //                            details.pending_trx_code = details.epoch.toString().substr(-6);
                                details.payment_received = receivedPayment.toString();
                                details.pending_trx_code = uniqueCode;
    //                            console.log('Disable Auto Manual Refund, Generate Pending Code', uniqueCode);
                                release_print('Waktu Transaksi Habis', 'Silakan Ulangi Transaksi Dalam Beberapa Saat');
                                return;
                            }
                        } else {
                            details.receipt_title = 'Transaksi Sukses';
                        }
                        refundChannel = 'CUSTOMER-SERVICE';
                        details.refund_channel = refundChannel;
                        details.refund_status = 'PENDING';
                        details.refund_number = '';
                        var exceed = validate_cash_refundable();
                        if (exceed == false){
                            details.refund_amount = receivedPayment.toString();
                        } else {
                            details.refund_amount = exceed.toString();
                        }
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
                        release_print('Pengembalian Dana Tertunda', 'Silakan Ambil Struk Transaksi Anda Dan Lapor Petugas');
                    }
                }
                if (abc.counter == 0){
                    console.log('[RETRY-PAYMENT]', 'TIMER-TIMEOUT', 'BACK-TO-HOMEPAGE');
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
        visible: !transactionInProcess && receivedPayment < totalPrice && VIEW_CONFIG.bill_type !== 'NV'

//        visible: !popup_loading.visible && !global_frame.visible && !qr_payment_frame.visible && !popup_refund.visible

        MouseArea{
            anchors.fill: parent
            onClicked: {
                // Add Extra Handling
                if (receivedPayment >= totalPrice){
                    back_button.visible = false;
                    return;
                }
                if (press != '0') return;
                press = '1';
                _SLOT.user_action_log('Press Cancel Button "Payment Process"');
                if (receivedPayment == initialPayment){
                    if (details.payment=='cash') {
                        _SLOT.stop_bill_receive_note();
                        exit_with_message(VIEW_CONFIG.bill_failure_page_timer);
                    } else {
                        exit_with_message(VIEW_CONFIG.failure_page_timer);
                    }
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
        popup_loading.textMain = 'Menutup Sesi Pembayaran Anda';
        popup_loading.textSlave = 'Anda Tetap Dapat Melanjutkan Transaksi Dari Kode Ulang Yang Tertera Pada Struk';
        back_button.visible = false;
        cancel_button_global.visible = false;
        delay(second*1000, function(){
            popup_loading.close();
            my_timer.stop();
            console.log('[RETRY-PAYMENT]', 'EXIT-MESSAGE-FUNCTION', 'BACK-TO-HOMEPAGE');
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
        if (global_frame.closeMode=='backToMain') my_timer.stop();
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
        global_frame.closeMode = closeMode;
        global_frame.timerDuration = 5;
        if (closeMode.indexOf('|') > -1){
            var selectedCloseMode = closeMode.split('|')[0];
            var frame_timer = closeMode.split('|')[1];
            global_frame.timerDuration = parseInt(frame_timer);
            global_frame.closeMode = selectedCloseMode;
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
//                set_refund_channel('CS_ONLY');
//                do_refund_or_print('user_payment_timeout_qr');
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
//        if (message != undefined && message.length > 0){
//            exceed_payment_transaction.textFirst = message[0];
//            exceed_payment_transaction.textSecond = (message[1] != undefined) ? message[1]  : '';
//            exceed_payment_transaction.textThird = (message[2] != undefined) ? message[2]  : '';
//            exceed_payment_transaction.textFourth = (message[3] != undefined) ? message[3]  : '';
//        }
        refundAmount = exceed;
        press = '0';
        my_timer.stop();
        exceed_payment_transaction.mainTitle = mode;
        exceed_payment_transaction.open();
        _SLOT.start_play_audio('please_input_wa_no');
    }

    function cancel_transaction(t){
        if (transactionInProcess){
            console.log('[WARNING] Transaction In Process Not Allowed Cancellation', t);
            return;
        }
        // Handle Remove Visibility Button CANCEL
        if (VIEW_CONFIG.bill_type == 'NV' && details.payment == 'cash'){
            switch(t){
                case 'GLOBAL_FRAME':
                    cancel_button_global.visible = false;
                break;
                case 'MAIN_FRAME':
                    back_button.visible = false;
                break;
            }
            console.log('[WARNING] Transaction Not Allowed Cancellation', VIEW_CONFIG.bill_type);
            return;
        }
        details.receipt_title = 'Transaksi Anda Batal';
        if (details.payment=='cash') {
            console.log('[CANCELLATION] Cash Method Payment Detected..!', t);
            proceedAble = false;
            if (initialPayment < totalPrice) _SLOT.stop_bill_receive_note();
            if (receivedPayment > initialPayment){
                console.log('[CANCELLATION] User Payment', receivedPayment);
                details.process_error = 1;
                details.payment_error = 1;
                if (!refundFeature){
//                            details.pending_trx_code = details.epoch.toString().substr(-6);
                    details.payment_received = receivedPayment.toString();
                    details.pending_trx_code = uniqueCode;
                    console.log('User Cancellation Without Refund, Generate Pending Code', uniqueCode);
                    release_print('Anda Telah Membatalkan Transaksi', 'Silakan Ambil Struk Transaksi Anda dan Lakukan Instruksi Sesuai Yang Tertera Pada Struk.');
                    return;
                }
                do_refund_or_print('user_cancellation');
                return;
            } else {
                exit_with_message(VIEW_CONFIG.failure_page_timer);
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
            details.payment_error = 1;
            if (!refundFeature){
//                            details.pending_trx_code = details.epoch.toString().substr(-6);
                details.payment_received = receivedPayment.toString();
                details.pending_trx_code = uniqueCode;
                console.log('User Cancellation Without Refund, Generate Pending Code', uniqueCode);
                release_print('Anda Telah Membatalkan Transaksi', 'Silakan Ambil Struk Transaksi Anda dan Lakukan Instruksi Sesuai Yang Tertera Pada Struk.');
                return;
            }
            set_refund_channel('CS_ONLY');
            do_refund_or_print('user_cancellation_debit');
            return;
        }
        my_timer.stop();
        console.log('[RETRY-PAYMENT]', 'CANCEL-TRANSACTION-FUNCTION', 'BACK-TO-HOMEPAGE', t);
        my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
    }


    MainTitle{
        id: main_title
        anchors.top: parent.top
        anchors.topMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Silakan Masukkan Uang Anda'
        size_: 50
        color_: "white"
        visible: !global_frame.visible && !popup_loading.visible && !qr_payment_frame.visible

    }

    Column{
        width: 900
        height: 500
        anchors.horizontalCenterOffset: -100
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20

        TextDetailRow{
            id: row1
            labelName: 'Tanggal'
            labelContent: Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        }

        TextDetailRow{
            id: row2
            labelName: (details.shop_type=='topup') ? 'Isi Ulang' : 'Pembelian'
        }

        TextDetailRow{
            id: row6
            visible: (details.shop_type=='topup')
            labelName: 'Nilai Topup'
            labelContent: 'Rp ' + FUNC.insert_dot(getDenom.toString());
        }

        TextDetailRow{
            id: row3
            labelName: (details.shop_type=='topup') ? 'Biaya Admin' : 'Harga Satuan'
            labelContent: (details.shop_type=='topup') ? 'Rp ' + FUNC.insert_dot(adminFee.toString()) :  'Rp ' + FUNC.insert_dot(details.value);
        }

        TextDetailRow{
            id: row5
            labelName: 'Total Bayar'
            labelContent: 'Rp ' + FUNC.insert_dot(totalPrice.toString())
        }

        TextDetailRow{
            id: row4
            labelName: (details.payment=='cash') ? 'Uang Masuk' : 'Jumlah'
            labelContent: (details.payment=='cash') ? 'Rp ' + FUNC.insert_dot(receivedPayment.toString()) : details.qty
        }

    }

    AnimatedImage  {
        id: original_image
        visible:  notice_cash_payment.visible
        width: 300
        height: 300
        anchors.verticalCenterOffset: -100
        anchors.horizontalCenterOffset: 500
        anchors.verticalCenter: parent.verticalCenter
        scale: 1
        anchors.horizontalCenter: parent.horizontalCenter
        source: 'source/insert_money.png'
        fillMode: Image.PreserveAspectFit
    }

    BoxTitle{
        id: notice_cash_payment
        width: 1200
        height: 120
        visible: (details.payment == 'cash' && !global_frame.visible)
        radius: 50
        fontSize: 30
        border.width: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 200
        anchors.horizontalCenter: parent.horizontalCenter
        title_text: 'SILAKAN MASUKKAN UANG ANDA PADA BILL ACCEPTOR\nPASTIKAN GUNAKAN LEMBAR UANG YANG BAIK'
//        modeReverse: (abc.counter %2 == 0) ? true : false
        boxColor: VIEW_CONFIG.frame_color

    }

    Text {
        text: "Lembar Uang yang diterima"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 150
        anchors.horizontalCenter: parent.horizontalCenter
        horizontalAlignment: Text.AlignHCenter
        color: "white"
        wrapMode: Text.WordWrap
        font.pixelSize: 30
        font.family: "Ubuntu"
        verticalAlignment: Text.AlignVCenter
        visible: notice_cash_payment.visible
    }

    Row{
        id: group_acceptable_money
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
        anchors.horizontalCenter: parent.horizontalCenter
        visible: notice_cash_payment.visible
        scale: 1
        spacing: 15
        Image{
            id: img_denom_100K
            scale: 0.9
            source: "source/100rb.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            id: img_denom_50K
            scale: 0.9
            source: "source/50rb.png"
            fillMode: Image.PreserveAspectFit
        }
        Image{
            id: img_denom_20K
            scale: 0.9
            source: "source/20rb.png"
            fillMode: Image.PreserveAspectFit
            // visible: (['bca'].indexOf(VIEW_CONFIG.theme_name.toLowerCase()) === false )
        }
        Image{
            id: img_denom_10K
            scale: 0.9
            source: "source/10rb.png"
            fillMode: Image.PreserveAspectFit
            // visible: (['bca'].indexOf(VIEW_CONFIG.theme_name.toLowerCase()) === false )
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
        calledFrom: 'retry_payment_process'

        CircleButton{
            id: cancel_button_global
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            z:99
            visible: frameWithButton && (details.payment != 'debit')
            MouseArea{
                anchors.fill: parent
                onClicked: {
//                    console.log('GLOBAL_FRAME_CANCEL_BUTTON', press);
                    if (press != '0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "BATAL" in Payment Notification');
                    if (details.payment=='cash') {
                        console.log('[CANCELLATION] Cash Method Payment Detected..!')
                        proceedAble = false;
                        _SLOT.stop_bill_receive_note(details.shop_type + details.epoch.toString());
                        if (receivedPayment > initialPayment){
                            console.log('[CANCELLATION] User Payment', receivedPayment)
                            do_refund_or_print('user_cancellation');
                            return;
    //                        print_failed_transaction('cash', 'USER_CANCELLATION');
                        }
                    }
                    if (details.payment == 'debit'){
                        console.log('[CANCELLATION] User Payment Debit', receivedPayment);
                        set_refund_channel('');
                        do_refund_or_print('user_cancellation_debit');
                        return;
                    }
                    my_timer.stop();
                    console.log('[RETRY-PAYMENT]', 'CANCEL-BUTTON-GLOBAL-FRAME', 'BACK-TO-HOMEPAGE');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
    //
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
                        modeButtonPopup = undefined;
                        back_button.visible = false;
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
                        var trxId = details.shop_type + details.epoch.toString() + '_' + attempt;
                        _SLOT.start_multiple_eject(trxId, attempt, attemptCD.toString());
                        centerOnlyButton = false;
                        popup_loading.open();
                        break;
                    case 'check_balance':
                        _SLOT.start_check_card_balance();
                        popup_loading.open();
                        break;
                    case 'mdr_correction':
                        var amount = getDenom.toString();
                        if (VIEW_CONFIG.c2c_mode == 1) amount = details.value;
                        var structId = details.shop_type + details.epoch.toString();
                        _SLOT.start_topup_mandiri_correction(amount, structId);
                        popup_loading.open();
                        break;
                    case 'bni_correction':
                        var trxid = details.shop_type + details.epoch.toString();
                        _SLOT.start_topup_bni_correction(getDenom.toString(), trxid);
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
        calledFrom: 'retry_payment_process'

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
                    if (press != '0') return;
                    press = '1';
                    _SLOT.user_action_log('Press "BATAL" in QR Payment Frame');
//                    _SLOT.start_cancel_qr_global('CANCEL_'+details.shop_type+details.epoch.toString());
                    qr_payment_frame.cancel('USER_CANCEL');
                    my_timer.stop();
                    console.log('[RETRY-PAYMENT]', 'CANCEL-BUTTON-QR-FRAME', 'BACK-TO-HOMEPAGE');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }
    }

    PopupInputNoRefund{
        id: popup_refund
        calledFrom: 'retry_payment_process'
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
        calledFrom: 'retry_payment_process'
//        handleButtonVisibility: next_button_input_number
//        externalSetValue: refundData
//        visible: true
        z: 999

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
        id: exceed_payment_transaction
        z: 101
        textFirst: 'Transaksi Kembalian akan dimasukkan ke Whatsapp Voucher.'
        textSecond: 'Silakan masukkan nomor Whatsapp Anda untuk transaksi kembalian.'
        textThird: 'Anda bisa melakukan transaksi Topup dan Beli Kartu melalui Whatsapp.'
        textFourth: 'Silakan Scan QR untuk melihat Voucher pengembalian Anda di Whatsapp.'
        showWhatAppQR: (VIEW_CONFIG.whatsapp_qr !== undefined)
        imageSource: VIEW_CONFIG.whatsapp_qr


        CircleButton{
            id: cancel_button_exceed_payment_transaction
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
                    exceed_payment_transaction.close();
                    release_print('Pelanggan YTH.', 'Silakan Ambil Struk Transaksi Anda Dan Periksa Transaksi Anda Dengan Memasukkan Kode Ulang Yang Tertera Pada Struk.');
                }
            }
        }

        CircleButton{
            id: next_button_exceed_payment_transaction
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
                    exceed_payment_transaction.close();
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
            visible: !transactionInProcess && receivedPayment < totalPrice && VIEW_CONFIG.bill_type !== 'NV'
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

