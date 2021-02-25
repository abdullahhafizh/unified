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
from _sService._GeneralPaymentService import GENERALPAYMENT_SIGNDLER
from _dDevice import _NV200


LOGGER = logging.getLogger()
COLLECTED_CASH = 0
TEST_MODE = _Common.TEST_MODE

CONFIG_GRG = os.path.join(sys.path[0], '_lLib', 'grg', 'BILLDTATM_CommCfg.ini')
EXEC_GRG = os.path.join(sys.path[0], '_lLib', 'grg', 'bill.exe')
LOG_BILL = os.path.join(sys.path[0], 'log')
BILL_TYPE = _Common.BILL_TYPE
BILL_PORT = _Common.BILL_PORT

GRG = {
    "SET": "501",
    "RECEIVE": "502",
    "STOP": "503",
    "STATUS": "504",
    "STORE": "505",
    "REJECT": "506",
    "GET_STATE": "507",
    "PORT": BILL_PORT.replace('COM', ''),
    "KEY_RECEIVED": "Received=IDR",
    "CODE_JAM": "14439",
    "TIMEOUT_BAD_NOTES": "acDevReturn:|acReserve:|",
    "UNKNOWN_ITEM": "Received=CNY|Denomination=0|",
    "LOOP_DELAY": 1,
    "KEY_STORED": None,
    "MAX_STORE_ATTEMPT": 1,
    "KEY_BOX_FULL": '!@#$%^&UI',
    "DIRECT_MODULE": False
}

NV = {
    "SET": "601",
    "RECEIVE": "602",
    "STORE": "603",
    "REJECT": "604",
    "STOP": "605",
    # "STATUS": "504",
    "RESET": "606",
    "KEY_RECEIVED": "Note in escrow, amount:",
    "PORT": BILL_PORT,
    # TODO Must Define Below Property
    "CODE_JAM": None,
    "TIMEOUT_BAD_NOTES": 'Invalid note',
    "UNKNOWN_ITEM": None ,
    "LOOP_DELAY": 2,
    "KEY_STORED": 'Note stacked',
    "MAX_STORE_ATTEMPT": 4,
    "KEY_BOX_FULL": 'Stacker full',
    "DIRECT_MODULE": _Common.BILL_NATIVE_MODULE
}


class BILLSignalHandler(QObject):
    __qualname__ = 'BILLSignalHandler'
    SIGNAL_BILL_RECEIVE = pyqtSignal(str)
    SIGNAL_BILL_STOP = pyqtSignal(str)
    SIGNAL_BILL_STATUS = pyqtSignal(str)
    SIGNAL_BILL_INIT = pyqtSignal(str)


BILL_SIGNDLER = BILLSignalHandler()

BILL = {}
SMALL_NOTES_NOT_ALLOWED = _Common.BILL_RESTRICTED_NOTES.split('|')
OPEN_STATUS = False
CASH_HISTORY = []
MAX_EXECUTION_TIME = 180
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
    LOGGER.debug(('command', command, 'output', str(process)))


def start_reset_bill():
    sleep(1)
    _Helper.get_thread().apply_async(reset_bill, )


DIRECT_PRICE_MODE = False
DIRECT_PRICE_AMOUNT = 0


def init_bill():
    global OPEN_STATUS, BILL
    BILL = GRG if BILL_TYPE == 'GRG' else NV
    # LOGGER.info(('Bill Command(s) Map', BILL_TYPE, str(BILL)))
    if BILL_PORT is None:
        LOGGER.warning(("port", BILL_PORT))
        _Common.BILL_ERROR = 'BILL_PORT_NOT_DEFINED'
        return False
    param = BILL["SET"] + '|' + BILL["PORT"]
    response, result = send_command_to_bill(param=param, output=None)
    if response == 0:
        OPEN_STATUS = True
    else:
        _Common.BILL_ERROR = 'FAILED_INIT_BILL_PORT'
    # LOGGER.info(("STANDBY_MODE BILL", BILL_TYPE, str(OPEN_STATUS)))
    BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('INIT_BILL|DONE')
    return OPEN_STATUS


def send_command_to_bill(param=None, output=None):
    if BILL["DIRECT_MODULE"] is True and BILL_TYPE == 'NV':
        result = _NV200.send_command(param, BILL, SMALL_NOTES_NOT_ALLOWED)
        code, message = result
        # Retry Command if Exception Raise
        if code == -99:
            LOGGER.debug(('EXCEPTION_RAISED', 'RETRY_COMMAND', param, result))
            sleep(1)
            result = _NV200.send_command(param, BILL, SMALL_NOTES_NOT_ALLOWED)
        LOGGER.info((param, result))
    else:
        result = _Command.send_request(param, output)
    return result


def reset_bill():
    global OPEN_STATUS, BILL
    BILL = GRG if BILL_TYPE == 'GRG' else NV
    # LOGGER.info(('Bill Command(s) Map', BILL_TYPE, str(BILL)))
    # if BILL_PORT is None:
    #     LOGGER.warning(("port", BILL_PORT))
    #     _Common.BILL_ERROR = 'BILL_PORT_NOT_DEFINED'
    #     return False
    param = BILL["SET"] + '|' + BILL["PORT"]
    if BILL_TYPE == 'NV':
        param = BILL["RESET"] + '|'
    response, result = send_command_to_bill(param=param, output=None)
    if response == 0:
        OPEN_STATUS = True
        BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('RESET_BILL|DONE')
    else:
        _Common.BILL_ERROR = 'FAILED_RESET_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('RESET_BILL|ERROR')
    # LOGGER.info(("STANDBY_MODE BILL", BILL_TYPE, str(OPEN_STATUS)))
    return OPEN_STATUS


def start_set_direct_price(price):
    _Helper.get_thread().apply_async(set_direct_price, (price,))


def set_direct_price(price):
    global DIRECT_PRICE_AMOUNT, DIRECT_PRICE_MODE, CASH_HISTORY, COLLECTED_CASH
    DIRECT_PRICE_MODE = True
    DIRECT_PRICE_AMOUNT = int(price)
    COLLECTED_CASH = 0
    CASH_HISTORY = []


def start_set_direct_price_with_current(current, price):
    _Helper.get_thread().apply_async(set_direct_price_with_current, (current, price, ))


def set_direct_price_with_current(current, price):
    global DIRECT_PRICE_AMOUNT, DIRECT_PRICE_MODE, CASH_HISTORY, COLLECTED_CASH
    DIRECT_PRICE_MODE = True
    DIRECT_PRICE_AMOUNT = int(price)
    COLLECTED_CASH = int(current)
    CASH_HISTORY = []
    CASH_HISTORY.append(current)


def start_bill_receive_note():
    # Add Billing Initiation En Every Note Receive For NV Only
    # if IS_RECEIVING is True:
    #     return
    # if BILL_TYPE == 'NV' and _Helper.empty(CASH_HISTORY):
    if not OPEN_STATUS:
        init_bill()
    _Helper.get_thread().apply_async(start_receive_note)


def parse_notes(_result):
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
    LOGGER.info(('Trigger Bill To Receive Money...'))
    try:
        attempt = 0
        IS_RECEIVING = True
        while True:
            # Handle NV IS_RECEIVING Flagging
            if IS_RECEIVING is False:
                LOGGER.warning(('[BREAK] start_receive_note Due To Stop Receive Event', str(IS_RECEIVING)))
                break
            attempt += 1
            param = BILL["RECEIVE"] + '|'
            _response, _result = send_command_to_bill(param=param, output=None)
            # _Helper.dump([_response, _result])
            if _response == -1:
                if BILL["DIRECT_MODULE"] is False or BILL_TYPE == 'GRG':
                    stop_receive_note()
                    sleep(2.5)
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|SERVICE_TIMEOUT')
                    break
                # else: 
                    # BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|SHOW_BACK_BUTTON')
                    # break
            if _response == 0 and BILL["KEY_RECEIVED"] in _result:
                cash_in = parse_notes(_result)
                # Insert Into Table Cashbox
                _DAO.insert_cashbox(cash_in)
                # -------------------------
                # _Helper.dump(cash_in)
                if BILL_TYPE != 'NV' or BILL["DIRECT_MODULE"] is False:
                    if cash_in in SMALL_NOTES_NOT_ALLOWED:
                        sleep(1.5)
                        param = BILL["REJECT"] + '|'
                        send_command_to_bill(param=param, output=None)
                        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|EXCEED')
                        break
                    if is_exceed_payment(DIRECT_PRICE_AMOUNT, cash_in, COLLECTED_CASH) is True:
                        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|EXCEED')
                        sleep(1.5)
                        param = BILL["REJECT"] + '|'
                        send_command_to_bill(param=param, output=None)
                        LOGGER.info(('Exceed Payment Detected :', json.dumps({'ADD': cash_in,
                                                                            'COLLECTED': COLLECTED_CASH,
                                                                            'TARGET': DIRECT_PRICE_AMOUNT})))
                        break
                update_cash_result, store_result = update_cash_status(str(cash_in), store_cash_into_cashbox())
                LOGGER.debug(('Cash Store/Update Status:', str(store_result), str(update_cash_result), str(cash_in)))
                _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
            if COLLECTED_CASH >= DIRECT_PRICE_AMOUNT:
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|COMPLETE')
                break
            if BILL["TIMEOUT_BAD_NOTES"] is not None and BILL["TIMEOUT_BAD_NOTES"] in _result:
                if BILL_TYPE == 'GRG':
                    _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
                    # send_command_to_bill(param=BILL["STOP"]+'|', output=None)
                    send_command_to_bill(param=BILL["REJECT"] + '|', output=None)
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                # if BILL_TYPE == 'NV':
                #     stop_receive_note()
                break
            if BILL["UNKNOWN_ITEM"] is not None and BILL["UNKNOWN_ITEM"] in _result:
                _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                break
            if BILL["CODE_JAM"] is not None and BILL["CODE_JAM"] in _result:
                _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
                _Common.BILL_ERROR = 'BILL_DEVICE_JAM'
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|JAMMED')
                LOGGER.warning(('BILL Jammed Detected :', json.dumps({'HISTORY': CASH_HISTORY,
                                                                    'COLLECTED': COLLECTED_CASH,
                                                                    'TARGET': DIRECT_PRICE_AMOUNT})))
                # Call API To Force Update Into Server
                _Common.upload_device_state('mei', _Common.BILL_ERROR)
                # sleep(1.5)
                # init_bill()
                break
            if attempt == MAX_EXECUTION_TIME:
                LOGGER.warning(('[BREAK] start_receive_note', str(attempt), str(MAX_EXECUTION_TIME)))
                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
                break
            # if IS_RECEIVING is False:
            #     LOGGER.warning(('[BREAK] start_receive_note by Event', str(IS_RECEIVING)))
            #     BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
            #     break
            sleep(_Common.BILL_STORE_DELAY)
    except Exception as e:
        _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
        if 'Invalid argument' in e:
            BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
            LOGGER.warning(('RECEIVE_BILL|BAD_NOTES'))
            return
        _Common.BILL_ERROR = 'FAILED_RECEIVE_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|ERROR')
        IS_RECEIVING = False
        LOGGER.warning(e)


def store_cash_into_cashbox():
    attempt = 0
    max_attempt = int(BILL['MAX_STORE_ATTEMPT'])
    while True:
        sleep(1)
        attempt += 1
        # Assumming Positive Response When Stacking Note
        if _Common.BILL_DIRECT_READ_NOTE is True:
            return True
        _, _result_store = send_command_to_bill(param=BILL["STORE"]+'|', output=None)
        LOGGER.debug((str(attempt), str(_result_store)))
        # 16/08 08:07:59 INFO store_cash_into_cashbox:273: ('1', 'Note stacked\r\n')
        if _Helper.empty(BILL['KEY_STORED']) or max_attempt == 1:
            return True
        if BILL['KEY_STORED'].lower() in _result_store.lower():
            return True
        if BILL['KEY_BOX_FULL'].lower() in _result_store.lower():
            _Common.BILL_ERROR = 'CASHBOX_FULL'
            total_cash = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__'],
            _Common.online_logger(['CASHBOX_FULL', str(total_cash)], 'device')
            _Common.log_to_config('BILL', 'last^money^inserted', 'FULL')
            return True
        if attempt == max_attempt:
            return False


def update_cash_status(cash_in, store_result=False):
    global CASH_HISTORY, COLLECTED_CASH
    try:
        if not store_result:
            LOGGER.warning(('Store Cash Failed', 'Update Cash Failed', store_result))
            return False, store_result
        CASH_HISTORY.append(str(cash_in))
        COLLECTED_CASH += int(cash_in)
        # _Helper.dump([str(CASH_HISTORY), COLLECTED_CASH])
        LOGGER.debug(('Cash Status:', json.dumps({
                    'ADD': cash_in,
                    'COLLECTED': COLLECTED_CASH,
                    'HISTORY': CASH_HISTORY})))
        # Signal Emit To Update View Cash Status
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|'+str(COLLECTED_CASH))
        result = True, store_result
    except Exception as e:
        LOGGER.warning('Store Cash Failed', 'Update Cash Failed', e)
        result = False, store_result
    finally:
        if not _Helper.empty(cash_in):
            BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|'+str(COLLECTED_CASH))
        return result


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
    # sleep(1)
    _Helper.get_thread().apply_async(stop_receive_note)


def stop_receive_note():
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING
    IS_RECEIVING = False
    # sleep(_Common.BILL_STORE_DELAY)
    try:
        param = BILL["STOP"] + '|'
        response, result = send_command_to_bill(param=param, output=None)
        if response == 0:
            if COLLECTED_CASH >= DIRECT_PRICE_AMOUNT:
                cash_received = {
                    'history': get_cash_history(),
                    'total': get_collected_cash()
                }
                BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|SUCCESS-'+json.dumps(cash_received))
                sleep(.5)
                GENERALPAYMENT_SIGNDLER.SIGNAL_GENERAL_PAYMENT.emit('CASH_PAYMENT')
            else:
                BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|SUCCESS')
            COLLECTED_CASH = 0
            CASH_HISTORY = []
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|ERROR')
            LOGGER.warning((str(response), str(result)))
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_STOP_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|ERROR')
        LOGGER.warning(e)
    # finally:
        # IS_RECEIVING = True
    # finally:
    #     if BILL_TYPE == 'NV':
    #         param = BILL["SET"] + '|'
    #         _response, _result = send_command_to_bill(param=param, output=None)
    #         if _response != 0:
    #             _Common.BILL_ERROR = 'FAILED_RESET_BILL_NV'
    #             LOGGER.warning(('FAILED_RESET_BILL_NV|ERROR'))


def start_get_status_bill():
    _Helper.get_thread().apply_async(get_status_bill)


def get_status_bill():
    try:
        param = BILL["STATUS"] + '|'
        response, result = send_command_to_bill(param=param, output=_Command.MO_REPORT, wait_for=1.5)
        LOGGER.debug((str(response), str(result)))
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
    _Helper.get_thread().apply_async(log_book_cash, (pid, amount,))


def log_book_cash(pid, amount, mode='normal'):
    param = {
        'csid': pid[::-1],
        'pid': pid,
        'tid': _Common.TID,
        'amount': amount
    }
    check_cash = _DAO.get_query_from('Cash', 'csid = "{}"'.format(param['csid']))
    if len(check_cash) > 0:
        _DAO.flush_table('Cash', 'csid = "{}"'.format(param['csid']))
        # LOGGER.debug(('DUPLICATE_CSID', mode, param))
        # return False
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

