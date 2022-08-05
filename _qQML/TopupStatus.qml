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


    scale: visible ? 1.0 : 0.1
    Behavior on scale {
        NumberAnimation  { duration: 500 ; easing.type: Easing.InOutBounce  }
    }

    Rectangle{
        anchors.fill: parent
        color: "black"
        opacity: .75
    }

    Row{
        id: row_button
        height: parent.height
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: (parent.width==1920) ? 50 : 20

        SmallCardItem {
            id: mandiri_status
            width: 200
            height: 160
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklingko-mandiri.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bni_status
            width: 200
            height: 160
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklingko-bni.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bri_status
            width: 200
            height: 160
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklingko-bri.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: bca_status
            width: 200
            height: 160
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklingko-bca.png"
            itemName: "ACTIVE"
        }

        SmallCardItem {
            id: dki_status
            width: 200
            height: 160
            anchors.verticalCenter: parent.verticalCenter
            sourceImage: "source/Jaklingko-dki.png"
            itemName: "ACTIVE"
        }



    }



}
