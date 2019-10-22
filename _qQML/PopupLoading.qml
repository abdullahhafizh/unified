import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0

Base{
    id:popup_loading
    isBoxNameActive: false
    property var textMain: 'Silakan Menunggu'
    property var textSlave: ''
    property var imageSource: "source/loading_static.png"
    property bool smallerSlaveSize: false
    property int textSize: 45
    visible: false
    opacity: visible ? 1.0 : 0.0
    Behavior on opacity {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutQuad  }
    }

//    Rectangle{
//        anchors.fill: parent
//        color: "gray"
//        opacity: 0.5
//    }

    Column{
        width: 600
        height: 500
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 30
        AnimatedImage  {
            width: 300
            height: 300
            anchors.horizontalCenter: parent.horizontalCenter
            source: imageSource
            fillMode: Image.PreserveAspectFit
        }
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

        }
        Text{
            text: textSlave
            width: parent.width
            wrapMode: Text.WordWrap
            font.pixelSize: (smallerSlaveSize) ? textSize-5: textSize
            anchors.horizontalCenter: parent.horizontalCenter
            font.bold: false
            color: 'white'
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.family:"Ubuntu"

        }
    }


    function open(){
        popup_loading.visible = true
    }

    function close(){
        popup_loading.visible = false
    }
}
