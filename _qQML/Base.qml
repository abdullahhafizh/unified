import QtQuick 2.4
import QtQuick.Controls 1.2
import QtGraphicalEffects 1.0
//import "screen.js" as SCREEN
//import "config.js" as CONF


Rectangle{
    id: main
    x:0
    y:0

//    property var globalScreenType: '1'
//    height: (globalScreenType=='2') ? 1024 : 1080
//    width: (globalScreenType=='2') ? 1280 : 1920

    width: parseInt(SCREEN_WIDTH)
    height: parseInt(SCREEN_HEIGHT)

    color: "transparent"
    property string mode_: "normal"
    property var use_
    property var boxName: base.globalBoxName
//    property var boxName: 'VM Shelter Blok M 01'
    property bool logo_vis: true
    property int header_height: 125
    property int idx_bg: 0

    //Change Background Asset
    property variant backgrounds: VIEW_CONFIG.backgrounds
    property variant logo: VIEW_CONFIG.master_logo
    property variant partner_logos: VIEW_CONFIG.partner_logos
//    property variant backgrounds: ['source/mandiri_background.png', 'source/mandiri_background.png', 'source/mandiri_background.png', 'source/mandiri_background.png' ]
    // Old Property Not Used But Cannot Be Removed
    property bool isPanelActive: false
    property bool isBoxNameActive: true
    property bool isHeaderActive: true
    property string imgPanel: "source/rocket.png"
    property string textPanel: ""
    property string colorPanel: "white"
    property int panelWidth: 400
    property var imgPanelScale: .9
    property var show_img: (mode_!='normal') ? "source/logo/logo_white_.png" : "source/logo/logo_red_.png"
    property var top_color: (mode_!='normal') ? "#f03838" : "white"
// Define All QR Provider Here
    property variant allQRProvider: VIEW_CONFIG.all_qr_provider
    property bool printerAvailable: true

// =========


    Image{
        id: img_background
        visible: true
        source: "source/background/" + backgrounds[0]
        fillMode: Image.PreserveAspectCrop
        anchors.fill: parent
    }

    Rectangle{
        id: body_opacity
        anchors.fill: parent
        color: 'black'
        opacity: 0.6
    }

    Rectangle{
        id: header_opacity
        width: parent.width
        height: header_height
        color: 'white'
        visible: isHeaderActive
        opacity: 0.1
    }

    Image{
        id: master_logo
        width: 275
        height: 80
        anchors.verticalCenter: header_opacity.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 25
        source: "source/logo/" +logo[0]
        fillMode: Image.PreserveAspectFit
        visible: logo_vis
    }


    Rectangle{
        id: printer_status_info
        color: 'white'
        anchors.left: parent.left
        anchors.leftMargin: 380
        height: header_height
        width: 180
        visible: !printerAvailable
        Image{
            anchors.topMargin: -20
            anchors.fill: parent
            scale: 0.8
            source: "source/empty_printer_paper.jpeg"
            fillMode: Image.PreserveAspectFit
        }
        Text {
            width: parent.width
            height: 50
            text: 'STRUK HABIS'
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            style: Text.Sunken
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignBottom
            font.family:"Ubuntu"
            font.pixelSize:24
            color:"#ff0000"

        }

    }

    Image{
        id: single_partner_logo
        height: 80
        width: 800
        anchors.verticalCenter: header_opacity.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 10
        visible: (partner_logos.length == 1)
        source: (partner_logos[0] !== undefined) ? "source/logo/" + partner_logos[0] : ''
        fillMode: Image.PreserveAspectFit
    }

    Row{
        id: partners_logo
        spacing: 3
        property int item_width: 225
        width: (item_width * partner_logos.length)
        height: 60
        anchors.verticalCenter: header_opacity.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 25
        visible: (partner_logos.length > 1)

        Image{
            visible: (partner_logos.length > 0 && partner_logos[0] !== undefined)
            width: parent.item_width
            height: parent.height
            source: (partner_logos.length > 0 && partner_logos[0] !== undefined) ? "source/logo/" + partner_logos[0] : ''
            fillMode: Image.PreserveAspectFit
        }

        Image{
            visible: (partner_logos.length > 1 && partner_logos[1] !== undefined)
            width: parent.item_width
            height: parent.height
            source: (partner_logos.length > 1 && partner_logos[1] !== undefined) ? "source/logo/" + partner_logos[1] : ''
            fillMode: Image.PreserveAspectFit
        }

        Image{
            visible: (partner_logos.length > 2 && partner_logos[2] !== undefined)
            width: parent.item_width
            height: parent.height
            source: (partner_logos.length > 2 && partner_logos[2] !== undefined) ? "source/logo/" + partner_logos[2] : ''
            fillMode: Image.PreserveAspectFit
        }

        Image{
            visible: (partner_logos.length > 3 && partner_logos[3] !== undefined)
            width: parent.item_width
            height: parent.height
            source: (partner_logos.length > 3 && partner_logos[3] !== undefined) ? "source/logo/" + partner_logos[3] : ''
            fillMode: Image.PreserveAspectFit
        }

    }


    Text {
        id: boxNameText
        width: 500
        height: 50
        text: boxName
        visible: isBoxNameActive
        style: Text.Sunken
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        horizontalAlignment: Text.AlignHCenter
        font.italic: false
        verticalAlignment: Text.AlignVCenter
        font.family:"Ubuntu"
        font.pixelSize:35
        color:"#ffffff"

    }


    Text {
        id: timeText
        x: 0
        width: 150
        height: 35
        style: Text.Sunken
        text: new Date().toLocaleTimeString(Qt.locale("id_ID"), "hh:mm:ss")
        anchors.top: parent.top
        anchors.topMargin: 80
        anchors.horizontalCenter: parent.horizontalCenter
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.family:"Ubuntu"
        font.pixelSize:30
        color:"#ffffff"
        visible: isBoxNameActive
    }

    Text {
        id: dateText
        x: 0
        width: 250
        height: 25
        style: Text.Sunken
        text: new Date().toLocaleDateString(Qt.locale("id_ID"), Locale.LongFormat)
        anchors.top: parent.top
        anchors.topMargin: 60
        anchors.horizontalCenter: parent.horizontalCenter
        horizontalAlignment: Text.AlignHCenter
        font.italic: false
        verticalAlignment: Text.AlignVCenter
        font.family:"Ubuntu"
        font.pixelSize:20
        color:"#ffffff"
        visible: isBoxNameActive
    }

    Timer {
        id: timer_clock
        interval: 1000
        repeat: true
        running: isBoxNameActive
        onTriggered:
        {
            timeText.text = new Date().toLocaleTimeString(Qt.locale("en_EN"), "hh:mm:ss")
        }
    }

//    Image {
//        id: img_logo_kasirku
//        width: 150
//        height: 80
//        anchors.left: parent.left
//        anchors.leftMargin: 120
//        fillMode: Image.PreserveAspectFit
//        anchors.bottom: parent.bottom
//        anchors.bottomMargin: 20
//        source: "source/kasirku_inacraft.png"
//        visible: !isPanelActive
//        z: 10
//    }

//    Image {
//        id: img_logo_jaklinggo
//        width: 150
//        height: 80
//        scale: 0.9
//        anchors.left: img_logo_kasirku.right
//        anchors.leftMargin: 0
//        anchors.bottom: parent.bottom
//        anchors.bottomMargin: 20
//        source: "source/logo/logo_jaklinggo.png"
//        visible: !isPanelActive
//        z: 10
//    }


    Rectangle{
        id: rec_left_panel
        y: header_height
        width: panelWidth
        height: parent.height - header_height
//        visible: isPanelActive
        visible: false
        color: '#1D294D'
        opacity: .97
//        Rectangle{
//            id: opacity
//            color: colorPanel
//            opacity: .7
//            anchors.fill: parent
//        }
//        Image {
//            id: img_pattern
//            source: "source/ornament_header.png"
//            anchors.fill: parent
//            opacity: .20
//            fillMode: Image.Tile
//        }
        Image{
            id: img_left_panel
            x: 0
            width: panelWidth
            height: 600
            scale: imgPanelScale
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 125
            source: imgPanel
            fillMode: Image.PreserveAspectFit
            visible: false
        }
        ColorOverlay {
            id: reverse_color_image
            anchors.fill: img_left_panel
            source: img_left_panel
            color: 'white'
            scale: imgPanelScale
        }
        Text{
            id: text_left_panel
            color: "white"
            text: textPanel
            anchors.topMargin: 150
            wrapMode: Text.WordWrap
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.top: parent.top
            font.pixelSize: 40
            font.family:"Ubuntu"
            textFormat: Text.PlainText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

    }

}
