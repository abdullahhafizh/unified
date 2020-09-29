import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
import "config.js" as CONF


Base{
    id: card_prepaid_history

//            property var globalScreenType: '1'
//            height: (globalScreenType=='2') ? 1024 : 1080
//            width: (globalScreenType=='2') ? 1280 : 1920
    property int timer_value: 300
    property var press: '0'
    property var cardNo: ''
    property var balance: '0'
    property var bankName: ''
    property var histories: []
    property bool canPrintButton: false

    imgPanel: 'source/cek_saldo.png'
    textPanel: 'History Kartu Prabayar'

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            abc.counter = timer_value;
            my_timer.start();
            popup_loading.open();
            press = '0';
            canPrintButton = false;
            load_history_data();
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop()
        }
    }

    Component.onCompleted:{
    }

    Component.onDestruction:{
    }

    function load_history_data(){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss");
        console.log("load_history_data : ", now);
        press = '0';
        history_model.clear();
        gridViewHistory.model = history_model;
        if (histories.length > 0){
            canPrintButton = true;
            for (var i=0;i < histories.length;i++){
                var row = {
                    'no': i+1,
                    'timestamp': histories[i].date + '\n' +  histories[i].time,
                    'type': histories[i].type,
                    'nominal': histories[i].amount,
                    'last_balance': histories[i].last_balance,
                }
                history_model.append(row);
//                console.log(i, JSON.stringify(row));
            }
        }
        popup_loading.close();
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
                    my_timer.stop()
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }))
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
        button_text: 'CLOSE'
        modeReverse: true
        visible: !popup_loading.visible && !preload_check_card.visible
        MouseArea{
            anchors.fill: parent
            onClicked: {
                _SLOT.user_action_log('Press CLOSE Button "Card Log History"');
                my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }))
            }
        }
    }

    CircleButton{
        id: next_button
        anchors.right: parent.right
        anchors.rightMargin: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'PRINT OUT'
        modeReverse: true
        visible: !popup_loading.visible && canPrintButton
        blinkingMode: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                _SLOT.user_action_log('Press "PRINT OUT"');
                if (press!='0') return;
                press = '1';
                var payload = {
                    card_no: cardNo,
                    last_balance: balance,
                    bank_name: bankName
                }
                _SLOT.start_print_card_history(JSON.stringify(payload));
                my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
            }
        }
    }


    //==============================================================
    //PUT MAIN COMPONENT HERE


    function false_notif(img, msg){
        if (img==undefined) img = 'source/smiley_down.png';
        if (msg==undefined) msg = 'Maaf Sementara Mesin Tidak Dapat Digunakan';
        press = '0';
        switch_frame(img, msg, '', 'backToMain', false )
        return;
    }

    function switch_frame(imageSource, textMain, textSlave, closeMode, smallerText){
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.closeMode = closeMode;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.open();
    }

    MainTitle{
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 175 : 150
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Log Kartu Prepaid ' + bankName + ' ' + cardNo
        visible: !popup_loading.visible
        size_: (globalScreenType == '1') ? 45 : 40
        color_: "white"

    }

    CardHistoryHeader{
        id: header_table_history
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 250 : 225
        anchors.horizontalCenter: parent.horizontalCenter
//        anchors.horizontalCenterOffset: (globalScreenType == '1') ? 0 : 75
        set_width: (globalScreenType == '1') ? 1000 : 800
        set_height: 50
        set_color: 'white'
        set_padding: (globalScreenType == '1') ? 40 : 30
        left_padding: 10
        set_opacity: .7
        set_font_size: (globalScreenType == '1') ? 30 : 25
    }

    Item  {
        id: flickable_items
        width: (globalScreenType == '1') ? 1100 : 950
        height: 750
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 320 : 280
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: (globalScreenType == '1') ? 0 : 75

        ScrollBarVertical{
            id: vertical_sbar
            flickable: gridViewHistory
            height: flickable_items.height
            color: "white"
            expandedWidth: 15
        }

        GridView{
            id: gridViewHistory
            cellHeight: 70
            cellWidth: (globalScreenType == '1') ? 1010 : 810
            anchors.fill: parent
            flickableDirection: Flickable.VerticalFlick
            contentHeight: 60
            contentWidth: (globalScreenType == '1') ? 1000 : 800
            flickDeceleration: 750
            maximumFlickVelocity: 1500
            layoutDirection: Qt.LeftToRight
            boundsBehavior: Flickable.StopAtBounds
            cacheBuffer: 500
            keyNavigationWraps: true
            snapMode: ListView.SnapToItem
            clip: true
            focus: true
            delegate: history_item
            add: Transition {
                    NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 500 }
                    NumberAnimation { property: "scale"; from: 0; to: 1.0; duration: 500 }
                }
        }

        ListModel {
            id: history_model
        }

        Component{
            id: history_item
            CardHistoryContent{
                set_width: (globalScreenType == '1') ? 1000 : 800
                set_height: 50
                set_padding: (globalScreenType == '1') ? 40 : 30
                left_padding: 10
                set_font_size: (globalScreenType == '1') ? 30 : 25
                set_font_color: 'white'
                content_no: no
                content_time: timestamp
                content_type: type
                content_nominal: FUNC.insert_dot(nominal)
                content_balance: FUNC.insert_dot(last_balance)
            }
        }
    }



    //==============================================================


    StandardNotifView{
        id: standard_notif_view
//        visible: true
//        withBackground: false
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
                console.log('alternative button is pressed..!')
                popup_loading.open();
                _SLOT.start_check_card_balance();
                parent.visible = false;
                parent.buttonEnabled = true;
            }
        }
    }

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }

    PreloadCheckCard{
        id: preload_check_card
//        visible: true
        CircleButton{
            id: cancel_button_preload
            anchors.left: parent.left
            anchors.leftMargin: 30
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'BATAL'
            modeReverse: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "BATAL"');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                }
            }
        }

        CircleButton{
            id: next_button_preload
            anchors.right: parent.right
            anchors.rightMargin: 100
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            button_text: 'LANJUT'
            modeReverse: true
            blinkingMode: true
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    _SLOT.user_action_log('Press "LANJUT"');
                    if (press!='0') return;
                    press = '1'
                    popup_loading.open();
                    switch(actionMode){
                    case 'check_balance':
                        _SLOT.start_check_card_balance();
                        break;
                    case 'update_balance_online':
                        _SLOT.start_update_balance_online(bankName);
                        break;
                    case 'get_card_log_history':
                        _SLOT.start_get_card_history(bankName);
                        break;
                    }
                    preload_check_card.close();
                }
            }
        }
    }

}

