import QtQuick 2.0

Rectangle{
    id: base_rec
    property var set_width: 1000
    property var set_height: 60
    property var set_color: 'white'
    property var set_padding: 40
    property var left_padding: 10
    property var set_opacity: .7
    property var set_font_size: 30
    width: set_width
    height: set_height
    color: 'transparent'
    Rectangle{
        id: main_rec
        anchors.fill: parent
        color: set_color
        opacity: set_opacity
    }
    Text{
        id: col_no
        text: 'No'
        anchors.left: parent.left
        anchors.leftMargin: left_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
    }
    Text{
        id: col_timestamp
        text: 'Time Stamp'
        anchors.left: col_no.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
    }
    Text{
        id: col_trx_type
        text: 'Transaction Type'
        anchors.left: col_timestamp.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
    }
    Text{
        id: col_amount
        text: 'Amount'
        anchors.left: col_trx_type.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
    }
    Text{
        id: col_last_balance
        text: 'Last Balance'
        anchors.left: col_amount.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
    }
}
