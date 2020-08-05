import QtQuick 2.4
import QtQuick.Controls 1.2

Rectangle{
    id: base_rectangle
    property bool modeReverse: false
    property string button_text: 'ISI SALDO\nOFFLINE'
    property real globalOpacity: .50
    property int fontSize: 30
    property bool blinkingMode: false
    property var forceColorButton: 'transparent'
    property int baseSize: 120
    width:baseSize
    height:baseSize
    color:"transparent"

    Rectangle{
        id: normalBox
        anchors.fill: parent
        color: (button_text=='BATAL') ? 'red' : 'white'
        opacity: (button_text=='BATAL') ? 1 : globalOpacity
        radius: width/2
        visible: (!blinkingMode && forceColorButton == 'transparent')
    }

    Rectangle{
        id: extraBox
        visible: false
        width: 165
        height: 165
        color: normalBox.color
        radius: width/2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }


    Rectangle{
        id: modeNormalColorBox
        anchors.fill: parent
        color: forceColorButton
        radius: width/2
        visible: (!blinkingMode && forceColorButton != 'transparent')
    }

    Rectangle{
        id: modeReverseBox
        visible: (blinkingMode && button_text!='BATAL')
        anchors.fill: parent
        color: (modeReverse) ? 'green' : 'white'
        radius: width/2
    }


    Text {
        anchors.fill: parent
        color: (modeReverse) ? 'white' : 'black'
        text: button_text.toUpperCase()
        style: Text.Sunken
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.family:"Ubuntu"
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: (button_text.length > 5 ) ? 23 : fontSize
        font.bold: true
    }

    QtObject{
        id:abc
        property int counter: 0
        Component.onCompleted:{
            abc.counter = 1;
        }
    }

    Timer{
        id: button_timer
        interval:1000
        repeat:true
        running:blinkingMode
        triggeredOnStart:blinkingMode
        onTriggered:{
            abc.counter += 1;
            if (abc.counter%2==0) {
                modeReverse = true;
                extraBox.visible = false;
            } else {
                modeReverse = false;
                if (blinkingMode) extraBox.visible = true;
            }
        }
    }

    Component.onCompleted: {
        if (blinkingMode) button_timer.start();
    }

    Component.onDestruction: {
        button_timer.stop();
    }



}


