import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
import "screen.js" as SCREEN

Rectangle{
    id:popup_update_stock
    visible: true
    width: parseInt(SCREEN.size.width)
    height: parseInt(SCREEN.size.height)
    color: 'transparent'
    property alias imageBody: imageBody
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
        width: 400
        height: 474
        color: "white"
        opacity: .8
        radius: 3
        anchors.verticalCenterOffset: -9
        anchors.horizontalCenterOffset: 5
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        Text {
            id: main_text
            color: "darkblue"
            text: 'Masukkan Stok Kartu Terbaru Pada Slot ' + selectedSlot
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.top: parent.top
            anchors.topMargin: 28
            anchors.horizontalCenterOffset: 22
            font.family:"Ubuntu"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 12
        }

        TextRectangle{
            id: textRectangle
            width: 357
            height: 39
            radius: 2
            anchors.top: parent.top
            anchors.horizontalCenterOffset: 1
            anchors.topMargin: 72
            anchors.horizontalCenter: parent.horizontalCenter
        }
        
        Image{
            id: imageBody
            width: 60
            height: 60
            transformOrigin: Item.Center
            anchors.top: parent.top
            anchors.topMargin: 6
            scale: 0.7
            anchors.left: parent.left
            anchors.leftMargin: 40
            source: titleImage
        }

        TextInput {
            id: inputText
            anchors.centerIn: textRectangle;
            text: textInput
    //        text: "INPUT NUMBER 1234567890SRDCVBUVTY"
            cursorVisible: true
            horizontalAlignment: Text.AlignLeft
            font.family: "Ubuntu"
            font.pixelSize: 20
            color: "darkblue"
            clip: true
            visible: true
            focus: true
        }

        NumKeyboard{
            id:virtual_numpad
            anchors.verticalCenterOffset: 33
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            property int count:0
            width: 156
            height: 218
            anchors.horizontalCenterOffset: 0
            
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
            y: 615
            width: parent.width
            anchors.bottom: parent.bottom
            anchors.bottomMargin: -200
            anchors.horizontalCenterOffset: -8
            anchors.horizontalCenter: parent.horizontalCenter
            NextButton{
                id: cancel_button
                y: -196
                width: 100
                height: 40
                anchors.left: parent.left
                fontSize: 15
                anchors.leftMargin: 297
                button_text: 'batal'
                MouseArea{
                    width: 100
                    anchors.fill: parent
                    anchors.rightMargin: 0
                    anchors.bottomMargin: 0
                    anchors.leftMargin: 0
                    anchors.topMargin: 0
                    onClicked: close();
                }
            }
            NextButton{
                id: update_button
                x: 0
                y: -194
                width: 100
                height: 40
                anchors.right: parent.right
                fontSize: 15
                anchors.rightMargin: 280
                button_text: 'update'
                MouseArea{
                    width: 100
                    height: 40
                    anchors.fill: parent
                    anchors.rightMargin: 8
                    anchors.bottomMargin: 0
                    anchors.leftMargin: -8
                    anchors.topMargin: 0
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
    D{i:0;formeditorZoom:0.9}
}
##^##*/
