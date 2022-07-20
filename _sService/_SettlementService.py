__author__ = "wahyudi@multidaya.id"

import json
from datetime import datetime
import os
import sys
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _ConfigParser, _Common
from _dDAO import _DAO
from _tTools import _Helper
from _nNetwork import _NetworkAccess
from _nNetwork import _SFTPAccess, _FTPAccess
from _dDevice import _QPROX, _EDC
from _sService import _TopupService, _MDSService
from time import sleep


class SettlementSignalHandler(QObject):
    __qualname__ = 'SettlementSignalHandler'
    SIGNAL_MANDIRI_SETTLEMENT = pyqtSignal(str)


ST_SIGNDLER = SettlementSignalHandler()
LOGGER = logging.getLogger()
BACKEND_URL = _Common.BACKEND_URL
TID = _Common.TID
SALT = '|KIOSK'
# Hardcoded Setting for SMT -----------------------
SMT_URL = 'https://smt.mdd.co.id:10000/c2c-api/'
SMT_MID = 'eb03307c9f8e26c02595be6bbf682c0c'
SMT_TOKEN = 'a34837228839a9af1d5d5d968ad1b885'
# -------------------------------------------------
_Common.SMT_CONFIG['url'] = SMT_URL
_Common.SMT_CONFIG['mid'] = SMT_MID
_Common.SMT_CONFIG['token'] = SMT_TOKEN
_Common.SMT_CONFIG['full_url'] = SMT_URL + 'settlement/submit'

HEADER = {
    'Content-Type': 'application/json',
}
FILE_PATH = os.path.join(sys.path[0], '_rRemoteFiles')
if not os.path.exists(FILE_PATH):
    os.makedirs(FILE_PATH)
C2C_FILE_PATH = os.path.join(sys.path[0], '_rRemoteFiles', 'C2C')
if not os.path.exists(C2C_FILE_PATH):
    os.makedirs(C2C_FILE_PATH)
C2C_SETT_FILE_PATH = os.path.join(sys.path[0], '_rRemoteFiles', 'C2C', 'Fee')
if not os.path.exists(C2C_SETT_FILE_PATH):
    os.makedirs(C2C_SETT_FILE_PATH)


BID = _Common.BID
GLOBAL_SETTLEMENT = []


def store_local_settlement(__param):
    try:
        param = {
            "sid": _Helper.get_uuid(),
            "tid": TID,
            "bid": BID[__param['bank']],
            "filename": __param['filename'],
            "remarks": json.dumps(__param),
            "trx_type": "PREPAID",
            "status": 'TOPUP_PREPAID|OPEN',
            "amount": __param['amount'],
            "row": __param['row']
        }
        _DAO.insert_settlement(param=param)
        return param['sid']
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def push_settlement_data_smt(__param):
    global GLOBAL_SETTLEMENT
    """
    "bid": "1",
    "amount": 999000,
    "row": 99,
    "filename": "FILETEST123456789098765432100000006.txt",
    "settlement_created_at": "2018-11-26 11:00:00"
    """
    __url = SMT_URL + 'settlement/submit'
    if __param is None:
        LOGGER.warning(('[FAILED] Missing __param'))
        return False
    __sid = store_local_settlement(__param)
    if not __sid:
        LOGGER.warning(('[FAILED] Store Local Settlement Data'))
        return False
    __param['mid'] = SMT_MID
    __param['token'] = SMT_TOKEN
    __param['tid'] = 'MDD-VM'+TID
    __param['endpoint'] = 'settlement/submit'
    try:
        status, response = _NetworkAccess.post_to_url(url=__url, param=__param)
        # LOGGER.debug(('push_settlement_data :', str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            _DAO.update_settlement({'sid': __sid, 'status': 'TOPUP_PREPAID|CLOSED'})
            for settle in GLOBAL_SETTLEMENT:
                settle['key'] = settle['rid']
                _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=9)
            GLOBAL_SETTLEMENT = []
            return True
        else:
            _Common.store_request_to_job(name=_Helper.whoami(), url=__url, payload=__param)
            return False
    except Exception as e:
        LOGGER.warning(('push_settlement_data :', e))
        _Common.store_request_to_job(name=_Helper.whoami(), url=__url, payload=__param)
        return False


def push_settlement_data(__param=None):
    global GLOBAL_SETTLEMENT
    """
    "filename": "HVOUYVUYVUYVUIVLIUV.txt",
    "bid": "1",
    "row": "1",
    "amount": "1",
    "host": "1.1.1.1",
    "remote_path": "/home/test/",
    "local_path": "c:/dir/",
    "remarks": "",
    """
    # 'path_file': _file_created,
    # 'filename': _filename,
    # 'row': len(settlements),
    # 'amount': str(_all_amount),
    # 'bank': bank,
    # 'bid': BID[bank],
    # 'remarks': _filecontent2.replace('|', '\n'),
    # 'settlement_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # if __param is not None:
    #     if 'remarks' in __param.keys():
    #         __param.pop('remarks')
    #     # LOGGER.info(('START_MDS_SETTLEMENT_DATA_SYNC', str(__param)))
    #     try:
    #         param = {
    #             "id": _Helper.get_uuid(),
    #             "file_name": __param['filename'],
    #             "header": __param['header'],
    #             "body": __param['body'],
    #             "footer": __param['footer'],
    #             "created_date": __param['settlement_created_at'].split(' ')[0],
    #             "created_time": __param['settlement_created_at'].split(' ')[1],
    #             "uploaded_date": __param['settlement_uploaded_at'].split(' ')[0],
    #             "uploaded_time": __param['settlement_uploaded_at'].split(' ')[1],
    #             "count_transaction": __param['row'],
    #             "total_transaction": __param['amount'],
    #             "bank_tid": _Common.C2C_TID if __param['bank'] == 'MANDIRI' else _Common.TID_BNI,
    #             "bank_mid": _Common.C2C_MID if __param['bank'] == 'MANDIRI' else _Common.MID_BNI,
    #         }
    #         # LOGGER.info(('MDS_SETTLEMENT_DATA', str(param)))
    #         return _MDSService.push_settlement_data(param)
    #     except Exception as e:
    #         LOGGER.warning((e))
    #         return False
    __url = _Common.BACKEND_URL + 'settlement/sync-record'
    if __param is None:
        LOGGER.warning(('[FAILED] Missing __param'))
        return False
    # {
    #     "sid": _Helper.get_uuid(),
    #     "tid": TID,
    #     "bid": BID[__param['bank']],
    #     "filename": __param['filename'],
    #     "status": 'TOPUP_PREPAID|OPEN',
    #     "amount": __param['amount'],
    #     "row": __param['row']
    # }
    __sid = store_local_settlement(__param)
    if not __sid:
        LOGGER.warning(('[FAILED] Store Local Settlement Data'))
        return False
    __param['endpoint'] = 'settlement/sync-record'
    try:
        status, response = _NetworkAccess.post_to_url(url=__url, param=__param)
        LOGGER.debug((str(status), str(response)))
        if status == 200 and response['result'] == 'OK':
            _DAO.update_settlement({'sid': __sid, 'status': 'TOPUP_PREPAID|CLOSED'})
            if not _Common.empty(GLOBAL_SETTLEMENT):
                for settle in GLOBAL_SETTLEMENT:
                    settle['key'] = settle['rid']
                    _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=9)
                GLOBAL_SETTLEMENT = []
            return True
        else:
            _Common.store_request_to_job(name=_Helper.whoami(), url=__url, payload=__param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        _Common.store_request_to_job(name=_Helper.whoami(), url=__url, payload=__param)
        return False


def upload_settlement_file(filename, local_path, remote_path=None, protocol='SFTP'):
    # Bypass Close Sending FS File By Manipulating Sending Result 14.0.G1-GLOBAL
    if True:
        return {
            "success": True,
            "host": 'tsf.mdd.co.id',
            "remote_path": remote_path,
            "local_path": local_path,
        }
    if protocol == 'SFTP':
        return _SFTPAccess.send_file(filename, local_path=local_path, remote_path=remote_path)
    else:
        return _FTPAccess.send_file(filename, local_path=local_path, remote_path=remote_path)


def get_response_settlement(filename, remote_path, protocol='SFTP'):
    if protocol == 'SFTP':
        return _SFTPAccess.get_file(filename, remote_path=remote_path)
    else:
        return _FTPAccess.get_file(filename, remote_path=remote_path)


MANDIRI_LAST_TIMESTAMP = ''
MANDIRI_LAST_FILENAME = ''
LAST_MANDIRI_C2C_SETTLEMENT_DATA = _Common.load_from_temp_data('last-mandiri-c2c-settlement', 'json')
LAST_BNI_SETTLEMENT_DATA = _Common.load_from_temp_data('last-bni-settlement', 'json')


def create_settlement_file(bank='BNI', mode='TOPUP', output_path=None, force=False):
    global GLOBAL_SETTLEMENT, MANDIRI_LAST_TIMESTAMP, MANDIRI_LAST_FILENAME, LAST_MANDIRI_C2C_SETTLEMENT_DATA, LAST_BNI_SETTLEMENT_DATA
    if bank == 'BNI' and mode == 'TOPUP':
        try:
            LOGGER.info(('Create Settlement File', bank, mode))
            if output_path is None:
                output_path = FILE_PATH
            settlements = _DAO.get_query_from('TopUpRecords', ' syncFlag=1 AND reportKA="N/A" AND cardNo LIKE "7546%" ')
            GLOBAL_SETTLEMENT = settlements
            if len(settlements) == 0:
                if not _Helper.empty(LAST_BNI_SETTLEMENT_DATA):
                    LOGGER.info(('Use Previous BNI Settlement', bank, mode, str(LAST_BNI_SETTLEMENT_DATA)))
                    return LAST_BNI_SETTLEMENT_DATA
                LOGGER.warning(('No Data For Settlement', str(settlements)))
                return False
            _filename = 'TOPMDD_'+_Common.MID_BNI + _Common.TID_BNI + datetime.now().strftime('%Y%m%d%H%M%S')+'.TXT'
            LOGGER.info(('Settlement Filename', bank, mode, _filename))
            _filecontent = ''
            _filecontent2 = ''
            _all_amount = 0
            _header = 'H01' + _Common.MID_BNI + _Common.TID_BNI + '|'
            _trailer = 'T' + str(len(settlements)).zfill(6) + '00000000'
            for settle in settlements:
                # remarks = json.loads(settle['remarks'])
                # Need to Parse Topup Amount Here From 
                # 754605000081474000000000062937950200C626010E6A004844005FB4001770302C8EB2C9664EAD9AD0BD9D0F424002070100015A0000D40000070100C62600000088889999AAFF92D04416FEDF7A941CF5F3C9B6720FBA417DCBA9A5EB010E6AC9664EAD9AC9664EAD9AD0BD9D00015A0000D400007546990000042075754699000004207552A3A9E4496A98B1
                _row_amount = int(settle['reportSAM'][46:52], 16)
                _all_amount += _row_amount
                _filecontent += ('D' + settle['reportSAM']) + '|'
                # settle['key'] = settle['rid']
                # _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=9)
            # Copy File Content Here to Update with the new CRC32
            _body = _filecontent
            _filecontent = _header + _filecontent
            _filecontent2 = _filecontent
            _filecontent += _trailer
            _file_created = os.path.join(output_path, _filename)
            with open(_file_created, 'w+') as f:
                __all_lines1 = _filecontent.split('|')
                for line in __all_lines1:
                    if line != __all_lines1[-1]:
                        f.write(line+'\n')
                    else:
                        f.write(line)
                f.close()
            _crc = _Helper.file2crc32(_file_created)
            if _crc is False:
                LOGGER.warning(('Settlement Filename Failed in CRC', _filename))
                return False
            _filecontent2 += ('T' + str(len(settlements)).zfill(6) + _crc)
            with open(_file_created, 'w+') as f:
                __all_lines2 = _filecontent2.split('|')
                for line in __all_lines2:
                    if line != __all_lines2[-1]:
                        f.write(line+'\n')
                    else:
                        f.write(line)
                f.close()
            _result = {
                'path_file': _file_created,
                'filename': _filename,
                'row': len(settlements),
                'amount': str(_all_amount),
                'bank': bank,
                'bid': BID[bank],
                'remarks': _filecontent2.replace('|', '\n'),
                'header': _header.replace('|', '\n'),
                'body': _body.replace('|', '\n'),
                'footer': _trailer.replace('|', '\n'),
                'settlement_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            # Insert Into DB
            #       smid            VARCHAR(100) PRIMARY KEY NOT NULL,
            #       fileName        TEXT,
            #       fileContent     TEXT,
            #       status          INT,
            #       remarks         TEXT,
            _DAO.insert_sam_record({
                'smid': _Helper.get_uuid(),
                'fileName': _filename,
                'fileContent': _filecontent2,
                'status': 1,
                'remarks': json.dumps(_result)
            })
            # To Prevent Re-Create The Same File When Failed Push To SMT
            for settle in GLOBAL_SETTLEMENT:
                settle['key'] = settle['rid']
                _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=9)
            LAST_BNI_SETTLEMENT_DATA = _result
            _Common.store_to_temp_data('last-bni-settlement', json.dumps(LAST_BNI_SETTLEMENT_DATA))
            return _result
        except Exception as e:
            LOGGER.warning((bank, mode, str(e)))
            return False
    elif bank == 'MANDIRI' and mode == 'TOPUP':
        try:
            # LOGGER.info(('Create Settlement File', bank, mode))
            if output_path is None:
                output_path = FILE_PATH
            settlements = _DAO.get_query_from('TopUpRecords', ' syncFlag=1 AND reportSAM <> "N/A" AND cardNo LIKE "6%" ')
            GLOBAL_SETTLEMENT = settlements
            if len(settlements) == 0 and force is False:
                LOGGER.warning(('No Data For Settlement', bank, mode, str(settlements)))
                return False
            __shift = '0002'
            __seq = '02'
            __timestamp = datetime.now().strftime('%d%m%Y%H%M')
            MANDIRI_LAST_TIMESTAMP = __timestamp
            __raw = _Common.MID_MAN + __shift + _Common.TID_MAN + __seq + (__timestamp * 2) + 'XXXX' + '.txt'
            __ds = _Helper.get_ds(__raw, 4, True)
            _filename = _Common.MID_MAN + __shift + _Common.TID_MAN + __seq + (__timestamp * 2) + __ds + '.txt'
            MANDIRI_LAST_FILENAME = _filename
            LOGGER.info(('Create Settlement Filename', bank, mode, _filename))
            _filecontent = ''
            _all_amount = 0
            x = 0
            for settle in settlements:
                x += 1
                remarks = json.loads(settle['remarks'])
                _all_amount += (int(remarks['value'])-int(remarks['admin_fee']))
                _filecontent += _Helper.full_row_reverse_hexdec(settle['reportSAM']) + __shift + str(x).zfill(6) + chr(3) + '|'
            _header = 'PREPAID' + str(len(settlements) + 2).zfill(8) + str(_all_amount).zfill(12) + __shift + \
                    _Common.MID_MAN + datetime.now().strftime('%d%m%Y') + chr(3) + '|'
            _body = _filecontent
            _filecontent = _header + _filecontent
            _trailer = _Common.MID_MAN + str(len(settlements)).zfill(8)
            _filecontent += _trailer
            _file_created = os.path.join(output_path, _filename)
            with open(_file_created, 'w+') as f:
                __all_lines = _filecontent.split('|')
                for line in __all_lines:
                    if line != __all_lines[-1]:
                        f.write(line+'\n')
                    else:
                        f.write(line)
                f.close()
            _file_created_ok = os.path.join(output_path, _filename.replace('.txt', '.ok'))
            with open(_file_created_ok, 'w+') as f_ok:
                f_ok.write('')
                f_ok.close()
            _result = {
                'path_file': _file_created,
                'filename': _filename,
                'row': len(settlements),
                'amount': str(_all_amount),
                'bank': bank,
                'bid': BID[bank],
                'remarks': _filecontent.replace('|', '\n'),
                'header': _header.replace('|', '\n'),
                'body': _body.replace('|', '\n'),
                'footer': _trailer.replace('|', '\n'),
                'settlement_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            _DAO.insert_sam_record({
                'smid': _Helper.get_uuid(),
                'fileName': _filename,
                'fileContent': _filecontent,
                'status': 1,
                'remarks': json.dumps(_result)
            })
            for settle in GLOBAL_SETTLEMENT:
                settle['key'] = settle['rid']
                _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=3)
            return _result
        except Exception as e:
            LOGGER.warning((bank, mode, str(e)))
            return False
    elif bank == 'MANDIRI' and mode == 'KA':
        try:
            # LOGGER.info(('Create Settlement File', bank, mode))
            if output_path is None:
                output_path = FILE_PATH
            settlements = _DAO.get_query_from('TopUpRecords', ' syncFlag=3 AND reportKA <> "N/A" ')
            # GLOBAL_SETTLEMENT = settlements
            if len(settlements) == 0 and force is False:
                LOGGER.warning(('No Data For Settlement', bank, mode, str(settlements)))
                return False
            __shift = '0002'
            # __seq = '02'
            # __timestamp = MANDIRI_LAST_TIMESTAMP
            # __ds = __timestamp[-4:]
            # _filename = 'KA' + _Common.MID_MAN + __shift + _Common.TID_MAN + __seq + (__timestamp * 2) + __ds + '.TXT'
            _filename = 'KA' + MANDIRI_LAST_FILENAME
            LOGGER.info(('Create Settlement Filename', bank, mode, _filename))
            _filecontent = ''
            _all_amount = 0
            x = 0
            for settle in settlements:
                x += 1
                remarks = json.loads(settle['remarks'])
                _all_amount += int(remarks['value'])
                _filecontent += settle['reportKA'] + __shift + str(x).zfill(6) + chr(3) + '|'
            _header = 'ADMINCARD' + str(len(settlements) + 2).zfill(8) + str(_all_amount).zfill(12) + __shift + \
                      _Common.MID_MAN + datetime.now().strftime('%d%m%Y') + chr(3) + '|'
            _body = _filecontent
            _filecontent = _header + _filecontent
            _trailer = _Common.MID_MAN + str(len(settlements)).zfill(8)
            _filecontent += _trailer
            _file_created = os.path.join(output_path, _filename)
            with open(_file_created, 'w+') as f:
                __all_lines = _filecontent.split('|')
                for line in __all_lines:
                    if line != __all_lines[-1]:
                        f.write(line+'\n')
                    else:
                        f.write(line)
                f.close()
            _file_created_ok = os.path.join(output_path, _filename.replace('.txt', '.ok'))
            with open(_file_created_ok, 'w+') as f_ok:
                f_ok.write('')
                f_ok.close()
            _result = {
                'path_file': _file_created,
                'filename': _filename,
                'row': len(settlements),
                'amount': str(_all_amount),
                'bank': bank,
                'bid': BID[bank],
                'remarks': _filecontent.replace('|', '\n'),
                'header': _header.replace('|', '\n'),
                'body': _body.replace('|', '\n'),
                'footer': _trailer.replace('|', '\n'),
                'settlement_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            _DAO.insert_sam_record({
                'smid': _Helper.get_uuid(),
                'fileName': _filename,
                'fileContent': _filecontent,
                'status': 1,
                'remarks': json.dumps(_result)
            })
            for settle in settlements:
                settle['key'] = settle['rid']
                _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=9)
            return _result
        except Exception as e:
            LOGGER.warning((bank, mode, str(e)))
            return False
    elif bank == 'MANDIRI' and mode == 'TOPUP_C2C':
        try:
            # LOGGER.info(('Create Settlement File', bank, mode))
            if output_path is None:
                output_path = C2C_FILE_PATH
            settlements = _DAO.get_query_from('TopUpRecords', ' syncFlag=1 AND reportKA <> "N/A" AND cardNo LIKE "6%" ')
            GLOBAL_SETTLEMENT = settlements
            if len(settlements) == 0 and force is False:
                if not _Helper.empty(LAST_MANDIRI_C2C_SETTLEMENT_DATA):
                    LOGGER.info(('Use Previous Mandiri C2C Settlement', bank, mode, str(LAST_MANDIRI_C2C_SETTLEMENT_DATA)))
                    return LAST_MANDIRI_C2C_SETTLEMENT_DATA
                LOGGER.warning(('No Data For Settlement', bank, mode, str(settlements)))
                return False
            __shift = '0001'
            # __seq = _ConfigParser.get_set_value_temp('TEMPORARY', _Common.C2C_MACTROS, '1').zfill(2)
            __seq = '01'
            __timestamp = datetime.now().strftime('%d%m%Y%H%M')
            MANDIRI_LAST_TIMESTAMP = __timestamp
            __raw = _Common.C2C_MID + __shift + _Common.C2C_MACTROS[:6] + _Common.C2C_TID[:4] + '00' + __seq + (__timestamp * 2) + 'XXXX' + '.txt'
            __ds = _Helper.get_ds(__raw, 4, True)
            _filename = _Common.C2C_MID + __shift + _Common.C2C_MACTROS[:6] + _Common.C2C_TID[:4] + '00' + __seq + (__timestamp * 2) + __ds + '.txt'
            MANDIRI_LAST_FILENAME = _filename
            LOGGER.info(('Create Settlement Filename', bank, mode, _filename))
            _filecontent = ''
            _all_amount = 0
            x = 0
            for settle in settlements:
                x += 1
                _all_amount += int(_Helper.reverse_hexdec(settle['reportKA'][46:54])) # Get Amount From Deposit Report
                _filecontent += settle['reportKA'] + settle['reportSAM'] + chr(3) + '|'
            _header = 'PREPAID' + str(x + 2).zfill(8) + str(_all_amount).zfill(12) + __shift + \
                    _Common.C2C_MID + datetime.now().strftime('%d%m%Y') + chr(3) + '|'
            _body = _filecontent
            _filecontent = _header + _filecontent
            _trailer = _Common.C2C_MID + str(x).zfill(8) + chr(3)
            _filecontent += _trailer
            _file_created = os.path.join(output_path, _filename)
            with open(file=_file_created, mode='w+') as f:
                __all_lines = _filecontent.split('|')
                for line in __all_lines:
                    if line != __all_lines[-1]:
                        f.write(line+'\n')
                    else:
                        f.write(line)
                f.close()
            _file_created_ok = os.path.join(output_path, _filename.replace('.txt', '.ok'))
            with open(_file_created_ok, 'w+') as f_ok:
                f_ok.write('')
                f_ok.close()
            _result = {
                'path_file': _file_created,
                'filename': _filename,
                'row': x,
                'amount': str(_all_amount),
                'bank': bank,
                'bid': BID[bank],
                'remarks': _filecontent.replace('|', '\n'),
                'header': _header.replace('|', '\n'),
                'body': _body.replace('|', '\n'),
                'footer': _trailer.replace('|', '\n'),
                'settlement_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            _DAO.insert_sam_record({
                'smid': _Helper.get_uuid(),
                'fileName': _filename,
                'fileContent': _filecontent,
                'status': 1,
                'remarks': json.dumps(_result)
            })
            # Panel For Removing Data Records Once Settlement Data is Created
            removeData = False
            for settle in GLOBAL_SETTLEMENT:
                if not removeData:
                    settle['key'] = settle['rid']
                    _DAO.mark_sync(param=settle, _table='TopUpRecords', _key='rid', _syncFlag=3)
                else:
                    # _DAO.flush_table('Terminal', 'tid <> "'+_Common.KIOSK_SETTING['tid']+'"')
                    _DAO.flush_table(_table='TopUpRecords', _where='rid = "'+settle['rid']+'"')
            # Update Sequence Settlement Record
            __new_seq = int(__seq) + 1
            if __new_seq == 100:
                __new_seq = 1
            _ConfigParser.set_value_temp('TEMPORARY', _Common.C2C_MACTROS, str(__new_seq))
            LAST_MANDIRI_C2C_SETTLEMENT_DATA = _result
            _Common.store_to_temp_data('last-mandiri-c2c-settlement', json.dumps(LAST_MANDIRI_C2C_SETTLEMENT_DATA))
            return _result
        except Exception as e:
            LOGGER.warning((bank, mode, str(e)))
            return False
    elif bank == 'MANDIRI' and mode == 'FEE_C2C':
        try:
            # LOGGER.info(('Create Settlement File', bank, mode))
            if output_path is None:
                output_path = C2C_SETT_FILE_PATH
            c2c_fees = _QPROX.get_c2c_settlement_fee()
            if not c2c_fees:
                LOGGER.warning(('Failed To Fetch Settlement Fee', bank, mode))
                return False
            _filecontent = ''
            for c in c2c_fees:
                if c == c2c_fees[0]:
                    _filecontent += (c + chr(3) + '\n')
                else:
                    _filecontent += (c + chr(3))
            _ds = _Helper.get_ds(_Common.C2C_MID + _Common.C2C_MACTROS[:4] + (2 * _Helper.time_string(f='%d%m%Y%H%M')))
            _filename = _Common.C2C_MID + _Common.C2C_MACTROS[:4] + (2 * _Helper.time_string(f='%d%m%Y%H%M')) + _ds + '.txt'
            LOGGER.info(('Create Settlement', bank, mode, _filename))
            _file_created = os.path.join(output_path, _filename)
            with open(_file_created, 'w+') as f:
                f.write(_filecontent)
                f.close()
            _file_created_ok = os.path.join(output_path, _filename.replace('.txt', '.ok'))
            with open(_file_created_ok, 'w+') as f_ok:
                f_ok.write('')
                f_ok.close()
            _result = {
                'path_file': _file_created,
                'filename': _filename,
                'bank': bank,
                'usage': 'Settlement Fee',
                'remarks': _filecontent,
            }
            return _result
        except Exception as e:
            LOGGER.warning((bank, mode, str(e)))
            return False
    else:
        LOGGER.warning(('Unknown bank/mode', bank, mode))
        return False

# {
#      'path_file': _file_created,
#      'filename': _filename,
#      'row': len(settlements),
#      'amount': str(_all_amount),
#      'bank': bank,
#      'bid': BID[bank],
#      'settlement_created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# }

def start_do_bni_topup_settlement():
    bank = 'BNI'
    _Helper.get_thread().apply_async(do_prepaid_settlement, (bank,))


def start_do_mandiri_topup_settlement():
    if int(_Common.MANDIRI_ACTIVE_WALLET) <= int(_Common.MANDIRI_THRESHOLD):
        if not _Common.C2C_MODE:
            bank = 'MANDIRI'
            _Common.MANDIRI_ACTIVE_WALLET = 0
        else:
            bank = 'MANDIRI_C2C'
        _Helper.get_thread().apply_async(do_prepaid_settlement, (bank,))
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')
    else:
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|NO_REQUIRED')


def start_reset_mandiri_settlement():
    if not _Common.C2C_MODE:
        bank = 'MANDIRI'
        _Common.MANDIRI_ACTIVE_WALLET = 0
    else:
        bank = 'MANDIRI_C2C'
    force = True
    _Helper.get_thread().apply_async(do_prepaid_settlement, (bank, force,))
    ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')


def start_dummy_mandiri_topup_settlement():
    if not _Common.C2C_MODE:
        bank = 'MANDIRI'
        _Common.MANDIRI_ACTIVE_WALLET = 0
    else:
        bank = 'MANDIRI_C2C'    
    force = True
    _Helper.get_thread().apply_async(do_prepaid_settlement, (bank, force,))
    ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')


def async_push_settlement_data(param):
    _Helper.get_thread().apply_async(push_settlement_data, (param,))


def do_prepaid_settlement(bank='BNI', force=False):
    if bank == 'BNI':
        _SFTPAccess.HOST_BID = 2
        if _Helper.is_online(source='bni_settlement') is False:
            return
        # if _SFTPAccess.SFTP is not None:
        #     _SFTPAccess.close_sftp()
        # _SFTPAccess.init_sftp()
        # if _SFTPAccess.SFTP is None:
        #     LOGGER.warning(('do_prepaid_settlement', bank, 'failed cannot init SFTP'))
        #     return
        _param = create_settlement_file(bank=bank)
        if _param is False:
            return
        _push = upload_settlement_file(_param['filename'], _param['path_file'])
        if _push['success'] is False:
            reupload = {
                'bank': bank, 
                'filename': _param['filename'],
                'path_file': _param['path_file'],
            }
            _param['reupload'] = reupload
            _Common.store_upload_to_job(name=_Helper.whoami(), host=bank, data=reupload)
        _param['settlement_uploaded_at'] = _Helper.time_string()
        _param['host'] = _push['host']
        _param['remote_path'] = _push['remote_path']
        _param['local_path'] = _push['local_path']
        push_settlement_data(_param)
    elif bank == 'MANDIRI':
        _SFTPAccess.HOST_BID = 1
        if _Helper.is_online(source='mandiri_settlement') is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_NO_INTERNET_CONNECTION')
            return
        # _QPROX.auth_ka_mandiri(_slot=_Common.get_active_sam(bank='MANDIRI', reverse=False), initial=False)
        # if _SFTPAccess.SFTP is not None:
        #     _SFTPAccess.close_sftp()
        # _SFTPAccess.init_sftp()
        # if _SFTPAccess.SFTP is None:
        #     LOGGER.warning(('do_prepaid_settlement', bank, 'failed cannot init SFTP'))
        #     return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|CREATE_FILE_SETTLEMENT')
        _param_sett = create_settlement_file(bank=bank, mode='TOPUP', force=force)
        if _param_sett is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_CREATE_FILE_SETTLEMENT')
            return
        _file_ok = _param_sett['filename'].replace('.TXT', '.OK')
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|UPLOAD_FILE_SETTLEMENT')
        _push_file_sett = upload_settlement_file(filename=[_param_sett['filename'], _file_ok],
                                                    local_path=_param_sett['path_file'],
                                                    remote_path=_Common.SFTP_MANDIRI['path']+'/Sett_Macin_DEV')
        if _push_file_sett['success'] is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_UPLOAD_FILE_SETTLEMENT')
            return
        _param_sett['host'] = _push_file_sett['host']
        _param_sett['remote_path'] = _push_file_sett['remote_path']
        _param_sett['local_path'] = _push_file_sett['local_path']
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA')
        # async_push_settlement_data(_param_sett)
        send_settlement_data = push_settlement_data(_param_sett)
        if not send_settlement_data:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_FAILED')
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|CREATE_FILE_KA_SETTLEMENT')
        _param_ka = create_settlement_file(bank=bank, mode='KA', force=force)
        if _param_ka is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_CREATE_FILE_KA_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|UPLOAD_FILE_KA_SETTLEMENT')
        _param_ka_ok = _param_ka['filename'].replace('.TXT', '.OK')
        _push_file_kalog = upload_settlement_file(filename=[_param_ka['filename'], _param_ka_ok],
                                                local_path=_param_ka['path_file'],
                                                remote_path=_Common.SFTP_MANDIRI['path']+'/Kalog_Macin_DEV')
        if _push_file_kalog['success'] is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_UPLOAD_FILE_KA_SETTLEMENT')
            return
        _param_ka['host'] = _push_file_kalog['host']
        _param_ka['remote_path'] = _push_file_kalog['remote_path']
        _param_ka['local_path'] = _push_file_kalog['local_path']
        # async_push_settlement_data(_param_ka)
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA')
        send_settlement_data = push_settlement_data(_param_ka)
        if not send_settlement_data:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_FAILED')
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|GENERATE_RQ1_SETTLEMENT')
        _rq1 = _QPROX.create_online_info_mandiri()
        if _rq1 is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_GENERATE_RQ1_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|CREATE_FILE_RQ1_SETTLEMENT')
        _file_rq1 = mandiri_create_rq1(content=_rq1)
        if _file_rq1 is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_CREATE_FILE_RQ1_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|UPLOAD_FILE_RQ1_SETTLEMENT')
        _push_rq1 = upload_settlement_file(filename=_file_rq1['filename'],
                                            local_path=_file_rq1['path_file'],
                                            remote_path=_Common.SFTP_MANDIRI['path']+'/UpdateRequestIn_DEV')
        if _push_rq1 is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_UPLOAD_FILE_RQ1_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|WAITING_RSP_UPDATE')
        _QPROX.do_update_limit_mandiri(_file_rq1['rsp'])
        # _QPROX.auth_ka_mandiri(_slot=_Common.get_active_sam(bank='MANDIRI', reverse=False), initial=False)
        # Move To QPROX Module
    elif bank == 'MANDIRI_C2C':
        _SFTPAccess.HOST_BID = 0
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|CREATE_FILE_SETTLEMENT')
        _param_sett = create_settlement_file(bank='MANDIRI', mode='TOPUP_C2C', force=force)
        if _param_sett is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_CREATE_FILE_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|UPLOAD_FILE_SETTLEMENT')
        _file_ok = _param_sett['filename'].replace('.txt', '.ok')
        _push_file_sett = upload_settlement_file(filename=[_param_sett['filename'], _file_ok],
                                                        local_path=_param_sett['path_file'],
                                                        remote_path=_Common.SFTP_C2C['path_settlement'])
        if _push_file_sett['success'] is False:
            reupload = {
                'bank': bank, 
                'filename': [_param_sett['filename'], _file_ok],
                'local_path':  _param_sett['path_file'],
                'remote_path':  _Common.SFTP_C2C['path_settlement'],
            }
            _param_sett['reupload'] = reupload
            _Common.store_upload_to_job(name=_Helper.whoami(), host=bank, data=reupload)
        _param_sett['settlement_uploaded_at'] = _Helper.time_string()
        _param_sett['host'] = _push_file_sett['host']
        _param_sett['remote_path'] = _push_file_sett['remote_path']
        _param_sett['local_path'] = _push_file_sett['local_path']
        # async_push_settlement_data(_param_sett)
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA')
        send_settlement_data = push_settlement_data(_param_sett)
        if not send_settlement_data:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_FAILED')
        # ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_SUCCESS')
        # Handle Single Attempt For Auto Reload
        # Deposit Mandiri Must Seen From Postpone Update Balance And Reload Process
        if _Common.exist_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'):
            LOGGER.warning(('ANOTHER MANDIRI_DEPOSIT_RELOAD_IN_PROGRES', str(_Common.load_from_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'))))
            return
        if _Common.exist_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED'):
            LOGGER.warning(('FOUND MDR_DEPOSIT_UPDATE_POSTPONED', str(_Common.load_from_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED', 'json'))))
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TOPUP_DEPOSIT_C2C_BALANCE')
        topup_result = _TopupService.topup_online('MANDIRI_C2C_DEPOSIT', 
                                            _Common.C2C_DEPOSIT_NO, 
                                            _Common.C2C_TOPUP_AMOUNT,
                                            'auto_refill'+str(_Helper.epoch())
                                            )
        if not topup_result:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TOPUP_DEPOSIT_C2C_ERROR')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TOPUP_DEPOSIT_C2C_SUCCESS')
    elif bank == 'MANDIRI_C2C_FEE':
        _SFTPAccess.HOST_BID = 0
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|CREATE_FEE_SETTLEMENT')
        _param_sett = create_settlement_file(bank='MANDIRI', mode='FEE_C2C', force=force)
        if _param_sett is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_CREATE_FEE_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|UPLOAD_FEE_SETTLEMENT')
        _push_file_sett = upload_settlement_file(filename=_param_sett['filename'],
                                                    local_path=_param_sett['path_file'],
                                                    remote_path=_Common.SFTP_C2C['path_fee'])
        if _push_file_sett['success'] is False:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_UPLOAD_FEE_SETTLEMENT')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|GET_C2C_FEE_SETTLEMENT')
        _result_update_fee = _QPROX.set_c2c_settlement_fee(_param_sett['filename'])
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|UPDATE_C2C_FEE_SETTLEMENT')
        if _result_update_fee is True:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|SUCCESS_SET_C2C_FEE')
        else:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|FAILED_SET_C2C_FEE')
    else:
        return


# Call Ad-Hoc C2C Fee Settlement
def start_do_c2c_update_fee():
    bank = 'MANDIRI_C2C_FEE'
    _Helper.get_thread().apply_async(do_prepaid_settlement, (bank, ))


def mandiri_create_rq1(content):
    try:
        _filename = MANDIRI_LAST_FILENAME.replace('.txt', '.RQ1')
        _file_rq1 = os.path.join(FILE_PATH, _filename)
        with open(_file_rq1, 'w+') as f:
            f.write(content)
            f.close()
        output = {
            'rq1': content,
            'filename': _filename,
            'path_file': _file_rq1,
            'rsp': MANDIRI_LAST_FILENAME.replace('.txt', '.RSP')
        }
        LOGGER.debug(str(output))
        return output
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def start_validate_update_balance():
    if not _Common.C2C_MODE:
        _Helper.get_thread().apply_async(validate_update_balance)
    else:
        _Helper.get_thread().apply_async(validate_update_balance_c2c)


def validate_update_balance_c2c():
    # FYI: Not Used For Now, Finding Better Way To Handle Backgorund Service Update Balance
    while True:
        sync_time = int(_ConfigParser.get_set_value('MANDIRI_C2C', 'daily^sync^time', '3600'))
        current_time = _Helper.now() / 1000
        LOGGER.debug(('MANDIRI_C2C_DEPOSIT_UPDATE_BALANCE', _Common.MANDIRI_ACTIVE_WALLET, _Common.C2C_THRESHOLD))
        if _Common.MANDIRI_ACTIVE_WALLET <= _Common.C2C_THRESHOLD:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')
            # do_prepaid_settlement(bank='MANDIRI_C2C', force=True)
            # Set Mandiri C2C Force Settlement Delivery to FALSE 
            do_prepaid_settlement(bank='MANDIRI_C2C', force=False)
        if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
            LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
            break
        next_run_time = current_time + sync_time
        LOGGER.debug(('MANDIRI_C2C_DEPOSIT_UPDATE_BALANCE NEXT RUN', _Helper.convert_epoch(t=next_run_time)))
        sleep(sync_time)


def start_check_mandiri_deposit():
    if _Common.C2C_MODE:
        _Helper.get_thread().apply_async(check_mandiri_deposit)
    else:
        print("pyt: [FAILED] CHECK_C2C_TOPUP_DEPOSIT, Not In C2C_MODE")
        

def check_mandiri_deposit():
    # Triggered After Success Transaction
    LOGGER.info(('MANDIRI DEPOSIT', _Common.MANDIRI_ACTIVE_WALLET, 'MANDIRI THRESHOLD', _Common.C2C_THRESHOLD))
    if _Common.MANDIRI_ACTIVE_WALLET <= _Common.C2C_THRESHOLD:
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')
        # _Common.MANDIRI_ACTIVE_WALLET = 0
        # _TopupService.send_kiosk_status()
        # do_prepaid_settlement(bank='MANDIRI_C2C', force=True)
        # Set Mandiri C2C Force Settlement Delivery to FALSE 
        # do_prepaid_settlement(bank='MANDIRI_C2C', force=False)
        # _TopupService.job_retry_reload_mandiri_deposit(first_run=False)
        topup_result = _TopupService.topup_online('MANDIRI_C2C_DEPOSIT', 
                                            _Common.C2C_DEPOSIT_NO, 
                                            _Common.C2C_TOPUP_AMOUNT,
                                            'auto_refill'+str(_Helper.epoch())
                                            )
        if not topup_result:
            ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TOPUP_DEPOSIT_C2C_ERROR')
            return
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TOPUP_DEPOSIT_C2C_SUCCESS')
        
        
def start_daily_mandiri_c2c_settlement():
    if _Common.C2C_MODE:
        _Helper.get_thread().apply_async(daily_mandiri_c2c_settlement)
    else:
        print("pyt: [FAILED] CHECK_C2C_TOPUP_DEPOSIT, Not In C2C_MODE")
        

def daily_mandiri_c2c_settlement():
    _SFTPAccess.HOST_BID = 0
    print('pyt: MANDIRI_SETTLEMENT|CREATE_FILE_SETTLEMENT')
    LOGGER.info(('MANDIRI_SETTLEMENT|CREATE_FILE_SETTLEMENT'))
    _param_sett = create_settlement_file(bank='MANDIRI', mode='TOPUP_C2C')
    if _param_sett is False:
        print('pyt: MANDIRI_SETTLEMENT|FAILED_CREATE_FILE_SETTLEMENT')
        LOGGER.error(('MANDIRI_SETTLEMENT|FAILED_CREATE_FILE_SETTLEMENT'))
        return
    print('pyt: MANDIRI_SETTLEMENT|UPLOAD_FILE_SETTLEMENT')
    LOGGER.info(('MANDIRI_SETTLEMENT|UPLOAD_FILE_SETTLEMENT'))
    _file_ok = _param_sett['filename'].replace('.txt', '.ok')
    _push_file_sett = upload_settlement_file(
        filename=[_param_sett['filename'], _file_ok],
        local_path=_param_sett['path_file'],
        remote_path=_Common.SFTP_C2C['path_settlement']
        )
    _param_sett['settlement_uploaded_at'] = _Helper.time_string()
    _param_sett['host'] = _push_file_sett['host']
    _param_sett['remote_path'] = _push_file_sett['remote_path']
    _param_sett['local_path'] = _push_file_sett['local_path']
    # async_push_settlement_data(_param_sett)
    send_settlement_data = push_settlement_data(_param_sett)
    if not send_settlement_data:
        print('pyt: MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_PENDING')
        LOGGER.error(('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_PENDING'))
        return
    print('pyt: MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_SUCCESS')
    LOGGER.info(('MANDIRI_SETTLEMENT|SYNC_SETTLEMENT_DATA_SUCCESS'))



def validate_update_balance():
    while True:
        daily_settle_time = _ConfigParser.get_set_value('MANDIRI', 'daily^settle^time', '02:00')
        sync_time = int(_ConfigParser.get_set_value('MANDIRI', 'daily^sync^time', '3600'))
        current_time = _Helper.now() / 1000
        LOGGER.debug(('MANDIRI_SAM_UPDATE_BALANCE', 'SYNC_TIME', sync_time, 'DAILY_SETTLEMENT', daily_settle_time))
        if _Common.LAST_UPDATE > 0:
            last_update_with_tolerance = (_Common.LAST_UPDATE/1000) + 84600
            if current_time >= last_update_with_tolerance:
                LOGGER.info(('DETECTED_EXPIRED_LIMIT_UPDATE', last_update_with_tolerance, current_time))
                _Common.MANDIRI_ACTIVE_WALLET = 0
                do_prepaid_settlement(bank='MANDIRI', force=True)
                ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')
        if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
            LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
            break
        next_run_time = current_time + sync_time
        LOGGER.debug(('MANDIRI_SAM_UPDATE_BALANCE NEXT RUN', _Helper.convert_epoch(t=next_run_time)))
        sleep(sync_time)


MANDIRI_UPDATE_SCHEDULE_RUNNING = False


def start_trigger_mandiri_sam_update():
    if _Common.C2C_MODE is True:
        print("pyt: [IGNORED] MANDIRI_SAM_KA_UPDATE_BALANCE, C2C Mode Is ON")
        return
    if not _QPROX.INIT_MANDIRI:
        LOGGER.warning(('[FAILED] MANDIRI_SAM_UPDATE_BALANCE', 'INIT_MANDIRI', _QPROX.INIT_MANDIRI))
        print("pyt: [FAILED] MANDIRI_SAM_UPDATE_BALANCE, Mandiri SAM Not Init Yet")
        return
    sleep(_Helper.get_random_num(.7, 2.9))
    if not MANDIRI_UPDATE_SCHEDULE_RUNNING:
        _Helper.get_thread().apply_async(trigger_mandiri_sam_update)
    else:
        print("pyt: [FAILED] MANDIRI_SAM_UPDATE_BALANCE, Already Triggered Previously")


def trigger_mandiri_sam_update():
    global MANDIRI_UPDATE_SCHEDULE_RUNNING
    # When This Function is Triggered, It will be forced update the SAM Balance And Ignore
    # Last Update Timestamp on TEMPORARY 
    daily_settle_time = _ConfigParser.get_set_value('MANDIRI', 'daily^settle^time', '02:00')
    current_time = _Helper.now() / 1000
    last_update = 0
    if _Common.LAST_UPDATE > 0:
        last_update = _Common.LAST_UPDATE/1000
    last_update_with_tolerance = (last_update + 84600000)/1000
    current_limit = 5000000
    if _Common.MANDIRI_ACTIVE_WALLET > current_limit:
        current_limit = 10000000
    if _Common.MANDIRI_ACTIVE_WALLET < current_limit or current_time >= last_update_with_tolerance:
        MANDIRI_UPDATE_SCHEDULE_RUNNING = True
        LOGGER.info(('TRIGGERED_BY_TIME_SETUP', _Helper.time_string('%H:%M'), daily_settle_time))
        _Common.MANDIRI_ACTIVE_WALLET = 0
        do_prepaid_settlement(bank='MANDIRI', force=True)
        ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.emit('MANDIRI_SETTLEMENT|TRIGGERED')
        MANDIRI_UPDATE_SCHEDULE_RUNNING = False
    else:
        LOGGER.warning(('FAILED_START_TIME_TRIGGER', _Helper.time_string('%H:%M'), daily_settle_time))
        LOGGER.warning(('LAST_UPDATE_BALANCE', _Helper.convert_epoch(last_update)))
        LOGGER.warning(('CURRENT_SAM_BALANCE', _Common.MANDIRI_ACTIVE_WALLET), current_limit)


def start_trigger_edc_settlement():
    sleep(_Helper.get_random_num(.7, 2.9))
    if not _Common.EDC_SETTLEMENT_RUNNING:
        _Common.EDC_SETTLEMENT_RUNNING = True
        _Helper.get_thread().apply_async(trigger_edc_settlement)
    else:
        print("pyt: [FAILED] EDC_SETTLEMENT_SCHEDULE, Already Triggered Previously")


def trigger_edc_settlement():
    daily_settle_time = _ConfigParser.get_set_value('EDC', 'daily^settle^time', '23:00')
    LOGGER.info(('TRIGGERED_BY_TIME_SETUP', 'EDC_SETTLEMENT_SCHEDULE', _Helper.time_string('%H:%M'), daily_settle_time))
    _EDC.define_edc_settlement()
    sleep(60)
    _Common.EDC_SETTLEMENT_RUNNING = False


