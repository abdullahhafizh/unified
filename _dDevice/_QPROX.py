__author__ = 'wahyudi@multidaya.id'

from _cConfig import _ConfigParser, _Common
from _cCommand import _Command
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from _tTools import _Helper, _Cryptograpy
from _dDAO import _DAO
from time import sleep
import json
from _nNetwork import _HTTPAccess
from datetime import datetime
import random
import os
import sys, traceback


if _Common.IS_WINDOWS:
    import win32com.client as client
    import pythoncom


LOGGER = logging.getLogger()
QPROX_PORT = _Common.QPROX_PORT
QPROX_BAUDRATE = _Common.QPROX_BAUDRATE
MID_MAN = _Common.MID_MAN
TID_MAN = _Common.TID_MAN
SAM_MAN = _Common.SAM_MAN
MID_BNI = _Common.MID_BNI
TID_BNI = _Common.TID_BNI
MC_BNI = _Common.MC_BNI
SLOT_SAM1_BNI = _Common.SLOT_SAM1_BNI
SLOT_SAM2_BNI = _Common.SLOT_SAM2_BNI
MID_BRI = _Common.MID_BRI
TID_BRI = _Common.TID_BRI
PROCODE_BRI = _Common.PROCODE_BRI
MID_BCA = _Common.MID_BCA
TID_BCA = _Common.TID_BCA

BANKS = _Common.BANKS
# print(BANKS)

BNI_SAM_SLOT = {
    '1': SLOT_SAM1_BNI,
    '2': SLOT_SAM2_BNI
}


QPROX = {
    "RESET_CONTACTLESS": "ST0",
    "READER_DUMP": "RD0",
    "ENABLE_READER_DUMP": "RD1",
    "DISABLE_READER_DUMP": "RD2",
    # -------
    "OPEN": "000",
    "INIT": "001",
    "AUTH": "002",
    "BALANCE": "003", #With Detail Card Attribute
    "TOPUP": "004", #Transfer Balance Offline MANDIRI
    "KA_INFO": "005",
    "CREATE_ONLINE_INFO": "006",
    "INIT_ONLINE": "007",
    "DEBIT": "008",
    "GENERAL_BALANCE": "009",
    "STOP": "010",
    "UPDATE_TID_BNI": "011",
    "INIT_SAM_BNI": "012", #Init SAM BNI (Purse SAM Data)
    "TOPUP_BNI": "013", #Transfer Balance Offline BNI
    "KA_INFO_BNI": "014",
    "PURSE_DATA_BNI": "015", #Get Card Info For Topup Modal
    "SEND_CRYPTO": "016", #Send Cryptogram For Topup Modal
    "REFILL_ZERO": "018", #Refill Zero To Fix Error Update Balance Failure
    "UPDATE_BALANCE_ONLINE_MANDIRI": "019", #Update Balance Online Mandiri
    "PURSE_DATA_BNI_CONTACTLESS": "020", #Get Card Info BNI Tapcash contactless,
    "SEND_CRYPTO_CONTACTLESS": "021", #Send Cryptogram For BNI Tapcash contactless,
    "DEBIT_NO_INIT_SINGLE_REPORT": "022",
    "GET_LAST_TRX_REPORT": "023",
    "UPDATE_BALANCE_ONLINE_BRI": "024", #BRI UBAL ONLINE
    "CARD_HISTORY_BRI": "025", #BRIZZI CARD LOG
    # C2C - Card To Card Mode
    "TOPUP_C2C": "026", 
    "INIT_C2C": "027",
    "CORRECTION_C2C": "028",
    "GET_FEE_C2C": "029",
    "SET_FEE_C2C": "030",
    "FORCE_SETTLEMENT": "031",
    "BALANCE_C2C": "033",
    "UPDATE_BALANCE_C2C_MANDIRI": "035", #Update Balance Online Mandiri For C2C Deposit Slot, TID, MID, Token
    "RAW_APDU": "034", #Send Raw APDU TO Target (255-SAM, 1/2/3/4-Slot)
    "CARD_HISTORY_MANDIRI": "039", #MANDIRI CARD LOG
    "CARD_HISTORY_BNI": "040", #BNI CARD LOG
    "CARD_HISTORY_BNI_RAW": "077", #BNI CARD LOG IN RAW FORMAT
    "BNI_TOPUP_INIT_KEY": "080",
    "SAM_HISTORY_BNI": "042", #BNI SAM LOG
    "GET_LAST_C2C_REPORT": "041", #"Send SAM C2C Slot"
    "TOPUP_ONLINE_DKI": "043", #"Send amount|TID|STAN|MID|InoviceNO|ReffNO "
    "UPDATE_BALANCE_ONLINE_BCA": "044", #BCA UBAL ONLINE TID, MID, Token
    "REVERSAL_ONLINE_BCA": "045", #BCA REVERSAL TID, MID, Token
    "CONFIG_ONLINE_BCA": "046", #BCA REVERSAL TID Topup BCA, MID Topup BCA
    # BCA NEW COMMAND : 2023-06-08
    "CARD_HISTORY_BCA": "047", 
    "CARD_HISTORY_BCA_RAW": "079", 
    # ---
    "BCA_CARD_INFO": "048",
    "REVERSAL_ONLINE_BRI": "049", #parameter sm dengan update balance bri nya
    "REVERSAL_ONLINE_DKI": "050", #parameter sm dengan top up dki nya,
    "REQUEST_TOPUP_DKI": "051", #parameter amount
    "CONFIRM_TOPUP_DKI": "052", #parameter data_to_card (From API)
    "CARD_HISTORY_DKI": "053", 
    "CARD_HISTORY_DKI_RAW": "054", 
    "CARD_HISTORY_BRI_RAW": "078",
}


# 14. UPDATE BALANCE BCA, parameter : TID | MID | TOKEN
# http://localhost:9000/Service/GET?cmd=044&param=01234567|1234567|ASDHKASJHDKSAJDabc&type=json

# 15. REVERSAL BCA, parameter : TID | MID | TOKEN
# http://localhost:9000/Service/GET?cmd=045&param=01234567|1234567|ASDHKASJHDKSAJDabc&type=json

# 16. UPDATE TID MID BCA, parameter : TID | MID
# http://localhost:9000/Service/GET?cmd=046&param=01234567|1234567&type=json

# MANDIRI OLD = NO | DATE | TID | COUNTER | TYPE | AMOUNT | BALANCE
# 0|200520153716|29040100|1295|1500|37450|166139
# #1|230220142147|01234567|1290|1200|1|128693
# #2|230220142532|01234567|1291|1200|1|128692
# #3|230220144318|01234567|1292|1200|1|128691
# #4|230220145239|01234567|1293|1200|1|128690
# #5|230220145302|01234567|1294|1200|1|128689
# #6|200520153716|29040100|1295|1500|37450|166139
# #7|230220135302|01234567|1286|1200|1|128697
# #8|230220135617|01234567|1287|1200|1|128696
# #9|230220141850|01234567|1288|1200|1|128695
# #10|230220142110|01234567|1289|1200|1|128694
# MANDIRI NEW = NO | DATE | TID | COUNTER | TYPE | AMOUNT | BALANCE 
# 0|050320003056|29010100|238|1000|20|189613
# #1|061219134951|20010200|11|1200|1|189570
# #2|171219111857|29010100|497|1000|1|189574
# #3|171219233451|29010100|526|1000|1|189579
# #4|290120000235|29010100|869|1000|1|189592
# BNI =  NO | TIPE | AMOUNT |DATE
# 0|01|1|20200205230607
# #1|01|1|20200203012345
# #2|01|1|20200203012244
# #3|01|1|20200203012150
# #4|01|1|20200203011458

# SERVICE MISSING COMMAND =================
# SEND APDU WITH POINTER
# UBAL SAM C2C DEPOSIT
# C2C GET FEE METHOD
# C2C GET SAM DEPOSIT UID
# C2C GET SAM CARD NO
# DEFINE OLD VS NEW APPLET
# AMOUNT TOPUP C2C + FORCE SETTLEMENT AMOUNT
# C2C UPLOAD CREDENTIAL
# TECH DOC SETTLEMENT FEE INTO  UI
# 


BNI_CARD_NO_SLOT_1 = ''
BNI_CARD_NO_SLOT_2 = ''


class QSignalHandler(QObject):
    __qualname__ = 'QSignalHandler'
    SIGNAL_INIT_QPROX = pyqtSignal(str)
    SIGNAL_DEBIT_QPROX = pyqtSignal(str)
    SIGNAL_AUTH_QPROX = pyqtSignal(str)
    SIGNAL_BALANCE_QPROX = pyqtSignal(str)
    SIGNAL_TOPUP_QPROX = pyqtSignal(str)
    SIGNAL_KA_INFO_QPROX = pyqtSignal(str)
    SIGNAL_ONLINE_INFO_QPROX = pyqtSignal(str)
    SIGNAL_INIT_ONLINE_QPROX = pyqtSignal(str)
    SIGNAL_STOP_QPROX = pyqtSignal(str)
    SIGNAL_REFILL_ZERO = pyqtSignal(str)
    SIGNAL_CARD_HISTORY = pyqtSignal(str)


QP_SIGNDLER = QSignalHandler()
OPEN_STATUS = False
TEST_MODE = _Common.TEST_MODE

# BNI ERROR CARD
ERROR_TOPUP = {
    '5106': 'ERROR_BNI_NOT_PRODUCTION',
    '5103': 'ERROR_BNI_PURSE_DISABLED',
    '1008': 'ERROR_INACTIVECARD',
    'FFFE': 'CARD_NOT_EXIST',
    '1004': 'PROCESS_TIMEOUT',
    'FFFD': 'PROCESS_NOT_FINISHED',
    '6969': 'CARD_NOT_MATCH'
}

# Waive BNI Card Validation
if not _Common.LIVE_MODE:
    ERROR_TOPUP.pop('5106')
    
    
DO_READER_DUMP_ON_CARD_HISTORY = False


def do_get_reader_dump(event, reff=None):
    if not _Common.SUPPORT_DUMP_VERSION: return
    if not DO_READER_DUMP_ON_CARD_HISTORY and 'get_card_history' in event: return 
    reff = _Helper.time_string('%Y%m%d%H%M%S') if reff is None else reff
    param = QPROX['READER_DUMP'] + '|' + event + '|'  + reff
    dump_response, dump_result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    LOGGER.info((dump_response, dump_result))
    

def start_disable_reader_dump():
    _Helper.get_thread().apply_async(disable_reader_dump)
    
    
def start_reset_reader_contact():
    _Helper.get_thread().apply_async(reset_card_contactless)
    

def start_enable_reader_dump():
    _Helper.get_thread().apply_async(enable_reader_dump)
    

def disable_reader_dump():
    # Add Reset Contact
    reset_card_contactless()
    if not _Common.SUPPORT_DUMP_VERSION: return
    if _Common.QPROX_READER_FORCE_DUMP:
        LOGGER.info(('QPROX_READER_FORCE_DUMP', _Common.QPROX_READER_FORCE_DUMP))
        return
    param = QPROX['DISABLE_READER_DUMP'] + '|'
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    LOGGER.info((response, result))
    
    
def enable_reader_dump():
    if not _Common.SUPPORT_DUMP_VERSION: return
    param = QPROX['ENABLE_READER_DUMP'] + '|'
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    LOGGER.info((response, result))


def bni_crypto_deposit(card_info, cyptogram, slot=1, bank='BNI'):
    if bank == 'BNI':
        #Getting Previous samBalance
        samPrevBalance = _Common.BNI_SAM_1_WALLET if slot == 1 else _Common.BNI_SAM_2_WALLET
        # Converting Default Slot into Actual Slot
        alias_slot = BNI_SAM_SLOT.get(str(slot))
        if alias_slot == '---' or _Common.BNI_SINGLE_SAM is True:
            alias_slot = SLOT_SAM1_BNI
        if len(card_info) == 0 or card_info is None:
            LOGGER.warning((str(card_info), 'WRONG_VALUE'))
            return False
        if len(cyptogram) == 0 or cyptogram is None:
            LOGGER.warning((str(cyptogram), 'WRONG_VALUE'))
            return False
        param = QPROX['SEND_CRYPTO'] + '|' + str(alias_slot) + '|' + str(card_info) + '|' + str(cyptogram)
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        # LOGGER.debug((result))
        if response == 0 and len(result) > 10:
            result = result.replace('#', '')
            output = {
                'result': result,
                'bank_id': '2',
                'bank_name': bank,
            }
            sleep(1)
            bni_c2c_balance_info(slot=slot)
            # get_card_info(slot=slot)
            # LOGGER.info((str(slot), bank, str(output)))
            samCardNo = _Common.BNI_SAM_1_NO if slot == 1 else _Common.BNI_SAM_2_NO
            samLastBalance = _Common.BNI_SAM_1_WALLET if slot == 1 else _Common.BNI_SAM_2_WALLET
            param = {
                'trxid': 'REFILL_SAM',
                'samCardNo': samCardNo,
                'samCardSlot': slot,
                'samPrevBalance': samPrevBalance,
                'samLastBalance': samLastBalance,
                'topupCardNo': '',
                'topupPrevBalance': samPrevBalance,
                'topupLastBalance': samLastBalance,
                'status': 'REFILL_SUCCESS',
                'remarks': result,
            }
            bni_topup_amount = int(samLastBalance) - int(samPrevBalance)
            # Update Audit Summary
            # bni_deposit_refill_count              BIGINT DEFAULT 0,
            # bni_deposit_refill_amount             BIGINT DEFAULT 0,
            # bni_deposit_last_balance              BIGINT DEFAULT 0,
            _DAO.create_today_report(_Common.TID)
            _DAO.update_today_summary_multikeys(['bni_deposit_refill_count'], 1)
            _DAO.update_today_summary_multikeys(['bni_deposit_refill_amount'], int(bni_topup_amount))
            _DAO.update_today_summary_multikeys(['bni_deposit_last_balance'], int(samLastBalance))
            _Common.store_upload_sam_audit(param)
            sleep(3)
            _Common.upload_bni_wallet()
            _Common.TRIGGER_MANUAL_TOPUP = True
            output['last_balance'] = samLastBalance
            return output
        else:
            #_Common.online_logger([result, card_info, cyptogram, slot, bank], 'general')
            _Common.NFC_ERROR = 'SEND_CRYPTO_BNI_ERROR_SLOT_'+str(slot)
            return False
    else:
        return False


# MO_REPORT
# 0001754699000002558375469900000255835A929C0E8DCEC98A95A574DE68D93CBB000000000100000088889999040000002D04C36E88889999040000002D04C36E0000000000000000000079EC3F7C7EED867EBC676CD434082D2F

def get_card_info(slot=1, bank='BNI'):
    global BNI_CARD_NO_SLOT_1, BNI_CARD_NO_SLOT_2
    if bank == 'BNI':
        # slot is index/sequence 0 and 1
        _slot = slot - 1
        param = QPROX['PURSE_DATA_BNI'] + '|' + str(_slot)
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        LOGGER.debug((result))
        if response == 0 and len(result) > 10:
            result = result.replace('#', '')
            output = {
                'card_info': result,
                'card_no': result[4:20],
                'bank_tid': _Common.TID_BNI,
                'bank_id': '2',
                'bank_name': bank,
            }
            # bni_c2c_balance_info(slot=slot)
            if slot == 1:
                _Common.BNI_SAM_1_NO = BNI_CARD_NO_SLOT_1 = output['card_no'] 
            if slot == 2:
                _Common.BNI_SAM_2_NO = BNI_CARD_NO_SLOT_2 = output['card_no']
            LOGGER.debug(('set_bni_sam_no', str(slot), output['card_no']))
            _Common.set_bni_sam_no(str(slot), output['card_no'])
            LOGGER.info((str(slot), bank, str(output)))
            return output
        else:
            if slot == 1:
                _Common.BNI_SAM_1_NO = ''
                BNI_CARD_NO_SLOT_1 = '' 
            if slot == 2:
                _Common.BNI_SAM_2_NO = ''
                BNI_CARD_NO_SLOT_2 = ''
            _Common.NFC_ERROR = 'CHECK_CARD_INFO_BNI_ERROR_SLOT_'+str(slot)
            return False
    elif bank == 'MANDIRI_C2C':
        # TODO Add Logic Handler Here
        pass
    elif bank == 'BNI_SAM_RAW_PURSE':
        _slot = slot - 1
        param = QPROX['PURSE_DATA_BNI'] + '|' + str(_slot) + '|' + 'BNI_SAM_RAW_PURSE' + '|'
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        LOGGER.debug((result))
        if response == 0:
            return result
        else:
            return ''
    else:
        return False


def open():
    global OPEN_STATUS
    if QPROX_PORT is None:
        LOGGER.debug(("port : ", QPROX_PORT))
        _Common.NFC_ERROR = 'PORT_NOT_DEFINED'
        return False
    param = QPROX["OPEN"] + "|" + QPROX_PORT + "|" + QPROX_BAUDRATE
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((param, result))
    OPEN_STATUS = True if response == 0 else False
    return OPEN_STATUS


def start_disconnect_qprox():
    _Helper.get_thread().apply_async(disconnect_qprox)


def disconnect_qprox():
    param = QPROX['STOP'] + '|'
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((response, result))


INIT_STATUS = False
INIT_MANDIRI = False
INIT_BNI = False
INIT_BRI = False
INIT_BCA = True
INIT_LIST = []
INIT_DELAY_TIME = int(_Common.INIT_DELAY_TIME)


# Route Check Method to Non / Secure Channel
def execute_topup_config_check(_param={}, _bank=''):
    LOGGER.debug((_param, _bank))
    if _Helper.empty(_param) or _Helper.empty(_bank): 
        return False, {'response': {'code': 999}}
    _bank = _bank.lower()
    _url = TOPUP_URL + 'topup-'+_bank+'/card-check?tid=' + _Common.TID
    # Non-Secure channel
    if not _Common.SECURE_CHANNEL_TOPUP:
        return _HTTPAccess.post_to_url(url=_url, param=_param)
    
    # UPDATE_BALANCE_URL_DEV = 'http://apidev.mdd.co.id:28194/v1/'
    _url = _url.replace('/v1/', '/enc-kiosk/')
    # AES-128-CBC Output in HEX
    encrypt_status, encrypt_result = _Cryptograpy.encrypt_aes(
                plaintext=json.dumps(_param),
                key=_Common.CORE_MID
            )
    if not _Common.LIVE_MODE:
        LOGGER.debug(('Encypt Result', str(encrypt_result)))
    if not encrypt_status:
        return False, {'response': {'code': 999}}
    _payload = {
            'data': encrypt_result
        }
    _header = _HTTPAccess.HEADER 
    _header['Kiosk-Partner-ID'] = _Common.CORE_MID
    _header['Kiosk-Terminal-ID'] = _Common.TID
    _header['Kiosk-Timestamp'] = str(_Helper.now())
    return _HTTPAccess.post_to_url(url=_url, param=_payload, header=_header)


def execute_topup_sof_check(_param={}):
    _url = TOPUP_URL + 'topup-online/sof-check?tid=' + _Common.TID    
    _url = _url.replace('/v1/', '/enc-kiosk/')

    # AES-128-CBC Output in HEX
    encrypt_status, encrypt_result = _Cryptograpy.encrypt_aes(
                plaintext=json.dumps(_param),
                key=_Common.CORE_MID
            )
    if not _Common.LIVE_MODE:
        LOGGER.debug(('Encypt Result', str(encrypt_result)))
    if not encrypt_status:
        return
    _payload = {
            'data': encrypt_result
        }
    _header = _HTTPAccess.HEADER 
    _header['Kiosk-Partner-ID'] = _Common.CORE_MID
    _header['Kiosk-Terminal-ID'] = _Common.TID
    _header['Kiosk-Timestamp'] = str(_Helper.now())
    _Common.BRI_TOPUP_ONLINE = False       
    _Common.BCA_TOPUP_ONLINE = False
    _Common.DKI_TOPUP_ONLINE = False 
    status, response = _HTTPAccess.post_to_url(url=_url, param=_payload, header=_header)
    if status == 200 and response['response']['code'] == 200:
        _Common.BRI_TOPUP_ONLINE = response['data']['BRI']['status']        
        _Common.BCA_TOPUP_ONLINE = response['data']['BCA']['status']        
        _Common.DKI_TOPUP_ONLINE = response['data']['DKI']['status']        


def validate_topup_online_config(bank=None):
    if bank is None: return
    param = _Common.serialize_payload({})
    # Fixed By Using ? to define it as Query String
    try:
        if bank == 'BRI':
            param['card_no'] = '6013' + ('0'*12)            
            status, response = execute_topup_config_check(_param=param, _bank=bank)
            LOGGER.info((response, str(param)))
            _Common.BRI_TOPUP_ONLINE = (status == 200 and response['response']['code'] == 200)
        elif bank == 'BCA':
            param['card_no'] = '0145' + ('0'*12)
            status, response = execute_topup_config_check(_param=param, _bank=bank)
            LOGGER.info((response, str(param)))
            _Common.BCA_TOPUP_ONLINE = (status == 200 and response['response']['code'] == 200)
        elif bank == 'DKI':
            param['card_no'] = '9360' + ('0'*12)
            status, response = execute_topup_config_check(_param=param, _bank=bank)
            LOGGER.info((response, str(param)))
            _Common.DKI_TOPUP_ONLINE = (status == 200 and response['response']['code'] == 200)
    except Exception as e:
        LOGGER.warning((e))


def start_init_config():
    _Helper.get_thread().apply_async(init_config)


def init_config():
    global INIT_STATUS, INIT_LIST, INIT_BNI, INIT_MANDIRI, INIT_BCA
    if OPEN_STATUS is not True:
        LOGGER.warning(('OPEN STATUS', str(OPEN_STATUS)))
        _Common.NFC_ERROR = 'PORT_NOT_OPENED'
        return
    try:
        for BANK in BANKS:
            if BANK['TOPUP_CHANNEL'] == 'ONLINE':
                if BANK['STATUS'] is True:
                    validate_topup_online_config(BANK['BANK'])
            else:
                if BANK['STATUS'] is True:
                    if BANK['BANK'] == 'MANDIRI':
                        param = QPROX['INIT'] + '|' + QPROX_PORT + '|' + BANK['SAM'] + \
                                    '|' + BANK['MID'] + '|' + BANK['TID']
                        response, result = _Command.send_request(param=param, output=None)
                        if response == 0:
                            LOGGER.info((BANK['BANK'], result))
                            INIT_LIST.append(BANK)
                            INIT_STATUS = True
                            if _Common.C2C_MODE is True:
                                _param = QPROX['INIT_C2C'] + '|' + _Common.C2C_TID + \
                                    '|' + _Common.C2C_MACTROS + '|' + _Common.C2C_SAM_SLOT
                                _response, _result = _Command.send_request(param=_param, output=None)
                                # {"Result":"0000","Command":"027","Parameter":"51040188|5104010000750000|1","Response":"","ErrorDesc":"Sukses"}
                                if _response == 0:
                                    INIT_MANDIRI = True
                                    mdr_c2c_balance_info()
                                else:
                                    LOGGER.warning(('FAILED_INIT_C2C_CONFIG', _response, _result))
                            else:
                                if _Common.active_auth_session():
                                    INIT_MANDIRI = True
                                # Positive Assumption Last Update Bringing KA LOGIN Session
                                if _Common.last_update_attempt():
                                    INIT_MANDIRI = True
                                    _Common.log_to_temp_config('last^auth')
                                if _Common.MANDIRI_SINGLE_SAM is True:
                                    # _Common.MANDIRI_ACTIVE = 1
                                    # _Common.save_sam_config(bank='MANDIRI')
                                    ka_info_mandiri(str(_Common.MANDIRI_ACTIVE), caller='FIRST_INIT_SINGLE_SAM')
                                else:
                                    ka_info_mandiri(str(_Common.get_active_sam(bank='MANDIRI', reverse=True)), caller='FIRST_INIT')
                        else:
                            LOGGER.warning((BANK['BANK'], result))
                    if BANK['BANK'] == 'BNI':
                        inject_param = QPROX['BNI_TOPUP_INIT_KEY'] + '|' + _Common.BNI_C2C_MASTER_KEY + '|' + _Common.BNI_C2C_PIN + '|' + TID_BNI
                        response, result = _Command.send_request(param=inject_param, output=None)
                        if response == 0:
                            LOGGER.info((BANK['BANK'], 'INJECT_KEY', result))
                            init_param = QPROX['UPDATE_TID_BNI'] + '|' + _Common.TID_BNI
                            response, result = _Command.send_request(param=init_param, output=None)
                            LOGGER.info((BANK['BANK'], 'UPDATE_TID', result))
                            if response == 0:
                                INIT_LIST.append(BANK)
                                INIT_STATUS = True
                                INIT_BNI = True
                                sleep(1)
                                bni_c2c_balance_info(slot=_Common.BNI_ACTIVE)
                                sleep(1)
                                get_card_info(slot=_Common.BNI_ACTIVE, bank='BNI')
                        # param = QPROX['BNI_TOPUP_INIT_KEY'] + '|' + _Common.BNI_C2C_MASTER_KEY + '|' + _Common.BNI_C2C_PIN + '|' +  TID_BNI
                        # response, result = _Command.send_request(param=param, output=None)
                        # if response == 0:
                        #     LOGGER.info((BANK['BANK'], result))
                        #     INIT_LIST.append(BANK)
                        #     INIT_STATUS = True
                        #     INIT_BNI = True
                        #     sleep(INIT_DELAY_TIME)
                        #     bni_c2c_balance_info(slot=_Common.BNI_ACTIVE)
                            # get_bni_wallet_status()
                        else:
                            LOGGER.warning((BANK['BANK'], result))
                    sleep(INIT_DELAY_TIME)
            continue
    except Exception as e:
        _Common.NFC_ERROR = 'FAILED_TO_INIT'
        LOGGER.warning((e))
    finally:
        if _Common.QPROX_READER_FORCE_DUMP:
            enable_reader_dump()
        else:
            disable_reader_dump()
    # finally:
    #     # Retry Read BNI SAM Balance
    #     if INIT_BNI is True and _Common.BNI_ACTIVE_WALLET <= 0:
    #         sleep(INIT_DELAY_TIME)
    #         bni_c2c_balance_info(slot=_Common.BNI_ACTIVE)
        

def start_recheck_bni_sam_balance():
    _Helper.get_thread().apply_async(recheck_bni_sam_balance,)

    
def recheck_bni_sam_balance():
    if INIT_BNI is True and _Common.BNI_ACTIVE_WALLET <= 0:
        bni_c2c_balance_info(slot=_Common.BNI_ACTIVE)
        sleep(1)
        get_card_info(slot=_Common.BNI_ACTIVE, bank='BNI')    


def start_debit_qprox(amount):
    _Helper.get_thread().apply_async(debit_qprox, (amount,))


def debit_qprox(amount):
    if len(INIT_LIST) == 0:
        LOGGER.warning(('INIT_LIST', str(INIT_LIST)))
        QP_SIGNDLER.SIGNAL_DEBIT_QPROX.emit('DEBIT|' + 'ERROR')
        _Common.NFC_ERROR = 'EMPTY_INIT_LIST'
        return
    param = QPROX['DEBIT'] + '|' + str(amount)
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((result))
    if response == 0 and result is not None:
        QP_SIGNDLER.SIGNAL_DEBIT_QPROX.emit('DEBIT|' + str(result))
    else:
        _Common.NFC_ERROR = 'DEBIT_ERROR'
        QP_SIGNDLER.SIGNAL_DEBIT_QPROX.emit('DEBIT|' + 'ERROR')


def start_auth_ka_mandiri():
    print('pyt: Waiting Login Card To Be Put Into Reader...')
    _Helper.get_thread().apply_async(auth_ka_mandiri)


def auth_ka_mandiri(_slot=None, initial=True):
    global INIT_MANDIRI
    if len(INIT_LIST) == 0:
        LOGGER.warning(('INIT_LIST', str(INIT_LIST)))
        QP_SIGNDLER.SIGNAL_AUTH_QPROX.emit('AUTH_KA|ERROR')
        _Common.NFC_ERROR = 'EMPTY_INIT_LIST'
        return
    # Stop Process Auth If Detected as C2C
    if _Common.C2C_MODE is True:
        QP_SIGNDLER.SIGNAL_AUTH_QPROX.emit('AUTH_KA|SUCCESS')
        return
    __single_sam = _Common.mandiri_single_sam()
    if __single_sam is True:
        _Common.MANDIRI_ACTIVE = 1
        _Common.save_sam_config(bank='MANDIRI')
    if _slot is None:
        if __single_sam:
            _slot = str(_Common.MANDIRI_ACTIVE)
        else:
            _slot = str(_Common.get_active_sam(bank='MANDIRI', reverse=True))
    _ka_pin = _Common.KA_PIN1
    if _slot == '2':
        _ka_pin = _Common.KA_PIN2
    param = QPROX['AUTH'] + '|' + QPROX_PORT + '|' + _slot + '|' + BANKS[0]['SAM'] + '|' + BANKS[0]['MID'] + '|' + \
            BANKS[0]['TID'] + '|' + _ka_pin + '|' + _Common.KL_PIN
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((_slot, result))
    if response == 0 and _Common.KA_NIK == result:
        # Log Auth Time
        _Common.log_to_temp_config()
        INIT_MANDIRI = True
        ka_info_mandiri(slot=_slot, caller='KA_AUTH')
        if initial is False or __single_sam is True:
            QP_SIGNDLER.SIGNAL_AUTH_QPROX.emit('AUTH_KA|SUCCESS')
        else:
            __slot = str(_Common.get_active_sam(bank='MANDIRI', reverse=True))
            __ka_pin = _Common.KA_PIN1
            if __slot == '2':
                __ka_pin = _Common.KA_PIN2
            __ka_pin = _Common.KA_PIN2
            __param = QPROX['AUTH'] + '|' + QPROX_PORT + '|' + __slot + '|' + BANKS[0]['SAM'] + '|' + BANKS[0]['MID'] \
                      + '|' + BANKS[0]['TID'] + '|' + __ka_pin + '|' + _Common.KL_PIN
            __response, __result = _Command.send_request(param=__param, output=None)
            LOGGER.debug((__slot, __result))
            if __response == 0:
                ka_info_mandiri(slot=__slot, caller='KA_AUTH_#2')
                QP_SIGNDLER.SIGNAL_AUTH_QPROX.emit('AUTH_KA|SUCCESS')
            else:
                _Common.NFC_ERROR = 'AUTH_KA_MANDIRI_ERROR'
                QP_SIGNDLER.SIGNAL_AUTH_QPROX.emit('AUTH_KA|'+str(__result))
    else:
        _Common.NFC_ERROR = 'AUTH_KA_MANDIRI_ERROR'
        QP_SIGNDLER.SIGNAL_AUTH_QPROX.emit('AUTH_KA|'+str(result))


def start_check_card_balance():
    _Helper.get_thread().apply_async(check_card_balance)


LAST_CARD_CHECK = None   
FW_BANK = _Common.FW_BANK

DUMMY_BALANCE_CHECK_BALANCE = [
        {
            'balance': '999999',
            'card_no': '60321111222333',
            'bank_type': '1',
            'bank_name': 'MANDIRI',
            'able_check_log': '0',
            'able_topup': '0000',
        },
        {
            'balance': '999999',
            'card_no': '75461111222333',
            'bank_type': '2',
            'bank_name': 'BNI',
            'able_check_log': '0',
            'able_topup': '0000',
        },
        {
            'balance': '999999',
            'card_no': '60131111222333',
            'bank_type': '3',
            'bank_name': 'BRI',
            'able_check_log': '1',
            'able_topup': '0000',
        },
        {
            'balance': '999999',
            'card_no': '10451111222333',
            'bank_type': '4',
            'bank_name': 'BCA',
            'able_check_log': '0',
            'able_topup': '0000',
        },
]


def check_card_balance():
    global LAST_CARD_CHECK
    param = QPROX['BALANCE'] + '|'
    # Start Force Testing Mode ==========================
    if _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
        dummy_output = random.choice(DUMMY_BALANCE_CHECK_BALANCE)
        QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|' + json.dumps(dummy_output))
        return
    # End Force Testing Mode ==========================
    # reset_card_contactless()
    
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((param, result))
    if response == 0 and '|' in result:
        bank_type = result.split('|')[2].replace('#', '')
        
        bank_name = FW_BANK.get(bank_type, 'N/A')
        card_no = result.split('|')[1].replace('#', '')
        if bank_type == '8':
            bank_type = '0'
            
        # Validation of Certain Bank Prepaid VS Theme
        if _Common.VIEW_CONFIG['theme_name'].lower() in _Common.SPESIFIC_PREPAID_PROVIDER.lower():
            selected_provider = _Common.SPESIFIC_PREPAID_PROVIDER.lower().split(':')
            if card_no[:4] not in selected_provider:
                QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|INVALID_PROVIDER')
                LOGGER.debug(('Spesific Provider Not Match', card_no[:4], _Common.VIEW_CONFIG['theme_name'], _Common.SPESIFIC_PREPAID_PROVIDER))
                return
            
        balance = result.split('|')[0]  
        able_check_log = '1' if bank_name in _Common.ALLOWED_BANK_CHECK_CARD_LOG else '0'
        output = {
            'balance': balance,
            'card_no': card_no,
            'bank_type': bank_type,
            'bank_name': bank_name,
            # 'able_topup': result.split('|')[3].replace('#', ''),
            'able_check_log': able_check_log,
            'able_topup': '0000', #Default
        }
        # Spesific Card Handling Per Bank
        if bank_name == 'MANDIRI':
            if card_no in _Common.MANDIRI_CARD_BLOCKED_LIST:
                output['able_topup'] = '1004'
            if card_no[:10] in _Common.MANDIRI_CLOSE_TOPUP_BIN_RANGE:
                output['able_topup'] = '1031'
            # LOGGER.debug((card_no, _Common.MANDIRI_CARD_BLOCKED_LIST, output))
        elif bank_name == 'BNI':
            output['able_topup'] = result.split('|')[3].replace('#', '')
            # Drop Balance Check If Not Available For Topup
            if output['able_topup'] not in ERROR_TOPUP.keys():
                output['able_topup'] = '0000'
        elif bank_name in _Common.TOPUP_ONLINE_BANK: # BRI, BCA, DKI
            # Topup Online Connection Validation
            _Common.IS_ONLINE = _Helper.is_online(bank_name.lower()+'_balance_check')
            _Common.KIOSK_STATUS = 'ONLINE' if _Common.IS_ONLINE else 'OFFLINE'
            output['able_topup'] = '0000' if _Common.IS_ONLINE else '9999'
        
        # Global Blacklist Validation
        if card_no in _Common.GENERAL_CARD_BLOCKED_LIST:
            output['able_topup'] = 'BLOCKED'
            
        # Final Validation From Topup Feature Setting
        if not _Common.CARD_TOPUP_FEATURES.get(bank_name, False):
            output['able_topup'] = 'DISABLED'

        # Add Timestamp in Card Check
        output['timestamp'] = _Helper.time_string()
        
        LAST_CARD_CHECK = output
        _Common.store_to_temp_data('last-card-check', json.dumps(output))
        _Common.NFC_ERROR = ''
        QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|' + json.dumps(output))
    else:
        # '003|', '{"statusCode": -999, "statusMessage": "Service Response Timeout/No Response From Device"}'
        try:
            output = json.loads(result)
            if 'statusCode' in output.keys():
                if output['statusCode'] == -999:
                    LOGGER.warning(('SERVICE_NOT_RESPONSE_DETECTED', 'RESTART_SERVICE', 'RE_INIT_READER'))
                    do_reinit_reader()
        except:
            pass
        QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|ERROR')
        

def restart_mdd_service():
    try:
        # pythoncom.CoInitialize()
        # shell = client.Dispatch("WScript.shell")
        os.system("net stop MDDTopUpService") 
        # shell.Run("net stop MDDTopUpService") 
        sleep(1)
        # shell.Run("net start MDDTopUpService") 
        os.system("net start MDDTopUpService") 
        return True
    except Exception as e:
        LOGGER.warning((e))
        return False
    

def do_reinit_reader():
    if restart_mdd_service():
        print("pyt: [INFO] Re-Init Prepaid Reader...")
        if open() is True:
            print("pyt: [INFO] Re-Init Bank Offline Config...")
            init_config()
            sleep(1)
            print("pyt: [INFO] Re-Init BCA Config...")
            init_config_bca()


def bca_card_info():
    param = QPROX['BCA_CARD_INFO'] + '|'
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((param, result))
    if response == 0 and len(result) >= 512:
        return True, result
    else:
        return False, result


def direct_card_balance(history_on=[]):
    param = QPROX['BALANCE'] + '|'
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((param, result))
    if response == 0 and '|' in result:
        bank_type = result.split('|')[2].replace('#', '')
        bank_name = FW_BANK.get(bank_type, 'N/A')
        card_no = result.split('|')[1].replace('#', '')
        if bank_type == '8':
            bank_type = '0'
        balance = result.split('|')[0]  
        able_check_log = '1' if bank_name in _Common.ALLOWED_BANK_CHECK_CARD_LOG else '0'
        output = {
            'balance': balance,
            'card_no': card_no,
            'bank_type': bank_type,
            'bank_name': bank_name,
            # 'able_topup': result.split('|')[3].replace('#', ''),
            'able_check_log': able_check_log,
            'able_topup': '0000', #Force Allowed Topup For All Non BNI
        }
        # Special Handling For BNI Tapcash
        if bank_name == 'MANDIRI':
            if card_no in _Common.MANDIRI_CARD_BLOCKED_LIST:
                output['able_topup'] = '1004'
            if card_no[:10] in _Common.MANDIRI_CLOSE_TOPUP_BIN_RANGE:
                output['able_topup'] = '1031'
            # LOGGER.debug((card_no, _Common.MANDIRI_CARD_BLOCKED_LIST, output))
        elif bank_name == 'BNI':
            output['able_topup'] = result.split('|')[3].replace('#', '')
            # Drop Balance Check If Not Available For Topup
            if output['able_topup'] in ERROR_TOPUP.keys():
                output['able_topup'] = '1004'
            else:
                output['able_topup'] = '0000'
        
        # Add Direct Check History On Certain Condition
        if bank_name in history_on:
            if bank_name == 'BCA': output['history'] = bca_card_history_direct()
            if bank_name == 'MANDIRI': output['history'] = mdr_card_history_direct()
            if bank_name == 'BNI': output['history'] = bni_card_history_direct()
            if bank_name == 'BRI': output['history'] = bri_card_history_direct()
            if bank_name == 'DKI': output['history'] = dki_card_history_direct()
                
        # Add Check Balance Timestamp
        output['timestamp'] = _Helper.time_string()
        
        # Validate MDD General Black List
        if card_no in _Common.GENERAL_CARD_BLOCKED_LIST:
            output['able_topup'] = 'BLOCKED'
        
        return output
    else:
        return False


def start_topup_offline_mandiri(amount, trxid):
    _Helper.get_thread().apply_async(topup_offline_mandiri_c2c, (amount, trxid,))


LAST_MANDIRI_C2C_REPORT = ""


def parse_c2c_report(report='', reff_no='', amount=0, status='0000'):
    global LAST_MANDIRI_C2C_REPORT
    if _Common.empty(report) or len(report) < 196:
        LOGGER.warning(('EMPTY/MISSMATCH REPORT LENGTH'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#WRONG_REPORT_LENGTH')
        return
    # Store To Memory Last Mandiri C2C Report
    LAST_MANDIRI_C2C_REPORT = report
    if '|' not in report:
        report = '0|'+report
    # 603298180000003600030D706E8693EA7B051040100120D0070000007D0000160520174428270F0000BA0F03DC050000992DA3603298608319158400030D706E8693EA7B510401880110F40100003A5D0100160520174428270F0000C4030361F63B
    try:
        r = report.split('|')
        __data = r[1]
        if len(r[1]) >= 196: 
            if r[1][:4] == '6308':
                #Trim Extra chars 4 in front, and get 196
                # |6308603298180000003600030D706E8693EA7B051040100120D0070000606D0000140520103434130F0000680F03DC050000739F8D603298608319158400030D706E8693EA7B510401880110F401000012400000140520103434130F00009A0303434D3490D
                # 603298180000003600030D706E8693EA7B051040100120D0070000606D0000140520103434130F0000680F03DC050000739F8D
                # 603298608319158400030D706E8693EA7B510401880110F401000012400000140520103434130F00009A0303434D34
                __data = r[1][4:200] 
            elif r[1][:2] == '08':
                #Trim Extra chars 2 in front, and get 196
                # |08603298180000003600030D706E8693EA7B510401880120B80B0000803E0000140520120659000000096C0F03DC050000FBA77B603298407586934100750D706E8693EA7B051040180110DC050000CA3E0100140520120659000000090009831C09FB3
                # 603298180000003600030D706E8693EA7B510401880120B80B0000803E0000140520120659000000096C0F03DC050000FBA77B
                # 603298407586934100750D706E8693EA7B051040180110DC050000CA3E0100140520120659000000090009831C09FB
                __data = r[1][2:198]
        __report_deposit = __data[:102]
        __report_emoney = __data[102:]
        # Update Local Mandiri Wallet
        __deposit_prev_balance = _Common.MANDIRI_ACTIVE_WALLET
        # TODO: Check If Balance is Initial or after process topup
        __deposit_last_balance = _Helper.reverse_hexdec(__report_deposit[54:62])
        if __deposit_last_balance > 0:
            _Common.MANDIRI_WALLET_1 = __deposit_last_balance
            _Common.MANDIRI_ACTIVE_WALLET = _Common.MANDIRI_WALLET_1
            MANDIRI_DEPOSIT_BALANCE = _Common.MANDIRI_ACTIVE_WALLET
        else:
            __deposit_prev_balance = _Common.MANDIRI_ACTIVE_WALLET + int(amount)
            __deposit_last_balance = _Common.MANDIRI_ACTIVE_WALLET
        __card_last_balance = _Helper.reverse_hexdec(__report_emoney[54:62])
        # Handle Force Settlement as Success TRX | Redefine Emoney Last Balance
        last_card_check = _Common.load_from_temp_data('last-card-check', 'json')

        if status == '0000' and __card_last_balance == 0:
            __card_last_balance = int(last_card_check['balance']) + (int(amount) - int(_Common.KIOSK_ADMIN))
            LOGGER.info(('REDEFINE EMONEY LAST BALANCE FROM FORCE_SETTLEMENT', __card_last_balance))
        # if not _Helper.empty(r[0].strip()) or r[0] != '0':
        #     __card_last_balance = r[0].strip()
        if __report_emoney[:16] == last_card_check['card_no']:
            __card_prev_balance = last_card_check['balance']
        else:
            __card_prev_balance = (int(__card_last_balance) - int(amount)) - int(_Common.KIOSK_ADMIN)
            
        output = {
            'last_balance': __card_last_balance,
            'report_sam': __report_emoney,
            'card_no': __report_emoney[:16],
            'report_ka': __report_deposit,
            'bank_id': '1',
            'bank_name': 'MANDIRI',
            'c2c_mode': '1',
        }
        # Store Ouput Record Into Local DB
        _Common.local_store_topup_record(output)
        if status == '0000':
            # Emit Topup Success Record Into Local DB
            output['prev_balance'] = __card_prev_balance
            output['deposit_no'] = __report_deposit[:16]
            output['deposit_prev_balance'] = __deposit_prev_balance
            output['deposit_last_balance'] = __deposit_last_balance
            output['topup_report'] = __data
            LOGGER.info((str(output)))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit(status+'|'+json.dumps(output))
        elif status in ['101C', 'FAILED']:
            # Renew C2C Deposit Balance Info
            mdr_c2c_balance_info()        
        # Ensure The C2C_DEPOSIT_NO same with Report
        if __report_deposit[:16] != _Common.C2C_DEPOSIT_NO:
            _Common.C2C_DEPOSIT_NO = __report_deposit[:16]
            _Common.MANDIRI_SAM_NO_1 = _Common.C2C_DEPOSIT_NO
        _Common.log_to_temp_config('c2c^card^no', __report_deposit[:16])
        param = {
            'trxid': reff_no,
            'samCardNo': _Common.C2C_DEPOSIT_NO,
            'samCardSlot': _Common.C2C_SAM_SLOT,
            'samPrevBalance': __deposit_prev_balance,
            'samLastBalance': __deposit_last_balance,
            'topupCardNo': __report_emoney[:16],
            'topupPrevBalance': __card_prev_balance,
            'topupLastBalance': __card_last_balance,
            'status': status,
            'remarks': __data,
            'c2c_mode': '1',
        }
        _Common.store_upload_sam_audit(param)
        # Update to server
        # Disabled = 2022-12-27
        # _Common.upload_mandiri_wallet()
    except Exception as e:
        LOGGER.warning((e, report, reff_no, amount, status))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#EXCEPTION_PARSING_REPORT')


def start_topup_mandiri_correction(amount, trxid):
    _Helper.get_thread().apply_async(top_up_mandiri_correction, (amount, trxid,))
        

def start_topup_bni_correction(amount, trxid):
    _Helper.get_thread().apply_async(topup_bni_correction, (amount, trxid,))


# 01, 02, 03
LAST_C2C_APP_TYPE = '0'
FORCE_MANDIRI_CHECK_NO = True


# Check Deposit Balance If Failed, When Deducted Hit Correction, If Correction Failed, Hit FOrce Settlement And Store
def top_up_mandiri_correction(amount, trxid=''):
    # Check Correction Result
    reset_card_contactless()
    # Add Check Card Number First Before Correction - Optional
    response, result = _Command.send_request(param=QPROX['BALANCE'] + '|', output=_Command.MO_REPORT)
    LOGGER.debug((response, result))
    # check_card_no = LAST_CARD_CHECK['card_no']
    check_card_no = '0'
    last_balance = '0'
    # if FORCE_MANDIRI_CHECK_NO is True:
    #     check_card_no = LAST_CARD_CHECK['card_no']
    #     last_balance = LAST_CARD_CHECK['balance']
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    
    last_audit_result = _Common.load_from_temp_data(trxid+'-last-audit-result', 'json')
    # rc = last_audit_result.get('err_code', 'FFFF').upper()
    rc = _Common.LAST_READER_ERR_CODE
    
    if response == 0 and '|' in result:
        check_card_no = result.split('|')[1].replace('#', '')
        last_balance = result.split('|')[0]
    else:
        LOGGER.warning(('CARD_NO NOT DETECTED', check_card_no, last_card_check['card_no'], trxid, result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_TOPUP_CORRECTION#RC_1024')
        return
    if last_card_check['card_no'] != check_card_no:
        LOGGER.warning(('MDR_CARD_MISSMATCH', check_card_no, last_card_check['card_no'], trxid, result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_TOPUP_CORRECTION#RC_'+rc)
        # get_force_settlement(amount, trxid)
        return
    # Add Customer Last Balance Card Check After Topup C2C Failure
    last_audit_result = _Common.load_from_temp_data(trxid+'-last-audit-result', 'json')
    # Below Condition under Transaction Success (025E Must Be Here)
    if (int(last_card_check['balance']) + int(amount) - 1500) == int(last_balance):
        # Force Settlement As Success
        get_force_settlement(amount, trxid, set_status='0000')

    else:
        # Just In Case 025E Not Captured Above
        if last_audit_result.get('err_code').upper() == '025E':
            get_force_settlement(amount, trxid, set_status='0000')
            return
        # New Applet Doing Correction
        # param = QPROX['CORRECTION_C2C'] + '|' + LAST_C2C_APP_TYPE + '|'
        # _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        get_force_settlement(amount, trxid, set_status='FAILED')
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#RC_'+rc)


def topup_bni_correction(amount, trxid=''):
    # Check Correction Result
    reset_card_contactless()
    # Add Check Card Number First Before Correction - Optional
    response, result = _Command.send_request(param=QPROX['BALANCE'] + '|', output=_Command.MO_REPORT)
    LOGGER.debug((response, result))
    # check_card_no = LAST_CARD_CHECK['card_no']
    check_card_no = '0'
    last_balance = '0'
    
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    
    last_audit_result = _Common.load_from_temp_data(trxid+'-last-audit-result', 'json')
    rc = _Common.LAST_READER_ERR_CODE
    # rc = last_audit_result.get('err_code', 'FFFF').upper()
    
    if response == 0 and '|' in result:
        check_card_no = result.split('|')[1].replace('#', '')
        last_balance = result.split('|')[0]
    else:
        LOGGER.warning(('CARD_NO NOT DETECTED', check_card_no, last_card_check['card_no'], trxid, result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BNI_TOPUP_CORRECTION#RC_1024')
        return
    
    if last_card_check['card_no'] != check_card_no:
        LOGGER.warning(('BNI_CARD_MISSMATCH', check_card_no, last_card_check['card_no'], trxid, result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BNI_TOPUP_CORRECTION#RC_'+rc)
        return

    # Below Condition under Transaction Success
    if (int(last_card_check['balance']) + int(amount)) == int(last_balance):
        # Treat As Success BNI Topup TRX. Cannot Generate Settlment Caused By Empty Report
        output = {
            'last_balance': last_balance,
            'report_sam': 'N/A',
            'card_no': check_card_no,
            'report_ka': 'N/A',
            'bank_id': '2',
            'bank_name': 'BNI',
            'prev_balance': last_card_check['balance'],
            'deposit_no': last_audit_result.get('samCardNo'),
            'deposit_prev_balance': last_audit_result.get('samPrevBalance'),
            'deposit_last_balance': last_audit_result.get('samLastBalance'),
            'topup_report': 'N/A',
        }
        LOGGER.info((str(output)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        return
    # Still Negative Condition
    # Get Card Log And Push SAM Audit
    try:
        param = last_audit_result
        if 'topup_result' in param.keys():
            param.pop('topup_result')
        if 'last_result' in param.keys():
            param.pop('last_result')
        # Will Change To Card Purse
        # sam_purse = last_audit_result.get('sam_purse')
        sam_history = last_audit_result.get('sam_history', '')
        card_purse, card_history = bni_card_history_direct(10)
        param['remarks'] = json.dumps({
            'mid': _Common.MID_BNI,
            'tid': _Common.TID_BNI,
            'can': check_card_no,
            # 'csn': card_purse[20:36] if card_purse is not None and len(card_purse) > 36 else '',
            'csn': '',
            'card_history': card_history,
            'amount': amount,
            'sam_history': sam_history,
            # 'sam_purse': sam_purse,
            'card_purse': card_purse,
            'err_code': param.get('err_code'),
        })
        # 00017546050002591031000000006E6E6E626187A02B89245456E2DDF0F451F39310000000000100157C88889999040021343360AD8F15789251010000003360CBBF50555243000000000000C307926DE549686CDE87AC42D7A4027D
        # 'trxid': trxid+'_FAILED',
        # 'samCardNo': _Common.BNI_SAM_1_NO,
        # 'samCardSlot': _Common.BNI_ACTIVE,
        # 'samPrevBalance': deposit_prev_balance,
        # 'samLastBalance': _Common.BNI_ACTIVE_WALLET,
        # 'topupCardNo': last_card_check['card_no'],
        # 'topupPrevBalance': last_card_check['balance'],
        # 'topupLastBalance': last_card_check['balance'],
        # 'status': 'FAILED',
        # 'remarks': {},
        # 'topup_result': json.loads(_result),
        # 'err_code': json.loads(_result),
        LOGGER.info((str(param)))
        _Common.store_upload_sam_audit(param)
    except Exception as e:
        LOGGER.warning((e))
    QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#RC_'+rc)


def start_mandiri_c2c_force_settlement(amount, trxid):
    if not _Common.C2C_MODE:
            return
    else:
        _Helper.get_thread().apply_async(get_force_settlement, (amount, trxid,))


def get_force_settlement(amount, trxid, set_status='FAILED'):
    _param = QPROX['FORCE_SETTLEMENT'] + '|' + LAST_C2C_APP_TYPE + '|'
    _response, _result = _Command.send_request(param=_param, output=_Command.MO_REPORT)
    LOGGER.debug((_param, _response, _result))
    try:
        _result = json.loads(_result)
        rc = _result.get('Result', 'FFFF').upper()
        if _response == 0 and len(_result) >= 196:
            # Update Detail TRX Detail Attribute
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_FORCE_SETTLEMENT')
            parse_c2c_report(report=_result, reff_no=trxid, amount=amount, status=set_status)
        else:
            LOGGER.warning((trxid, _result))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_TOPUP_CORRECTION#FC_'+rc)
    except Exception as e:
        LOGGER.warning((trxid, _result, e))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_TOPUP_CORRECTION#EXCP')
        
        
def get_force_settlement_bni(card_purse=None):
    old_card_purse = LAST_BNI_CARD_PURSE
    if old_card_purse is False:
        LOGGER.warning(('LAST_BNI_CARD_PURSE is Empty', LAST_BNI_CARD_PURSE))
        return ''
    if card_purse is None or card_purse == '' or len(card_purse) != len(old_card_purse):
        LOGGER.warning(('NEW BNI_CARD_PURSE is Not Valid/Empty', card_purse))
        return ''
    old_sam_purse = LAST_BNI_SAM_PURSE
    if old_sam_purse is False:
        LOGGER.warning(('LAST_BNI_SAM_PURSE is Empty', LAST_BNI_SAM_PURSE))
        return ''
    return build_bni_force_settlement(old_card_purse, card_purse, old_sam_purse)


def build_bni_force_settlement(old_card_purse, new_card_purse, old_sam_purse):
    new_sam_purse = get_card_info(_Common.BNI_ACTIVE, 'BNI_SAM_RAW_PURSE')
    if new_sam_purse is False or len(new_sam_purse) < 1:
        LOGGER.warning(('NEW BNI_SAM_PURSE is Empty', new_sam_purse))
        return ''
    last_topup_rc = LAST_BNI_TOPUP_RC
    # TODO: Finalise This With Actual BNI Format
    return ''.join([
        'D',
        old_card_purse,
        new_card_purse,
        old_sam_purse,
        new_sam_purse,
        last_topup_rc
    ])


def get_last_error_report_bni():
    global LAST_BNI_ERROR_REPORT

    last_error_report_bni = LAST_BNI_ERROR_REPORT
    LAST_BNI_ERROR_REPORT = ''
    return last_error_report_bni


# Check Deposit Balance If Failed, When Deducted Hit Correction, If Correction Failed, Hit FOrce Settlement And Store
def topup_offline_mandiri_c2c(amount, trxid='', slot=None):
    global LAST_C2C_APP_TYPE
    
    # New Topup Procedure Validation
    validate_rules, error = _Common.check_topup_procedure('mandiri', trxid, amount)
    if not validate_rules:
        LOGGER.warning(('mandiri', amount, trxid, error))
        return
    
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    validate_card = revalidate_card(last_card_check['card_no'])
    if not validate_card:
        return
    
    if last_card_check['card_no'] in _Common.MANDIRI_CARD_BLOCKED_LIST:
        LOGGER.warning(('Card No: ', last_card_check['card_no'], 'Found in Mandiri Card Blocked Data'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_BLOCKED')
        return
    
    mdr_c2c_balance_info()
    prev_deposit_balance = _Common.MANDIRI_ACTIVE_WALLET
    LOGGER.info(('MDR PREV_BALANCE_DEPOSIT', prev_deposit_balance ))
    
    # Deposit Balance Validation
    if int(prev_deposit_balance) < int(_Common.C2C_THRESHOLD) or int(prev_deposit_balance) < int(amount):
        LOGGER.warning(('Deposit Balance: ', prev_deposit_balance, amount, _Common.C2C_THRESHOLD ))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#INSUFFICIENT_DEPOSIT')
        return
    
    param = QPROX['TOPUP_C2C'] + '|' + str(amount) #Amount Must Be Full Denom
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    LOGGER.info((_response, _result))
    # {"Result":"0000","Command":"026","Parameter":"2000","Response":"|6308603298180000003600030D706E8693EA7B051040100120D0070000384A0000050520120439FF0E00004D0F03DC0500000768C7603298602554826300020D706E8693EA7B510401880110F4010000CE4A0000050520120439FF0E0000020103E7F2E790A","ErrorDesc":"Sukses"}
    
    # {"Command": "028", "ErrorDesc": "Gagal", "Result": "0290", "Response": "", "Parameter": "0"}
    if _response == 0 and len(_result) >= 196:
        c2c_report = _result
        _Common.LAST_TOPUP_TRXID = trxid
        parse_c2c_report(report=c2c_report, reff_no=trxid, amount=amount)
        return
    
    # Error Condition/ Failure Transaction Below
    try:
        # Call Reader Dump
        if 'topup_mandiri' in _Common.SELECTED_DEBUG_MODE:
            do_get_reader_dump(str(last_card_check['card_no']), trxid)
        # param = QPROX['READER_DUMP'] + '|' + str(last_card_check['card_no']) + '|'  + trxid
        # dump_response, dump_result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        # LOGGER.info((dump_response, dump_result))
                
        # Parse Previous Error Result
        topup_result = json.loads(_result)
        
        LAST_C2C_APP_TYPE = '0'
        if topup_result["Response"] == '83' or topup_result["Result"] in ["6208"]:
            LAST_C2C_APP_TYPE = '1'
        
        # LOGGER.warning(('MDR C2C FAILED', 'trxid:', trxid, 'result:', topup_result, 'applet_type:', LAST_C2C_APP_TYPE ))
        # validate if deposit balance is deducted
        sleep(1)
        mdr_c2c_balance_info()
        last_deposit_balance = _Common.MANDIRI_ACTIVE_WALLET
        LOGGER.info(('MDR LAST_BALANCE_DEPOSIT', last_deposit_balance ))
        
        rc = topup_result.get("Result", 'FFFF').upper()
        
        if prev_deposit_balance == last_deposit_balance:
            LOGGER.debug(('MDR DEPOSIT_NOT_DEDUCTED', trxid, amount, last_card_check['card_no']))
            # New Handling TO Retry Topup Process
            if trxid != _Common.LAST_TOPUP_TRXID:
                _Common.LAST_TOPUP_TRXID = trxid
                LOGGER.debug(('MDR TRIGGER RETRY TOPUP', trxid, amount, _Common.LAST_TOPUP_TRXID))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('RETRY_TOPUP_PREPAID')
                return
            
            # Still Needed ?
            # Keep Trigger Force Settlement For New Applet When Deposit Balance Not Deducted
            if topup_result["Result"] in ["6208"]:
                LAST_C2C_APP_TYPE == '1'
                get_force_settlement(amount, trxid, 'FAILED')
                sleep(1)
            
            # Set To Old Handler Conditionally
            if not _Common.NEW_TOPUP_FAILURE_HANDLER:
                _Common.LAST_TOPUP_TRXID = trxid
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#RC_'+rc)
                return
        
        _Common.LAST_TOPUP_TRXID = trxid
        LOGGER.debug(('MDR DEPOSIT_DEDUCTED', trxid, amount))
        topup_audit_status = 'FORCE_SETTLEMENT' if str(prev_deposit_balance) != str(_Common.MANDIRI_ACTIVE_WALLET) else 'FAILED'
        trx_partial_status = ['101C', '100C']
        
        if rc in trx_partial_status:
            if rc == '100C': 
                # New Applet (100C Without Report)
                LAST_C2C_APP_TYPE = '1'
            # Old Applet Will Captured Here (101C)
            # In new Reader FW will have force_settlement report
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('RETAP_CARD')
            reset_card_contactless()
            last_deposit_balance = _Common.MANDIRI_ACTIVE_WALLET
            LOGGER.info(('MDR RECHECK PREV_BALANCE_DEPOSIT '+rc, prev_deposit_balance ))
            LOGGER.info(('MDR RECHECK LAST_BALANCE_DEPOSIT '+rc, last_deposit_balance ))     
            topup_audit_status = 'PARTIAL_FAILURE'
        
        last_audit_report = json.dumps({
                'trxid': trxid + '_FAILED',
                'samCardNo': _Common.MANDIRI_SAM_NO_1,
                'samCardSlot': _Common.MANDIRI_ACTIVE,
                'samPrevBalance': prev_deposit_balance,
                'samLastBalance': _Common.MANDIRI_ACTIVE_WALLET,
                'topupCardNo': last_card_check['card_no'],
                'topupPrevBalance': last_card_check['balance'],
                'topupLastBalance': last_card_check['balance'],
                'status': topup_audit_status,
                'remarks': {
                    'mid': _Common.C2C_MID,
                    'tid': _Common.C2C_TID
                    },
                'last_result': topup_result,
                'err_report': topup_result.get('Response'),
                'err_code': topup_result.get('Result'),
                # 'sam_purse': bni_sam_raw_purse,
                # 'sam_history': bni_sam_history_direct()
        })
        _Common.store_to_temp_data(trxid+'-last-audit-result', last_audit_report)
        # New Topup Failure Handler
        if _Common.NEW_TOPUP_FAILURE_HANDLER:
            new_topup_failure_handler('MANDIRI', trxid, amount)
        # Old Handler
        else:
        # "6987", "100C", "10FC" Another Captured Error Code
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_TOPUP_CORRECTION#RC_'+rc)
    except Exception as e:
        LOGGER.warning((e))
        last_audit_report = json.dumps({
                'trxid': trxid + '_FAILED',
                'samCardNo': _Common.MANDIRI_SAM_NO_1,
                'samCardSlot': _Common.MANDIRI_ACTIVE,
                'samPrevBalance': prev_deposit_balance,
                'samLastBalance': _Common.MANDIRI_ACTIVE_WALLET,
                'topupCardNo': last_card_check['card_no'],
                'topupPrevBalance': last_card_check['balance'],
                'topupLastBalance': last_card_check['balance'],
                'status': 'FAILED',
                'remarks': {
                    'mid': _Common.C2C_MID,
                    'tid': _Common.C2C_TID
                    },
                'last_result': topup_result,
                'err_code': topup_result.get('Result'),
                # 'sam_purse': bni_sam_raw_purse,
                # 'sam_history': bni_sam_history_direct()
        })
        _Common.store_to_temp_data(trxid+'-last-audit-result', last_audit_report)
        if _Common.NEW_TOPUP_FAILURE_HANDLER:
            new_topup_failure_handler('MANDIRI', trxid, amount)
        # Old Handler
        else:
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MDR_TOPUP_CORRECTION#EXCP')


def topup_offline_mandiri(amount, trxid='', slot=None):
    global INIT_MANDIRI
    if len(INIT_LIST) == 0:
        LOGGER.warning(('INIT_LIST', str(INIT_LIST)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#BANK_NOT_INIT')
        _Common.NFC_ERROR = 'EMPTY_INIT_LIST'
        return
    if slot is None:
        slot = str(_Common.MANDIRI_ACTIVE)
    param = QPROX['TOPUP'] + '|' + str(amount)
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    
    if _response == 0 and '|' in _result:
        __data = _result.split('|')
        __status = __data[0]
        __remarks = ''
        if __status == '0000':
            __remarks = __data[5]
        if __status == '6969':
            LOGGER.warning(('TOPUP_FAILED_CARD_NOT_MATCH', last_card_check))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_FAILED_CARD_NOT_MATCH')
            return
        if __status == '6984':
            LOGGER.warning(('MANDIRI_SAM_BALANCE_EXPIRED', _result))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('MANDIRI_SAM_BALANCE_EXPIRED')
            # INIT_MANDIRI = False
            _Common.MANDIRI_ACTIVE_WALLET = 0
            return
        if __status in ['6982', '1001']:
            LOGGER.warning(('TOPUP_FAILED_KA_NOT_LOGIN', _result))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_FAILED_KA_NOT_LOGIN')
            INIT_MANDIRI = False
            _Common.MANDIRI_ACTIVE_WALLET = 0
            return
        if __status in ERROR_TOPUP.keys():
            __remarks += '|'+ERROR_TOPUP[__status]
        __deposit_last_balance = __data[3].lstrip('0')
        __report_sam = __data[5]
        output = {
            'last_balance': __data[8].lstrip('0'),
            'report_sam': __report_sam.split('#')[0],
            'card_no': __data[6],
            'report_ka': __report_sam.split('#')[1],
            'bank_id': '1',
            'bank_name': 'MANDIRI',
        }
        # Update Local Mandiri Wallet
        if slot == '1':
            _Common.MANDIRI_WALLET_1 = _Common.MANDIRI_WALLET_1 - int(amount)
            _Common.MANDIRI_ACTIVE_WALLET = _Common.MANDIRI_WALLET_1
        if slot == '2':
            _Common.MANDIRI_WALLET_2 = _Common.MANDIRI_WALLET_2 - int(amount)
            _Common.MANDIRI_ACTIVE_WALLET = _Common.MANDIRI_WALLET_2
        LOGGER.info((slot, __status, str(output), _result))
        if __status == '0000':
            # Store Topup Success Record Into Local DB
            _Common.local_store_topup_record(output)
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit(__status+'|'+json.dumps(output))
        __card_uid = __report_sam.split('#')[1][:14]
        param = {
            'trxid': trxid,
            'samCardNo': __card_uid,
            'samCardSlot': slot,
            'samPrevBalance': __data[2].lstrip('0'),
            'samLastBalance': __deposit_last_balance,
            'topupCardNo': __data[6],
            'topupPrevBalance': __data[7].lstrip('0'),
            'topupLastBalance': __data[8].lstrip('0'),
            'status': __status,
            'remarks': __remarks,            
        }
        _Common.set_mandiri_uid(slot, __card_uid)
        _Common.store_upload_sam_audit(param)
        # Update to server
        # Disabled = 2022-12-27
        # _Common.upload_mandiri_wallet()
    else:
        rc = _Common.LAST_READER_ERR_CODE
        LOGGER.warning((slot, _result))
        _Common.NFC_ERROR = 'TOPUP_MANDIRI_ERROR'
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#RC_'+rc)


def start_topup_offline_bni(amount, trxid):
    # get_bni_wallet_status()
    _Helper.get_thread().apply_async(topup_offline_bni, (amount, trxid,))


def get_bni_wallet_status(upload=True):
    global BNI_DEPOSIT_BALANCE
    try:
        # First Attempt For SLOT 1
        attempt = 0
        while True:
            attempt += 1
            get_card_info(slot=1)
            sleep(1)
            bni_c2c_balance_info(slot=1)
            if attempt == 3 or _Common.BNI_SAM_1_WALLET != 0:
                break
            sleep(1)
        # Second Attempt For SLOT 2
        _attempt = 0
        while True:
            _attempt += 1
            get_card_info(slot=2)
            sleep(1)
            bni_c2c_balance_info(slot=2)
            if _attempt == 3 or _Common.BNI_SAM_2_WALLET != 0:
                break
            sleep(1)
        if _Common.BNI_ACTIVE == 1:
            _Common.BNI_ACTIVE_WALLET = _Common.BNI_SAM_1_WALLET
            # BNI_DEPOSIT_BALANCE = _Common.BNI_SAM_1_WALLET
            LOGGER.info((str(_Common.BNI_ACTIVE), str(_Common.BNI_SAM_1_WALLET)))
        if _Common.BNI_ACTIVE == 2:
            _Common.BNI_ACTIVE_WALLET = _Common.BNI_SAM_2_WALLET
            # BNI_DEPOSIT_BALANCE = _Common.BNI_SAM_2_WALLET
            LOGGER.info((str(_Common.BNI_ACTIVE), str(_Common.BNI_SAM_2_WALLET)))
        if upload is True:
            # Do Upload To Server
            _Common.upload_bni_wallet()
    except Exception as e:
        LOGGER.warning((str(e)))


def update_bni_wallet(slot, amount, last_balance=None):
    if slot == 1:
        if last_balance is None:
            _Common.BNI_SAM_1_WALLET = _Common.BNI_SAM_1_WALLET - int(amount)
        else:
            _Common.BNI_SAM_1_WALLET = int(last_balance)
        _Common.BNI_ACTIVE_WALLET = _Common.BNI_SAM_1_WALLET
    if slot == 2:
        if last_balance is None:
            _Common.BNI_SAM_2_WALLET = _Common.BNI_SAM_2_WALLET - int(amount)
        else:
            _Common.BNI_SAM_2_WALLET = int(last_balance)
        _Common.BNI_ACTIVE_WALLET = _Common.BNI_SAM_2_WALLET
    _Common.upload_bni_wallet()


def start_fake_update_dki(card_no, amount):
    bank = 'DKI'
    _Helper.get_thread().apply_async(fake_update_balance, (bank, card_no, amount,))


def start_topup_dki_by_service(amount, trxid):
    _Helper.get_thread().apply_async(topup_dki_by_service, (amount, trxid,))

# "TOPUP_ONLINE_DKI": "043", #"Send amount|TID|STAN|MID|InoviceNO|ReffNO "


def get_set_dki_stan():
    dki_stan = _ConfigParser.get_value('TEMPORARY', 'dki^last^topup^stan')
    _Common.LAST_DKI_STAN = dki_stan
    _Common.log_to_config('TEMPORARY', 'dki^last^topup^stan', str(int(dki_stan)+1))
    return dki_stan


def get_set_dki_invoice():
    dki_invoice = _ConfigParser.get_value('TEMPORARY', 'dki^last^topup^invoice')
    _Common.LAST_DKI_INVOICE_NO = dki_invoice
    _Common.log_to_config('TEMPORARY', 'dki^last^topup^invoice', str(int(dki_invoice)+1))
    return dki_invoice


# {
# "Result":"0000",
# "Command":"043",
# "Parameter":"80|91009003|000120|000080080088881|000060|200505191908",
# "Response":"9360885090123100|80|93800",
# "ErrorDesc":"Sukses"
# }


def start_init_config_bca():
    _Helper.get_thread().apply_async(init_config_bca)


def init_config_bca():
    # if '---' in _Common.MID_TOPUP_BCA or '---' in _Common.TID_TOPUP_BCA:
    #     LOGGER.warning(('BCA Topup Config Init Failed, Wrong TID/MID Topup', _Common.MID_TOPUP_BCA, _Common.TID_TOPUP_BCA))
    #     return
    if not _Common.bca_topup_online_validation():
        LOGGER.warning(('BCA Topup Config Init Failed, Wrong TID/MID Topup', '885'+_Common.MID_TOPUP_BCA, _Common.TID_TOPUP_BCA))
        return
    param = QPROX['CONFIG_ONLINE_BCA'] + '|' + _Common.TID_TOPUP_BCA + '|' + _Common.MID_TOPUP_BCA + '|'
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((param, result, response))
    if response == 0:
        _Common.BCA_TOPUP_ONLINE = True
        LOGGER.info(('BCA_TOPUP_ONLINE', _Common.BCA_TOPUP_ONLINE))
    else:
        _Common.NFC_ERROR = 'INIT_CONFIG_BCA_TOPUP_ERROR'
        _Common.BCA_TOPUP_ONLINE = False
        LOGGER.warning(('BCA_TOPUP_ONLINE', _Common.BCA_TOPUP_ONLINE))


def topup_dki_by_service(amount, trxid):
    dki_stan = get_set_dki_stan()
    dki_invoice = get_set_dki_invoice()
    param = '|'.join([QPROX['TOPUP_ONLINE_DKI'], str(amount), _Common.TID_TOPUP_ONLINE_DKI, dki_stan.zfill(6), 
            _Common.MID_TOPUP_ONLINE_DKI, dki_invoice.zfill(6), trxid])
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    if _response == 0 and ('|'+str(amount)+'|') in _result:
        _data = _result.split('|')
        output = {
                    'last_balance': _data[2],
                    'topup_amount': _data[1],
                    'report_sam': 'N/A',
                    'card_no': _data[0],
                    'report_ka': 'N/A',
                    'bank_id': '5',
                    'bank_name': 'DKI',
            }
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        return True
    else:
        _result = json.loads(_result)
        rc = _result.get('Result', 'FFFF')
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('DKI_TOPUP_CORRECTION#RC_'+rc)
        return False
        

def reversal_topup_dki_by_service(amount, trxid):
    dki_stan = _Common.LAST_DKI_STAN
    dki_invoice = _Common.LAST_DKI_INVOICE_NO
    param = '|'.join([QPROX['REVERSAL_ONLINE_DKI'], str(amount), _Common.TID_TOPUP_ONLINE_DKI, dki_stan.zfill(6), 
            _Common.MID_TOPUP_ONLINE_DKI, dki_invoice.zfill(6), trxid])
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    if _response == 0:
        return True
    else:
        return False


def fake_update_balance(bank, card_no, amount):
    if bank == 'DKI':
        sleep(2)
        prev_balance = _ConfigParser.get_value('TEMPORARY', card_no)
        last_balance = int(prev_balance) + int(amount)
        output = {
            'last_balance': str(last_balance),
            'report_sam': 'DUMMY-'+card_no+'-'+amount+'-'+str(_Helper.now()),
            'card_no': card_no,
            'report_ka': 'N/A',
            'bank_id': '4',
            'bank_name': 'DKI',
            }
        _Common.log_to_temp_config(card_no, last_balance)
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
    else:
        return


def start_topup_offline_bni_with_attempt(amount, trxid, attempt):
    slot = None
    _Helper.get_thread().apply_async(topup_offline_bni, (amount, trxid, slot, attempt,))


LAST_BNI_CARD_PURSE = False
LAST_BNI_SAM_PURSE = False
LAST_BNI_TOPUP_RC = ''
LAST_BNI_ERROR_REPORT = ''

def topup_offline_bni(amount, trxid, slot=None, attempt=None):
    global LAST_BNI_CARD_PURSE, LAST_BNI_SAM_PURSE, LAST_BNI_TOPUP_RC, LAST_BNI_ERROR_REPORT
    
    # New Topup Procedure Validation
    validate_rules, error = _Common.check_topup_procedure('bni', trxid, amount)
    if not validate_rules:
        LOGGER.warning(('bni', amount, trxid, error))
        return
    
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    validate_card = revalidate_card(last_card_check['card_no'])
    if not validate_card:
        return
    
    _slot = 1
    if slot is None:
        slot = _Common.BNI_ACTIVE
        _slot = _Common.BNI_ACTIVE - 1
    if attempt == '5':
        LOGGER.debug(('TOPUP_ATTEMPT_REACHED', str(int(attempt) - 1)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ATTEMPT_REACHED')
        return
    
    # Disabled : Cmd Migrated From Reader FW
    # Add BNI Card Purse
    # LAST_BNI_CARD_PURSE = get_card_info_tapcash('MODE_F9')
    # if not LAST_BNI_CARD_PURSE:
    #     QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_PURSE_FAILED')
    #     return
    
    bni_c2c_balance_info(_Common.BNI_ACTIVE)
    deposit_prev_balance = _Common.BNI_ACTIVE_WALLET

    # Deposit Balance Validation
    if int(deposit_prev_balance) < int(_Common.BNI_THRESHOLD) or int(deposit_prev_balance) < int(amount):
        LOGGER.warning(('Deposit Balance: ', deposit_prev_balance, amount, _Common.BNI_THRESHOLD ))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#INSUFFICIENT_DEPOSIT')
        return
    
    param = QPROX['INIT_SAM_BNI'] + '|' + str(_slot) + '|' + TID_BNI
    response, bni_sam_raw_purse = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((amount, trxid, slot, bni_sam_raw_purse))
    LOGGER.info(('BNI PREV_BALANCE_DEPOSIT', deposit_prev_balance ))
    
    # Reset Previous Topup RC
    LAST_BNI_TOPUP_RC = ''
    LAST_BNI_ERROR_REPORT = ''
    topup_result = ''

    if response == 0:
        LAST_BNI_SAM_PURSE = bni_sam_raw_purse
        _param = QPROX['TOPUP_BNI'] + '|' + str(amount) + '|' + str(_slot)
        _response, _result = _Command.send_request(param=_param, output=_Command.MO_REPORT, wait_for=2)
        LOGGER.debug((amount, trxid, slot, _result))
        topup_result = _result
        
        # Override status FFEE (Failure Topup BNI, But Have NOK Report)
        if _response == -1 and 'FFEE' in _result:
            _response = 0
            _result = json.loads(_result).get('Response')
            
        remarks = ''
        report_sam = ''
        if _response == 0 and '|' in _result:
            _result = _result.replace('#', '')
            data = _result.split('|')
            
            # 0000 : Success, Others Failed
            status = data[0]
            LAST_BNI_TOPUP_RC = status
            
            report_sam = data[5]
            card_prev_balance = data[7].lstrip('0')
            card_last_balance = data[8].lstrip('0')
            card_no = data[6]
                        
            output = {
                'last_balance': card_last_balance,
                'report_sam': report_sam,
                'card_no': card_no,
                'report_ka': 'N/A',
                'bank_id': '2',
                'bank_name': 'BNI',
            }
            # Disabled - 2022-12-27
            # update_bni_wallet(slot, amount, deposit_last_balance)
            # Logic IF Only Success
            if status == '0000':
                deposit_last_balance = str(int(report_sam[58:64], 16)) if len(report_sam) > 64 else ''
                _Common.BNI_ACTIVE_WALLET = int(report_sam[58:64], 16) if len(report_sam) > 64 else _Common.BNI_ACTIVE_WALLET
                
                # Set Deposit Based on Slot
                if _slot == 0: _Common.BNI_SAM_1_WALLET = _Common.BNI_ACTIVE_WALLET
                if _slot == 1: _Common.BNI_SAM_2_WALLET = _Common.BNI_ACTIVE_WALLET
                
                remarks = data[5]
                deposit_no = _Common.BNI_SAM_1_NO
                # Store Topup Success Record Into Local DB
                _Common.local_store_topup_record(output)
                output['prev_balance'] = card_prev_balance
                output['deposit_no'] = deposit_no
                output['deposit_prev_balance'] = deposit_prev_balance
                output['deposit_last_balance'] = deposit_last_balance
                output['topup_report'] = report_sam
                LOGGER.info((str(output)))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit(status+'|'+json.dumps(output))
                param = {
                    'trxid': trxid,
                    'samCardNo': deposit_no,
                    'samCardSlot': slot,
                    'samPrevBalance': deposit_prev_balance,
                    'samLastBalance': deposit_last_balance,
                    'topupCardNo': card_no,
                    'topupPrevBalance': card_prev_balance,
                    'topupLastBalance': card_last_balance,
                    'status': status,
                    'remarks': remarks,
                }
                _Common.store_upload_sam_audit(param)
                _Common.LAST_TOPUP_TRXID = trxid
                # Return Success Condition Here
                return
            elif status == 'FFEE':
                if len(report_sam) >= 266:
                    force_settlement = {
                        'last_balance': last_card_check['balance'],
                        'report_sam': report_sam,
                        'card_no': last_card_check['card_no'],
                        'report_ka': 'NOK',
                        'bank_id': '2',
                        'bank_name': 'BNI',
                    }
                    _Common.local_store_topup_record(force_settlement)
        # False Condition
        
        # Call Reader Dump
        if 'topup_bni' in _Common.SELECTED_DEBUG_MODE:
            do_get_reader_dump(str(last_card_check['card_no']), trxid)
        # param = QPROX['READER_DUMP'] + '|' + str(last_card_check['card_no']) + '|'  + trxid
        # dump_response, dump_result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        # LOGGER.info((dump_response, dump_result))
        
        bni_c2c_balance_info(_Common.BNI_ACTIVE)
        LOGGER.info(('BNI LAST_BALANCE_DEPOSIT', _Common.BNI_ACTIVE_WALLET ))

        topup_result = json.loads(topup_result)
        rc = topup_result.get('Result', 'FFFF')
        
        if int(deposit_prev_balance) == int(_Common.BNI_ACTIVE_WALLET):
            LOGGER.debug(('BNI DEPOSIT_NOT_DEDUCTED', trxid, amount, last_card_check['card_no']))
            # New Handling TO Retry Topup Process
            if trxid != _Common.LAST_TOPUP_TRXID:
                _Common.LAST_TOPUP_TRXID = trxid
                LOGGER.debug(('BNI TRIGGER RETRY TOPUP', trxid, amount, _Common.LAST_TOPUP_TRXID))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('RETRY_TOPUP_PREPAID')
                return
            # Set To Old Handler Conditionally
            if not _Common.NEW_TOPUP_FAILURE_HANDLER:
                _Common.LAST_TOPUP_TRXID = trxid
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#RC_'+rc)
                return
        else:
            LOGGER.debug(('BNI DEPOSIT_DEDUCTED', trxid, amount))
        
        # Wether Error or Success, If Deposit Already Deduct Must Have Report NOK Here
        LAST_BNI_ERROR_REPORT = report_sam
        LOGGER.info(('BNI LAST_ERROR_REPORT', LAST_BNI_ERROR_REPORT))
        
        _Common.LAST_TOPUP_TRXID = trxid
        
        # Real False Condition
        last_audit_report = json.dumps({
                    'trxid': trxid + '_FAILED',
                    'samCardNo': _Common.BNI_SAM_1_NO,
                    'samCardSlot': _Common.BNI_ACTIVE,
                    'samPrevBalance': deposit_prev_balance,
                    'samLastBalance': _Common.BNI_ACTIVE_WALLET,
                    'topupCardNo': last_card_check['card_no'],
                    'topupPrevBalance': last_card_check['balance'],
                    'topupLastBalance': last_card_check['balance'],
                    'status': 'FORCE_SETTLEMENT' if str(deposit_prev_balance) != str(_Common.BNI_ACTIVE_WALLET) else 'FAILED',
                    'remarks': {
                        'tid': _Common.TID_BNI,
                        'mid': _Common.MID_BNI
                        },
                    'last_result': topup_result,
                    'err_code': topup_result.get('Result'),
                    'err_report': report_sam,
                    # 'sam_purse': bni_sam_raw_purse,
                    # 'sam_history': bni_sam_history_direct()
            })
        _Common.store_to_temp_data(trxid+'-last-audit-result', last_audit_report)

        # New Handler
        if _Common.NEW_TOPUP_FAILURE_HANDLER:
            new_topup_failure_handler('BNI', trxid, amount)
        # Old Handler
        else:
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BNI_TOPUP_CORRECTION#RC_'+rc)
    else:
        LAST_BNI_SAM_PURSE = False
        LOGGER.warning(('INIT_SAM_BNI', bni_sam_raw_purse))
        init_topup_result = json.loads(bni_sam_raw_purse)
        rc = init_topup_result.get('Result', 'FFFF')
        if _Common.NEW_TOPUP_FAILURE_HANDLER:
            new_topup_failure_handler('BNI', trxid, amount)
        # Old Handler
        else:
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#RC_'+rc)
            _Common.NFC_ERROR = 'TOPUP_BNI_ERROR'


def start_ka_info():
    _Helper.get_thread().apply_async(ka_info_mandiri)


MANDIRI_DEPOSIT_BALANCE = 0


def mdr_c2c_balance_info():
    try:
        param = QPROX['BALANCE_C2C'] + '|'
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        if response == 0 and '|' in result:
            # 24000|CF8703D6|603298180000003627070120138508320065030106000000000003DB727BDF078EEDD1518ABD6FC1A678B42C4346DA84117374E4C96A17022003224070FFFF
            res = result.split('|')
            MANDIRI_DEPOSIT_BALANCE = int(res[0])
            _Common.C2C_DEPOSIT_UID = res[1]
            _Common.log_to_temp_config('c2c^card^uid', res[1])
            _Common.C2C_DEPOSIT_NO = res[2][:16]
            _Common.MANDIRI_SAM_NO_1 = _Common.C2C_DEPOSIT_NO
            _Common.MANDIRI_ACTIVE_WALLET = MANDIRI_DEPOSIT_BALANCE
            _Common.MANDIRI_WALLET_1 = MANDIRI_DEPOSIT_BALANCE
            _Common.MANDIRI_ACTIVE = 1
            _DAO.create_today_report(_Common.TID)
            _DAO.update_today_summary_multikeys(['mandiri_deposit_last_balance'], int(_Common.MANDIRI_ACTIVE_WALLET))
            QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('C2C_BALANCE_INFO|' + str(result))
        else:
            _Common.C2C_DEPOSIT_UID = 'N/A'
            _Common.C2C_DEPOSIT_NO = ''
            _Common.MANDIRI_SAM_NO_1 = ''
            _Common.MANDIRI_ACTIVE_WALLET = -1
            _Common.MANDIRI_WALLET_1 = -1
            _Common.NFC_ERROR = 'C2C_BALANCE_INFO_MANDIRI_ERROR'
            #_Common.online_logger(['C2C INFO ERROR MANDIRI', result], 'device')
            QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('C2C_BALANCE_INFO|ERROR')
    except Exception as e:
        LOGGER.warning((e))
    finally:
        LOGGER.info((_Common.MANDIRI_ACTIVE_WALLET))


def ka_info_mandiri(slot=None, caller=''):
    global MANDIRI_DEPOSIT_BALANCE
    if _Common.C2C_MODE is True:
        mdr_c2c_balance_info()
        return
    if slot is None:
        slot = str(_Common.MANDIRI_ACTIVE)
    param = QPROX['KA_INFO'] + '|' + slot + '|'
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    LOGGER.debug((caller, slot, result))
    if response == 0 and result is not None:
        MANDIRI_DEPOSIT_BALANCE = int(result.split('|')[0])
        _Common.MANDIRI_ACTIVE_WALLET = MANDIRI_DEPOSIT_BALANCE
        if slot == '1':
            _Common.MANDIRI_WALLET_1 = MANDIRI_DEPOSIT_BALANCE
            _Common.MANDIRI_ACTIVE = 1
        elif slot == '2':
            _Common.MANDIRI_WALLET_2 = MANDIRI_DEPOSIT_BALANCE
            _Common.MANDIRI_ACTIVE = 2
        _Common.save_sam_config(bank='MANDIRI')
        _DAO.create_today_report(_Common.TID)
        _DAO.update_today_summary_multikeys(['mandiri_deposit_last_balance'], int(_Common.MANDIRI_ACTIVE_WALLET))
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|' + str(result))
    else:
        _Common.NFC_ERROR = 'KA_INFO_MANDIRI_ERROR'
        #_Common.online_logger(['KA INFO ERROR MANDIRI', result, slot], 'device')
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|ERROR')


BNI_DEPOSIT_BALANCE = 0


def bni_c2c_balance_info(slot=1):
    global BNI_DEPOSIT_BALANCE
    # Slot defined as sequence
    try:
        _slot = slot - 1
        param = QPROX['KA_INFO_BNI'] + '|' + str(_slot)
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
        LOGGER.debug((str(slot), result))
        if response == 0 and (result is not None and result != ''):
            BNI_DEPOSIT_BALANCE = int(result.split('|')[0])
            _Common.BNI_ACTIVE_WALLET = BNI_DEPOSIT_BALANCE
            if slot == 1:
                _Common.BNI_SAM_1_WALLET = BNI_DEPOSIT_BALANCE
            if slot == 2:
                _Common.BNI_SAM_2_WALLET = BNI_DEPOSIT_BALANCE
            _DAO.create_today_report(_Common.TID)
            _DAO.update_today_summary_multikeys(['bni_deposit_last_balance'], int(_Common.BNI_ACTIVE_WALLET))
            QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|' + str(result))
        else:
            if slot == 1:
                _Common.BNI_SAM_1_WALLET = -1
                _Common.BNI_ACTIVE_WALLET = -1
            if slot == 2:
                _Common.BNI_SAM_2_WALLET = -1
                _Common.BNI_ACTIVE_WALLET = -1
            _Common.NFC_ERROR = 'KA_INFO_BNI_ERROR'
            # #_Common.online_logger(['KA INFO ERROR BNI', result, slot], 'device')
            QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|ERROR')
    except Exception as e:
        LOGGER.warning((e))
    finally:
        LOGGER.info((_Common.BNI_ACTIVE_WALLET))


def start_create_online_info_mandiri():
    _Helper.get_thread().apply_async(create_online_info_mandiri)


PREV_RQ1_DATA = None
PREV_RQ1_SLOT = None


def create_online_info_mandiri(slot=None):
    global PREV_RQ1_DATA, PREV_RQ1_SLOT
    if slot is None:
        slot = str(_Common.MANDIRI_ACTIVE)
    param = QPROX['CREATE_ONLINE_INFO'] + '|' + slot + '|'
    if _Common.MANDIRI_ACTIVE_WALLET > 0:
        _Common.MANDIRI_ACTIVE_WALLET = 0  
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((slot, result))
    if response == 0 and len(result) > 3:
        PREV_RQ1_DATA = str(result)
        PREV_RQ1_SLOT = str(_Common.MANDIRI_ACTIVE)
        # Also Re-write last^auth (MANDIRI_KA_LOGIN state in temp config)
        _Common.log_to_temp_config(section='last^auth')
        # QP_SIGNDLER.SIGNAL_ONLINE_INFO_QPROX.emit('CREATE_ONLINE_INFO|' + str(result))
        return PREV_RQ1_DATA
    else:
        _Common.NFC_ERROR = 'CREATE_ONLINE_INFO_ERROR'
        # QP_SIGNDLER.SIGNAL_ONLINE_INFO_QPROX.emit('CREATE_ONLINE_INFO|ERROR')
        return False


def start_init_online_mandiri():
    _Helper.get_thread().apply_async(init_online_mandiri)


def init_online_mandiri(rsp=None, slot=None):
    if rsp is None:
        LOGGER.warning(("[FAILED]", rsp, slot))
        return
    param = QPROX['INIT_ONLINE'] + '|' + slot + '|' + rsp + '|'
    response, result = _Command.send_request(param=param, output=None)
    LOGGER.debug((rsp, slot, result, response))
    if response == 0 and result is not None:
        ka_info_mandiri(slot=slot, caller='UPDATE_SALDO_KA')
        QP_SIGNDLER.SIGNAL_INIT_ONLINE_QPROX.emit('INIT_ONLINE|SUCCESS')
        _Common.log_to_temp_config(section='last^update')
        QP_SIGNDLER.SIGNAL_INIT_ONLINE_QPROX.emit('MANDIRI_SETTLEMENT|SUCCESS')
        return True
    else:
        _Common.NFC_ERROR = 'INIT_ONLINE_ERROR'
        QP_SIGNDLER.SIGNAL_INIT_ONLINE_QPROX.emit('INIT_ONLINE|ERROR')
        return False


def do_update_limit_mandiri(rsp):
    attempt = 0
    _url = 'http://'+_Common.SFTP_MANDIRI['host']+'/bridge-service/filecheck.php?content=1&no_correction=1'
    _param = {
        'ext': '.RSP',
        'file_path': _Common.SFTP_MANDIRI['path']+'/UpdateRequestDownload_DEV/'+rsp
    }
    if '_DEV' in _param['file_path']:
        if _Common.LIVE_MODE is True or _Common.TEST_MODE is True:
            _param['file_path'] = _param['file_path'].replace('_DEV', '')
    while True:
        attempt += 1
        _stat, _res = _HTTPAccess.post_to_url(_url, _param)
        LOGGER.debug((attempt, rsp, _stat, _res))
        if _stat == 200 and _res['status'] == 0 and _res['file'] is True:
            __content_rq1 = _res['content'].split('#')[0]
            if PREV_RQ1_DATA == __content_rq1:
                __content_rsp = _res['content'].split('#')[1]
                init_online_mandiri(__content_rsp, PREV_RQ1_SLOT)
                LOGGER.info(('RQ1 MATCH', PREV_RQ1_SLOT, PREV_RQ1_DATA, __content_rq1, __content_rsp))
                break
            else:
                LOGGER.warning(('[DETECTED] RQ1 NOT MATCH', PREV_RQ1_DATA, __content_rq1))
            if not _Common.mandiri_single_sam():
                # Switch To The Other Slot
                auth_ka_mandiri(_slot=_Common.get_active_sam(bank='MANDIRI', reverse=True), initial=False)
            break
        sleep(15)


def get_card_info_tapcash(mode='NORMAL'):
    # PURSE_DATA_BNI_CONTACTLESS
    # {"Result":"0","Command":"020","Parameter":"0","Response":"000175461700003074850000000001232195AEEADE4A080F4B00285DDCD9B4BA924B00000000010013B288889999040000962F210F4088889999040000962F210F4000000000000000000000ACD44750B49BC46B63D15DC8579D3280","ErrorDesc":"Sukses"}
    param = QPROX['PURSE_DATA_BNI_CONTACTLESS'] + '|'
    if mode == 'MODE_F9':
        param = QPROX['PURSE_DATA_BNI_CONTACTLESS'] + '|' + mode + '|'
    try:
        response, result = _Command.send_request(param=param, output=None)
        if response == 0 and result is not None:
            return result
        else:
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def bni_crypto_tapcash(cyptogram, card_info):
    if cyptogram is None or card_info is None:
        return False
    try:
        param = QPROX['SEND_CRYPTO_CONTACTLESS'] + '|' + str(card_info) + '|' + str(cyptogram)
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        LOGGER.debug((str(response), str(result)))
        return True if response == 0 else False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def get_c2c_settlement_fee():
    # Must Return Array String or False
    output = []
    try:
        # Must Trigger New Get Fee Then Old Get Fee
        for applet_type in range(len(_Common.C2C_ADMIN_FEE)):
            applet_sequence = '1' if applet_type == 0 else '0' #Reverse Sequence on Get Fee
            param = QPROX['GET_FEE_C2C'] + '|' + str(applet_sequence) + '|'
            response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
            LOGGER.debug((applet_sequence, str(response), str(result)))
            # 0D706E8693EA7B160520115936DC050000831E61CB55C30FC36938ED
            if response == 0 and len(result) > 50:
                clean_result = result.strip().replace(' ', '')
                output.insert(0, clean_result)
            else:
                return False
        return output
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def pull_set_c2c_settlement_fee(file):
    attempt = 0
    # Host Remote Path
    # /topupoffline/transferbalance/responsefee
    host_check = _Common.C2C_FORWARDER_HOST
    url = 'http://'+host_check+'/bridge-service/fileget-ftp.php'
    param = {
        'host' : _Common.C2C_BANK_HOST, 
        'user' : _Common.C2C_BANK_USERNAME, 
        'password' : _Common.C2C_BANK_PASSWORD, 
        'local_path': '/home/' + _Common.SFTP_C2C['user'] + '/' + _Common.SFTP_C2C['path_fee_response'] + '/' + file,
        'remote_path': '/topupoffline/transferbalance/responsefee/' + file
    }
    LOGGER.debug((attempt, url, param))
    while True:
        attempt += 1
        response, result = _HTTPAccess.post_to_url(url, param)
        LOGGER.debug((attempt, file, response, result))
        if response == 200 and result['status'] == 0:
            new_c2c_fees = result['content'].split('\r\n')
            result_fee = []
            for applet_type in range(len(_Common.C2C_ADMIN_FEE)):
                if _Helper.empty(new_c2c_fees[applet_type]): continue
                apdu_response = new_c2c_fees[applet_type]
                fee_data = apdu_response[2:10] if apdu_response[:2] == '01' else apdu_response[:8]
                param = QPROX['SET_FEE_C2C'] + '|' + str(applet_type) + '|' + str(apdu_response) + '|'
                response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
                LOGGER.debug((applet_type, str(response), str(result)))
                data = {
                    'applet_type': 'OLD_APPLET' if applet_type == 0 else 'NEW_APPLET',
                    'response': apdu_response,
                    'fee': _Helper.reverse_hexdec(fee_data),
                    'result': True if response == 0 else False
                }
                result_fee.append(data)
            if len(result_fee) >= 2:
                _Common.log_to_temp_config('last^c2c^set^fee', _Helper.time_string())
                return result_fee
        sleep(_Common.C2C_FEE_CHECK_INTERVAL)


def start_get_card_history(bank):
    _Helper.get_thread().apply_async(get_card_history, (bank,))


def get_card_history(bank):
    if _Helper.empty(bank) is True or bank not in _Common.ALLOWED_BANK_CHECK_CARD_LOG:
        LOGGER.warning((bank, 'NOT_ALLOWED_GET_CARD_HISTORY', str(_Common.ALLOWED_BANK_CHECK_CARD_LOG)))
        QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|ERROR')
        return 
    if bank == 'BRI':
        if not _Common.BRI_SAM_ACTIVE:
            LOGGER.warning((bank, 'SAM_NOT_ACTIVE', str(_Common.BRI_SAM_ACTIVE)))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BRI_ERROR')
            return       
        param = QPROX['CARD_HISTORY_BRI'] + '|' + _Common.SLOT_BRI + '|'
        try:
            if _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
                response, result = 0, '504F535245414452|706F737265616472|070420|114840|EB|1|60022|60021#504F535245414452|706F737265616472|090420|113008|EF|1|60021|60022#504F535245414452|706F737265616472|090420|141527|EF|1|60022|60023#504F535245414452|706F737265616472|090420|141715|EB|1000|60023|61023#504F535245414452|706F737265616472|090420|145545|EF|1|61023|61024#504F535245414452|706F737265616472|090420|150157|EF|1|61024|61025#504F535245414452|706F737265616472|090420|165457|EF|2|61025|61027#504F535245414452|706F737265616472|090420|165524|EF|1|61027|61028#504F535245414452|706F737265616472|090420|165631|EF|1|61028|61029#504F535245414452|706F737265616472|080520|123106|EF|1002|61028|62030#'
            else:
                response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = parse_card_history(bank, result)
                _Common.LAST_CARD_LOG_HISTORY = output
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|'+json.dumps(output))
            else:
                
                do_get_reader_dump('get_card_history_bri')
                
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BRI_ERROR')
        except Exception as e:
            LOGGER.warning(str(e))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BRI_ERROR')
    elif bank == 'MANDIRI':    
        param = QPROX['CARD_HISTORY_MANDIRI'] + '|'
        try:
            response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = parse_card_history(bank, result)
                _Common.LAST_CARD_LOG_HISTORY = output
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|'+json.dumps(output))
            else:
                do_get_reader_dump('get_card_history_mdr')
                
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|MANDIRI_ERROR')
        except Exception as e:
            LOGGER.warning(str(e))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|MANDIRI_ERROR')
    elif bank == 'BNI':   
        param = QPROX['CARD_HISTORY_BNI'] + '|'
        try:
            response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = parse_card_history(bank, result)
                _Common.LAST_CARD_LOG_HISTORY = output
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|'+json.dumps(output))
            else:
                do_get_reader_dump('get_card_history_bni')
                
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BNI_ERROR')
        except Exception as e:
            LOGGER.warning(str(e))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BNI_ERROR')
    elif bank == 'BCA':   
        param = QPROX['CARD_HISTORY_BCA'] + '|'
        try:
            response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = parse_card_history(bank, result)
                _Common.LAST_CARD_LOG_HISTORY = output
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|'+json.dumps(output))
            else:
                do_get_reader_dump('get_card_history_bca')
                
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BCA_ERROR')
        except Exception as e:
            LOGGER.warning(str(e))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BCA_ERROR')
    elif bank == 'BNI_C2C':   
        slot = _Common.BNI_ACTIVE
        _slot = _Common.BNI_ACTIVE - 1
        param = QPROX['SAM_HISTORY_BNI'] + '|' + str(_slot) + '|'
        try:
            response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = parse_card_history(bank, result)
                return output
            else:
                return
        except Exception as e:
            LOGGER.warning(str(e))
            return
    elif bank == 'DKI':  
        param = QPROX['CARD_HISTORY_DKI'] + '|'
        try:
            response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = parse_card_history(bank, result)
                _Common.LAST_CARD_LOG_HISTORY = output
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|'+json.dumps(output))
            else:
                
                do_get_reader_dump('get_card_history_dki')
                
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|DKI_ERROR')
        except Exception as e:
            LOGGER.warning((e))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|DKI_ERROR')
    else:
        QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('SAM_HISTORY|ERROR')
        return



def bni_card_history_direct(row=30):
    param = QPROX['CARD_HISTORY_BNI_RAW'] + '|' + str(row) + '|'
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        card_purse = result.split('#')[0]
        card_history = result.split('#')[1]
        return card_purse, card_history
    else:
        do_get_reader_dump(_Helper.whoami())
        return "", ""


def mdr_card_history_direct():
    param = QPROX['CARD_HISTORY_MANDIRI'] + '|' + 'RAW' + '|'
    response, result = _Command.send_request(param=param, output=None)
    if response == 0 and len(result) > 10:
        return result
    else:
        do_get_reader_dump(_Helper.whoami())
        return ''


def bri_card_history_direct():
    param = QPROX['CARD_HISTORY_BRI_RAW'] + '|' + _Common.SLOT_BRI + '|' + 'MODE_RAW' + '|'
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        return result
    else:
        do_get_reader_dump(_Helper.whoami())
        return ""
    

def dki_card_history_direct():
    param = QPROX['CARD_HISTORY_DKI_RAW'] + '|'
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        return result
    else:
        do_get_reader_dump(_Helper.whoami())
        return ""


def bca_card_history_direct():
    param = QPROX['CARD_HISTORY_BCA_RAW'] + '|'
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        return result
    else:
        do_get_reader_dump(_Helper.whoami())
        return ""


def bni_sam_history_direct():
    # TODO CHECK SLOT VALUE
    sam_slot = _Common.BNI_ACTIVE - 1
    param = QPROX['SAM_HISTORY_BNI'] + '|' + str(sam_slot) + '|'
    response, result = _Command.send_request(param=param, output=None)
    return result if response == 0 else ''


def parse_card_history(bank, raw):
    card_history = []
    if bank is None or _Helper.empty(raw) is True:
        return card_history
    if bank == 'BRI':
        histories = raw.split('#')
        for history in histories:
            # MID Padded 0 | TID Padded 3 | Date | Time | Trx Type | Amount | Prev Balance | Last Balance
            # 0123456789123456|3330303432303230|300420|141108|EB|1|61029|61028#
            history = history.replace(' ', '')
            if _Helper.empty(history) is True:
                continue
            row = history.split('|')
            card_history.append({
                'date': datetime.strptime(row[2], '%d%m%y').strftime('%Y-%m-%d'),
                'time': ':'.join(_Helper.strtolist(row[3])),
                'type': _Common.BRI_LOG_LEGEND.get(row[4], ''),
                'amount': row[5],
                'prev_balance': row[6],
                'last_balance': row[7]
            })
        return card_history
    elif bank == 'MANDIRI':
        # NO | DATE | TID | COUNTER | TYPE | AMOUNT | BALANCE
        # 0|200520153716|29040100|1295|1500|37450|166139#1|230220142147|01234567|1290|1200|1|128693#2|230220142532|01234567|1291|1200|1|128692#3|230220144318|01234567|1292|1200|1|128691\#4|230220145239|01234567|1293|1200|1|128690
        # #5|230220145302|01234567|1294|1200|1|128689#6|200520153716|29040100|1295|1500|37450|166139#7|230220135302|01234567|1286|1200|1|128697
        # #8|230220135617|01234567|1287|1200|1|128696#9|230220141850|01234567|1288|1200|1|128695#10|230220142110|01234567|1289|1200|1|128694
        histories = raw.split('#')
        for history in histories:
            history = history.replace(' ', '')
            if _Helper.empty(history) is True:
                continue
            row = history.split('|')
            card_history.append({
                'date': datetime.strptime(row[1][:6], '%d%m%y').strftime('%Y-%m-%d'),
                'time': ':'.join(_Helper.strtolist(row[1][6:])),
                'type': _Common.MANDIRI_LOG_LEGEND.get(row[4], 'TOPUP'),
                # 'type': '-'.join([_Common.MANDIRI_LOG_LEGEND.get(row[4], ''), row[2]]),
                'amount': row[5],
                'prev_balance': str(int(row[6])-1),
                'last_balance': row[6]
            })
        return card_history
    elif bank == 'BNI':
        # BNI =  NO | TIPE | AMOUNT |DATE
        # 0|01|1|20200205230607#1|01|1|20200203012345#2|01|1|20200203012244#3|01|1|20200203012150#4|01|1|20200203011458
        histories = raw.split('#')
        for history in histories:
            history = history.replace(' ', '')
            if _Helper.empty(history) is True:
                continue
            row = history.split('|')
            card_history.append({
                'date': datetime.strptime(row[3][:8], '%Y%m%d').strftime('%Y-%m-%d'),
                'time': ':'.join(_Helper.strtolist(row[3][8:])),
                'type': _Common.BNI_LOG_LEGEND.get(row[1], ''),
                'amount': row[2],
                'prev_balance': '',
                'last_balance': ''
            })
        return card_history
    elif bank == 'BCA':
        # BCA =  NO | TIPE | AMOUNT | DATE
        # 0|24|1|20200205230607#1|01|1|20200203012345#2|01|1|20200203012244#3|01|1|20200203012150#4|01|1|20200203011458
        # 24 0000020016 885096050087 EGEN2010 180830112727
        histories = raw.split('#')
        for history in histories:
            history = history.replace(' ', '')
            if _Helper.empty(history) is True:
                continue
            row = history.split('|')
            card_history.append({
                'date': datetime.strptime(row[3][:6], '%y%m%d').strftime('%Y-%m-%d'),
                'time': ':'.join(_Helper.strtolist(row[3][6:])),
                'type': _Common.BCA_LOG_LEGEND.get(row[1], ''),
                'amount': row[2],
                'prev_balance': '',
                'last_balance': ''
            })
        return card_history
    elif bank == 'DKI':
        histories = raw.split('#')
        # 1|02|8500|20221124121951|56000#
        # 2|02|8500|20221103125415|47500#
        # 3|01|1500|20220913163320|39000#
        # 4|01|3500|20220913142306|40500#
        # 5|02|8500|20220913141621|44000#
        # 6|02|8500|20220913140819|35500#
        # 7|02|8500|20220824175115|27000#
        # 8|02|8500|20220819165251|18500#
        # 9|02|10000|20210112185142|10000#
        for history in histories:
            history = history.replace(' ', '')
            if _Helper.empty(history) is True:
                continue
            row = history.split('|')
            if len(row) < 3:
                continue
            card_history.append({
                'date': datetime.strptime(row[3][:8], '%Y%m%d').strftime('%Y-%m-%d'),
                'time': ':'.join(_Helper.strtolist(row[3][8:])),
                'type': _Common.DKI_LOG_LEGEND.get(row[1], ''),
                'amount': row[2],
                'prev_balance': '',
                'last_balance': row[4]
            })
        return card_history
    else:
        return card_history


def reset_card_contactless():
    # Add Reset Reader Card Contactless
    response, result = _Command.send_request(param=QPROX['RESET_CONTACTLESS'] + '|', output=_Command.MO_REPORT)
    LOGGER.debug((response, result))


def new_topup_failure_handler(bank, trxid, amount, pending_data=None):
    # output = {
        #     'balance': balance,
        #     'card_no': card_no,
        #     'bank_type': bank_type,
        #     'bank_name': bank_name,
        #     'able_check_log': able_check_log,
        #     'able_topup': '0000', #Default
        # }
    LOGGER.info((_Common.NEW_TOPUP_FAILURE_HANDLER))
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    if last_card_check.get('bank_name') != bank:
        LOGGER.warning(('Card Bank Not Match'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_03')
        return
    
    card_check = False
    attempt = 3
    while card_check is False:
        if attempt == 0:
            break
        reset_card_contactless()
        sleep(.5)
        card_check = direct_card_balance(history_on=['BCA'])
        if card_check is not False:
            if card_check['card_no'] != last_card_check['card_no']:
                LOGGER.warning(('TOPUP_FAILURE_03', 'CARD_NO_NOT_MATCH'))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_03')
                return
            break
        attempt -= 1
        sleep(2)
        
    if card_check is False:
        LOGGER.warning(('TOPUP_FAILURE_03', 'CARD_NOT_DETECTED_3_ATTEMPTS'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_03')
        return
    
    if bank == 'MANDIRI':
        amount = int(amount) - _Common.KIOSK_ADMIN
        
    elif bank == 'BCA':
        if len(card_check.get('history', '')) < 4:
            LOGGER.warning(('TOPUP_FAILURE_03', 'CARD_NOT_DETECTED_3_ATTEMPTS'))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_03')
            return
    
    card_check['prev_balance'] = last_card_check['balance']
    
    if int(card_check['balance']) != int(last_card_check['balance']) or int(card_check['balance']) == int(last_card_check['balance']) + int(amount) :
        # Removal Data Pending Lock For Topup Online
        _Common.remove_temp_data(trxid)
        _Common.remove_temp_data(card_check.get('card_no'))
        handle_topup_success_event(bank, amount, trxid, card_check, pending_data)
        return
    
    # Handle Negative Result
    handle_topup_failure_event(bank, amount, trxid, card_check, pending_data)  
    

def handle_topup_success_event(bank, amount, trxid, card_data, pending_data):
    last_audit_result = _Common.load_from_temp_data(trxid+'-last-audit-result', 'json')
    rc = last_audit_result.get('err_code')
    # 'trxid': trxid+'_FAILED',
    # 'samCardNo': _Common.MANDIRI_SAM_NO_1,
    # 'samCardSlot': _Common.MANDIRI_ACTIVE,
    # 'samPrevBalance': prev_deposit_balance,
    # 'samLastBalance': _Common.MANDIRI_ACTIVE_WALLET,
    # 'topupCardNo': last_card_check['card_no'],
    # 'topupPrevBalance': last_card_check['balance'],
    # 'topupLastBalance': last_card_check['balance'],
    # 'status': 'FORCE_SETTLEMENT' if str(prev_deposit_balance) != str(_Common.MANDIRI_ACTIVE_WALLET) else 'FAILED',
    # 'remarks': {},
    # 'last_result': topup_result,
    # 'err_code': topup_result.get('Result'),
    if bank == 'MANDIRI':
        # redefine amount, previouly already deducted with admin fee
        amount = int(amount) + _Common.KIOSK_ADMIN
        if rc == '101C':
            # Old Applet
            _param = '101C_NOPARAM'
            _response = rc
            _result = ''
            # New Partial
            if not _Helper.empty(last_audit_result.get('err_report')):
                _result = last_audit_result.get('err_report')
                parse_c2c_report(report=_result, reff_no=trxid, amount=amount, status='101C')
        else:
            # 100C Will Also Get Force Settlement Command
            # LAST_C2C_APP_TYPE Must Be '1'
            _param = QPROX['FORCE_SETTLEMENT'] + '|' + LAST_C2C_APP_TYPE + '|'
            _response, _result = _Command.send_request(param=_param, output=_Command.MO_REPORT)
            
        LOGGER.debug((_param, _response, _result))
        if _response == 0 and len(_result) >= 196 and rc != '101C':
            parse_c2c_report(report=_result, reff_no=trxid, amount=amount, status='0000')
        else:
            # Force Success If Not Get Force Settlement Report
            output = {
                'last_balance': card_data.get('balance'),
                'report_sam': 'N/A',
                'card_no': card_data.get('card_no'),
                'report_ka': 'N/A',
                'bank_id': '1',
                'bank_name': 'MANDIRI',
                'prev_balance': card_data.get('prev_balance'),
                'deposit_no': last_audit_result.get('samCardNo'),
                'deposit_prev_balance': last_audit_result.get('samPrevBalance'),
                'deposit_last_balance': last_audit_result.get('samLastBalance'),
                'topup_report': 'N/A',
            }
            LOGGER.info((bank, str(output), 'SUCCESS_TOPUP_BUT_NOT_FOUND_REPORT'))
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
            
    elif bank == 'BNI':
        output = {
            'last_balance': card_data.get('balance'),
            'report_sam': 'N/A',
            'card_no': card_data.get('card_no'),
            'report_ka': 'N/A',
            'bank_id': '2',
            'bank_name': 'BNI',
            'prev_balance': card_data.get('balance'),
            'deposit_no': last_audit_result.get('samCardNo'),
            'deposit_prev_balance': last_audit_result.get('samPrevBalance'),
            'deposit_last_balance': last_audit_result.get('samLastBalance'),
            'topup_report': 'N/A',
        }
        LOGGER.info((bank, str(output)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
    else :
        output = {
            # 'prev_wallet': pending_result['prev_wallet'],
            # 'last_wallet': pending_result['last_wallet'],
            'last_balance': card_data.get('balance'),
            'topup_amount': amount,
            'other_channel_topup': '0',
            'report_sam': 'N/A',
            'card_no': card_data.get('card_no'),
            'report_ka': 'N/A',
            'bank_id': _Common.CODE_BANK_BY_NAME.get(bank),
            'bank_name': bank,
            'prev_balance': card_data.get('prev_balance'),
            'deposit_no': 'N/A',
            'deposit_prev_balance': 'N/A',
            'deposit_last_balance': 'N/A',
            'topup_report': json.dumps(pending_data)
            }
        LOGGER.info((bank, str(output)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        # Must Send Force ACK Success To Core API
        # Merging Pending Data With Output
        output.update(pending_data)
        send_force_confirmation(bank, output)
        
TOPUP_URL = _Common.UPDATE_BALANCE_URL_DEV

if _Common.LIVE_MODE is True or _Common.PTR_MODE is True:
    TOPUP_URL = _Common.UPDATE_BALANCE_URL
    

def send_force_confirmation(bank, data):
    if bank == 'BRI':
        try:
            param = {
                'invoice_no': data.get('invoice_no'),
                'token': _Common.CORE_TOKEN,
                'mid': _Common.CORE_MID,
                'tid': _Common.TID,
                'reff_no_host': data.get('reff_no_trx'),
                'card_no': data.get('card_no'),
                'last_balance': data.get('last_balance'),
                'force_confirm': 1,
                'random_token': 'N/A'
            }
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bri/confirm', param=param)
            LOGGER.debug((str(param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                pass
            else:
                param['endpoint'] = 'topup-bri/confirm'
                _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-bri/confirm', payload=param)
        except Exception as e:
            LOGGER.warning((e))
            
    elif bank == 'BCA':
        try:
            res_bca_card_info, bca_card_info_data = bca_card_info()
            if res_bca_card_info is False:
                LOGGER.warning(('BCA_CARD_INFO_FAILED', data.get('invoice_no'), bca_card_info_data))
                bca_card_info_data = ''
            param = {
                'invoice_no': data.get('invoice_no'),
                'token': _Common.CORE_TOKEN,
                'mid': _Common.CORE_MID,
                'tid': _Common.TID,
                'reference_id': _Common.LAST_BCA_REFF_ID,
                'card_no': data.get('card_no'),
                'last_balance': data.get('last_balance'),
                'confirm_data': bca_card_info_data
            }
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bca/confirm', param=param)
            LOGGER.debug((str(param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                pass
            else:
                param['endpoint'] = 'topup-bca/confirm'
                _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-bca/confirm', payload=param)
        except Exception as e:
            LOGGER.warning((e))
            
    elif bank == 'DKI':
        try:
            param = {
                'invoice_no': data.get('invoice_no'),
                'token': _Common.CORE_TOKEN,
                'mid': _Common.CORE_MID,
                'tid': _Common.TID,
                'reff_no': data.get('reff_no'),
                'card_no': data.get('card_no'),
                'last_balance': data.get('last_balance'),
                'force_confirm': 1,
            }
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-dki/confirm', param=param)
            LOGGER.debug((str(param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                pass
            else:
                param['endpoint'] = 'topup-dki/confirm'
                _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-dki/confirm', payload=param)
        except Exception as e:
            LOGGER.warning((e))


def handle_topup_failure_event(bank, amount, trxid, card_data, pending_data):    
    last_audit_result = _Common.load_from_temp_data(trxid+'-last-audit-result', 'json')
    topup_url = _Common.UPDATE_BALANCE_URL if _Common.LIVE_MODE else _Common.UPDATE_BALANCE_URL_DEV
    if bank == 'MANDIRI':
        try:
            force_report = ''
            # Mandiri Deposit Not Deducted
            if int(last_audit_result.get('samPrevBalance', 0)) == int(last_audit_result.get('samLastBalance', 0)):
                failure_rc = '0511'
            else:
                failure_rc = '02'
                rc = last_audit_result.get('err_code')
                amount = int(amount) + _Common.KIOSK_ADMIN
                attempt = 2
                
                while True:
                    if attempt == 0:
                        break
                    last_audit_result['status'] = 'FORCE_SETTLEMENT'

                    if rc == '101C':
                        status = rc
                        _response = 0
                        _param = '101C_NOPARAM'
                        if not _Helper.empty(last_audit_result.get('err_report')):
                            force_report = last_audit_result.get('err_report')
                    else:
                        # 100C And Other Error
                        # 100C = Must Be New Applet
                        # LAST_C2C_APP_TYPE = Must Be '1'
                        status = 'FAILED'
                        _param = QPROX['FORCE_SETTLEMENT'] + '|' + LAST_C2C_APP_TYPE + '|'
                        _response, force_report = _Command.send_request(param=_param, output=_Command.MO_REPORT)
                        
                    LOGGER.debug((_param, _response, force_report))
                    if _response == 0 and len(force_report) >= 196:
                        parse_c2c_report(report=force_report, reff_no=trxid, amount=amount, status=status)
                        break
                    attempt -= 1
                    sleep(1)
                    
            extra_data = {
                    'mid': _Common.C2C_MID,
                    'tid': _Common.C2C_TID,
                    'amount': amount,
                    'force_report': force_report,
                    'err_code': last_audit_result.get('err_code', _Common.LAST_READER_ERR_CODE),
                    'can': '',
                    'csn': '',
                    'card_history': '',
                    'sam_history': '',
                    # 'sam_purse': sam_purse,
                    'card_purse': '',
            }
            
            last_audit_result.update(extra_data)
            _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(last_audit_result))
            
        except Exception as e:
            LOGGER.warning((e))
        finally:
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_'+failure_rc)
    
    elif bank == 'BNI':
        # Get Card Log And Push SAM Audit
        try:
            param = last_audit_result
            # BNI Deposit Not Deducted
            if int(last_audit_result.get('samPrevBalance', 0)) == int(last_audit_result.get('samLastBalance', 0)):
                failure_rc = '0521'
            else:
                failure_rc = '02'
                if 'topup_result' in param.keys():
                    param.pop('topup_result')
                if 'last_result' in param.keys():
                    param.pop('last_result')
                # Will Change To Card Purse
                # sam_purse = last_audit_result.get('sam_purse')
        
            sam_history = last_audit_result.get('sam_history', '') 
            card_purse, card_history = bni_card_history_direct(10)
            # Build BNI Force Settlement Using Old FW
            # force_report = get_force_settlement_bni(card_purse)
            # grab NOK File in New FW
            # force_report = get_last_error_report_bni()
            # New FW, Report Force Will Be Generated From Reader
            force_report = last_audit_result.get('err_report', '') 
            
            extra_data = {
                    'mid': _Common.MID_BNI,
                    'tid': _Common.TID_BNI,
                    'can': card_data.get('card_no'),
                    'csn': '',
                    'card_history': card_history,
                    'amount': amount,
                    'sam_history': sam_history,
                    'force_report': force_report,
                    # 'sam_purse': sam_purse,
                    'card_purse': card_purse,
                    'err_code': last_audit_result.get('err_code', _Common.LAST_READER_ERR_CODE),
                }
                
            param['remarks'] = json.dumps(extra_data)
            
            if failure_rc == '02':
                # Send To SAM Audit If Only Deduct Deposit Balance
                _Common.store_upload_sam_audit(param)
            
            last_audit_result.update(extra_data)
            _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(last_audit_result))

        except Exception as e:
            LOGGER.warning((e))
        finally:
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_'+failure_rc)
    
    # Below Will Handle Topup Online Failure Which Must Be Handling Reversal/Topup As Well
    elif bank == 'BRI':
        try:
            card_history = bri_card_history_direct()   
            reversal_result = ''
            refund_result = ''
            if pending_data is not None:
                # Only Send Reversal If Already Get Access Token On Update Balance
                if len(pending_data.get('access_token', '')) > 0:
                    _param = QPROX['REVERSAL_ONLINE_BRI'] + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN +  '|' + _Common.SLOT_BRI + '|' + pending_data.get('access_token') + '|' + pending_data.get('bank_reff_no') + '|'
                    response, reversal_result = _Command.send_request(param=_param, output=None)
                    # {"Result":"0000","Command":"024","Parameter":"01234567|1234567abc|165eea86947a4e9483d1902f93495fc6|3",
                    # "Response":"6013500601505143|1000|66030","ErrorDesc":"Sukses"}
                    LOGGER.debug((response, reversal_result))
                # Whatever The Reversal Result, Continue To Do Refund
                param = {
                    'token': _Common.CORE_TOKEN,
                    'mid': _Common.CORE_MID,
                    'tid': _Common.TID,
                    'reff_no_host': pending_data.get('reff_no_trx'),
                    'card_no': card_data.get('card_no'),
                }
                status, refund_result = _HTTPAccess.post_to_url(url=topup_url + 'topup-bri/refund', param=param)
                LOGGER.debug((bank, str(param), str(refund_result)))
                
                if status == 200 and refund_result['response']['code'] == 200:
                    _Common.remove_temp_data(trxid)
                else:
                    _Common.LAST_BRI_ERR_CODE = '33'
            else:
                pending_data = {}
            # Re-write Last Audit Result
            last_audit_result.update({
                    'tid': '',
                    'mid': '',
                    'pending_result': pending_data,
                    'card_history': card_history,
                    'amount': amount,
                    'err_code': last_audit_result.get('err_code', _Common.LAST_READER_ERR_CODE),
                    'ack_result': '',
                    'refund_result': refund_result,
                    'reversal_result': reversal_result,
                    'card_info': ''
                })
            _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(last_audit_result))
        except Exception as e:
            LOGGER.warning((e))
        finally:
            sub_rc = _Common.LAST_BRI_ERR_CODE
            if sub_rc == '': sub_rc = '01'
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_04'+sub_rc)
            
    elif bank == 'BCA':
        try:
            bca_card_info_data = ''
            ack_result = ''
            if pending_data is not None:
                # Sending ACK
                res_bca_card_info, bca_card_info_data = bca_card_info()
                if res_bca_card_info is False:
                    LOGGER.warning(('BCA_CARD_INFO_FAILED', trxid, bca_card_info_data))
                    bca_card_info_data = ''
                    # rc = bca_card_info.get('Result', 'FFFF')
                param = {
                    'token': _Common.CORE_TOKEN,
                    'mid': _Common.CORE_MID,
                    'tid': _Common.TID,
                    'card_data': bca_card_info_data,
                    'card_no': card_data.get('card_no'),
                    'last_balance': card_data.get('balance'),
                    'reference_id': _Common.LAST_BCA_REFF_ID,
                }
                # Send ACK
                status, ack_result = _HTTPAccess.post_to_url(url=topup_url + 'topup-bca/confirm', param=param)
                LOGGER.debug((bank, str(param), str(ack_result)))
                
                if status == 200 and ack_result['response']['code'] == 200:
                    _Common.remove_temp_data(trxid)
                else:
                    # _Common.LAST_BCA_ERR_CODE = '44'
                    pass
            else:
                pending_data = {}
            # Re-write Last Audit Result
            # card_history = bca_card_history_direct()   
            card_history = card_data.get('history')
            last_audit_result.update({
                    'tid': _Common.TID_TOPUP_BCA,
                    'mid': _Common.MID_TOPUP_BCA,
                    'pending_result': pending_data,
                    'card_history': card_history,
                    'amount': amount,
                    'err_code': last_audit_result.get('err_code', _Common.LAST_READER_ERR_CODE),
                    'ack_result': ack_result,
                    'refund_result': '',
                    'card_info': bca_card_info_data,
                    'reversal_result': _Common.LAST_BCA_REVERSAL_RESULT
            })
            _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(last_audit_result))
        except Exception as e:
            LOGGER.warning((e))
        finally:
            _Common.LAST_BCA_REVERSAL_RESULT = ''
            sub_rc = _Common.LAST_BCA_ERR_CODE
            if sub_rc == '': sub_rc = '01'
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_04'+sub_rc)
            
    elif bank == 'DKI':
        try:
            reversal_result = ''
            card_history = dki_card_history_direct()   

            if pending_data is not None:
                param = {
                    'token': _Common.CORE_TOKEN,
                    'mid': _Common.CORE_MID,
                    'tid': _Common.TID,
                    'card_no': card_data.get('card_no'),
                    'reff_no': trxid
                }
                status, reversal_result = _HTTPAccess.post_to_url(url=topup_url + 'topup-dki/reversal', param=param)
                LOGGER.debug((bank, str(param), str(reversal_result)))
                
                if status == 200 and reversal_result['response']['code'] == 200:
                    _Common.remove_temp_data(trxid)      
                else:
                    _Common.LAST_DKI_ERR_CODE = '52'
            else:
                pending_data = {}
            # Re-write Last Audit Result
            last_audit_result.update({
                    'pending_result': pending_data,
                    'tid': _Common.TID_TOPUP_ONLINE_DKI,
                    'mid': _Common.MID_TOPUP_ONLINE_DKI,
                    'card_history': card_history,
                    'ack_result': '',
                    'refund_result': '',
                    'card_info': '',
                    'amount': amount,
                    'err_code': last_audit_result.get('err_code', _Common.LAST_READER_ERR_CODE),
                    'reversal_result': reversal_result
            })
            _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(last_audit_result))
        except Exception as e:
            trace = traceback.format_exc()
            formatted_lines = trace.splitlines()
            err_message = traceback._cause_message
            LOGGER.warning((str(trace), str(formatted_lines), str(err_message)))
        finally:
            sub_rc = _Common.LAST_DKI_ERR_CODE
            if sub_rc == '': sub_rc = '01'
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FAILURE_04'+sub_rc)


def revalidate_card(cardno):
    reset_card_contactless()
    max_attempt = 3
    attempt = 0
    while True:
        attempt += 1
        validate_card = direct_card_balance()
        LOGGER.debug((attempt, str(validate_card)))
        if validate_card is not False or attempt == max_attempt:
            break
        sleep(1)
    if validate_card is False:
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_MISSMATCH')
        return False
    if validate_card.get('card_no') != cardno:
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_MISSMATCH')
        return False
    return True
