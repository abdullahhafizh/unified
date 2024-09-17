import QtQuick 2.5
import QtQuick.Controls 1.5

Rectangle{
    width:180
    height:90
    color:"transparent"
    property bool modeReverse: false
    property string button_text: 'lanjut'
    property real globalOpacity: .97
    property int fontSize: 30
    property bool modeRadius: true
    property var color_set: '#1D294D'

    Rectangle{
        anchors.fill: parent
        color: (modeReverse) ? 'white' : color_set
        opacity: globalOpacity
        radius: (modeRadius) ? fontSize : 0
    }

    Text {
        color: (modeReverse) ? color_set : 'white'
        anchors.fill: parent
        text: button_text.toUpperCase()
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.family:"Ubuntu"
        anchors.horizontalCenter: parent.horizontalCenter
        font.pixelSize: fontSize
    }

}


