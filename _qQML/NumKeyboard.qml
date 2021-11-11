import QtQuick 2.4
import QtQuick.Controls 1.2

Rectangle{
    id:full_numpad
    width:155
    height:220
    color:"transparent"
    signal strButtonClick(string str)
    signal funcButtonClicked(string str)


    NumButton{
        x:0
        y:0
        width: 50
        height: 50
        show_text:"1"
    }
    NumButton{
        x:52
        y:0
        width: 50
        height: 50
        show_text:"2"
    }
    NumButton{
        x:104
        y:0
        width: 50
        height: 50
        show_text:"3"
    }
    NumButton{
        x:0
        y:55
        width: 50
        height: 50
        show_text:"4"
    }
    NumButton{
        x:52
        y:55
        width: 50
        height: 50
        show_text:"5"
    }
    NumButton{
        x:104
        y:55
        width: 50
        height: 50
        show_text:"6"
    }
    NumButton{
        x:0
        y:109
        width: 50
        height: 50
        show_text:"7"
    }
    NumButton{
        x:52
        y:109
        width: 50
        height: 50
        show_text:"8"
    }
    NumButton{
        x:104
        y:110
        width: 50
        height: 50
        show_text:"9"
    }
    NumButton{
        x:52
        y:165
        width: 50
        height: 50
        show_text:"0"
    }
    NumboardClear{
        x:0
        y:165
        width: 50
        height: 50
        color: "#5a5a5a"
        border.width: 0
        slot_text:"Clear"

    }
    NumboardBack{
        x:104
        y:165
        width: 50
        height: 50
        color: "#ffc125"
        border.width: 0
        slot_text: "Back"
    }
}
