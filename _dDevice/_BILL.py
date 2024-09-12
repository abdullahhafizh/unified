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
from _dDevice import _NV200, _NVProcess
from threading import Event
import traceback

if _Common.IS_LINUX:
    from _dDevice import _MeiSCR


LOGGER = logging.getLogger()
COLLECTED_CASH = 0
TEST_MODE = _Common.TEST_MODE

CONFIG_GRG = os.path.join(sys.path[0], '_lLib', 'grg', 'BILLDTATM_CommCfg.ini')
EXEC_GRG = os.path.join(sys.path[0], '_lLib', 'grg', 'bill.exe')
NV_LIB_MODE = True
NV_ENGINE_LIB = os.path.join(sys.path[0], '_lLib', 'nv_itl')
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
    "TYPE": "GRG_08",
    "MAX_EXECUTION_TIME": _Common.BILL_PAYMENT_TIME,
    "RECEIVE_ATTEMPT": 90
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
    "TYPE": "NV_200",
    "MAX_EXECUTION_TIME": _Common.BILL_PAYMENT_TIME,
    "RECEIVE_ATTEMPT": 1
}

NV_ITL = {
    "SET": "611",
    "RECEIVE": "612",
    "STOP": "613",
    "STATUS": "614",
    "STORE": "615",
    "REJECT": "616",
    "GET_STATE": "617",
    "ENABLE": "618",
    "PORT": BILL_PORT,
    "KEY_RECEIVED": "Note held in escrow, amount: ",
    "CODE_JAM": "Unsafe jam|Safe jam",
    "TIMEOUT_BAD_NOTES": "Invalid note",
    "UNKNOWN_ITEM": None,
    "LOOP_DELAY": 0.25,
    "KEY_STORED": "Note stacked",
    "MAX_STORE_ATTEMPT": 1,
    "KEY_BOX_FULL": 'Stacker full',
    "DIRECT_MODULE": False,
    "TYPE": "NV_200_ITL",
    "MAX_EXECUTION_TIME": _Common.BILL_PAYMENT_TIME,
    "RECEIVE_ATTEMPT": 57,
    "ENGINE_LIB": NV_ENGINE_LIB
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
    "TYPE": "MEI_SCR",
    "MAX_EXECUTION_TIME": _Common.BILL_PAYMENT_TIME,
    "RECEIVE_ATTEMPT": 90
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
    try:
        LOGGER.debug(("BILL_TYPE", BILL_TYPE))
        
        if BILL_TYPE == 'GRG': BILL = GRG 
        if BILL_TYPE == 'NV':
            if NV_LIB_MODE:
                BILL = NV_ITL
                LOGGER.debug(("BILL", BILL))
            else:
                BILL = NV 
        if BILL_TYPE == 'MEI': BILL = MEI 

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

        BILL_SIGNDLER.SIGNAL_BILL_INIT.emit('INIT_BILL|DONE')
    except Exception as e:
        error_string = traceback.format_exc()
        LOGGER.warning((e))
        LOGGER.debug(error_string)
        _Common.BILL_ERROR = 'INIT_BILL_ERROR'
        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('INIT_BILL|ERROR')
    return OPEN_STATUS


def send_command_to_bill(param=None, output=None):
    if BILL_TYPE == 'NV':
        if NV_LIB_MODE:
            LOGGER.debug(("nv_send_command", param, BILL, SMALL_NOTES_NOT_ALLOWED, HOLD_NOTES))
            result = _NVProcess.send_command(param, BILL, SMALL_NOTES_NOT_ALLOWED, HOLD_NOTES)
        else:
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

    if BILL_TYPE == 'GRG': BILL = GRG 
    if BILL_TYPE == 'NV': 
        if NV_LIB_MODE:
            BILL = NV_ITL
        else:
            BILL = NV 
    if BILL_TYPE == 'MEI': BILL = MEI 
 
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
    if not OPEN_STATUS:
        init_bill()
    # Assign Cash TRX_ID
    _Common.ACTIVE_CASH_TRX_ID = trxid
    _Helper.get_thread().apply_async(wrapper_start_receive_note, (trxid,))


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
            if NV_LIB_MODE:
                cash_in = _result.split(BILL["KEY_RECEIVED"])[1].split('.00')[0]
            else:
                # Note in escrow, amount: 2000.00  IDR
                cash_in = _result.split('amount: ')[1].split('.00')[0]
    except Exception as e:
        LOGGER.warning((e))
    finally:
        return cash_in

NV_ITL_EVENT= Event()
def wrapper_start_receive_note(trxid):
    # Ada banyak return di start_receive_note yg membuat kompleks untuk enable dan disable NV, kalau sudah atomic level race condition ini ga bisa prevent multiple running
    global NV_ITL_EVENT
    if BILL_TYPE == "NV" and NV_LIB_MODE:
        if NV_ITL_EVENT.is_set():
            # kalau sudah set jgn jalankan lagi, berarti ada process/thread yg sedang jalan
            return        
        NV_ITL_EVENT.set()
        # ENABLE DULU baru bisa terima uang
        _response, _result = send_command_to_bill(param=BILL["ENABLE"]+"|", output=None)
        if _response != 0:
            # ERROR, perlu log?
            NV_ITL_EVENT.clear()
            return

    start_receive_note(trxid)

    if BILL_TYPE == "NV" and NV_LIB_MODE:
        # karena kalau di stop akan mengakibatkan uang dikeluarkan paksa setelah timeout dari escrow
        NV_ITL_EVENT.clear()
        # if COLLECTED_CASH >= TARGET_CASH_AMOUNT:
        # _response, _result = send_command_to_bill(param=BILL["STOP"]+"|", output=None)
    

def start_receive_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY, HOLD_NOTES
    if _Common.IDLE_MODE is True:
        LOGGER.info(('[INFO] Machine Try To Reactivate Bill in IDLE Mode', str(_Common.IDLE_MODE)))
        return
    
    LOGGER.info(('Trigger Bill', BILL_TYPE, trxid, TARGET_CASH_AMOUNT, str(BILL['MAX_EXECUTION_TIME'])))
    
    HOLD_NOTES = _Common.single_denom_trx_detected(trxid)
    LOGGER.info(('Hold Notes | Single Denom TRX', trxid, HOLD_NOTES))
    # if not HOLD_NOTES and BILL_TYPE == 'NV' :
    #     HOLD_NOTES = (len(CASH_HISTORY) > 0)
    #     LOGGER.info(('Multi Denom Detected on NV, Must Enable HOLD Mode', trxid, HOLD_NOTES, str(CASH_HISTORY)))

    try:
        attempt = 0
        IS_RECEIVING = True
        _result = None
        while True:
            try:
                # Extra Handling NV BILL Before Call
                # IS_RECEIVING Flagging
                if not IS_RECEIVING:
                    LOGGER.debug(('Stop Bill Acceptor Acceptance By IS_RECEIVING', str(IS_RECEIVING)))
                    return
                # Active TRX_ID
                if trxid != _Common.ACTIVE_CASH_TRX_ID:
                    LOGGER.debug(('Stop Bill Acceptor Acceptance By ACTIVE_CASH_TRX_ID', str(_Common.ACTIVE_CASH_TRX_ID)))
                    return
                
                attempt += 1
                
                _response, _result = send_command_to_bill(param=BILL["RECEIVE"] + '|', output=None)
                # _Helper.dump([_response, _result])
                if _response == -1:
                    if BILL["DIRECT_MODULE"] is False or BILL_TYPE == 'GRG':
                        sleep(1)
                        continue
                
                # Handle Get Bill Response in Different thread or racing condition after call
                if trxid != _Common.ACTIVE_CASH_TRX_ID:
                    LOGGER.debug(('Void Bill Acceptor Response By Different Thread TRX_ID', str(_Common.ACTIVE_CASH_TRX_ID), trxid, _result))
                    return
                
                if BILL['KEY_BOX_FULL'].lower() in _result.lower():
                    set_cashbox_full()
                    IS_RECEIVING = False
                    BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|ERROR')
                    # _Common.log_to_config('BILL', 'last^money^inserted', 'UNKNOWN')
                    _Common.store_notes_activity('ERROR', trxid)
                    break
                if _response == 0 and BILL["KEY_RECEIVED"] in _result:
                    cash_in = parse_notes(_result)
                    
                    # Validate Exceed Payment
                    exceed_payment = is_exceed_payment(TARGET_CASH_AMOUNT, cash_in, COLLECTED_CASH)
                    LOGGER.info(('Exceed Payment :', BILL_TYPE, exceed_payment))
                    # NV Cannot Reject Notes Which Enabled Without Special Hold Command
                    if exceed_payment is True:
                        sleep(.5)
                        send_command_to_bill(param=BILL["REJECT"] + '|', output=None)
                        BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                        LOGGER.warning(('Exceed Payment Detected :', json.dumps({'REJECT': cash_in,
                                                                            'COLLECTED': COLLECTED_CASH,
                                                                            'TARGET': TARGET_CASH_AMOUNT})))
                        break
                    
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
                            BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                            break
                        # exceed_payment = is_exceed_payment(TARGET_CASH_AMOUNT, cash_in, COLLECTED_CASH)
                        # LOGGER.info(('Exceed Payment :', BILL_TYPE, exceed_payment))
                        # # NV Cannot Reject Notes Which Enabled Without Special Hold Command
                        # if exceed_payment is True and BILL_TYPE != 'NV':
                        #     sleep(.5)
                        #     send_command_to_bill(param=BILL["REJECT"] + '|', output=None)
                        #     BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.emit('RECEIVE_BILL|BAD_NOTES')
                        #     LOGGER.warning(('Exceed Payment Detected :', json.dumps({'REJECT': cash_in,
                        #                                                         'COLLECTED': COLLECTED_CASH,
                        #                                                         'TARGET': TARGET_CASH_AMOUNT})))
                        #     break
                    # ===========================================
                    # Process Store and Update Data Cash
                    # ===========================================
                    store_result = store_cash_into_cashbox(trxid, str(cash_in))
                    if store_result is True:
                        update_cash_result, store_result = update_cash_status(str(cash_in), store_result)
                        LOGGER.debug(('Cash Store/Update Status:', str(store_result), str(update_cash_result), str(cash_in)))
                        _Common.log_to_config('BILL', 'last^money^inserted', str(cash_in))
                        
                # ===========================================
                # Next Handling When Notes Already Received
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

                if BILL_TYPE == "NV" and NV_LIB_MODE:
                    max_attempt = BILL['MAX_EXECUTION_TIME'] / BILL['LOOP_DELAY']
                else:
                    max_attempt = BILL['RECEIVE_ATTEMPT']

                if attempt == max_attempt:
                    LOGGER.warning(('Stop Bill Acceptor Acceptance By MAX_EXECUTION_TIME', str(attempt), str(BILL['MAX_EXECUTION_TIME'])))
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
            if BILL_TYPE == "NV" and NV_LIB_MODE:
                sleep(BILL['LOOP_DELAY'])
            else:
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
    # total_cash = _Common.get_cash_activity()['total']
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
    LOGGER.debug(('Try Execute Stop Receive Note'))
    try:
        # Extra Handling Stop Bill Event
        if trxid != _Common.ACTIVE_CASH_TRX_ID:
            LOGGER.debug(('Stop Bill Acceptor Disacceptance By ACTIVE_CASH_TRX_ID', str(_Common.ACTIVE_CASH_TRX_ID), str(trxid)))
            return

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
                # Not Receive Any Cash Must VOID Any Signal
                if COLLECTED_CASH == 0:
                    response, result = send_command_to_bill(param=BILL["STOP"]+'|', output=None)
                    LOGGER.info(('HOLD_NOTES WITHOUT ANY CASH RECEIVED', trxid, COLLECTED_CASH))
                    return
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
    _Helper.get_thread().apply_async(bill_store_note, (trxid,))


def bill_store_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY
    IS_RECEIVING = False
    LOGGER.debug(('Try Execute Store Receive Note'))
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

        if response == 0:
            LOGGER.info(('COLLECTED_CASH', COLLECTED_CASH, 'TARGET_CASH_AMOUNT', TARGET_CASH_AMOUNT))
            BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('STORE_BILL|SUCCESS')
        else:
            BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('STORE_BILL|ERROR')
            LOGGER.warning((trxid, str(response), str(result)))
            
            # Do Delete Last Cash Input in cashbox.status
            # _Common.remove_notes_activity(trxid)
            # Put Error Message In that situation
            _Common.store_notes_activity('ERROR', trxid)
            
            # GRG Do Re-init Bill
            if BILL_TYPE == 'GRG': init_bill()
            
    except Exception as e:
        _Common.BILL_ERROR = 'FAILED_STORE_BILL'
        BILL_SIGNDLER.SIGNAL_BILL_STORE.emit('STORE_BILL|ERROR')
        LOGGER.warning(e)
        
    finally:
        # Reset Temporary Calculation
        COLLECTED_CASH = 0
        CASH_HISTORY = []
        CASH_TIME_HISTORY = []
        response, result = send_command_to_bill(param=BILL["STOP"]+'|', output=None)
        LOGGER.debug((BILL['TYPE'], trxid, response, result))


def start_bill_reject_note(trxid):
    _Helper.get_thread().apply_async(bill_reject_note, (trxid,))


def bill_reject_note(trxid):
    global COLLECTED_CASH, CASH_HISTORY, IS_RECEIVING, CASH_TIME_HISTORY
    IS_RECEIVING = False
    LOGGER.debug(('Try Execute Reject Receive Note'))
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

