import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN

Rectangle{
    id:popup_update_stock
    visible: false
    width: parseInt(SCREEN_WIDTH)
    height: parseInt(SCREEN_HEIGHT)
    color: 'transparent'
    property int max_count: 4
    property var press: "0"
    property var initStockInput: ""
    property var addStockInput: ""
    property var titleImage: "source/plus_circle.png"
    property var selectedSlot: '1'
    property var inputStep: 1

    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: notif_rec
        width: (parent.width==1920) ? 1200 : parent.width
        height: (parent.width==1920) ? 800 : 750
        color: "white"
        opacity: .8
        radius: 25
        anchors.verticalCenterOffset: (parent.width==1920) ? 50 : 35
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        Text {
            id: main_text
            color: "darkblue"
            text: 'Masukkan Stok Kartu Awal Pada Slot ' + selectedSlot
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.top: parent.top
            anchors.topMargin: 60
            anchors.horizontalCenterOffset: 5
            font.family:"Ubuntu"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 40
        }

        TextRectangle{
            id: textRectangle
            width: 700
            height: 80
            anchors.top: parent.top
            anchors.topMargin: 180
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Image{
            id: imageBody
            anchors.top: parent.top
            anchors.topMargin: 20
            scale: 0.7
            anchors.left: parent.left
            anchors.leftMargin: 20
            source: titleImage
        }

        TextInput {
            id: inputText
            anchors.centerIn: textRectangle;
//            text: initStockInput
    //        text: "INPUT NUMBER 1234567890SRDCVBUVTY"
            cursorVisible: true
            horizontalAlignment: Text.AlignLeft
            font.family: "Ubuntu"
            font.pixelSize: 40
            color: "darkblue"
            clip: true
            visible: true
            focus: true
        }

        NumKeyboard{
            id:virtual_numpad
            anchors.verticalCenterOffset: 60
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            property int count:0

            Component.onCompleted: {
                virtual_numpad.strButtonClick.connect(typeIn);
                virtual_numpad.funcButtonClicked.connect(functionIn);
            }

            function functionIn(str){
                if(str == "OK"){
                    if(press != "0"){
                        return
                    }
                    press = "1"
                }
                if(str=="Back"){
                    count--
                    if (inputStep==1) {
                        initStockInput = initStockInput.substring(0,initStockInput.length-1);
                        inputText.text = initStockInput;
                    }
                    else if (inputStep==2) {
                        addStockInput = addStockInput.substring(0,addStockInput.length-1);
                        inputText.text = addStockInput;
                    }
                }

                if(str=="Clear"){
                    count = 0;
                    if (inputStep==1) inputText.text = initStockInput = "";
                    else if (inputStep==2) inputText.text = addStockInput = "";
                }
            }

            function typeIn(str){
                if (str == "" && count > 0){
                    if(count>=max_count){
                        count=max_count;
                    }
                    count--;
                    if (inputStep==1) {
                        initStockInput = initStockInput.substring(0,count);
                        inputText.text = initStockInput;
                    }
                    else if (inputStep==2) {
                        addStockInput = addStockInput.substring(0,count);
                        inputText.text = addStockInput;
                    }

                }

                if (str!=""&&count<max_count){
                    count++;
                }

                if (count>=max_count){
                    str="";
                }

                if (inputStep==1) {
                    initStockInput += str;
                    inputText.text = initStockInput;
                }
                else if (inputStep==2) {
                    addStockInput += str;
                    inputText.text = addStockInput;
                }
            }
        }

        GroupBox{
            id: groupBox1
            flat: true
            x: 200
            y: 472
            width: parent.width
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenterOffset: 0
            anchors.horizontalCenter: parent.horizontalCenter
            NextButton{
                id: cancel_button
                width: 190
                anchors.left: parent.left
                anchors.leftMargin: 250
                button_text: 'batal'
                color_set: 'red'
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        console.log('cancel_button is pressed..!');
                        reset();
                        close();
                    }
                }
            }
            NextButton{
                id: update_button
                width: 190
                anchors.right: parent.right
                anchors.rightMargin: 250
                button_text: (inputStep == 2) ? 'update' : 'lanjut'
                color_set: 'green'
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
//                        console.log('Init Stock : ' +initStockInput)
//                        console.log('Add Stock : ' +addStockInput)
//                        console.log('Input Step : ' +inputStep)
                        if (initStockInput!='' && parseInt(initStockInput)>-1){
                            inputStep = 2;
                            virtual_numpad.count = 0;
                            inputText.text = addStockInput;
                            if (addStockInput!='' && parseInt(addStockInput)>-1){
                                var __signal = JSON.stringify({
                                                                port: selectedSlot,
                                                                init_stock: initStockInput,
                                                                add_stock: addStockInput,
                                                                last_stock: parseInt(initStockInput) + parseInt(addStockInput),
                                                                type: 'changeStock'
                                                            });
                                admin_page.update_product_stock(__signal);
                                close();
                            } else {
                                main_text.text = 'Sisa Stok Kartu ('+initStockInput+')\nMasukkan Penambahan Stok Kartu Pada Slot ' + selectedSlot.replace('10', '');
                            }
                        }
                    }
                }
            }
        }
    }


    function reset(){
        initStockInput = '';
        addStockInput = '';
        inputStep = 1;
        virtual_numpad.count = 0;
        inputText.text = initStockInput;
    }

    function open(slot){
        reset();
        // Must Put Here After Adjustment;
        selectedSlot = slot;
        main_text.text = 'Masukkan Sisa Stok Kartu Slot ' + selectedSlot.replace('10', '');
        popup_update_stock.visible = true;
    }

    function close(){
        popup_update_stock.visible = false;
    }

}
