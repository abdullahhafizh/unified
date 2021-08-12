import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0


Rectangle{
    id:full_numpad
    width:200
    height:300
    color:"transparent"
    signal strButtonClick(string str)
    signal funcButtonClicked(string str)
    visible: false
    opacity: visible ? 1.0 : 0.0
    Behavior on opacity {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutQuad  }
    }


    NumButtonCircle{
        width: 60
        height: 60
        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.left: parent.left
        anchors.leftMargin: 4
        show_text:"1"
    }
    NumButtonCircle{
        x:40
        width: 60
        height: 60
        anchors.top: parent.top
        anchors.horizontalCenterOffset: 0
        anchors.topMargin: 8
        anchors.horizontalCenter: parent.horizontalCenter
        show_text:"2"
    }
    NumButtonCircle{
        x:136
        width: 60
        height: 60
        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.right: parent.right
        anchors.rightMargin: 4
        show_text:"3"
    }
    NumButtonCircle{
        y:74
        width: 60
        height: 60
        anchors.left: parent.left
        anchors.leftMargin: 4
        show_text:"4"
    }
    NumButtonCircle{
        x:90
        y:74
        width: 60
        height: 60
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter
        show_text:"5"
    }
    NumButtonCircle{
        x:136
        y:74
        width: 60
        height: 60
        anchors.right: parent.right
        anchors.rightMargin: 4
        show_text:"6"
    }
    NumButtonCircle{
        y:140
        width: 60
        height: 60
        anchors.left: parent.left
        anchors.leftMargin: 8
        show_text:"7"
    }
    NumButtonCircle{
        x:90
        y:140
        width: 60
        height: 60
        anchors.horizontalCenterOffset: 1
        anchors.horizontalCenter: parent.horizontalCenter
        show_text:"8"
    }
    NumButtonCircle{
        x:136
        y:140
        width: 60
        height: 60
        anchors.right: parent.right
        anchors.rightMargin: 4
        show_text:"9"
    }
    NumButtonCircle{
        x:90
        y:206
        width: 60
        height: 60
        anchors.bottom: parent.bottom
        anchors.horizontalCenterOffset: 2
        anchors.bottomMargin: 34
        anchors.horizontalCenter: parent.horizontalCenter
        show_text:"0"
    }
    NumboardClearCircle{
        y:206
        width: 60
        height: 60
        color: "#5a5a5a"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 34
        anchors.left: parent.left
        anchors.leftMargin: 8
        border.width: 0
        slot_text:"Clear"
    }
    NumboardBackCircle{
        x:136
        y:206
        width: 60
        height: 60
        color: "#ffc125"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 34
        anchors.right: parent.right
        anchors.rightMargin: 4
        border.width: 0
        slot_text: "Back"
    }
}
