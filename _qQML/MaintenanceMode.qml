import QtQuick 2.2
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0

Base{
    id:maintenance_mode
    isBoxNameActive: false
    property var textMain: 'Mohon Maaf'
    property var textSlave: 'Mesin Sedang Dalam Pemeliharaan Sistem'
    property var imageSource: "source/vm-maintenance.gif"
    property bool smallerSlaveSize: false
    property int textSize: 40
//    width: 1920
//    height: 1280
    visible: false
    opacity: visible ? 1.0 : 0.0
    Behavior on opacity {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutQuad  }
    }


    Column{
        width: parent.width
        height: 500
        anchors.verticalCenterOffset: -100
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        spacing: 20
        Rectangle{
            color: 'transparent'
            width: parent.width
            height: parent.height
            AnimatedImage  {
                width: 700
                height: 500
                anchors.horizontalCenter: parent.horizontalCenter
                source: imageSource
                fillMode: Image.PreserveAspectFit
            }

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
        maintenance_mode.visible = true;
    }

    function close(){
        maintenance_mode.visible = false;
    }
}
