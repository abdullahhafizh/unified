#!/bin/bash
# Put This File into /etc/init.d Folder
echo "Fix Screen Rotation"
xrandr -o normal
echo "Change Directory"
cd /home/kiosk/vm-kiosk
echo "Start Application"
python3 _app.py