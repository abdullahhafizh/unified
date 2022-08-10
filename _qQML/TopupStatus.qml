import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN
//import "config.js" as CONF


Rectangle{
    id:topup_status_component
    visible: true
    color: 'transparent'
    height: 160
//    width: 1280
    width: parseInt(SCREEN_WIDTH)
    property alias statusMandiri: mandiri_status.itemName
    property alias statusBni: bni_status.itemName
    property alias statusBri: bri_status.itemName
    property alias statusBca: bca_status.itemName
    property alias statusDki: dki_status.itemName


    Rectangle{
        anchors.fill: parent
        color: "black"
        opacity: .75
    }

    Text{
        id: label1
        width: 225
        text: "INFORMASI STATUS TOPUP"
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: row_button.left
        anchors.rightMargin: 50
        color: "white"
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignRight
        style: Text.Sunken
        font.bold: true
        font.pixelSize: 33
        font.family: "Ubuntu"
        visible: (parent.width==1920)
    }

    Row{
        id: row_button
        height: parent.height
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: (parent.width==1920) ? 50 : 20

        SmallCardItem {
            id: mandiri_status
            width: 200 * 0.8
            height: 160 * 0.8
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-mandiri.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bni_status
            width: 200 * 0.8
            height: 160 * 0.8
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-bni.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bri_status
            width: 200 * 0.8
            height: 160 * 0.8
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-bri.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bca_status
            width: 200 * 0.8
            height: 160 * 0.8
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-bca.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: dki_status
            width: 200 * 0.8
            height: 160 * 0.8
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-dki.png"
            itemName: "ACTIVE"
        }



    }


    Text{
        id: label2
        width: 225
        text: "KARTU UANG ELEKTRONIK"
        anchors.left: row_button.right
        anchors.leftMargin: 50
        anchors.verticalCenter: parent.verticalCenter
        color: "white"
        horizontalAlignment: Text.AlignLeft
        wrapMode: Text.WordWrap
        style: Text.Sunken
        font.bold: true
        font.pixelSize: 33
        font.family: "Ubuntu"
        visible: (parent.width==1920)

    }

}
