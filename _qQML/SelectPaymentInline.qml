import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN
//import "config.js" as CONF


Rectangle{
    id:select_payment_popup
    property var title_text: "Pilih Metode Pembayaran"
    property bool modeReverse: true
    property var calledFrom: 'prepaid_topup_denom'
    property bool _qrMultiEnable: false
    property var listActivePayment: []
    property var totalEnable: 6
    visible: false
    color: 'transparent'
    height: 350
    width: parseInt(SCREEN_WIDTH)
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    MainTitle{
        id: main_text
        anchors.top: parent.top
        anchors.topMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: title_text
        size_: (parent.width==1920) ? 50 : 40
        color_: VIEW_CONFIG.text_color
    }

    Row{
        id: row_button
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        height: 300
        anchors.verticalCenterOffset: 50
        spacing: (parent.width==1920) ? 50 : 20

        SmallSimplyItem {
            id: button_debit
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/credit card black.png"
            itemName: "Kartu Debit"
            modeReverse: true
            visible: (listActivePayment.indexOf('debit') > -1)
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "DEBIT/CREDIT" Payment Method');
                    var payment = 'debit';
                    do_release_all_set_active(button_debit);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_multi_qr
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: 'Q R I S'
            modeReverse: true
            visible: _qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "MULTI_QR" Payment Method');
                    var payment = 'MULTI_QR';
                    do_release_all_set_active(button_multi_qr);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_cash
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/cash black.png"
            itemName: "Tunai"
            modeReverse: true
            visible: (listActivePayment.indexOf('cash') > -1)
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "CASH" Payment Method');
                    var payment = 'cash';
                    do_release_all_set_active(button_cash);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_ovo
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' :"QR OVO"
            modeReverse: true
            visible: (listActivePayment.indexOf('ovo') > -1) && !_qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "OVO" Payment Method');
                    var payment = 'ovo';
                    do_release_all_set_active(button_ovo);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_linkaja
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "QRIS LinkAja"
            modeReverse: true
            visible: (listActivePayment.indexOf('linkaja') > -1) && !_qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "LINKAJA" Payment Method');
                    var payment = 'linkaja';
                    do_release_all_set_active(button_linkaja);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_duwit
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "QRIS Duwit"
            modeReverse: true
            visible: (listActivePayment.indexOf('duwit') > -1) && !_qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "DUWIT" Payment Method');
                    var payment = 'duwit';
                    do_release_all_set_active(button_duwit);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_dana
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "QRIS Dana"
            modeReverse: true
            visible: (listActivePayment.indexOf('dana') > -1) && !_qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "DANA" Payment Method');
                    var payment = 'dana';
                    do_release_all_set_active(button_dana);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_shopeepay
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "QRIS ShopeePay"
            modeReverse: true
            visible: (listActivePayment.indexOf('shopeepay') > -1) && !_qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "SHOPEEPAY" Payment Method');
                    var payment = 'shopeepay';
                    do_release_all_set_active(button_shopeepay);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }

        SmallSimplyItem {
            id: button_jakone
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "QRIS JakOne"
            modeReverse: true
            visible: (listActivePayment.indexOf('jakone') > -1) && !_qrMultiEnable
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "JAKONE" Payment Method');
                    var payment = 'jakone';
                    do_release_all_set_active(button_jakone);
                    if (calledFrom=='prepaid_topup_denom'){
                        if (prepaid_topup_denom.press != '0') return;
                        prepaid_topup_denom.press = '1';
                        prepaid_topup_denom.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='general_shop_card'){
                        if (general_shop_card.press != '0') return;
                        general_shop_card.press = '1';
                        general_shop_card.get_payment_method_signal(payment);
                    }
                    if (calledFrom=='global_input_number'){
                        if (global_input_number.press != '0') return;
                        global_input_number.press = '1';
                        global_input_number.get_payment_method_signal(payment);
                    }
                }
            }
        }
    }


    function do_release_all_set_active(id){
        button_cash.do_release();
        button_debit.do_release();
        button_multi_qr.do_release();
        button_ovo.do_release();
        button_linkaja.do_release();
        button_duwit.do_release();
        button_dana.do_release();
        button_shopeepay.do_release();
        button_jakone.do_release();
        id.set_active();
    }

    function init_payment_channel(){
        button_cash.visible = (listActivePayment.indexOf('cash') > -1);
        button_debit.visible = (listActivePayment.indexOf('debit') > -1);
        button_ovo.visible = (listActivePayment.indexOf('ovo') > -1) && !_qrMultiEnable;
        button_linkaja.visible = (listActivePayment.indexOf('linkaja') > -1) && !_qrMultiEnable;
        button_duwit.visible = (listActivePayment.indexOf('duwit') > -1) && !_qrMultiEnable;
        button_dana.visible = (listActivePayment.indexOf('dana') > -1) && !_qrMultiEnable;
        button_shopeepay.visible = (listActivePayment.indexOf('shopeepay') > -1) && !_qrMultiEnable;
        button_jakone.visible = (listActivePayment.indexOf('jakone') > -1) && !_qrMultiEnable;
    }

    function open(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('listActivePayment', now, listActivePayment);
        init_payment_channel();
        select_payment_popup.visible = true;
    }


    function close(){
        select_payment_popup.visible = false;
    }


//    Flickable{
//        id: flick_button
//        width: parent.width
//        height: 200
//        anchors.bottom: parent.bottom
//        anchors.bottomMargin: 25
//        anchors.horizontalCenter: notif_rec.horizontalCenter
//        contentHeight: row_button.height
//        contentWidth: row_button.width
//    }


//    CircleButton{
//        id:back_button
//        anchors.left: parent.left
//        anchors.leftMargin: 30
//        anchors.bottom: parent.bottom
//        anchors.bottomMargin: 30
//        button_text: 'BATAL'
//        modeReverse: true
//        MouseArea{
//            anchors.fill: parent
//            onClicked: {
//                _SLOT.user_action_log('press "BATAL" In Select Payment Frame');
//                my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
//            }
//        }
//    }


}
