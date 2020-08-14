@echo off
pip install eSSP6
pip install --upgrade sentry-sdk==0.16.2
pip list
git config http.sslVerify false
git pull
exit

