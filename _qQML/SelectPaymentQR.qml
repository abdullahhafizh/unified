import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
import "screen.js" as SCREEN
import "config.js" as CONF


Rectangle{
    id:select_payment_qr
    property var title_text: "Pilih Provider QR"
    property bool modeReverse: true
    property var calledFrom: 'prepaid_topup_denom'
    property bool _cashEnable: false
    property bool _cardEnable: false
    property bool _qrOvoEnable: false
    property bool _qrDanaEnable: false
    property bool _qrGopayEnable: false
    property bool _qrLinkAjaEnable: false
    property bool _qrShopeeEnable: false
    property bool _qrJakoneEnable: false
    property bool _qrBcaEnable: false
    property bool _qrMultiEnable: false
    property var totalEnable: 6
    visible: false
    color: 'transparent'
    height: 350
    width: parseInt(SCREEN.size.width)
//    width: 1920
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
        color_: CONF.text_color
    }

    Row{
        id: row_button
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        height: 300
        anchors.verticalCenterOffset: 50
        spacing: (parent.width==1920) ? 40 : 20

        SmallSimplyItem {
            id: button_cash
            width: 200
            height: 183
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
            width: 200
            height: 183
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
            width: 200
            height: 183
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/ovo_white_logo.png"
            itemName: "O V O"
            isActivated: _qrOvoEnable
            modeReverse: false
            MouseArea{
                enabled: _qrOvoEnable
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
            id: button_bca
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/bca_white_logo.png"
            itemName: "B C A"
            isActivated: _qrBcaEnable
            modeReverse: false
            MouseArea{
                enabled: _qrBcaEnable
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "BCA" Payment Method');
                    var payment = 'bca-qris';
                    do_release_all_set_active(button_bca);
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/linkaja_white_logo.png"
            itemName: "Linkaja"
            isActivated: _qrLinkAjaEnable
            modeReverse: false
            MouseArea{
                enabled: _qrLinkAjaEnable
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
            id: button_gopay
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/gopay_white_logo.png"
            itemName: "GOPAY"
            isActivated: _qrGopayEnable
            modeReverse: false
            MouseArea{
                enabled: _qrGopayEnable
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "GOPAY" Payment Method');
                    var payment = 'gopay';
                    do_release_all_set_active(button_gopay);
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/dana_white_logo.png"
            itemName: "DANA"
            isActivated: _qrDanaEnable
            modeReverse: false
            MouseArea{
                enabled: _qrDanaEnable
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/shopeepay_white_logo.png"
            itemName: "SHOPEEPAY"
            isActivated: _qrShopeeEnable
            modeReverse: false
            MouseArea{
                enabled: _qrShopeeEnable
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/jakone_white_logo.png"
            itemName: "JAKONE"
            isActivated: _qrJakoneEnable
            modeReverse: false
            MouseArea{
                enabled: _qrJakoneEnable
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
        button_bca.do_release();
        button_linkaja.do_release();
        button_gopay.do_release();
        button_dana.do_release();
        button_shopeepay.do_release();
        button_jakone.do_release();
        id.set_active();
    }

    function open(){
        select_payment_qr.visible = true;
    }


    function close(){
        select_payment_qr.visible = false;
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
