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


LOGGER = logging.getLogger()
CD_PORT1 = _Common.CD_PORT1
CD_PORT2 = _Common.CD_PORT2
CD_PORT3 = _Common.CD_PORT3
CD_MID = ''
CD_TID = ''

CMD_CD_EXEC = os.path.join(sys.path[0], '_lLib', 'cd', 'card_dispenser.exe')
CMD_CD_NEW = os.path.join(sys.path[0], '_lLib', 'cd', 'new', 'card.exe')
CMD_CD_OLD = os.path.join(sys.path[0], '_lLib', 'cd', 'general', 'card.exe')

GENERAL_PATH = os.path.join(sys.path[0], '_lLib', 'cd', 'general')
CD_INIT = os.path.join(sys.path[0], '_lLib', 'cd', 'init', 'start.exe')

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


def init_cd_library():
    with open(os.path.join(GENERAL_PATH, 'card.ini'), 'w') as init:
        init.write('path='+GENERAL_PATH)
        init.close()
    with open(os.path.join(GENERAL_PATH, '101.card.ini'), 'w') as cd1:
        cd1.write('com='+CD_PORT1+os.linesep+'baud=9600')
        cd1.close()
    with open(os.path.join(GENERAL_PATH, '102.card.ini'), 'w') as cd2:
        cd2.write('com='+CD_PORT2+os.linesep+'baud=9600')
        cd2.close()
    with open(os.path.join(GENERAL_PATH, '103.card.ini'), 'w') as cd3:
        cd3.write('com='+CD_PORT3+os.linesep+'baud=9600')
        cd3.close()
    

def open_card_disp():
    if CD_PORT1 is None:
        LOGGER.debug(("[ERROR] open_card_disp port : ", CD_PORT1))
        _Common.CD1_ERROR = 'PORT_NOT_OPENED'
        return False
    param = CD["OPEN"] + "|" + CD_PORT1
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((param, result))
    # return True if '0' in status else False
    return True if response == 0 else False


def init_card_disp():
    global INIT_STATUS
    param = CD["INIT"] + "|"
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((param, result))
    INIT_STATUS = True if response == 0 else False
    return INIT_STATUS


def start_move_card_disp():
    attempt = 1
    _Helper.get_thread().apply_async(move_card_disp, (attempt,))


def start_get_multiple_eject_status():
    _Helper.get_thread().apply_async(get_multiple_eject_status, )


MULTIPLE_EJECT  = True if (_ConfigParser.get_set_value('CD', 'multiple^eject', '0') == '1') else False


def get_multiple_eject_status():
    global MULTIPLE_EJECT
    check_multiple_eject = _ConfigParser.get_set_value('CD', 'multiple^eject', '0')
    MULTIPLE_EJECT = 'AVAILABLE' if check_multiple_eject == '1' else 'N/A'
    # print('pyt: MULTIPLE_EJECT_STATUS -> ' + eject_status)
    LOGGER.debug(('get_multiple_eject_status', MULTIPLE_EJECT))
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
    # if _Common.CD_NEW_TYPE.get(port, False) is True:
    #     _Helper.get_thread().apply_async(new_cd_eject, (port, attempt, ))
    # else:
    #     _Helper.get_thread().apply_async(general_cd_eject, (attempt, multiply,))
    

def start_card_validate_redeem(attempt, multiply, vcode):
    port = CD_PORT_LIST.get(attempt)
    # Generalise Command
    # false_ok = False
    # if not _Common.CD_NEW_TYPE.get(port, False):
    #     # Old CD Treated to Allow False OK Response (80/78)
    #     false_ok = True
    slot = attempt
    _Helper.get_thread().apply_async(voucher_trigger_card_dispenser, (port, slot, multiply, vcode,))


def new_cd_eject(port, attempt):
    try:
        # command = CMD_CD_NEW + " hold " + port
        command = " ".join([CMD_CD_NEW, "hold", port])
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        output = output[0].split(";")
        response = json.loads(output[0])
        LOGGER.debug((command, 'output', output, 'response', response))
        if int(response) > 0:
            # Handle Failure Here
            emit_eject_error(attempt, str(output), 'new_cd_eject')
        else:
            sleep(1)
            CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|SUCCESS')
    except Exception as e:
        emit_eject_error(attempt, str(e), 'new_cd_eject')
        

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


def general_cd_eject(attempt, multiply, false_ok=False):
    # _cd_selected_port = None
    # try:
    #     selected_port = CD_PORT_LIST[attempt]
    #     # LOGGER.info(('_cd_selected_port :', _cd_selected_port))
    # except IndexError:
    #     LOGGER.warning(('Failed to Select CD Port', attempt))
    #     CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|ERROR')
    #     return
    # if _Common.TEST_MODE is True:
    #     CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|SUCCESS')
    #     LOGGER.debug(('ByPassing Mode', str(_Common.TEST_MODE), attempt, multiply))
    #     return
    try:
        # command = CMD_CD_NEW + " hold " + selected_port
        # Switch Command For Old Type CD
        # command = CMD_CD_OLD + " card " + str(attempt)
        command = " ".join([CMD_CD_OLD, "card", str(attempt)])
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        output = output[0].split(";")
        response = json.loads(output[0])
        LOGGER.debug((command, 'response', response))
        if response.get('ec') is not None:
            # ec 80 is Success, otherwise is failure
            if response['ec'] == 80 or false_ok is True:
                # Force Reply Success in TESTING MODE
                if multiply == '1':
                    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|SUCCESS')
                else:
                    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|PARTIAL')
            else:
                emit_eject_error(attempt, output[0], 'general_cd_eject')
        else:
            emit_eject_error(attempt, output[0], 'general_cd_eject')
    except Exception as e:
        emit_eject_error(attempt, str(e), 'general_cd_eject')


def eject_full_round(attempt):
    # attempt is defined from product status as address
    _cd_selected_port = None
    try:
        _cd_selected_port = CD_PORT_LIST[attempt]
        LOGGER.info(('_cd_selected_port :', _cd_selected_port))
    except IndexError:
        LOGGER.warning(('Failed to Select CD Port', _cd_selected_port))
        CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|ERROR')
        return
    try:
        # Open CD Port
        param = CD["OPEN"] + "|" + _cd_selected_port
        response, result = _Command.send_request(param=param, output=None)
        LOGGER.debug(("eject_full_round [OPEN] : ", param, result))
        # return True if '0' in status else False
        if response == 0:
            # Init CD Port
            sleep(1)
            param = CD["INIT"] + "|"
            response, result = _Command.send_request(param=param, output=None)
            LOGGER.debug(("eject_full_round [INIT] : ", param, result))
            if response == 0:
                # Eject From CD
                sleep(1)
                param = CD["MOVE"] + "|"
                response, result = _Command.send_request(param=param, output=None)
                LOGGER.debug(("eject_full_round [MOVE] : ", param, result))
                if response == 0:
                    CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|SUCCESS')
                else:
                    emit_eject_error(attempt, 'DEVICE_NOT_MOVE|'+attempt)
                    return
                # Stop/Close The Connection Session
                sleep(1)
                param = CD["STOP"] + "|"
                response, result = _Command.send_request(param=param, output=None)
                LOGGER.debug(("eject_full_round [STOP] : ", param, result))
            else:
                emit_eject_error(attempt, 'DEVICE_NOT_INIT|'+attempt)
                return
        else:
            emit_eject_error(attempt, 'DEVICE_NOT_OPEN|'+attempt)
            return
    except Exception as e:
        emit_eject_error(attempt, str(e) + '|' + attempt)


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


def move_card_disp(attempt):
    if INIT_STATUS is not True:
        CD_SIGNDLER.SIGNAL_CD_MOVE.emit('ERROR')
        _Common.CD1_ERROR = 'DEVICE_NOT_INIT'
        return
    param = CD["HOLD"] + "|"
    if MULTIPLE_EJECT is True:
        param = CD["MOVE"] + "|"
    for x in range(attempt):
        response, result = _Command.send_request(param=param, output=None)
        LOGGER.debug(("move_card_disp : ", param, result, str(x)))
        if x == (attempt-1):
            if response == 0:
                CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|SUCCESS-' + str(x))
            else:
                _Common.CD1_ERROR = 'FAILED_TO_EJECT'
                CD_SIGNDLER.SIGNAL_CD_MOVE.emit('EJECT|ERROR-' + str(x))
        else:
            continue
        sleep(1)


def start_hold_card_disp():
    _Helper.get_thread().apply_async(hold_card_disp, )


def hold_card_disp():
    if INIT_STATUS is not True:
        CD_SIGNDLER.SIGNAL_CD_HOLD.emit('ERROR')
        _Common.CD1_ERROR = 'DEVICE_NOT_INIT'
        return
    param = CD["HOLD"] + "|"
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug(("hold_card_disp : ", param, result))
    if response == 0:
        CD_SIGNDLER.SIGNAL_CD_HOLD.emit('SUCCESS')
    else:
        _Common.CD1_ERROR = 'FAILED_TO_HOLD_EJECT'
        CD_SIGNDLER.SIGNAL_CD_HOLD.emit('ERROR')


def start_stop_card_disp():
    _Helper.get_thread().apply_async(stop_card_disp, )


def stop_card_disp():
    if INIT_STATUS is not True:
        CD_SIGNDLER.SIGNAL_CD_STOP.emit('ERROR')
        _Common.CD1_ERROR = 'DEVICE_NOT_INIT'
        return
    param = CD["STOP"] + "|"
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug(("stop_card_disp : ", param, result))
    if response == 0:
        CD_SIGNDLER.SIGNAL_CD_STOP.emit('SUCCESS')
    else:
        _Common.CD1_ERROR = 'DEVICE_NOT_STOP'
        CD_SIGNDLER.SIGNAL_CD_STOP.emit('ERROR')


def start_check_init_cd(com):
    _Helper.get_thread().apply_async(init_cd, (com, ))


def init_cd(com):
    command = CD_INIT + " init " + str(com)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
    output = output[0].split(";")
    LOGGER.debug(('init_cd', com, output))
    CD_SIGNDLER.SIGNAL_CD_PORT_INIT.emit(json.dumps({'port': com, 'status': output}))
    return True if '1' not in output else False


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
    LOGGER.debug(('get_cd_readiness', json.dumps(_Common.CD_READINESS)))


def check_init_cd(port):
    if _Common.CD_NEW_TYPE.get(port, False) is True or _Common.CD_DISABLE_CHECK_STATUS is True:
        return True
    return init_cd(port)
