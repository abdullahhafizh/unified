@echo off
pip install --upgrade sentry-sdk
pip list
git config http.sslVerify false
git pull origin master
exit

