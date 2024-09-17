import QtQuick 2.5
import QtQuick.Controls 1.5
import Qt.labs.folderlistmodel 1.0
//import QtMultimedia 5.0


Rectangle{
    id:parent_root
    color: "black"
    width: parseInt(SCREEN_WIDTH)
    height: parseInt(SCREEN_HEIGHT)

    property string img_path: "/_vVideo/"
    property url img_path_: "../.." + img_path
    property var qml_pic
    property string pic_source: ""
    property int num_pic
    property string mode // ["staticVideo", "mediaPlayer", "liveView"]
//    property var list_pic: img_files
    property variant media_files: []
    property int index: 0
    property var mandiri_update_schedule
    property var edc_settlement_schedule
    property int counter: 0


    Stack.onStatusChanged:{
        if(Stack.status==Stack.Activating){
//            if(media_files.length == 0){
//                _SLOT.get_file_list(img_path);
//            }
            counter = 0;
        }
        if(Stack.status==Stack.Deactivating){
//            player.stop()
            while (media_files.length > 0) {
                media_files.pop();
            }
        }
    }

    Component.onCompleted: {
        hidden_timer.start();
        base.result_get_file_list.connect(get_result);
        base.result_general.connect(handle_general);
    }

    Component.onDestruction: {
        hidden_timer.stop();
        base.result_get_file_list.disconnect(get_result);
        base.result_general.disconnect(handle_general);
    }

    Rectangle{
        width: 10
        height: 10
        x:0
        y:0
        visible: false
        Timer{
            id: hidden_timer
            interval:1000
            repeat:true
            running:false
            triggeredOnStart:true
            onTriggered:{
                counter += 1;
                //Mandiri Auto Settlement Timer Trigger
                if (mandiri_update_schedule != undefined){
                    var hm = Qt.formatDateTime(new Date(), "HH:mm");
                    if (hm == mandiri_update_schedule && counter%3==0) {
                        console.log('MANDIRI_UPDATE_SCHEDULE_TVC', hm, mandiri_update_schedule);
                        _SLOT.start_mandiri_update_schedule();
                    }
                }
                //EDC Auto Settlement Timer Trigger
                if (edc_settlement_schedule != undefined){
                    var hm = Qt.formatDateTime(new Date(), "HH:mm");
                    if (hm == edc_settlement_schedule && counter%3==0) {
                        console.log('EDC_SETTLEMENT_SCHEDULE_TVC', hm, edc_settlement_schedule);
                        _SLOT.start_trigger_edc_settlement();
                    }
                }
            }
        }
    }


    function handle_general(result){
        var now = Qt.formatDateTime(new Date(), "yyyy-MM-dd HH:mm:ss")
        console.log("handle_general : ", now, result);
        if (result=='') return
        if (result=='MAINTENANCE_MODE_ON'){
            maintenance_mode.open();
            return;
        }
        if (result=='MAINTENANCE_MODE_OFF'){
            maintenance_mode.close();
            return;
        }
    }


    function get_result(result){
        console.log('get_result : ', result);
        if (result == "ERROR" || result == ""){
            console.log("No Media Files!");
            moving_text.text = "Playlist Media File(s) Not Found";
            mediaOnPlaying = false;
            my_layer.pop();
            return;
        } else {
            var files = JSON.parse(result);
            media_files = files.result;
            if (parseInt(files.count) == 0){
                console.log("Missing Contents, Cannot Play Media!")
                my_layer.pop();
                mediaOnPlaying = false;
                return;
            } else if (files.dir == img_path && media_files.length > 0){
                console.log("Media Files (" + media_files.length + ") : " + media_files)
                if (!mediaOnPlaying){
                    media_mode.setIndex(0);
                } else {
                    console.log("Media is Being Played Already!");
                }
            }
        }
    }


    // Play Multiple Videos
    Rectangle {
        id: media_mode
        visible: (mode=="mediaPlayer") ? true : false
        anchors.fill: parent
        color: "black"

        function setIndex(i){
            index = i;
            index %= media_files.length;
//            player.source = img_path_ + media_files[index];
//            console.log("Playing List (" + i + ") - " + player.source)
//            _SLOT.post_tvc_log(media_files[index])
//            player.play();
            mediaOnPlaying = true;
        }

        function next(){
            setIndex(index + 1);
        }

        function previous(){
            setIndex(index - 1);
        }

//        Connections {
//            target: player
//            onStopped: {
//                if (player.status == MediaPlayer.EndOfMedia) {
//                    if (index==media_files.length-1){ //Looping start from beginning
//                        media_mode.setIndex(0);
//                    } else{
//                        media_mode.next();
//                    }
//                }
//            }
//        }

//        MediaPlayer {
//            id: player
//        }

//        VideoOutput {
//            anchors.fill: parent
//            source: player
//        }

        MouseArea{
            anchors.fill: parent
            onClicked: {
//                player.stop();
                if (maintenance_mode.visible) return;
                while (media_files.length > 0) {
                    media_files.pop();
                }
                my_layer.pop();
                mediaOnPlaying = false;
            }
            onDoubleClicked: onClicked
        }
    }

    Rectangle{
        id: header_opacity
        width: parent.width
        height: 125
        color: 'white'
        visible: true
        opacity: 0.1
    }

    Image{
        id: img_logo_left
        width: 275
        height: 100
        anchors.verticalCenter: header_opacity.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 50
        source: 'source/logo/'+VIEW_CONFIG.master_logo[0]
        fillMode: Image.PreserveAspectFit
    }

    Image{
        id: img_logo_right
        width: 275
        height: 100
        anchors.verticalCenter: header_opacity.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 50
        source: ''
        fillMode: Image.PreserveAspectFit
        visible: false
    }

    Rectangle{
        id: running_text_box
        width: parent.width
        height: 100
        color: "transparent"
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        Rectangle{
            id: opacity_background
            anchors.fill: parent
            color: 'white'
            opacity: .4
        }

        Text{
            id: moving_text
            x: parent.width
            anchors.fill: running_text_box
            color: VIEW_CONFIG.running_text_color
            text: VIEW_CONFIG.running_text
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 50
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.family:"Ubuntu"

            NumberAnimation on x{
                duration: 5000
                easing.type: Easing.Linear
                from: running_text_box.width
                to: -1*moving_text.width
                loops: Animation.Infinite
            }
        }
    }

    MaintenanceMode{
        id: maintenance_mode
        z: 999999
    }

}

