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
            aliasName: 'debit'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/credit card black.png"
            itemName: "Kartu Debit"
            modeReverse: true
            visible: (listActivePayment.indexOf(aliasName) > -1)
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "DEBIT/CREDIT" Payment Method');
                    do_release_all_set_active(button_debit);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_multi_qr
            aliasName: 'MULTI_QR'
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
                    do_release_all_set_active(button_multi_qr);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_bni
            aliasName: 'bni-qris'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "B N I"
            visible: false
            modeReverse: true
            MouseArea{
                // enabled: (listActivePayment.indexOf('bni-qris') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "BNI" Payment Method');
                    do_release_all_set_active(button_bni);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_bca
            aliasName: 'bca-qris'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "B C A"
            visible: false
            modeReverse: true
            MouseArea{
                // enabled: (listActivePayment.indexOf('bca-qris') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "BCA" Payment Method');
                    do_release_all_set_active(button_bca);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_mdr
            aliasName: 'mdr-qris'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "MANDIRI"
            visible: false
            modeReverse: true
            MouseArea{
                // enabled: (listActivePayment.indexOf('mdr-qris') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "MANDIRI" Payment Method');
                    do_release_all_set_active(button_mdr);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_nobu
            aliasName: 'nobu-qris'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "NOBU"
            visible: false
            modeReverse: true
            MouseArea{
                // enabled: (listActivePayment.indexOf('nobu-qris') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "NOBU" Payment Method');
                    do_release_all_set_active(button_nobu);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_bri
            aliasName: 'bri-qris'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "B R I"
            visible: false
            modeReverse: true
            MouseArea{
                // enabled: (listActivePayment.indexOf('bri-qris') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "BRI" Payment Method');
                    do_release_all_set_active(button_bri);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_jakone
            aliasName: 'jakone'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "JAKONE"
            visible: false
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "JAKONE" Payment Method');
                    do_release_all_set_active(button_jakone);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_gopay
            aliasName: 'gopay'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "GOPAY"
            visible: false
            modeReverse: true
            MouseArea{
                // enabled: (listActivePayment.indexOf('gopay') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "GOPAY" Payment Method');
                    do_release_all_set_active(button_gopay);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_linkaja
            aliasName: 'linkaja'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "LINKAJA"
            modeReverse: true
            visible: false
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "LINKAJA" Payment Method');
                    do_release_all_set_active(button_linkaja);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_duwit
            aliasName: 'duwit'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "DUWIT"
            modeReverse: true
            visible: false
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "DUWIT" Payment Method');
                    do_release_all_set_active(button_duwit);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_dana
            aliasName: 'dana'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "DANA"
            modeReverse: true
            visible: false
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "DANA" Payment Method');
                    do_release_all_set_active(button_dana);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_shopeepay
            aliasName: 'shopeepay'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/phone_qr.png"
            itemName: (VIEW_CONFIG.general_qr=='1') ? 'Q R I S' : "SHOPEEPAY"
            modeReverse: true
            visible: false
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "SHOPEEPAY" Payment Method');
                    do_release_all_set_active(button_shopeepay);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_cash
            aliasName: 'cash'
            width: 359
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/cash black.png"
            itemName: "Tunai"
            modeReverse: true
            visible: (listActivePayment.indexOf(aliasName) > -1)
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "CASH" Payment Method');
                    do_release_all_set_active(button_cash);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

    }


    function do_set_selected_payment(payment){
        switch(calledFrom){
            case 'prepaid_topup_denom':
                if (prepaid_topup_denom.press != '0') return;
                prepaid_topup_denom.press = '1';
                prepaid_topup_denom.get_payment_method_signal(payment);
                break;
            case 'general_shop_card':
                if (general_shop_card.press != '0') return;
                general_shop_card.press = '1';
                general_shop_card.get_payment_method_signal(payment);
                break;
            case 'global_input_number':
                if (global_input_number.press != '0') return;
                global_input_number.press = '1';
                global_input_number.get_payment_method_signal(payment);
                break;
            default:
                break;
        }
        close();
    }


    function do_release_all_set_active(id){
        button_cash.do_release();
        button_debit.do_release();
        button_multi_qr.do_release();
        button_bni.do_release();
        button_bca.do_release();
        button_mdr.do_release();
        button_bri.do_release();
        button_nobu.do_release();
        button_jakone.do_release();
        button_linkaja.do_release();
        button_duwit.do_release();
        button_dana.do_release();
        button_shopeepay.do_release();
        button_gopay.do_release();
        id.set_active();
    }

    function init_payment_channel(){
        button_cash.visible = (listActivePayment.indexOf('cash') > -1);
        button_debit.visible = (listActivePayment.indexOf('debit') > -1);
        // Bank QR
        button_bni.visible = (listActivePayment.indexOf('bni-qris') > -1) && !_qrMultiEnable;
        button_bca.visible = (listActivePayment.indexOf('bca-qris') > -1) && !_qrMultiEnable;
        button_mdr.visible = (listActivePayment.indexOf('mdr-qris') > -1) && !_qrMultiEnable;
        button_bri.visible = (listActivePayment.indexOf('bri-qris') > -1) && !_qrMultiEnable;
        button_nobu.visible = (listActivePayment.indexOf('nobu-qris') > -1) && !_qrMultiEnable;
        button_jakone.visible = (listActivePayment.indexOf('jakone') > -1) && !_qrMultiEnable;
        // Ewallet QR
        button_gopay.visible = (listActivePayment.indexOf('gopay') > -1) && !_qrMultiEnable;
        button_linkaja.visible = (listActivePayment.indexOf('linkaja') > -1) && !_qrMultiEnable;
        button_duwit.visible = (listActivePayment.indexOf('duwit') > -1) && !_qrMultiEnable;
        button_dana.visible = (listActivePayment.indexOf('dana') > -1) && !_qrMultiEnable;
        button_shopeepay.visible = (listActivePayment.indexOf('shopeepay') > -1) && !_qrMultiEnable;
    }

    function open(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('listActivePayment', now, listActivePayment, _qrMultiEnable);
        console.log('_qrMultiEnable', now, _qrMultiEnable);
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
