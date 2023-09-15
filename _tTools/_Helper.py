__author__ = 'wahyudi@multidaya.id'

import logging
from multiprocessing.dummy import Pool as ThreadPool
import uuid
import time
import datetime
from _cConfig import _ConfigParser
import random
import binascii
from _nNetwork import _HTTPAccess
import subprocess
from sys import _getframe as whois
import re
import hmac
import hashlib 
# import inspect

# Hardcoded Maximum Thread at a time
MAX_THREAD = 16

LOGGER = logging.getLogger()
THREADS = ThreadPool(MAX_THREAD)


def get_thread():
    return THREADS
    

def get_global_port(device_name, default_baud_rate, default_port, default_timeout=1):
    baudrate = default_baud_rate
    port = default_port
    timeout = default_timeout
    if _ConfigParser.get_value(device_name, 'baudrate'):
        baudrate = int(_ConfigParser.get_value(device_name, 'baudrate'))
    if _ConfigParser.get_value(device_name, 'port'):
        port = _ConfigParser.get_value(device_name, 'port')
    if _ConfigParser.get_value(device_name, 'timeout'):
        timeout = int(_ConfigParser.get_value(device_name, 'timeout'))
    __RES = {'baudrate': baudrate, 'port': port, 'timeout': timeout}
    LOGGER.debug((device_name, __RES))
    return __RES


def now():
    return int(time.time()) * 1000


def epoch(mode='DEFAULT'):
    if mode == 'MDS':
        return str(now())
    return int(time.time())


def today():
    now_time = time.time()
    midnight = now_time - now_time % 86400 + time.timezone
    return int(midnight) * 1000


def today_time():
    now_time = time.time()
    midnight = now_time - (now_time % 86400) + time.timezone
    return int(midnight)


TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def convert_epoch(t = None, f=''):
    if t is None:
        t = time.time()
    if len(f) == 0:
        f = TIME_FORMAT
    return datetime.datetime.fromtimestamp(t).strftime(f)


def time_string(f=''):
    if len(f) == 0:
        f = TIME_FORMAT
    return datetime.datetime.now().strftime(f)


def get_uuid():
    return str(uuid.uuid1().hex)


def get_value_from(__key, __map, __default=None):
    if __map is None:
        return __default
    if __key in __map.keys():
        return __map[__key]
    return __default


def get_random_chars(length=3, chars='ABCDEFGHJKMNPQRSTUVWXYZ'):
    __random = ''
    i = 0
    while i < length:
        __random += random.choice(chars)
        i += 1
    return __random


def get_random_num(start=0, end=1):
    return random.uniform(start, end)


def get_number_from_time(t='08:00'):
    return int(t.replace(':', ''))


def file2crc32(filename):
    try:
        buf = open(filename, 'rb').read()
        buf = (binascii.crc32(buf) & 0xFFFFFFFF)
        return "%08X" % buf
    except Exception as e:
        LOGGER.warning(('file2crc32', filename, str(e)))
        return False


def is_online(source=''):
    return _HTTPAccess.is_online(source=source)


def get_ds(string, length=4, log=False):
    salt = 'MDDCOID'
    __ = str(abs(hash(string+salt)) % (10 ** length))
    if len(__) != length:
        __ = (__[0] * (length-len(__))) + __
    if log is True:
        LOGGER.debug(('length', length, 'hash', __, 'string', str(string+salt)))
    return __


def full_row_reverse_hexdec(string):
    __hex1 = string[46:54]
    __hex2 = string[54:62]
    __front = string[:46]
    __back = string[62:]
    __dec1 = reverse_hexdec(string=__hex1, mode='BIG_ENDIAN')
    __dec2 = reverse_hexdec(string=__hex2, mode='BIG_ENDIAN')
    return str(__front) + str(__dec1).zfill(8) + str(__dec2).zfill(8) + str(__back)


def reverse_hexdec(string, mode="BIG_ENDIAN"):
    try:
        if mode in ['BIG_ENDIAN']:
            return int("".join(map(str.__add__, string[-2::-2], string[-1::-2])), 16)
        else:
            return int(string, 16)
    except:
        return 0


def dump(s, iterate=False):
    caller = whois(1).f_code.co_name
    if type(s) == str:
        print('pyt: DUMP [' + str(caller) + '] >>> ' + str(type(s)) + ' >>> ' + str(s))
    elif type(s) == list:
        if iterate is True:
            for l in s:
                print('pyt: DUMP [' + str(caller) + '] >>> ' + str(type(l)) + ' >>> ' + str(l))
        else:
            print('pyt: DUMP [' + str(caller) + '] >>> ' + str(type(s)) + ' >>> ' + str(s))
    else:
        print('pyt: DUMP [' + str(caller) + '] >>> ' + str(type(s)) + ' >>> ' + str(s))


def os_command(command, key, reverse=False):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    response = process.communicate()[0].decode('utf-8').strip().split("\r\n")
    dump(command)
    dump(response)
    if len(response) > 0:
        if not reverse and key in response[-1]:
            return True
        elif reverse is True and key not in response:
            return True
        else:
            return False
    else:
        return False


def execute_console(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    response = process.communicate()[0].decode('utf-8').strip().split("\r\n")
    LOGGER.debug((command, response))
    # dump(command)
    # dump(response)
    return response


def whoami():
    return whois(1).f_code.co_name


def empty(s):
    if s is None:
        return True
    elif type(s) == dict and len(s.keys()) == 0:
        return True
    elif type(s) == bool and s is False:
        return True
    elif type(s) == int and s == 0:
        return True
    elif type(s) != int and len(s) == 0:
        return True
    else:
        return False


def strtolist(string=None, length=2):
    if string is None:
        return []
    n = '.' * length
    return re.findall(n, string)


def compare_time(time_int = 22):
    return True if (time.gmtime() + 7) > time_int else False


def hash_sha256_signature(key, message):
    byte_key = binascii.unhexlify(key)
    message = message.encode()
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()


def url_to_endpoint(url):
    if empty(url):
        return ''
    new_url = url.split('://')[1].split('/')
    return "/".join(new_url[1:])


def get_char_from(s):
    return ''.join([i for i in s if not i.isdigit()])


def get_int(s):
    if s is None: return 0
    if type(s) == str: s = s.replace(':', '')
    return int(s)


def valid_ip(ip=None, version=4):
    if empty(ip): return False
    if version != 4: return False
    return [0<=int(x)<256 for x in re.split('\.',re.match(r'^\d+\.\d+\.\d+\.\d+$',ip).group(0))].count(True)==version
