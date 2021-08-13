@echo off
start /b /w _update.bat
echo Init Setting From Host
python _init_host_setting.py
echo Call Application
python _app.py

