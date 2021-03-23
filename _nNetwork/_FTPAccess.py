__author__ = "fitrah.wahyudi.imam@gmail.com"

import os
from time import sleep
import sys
import logging
import ftplib
from _cConfig import _Common


LOGGER = logging.getLogger()
FTP_SERVER = _Common.FTP['host']
FTP_USER = _Common.FTP['user']
FTP_PASS = _Common.FTP['pass']
FTP_PORT = _Common.FTP['port']
REMOTE_PATH = _Common.FTP['path']
BUFFER = 1024
LOCAL_PATH = os.path.join(sys.path[0], '_rRemoteFiles')
if not os.path.exists(sys.path[0] + '/_rRemoteFiles/'):
    os.makedirs(sys.path[0] + '/_rRemoteFiles/')

FTP = None
HOST_BID = 1
MAX_ATTEMP = 1
DELAY_TIME = 1


def redefine_config():
    global FTP_SERVER, FTP_USER, FTP_PASS, FTP_PORT, REMOTE_PATH
    if _Common.C2C_MODE is True and HOST_BID == 1:
        FTP_SERVER = _Common.FTP_C2C['host']
        FTP_USER = _Common.FTP_C2C['user']
        FTP_PASS = _Common.FTP_C2C['pass']
        FTP_PORT = _Common.FTP_C2C['port']
        REMOTE_PATH = _Common.FTP_C2C['path']


def init_ftp():
    global FTP
    try:
        redefine_config()
        FTP = ftplib.FTP(FTP_SERVER, FTP_USER, FTP_PASS)
        LOGGER.debug(('init_ftp', 'TRUE'))
    except Exception as e:
        #_Common.online_logger(e, 'connection')
        LOGGER.warning(('init_ftp', str(e)))
        if FTP is not None:
            FTP.quit()


def send_file(local_path, remote_path=None):
    global FTP
    result = {}
    result["success"] = False
    if remote_path is None:
        remote_path = REMOTE_PATH
    if FTP is None:
        init_ftp()
    try:
        FTP.cwd(remote_path)
        local_file = open(local_path)
        file_name = local_path.split('/')[-1]
        FTP.storbinary('STOR '+file_name, local_file)
        local_file.close()
        LOGGER.debug((file_name, local_path, remote_path))
        result = {
            "success": True,
            "host": FTP_SERVER,
            "remote_path": remote_path,
            "local_path": local_path,
        }
    except Exception as e:
        LOGGER.warning((str(e)))
        #_Common.online_logger([local_path, remote_path], 'connection')
        result = {
            "success": False,
            "host": FTP_SERVER,
            "remote_path": remote_path,
            "local_path": local_path,
        }
    finally:
        if FTP is not None:
            FTP.quit()
        FTP = None
        return result


def get_file(file, remote_path=None):
    global FTP
    result = False
    if file is None:
        LOGGER.warning(('get_file', 'File Param is Missing'))
        return result
    if remote_path is None:
        remote_path = REMOTE_PATH
    if FTP is None:
        init_ftp()
    try:
        remote_file = os.path.join(remote_path, file)
        local_file = os.path.join(LOCAL_PATH, file)
        local_file_create = open(local_file, 'wb')
        attemp = 0
        while True:
            attemp += 1
            FTP.retrbinary('RETR ' + remote_file, local_file_create.write, BUFFER)
            local_file_create.close()
            local_file_check = open(local_file, 'r').readlines()
            if len(local_file_check) == 0:
                os.remove(local_file)
                LOGGER.warning((remote_file, 'Not Exist', str(local_file_check)))
                result = False
            else:
                LOGGER.info((local_file, remote_file, str(local_file_check)))
                result = {
                    "host": FTP_SERVER,
                    "remote_path": remote_file,
                    "local_path": local_file,
                    "content": local_file_check,
                }
                break
            if attemp == MAX_ATTEMP :
                break
            sleep(DELAY_TIME)
    except Exception as e:
        LOGGER.warning((str(e)))
        #_Common.online_logger([file, remote_path], 'connection')
        return False
    finally:
        if FTP is not None:
            FTP.quit()
        FTP = None
        return result

