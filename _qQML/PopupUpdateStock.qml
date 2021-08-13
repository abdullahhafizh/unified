import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
import "screen.js" as SCREEN

Rectangle{
    id:popup_update_stock
    visible: false
    width: parseInt(SCREEN.size.width)
    height: parseInt(SCREEN.size.height)
    color: 'transparent'
    property int max_count: 50
    property var press: "0"
    property var textInput: ""
    property var titleImage: "source/plus_circle.png"
    property var selectedSlot: '1'

    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        id: notif_rec
        width: 500
        height: 472
        color: "white"
        opacity: .8
        radius: 25
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 70
        anchors.horizontalCenterOffset: 0

        Text {
            id: main_text
            color: "darkblue"
            text: 'Masukkan Stok Kartu Terbaru Pada Slot ' + selectedSlot
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.top: parent.top
            anchors.topMargin: 35
            anchors.horizontalCenterOffset: 33
            font.family:"Ubuntu"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 16
        }

        TextRectangle{
            id: textRectangle
            width: 400
            height: 40
            anchors.top: parent.top
            anchors.horizontalCenterOffset: 0
            anchors.topMargin: 92
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Image{
            id: imageBody
            anchors.top: parent.top
            anchors.topMargin: 6
            scale: 0.7
            anchors.left: parent.left
            anchors.leftMargin: 38
            source: titleImage
            sourceSize.height: 80
            sourceSize.width: 80
        }

        TextInput {
            id: inputText
            anchors.centerIn: textRectangle;
            text: textInput
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
            anchors.verticalCenterOffset: 22
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenterOffset: 1
            anchors.horizontalCenter: parent.horizontalCenter
            property int count:0

            Component.onCompleted: {
                virtual_numpad.strButtonClick.connect(typeIn)
                virtual_numpad.funcButtonClicked.connect(functionIn)
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
                    textInput=textInput.substring(0,textInput.length-1);
                }
                if(str=="Clear"){
                    count = 0;
                    textInput = "";
                }
            }

            function typeIn(str){
                if (str == "" && count > 0){
                    if(count>=max_count){
                        count=max_count
                    }
                    count--
                    textInput=textInput.substring(0,count);
                }
                if (str!=""&&count<max_count){
                    count++
                }
                if (count>=max_count){
                    str=""
                } else{
                    textInput += str
                }
            }
        }

        GroupBox{
            id: groupBox1
            flat: true
            x: 200
            y: 489
            width: parent.width
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 17
            anchors.horizontalCenterOffset: 0
            anchors.horizontalCenter: parent.horizontalCenter
            NextButton{
                id: cancel_button
                y: 4
                width: 80
                height: 60
                anchors.left: parent.left
                fontSize: 20
                anchors.leftMargin: 394
                button_text: 'batal'
                MouseArea{
                    anchors.fill: parent
                    anchors.rightMargin: 2
                    anchors.bottomMargin: 1
                    anchors.leftMargin: -2
                    anchors.topMargin: -1
                    onClicked: close();
                }
            }
            NextButton{
                id: update_button
                x: 11
                y: 8
                width: 80
                height: 60
                anchors.right: parent.right
                fontSize: 20
                anchors.rightMargin: 389
                button_text: 'update'
                MouseArea{
                    anchors.fill: parent
                    anchors.rightMargin: 0
                    anchors.bottomMargin: 2
                    anchors.leftMargin: 0
                    anchors.topMargin: -2
                    onClicked: {
                        if (textInput!='' && parseInt(textInput) > 0){
                            var _signal = JSON.stringify({
                                                             port: selectedSlot,
                                                             stock: textInput,
                                                             type: 'changeStock'
                                                         });
                            admin_page.update_product_stock(_signal);
                            close();
                        }
                    }
                }
            }

        }

    }

    function open(){
        textInput = '';
        popup_update_stock.visible = true;
    }

    function close(){
        popup_update_stock.visible = false;
    }

}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.75}
}
##^##*/
