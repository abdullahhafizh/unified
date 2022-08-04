__author__ = 'wahyudi@multidaya.id'

from _cConfig import _ConfigParser, _Common
from _cCommand import _Command
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from _tTools import _Helper
from _nNetwork import _NetworkAccess
from time import sleep
import os
import sys
import subprocess
import json
from _dDAO import _DAO

LOGGER = logging.getLogger()
CD_PORT1 = _Common.CD_PORT1
CD_PORT2 = _Common.CD_PORT2
CD_PORT3 = _Common.CD_PORT3
CD_MID = ''
CD_TID = ''

CMD_CD_EXEC = os.path.join(sys.path[0], '_lLib', 'cd', 'card_dispenser.exe')
if _Common.IS_LINUX:
    CMD_CD_EXEC = os.path.join(sys.path[0], '_lLib', 'cd', 'card_dispenser')

CD = {
    "OPEN": "101",
    "INIT": "102",
    "MOVE": "103",
    "HOLD": "104",
    "STOP": "105"
}

CD_PORT_LIST = _Common.CD_PORT_LIST

class CDSignalHandler(QObject):
    __qualname__ = 'CDSignalHandler'
    SIGNAL_CD_MOVE = pyqtSignal(str)
    SIGNAL_CD_HOLD = pyqtSignal(str)
    SIGNAL_CD_STOP = pyqtSignal(str)
    SIGNAL_MULTIPLE_EJECT = pyqtSignal(str)
    SIGNAL_CD_READINESS = pyqtSignal(str)
    SIGNAL_CD_PORT_INIT = pyqtSignal(str)


CD_SIGNDLER = CDSignalHandler()
INIT_STATUS = False


def start_get_multiple_eject_status():
    _Helper.get_thread().apply_async(get_multiple_eject_status, )


MULTIPLE_EJECT  = True if (_ConfigParser.get_set_value('CD', 'multiple^eject', '0') == '1') else False


def get_multiple_eject_status():
    global MULTIPLE_EJECT
    check_multiple_eject = _ConfigParser.get_set_value('CD', 'multiple^eject', '0')
    MULTIPLE_EJECT = 'AVAILABLE' if check_multiple_eject == '1' else 'N/A'
    # print('pyt: MULTIPLE_EJECT_STATUS -> ' + eject_status)
    LOGGER.debug((MULTIPLE_EJECT))
    CD_SIGNDLER.SIGNAL_MULTIPLE_EJECT.emit(MULTIPLE_EJECT)


def start_multiple_eject(attempt, multiply):
    port = CD_PORT_LIST.get(attempt)
    # Generalise Command
    # false_ok = False
    # if not _Common.CD_NEW_TYPE.get(port, False):
    #     # Old CD Treated to Allow False OK Response (80/78)
    #     false_ok = True
    slot = attempt
    _Helper.get_thread().apply_async(trigger_card_dispenser, (port, slot, multiply,))
    

def start_card_validate_redeem(attempt, multiply, vcode):
    port = CD_PORT_LIST.get(attempt)
    # Generalise Command
    # false_ok = False
    # if not _Common.CD_NEW_TYPE.get(port, False):
    #     # Old CD Treated to Allow False OK Response (80/78)
    #     false_ok = True
    slot = attempt
    _Helper.get_thread().apply_async(voucher_trigger_card_dispenser, (port, slot, multiply, vcode,))


def trigger_card_dispenser(port, slot, multiply='1'):
    try:
        command = " ".join([CMD_CD_EXEC, str(port), "9600", multiply])
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        # Multi replace below must be performed to get the response object
        output = process.communicate()[0].decode('utf-8').strip().replace('\\r\\n  ', '').replace("\'", "\"")
        response = json.loads(output)
        # LOGGER.debug((command, output, type(response), str(response)))
        if response.get('code') is not None:
            # {'cmd': 'SIMPLY_EJECT', 'param': '', 'data': {}, 'message': 'CONTOH: card_dispenser.exe [PORT_CARD_DISPENSER] [BAUD_RATE_CARD_DISPENSER] [JUMLAH_KARTU_YANG_DIINGINKAN] -> card_dispenser.exe COM1 9600 20', 'code': 'EXCP'}
            if response['code'] == '0000':
                if multiply == '1':
                    # Direct Reduce Slot Without Transaction Record Dependant
                    _DAO.reduce_product_stock_by_slot_status(status=slot)
                    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|SUCCESS')
                else:
                    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|PARTIAL')
            else:
                emit_eject_error(slot, output, 'trigger_card_dispenser')
        else:
            emit_eject_error(slot, output, 'trigger_card_dispenser')
    except Exception as e:
        emit_eject_error(slot, str(e), 'trigger_card_dispenser')


def voucher_trigger_card_dispenser(port, slot, multiply='1', vcode=''):
    try:
        success = False
        payload = {
            'vcode': vcode
        }
        url = _Common.BACKEND_URL+'ppob/voucher/check'
        s, r = _NetworkAccess.post_to_url(url=url, param=payload, custom_timeout=5)
        if s == 200 and r['result'] == 'OK' and r['data']['Response'] == '0':
            success = True
        LOGGER.info((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
    finally:
        if success:
            trigger_card_dispenser(port, slot, multiply)
        else:
            emit_eject_error(slot, 'Vcode Validation Failed', 'voucher_trigger_card_dispenser')


def emit_eject_error(attempt, error_message, method='eject_full_round'):
    if attempt == '101':
        _Common.CD1_ERROR = 'DEVICE_RESPONSE_ERROR'
        _Common.upload_device_state('cd1', _Common.CD1_ERROR)
    if attempt == '102':
        _Common.CD2_ERROR = 'DEVICE_RESPONSE_ERROR'
        _Common.upload_device_state('cd2', _Common.CD2_ERROR)
    if attempt == '103':
        _Common.CD3_ERROR = 'DEVICE_RESPONSE_ERROR'
        _Common.upload_device_state('cd3', _Common.CD3_ERROR)
    _Common.online_logger(['Card Dispenser', attempt, method, error_message], 'device')
    LOGGER.warning((method, str(attempt), error_message))
    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|ERROR|'+error_message)


def kiosk_get_cd_readiness():
    _Helper.get_thread().apply_async(get_cd_readiness, )


def get_cd_readiness():
    if _Common.digit_in(_Common.CD_PORT1) is True:
        _Common.CD_READINESS['port1'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT1) is True and _Common.CD_PORT1_TYPE in ['OLD', 'NEW'] else 'N/A'
    if _Common.digit_in(_Common.CD_PORT2) is True:
        _Common.CD_READINESS['port2'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT2) is True and _Common.CD_PORT2_TYPE in ['OLD', 'NEW'] else 'N/A'
    if _Common.digit_in(_Common.CD_PORT3) is True:
        _Common.CD_READINESS['port3'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT3) is True and _Common.CD_PORT3_TYPE in ['OLD', 'NEW'] else 'N/A'
    CD_SIGNDLER.SIGNAL_CD_READINESS.emit(json.dumps(_Common.CD_READINESS))
    LOGGER.info((json.dumps(_Common.CD_READINESS)))


def check_init_cd(port):
    if _Common.CD_NEW_TYPE.get(port, False) is True or _Common.CD_DISABLE_CHECK_STATUS is True:
        return True
    return True