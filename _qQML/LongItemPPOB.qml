import QtQuick 2.0
import QtGraphicalEffects 1.0


Rectangle {
    id: rectangle
    property bool modeReverse: false
    property var color_: (modeReverse) ? "black" : "white"
    property var text_:"Data 25.000"
    property var text2_:"Kuota Reguler 270-750MB + 2GB Video Max. Berlaku selama 30 hari"
    property var logo_:"source/ppob_operator/Pulsa.png"
    property var logo2_:"source/ppob_operator/Pulsa.png"
    property var itemWidth: 1000
    width: itemWidth
    height: 150
    color: 'transparent'
    visible: true

    Rectangle{
        id: background_base
        anchors.fill: parent
        color: color_
        opacity: .3
    }

    AnimatedImage{
        id: operator_logo
        height: parent.height
        scale: 0.8
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 0
        width: 150
        fillMode: Image.PreserveAspectFit
        source: logo_
        onStatusChanged: {
            if (operator_logo.status == Image.Error) {
                operator_logo.source = logo2_;
                operator_logo.scale = 0.6;
            }
        }
    }

    Text{
        id: name_item
        width: parent.width
        color: color_
        text: text_.toUpperCase()
        anchors.top: parent.top
        anchors.topMargin: 25
        anchors.left: parent.left
        anchors.leftMargin: 150
        font.pixelSize: (itemWidth==1000) ? 33 : 25
        wrapMode: Text.WordWrap
        style: Text.Sunken
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
    }

    Text{
        id: select_item
        width: parent.width
        color: color_
        text: "Pilih >"
        anchors.right: parent.right
        anchors.rightMargin: 25
        anchors.top: parent.top
        anchors.topMargin: 25
        font.pixelSize: (itemWidth==1000) ? 35 : 25
        wrapMode: Text.WordWrap
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignRight
    }

    Rectangle {
        id: separator_line
        color: "white"
        anchors.horizontalCenterOffset: 50
        anchors.verticalCenterOffset: 10
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        height: 5
        width: parent.width - 50 - 150
    }

    Text{
        id: desc_item
        color: color_
        text: text2_.toUpperCase()
        anchors.left: parent.left
        anchors.leftMargin: 150
        font.pixelSize: (itemWidth==1000) ? 21 : 19
        anchors.bottomMargin: 25
        anchors.horizontalCenterOffset: 0
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        font.family:"Ubuntu"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
    }

}

