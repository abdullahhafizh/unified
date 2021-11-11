import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
import "screen.js" as SCREEN
import "config.js" as CONF


Rectangle{
    id:select_payment_popup
    property var title_text: "Pilih Metode Pembayaran"
    property bool modeReverse: true
    property var calledFrom: 'prepaid_topup_denom'
    property bool _cashEnable: false
    property bool _cardEnable: false
    property bool _qrOvoEnable: false
    property bool _qrDanaEnable: false
    property bool _qrDuwitEnable: false
    property bool _qrLinkAjaEnable: false
    property bool _qrShopeeEnable: false
    property bool _qrJakoneEnable: false
    property bool _qrMultiEnable: false
    property var totalEnable: 6
    visible: true
    color: 'transparent'
    height: 350
    width: parseInt(SCREEN.size.width)
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    MainTitle{
        id: main_text
        anchors.top: parent.top
        anchors.horizontalCenterOffset: 0
        size_: 28
        anchors.topMargin: 0
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: title_text
        color_: CONF.text_color
    }

    Row{
        id: row_button
        width: 940
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenterOffset: 0
        height: 183
        anchors.verticalCenterOffset: 11
        spacing: (parent.width==1920) ? 50 : 20

        SmallSimplyItem {
            id: button_cash
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/cash black.png"
            itemName: "Tunai"
            modeReverse: true
            visible: _cashEnable
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
            id: button_debit
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/credit card black.png"
            itemName: "Kartu Debit"
            modeReverse: true
            visible: _cardEnable
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
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: 'QRIS Payment'
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
            id: button_ovo
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (CONF.general_qr=='1') ? 'QRIS Payment' :"QR OVO"
            modeReverse: true
            visible: _qrOvoEnable && !_qrMultiEnable
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
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (CONF.general_qr=='1') ? 'QRIS Payment' : "QRIS LinkAja"
            modeReverse: true
            visible: _qrLinkAjaEnable && !_qrMultiEnable
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
<<<<<<< HEAD
            id: button_gopay
            width: 300
            height: 150
=======
            id: button_duwit
            width: 359
            height: 183
>>>>>>> develop
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (CONF.general_qr=='1') ? 'QRIS Payment' : "QRIS Duwit"
            modeReverse: true
            visible: _qrDuwitEnable && !_qrMultiEnable
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
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (CONF.general_qr=='1') ? 'QRIS Payment' : "QRIS Dana"
            modeReverse: true
            visible: _qrDanaEnable && !_qrMultiEnable
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
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (CONF.general_qr=='1') ? 'QRIS Payment' : "QRIS ShopeePay"
            modeReverse: true
            visible: _qrShopeeEnable && !_qrMultiEnable
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
            width: 300
            height: 150
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (CONF.general_qr=='1') ? 'QRIS Payment' : "QRIS JakOne"
            modeReverse: true
            visible: _qrJakoneEnable && !_qrMultiEnable
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

    function open(){
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

/*##^##
Designer {
    D{i:0;formeditorZoom:0.66}
}
##^##*/
