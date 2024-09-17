import QtQuick 2.2
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN
//import "config.js" as CONF


Rectangle{
    id:select_payment_qr
    property var title_text: "Pilih Provider QR"
    property bool modeReverse: true
    property var calledFrom: 'prepaid_topup_denom'
    property bool _qrMultiEnable: false
    property var listActivePayment: []
    property var totalEnable: 6
    visible: false
    color: 'transparent'
    height: 350
    width: parseInt(SCREEN_WIDTH)
//    width: 1920
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    MainTitle{
        id: main_text
        visible: parent.visible && !smallHeight
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
        spacing: (parent.width==1920) ? 40 : 20

        SmallSimplyItem {
            id: button_multi_qr
            aliasName: 'MULTI_QR'
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
                    do_release_all_set_active(button_multi_qr);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_bni
            aliasName: 'bni-qris'
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/bni_white_logo.png"
            itemName: "B N I"
            // isActivated: (listActivePayment.indexOf('bni-qris') > -1)
            modeReverse: false
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/bca_white_logo.png"
            itemName: "B C A"
            // isActivated: (listActivePayment.indexOf('bca-qris') > -1)
            modeReverse: false
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/mdr_white_logo.png"
            itemName: "MANDIRI"
            // isActivated: (listActivePayment.indexOf('mdr-qris') > -1)
            modeReverse: false
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/nobu_white_logo.png"
            itemName: "NOBU"
            // isActivated: (listActivePayment.indexOf('nobu-qris') > -1)
            modeReverse: false
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/bri_white_logo.png"
            itemName: "B R I"
            // isActivated: (listActivePayment.indexOf('bri-qris') > -1)
            modeReverse: false
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
            id: button_gopay
            aliasName: 'gopay'
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/gopay_white_logo.png"
            itemName: "GOPAY"
            // isActivated: (listActivePayment.indexOf('gopay') > -1)
            modeReverse: false
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/linkaja_white_logo.png"
            itemName: "Linkaja"
            // isActivated: (listActivePayment.indexOf('linkaja') > -1)
            modeReverse: false
            MouseArea{
                // enabled: (listActivePayment.indexOf('linkaja') > -1)
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/duwit_white_logo.png"
            itemName: "DUWIT"
            // isActivated: (listActivePayment.indexOf('duwit') > -1)
            modeReverse: false
            MouseArea{
                // enabled: (listActivePayment.indexOf('duwit') > -1)
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/dana_white_logo.png"
            itemName: "DANA"
            // isActivated: (listActivePayment.indexOf('dana') > -1)
            modeReverse: false
            MouseArea{
                // enabled: (listActivePayment.indexOf('dana') > -1)
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
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/shopeepay_white_logo.png"
            itemName: "SHOPEEPAY"
            // isActivated: (listActivePayment.indexOf('shopeepay') > -1)
            modeReverse: false
            MouseArea{
                // enabled: (listActivePayment.indexOf('shopeepay') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "SHOPEEPAY" Payment Method');
                    do_release_all_set_active(button_shopeepay);
                    do_set_selected_payment(parent.aliasName);
                }
            }
        }

        SmallSimplyItem {
            id: button_jakone
            aliasName: 'jakone'
            width: 200
            height: 183
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/qr_logo/jakone_white_logo.png"
            itemName: "JAKONE"
            // isActivated: (listActivePayment.indexOf('jakone') > -1)
            modeReverse: false
            MouseArea{
                // enabled: (listActivePayment.indexOf('jakone') > -1)
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('choose "JAKONE" Payment Method');
                    do_release_all_set_active(button_jakone);
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
        button_multi_qr.do_release();
        button_bni.do_release();
        button_bca.do_release();
        button_mdr.do_release();
        button_bri.do_release();
        button_nobu.do_release();
        button_jakone.do_release();
        button_gopay.do_release();
        button_linkaja.do_release();
        button_duwit.do_release();
        button_dana.do_release();
        button_shopeepay.do_release();
        id.set_active();
    }


    function init_payment_channel(){
        // Button Visibility
        button_bni.visible = (listActivePayment.indexOf('bni-qris') > -1);
        button_bca.visible = (listActivePayment.indexOf('bca-qris') > -1);
        button_linkaja.visible = (listActivePayment.indexOf('linkaja') > -1);
        button_duwit.visible = (listActivePayment.indexOf('duwit') > -1);
        button_dana.visible = (listActivePayment.indexOf('dana') > -1);
        button_shopeepay.visible = (listActivePayment.indexOf('shopeepay') > -1);
        button_jakone.visible = (listActivePayment.indexOf('jakone') > -1);
        button_gopay.visible = (listActivePayment.indexOf('gopay') > -1);
        button_mdr.visible = (listActivePayment.indexOf('mdr-qris') > -1);
        button_bri.visible = (listActivePayment.indexOf('bri-qris') > -1);
        button_nobu.visible = (listActivePayment.indexOf('nobu-qris') > -1);
        // Activation Flag
        button_bni.isActivated = button_bni.visible;
        button_bca.isActivated = button_bca.visible;
        button_linkaja.isActivated = button_linkaja.visible;
        button_duwit.isActivated = button_duwit.visible;
        button_dana.isActivated = button_dana.visible;
        button_shopeepay.isActivated = button_shopeepay.visible;
        button_jakone.isActivated = button_jakone.visible;
        button_gopay.isActivated = button_gopay.visible;
        button_mdr.isActivated = button_mdr.visible;
        button_bri.isActivated = button_bri.visible;
        button_nobu.isActivated = button_nobu.visible;
    }

    function open(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('listActivePayment', now, listActivePayment);
        init_payment_channel();
        select_payment_qr.visible = true;
    }


    function close(){
        select_payment_qr.visible = false;
    }

}
