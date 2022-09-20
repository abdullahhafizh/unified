import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0

Base{
    id:globalFrame
//        property var globalScreenType: '1'
//        height: (globalScreenType=='2') ? 1024 : 1080
//        width: (globalScreenType=='2') ? 1280 : 1920

    property var calledFrom

    property var textMain: 'Masukkan Kartu Debit dan PIN Anda Pada EDC'
    property var textSlave: 'Posisi Mesin EDC Tepat Di Tengah Bawah Layar'
    property var imageSource: "source/insert_card_dc.png"
    property bool smallerSlaveSize: true
    property bool withTimer: true
    property int textSize: (globalScreenType == '1') ? 40 : 35
    property int timerDuration: 5
    property int showDuration: 0
    property var closeMode: 'closeWindow' // 'closeWindow', 'backToMain', 'backToPrev'
    property var specialHandler
    property var modeAction: ""

    logo_vis: !smallHeight
    isHeaderActive: !smallHeight
    isBoxNameActive: false

    visible: false
    opacity: visible ? 1.0 : 0.0
    Behavior on opacity {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutQuad  }
    }

    Rectangle{
        id: overlay_background
        anchors.fill: parent
        color: 'black'
        opacity: .3
    }

    Column{
        id: column
        width: parent.width - 100
        height: 500
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: (globalScreenType == '1') ? 30 : 25
        AnimatedImage  {
            id: original_image
            visible:  (imageSource!='source/insert_card_dc.png')
            width: 300
            height: 300
            scale: 0.9
            anchors.horizontalCenter: parent.horizontalCenter
            source: imageSource
            fillMode: Image.PreserveAspectFit
        }
        GroupBox{
            id: multiple_images_edc
            flat: true
            width: parent.width
            height: 300
            anchors.horizontalCenter: parent.horizontalCenter
            visible: (imageSource=='source/insert_card_dc.png')
            Rectangle {
                color: 'white'
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width
                height: 400
                AnimatedImage{
                    anchors.fill: parent
                    anchors.verticalCenter: parent.verticalCenter
                    source: "source/vm_edc_usage_guideline.gif"
                    scale: 1.2
                    fillMode: Image.PreserveAspectFit
                }
            }

        }
//        ColorOverlay {
//            id: reverse_original_image
//            anchors.fill: original_image
//            source: original_image
//            color: 'white'
//            scale: original_image.scale
//            visible: (imageSource.indexOf('black') > -1)
//        }
        Text{
            text: textMain
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
            font.pixelSize: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
            visible: (imageSource!='source/insert_card_dc.png')
        }
        Text{
            text: textSlave
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
            wrapMode: Text.WordWrap
            font.pixelSize: (smallerSlaveSize) ? textSize-5: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
            visible: (imageSource!='source/insert_card_dc.png')
        }
//        Text{
//            visible:  (imageSource=='source/insert_money.png')
//            text: 'PENTING : Uang Yang Dapat Diterima'
//            horizontalAlignment: Text.AlignHCenter
//            width: parent.width
//            wrapMode: Text.WordWrap
//            font.pixelSize: textSize
//            anchors.horizontalCenter: parent.horizontalCenter
//            font.bold: false
//            color: 'white'
//            verticalAlignment: Text.AlignVCenter
//            font.family:"Ubuntu"
//        }
//        Row{
//            id: group_acceptable_money
//            anchors.horizontalCenter: parent.horizontalCenter
//            visible:  (imageSource=='source/insert_money.png')
//            scale: 1
//            spacing: 16
//            Image{
//                id: img_count_100
//                scale: 0.9
//                source: "source/100rb.png"
//                fillMode: Image.PreserveAspectFit
//            }
//            Image{
//                id: img_count_50
//                scale: 0.9
//                source: "source/50rb.png"
//                fillMode: Image.PreserveAspectFit
//            }
//            Image{
//                id: img_count_20
//                scale: 0.9
//                source: "source/20rb.png"
//                fillMode: Image.PreserveAspectFit
//            }
//            Image{
//                id: img_count_10
//                scale: 0.9
//                source: "source/10rb.png"
//                fillMode: Image.PreserveAspectFit
//            }

//        }
    }

    AnimatedImage  {
        width: 100
        height: 100
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
        anchors.horizontalCenter: parent.horizontalCenter
        scale: 1
        source: 'source/blue_gradient_circle_loading.gif'
        fillMode: Image.PreserveAspectFit
        visible: withTimer && showDuration > 0
        Text{
            id: text_timer_show
            anchors.fill: parent
            text: showDuration
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 25
            color: 'yellow'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
    }

    Timer {
        id: global_frame_timer
        interval: 1000
        repeat: true
        running: parent.visible && withTimer
        onTriggered: {
            // console.log('[GLOBAL-FRAME]', showDuration);
            showDuration -= 1;
            if (showDuration==0) {
                global_frame_timer.stop();
                switch(closeMode){
                case 'backToMain':
                    console.log('[GLOBAL-FRAME]', 'TIMER-TIMEOUT', 'BACK-TO-HOMEPAGE');
                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }));
                    break;
                case 'backToPrev': case 'backToPrevious':
                    my_layer.pop();
                    break;
                default: close();
                    break;
                }
            }
        }
    }

    function open(){
        if (timerDuration < 0) timerDuration = 30;
        console.log('open_frame', textMain, textSlave, imageSource, timerDuration, closeMode, withTimer);
        globalFrame.visible = true;
        showDuration = timerDuration;
        if (withTimer) global_frame_timer.start();
    }

    function close(){
        if (withTimer) global_frame_timer.stop();
        globalFrame.visible = false;
        specialHandler = undefined;
        if (calledFrom != undefined){
            switch(calledFrom){
            case 'general_payment_process':
                general_payment_process.framingSignal('CALLBACK_ACTION|'+modeAction);
                break;
            case 'retry_payment_process':
                retry_payment_process.framingSignal('CALLBACK_ACTION|'+modeAction);
                break;

            }
        }
    }

    function exit_stop(){
        global_frame_timer.stop();
        globalFrame.visible = false;
        specialHandler = undefined;
    }

}
