__author__ = "fitrah.wahyudi.imam@gmail.com"

import logging
import requests
from _cConfig import _ConfigParser
import socket
import time
import os
import shutil
import urllib3
urllib3.disable_warnings()


def is_online_old(host="8.8.8.8", port=53, timeout=3, source=''):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        if source != '':
            LOGGER.debug(('source', source))
        return True
    except Exception as e:
        LOGGER.debug((str(e), 'source', source))
        return False


IS_ONLINE = False
LAST_REQUEST = 0
# Set Previous Waiting Time Into 1 second only
WAITING_TIME_ONLINE = 1 


def is_online(host="www.google.com", timeout=1, source=''):
    global IS_ONLINE, LAST_REQUEST
    try:
        if LAST_REQUEST != 0:
            if int(time.time()) < (LAST_REQUEST + WAITING_TIME_ONLINE):
                LOGGER.debug(('previous_state', source, IS_ONLINE))
                return IS_ONLINE
        socket.create_connection((socket.gethostbyname(host), 80), timeout)
        IS_ONLINE = True
        if source != '':
            LOGGER.debug((source, IS_ONLINE))
    except Exception as e:
        IS_ONLINE = False
        LOGGER.debug((str(e), source, IS_ONLINE))
    finally:
        LAST_REQUEST = int(time.time())
        return IS_ONLINE


NO_INTERNET = {
    'statusCode': -1,
    'statusMessage': 'Not Internet'
}
TIMEOUT = {
    'statusCode': -13,
    'statusMessage': 'Read Timeout'
}
ERROR_RESPONSE = {
    'statusCode': -99,
    'statusMessage': 'Value Error'
}
SERVICE_NOT_RESPONDING = {
    'statusCode': -999,
    'statusMessage': 'Service Response Timeout/No Response From Device'
}

DISK_SERIAL_NUMBER = ''
LOGGER = logging.getLogger()
GLOBAL_TIMEOUT = 60


def get_header(tid='', token=''):
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
        'Content-Type': 'application/json',
        'tid': tid,
        'token': token,
        'unique': DISK_SERIAL_NUMBER,
        'User-Agent': 'MDD Vending Machine ID ['+tid+']'
    }
    return header


HEADER = None


def get_from_url(url, param=None, header=None, log=True, force=False):
    if is_online(source=url) is False and force is False:
        return -1, NO_INTERNET
    if header is None:
        header = HEADER
    try:
        s = requests.session()
        s.keep_alive = False
        # s.headers['Connection'] = 'close'
        r = requests.get(url, headers=header, json=param, timeout=GLOBAL_TIMEOUT)
    except Exception as e:
        LOGGER.warning((url, NO_INTERNET, e))
        return -1, NO_INTERNET

    try:
        if '/ping' in url:
            response = r.text
        else:
            response = r.json()
    except Exception as e:
        LOGGER.warning((url, ERROR_RESPONSE, e))
        return r.status_code, ERROR_RESPONSE

    if log is True and 'get/product' not in url:
        if len(response) > 255:
            LOGGER.debug(('<URL>: ' + str(url) + " <STAT>: " + str(r.status_code) + " <RESP>: [TRIM]" + str(response[:255])))
        elif 'FAIL|' in response:
            LOGGER.debug(('<URL>: ' + str(url) + " <STAT>: " + str(r.status_code) + " <RESP>: [TRIM]" + str(response[:255])))
        else:
            LOGGER.debug(('<URL>: ' + str(url) + " <STAT>: " + str(r.status_code) + " <RESP>: " + str(response)))
    return r.status_code, response


def post_to_url(url, param=None, header=None, log=True, custom_timeout=None):
    if is_online(source=url) is False and ('apidev.mdd.co.id' not in url or 'apiv2.mdd.co.id' not in url or 'v2/diva/' not in url or 'refund/' not in url):
        return -1, NO_INTERNET
    if header is None:
        header = HEADER
    try:
        s = requests.session()
        s.keep_alive = False
        # s.headers['Connection'] = 'close'
        __timeout = GLOBAL_TIMEOUT if custom_timeout is None else custom_timeout
        if '/v2/ppob' in url or 'http://apiv2.mdd.co.id:10107' in url or 'http://apidev.mdd.co.id:28194' in url:
            __timeout = 180 if custom_timeout is None else custom_timeout
            r = requests.post(url, headers=header, json=param, timeout=__timeout)
        elif 'https' in url and _ConfigParser.get_set_value('GENERAL', 'ssl^verify', '0') == '0':
            r = requests.post(url, headers=header, json=param, timeout=__timeout, verify=False)
        else:
            r = requests.post(url, headers=header, json=param, timeout=__timeout)
    except requests.exceptions.Timeout as t:
        LOGGER.warning((url, TIMEOUT, t))
        return -13, TIMEOUT
    except Exception as e:
        LOGGER.warning((url, NO_INTERNET, e))
        return -1, NO_INTERNET

    try:
        if '/ping' in url:
            response = r.text
        else:
            response = r.json()
    except Exception as e:
        LOGGER.warning((url, ERROR_RESPONSE, e))
        return r.status_code, ERROR_RESPONSE

    if log is True:
        if len(response) > 255:
            LOGGER.debug(('<URL>: ' + str(url) + " <POST> : " + str(param) + " <RESP> : [TRIM]" + str(response[:255])))
        elif 'FAIL|' in response:
            LOGGER.debug(('<URL>: ' + str(url) + " <POST> : " + str(param) + " <RESP> : [TRIM]" + str(response[:255])))
        else:
            LOGGER.debug(('<URL>: ' + str(url) + " <POST> : " + str(param) + " <RESP> : " + str(response)))
    return r.status_code, response


def get_local(url, param=None, log=True):
    try:
        s = requests.session()
        s.keep_alive = False
        r = requests.get(url, json=param, timeout=GLOBAL_TIMEOUT)
    except Exception as e:
        LOGGER.warning((url, SERVICE_NOT_RESPONDING, e))
        return -1, SERVICE_NOT_RESPONDING

    try:
        response = r.json()
    except Exception as e:
        LOGGER.warning((url, ERROR_RESPONSE, e))
        return r.status_code, ERROR_RESPONSE

    if log is True:
        LOGGER.debug(('<URL>: ' + str(url) + " <STAT>: " + str(r.status_code) + " <RESP>: " + str(response)))
    return r.status_code, response


def item_download(url, path, name=None):
    if 'mdd.co.id:11199' in url:
        url = url.replace('11199', '2142')
    if name is None:
        item = url.split('/')[-1]
    else:
        item = name
    if not os.path.exists(path):
        os.makedirs(path)
    file = os.path.join(path, item)
    if os.path.exists(file):
        return True, item
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        return False, item
    with open(file, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    LOGGER.debug(('stream down', file, url))
    del r
    return True, item


def stream_large_download(url, item, temp_path, final_path):
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    file = os.path.join(temp_path, item)
    new_file = os.path.join(final_path, item)
    if os.path.exists(file):
        shutil.copy(new_file, file)
        LOGGER.debug(('copy backup', file, new_file))
        return True, item
    if os.path.exists(new_file):
        return True, item
    r = requests.get(url, stream=True, allow_redirects=True, verify=False)
    if r.status_code != 200:
        return False, item
    with open(file, 'wb') as media:
        # for chunk in r.iter_content(chunk_size=1024*1024):
        for chunk in r.iter_content(chunk_size=256*256):
            if chunk:
                media.write(chunk)
    shutil.copy(file, new_file)
    # os.remove(file)
    LOGGER.debug(('stream down', file, url))
    del r
    return True, item
