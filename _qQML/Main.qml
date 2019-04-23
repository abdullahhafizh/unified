import QtQuick 2.4
import QtQuick.Controls 1.2

Rectangle {
    id:base
    width: 1280
    height: 1024
    color: 'transparent'
    property var top_color: "#f03838"
    property var language: "INA"
    property var raw_origin: undefined
    property var raw_destination: undefined
    property var raw_transit: undefined

    //==================================================================================================//
    signal result_get_file_list(string str)
    signal result_get_gui_version(string str)
    signal result_get_kiosk_name(string str)
    signal result_set_plan(string str)
    signal result_create_schedule(string str)
    signal result_create_chart(string str)
    signal result_post_person(string str)
    signal result_create_booking(string str)
    signal result_create_payment(string str)
    signal result_create_print(string str)
    signal result_clear_person(string str)
    signal result_sale_edc(string str)
    signal result_get_device(string str)
    signal result_confirm_schedule(string str)
    signal result_accept_mei(string str)
    signal result_dis_accept_mei(string str)
    signal result_stack_mei(string str)
    signal result_return_mei(string str)
    signal result_store_es_mei(string str)
    signal result_return_es_mei(string str)
    signal result_dispense_cou_mei(string str)
    signal result_float_down_cou_mei(string str)
    signal result_dispense_val_mei(string str)
    signal result_float_down_all_mei(string str)
    signal result_return_status(string str)
    signal result_init_qprox(string str)
    signal result_debit_qprox(string str)
    signal result_auth_qprox(string str)
    signal result_balance_qprox(string str)
    signal result_topup_qprox(string str)
    signal result_ka_info_qprox(string str)
    signal result_online_info_qprox(string str)
    signal result_init_online_qprox(string str)
    signal result_stop_qprox(string str)
    signal result_airport_name(string str)
    signal result_generate_pdf(string str)
    signal result_general(string str)
    signal result_passenger(string str)
    signal result_flight_data_sorted(string str)
    signal result_kiosk_status(string str)
    signal result_price_setting(string str)
    signal result_collect_cash(string str)
    signal result_list_cash(string str)
    signal result_booking_search(string str)
    signal result_reprint(string str)
    signal result_recreate_payment(string str)
    signal result_get_settlement(string str)
    signal result_print_global(string str)
    signal result_process_settlement(string str)
    signal result_void_settlement(string str)
    signal result_check_booking_code(string str)
    signal result_get_boarding_pass(string str)
    signal result_print_boarding_pass(string str)
    signal result_admin_key(string str)
    signal result_wallet_check(string str)


    //==================================================================================================//

    StackView {
        id: my_layer
        anchors.fill: base
//        initialItem: test_view
        initialItem: home_page

        delegate: StackViewDelegate {
            function transitionFinished(properties)
            {
                properties.exitItem.opacity = 1
            }

            pushTransition: StackViewTransition {
                PropertyAnimation {
                    target: enterItem
                    property: "opacity"
                    from: 0
                    to: 1
                }
                PropertyAnimation {
                    target: exitItem
                    property: "opacity"
                    from: 1
                    to: 0
                }
            }
        }
    }

    Component{id: checkin_success
        CheckInSuccess{}
    }

    Component{id: select_seat
        SelectSeatView{}
    }

    Component{id: checkin_page
        CheckInPage{}
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

    Component {id: media_page
        MediaPage{}
    }

    Component {id: coming_soon
        ComingSoon{}
    }

//    Component {id: buy_ticket
//        BuyTicketWebPage{}
//    }

    Component {id: select_ticket
        SelectTicketView{}
    }

    Component {id: select_plan
        SelectPlanView{}
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

    Component {id: global_web_view
        GlobalWebView{}
    }

    Component {id: faq_ina
        FAQPageINA{}
    }

    Component {id: faq_en
        FAQPageEN{}
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


}




