@echo off
pip install elevate
pip list
git config http.sslVerify false
git pull origin master
exit

