__author__ = 'wahyudi@multidaya.id'

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

if _Common.IS_LINUX:
    from _dDevice import _MeiSCR


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
    "DIRECT_MODULE": False,
    "TYPE": "GRG_08"
}

NV = {
    "SET": "601",
    "RECEIVE": "602",
    "STORE": "603",
    "REJECT": "604",
    "STOP": "605",
    # "STATUS": "504",
    "RESET": "606",
    "KEY_RECEIVED": "IDR",
    "PORT": BILL_PORT,
    # TODO Must Define Below Property
    "CODE_JAM": 'Unsafe Jam',
    "TIMEOUT_BAD_NOTES": 'Invalid note',
    "UNKNOWN_ITEM": None ,
    "LOOP_DELAY": 2,
    "KEY_STORED": 'stacked',
    "MAX_STORE_ATTEMPT": 1,
    "KEY_BOX_FULL": 'Stacker full',
    "DIRECT_MODULE": _Common.BILL_NATIVE_MODULE,
    "TYPE": "NV_200"
}

MEI = {
    "SET": "301",
    "RECEIVE": "302",
    "STORE": "303",
    "REJECT": "304",
    "STOP": "305",
    # "STATUS": "504",
    "RESET": "306",
    "KEY_RECEIVED": "Received=IDR|Denomination=",
    "PORT": BILL_PORT,
    # TODO Check Property Below Property
    "CODE_JAM": '_disabledReason=JAMMED',
    "TIMEOUT_BAD_NOTES": '_documentStatus=REJECTED',
    "UNKNOWN_ITEM": None ,
    "LOOP_DELAY": 2,
    "KEY_STORED": '_documentStatus=STACKED',
    "MAX_STORE_ATTEMPT": 1,
    "KEY_BOX_FULL": '_cassetteStatus=FULL',
    "DIRECT_MODULE": _Common.BILL_NATIVE_MODULE,
    "TYPE": "MEI_SCR"
}


class BILLSignalHandler(QObject):
    __qualname__ = 'BILLSignalHandler'
    SIGNAL_BILL_RECEIVE = pyqtSignal(str)
    SIGNAL_BILL_STORE = pyqtSignal(str)
    SIGNAL_BILL_REJECT = pyqtSignal(str)
    SIGNAL_BILL_STOP = pyqtSignal(str)
    SIGNAL_BILL_STATUS = pyqtSignal(str)
    SIGNAL_BILL_INIT = pyqtSignal(str)


BILL_SIGNDLER = BILLSignalHandler()


# Abstract Class MeiScr
class _AbstractMeiSCR:
    def __init__(self):
        pass
    
    def send_command(self, param=None, config=[], recycleNotes=[]):
        try:
            args = param.split('|')
            command = args[0]
            param = "0"
            if len(args[1:]) > 0:
                param = "|".join(args[1:])
            err = 'GENERAL_ERROR'
            LOGGER.debug((command, param, config))
            return -1, err
        except Exception as e:
            LOGGER.warning((e))
            return -99, str(e)


if _Common.IS_WINDOWS:
    _MeiSCR = _AbstractMeiSCR()


BILL = {}
SMALL_NOTES_NOT_ALLOWED = _Common.BILL_RESTRICTED_NOTES.split('|')
OPEN_STATUS = False
CASH_HISTORY = []
CASH_TIME_HISTORY = []
MAX_EXECUTION_TIME = 180
IS_RECEIVING = False

# Handle Single Denom TRX With Holding Notes
HOLD_NOTES = False


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
TARGET_CASH_AMOUNT = 0


def init_bill():
    global OPEN_STATUS, BILL
    if BILL_TYPE == 'GRG': BILL = GRG 
    if BILL_TYPE == 'NV': BILL = NV 
    if BILL_TYPE == 'MEI': BILL = MEI 
    # exec('BILL='+BILL_TYPE)
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
    if BILL_TYPE == 'NV':
        result = _NV200.send_command(param, BILL, SMALL_NOTES_NOT_ALLOWED, HOLD_NOTES)
        # code, message = result
        # Retry Command if Exception Raise
        # if code == -99:
            # LOGGER.debug(('EXCEPTION_RAISED', 'RETRY_COMMAND', param, result))
            # sleep(1)
            # result = _NV200.send_command(param, BILL, SMALL_NOTES_NOT_ALLOWED)
    elif BILL_TYPE == 'MEI':
        result = _MeiSCR.send_command(param, BILL)
    else:
        result = _Command.send_request(param, output)
    LOGGER.info((param, result))
    return result


def reset_bill():
    global OPEN_STATUS, BILL
    # BILL = GRG if BILL_TYPE == 'GRG' else NV
    # exec('BILL='+BILL_TYPE)
    if BILL_TYPE == 'GRG': BILL = GRG 
    if BILL_TYPE == 'NV': BILL = NV 
    if BILL_TYPE == 'MEI': BILL = MEI 
    # LOGGER.info(('Bill Command(s) Map', BILL_TYPE, str(BILL)))
    # if BILL_PORT is None:
    #     LOGGER.warning(("port", BILL_PORT))
    #     _Common.BILL_ERROR = 'BILL_PORT_NOT_DEFINED'
    #     return False
    param = BILL["SET"] + '|' + BILL["PORT"]
    if BILL_TYPE in ['MEI']:
        OPEN_STATUS = True
        _Common.BILL_ERROR = ''
        BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('RESET_BILL|DONE')
        return
    if BILL_TYPE in ['NV']:
        param = BILL["RESET"] + '|'
    response, result = send_command_to_bill(param=param, output=None)
    if response == 0:
        OPEN_STATUS = True
        _Common.BILL_ERROR = ''
        BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('RESET_BILL|DONE')
    else:
        _Common.BILL_ERROR = 'FAILED_RESET_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('RESET_BILL|ERROR')
    # LOGGER.info(("STANDBY_MODE BILL", BILL_TYPE, str(OPEN_STATUS)))
    return OPEN_STATUS


def start_set_direct_price(price):
    _Helper.get_thread().apply_async(set_direct_price, (price,))


def set_direct_price(price):
    global TARGET_CASH_AMOUNT, DIRECT_PRICE_MODE, CASH_HISTORY, COLLECTED_CASH, CASH_TIME_HISTORY
    DIRECT_PRICE_MODE = True
    TARGET_CASH_AMOUNT = int(price)
    COLLECTED_CASH = 0
    CASH_HISTORY = []
    CASH_TIME_HISTORY = []


def start_set_direct_price_with_current(current, price):
    _Helper.get_thread().apply_async(set_direct_price_with_current, (current, price, ))


def set_direct_price_with_current(current, price):
    global TARGET_CASH_AMOUNT, DIRECT_PRICE_MODE, CASH_HISTORY, COLLECTED_CASH, CASH_TIME_HISTORY
    DIRECT_PRICE_MODE = True
    TARGET_CASH_AMOUNT = int(price)
    COLLECTED_CASH = int(current)
    CASH_HISTORY = []
    CASH_TIME_HISTORY = []
    CASH_HISTORY.append(current)
    CASH_TIME_HISTORY.append(_Helper.time_string())
    LOGGER.info(('COLLECTED_CASH', COLLECTED_CASH, 'TARGET_CASH_AMOUNT', TARGET_CASH_AMOUNT, 'CASH_HISTORY', CASH_HISTORY))


def start_bill_receive_note(trxid):
    # Add Billing Initiation En Every Note Receive For NV Only
    # if IS_RECEIVING is True:
    #     return
    # if BILL_TYPE == 'NV' and _Helper.empty(CASH_HISTORY):
    if not OPEN_STATUS:
        init_bill()
    _Helper.get_thread().apply_async(start_receive_note, (trxid,))


def parse_notes(_result):
    cash_in = '0'
    try:
        if BILL_TYPE == 'GRG':
            # Received=IDR|Denomination=5000|Version=2|SerialNumber=1|Go=0
            cash_in = _result.split('|')[1].split('=')[1]
        elif BILL_TYPE == 'MEI':
            # Received=IDR|Denomination=10000.0|Version=286318130
            cash_in = _result.split('|')[1].split('=')[1].replace('.0', '')
        elif BILL_TYPE == 'NV':
            # Note in escrow, amount: 2000.00  IDR
            cash_in = _result.split('amount: ')[1].split('.00')[0]
    except Exception as e:
        LOGGER.warning((e))
    finally:
        # Insert Into Table Cashbox
        # _DAO.insert_cashbox(cash_in)
        return cash_in
    

def start_receive_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY, HOLD_NOTES
    if _Common.IDLE_MODE is True:
        LOGGER.info(('[INFO] Machine Try To Reactivate Bill in IDLE Mode', str(_Common.IDLE_MODE)))
        return
    LOGGER.info(('Trigger Bill', BILL_TYPE, trxid, TARGET_CASH_AMOUNT))
    HOLD_NOTES = _Common.single_denom_trx_detected(trxid)
    LOGGER.info(('Hold Notes or Single Denom TRX', trxid, HOLD_NOTES))
    if not HOLD_NOTES:
        HOLD_NOTES = (len(CASH_HISTORY) == 0)
        LOGGER.info(('Multi Denom Detected', trxid, HOLD_NOTES, str(CASH_HISTORY)))

    try:
        attempt = 0
        IS_RECEIVING = True
        _result = None
        while True:
            try:
                # Handle NV IS_RECEIVING Flagging
                if IS_RECEIVING is False:
                    LOGGER.info(('[BREAK] start_receive_note Due To Stop Receive Event', str(IS_RECEIVING)))
                    break
                attempt += 1
                
                _response, _result = send_command_to_bill(param=BILL["RECEIVE"] + '|', output=None)
                # _Helper.dump([_response, _result])
                if _response == -1:
                    if BILL["DIRECT_MODULE"] is False or BILL_TYPE == 'GRG':
                        sleep(1)
                        continue
                if BILL['KEY_BOX_FULL'].lower() in _result.lower():
                    set_cashbox_full()
                    IS_RECEIVING = False
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|ERROR')
                    _Common.store_notes_activity('ERROR', trxid)
                    break
                if _response == 0 and BILL["KEY_RECEIVED"] in _result:
                    cash_in = parse_notes(_result)
                    
                    # -------------------------
                    # Dummy True Condition (Must Be True)
                    if BILL_TYPE in _Common.BILL_SINGLE_DENOM_TYPE:
                        # Handle Single Denom
                        if HOLD_NOTES:
                            # Handle Double Read Anomalu in Single Denom TRX -- No More Relevant For Multi Denom But Keep Holded
                            # if len(CASH_HISTORY) > 0:
                            #     if CASH_HISTORY[0] == cash_in:
                            #         LOGGER.info(('NOTES_DETECTED_MULTIPLE_TIMES', str(CASH_HISTORY)))
                            #         # Return The Process
                            #         return
                            if int(cash_in) != int(TARGET_CASH_AMOUNT):
                                sleep(.5)
                                send_command_to_bill(param=BILL["REJECT"] + '|', output=None)
                                BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                                break
                        if cash_in in SMALL_NOTES_NOT_ALLOWED:
                            sleep(.5)
                            send_command_to_bill(param=BILL["REJECT"] + '|', output=None)
                            BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|EXCEED')
                            break
                        if is_exceed_payment(TARGET_CASH_AMOUNT, cash_in, COLLECTED_CASH) is True:
                            sleep(.5)
                            send_command_to_bill(param=BILL["REJECT"] + '|', output=None)
                            BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|EXCEED')
                            LOGGER.info(('Exceed Payment Detected :', json.dumps({'REJECT': cash_in,
                                                                                'COLLECTED': COLLECTED_CASH,
                                                                                'TARGET': TARGET_CASH_AMOUNT})))
                            break
                    if HOLD_NOTES:
                        # Somehow, Trigger OSError accidentally
                        store_result = store_cash_into_cashbox(trxid, str(cash_in))
                        if store_result is True:
                            update_cash_result, store_result = update_cash_status(str(cash_in), store_result)
                            LOGGER.debug(('Cash Store/Update Status:', str(store_result), str(update_cash_result), str(cash_in)))
                            # _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
                    # Process Store and Update Data Cash
                    else:
                        store_result = store_cash_into_cashbox(trxid, str(cash_in))
                        if store_result is True:
                            update_cash_result, store_result = update_cash_status(str(cash_in), store_result)
                            LOGGER.debug(('Cash Store/Update Status:', str(store_result), str(update_cash_result), str(cash_in)))
                            _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
                if COLLECTED_CASH >= TARGET_CASH_AMOUNT:
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|COMPLETE')
                    break
                if BILL["TIMEOUT_BAD_NOTES"] is not None and BILL["TIMEOUT_BAD_NOTES"] in _result:
                    # Because GRG Not Trigger Auto Reject On Bad Notes
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
                    _Common.BILL_ERROR = 'BILL_JAMMED_('+trxid+')'
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|JAMMED')
                    LOGGER.warning(('BILL Jammed Detected :', json.dumps({'HISTORY': CASH_HISTORY,
                                                                        'COLLECTED': COLLECTED_CASH,
                                                                        'TARGET': TARGET_CASH_AMOUNT,
                                                                        'RECEIVED_TIMESTAMP': CASH_TIME_HISTORY})))
                    # Call API To Force Update Into Server
                    _Common.upload_device_state('mei', _Common.BILL_ERROR)
                    break
                if attempt == MAX_EXECUTION_TIME:
                    LOGGER.warning(('[BREAK] start_receive_note', str(attempt), str(MAX_EXECUTION_TIME)))
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
                    break
                # if IS_RECEIVING is False:
                #     LOGGER.warning(('[BREAK] start_receive_note by Event', str(IS_RECEIVING)))
                #     BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|TIMEOUT')
                #     break
                # sleep(_Common.BILL_STORE_DELAY)
            except OSError as o:
                LOGGER.warning(('ANOMALY_FOUND_HERE', o))
                # WARNING: Dangerous Zone Here
                if _result is not None:
                    cash_in = parse_notes(_result)
                    if int(cash_in) > 0:
                        store_result = store_cash_into_cashbox(trxid)
                        if store_result is True:
                            update_cash_result, store_result = update_cash_status(str(cash_in), store_result)
                            LOGGER.debug(('#2 Cash Store/Update Status:', str(store_result), str(update_cash_result), str(cash_in)))
                            _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
                pass
            # sleep(_Common.BILL_STORE_DELAY)
            sleep(1)
    except OSError as o:
        LOGGER.warning(('ANOMALY_FOUND_HERE', o))
        # Do you need recall same function ???
        # start_receive_note(trxid)
        # [Errno 22] Invalid argument
        # if 'Invalid argument' in o:
        #     BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
        #     LOGGER.warning(('RECEIVE_BILL|BAD_NOTES'))
        #     return
        pass
    except Exception as e:
        LOGGER.warning(e)
        if _Common.LAST_INSERT_CASH_TIMESTAMP == _Helper.time_string(f='%Y%m%d%H%M%S'):
            LOGGER.info(('DUPLICATE_TRXID_WHEN_STORE_CASH_ACTIVITY', _Common.LAST_INSERT_CASH_TIMESTAMP))
            return # Must Stop Here
        IS_RECEIVING = False
        _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
        _Common.store_notes_activity('ERROR', trxid)
        _Common.BILL_ERROR = 'FAILED_RECEIVE_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|ERROR')
        #_Common.online_logger([trxid, CASH_HISTORY, COLLECTED_CASH, TARGET_CASH_AMOUNT, CASH_TIME_HISTORY], 'device')


def store_cash_into_cashbox(trxid, cash_in):
    try:
        result = True
        # ######################################
        # Direct Return Without Any Bill Process
        # Handle Single Denom TRX or Cash History Exist
        if HOLD_NOTES and len(CASH_HISTORY) == 0:
            return result
        # Dummy Store Per Notes, MEI Actually Doing Bulk Storing in Stop Event
        if BILL_TYPE == 'MEI':
            return result
        # ######################################
        max_attempt = int(BILL['MAX_STORE_ATTEMPT'])
        sleep(1)
        # Trigger Bill To Store
        _resp, _res = send_command_to_bill(param=BILL["STORE"]+'|', output=None)
        LOGGER.debug((BILL['TYPE'], _resp, _res))
        # 16/08 08:07:59 INFO store_cash_into_cashbox:273: ('1', 'Note stacked\r\n')
        if BILL['KEY_STORED'] is None and max_attempt == 1: #TODO: Re-validate this handle
            pass
        elif BILL['KEY_STORED'].lower() in _res.lower():
            pass
        elif BILL['KEY_BOX_FULL'].lower() in _res.lower(): #TODO: Re-validate this handle
            set_cashbox_full()
            result = False
    except OSError as o:
        LOGGER.warning(('ANOMALY_FOUND_HERE', o))
        result = True
    except Exception as e:
        LOGGER.warning((e))
        result = False
    finally:
        if result is True:
            # Move Store Cash Status into cashbox.status
            _Common.store_notes_activity(cash_in, trxid)
            _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
        else:
            LOGGER.info(('FAILED'))
        return result
    
    # attempt = 0
    # max_attempt = int(BILL['MAX_STORE_ATTEMPT'])
    # while True:
    #     sleep(1)
    #     attempt += 1
    #     # Assumming Positive Response When Stacking Note
    #     # if _Common.BILL_DIRECT_READ_NOTE is True:
    #     #     return True
    #     _, _result_store = send_command_to_bill(param=BILL["STORE"]+'|', output=None)
    #     LOGGER.debug((str(attempt), str(_result_store)))
    #     # 16/08 08:07:59 INFO store_cash_into_cashbox:273: ('1', 'Note stacked\r\n')
    #     if _Helper.empty(BILL['KEY_STORED']) or max_attempt == 1:
    #         return True
    #     if BILL['KEY_STORED'].lower() in _result_store.lower():
    #         return True
    #     if BILL['KEY_BOX_FULL'].lower() in _result_store.lower():
    #         set_cashbox_full()
    #         return True
    #     if attempt == max_attempt:
    #         return False
        

def set_cashbox_full():
    _Common.BILL_ERROR = 'CASHBOX_FULL'
    # total_cash = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__']
    total_cash = _Common.get_cash_activity()['total']
    #_Common.online_logger(['CASHBOX_FULL', str(total_cash)], 'device')
    _Common.log_to_config('BILL', 'last^money^inserted', 'FULL')


def update_cash_status(cash_in, store_result=False):
    global CASH_HISTORY, COLLECTED_CASH, CASH_TIME_HISTORY
    # print("pyt: ", _Helper.whoami())
    try:
        if not store_result:
            LOGGER.warning(('Store Cash Failed', 'Update Cash Failed', store_result))
            return False, store_result
        if _Helper.time_string() not in CASH_TIME_HISTORY:
            CASH_HISTORY.append(str(cash_in))
            CASH_TIME_HISTORY.append(_Helper.time_string())
            COLLECTED_CASH += int(cash_in)
        # _Helper.dump([str(CASH_HISTORY), COLLECTED_CASH])
        LOGGER.debug(('Cash Status:', json.dumps({
                    'ADD': cash_in,
                    'COLLECTED': COLLECTED_CASH,
                    'RECEIVED_TIMESTAMP': CASH_TIME_HISTORY,
                    'HISTORY': CASH_HISTORY})))
        # Signal Emit To Update View Cash Status
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|'+str(COLLECTED_CASH))
        result = True, store_result
    except Exception as e:
        LOGGER.warning('Store Cash Failed', 'Update Cash Failed', e)
        result = False, store_result
    finally:
        # TODO: Check The Impact On GRG / NV
        # if not _Helper.empty(cash_in):
        #     BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|'+str(COLLECTED_CASH))
        return result


def is_exceed_payment(target, value_in, current_value):
    if _Common.ALLOW_EXCEED_PAYMENT is True:
        return False
    actual = int(value_in) + int(current_value)
    if actual > int(target):
        return True
    else:
        return False


def stop_bill_receive_note(trxid):
    _Helper.get_thread().apply_async(stop_receive_note, (trxid,))


def stop_receive_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY
    IS_RECEIVING = False
    # sleep(_Common.BILL_STORE_DELAY)
    try:
        if HOLD_NOTES:
            if COLLECTED_CASH >= TARGET_CASH_AMOUNT:
                cash_received = {
                    'history': get_cash_history(),
                    'total': get_collected_cash()
                }
                BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|SUCCESS-'+json.dumps(cash_received))
                sleep(.5)
                GENERALPAYMENT_SIGNDLER.SIGNAL_GENERAL_PAYMENT.emit('CASH_PAYMENT')
            else:
                BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|SUCCESS')
            return
        
        if BILL_TYPE == 'MEI' and COLLECTED_CASH > 0:
            # Do Store Any Notes that stored in Escrow
            r, s = send_command_to_bill(param=BILL["STORE"]+'|', output=None)
            LOGGER.debug((BILL_TYPE, r, s))
            # ----------------------------

        response, result = send_command_to_bill(param=BILL["STOP"]+'|', output=None)
        if response == 0:
            LOGGER.info(('COLLECTED_CASH', COLLECTED_CASH, 'TARGET_CASH_AMOUNT', TARGET_CASH_AMOUNT))
            if COLLECTED_CASH >= TARGET_CASH_AMOUNT:
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
            CASH_TIME_HISTORY = []
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|ERROR')
            LOGGER.warning((trxid, str(response), str(result)))
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_STOP_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STOP.emit('STOP_BILL|ERROR')
        LOGGER.warning(e)


def start_bill_store_note(trxid):
    if BILL_TYPE == 'NV':
        _Helper.get_thread().apply_async(bill_store_note, (trxid,))
        sleep(3)
    _Helper.get_thread().apply_async(bill_store_note, (trxid,))


def bill_store_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY
    IS_RECEIVING = False
    try:
        if not HOLD_NOTES:
            LOGGER.warning((trxid, 'STORE_NOTES', BILL['TYPE'], 'HOLD_NOTES', HOLD_NOTES))
            return
        
        attempt = 3 if BILL_TYPE == 'GRG' else 1
        
        while True:
            attempt = attempt - 1
            response, result = send_command_to_bill(param=BILL["STORE"]+'|', output=None)
            LOGGER.info((trxid, 'STORE_NOTES', attempt, BILL['TYPE'], response, result))
            if attempt == 0: break
            if response == 0: break
            sleep(1)

        # Special Handling For GRG
        if response != 0 and BILL_TYPE == 'GRG':
            init_bill()
            response = 0

        if response == 0:
            LOGGER.info(('COLLECTED_CASH', COLLECTED_CASH, 'TARGET_CASH_AMOUNT', TARGET_CASH_AMOUNT))
            BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('STORE_BILL|SUCCESS')
            # Disabled - Will Not Be Actual From CASH_HISTORY When There Was Partial Error
            # for cash_in in CASH_HISTORY:
            #     _Common.store_notes_activity(cash_in, trxid)
            #     _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
            COLLECTED_CASH = 0
            CASH_HISTORY = []
            CASH_TIME_HISTORY = []
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('STORE_BILL|ERROR')
            LOGGER.warning((trxid, str(response), str(result)))
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_STORE_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('STORE_BILL|ERROR')
        LOGGER.warning(e)
    finally:
        response, result = send_command_to_bill(param=BILL["STOP"]+'|', output=None)
        LOGGER.debug((BILL['TYPE'], trxid, response, result))
        

def start_bill_reject_note(trxid):
    _Helper.get_thread().apply_async(bill_reject_note, (trxid,))


def bill_reject_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY
    IS_RECEIVING = False
    try:
        if not HOLD_NOTES:
            return
        response, result = send_command_to_bill(param=BILL["REJECT"]+'|', output=None)
        LOGGER.info((trxid, 'REJECT_NOTES', BILL['TYPE'], response, result))
        if response == 0:
            # Must Delete Last Cash Input in cashbox.status
            _Common.remove_notes_activity(trxid)
            _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
            BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('REJECT_BILL|SUCCESS')
            COLLECTED_CASH = 0
            CASH_HISTORY = []
            CASH_TIME_HISTORY = []
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('REJECT_BILL|ERROR')
            LOGGER.warning((trxid, str(response), str(result)))
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_REJECT_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('REJECT_BILL|ERROR')
        LOGGER.warning(e)
    finally:
        response, result = send_command_to_bill(param=BILL["STOP"]+'|', output=None)
        LOGGER.debug((BILL['TYPE'], trxid, response, result))


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
    disabled = True
    if disabled:
        return disabled
    param = {
        'csid': pid[::-1],
        'pid': pid,
        'tid': _Common.TID,
        'amount': amount
    }
    check_cash = _DAO.get_query_from('Cash', 'csid = "{}"'.format(param['csid']))
    if len(check_cash) > 0:
        for i in range(len(check_cash)):
            LOGGER.debug(('PREV_CASH_DATA', param, check_cash[i]))
            prev_amount = int(check_cash[i]['amount'])
            param['csid'] = '_'.join(['ret', str(i+1), pid])
            # param['amount'] = int(param['amount']) - prev_amount
            LOGGER.debug(('UPDATE_CASH_DATA_RETRY_TRX', param['csid'], prev_amount, param['amount']))
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

