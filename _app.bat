@echo off
echo Init Setting From Host
python _init_host_setting.py
echo Call Application in Watchdog
start /b /w _start.bat

