import QtQuick 2.0
//import QtGraphicalEffects 1.0

Rectangle{
    id: rectangle
    property var _boxSize: 200
    property var _width: 1280
    property var _padding: 20
    property var _textSize: 30
    property alias textContent: _text.text
    property alias imageSource: _image.source
    width: _width
    height: _boxSize
    color: "transparent"

    AnimatedImage  {
        id: _image
        width: _boxSize
        height: _boxSize
        anchors.left: parent.left
        anchors.leftMargin: _padding * 2
        scale: 1
        source: "source/inputcode_icon_tnc.png"
        fillMode: Image.PreserveAspectFit
    }

    Text{
        id: _text
        text: "Mesin ini tidak dapat mengembalikan uang, Proses pengembalian uang akan dilakukan melalui Whatsapp Voucher."
        anchors.left: _image.right
        anchors.leftMargin: _padding
        horizontalAlignment: Text.AlignLeft
        font.pixelSize: _textSize
        width: parent.width - _boxSize - (_padding * 3)
        height: _boxSize
        wrapMode: Text.WordWrap
        font.bold: false
        color: 'white'
        verticalAlignment: Text.AlignVCenter
        font.family: "Ubuntu"
    }
}
