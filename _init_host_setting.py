__author__ = "fitrah.wahyudi.imam@gmail.com"

import os
import re
import sys
import time
import json
import requests
import logging
from _cConfig import _ConfigParser
# import pywin32
import datetime


LOGGER = logging.getLogger()


def set_system_time(time_tuple):
    import win32api
    # time_tuple = ( 2012, # Year
            #       9, # Month
            #       6, # Day
            #       0, # Hour
            #      38, # Minute
            #       0, # Second
            #       0, # Millisecond
            #   )
    # http://timgolden.me.uk/pywin32-docs/win32api__SetSystemTime_meth.html
    # pywin32.SetSystemTime(year, month , dayOfWeek , day , hour , minute , second , millseconds )
    dayOfWeek = datetime.datetime(time_tuple).isocalendar()[2]
    win32api.SetSystemTime( time_tuple[:2] + (dayOfWeek,) + time_tuple[2:])
    

def get_from_url(url):
    try:
        tid = _ConfigParser.get_value('GENERAL', 'tid')
        token = _ConfigParser.get_value('GENERAL', 'token')
        s = requests.session()
        s.keep_alive = False
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Content-Type': 'application/json',
            'tid': tid, 
            'token': token,
            'User-Agent': 'MDD Vending Machine ID ['+tid+']'
        }
        s.headers['Connection'] = 'close'
        r = requests.get(url, headers=header, timeout=10)
    except Exception as e:
        LOGGER.warning((e))
        return -1, False

    try:
        response = r.json()
    except Exception as e:
        LOGGER.warning((url, e))
        return -99, False
    
    return r.status_code, response


def clean_white_space(s):
    return re.sub(r'\s+', '', s)


TEMP_FOLDER = None


def init_temp_data():
    global TEMP_FOLDER
    if not os.path.exists(sys.path[0] + '/_tTmp/'):
        os.makedirs(sys.path[0] + '/_tTmp/')
    TEMP_FOLDER = sys.path[0] + '/_tTmp/'


def store_to_temp_data(temp, content):
    LOGGER.info((temp, content))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_path = os.path.join(TEMP_FOLDER, temp)
    if len(clean_white_space(content)) == 0:
        content = '{}'
    with open(temp_path, 'w+') as t:
        t.write(content)
        t.close()


def remove_temp_data(temp):
    LOGGER.info((temp))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_file = os.path.join(TEMP_FOLDER, temp)
    if os.path.isfile(temp_file):
        os.remove(temp_file)


def exist_temp_data(temp):
    LOGGER.info((temp))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_file = os.path.join(TEMP_FOLDER, temp)
    if os.path.isfile(temp_file):
        return True
    return False


def load_from_temp_data(temp, mode='text'):
    LOGGER.info((temp))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_path = os.path.join(TEMP_FOLDER, temp)
    if not os.path.exists(temp_path):
        with open(temp_path, 'w+') as t:
            if mode == 'json':
                t.write('{}')
            else:
                t.write(' ')
            t.close()
    content = open(temp_path, 'r').read().strip()
    if len(clean_white_space(content)) == 0:
        os.remove(temp_path)
        store_to_temp_data(temp_path, '{}')
        content = '{}'
    if mode == 'json':
        return json.loads(content)
    return content


if __name__ == '__main__':
    print("pyt: Initiating Temporary Folder Data...")
    init_temp_data()
    # print("pyt: Initiating Time Setting From NTP...")
    # set_system_time()
    print("pyt: Initiating Setting From Host...")
    url = _ConfigParser.get_value('GENERAL', 'backend^server') + 'get/init-setting'
    # print("pyt: URL Host : ", url)

    status, response = get_from_url(url)
    if status == 200 and response['result'] == 'OK':
        if len(response['data']) > 0:
            print("pyt: Count Setting...", str(len(response['data'])))
            store_to_temp_data('host-setting', json.dumps(response['data']))
            for set in response['data']:
                print("pyt: Set Setting : " + str(set))
                # LOGGER.debug(('SET TO LOCAL', str(set)))
                _ConfigParser.set_value(set['section'], set['option'], set['value'])
                time.sleep(.25)
        else:
            print("pyt: No Setting Found From Host...")
    else:
        LOGGER.warning((status, response))
        print("pyt: Failed Initiating Config From Host...")
    sys.exit(0)
