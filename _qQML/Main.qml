import QtQuick 2.2
import QtQuick.Controls 1.2
//import "screen.js" as SCREEN


Rectangle {
    id:base
    color: 'transparent'
    property var top_color: "#f03838"
    property var language: "INA"
    property var globalBoxName: ""
    property bool mediaOnPlaying: false
    property int globalWidth: parseInt(SCREEN_WIDTH)
    property int globalHeight: parseInt(SCREEN_HEIGHT)
    width: globalWidth
    height: globalHeight

    property var globalScreenType: (globalWidth==1920) ? '1' : '2'

    //Type 1 : var size = { "width": 1920, "height": 1080};
    //Type 2 : var size = { "width": 1280, "height": 1024};
//        property var globalScreenType: '1'
//        height: (globalScreenType=='2') ? 1024 : 1080
//        width: (globalScreenType=='2') ? 1280 : 1920


    //==================================================================================================//
    signal result_get_file_list(string str)
    signal result_get_gui_version(string str)
    signal result_get_kiosk_name(string str)
    signal result_sale_edc(string str)
    signal result_get_payment(string str)
    signal result_return_status(string str)
    signal result_init_qprox_config(string str)
    signal result_debit_qprox(string str)
    signal result_auth_qprox(string str)
    signal result_balance_qprox(string str)
    signal result_topup_qprox(string str)
    signal result_ka_info_qprox(string str)
    signal result_online_info_qprox(string str)
    signal result_init_online_mandiri(string str)
    signal result_stop_qprox(string str)
    signal result_generate_pdf(string str)
    signal result_general(string str)
    signal result_kiosk_status(string str)
    signal result_price_setting(string str)
    signal result_collect_cash(string str)
    signal result_list_cash(string str)
    signal result_get_settlement(string str)
    signal result_process_settlement(string str)
    signal result_void_settlement(string str)
    signal result_check_booking_code(string str)
    signal result_get_boarding_pass(string str)
    signal result_print_boarding_pass(string str)
    signal result_admin_key(string str)
    signal result_wallet_check(string str)
    signal result_cd_hold(string str)
    signal result_cd_move(string str)
    signal result_cd_stop(string str)
    signal result_product_stock(string str)
    signal result_store_transaction(string str)
    signal result_topup_amount(string str)
    signal result_topup_readiness(string str)
    signal result_sale_print(string str)
    signal result_multiple_eject(string str)
    signal result_store_topup(string str)
    signal result_user_login(string str)
    signal result_kiosk_admin_summary(string str)
    signal result_change_stock(string str)
    signal result_bill_status(string str)
    signal result_bill_receive(string str)
    signal result_bill_stop(string str)
    signal result_bill_store(string str)
    signal result_bill_reject(string str)
    signal result_do_topup_deposit_bni(string str)
    signal result_admin_print(string str)
    signal result_reprint_global(string str)
    signal result_init_bill(string str)
    signal result_activation_bni(string str)
    signal result_cd_readiness(string str)
    signal result_mandiri_settlement(string str)
    signal result_update_app(string str)
    signal result_get_ppob_product(string str)
    signal result_get_payment_setting(string str)
    signal result_sync_ads(string str)
    signal result_check_ppob(string str)
    signal result_trx_ppob(string str)
    signal result_check_trx(string str)
    signal result_get_qr(string str)
    signal result_pay_qr(string str)
    signal result_check_qr(string str)
    signal result_confirm_qr(string str)
    signal result_check_voucher(string str)
    signal result_use_voucher(string str)
    signal result_diva_balance_check(string str)
    signal result_global_refund_balance(string str)
    signal result_update_balance_online(string str)
    signal result_admin_sync_stock(string str)
    signal result_init_check_cd(string str)
    signal result_get_refund(string str)
    signal result_check_online_topup(string str)
    signal result_card_log_history(string str)
    signal result_do_online_topup(string str)
    signal result_general_payment(string str)
    signal result_ppob_check_customer(string str)
    signal result_panel_setting(string str)
    signal result_scanner_read(string str)


    //==================================================================================================//

    StackView {
        id: my_layer
        anchors.fill: base
        initialItem: home_page

        delegate: StackViewDelegate {
            function transitionFinished(properties)
            {
                properties.exitItem.opacity = 1.0
            }

            pushTransition: StackViewTransition {
                PropertyAnimation {
                    target: enterItem
                    property: "opacity"
                    from: 0.0
                    to: 1.0
                }
                PropertyAnimation {
                    target: exitItem
                    property: "opacity"
                    from: 1.0
                    to: 0.0
                }
            }
        }
    }

    Component{id: admin_manage
        AdministratorPage{}
    }

    Component{id: admin_login
        AdministratorLogin{}
    }

    Component{id: topup_prepaid_denom
        PrepaidTopupDenom{}
    }

    Component{id: process_shop
        ProcessShop{}
    }

    Component{id: select_prepaid_provider
        SelectPrepaidProvider{}
    }

    Component{id: shop_prepaid_card
        ShopPrepaidCard{}
    }

    Component{id: check_balance
        CheckPrepaidBalance{}
    }

    Component{id: backdooor_login
        BackDoorLogin{}
    }

    Component{id: test_payment_page
        TestPaymentPage{}
    }

    Component {id: home_page
        HomePage{}  
    }

    Component {id: home_page_event
        HomePageEvent{}
    }

    Loader {
        id: media_page
        sourceComponent: ENABLE_MULTIMEDIA ? NoMediaPage{} : MediaPage{}
    }

    Component {id: no_media_page
        NoMediaPage{}
    }

    Component {id: coming_soon
        ComingSoon{}
    }


    Component {id: input_number
        InputGeneralNumber{}
    }

    Component {id: input_details
        InputDetails{}
    }

    Component {id: select_payment
        SelectPayment{}
    }

    Component {id: loading_view
        LoadingView{}
    }


    Component {id: test_view
        GeneralTemplate{}
    }

    Component {id: reprint_view
        ReprintPage{}
    }

    Component {id: reprint_detail_view
        ReprintDetailPage{}
    }

    Component {id: home_page_tj
        HomePageTJ{}
    }

    Component {id: general_shop_card
        GeneralShopCard{}
    }

    Component {id: general_payment_process
        GeneralPaymentProcess{}
    }

    Component {id: ppob_category
        PPOBCategoryPage{}
    }

    Component {id: ppob_product_operator
        PPOBOperatorPage{}
    }

    Component {id: ppob_product
        PPOBProductPage{}
    }

    Component {id: global_input_number
        GlobalInputNumber{}
    }

    Component {id: card_prepaid_history
        CardPrepaidHistory{}
    }

    Component {id: retry_payment_process
        RetryPaymentProcess{}

    }

    Component {id: ereceipt_view
        ElectronicReceipt{}
    }


}




