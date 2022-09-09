DEPENDENCIES  :
- Python 3.5
- PyQt 5.8

External Module(s) / Librari(es) :
- pyQT,
- requests,
- WMI, (windows)
- win32, (windows)
- pyWIN32, (windows)
- pyserial,
- pyUsb,
- HID,
- ecspos,
- fpdf,
- func_timeout
- flask,
- python-printer-escpos,
- python-escpos,
- pymouse,
- pyuserinput,

Installer:
[Windows]
- PyQt5-5.5.1-gpl-Py3.4-Qt5.5.1-x64
- pywin32-221.win-amd64-py3.4

[Linux Ubuntu 20.04]
- sudo apt install libxcb-xinerama0 
- sudo apt install preload
- sudo apt install gnome-shell-extension-autohidetopbar
- sudo apt install acpi
- sudo apt-get install libqt5multimedia5-plugins qml-module-qtmultimedia
- sudo apt install vlc

###Jika Menggunakan VM Lunari Untuk Kalibrasi Touchsreen###
- sudo modprobe -r usbtouchscreen
- sudo apt install xinput-calibrator
- sudo apt install xserver-xorg-input-evdev
- sudo apt remove xserver-xorg-input-libinput
- xinput --list (cari device KTURSLibG URSG101)
- xinput_calibrator --device (device_id)
- copy output calibrator ke /usr/local/X11/xorg.conf.d/99-calibration.conf
- 


