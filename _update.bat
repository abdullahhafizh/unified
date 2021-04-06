@echo off
pip install pika
pip install pycryptodome
pip install Flask
pip install func-timeout
pip list
git config http.sslVerify false
git pull origin master
exit

