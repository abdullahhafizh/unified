import QtQuick 2.0

Rectangle{
    id: base_rec
    property var set_width: 1000
    property var set_height: 60
    property var set_padding: 40
    property var left_padding: 10
    property var set_font_size: 30
    property var set_font_color: 'white'
    property var content_no: 'no'
    property var content_time: 'timestamp'
    property var content_type: 'type'
    property var content_nominal: 'nominal'
    property var content_balance: 'last_balance'
    width: set_width
    height: set_height
    color: 'transparent'
    Text{
        id: dummy_no
        text: 'No'
        style: Text.Sunken
        font.weight: Font.Bold
        anchors.left: parent.left
        anchors.leftMargin: left_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Tahoma"
        font.pixelSize: set_font_size
        color: "white"
        visible: false
    }
    Text{
        id: col_no
        text: content_no
        width: dummy_no.width
        style: Text.Sunken
        font.weight: Font.Bold
        anchors.left: parent.left
        anchors.leftMargin: left_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Tahoma"
        font.pixelSize: set_font_size
        color: set_font_color
    }
    Text{
        id: dummy_col_timestamp
        text: 'Time Stamp'
        anchors.left: col_no.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
        visible: false
    }
    Text{
        id: col_timestamp
        text: content_time
        width: dummy_col_timestamp.width
        anchors.left: col_no.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: set_font_color
    }
    Text{
        id: dummy_col_trx_type
        text: 'Transaction Type'
        anchors.left: col_timestamp.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
        visible: false
    }
    Text{
        id: col_trx_type
        text: content_type
        width: dummy_col_trx_type.width
        anchors.left: col_timestamp.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignLeft
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: set_font_color
    }
    Text{
        id: dummy_col_amount
        text: 'Amount'
        anchors.left: col_trx_type.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignRight
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
        visible: false
    }
    Text{
        id: col_amount
        text: content_nominal
        width: dummy_col_amount.width
        anchors.left: col_trx_type.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignRight
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: set_font_color
    }
    Text{
        id: dummy_col_last_balance
        text: 'Last Balance'
        anchors.left: col_amount.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignRight
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: "darkblue"
        visible: false
    }
    Text{
        id: col_last_balance
        text: content_balance
        width: dummy_col_last_balance.width
        anchors.left: col_amount.right
        anchors.leftMargin: set_padding
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignRight
        font.family: "Ubuntu"
        font.pixelSize: set_font_size
        color: set_font_color
    }
}
