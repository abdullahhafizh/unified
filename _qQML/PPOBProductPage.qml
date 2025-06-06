import QtQuick 2.2
import QtQuick.Controls 1.3
import "base_function.js" as FUNC

Base{
    id: ppob_product
//        property var globalScreenType: '2'
//        height: (globalScreenType=='2') ? 1024 : 1080
//        width: (globalScreenType=='2') ? 1280 : 1920
    property int timer_value: (VIEW_CONFIG.page_timer * 3)

    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false

    textPanel: 'Pilih Produk'
    property var ppobData
    property bool frameWithButton: false
    property var selectedCategory
    property var selectedOperator
    property var channelMDD: ['CASHIN OVO', 'CASHIN LINKAJA']
    property var adminFee: 1500


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            abc.counter = timer_value;
            my_timer.start();
            popup_loading.open();
            if (ppobData!=undefined) parse_item_category(selectedCategory);
            _SLOT.start_play_audio('choose_item_product');
        }
        if(Stack.status==Stack.Deactivating){
            my_timer.stop()
            loading_view.close()
        }
    }

    Component.onCompleted:{
    }

    Component.onDestruction:{
    }


    function parse_item_category(c){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log('parse_item_category', now, c);
        product_model.clear();
        gridViewPPOB.model = product_model;
        var p = JSON.parse(ppobData)
        for (var i=0;i < p.length;i++){
            if (selectedOperator == undefined){
                if (p[i]['category']==c){
                    var formated_price = 'Rp. ' + FUNC.insert_dot(p[i]['rs_price']) + ',-';
                    var prod_name = p[i]['category'].toUpperCase() + ' - ' + p[i]['operator'] + ' ' + formated_price;
                    var desc = p[i]['description'];
                    var product_channel = (channelMDD.indexOf(p[i]['operator']) > -1) ? 'MDD' : 'DIVA';
                    if (p[i]['product_channel'] !== undefined) product_channel = p[i]['product_channel'];
                    if (['COMBO SAKTI'].indexOf(p[i]['category'].toUpperCase()) > -1 ) {
                        prod_name = p[i]['operator'].toUpperCase();
                        desc = 'Siapkan Kode Pembayaran Telkomsel Anda';
                        product_channel = 'DIVA';
                    }
                    if (['TAGIHAN', 'TAGIHAN AIR'].indexOf(p[i]['category'].toUpperCase()) > -1 ) {
                        prod_name = p[i]['category'].toUpperCase() + ' - ' + p[i]['description'];
                        desc = 'Plus Biaya Admin ' + formated_price;
                    }
                    if (['VOUCHER', 'ZAKAT', 'PAKET INTERNET', 'UANG ELEKTRONIK', 'GAME', 'OJEK ONLINE', 'PULSA', 'LISTRIK'].indexOf(p[i]['category'].toUpperCase()) > -1 ) {
                        prod_name = p[i]['description'];
                        desc = 'Rp. ' + FUNC.insert_dot(p[i]['rs_price']) + ',-';
                    }
                    var clean_operator = FUNC.strip(p[i]['operator'].toLowerCase());
                    var operator_logo = 'source/ppob_operator/'+clean_operator+'.png';
                    var clean_category = FUNC.strip(p[i]['category'].toLowerCase());
                    var category_logo = 'source/ppob_category/'+clean_category+'.png';
                    if (product_channel == 'MDD'){
                        desc = desc + ' - Admin Fee ' + adminFee.toString()+ ' IDR';
                        if (channelMDD.indexOf(p[i]['operator']) > -1){
                            var denom = parseInt(p[i]['rs_price']) - parseInt(adminFee);
                            var formatted_denom = FUNC.insert_dot(denom.toString());
                            var formatted_admin = FUNC.insert_dot(adminFee.toString());
                            desc = 'Saldo Diterima (Rp. ' + formatted_denom + ',-) Dikurangi Biaya Admin (Rp. ' +formatted_admin+ ',-)';
                            if (p[i]['operator']=='CASHIN OVO') desc = 'Saldo OVO Cash Anda Akan Dipotong Biaya Admin (Rp. ' +formatted_admin+ ',-)';
                        }
                    }
                    product_model.append({
                                        'ppob_name': prod_name,
                                        'ppob_desc': desc,
                                        'ppob_price': formated_price,
                                        'ppob_operator_logo': operator_logo,
                                        'ppob_category_logo': category_logo,
                                        'ppob_product_channel': product_channel,
                                        'raw': p[i]
                                    });
                }
            } else {
                if (p[i]['category']==c && p[i]['operator'] == selectedOperator){
                    formated_price = 'Rp. ' + FUNC.insert_dot(p[i]['rs_price']) + ',-';
                    prod_name = p[i]['category'].toUpperCase() + ' - ' + p[i]['operator'] + ' ' + formated_price;
                    desc = p[i]['description'];
                    product_channel = (channelMDD.indexOf(p[i]['operator']) > -1) ? 'MDD' : 'DIVA';
                    if (p[i]['product_channel'] !== undefined) product_channel = p[i]['product_channel'];
                    if (['COMBO SAKTI'].indexOf(p[i]['category'].toUpperCase()) > -1 ) {
                        prod_name = p[i]['operator'].toUpperCase();
                        desc = 'Siapkan Kode Pembayaran Telkomsel Anda';
                        product_channel = 'DIVA';
                    }
                    if (['TAGIHAN', 'TAGIHAN AIR'].indexOf(p[i]['category'].toUpperCase()) > -1 ) {
                        prod_name = p[i]['category'].toUpperCase() + ' - ' + p[i]['description'];
                        desc = 'Plus Biaya Admin ' + formated_price;
                    }
                    if (['VOUCHER', 'ZAKAT', 'PAKET INTERNET', 'UANG ELEKTRONIK', 'GAME', 'OJEK ONLINE', 'PULSA', 'LISTRIK'].indexOf(p[i]['category'].toUpperCase()) > -1 ) {
                        prod_name = p[i]['description'];
                        desc = 'Rp. ' + FUNC.insert_dot(p[i]['rs_price']) + ',-';
                    }
                    clean_operator = FUNC.strip(p[i]['operator'].toLowerCase());
                    clean_operator = clean_operator.replace('/', '-');
                    operator_logo = 'source/ppob_operator/'+clean_operator+'.png';
                    clean_category = FUNC.strip(p[i]['category'].toLowerCase());
                    category_logo = 'source/ppob_category/'+clean_category+'.png';
                    if (product_channel == 'MDD'){
                        desc = desc + ' - Admin Fee ' + adminFee.toString()+ ' IDR';
                        if (channelMDD.indexOf(p[i]['operator']) > -1){
                            denom = parseInt(p[i]['rs_price']) - parseInt(adminFee);
                            formatted_denom = FUNC.insert_dot(denom.toString());
                            formatted_admin = FUNC.insert_dot(adminFee.toString());
                            desc = 'Saldo Diterima (Rp. ' + formatted_denom + ',-) Dikurangi Biaya Admin (Rp. ' +formatted_admin+ ',-)';
                            if (p[i]['operator']=='CASHIN OVO') desc = 'Saldo OVO Cash Anda Akan Dipotong Biaya Admin (Rp. ' +formatted_admin+ ',-)';
                        }
                    }

                    product_model.append({
                                            'ppob_name': prod_name,
                                            'ppob_desc': desc,
                                            'ppob_price': formated_price,
                                            'ppob_operator_logo': operator_logo,
                                            'ppob_category_logo': category_logo,
                                            'ppob_product_channel': product_channel,
                                            'raw': p[i]
                                        })
                }
            }
        }
        popup_loading.close();
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
        global_frame.closeMode = closeMode;
        global_frame.timerDuration = 5;
        if (closeMode.indexOf('|') > -1){
            var selectedCloseMode = closeMode.split('|')[0];
            var frame_timer = closeMode.split('|')[1];
            global_frame.timerDuration = parseInt(frame_timer);
            global_frame.closeMode = selectedCloseMode;
        }
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
        global_frame.imageSource = imageSource;
        global_frame.textMain = textMain;
        global_frame.textSlave = textSlave;
        global_frame.closeMode = closeMode;
        global_frame.smallerSlaveSize = smallerText;
        global_frame.withTimer = false;
        global_frame.open();
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
        button_text: 'KEMBALI'
        modeReverse: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                _SLOT.user_action_log('press "KEMBALI" In PPOB Product Page');
                my_timer.stop()
                my_layer.pop()
            }
        }
    }

    //==============================================================
    //PUT MAIN COMPONENT HERE

    MainTitle{
        anchors.top: parent.top
        anchors.topMargin: (globalScreenType == '1') ? 150 : (smallHeight) ? 30 : 120
        anchors.horizontalCenter: parent.horizontalCenter
        show_text: 'Pilih Nominal / Item Produk'
        visible: !popup_loading.visible
        size_: (globalScreenType == '1') ? 50 : 45
        color_: "white"

    }

    Item  {
        id: flickable_items
        width: (globalScreenType == '1') ? 1100 : 950
        height: 800
        anchors.verticalCenterOffset: 100
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: (globalScreenType == '1') ? 0 : 75
        anchors.verticalCenter: parent.verticalCenter

        ScrollBarVertical{
            id: vertical_sbar
            flickable: gridViewPPOB
            height: flickable_items.height
            color: "white"
            expandedWidth: 15
        }

        GridView{
            id: gridViewPPOB
            cellHeight: 170
            cellWidth: (globalScreenType == '1') ? 1010 : 810
            anchors.fill: parent
            flickableDirection: Flickable.VerticalFlick
            contentHeight: 150
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
            delegate: component_ppob
            add: Transition {
                    NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 500 }
                    NumberAnimation { property: "scale"; from: 0; to: 1.0; duration: 500 }
                }
        }

        ListModel {
            id: product_model
        }

        Component{
            id: component_ppob
            LongItemPPOB{
                id: item_ppob;
                text_: ppob_name;
                text2_: ppob_desc;
                logo_: ppob_operator_logo;
                logo2_: ppob_category_logo;
                itemWidth :  (globalScreenType == '1') ? 1000 : 780
                MouseArea{
                    anchors.fill: parent;
                    onClicked: {
                        _SLOT.user_action_log('choose "'+ppob_name+'" PPOB Product');
                        var details = {
                            category: raw.category,
                            operator: raw.operator,
                            description: raw.description,
                            product_id: raw.product_id,
                            rs_price: raw.rs_price,
                            amount: raw.amount,
                            product_channel: ppob_product_channel,
                        }
                        console.log('Set Selected Product Into Input Layer: ', JSON.stringify(details));
                        my_layer.push(global_input_number, {selectedProduct: details, mode: 'PPOB'});
                    }
                }
            }
        }
    }


    Image{
        id: sign_scroll
        scale: (globalScreenType == '1') ? 0.75 : 0.45
        anchors.right: parent.right
        anchors.rightMargin: (globalScreenType == '1') ? 50 : -50
        anchors.verticalCenter: parent.verticalCenter
        source: 'source/scroll_sign.png'
    }

    //==============================================================


    ConfirmView{
        id: confirm_view
        show_text: "Dear Customer"
        show_detail: "Proceed This ?."
        z: 99
        MouseArea{
            id: ok_confirm_view
            x: 668; y:691
            width: 190; height: 50;
            onClicked: {
            }
        }
    }

    NotifView{
        id: notif_view
        isSuccess: false
        show_text: "Dear Customer"
        show_detail: "Please Ensure You have set Your plan correctly."
        z: 99
    }

    LoadingView{
        id:loading_view
        z: 99
        show_text: "Finding Flight..."
    }

    PopupLoading{
        id: popup_loading
    }

    GlobalFrame{
        id: global_frame
    }




}

