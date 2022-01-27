import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC
import "screen.js" as SCREEN
import "config.js" as CONF


Rectangle{
    id:popup_input_otp
    width: parseInt(SCREEN.size.width)
    height: parseInt(SCREEN.size.height)

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    color: 'transparent'
    property var colorMode: "darkgray"
    property bool withBackground: true

    property var calledFrom
    property var handleButtonVisibility
    property var externalSetValue

    property var escapeFunction: 'closeWindow' //['closeWindow', 'backToMain', 'backToPrevious']
    property var press: "0"

    property int minCountInput: 6
    property int maxCountInput: 15
    property var numberInput: ""
    property var pattern: '08'

    property string caseTitle: ""
    property var mainTitleMode: "normal" //normal/center
    property string mainTitle: "Masukkan Kode OTP (Konfirmasi) Dari Administrator"

    visible: false
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: base_overlay
        visible: withBackground
        anchors.fill: parent
        color: CONF.background_color
//        color: 'black'
        opacity: 0.6
    }

    Rectangle{
        id: notif_rec
        width: parent.width
        height: parent.height - 100
//        color: CONF.frame_color
        color: colorMode
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        MainTitle{
            id: main_title
            width: parent.width - 200
            anchors.top: parent.top
            anchors.topMargin: mainTitleMode=="normal" ? 45 : popup_input_otp.height/2
            anchors.horizontalCenter: parent.horizontalCenter
            show_text: caseTitle + mainTitle
            size_: (popup_input_otp.width==1920) ? 50 : 40
            color_: CONF.text_color
        }

        TextRectangle{
            id: text_rectangle
            width: 650
            height: 100
            anchors.top: parent.top
            anchors.topMargin: 160
            anchors.horizontalCenter: parent.horizontalCenter
            borderColor: CONF.text_color
            visible: !manualMethod.isSelected
        }

        TextInput {
            id: inputText
            anchors.centerIn: text_rectangle;
            text: numberInput
    //        text: "INPUT NUMBER 1234567890SRDCVBUVTY"
            cursorVisible: true
            horizontalAlignment: Text.AlignLeft
            font.family: "Ubuntu"
            font.pixelSize: (popup_input_otp.width==1920) ? 50 : 45
            color: CONF.text_color
            clip: true
            visible: !manualMethod.isSelected
            focus: true
        }

        NumKeyboardCircle{
            id:virtual_numpad
            width:320
            height:420
            anchors.verticalCenterOffset: 50
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            //TODO: Assign this into conditional view
            visible: !manualMethod.isSelected
            property int count:0

            Component.onCompleted: {
                virtual_numpad.strButtonClick.connect(typeIn)
                virtual_numpad.funcButtonClicked.connect(functionIn)
            }

            function functionIn(str){
                if(str == "Back"){
                    count--
                    numberInput = numberInput.substring(0,numberInput.length-1);
                }
                if(str == "Clear"){
                    count = 0;
                    numberInput = "";
                }
            }

            function typeIn(str){
                if (str == "" && count > 0){
                    if(count >= maxCountInput){
                        count = maxCountInput
                    }
                    count--
                    numberInput = numberInput.substring(0,count);
                }
                if (str != "" && count<maxCountInput){
                    count++
                }
                if (count >= maxCountInput){
                    str = ""
                } else {
                    numberInput += str
                }
            }
        }

    }

    function open(msg){
        if (msg!=undefined) caseTitle = msg;
        popup_input_otp.visible = true;
        reset_counter();
    }

    function close(){
        popup_input_otp.visible = false;
        reset_counter();
    }

    function reset_counter(){
        numberInput = '';
        maxCountInput = 15;
        virtual_numpad.count = 0;
    }

    function check_availability(){
//        console.log('numberInput', numberInput, canProceed);
        if (numberInput.substring(0, 2)==pattern && numberInput.length > minCountInput) {
            if (calledFrom!=undefined) {
                switch(calledFrom){
                case 'general_payment_process':
                    general_payment_process.framingSignal('PHONE_INPUT_FRAME|'+numberInput)
                    break;
                }
            }
            if (handleButtonVisibility!=undefined){
                handleButtonVisibility.visible = true;
            }
        }
    }


}
