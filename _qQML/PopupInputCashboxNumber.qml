import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0
import "base_function.js" as FUNC

Rectangle{
    id:popup_input_cashbox_no
    width: parseInt(SCREEN_WIDTH)
    height: parseInt(SCREEN_HEIGHT)

    color: 'transparent'
    // property var colorMode: "292F32"
    property bool withBackground: true

    property var calledFrom
    property var handleButtonVisibility
    property var externalSetValue

    property var escapeFunction: 'closeWindow' //['closeWindow', 'backToMain', 'backToPrevious']
    property var press: "0"

    property int minCountInput: 3
    property int maxCountInput: 15
    property var numberInput: ""
    property var showDuration: "0"

    property string caseTitle: ""
    property var mainTitleMode: "normal" //normal/center
    property string mainTitle: "Masukkan Nomor Serial Cashbox"

    visible: false
    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: base_overlay
        visible: withBackground
        anchors.fill: parent
        color: "darkgray"
        // color: '#1A144A'
        opacity: 0.6
    }

    Rectangle{
        id: notif_rec
        width: parent.width
        height: parent.height - 100
        // color: VIEW_CONFIG.frame_color
        color: '#1A144A'
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        MainTitle{
            id: main_title
            width: parent.width - 200
            anchors.top: parent.top
            anchors.topMargin: mainTitleMode=="normal" ? 45 : popup_input_cashbox_no.height/2
            anchors.horizontalCenter: parent.horizontalCenter
            show_text: caseTitle + mainTitle
            size_: (popup_input_cashbox_no.width==1920) ? 50 : 40
            color_: "white"
        }

        TextRectangle{
            id: text_rectangle
            width: 650
            height: 100
            anchors.top: parent.top
            anchors.topMargin: 160
            anchors.horizontalCenter: parent.horizontalCenter
            borderColor: "white"
        }

        TextInput {
            id: inputText
            anchors.centerIn: text_rectangle;
            text: VIEW_CONFIG.bill_cashbox_prefix + numberInput
    //        text: "INPUT NUMBER 1234567890SRDCVBUVTY"
            cursorVisible: true
            horizontalAlignment: Text.AlignLeft
            font.family: "Ubuntu"
            font.pixelSize: (popup_input_cashbox_no.width==1920) ? 50 : 45
            color: "white"
            clip: true
            focus: true
        }

        NumKeyboardCircle{
            id:virtual_numpad
            width:320
            height:420
            anchors.verticalCenterOffset: 50
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            visible: true
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
                check_availability();
            }
        }

    }

    AnimatedImage  {
        width: 100
        height: 100
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
        scale: 1
        anchors.horizontalCenter: parent.horizontalCenter
        source: 'source/blue_gradient_circle_loading.gif'
        fillMode: Image.PreserveAspectFit
        Text{
            id: text_timer_show
            anchors.fill: parent
            text: showDuration
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: 20
            color: 'yellow'
            verticalAlignment: Text.AlignVCenter
            font.family:"Ubuntu"
        }
    }

    function open(msg){
        if (msg!=undefined) caseTitle = msg;
        popup_input_cashbox_no.visible = true;
        reset_counter();
    }

    function close(){
        popup_input_cashbox_no.visible = false;
        reset_counter();
    }

    function reset_counter(){
        numberInput = '';
        maxCountInput = 15;
        virtual_numpad.count = 0;
    }

    function check_availability(){
//        console.log('numberInput', numberInput, canProceed);
        if (numberInput.length == minCountInput) {
            if (handleButtonVisibility!=undefined){
                handleButtonVisibility.visible = true;
            }
        }
    }


}
