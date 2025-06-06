__author__ = 'wahyudi@multidaya.id'

from _cConfig import _ConfigParser, _Common
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from _tTools import _Helper
from _nNetwork import _HTTPAccess
import os
import sys
import subprocess
import json
from _dDAO import _DAO
from _mModule import _InterfaceCD as CDLibrary

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


ACTIVE_TRX_ID = ''


def start_multiple_eject(trx_id, attempt, multiply):
    global ACTIVE_TRX_ID
    LOGGER.debug(("Trigger CD", trx_id, attempt))
    if ACTIVE_TRX_ID == trx_id: 
        LOGGER.warning(('ACTIVE_TRX_ID', ACTIVE_TRX_ID, trx_id))
        return
    ACTIVE_TRX_ID = trx_id
    port = CD_PORT_LIST.get(attempt)
    # Generalise Command
    # false_ok = False
    slot = attempt
    _Helper.get_thread().apply_async(trigger_card_dispenser, (port, slot, multiply,))
    

def start_card_validate_redeem(attempt, multiply, vcode):
    port = CD_PORT_LIST.get(attempt)
    # Generalise Command
    # false_ok = False
    slot = attempt
    _Helper.get_thread().apply_async(voucher_trigger_card_dispenser, (port, slot, multiply, vcode,))


def trigger_card_dispenser(port, slot, multiply='1'):
    try:
        # Handle Multiply CD Vendor By Type
        cd_type = _Common.CD_TYPES.get(port, False)
        LOGGER.info(("Detect CD Types", port, str(_Common.CD_TYPES)))
        LOGGER.info(("Start Execute CD", cd_type , port, slot, multiply))

        if not cd_type:
            emit_eject_error(slot, 'Card Type Not Found', 'trigger_card_dispenser')
            return
        if cd_type == 'KYT':
            trigger_card_dispenser_kyt(port, slot, multiply)
            return
        if cd_type == 'SYN':
            trigger_card_dispenser_syn(port, slot, multiply)
            return
        if cd_type == 'MTK':
            trigger_card_dispenser_mtk(port, slot, multiply)
            return
        
        command = " ".join([CMD_CD_EXEC, str(port), "9600", multiply])
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        # Multi replace below must be performed to get the response object
        output = process.communicate()[0].decode('utf-8').strip().replace('\\r\\n  ', '').replace("\'", "\"")
        response = json.loads(output)
        # LOGGER.debug((command, output, type(response), str(response)))
        if response.get('code') is not None:
            # {'cmd': 'SIMPLY_EJECT', 'param': '', 'data': {}, 'message': 'CONTOH: card_dispenser.exe [PORT_CARD_DISPENSER] [BAUD_RATE_CARD_DISPENSER] [JUMLAH_KARTU_YANG_DIINGINKAN] -> card_dispenser.exe COM1 9600 20', 'code': 'EXCP'}
            if response['code'] in ['0000', 'FF10']: #Set Card Jam Into Success Release
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


def trigger_card_dispenser_kyt(port, slot, multiply='1'):
    try:
        response = {
            "cmd": 'SIMPLY_EJECT_KYT',
            "param": port + '|',
            "message": "N/A",
            "code": "9999"
        }
        output = CDLibrary.simply_eject_kyt(port, response)
        # LOGGER.debug((command, output, type(response), str(response)))
        if response.get('code') is not None:
            # {'cmd': 'SIMPLY_EJECT', 'param': '', 'data': {}, 'message': 'CONTOH: card_dispenser.exe [PORT_CARD_DISPENSER] [BAUD_RATE_CARD_DISPENSER] [JUMLAH_KARTU_YANG_DIINGINKAN] -> card_dispenser.exe COM1 9600 20', 'code': 'EXCP'}
            if response['code'] in ['0000']: #Set Card Jam Into Success Release
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
        
        
def trigger_card_dispenser_syn(port, slot, multiply='1'):
    try:
        response = {
            "cmd": 'SIMPLY_EJECT_SYN',
            "param": port + '|',
            "message": "N/A",
            "code": "9999"
        }
        output = CDLibrary.simply_eject_syn(port, response)
        # LOGGER.debug((command, output, type(response), str(response)))
        if response.get('code') is not None:
            # {'cmd': 'SIMPLY_EJECT', 'param': '', 'data': {}, 'message': 'CONTOH: card_dispenser.exe [PORT_CARD_DISPENSER] [BAUD_RATE_CARD_DISPENSER] [JUMLAH_KARTU_YANG_DIINGINKAN] -> card_dispenser.exe COM1 9600 20', 'code': 'EXCP'}
            if response['code'] in ['0000']: #Set Card Jam Into Success Release
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


def trigger_card_dispenser_mtk(port, slot, multiply='1'):
    try:
        response = {
            "cmd": 'SIMPLY_EJECT_MTK',
            "param": port + '|',
            "message": "N/A",
            "code": "9999"
        }
        output = CDLibrary.simply_eject_mtk(port, response)
        # LOGGER.debug((command, output, type(response), str(response)))
        if response.get('code') is not None:
            # {'cmd': 'SIMPLY_EJECT', 'param': '', 'data': {}, 'message': 'CONTOH: card_dispenser.exe [PORT_CARD_DISPENSER] [BAUD_RATE_CARD_DISPENSER] [JUMLAH_KARTU_YANG_DIINGINKAN] -> card_dispenser.exe COM1 9600 20', 'code': 'EXCP'}
            if response['code'] in ['0000']: #Set Card Jam Into Success Release
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
        s, r = _HTTPAccess.post_to_url(url=url, param=payload, custom_timeout=5)
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
        _Common.log_to_temp_config('cd1^error', 'DEVICE_RESPONSE_ERROR')
        _Common.upload_device_state('cd1', 'DEVICE_RESPONSE_ERROR')
    if attempt == '102':
        _Common.log_to_temp_config('cd2^error', 'DEVICE_RESPONSE_ERROR')
        _Common.upload_device_state('cd2', 'DEVICE_RESPONSE_ERROR')
    if attempt == '103':
        _Common.log_to_temp_config('cd3^error', 'DEVICE_RESPONSE_ERROR')
        _Common.upload_device_state('cd3', 'DEVICE_RESPONSE_ERROR')
    if attempt == '104':
        _Common.log_to_temp_config('cd4^error', 'DEVICE_RESPONSE_ERROR')
        _Common.upload_device_state('cd4', 'DEVICE_RESPONSE_ERROR')
    if attempt == '105':
        _Common.log_to_temp_config('cd5^error', 'DEVICE_RESPONSE_ERROR')
        _Common.upload_device_state('cd5', 'DEVICE_RESPONSE_ERROR')
    if attempt == '106':
        _Common.log_to_temp_config('cd6^error', 'DEVICE_RESPONSE_ERROR')
        _Common.upload_device_state('cd6', 'DEVICE_RESPONSE_ERROR')
    #_Common.online_logger(['Card Dispenser', attempt, method, error_message], 'device')
    LOGGER.warning((method, str(attempt), error_message))
    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|ERROR|'+error_message)



def start_reset_cd_status(slot):
    _Helper.get_thread().apply_async(reset_cd_status, (slot,))
    

def reset_cd_status(slot):
    if slot == '101':
        _Common.log_to_temp_config('cd1^error', '')
        _Common.upload_device_state('cd1', '')
    if slot == '102':
        _Common.log_to_temp_config('cd2^error', '')
        _Common.upload_device_state('cd2', '')
    if slot == '103':
        _Common.log_to_temp_config('cd3^error', '')
        _Common.upload_device_state('cd3', '')
    if slot == '104':
        _Common.log_to_temp_config('cd4^error', '')
        _Common.upload_device_state('cd4', '')
    if slot == '105':
        _Common.log_to_temp_config('cd5^error', '')
        _Common.upload_device_state('cd5', '')
    if slot == '106':
        _Common.log_to_temp_config('cd6^error', '')
        _Common.upload_device_state('cd6', '')


def kiosk_get_cd_readiness():
    _Helper.get_thread().apply_async(get_cd_readiness, )


ALLOWED_CD_TYPE = ['OLD', 'NEW', 'KYT', 'SYN', 'MTK']


def get_cd_readiness():
    if _Common.digit_in(_Common.CD_PORT1) is True:
        _Common.CD_READINESS['cd1'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT1, '101') is True and _Common.CD_PORT1_TYPE in ALLOWED_CD_TYPE else 'N/A'
    if _Common.digit_in(_Common.CD_PORT2) is True:
        _Common.CD_READINESS['cd2'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT2, '102') is True and _Common.CD_PORT2_TYPE in ALLOWED_CD_TYPE else 'N/A'
    if _Common.digit_in(_Common.CD_PORT3) is True:
        _Common.CD_READINESS['cd3'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT3, '103') is True and _Common.CD_PORT3_TYPE in ALLOWED_CD_TYPE else 'N/A'
    if _Common.digit_in(_Common.CD_PORT4) is True:
        _Common.CD_READINESS['cd4'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT4, '104') is True and _Common.CD_PORT4_TYPE in ALLOWED_CD_TYPE else 'N/A'
    if _Common.digit_in(_Common.CD_PORT5) is True:
        _Common.CD_READINESS['cd5'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT5, '105') is True and _Common.CD_PORT5_TYPE in ALLOWED_CD_TYPE else 'N/A'
    if _Common.digit_in(_Common.CD_PORT6) is True:
        _Common.CD_READINESS['cd6'] = 'AVAILABLE' if check_init_cd(_Common.CD_PORT6, '106') is True and _Common.CD_PORT6_TYPE in ALLOWED_CD_TYPE else 'N/A'

    CD_SIGNDLER.SIGNAL_CD_READINESS.emit(json.dumps(_Common.CD_READINESS))
    LOGGER.info((json.dumps(_Common.CD_READINESS)))


def check_init_cd(port, attempt):
    # Validate Based On Error History
    # Detect Bank ID Based On Attempt
    bank_id = _DAO.get_product_bank_by_slot_status(attempt) 
    if not _Common.CARD_SALE_FEATURES.get(bank_id, False):
        return False
    
    if attempt == '101' and _Common.load_from_temp_config('cd1^error') == '':
        return True
    if attempt == '102' and _Common.load_from_temp_config('cd2^error') == '':
        return True
    if attempt == '103' and _Common.load_from_temp_config('cd3^error') == '':
        return True
    if attempt == '104' and _Common.load_from_temp_config('cd4^error') == '':
        return True
    if attempt == '105' and _Common.load_from_temp_config('cd5^error') == '':
        return True
    if attempt == '106' and _Common.load_from_temp_config('cd6^error') == '':
        return True
    return False

