import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN
//import "config.js" as CONF


Rectangle{
    id:topup_status_component
    visible: true
    color: 'transparent'
    height: 200
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
        width: parent.width
        height: 50
        text: "INFORMASI STATUS TOPUP KARTU UANG ELEKTRONIK"
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.horizontalCenter: parent.horizontalCenter
        color: "white"
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        style: Text.Sunken
        font.bold: true
        font.pixelSize: 30
        font.family: "Ubuntu"
    }

    Row{
        id: row_button
        height: 150
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: (parent.width==1920) ? 50 : 20

        SmallCardItem {
            id: mandiri_status
            width: 200 * 0.75
            height: 160 * 0.75
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-mandiri.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bni_status
            width: 200 * 0.75
            height: 160 * 0.75
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-bni.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bri_status
            width: 200 * 0.75
            height: 160 * 0.75
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-bri.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bca_status
            width: 200 * 0.75
            height: 160 * 0.75
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-bca.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: dki_status
            width: 200 * 0.75
            height: 160 * 0.75
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklinko-dki.png"
            itemName: "ACTIVE"
        }



    }


}
