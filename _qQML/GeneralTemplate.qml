import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.3
import "base_function.js" as FUNC


Base{
    id: base_page
    mode_: "reverse"
    isPanelActive: true
    textPanel: "Scan/Input The Numbers"
    property int timer_value: 60

    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
            abc.counter = timer_value
            my_timer.start()

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

//    Rectangle{
//        id: rec_timer
//        width:10
//        height:10
//        y:10
//        color:"transparent"
//        QtObject{
//            id:abc
//            property int counter
//            Component.onCompleted:{
//                abc.counter = timer_value
//            }
//        }

//        Timer{
//            id:my_timer
//            interval:1000
//            repeat:true
//            running:true
//            triggeredOnStart:true
//            onTriggered:{
//                abc.counter -= 1
//                if(abc.counter < 0){
//                    my_timer.stop()
//                    my_layer.pop(my_layer.find(function(item){if(item.Stack.index === 0) return true }))
//                }
//            }
//        }
//    }

    CircleButton{
        id:back_button
        anchors.left: parent.left
        anchors.leftMargin: 50
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        button_text: 'BATAL'
        modeReverse: true
        MouseArea{
            anchors.fill: parent
            onClicked: {
                my_layer.pop()
            }
        }
    }

    //==============================================================
    //PUT MAIN COMPONENT HERE
//    DatePickerNew{
//        id: datepicker
//    }

    function false_notif(param){
        press = '0';
        switch_frame('source/smiley_down.png', 'Maaf Sementara Mesin Tidak Dapat Digunakan', '', 'backToMain', false )
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

