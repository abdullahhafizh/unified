__author__ = 'fitrah.wahyudi.imam@gmail.com'

from _cCommand import _Command
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from _dDAO import _DAO
import json
from _cConfig import _Common
from _tTools import _Helper
from time import sleep
import sys
import os
import subprocess


LOGGER = logging.getLogger()
COLLECTED_CASH = 0
TEST_MODE = _Common.TEST_MODE

CONFIG_GRG = os.path.join(sys.path[0], '_lLib', 'grg', 'BILLDTATM_CommCfg.ini')
EXEC_GRG = os.path.join(sys.path[0], '_lLib', 'grg', 'bill.exe')
LOG_BILL = os.path.join(sys.path[0], 'log')


GRG = {
    "SET": "501",
    "RECEIVE": "502",
    "STOP": "503",
    "STATUS": "504",
    "STORE": "505",
    "REJECT": "506",
    "GET_STATE": "507"
}

NV = {
    "SET": "601",
    "RECEIVE": "602",
    "STORE": "603",
    "REJECT": "604",
    "STOP": "605",
    # "STATUS": "504",
    "RESET": "606"
}

BILL_TYPE = _Common.BILL_TYPE
BILL = GRG if BILL_TYPE == 'GRG' else NV
LOGGER.info(('Bill Command(s) Map', BILL_TYPE, str(BILL)))

# 1. OPEN PORT
# http://localhost:9000/Service/GET?cmd=601&param=COM10&type=json
# {"Result":"0","Command":"601","Parameter":"COM10","Response":"","ErrorDesc":"Sukses"}

# 2. ACCEPT
# http://localhost:9000/Service/GET?cmd=602&param=0&type=json
# {"Result":"0","Command":"602","Parameter":"0","Response":"Note in escrow, amount: 2000.00  IDR","ErrorDesc":"Sukses"}

# 3. STACK
# http://localhost:9000/Service/GET?cmd=603&param=0&type=json
# {"Result":"0","Command":"603","Parameter":"0","Response":"Note stacked","ErrorDesc":"Sukses"}

# 4. RETURN
# http://localhost:9000/Service/GET?cmd=604&param=0&type=json
# {"Result":"0","Command":"604","Parameter":"0","Response":"Host rejected note","ErrorDesc":"Sukses"}

# 5. DISABLE
# http://localhost:9000/Service/GET?cmd=605&param=0&type=json
# {"Result":"0","Command":"605","Parameter":"0","Response":"Unit disabled...","ErrorDesc":"Sukses"}

# 6. RESET
# http://localhost:9000/Service/GET?cmd=606&param=0&type=json
# {"Result":"0","Command":"606","Parameter":"0","Response":"Unit reset","ErrorDesc":"Sukses"}

BILL_PORT = _Common.BILL_PORT


class BILLSignalHandler(QObject):
    __qualname__ = 'BILLSignalHandler'
    SIGNAL_BILL_RECEIVE = pyqtSignal(str)
    SIGNAL_BILL_STOP = pyqtSignal(str)
    SIGNAL_BILL_STATUS = pyqtSignal(str)
    SIGNAL_BILL_INIT = pyqtSignal(str)


BILL_SIGNDLER = BILLSignalHandler()
OPEN_STATUS = False
CASH_HISTORY = []
MAX_EXECUTION_TIME = 150
IS_RECEIVING = False


def rewrite_config_init():
    __config = '''
[BILLDEPOSITDEV]
COMMTYPE =1
ComID =''' + BILL_PORT.replace('COM', '') + '''
ComBaud =19200
ComBoardPort =
ComBoardPortBaud =
DevCommLogID =2100
DevTraceLogID =2101
IniCfgFileName=BillDepositDevCfg.ini'''
    with open(CONFIG_GRG, 'w') as c:
        c.write(__config)
        c.close()
    command = EXEC_GRG + ' init'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    LOGGER.debug(('bill_init in when rewrite_config_init', 'command', command, 'output', str(process)))


def start_init_bill():
    sleep(1)
    _Helper.get_pool().apply_async(init_bill, )


def init_bill():
    global OPEN_STATUS, BILL_PORT
    if BILL_PORT is None:
        LOGGER.debug(("init_bill port : ", BILL_PORT))
        _Common.BILL_ERROR = 'BILL_PORT_NOT_DEFINED'
        return False
    _port = BILL_PORT.replace('COM', '') if BILL_TYPE == 'GRG' else BILL_PORT
    param = BILL["SET"] + '|' + _port
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        OPEN_STATUS = True
        if BILL_TYPE == 'NV':
            param = BILL['RESET'] + '|'
            response, result = _Command.send_request(param=param, output=None)
            if response != 0:
                OPEN_STATUS = False
                _Common.BILL_ERROR = 'FAILED_RESET_BILL'
    else:
        _Common.BILL_ERROR = 'FAILED_INIT_BILL_PORT'
    LOGGER.info(("Starting BILL in Standby_Mode : ", str(OPEN_STATUS)))
    BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('INIT_BILL|DONE')
    return OPEN_STATUS


KEY_RECEIVED = 'Received=IDR'
CODE_JAM = '14439'
TIMEOUT_BAD_NOTES = 'acDevReturn:|acReserve:|'
SMALL_NOTES_NOT_ALLOWED = ['1000', '2000', '5000']
UNKNOWN_ITEM = 'Received=CNY|Denomination=0|'

DIRECT_PRICE_MODE = False
DIRECT_PRICE_AMOUNT = 0


def start_set_direct_price(price):
    _Helper.get_pool().apply_async(set_direct_price, (price,))


def set_direct_price(price):
    global DIRECT_PRICE_AMOUNT, DIRECT_PRICE_MODE, CASH_HISTORY, COLLECTED_CASH
    DIRECT_PRICE_MODE = True
    DIRECT_PRICE_AMOUNT = int(price)
    COLLECTED_CASH = 0
    CASH_HISTORY = []


def start_bill_receive_note():
    _Helper.get_pool().apply_async(start_receive_note)


def simply_exec_bill(amount=None):
    global COLLECTED_CASH, CASH_HISTORY
    if amount is None:
        amount = DIRECT_PRICE_AMOUNT
    try:
        r = _Helper.time_string('%Y%m%d%H%M%S%f')
        command = 'start /B ' + EXEC_GRG + ' input ' + str(amount) + ' ' + str(r) + ' ' + str(MAX_EXECUTION_TIME)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        reply = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        LOGGER.debug(('simply_eject', 'command', command, 'output', str(reply)))
        output = os.path.join(LOG_BILL, r+'.json')
        attempt = 0
        while True:
            attempt += 1
            if os.path.isfile(output):
                output = open(output, 'r').readlines()
                LOGGER.debug('output_file', output)
                result = json.loads(output[0])
                if len(result['money']) > 0:
                    cash_in = str(result['money'][-1]['denom'])
                    if COLLECTED_CASH < DIRECT_PRICE_AMOUNT:
                        CASH_HISTORY.append(str(cash_in))
                        COLLECTED_CASH += int(cash_in)
                        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|' + str(COLLECTED_CASH))
                        LOGGER.info(('Cash Status:', json.dumps({'ADD': cash_in,
                                                                 'COLLECTED': COLLECTED_CASH,
                                                                 'HISTORY': CASH_HISTORY})))
                    if COLLECTED_CASH >= DIRECT_PRICE_AMOUNT:
                        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|COMPLETE')
                        break
            if attempt == MAX_EXECUTION_TIME:
                LOGGER.warning(('[BREAK] start_receive_note', str(attempt), str(MAX_EXECUTION_TIME)))
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
                break
            sleep(1)
    except Exception as e:
        LOGGER.warning(('simply_exec_bill', str(e)))
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|ERROR')


def parse_cash_in(_result):
    if BILL_TYPE == 'GRG':
        # Received=IDR|Denomination=5000|Version=2|SerialNumber=1|Go=0
        return _result.split('|')[1].split('=')[1]
    elif BILL_TYPE == 'NV':
        # Note in escrow, amount: 2000.00  IDR
        return _result.split('amount: ')[1].split('.00')[0]
    else:
        return '0'


def start_receive_note():
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING
    try:
        attempt = 0
        IS_RECEIVING = True
        while True:
            attempt += 1
            param = BILL["RECEIVE"] + '|'
            _response, _result = _Command.send_request(param=param, output=None)
            _Helper.dump([_response, _result])
            if _response == 0 and KEY_RECEIVED in _result:
                cash_in = parse_cash_in(_result)
                _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
                if cash_in in SMALL_NOTES_NOT_ALLOWED:
                    sleep(.25)
                    param = BILL["REJECT"] + '|'
                    _Command.send_request(param=param, output=None)
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|EXCEED')
                    break
                if is_exceed_payment(DIRECT_PRICE_AMOUNT, cash_in, COLLECTED_CASH) is True:
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|EXCEED')
                    sleep(.25)
                    param = BILL["REJECT"] + '|'
                    _Command.send_request(param=param, output=None)
                    LOGGER.info(('Exceed Payment Detected :', json.dumps({'ADD': cash_in,
                                                                          'COLLECTED': COLLECTED_CASH,
                                                                          'TARGET': DIRECT_PRICE_AMOUNT})))
                    break
                # if COLLECTED_CASH >= _MEI.DIRECT_PRICE_AMOUNT:
                #     BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|COMPLETE')
                #     break
                # Call Store Function Here
                CASH_HISTORY.append(str(cash_in))
                COLLECTED_CASH += int(cash_in)
                _Helper.dump([str(CASH_HISTORY), COLLECTED_CASH])
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|'+str(COLLECTED_CASH))
                _Command.send_request(param=BILL["STORE"]+'|', output=None)
                LOGGER.info(('Cash Status:', json.dumps({
                    'ADD': cash_in,
                    'COLLECTED': COLLECTED_CASH,
                    'HISTORY': CASH_HISTORY})))
                if COLLECTED_CASH >= DIRECT_PRICE_AMOUNT:
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|COMPLETE')
                    break
                # else:
                #     sleep(.25)
                #     param = BILL["RECEIVE"] + '|'
                #     _Command.send_request(param=param, output=None)
            if (TIMEOUT_BAD_NOTES in _result or UNKNOWN_ITEM in _result) and BILL_TYPE == "GRG":
                _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
                if TIMEOUT_BAD_NOTES in _result:
                    _Command.send_request(param=BILL["STOP"]+'|', output=None)
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                break
            if CODE_JAM in _result and BILL_TYPE == 'GRG':
                _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
                _Common.BILL_ERROR = 'BILL_DEVICE_JAM'
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|JAMMED')
                LOGGER.warning(('BILL Jammed Detected :', json.dumps({'HISTORY': CASH_HISTORY,
                                                                     'COLLECTED': COLLECTED_CASH,
                                                                     'TARGET': DIRECT_PRICE_AMOUNT})))
                # Call API To Force Update Into Server
                _Common.upload_device_state('mei', _Common.BILL_ERROR)
                sleep(1)
                init_bill()
                break
            if attempt == MAX_EXECUTION_TIME:
                LOGGER.warning(('[BREAK] start_receive_note', str(attempt), str(MAX_EXECUTION_TIME)))
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
                break
            if IS_RECEIVING is False:
                LOGGER.warning(('[BREAK] start_receive_note by Event', str(IS_RECEIVING)))
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
                break
            sleep(1)
    except Exception as e:
        _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
        _Common.BILL_ERROR = 'FAILED_RECEIVE_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|ERROR')
        LOGGER.warning(e)


def is_exceed_payment(target, value_in, current_value):
    if _Common.ALLOW_EXCEED_PAYMENT is True:
        return False
    actual = int(value_in) + int(current_value)
    if actual > int(target):
        return True
    else:
        return False


def stop_bill_receive_note():
    # log_book_cash('', get_collected_cash())
    sleep(1)
    _Helper.get_pool().apply_async(stop_receive_note)


def stop_receive_note():
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING
    IS_RECEIVING = False
    try:
        param = BILL["STOP"] + '|'
        response, result = _Command.send_request(param=param, output=None)
        if response == 0:
            cash_received = {
                'history': get_cash_history(),
                'total': get_collected_cash()
            }
            BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|SUCCESS-'+json.dumps(cash_received))
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|ERROR')
            LOGGER.warning(('stop_receive_note', str(response), str(result)))
        COLLECTED_CASH = 0
        CASH_HISTORY = []
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_STOP_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|ERROR')
        LOGGER.warning(e)


def start_get_status_bill():
    _Helper.get_pool().apply_async(get_status_bill)


def get_status_bill():
    try:
        param = BILL["STATUS"] + '|'
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
        LOGGER.debug(('get_status_bill', str(response), str(result)))
        if response == 0 and result is not None:
            BILL_SIGNDLER.SIGNAL_BILL_STATUS.emit('STATUS_BILL|'+result)
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STATUS.emit('STATUS_BILL|ERROR')
            LOGGER.warning(('get_status_bill', str(response), str(result)))
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_STATUS_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STATUS.emit('STATUS_BILL|ERROR')
        LOGGER.warning(e)


def start_log_book_cash(pid, amount):
    _Helper.get_pool().apply_async(log_book_cash, (pid, amount,))


def log_book_cash(pid, amount, mode='normal'):
    param = {
        'csid': pid[::-1],
        'pid': pid,
        'tid': _Common.TID,
        'amount': amount
    }
    check_cash = _DAO.get_query_from('Cash', 'csid = "{}"'.format(param['csid']))
    if len(check_cash) > 0:
        LOGGER.debug(('DUPLICATE_CSID', mode, param))
        return False
    try:
        _DAO.insert_cash(param=param)
        LOGGER.info(('SUCCESS', mode, param))
        return True
    except Exception as e:
        LOGGER.warning(('FAILED', mode, param, str(e)))
        return False


def get_collected_cash():
    return str(COLLECTED_CASH)


def get_cash_history():
    return '|'.join(CASH_HISTORY)


def get_total_cash():
    total_cash = 0
    for cash in CASH_HISTORY:
        total_cash += int(cash)
    return total_cash

