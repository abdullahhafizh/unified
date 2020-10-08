__author__ = 'fitrah.wahyudi.imam@gmail.com'


from _cConfig import _ConfigParser, _Common
from _cCommand import _Command
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from _tTools import _Helper
from _dDAO import _DAO
from time import sleep
import json
from _nNetwork import _NetworkAccess
from datetime import datetime
import random


LOGGER = logging.getLogger()
QPROX_PORT = _Common.QPROX_PORT
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
    "INIT_BNI": "012",
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
    "GET_LAST_C2C_REPORT": "041", #"Send SAM C2C Slot"
    "TOPUP_ONLINE_DKI": "043", #"Send amount|TID|STAN|MID|InoviceNO|ReffNO "
}


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

def bni_crypto_deposit(card_info, cyptogram, slot=1, bank='BNI'):
    if bank == 'BNI':
        #Getting Previous samBalance
        samPrevBalance = _Common.BNI_SAM_1_WALLET if slot == 1 else _Common.BNI_SAM_2_WALLET
        # Converting Default Slot into Actual Slot
        alias_slot = BNI_SAM_SLOT[str(slot)]
        if len(card_info) == 0 or card_info is None:
            LOGGER.warning((str(card_info), 'WRONG_VALUE'))
            return False
        if len(cyptogram) == 0 or cyptogram is None:
            LOGGER.warning((str(cyptogram), 'WRONG_VALUE'))
            return False
        param = QPROX['SEND_CRYPTO'] + '|' + str(alias_slot) + '|' + str(card_info) + '|' + str(cyptogram)
        response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
        LOGGER.debug((result))
        if response == 0 and len(result) > 10:
            result = result.replace('#', '')
            output = {
                'result': result,
                'bank_id': '2',
                'bank_name': bank,
            }
            sleep(1)
            ka_info_bni(slot=slot)
            # get_card_info(slot=slot)
            LOGGER.info((str(slot), bank, str(output)))
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
            #Upload To Server
            _Common.upload_bni_wallet()
            _Common.TRIGGER_MANUAL_TOPUP = True
            return output
        else:
            _Common.online_logger([result, card_info, cyptogram, slot, bank], 'general')
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
            # ka_info_bni(slot=slot)
            if slot == 1:
                _Common.BNI_SAM_1_NO = BNI_CARD_NO_SLOT_1 = output['card_no'] 
            if slot == 2:
                _Common.BNI_SAM_2_NO = BNI_CARD_NO_SLOT_2 = output['card_no']
            LOGGER.debug(('set_bni_sam_no', str(slot), output['card_no']))
            _Common.set_bni_sam_no(str(slot), output['card_no'])
            LOGGER.info((str(slot), bank, str(output)))
            return output
        else:
            _Common.NFC_ERROR = 'CHECK_CARD_INFO_BNI_ERROR_SLOT_'+str(slot)
            return 
    elif bank == 'MANDIRI_C2C':
        # TODO Add Logic Handler Here
        pass
    else:
        return False


def open():
    global OPEN_STATUS
    if QPROX_PORT is None:
        LOGGER.debug(("port : ", QPROX_PORT))
        _Common.NFC_ERROR = 'PORT_NOT_DEFINED'
        return False
    param = QPROX["OPEN"] + "|" + QPROX_PORT
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
INIT_BCA = False
INIT_LIST = []


def start_init_config():
    _Helper.get_thread().apply_async(init_config)


def init_config():
    global INIT_STATUS, INIT_LIST, INIT_BNI, INIT_MANDIRI
    if OPEN_STATUS is not True:
        LOGGER.warning(('OPEN STATUS', str(OPEN_STATUS)))
        _Common.NFC_ERROR = 'PORT_NOT_OPENED'
        return
    try:
        for BANK in BANKS:
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
                                c2c_balance_info()
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
                    param = QPROX['UPDATE_TID_BNI'] + '|' + TID_BNI
                    response, result = _Command.send_request(param=param, output=None)
                    if response == 0:
                        LOGGER.info((BANK['BANK'], result))
                        INIT_LIST.append(BANK)
                        INIT_STATUS = True
                        INIT_BNI = True
                        ka_info_bni(slot=_Common.BNI_ACTIVE)
                        sleep(1.5)
                        get_card_info(slot=_Common.BNI_ACTIVE, bank='BNI')    
                        # get_bni_wallet_status()
                    else:
                        LOGGER.warning((BANK['BANK'], result))
            sleep(1)
            continue
    except Exception as e:
        _Common.NFC_ERROR = 'FAILED_TO_INIT'
        LOGGER.warning((e))


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


LAST_BALANCE_CHECK = None
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
    global LAST_BALANCE_CHECK
    param = QPROX['BALANCE'] + '|'
    # Start Force Testing Mode ==========================
    if _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
        dummy_output = random.choice(DUMMY_BALANCE_CHECK_BALANCE)
        QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|' + json.dumps(dummy_output))
        return
    # End Force Testing Mode ==========================
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
            LOGGER.debug((card_no, _Common.MANDIRI_CARD_BLOCKED_LIST, output))
        elif bank_name == 'BNI':
            output['able_topup'] = result.split('|')[3].replace('#', '')
            # Drop Balance Check If Not Available For Topup
            if output['able_topup'] in ERROR_TOPUP.keys():
                output['able_topup'] = '1004'
            else:
                output['able_topup'] = '0000'
        # elif bank_name == 'DKI':
        #     prev_last_balance = _ConfigParser.get_value('TEMPORARY', card_no)
        #     if not _Common.empty(prev_last_balance):
        #         output['balance'] = prev_last_balance
        #     else:
        #         _Common.log_to_temp_config(card_no, balance)
        LAST_BALANCE_CHECK = output
        _Common.NFC_ERROR = ''
        QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|' + json.dumps(output))
    else:
        QP_SIGNDLER.SIGNAL_BALANCE_QPROX.emit('BALANCE|ERROR')


def start_topup_offline_mandiri(amount, trxid):
    if not _Common.C2C_MODE:
        _Helper.get_thread().apply_async(topup_offline_mandiri, (amount, trxid,))
    else:
        _Helper.get_thread().apply_async(topup_offline_mandiri_c2c, (amount, trxid,))


def parse_c2c_report(report='', reff_no='', amount=0, status='0000'):
    if _Common.empty(report) or len(report) < 100:
        LOGGER.warning(('EMPTY/MISSMATCH REPORT LENGTH'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        return
    if '|' not in report:
        report = '0|'+report
    # 603298180000003600030D706E8693EA7B051040100120D0070000007D0000160520174428270F0000BA0F03DC050000992DA3603298608319158400030D706E8693EA7B510401880110F40100003A5D0100160520174428270F0000C4030361F63B
    try:
        r = report.split('|')
        __data = r[1]
        if len(r[1]) > 196: 
            if r[1][:4] == '6308':
                #Trim Extra chars 4 in front, and get 196
                # |6308603298180000003600030D706E8693EA7B051040100120D0070000606D0000140520103434130F0000680F03DC050000739F8D603298608319158400030D706E8693EA7B510401880110F401000012400000140520103434130F00009A0303434D3490D
                # 603298180000003600030D706E8693EA7B051040100120D0070000606D0000140520103434130F0000680F03DC050000739F8D
                # 603298608319158400030D706E8693EA7B510401880110F401000012400000140520103434130F00009A0303434D34
                __data = r[1][4:200] 
            elif r[1][:4] == '0860':
                #Trim Extra chars 2 in front, and get 196
                # |08603298180000003600030D706E8693EA7B510401880120B80B0000803E0000140520120659000000096C0F03DC050000FBA77B603298407586934100750D706E8693EA7B051040180110DC050000CA3E0100140520120659000000090009831C09FB3
                # 603298180000003600030D706E8693EA7B510401880120B80B0000803E0000140520120659000000096C0F03DC050000FBA77B
                # 603298407586934100750D706E8693EA7B051040180110DC050000CA3E0100140520120659000000090009831C09FB
                __data = r[1][2:198]
        __report_deposit = __data[:102]
        __report_emoney = __data[102:]
        # TODO: Check If Balance is Initial or after process topup
        __deposit_balance = _Helper.reverse_hexdec(__report_deposit[54:62])
        if __deposit_balance > 0:
            _Common.MANDIRI_WALLET_1 = __deposit_balance
            _Common.MANDIRI_ACTIVE_WALLET = _Common.MANDIRI_WALLET_1
        else:
            __deposit_balance = _Common.MANDIRI_ACTIVE_WALLET
        # Update Local Mandiri Wallet
        __sam_prev_balance = _Common.MANDIRI_ACTIVE_WALLET
        __emoney_balance = _Helper.reverse_hexdec(__report_emoney[54:62])
        if not _Helper.empty(r[0].strip()) or r[0] != '0':
            __emoney_balance = r[0].strip()
        __emoney_prev_balance = int(__emoney_balance) - int(amount)
        if __report_emoney[:16] == LAST_BALANCE_CHECK['card_no']:
            __emoney_prev_balance = LAST_BALANCE_CHECK['balance']
        output = {
            'last_balance': __emoney_balance,
            'report_sam': __report_emoney,
            'card_no': __report_emoney[:16],
            'report_ka': __report_deposit,
            'bank_id': '1',
            'bank_name': 'MANDIRI',
            'c2c_mode': '1'
        }
        # Store Ouput Record Into Local DB
        _Common.local_store_topup_record(output)
        if status == '0000':
            # Emit Topup Success Record Into Local DB
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit(status+'|'+json.dumps(output))
        elif status == 'FAILED':
            # Renew C2C Deposit Balance Info
            c2c_balance_info()
            # Close Double Whatsapp When Failure
            # QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('C2C_FORCE_SETTLEMENT')
        # Ensure The C2C_DEPOSIT_NO same with Report
        if __report_deposit[:16] != _Common.C2C_DEPOSIT_NO:
            _Common.C2C_DEPOSIT_NO = __report_deposit[:16]
            _Common.MANDIRI_SAM_NO_1 = _Common.C2C_DEPOSIT_NO
        _Common.log_to_temp_config('c2c^card^no', __report_deposit[:16])
        param = {
            'trxid': reff_no,
            'samCardNo': _Common.C2C_DEPOSIT_NO,
            'samCardSlot': _Common.C2C_SAM_SLOT,
            'samPrevBalance': __sam_prev_balance,
            'samLastBalance': __deposit_balance,
            'topupCardNo': __report_emoney[:16],
            'topupPrevBalance': __emoney_prev_balance,
            'topupLastBalance': __emoney_balance,
            'status': status,
            'remarks': __data,
            'c2c_mode': '1'
        }
        _Common.store_upload_sam_audit(param)
        # Update to server
        _Common.upload_mandiri_wallet()
    except Exception as e:
        LOGGER.warning((e, report, reff_no, amount, status))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')

    

def start_topup_mandiri_correction(amount, trxid):
    if not _Common.C2C_MODE:
        return
    else:
        _Helper.get_thread().apply_async(top_up_mandiri_correction, (amount, trxid,))


# 01, 02, 03
LAST_C2C_APP_TYPE = '0'


# Check Deposit Balance If Failed, When Deducted Hit Correction, If Correction Failed, Hit FOrce Settlement And Store
def top_up_mandiri_correction(amount, trxid=''):
    param = QPROX['CORRECTION_C2C'] + '|' + LAST_C2C_APP_TYPE + '|'
    # Check Correction Result
    # Add Check Card Number First Before Correction
    response, result = _Command.send_request(param=QPROX['BALANCE'] + '|', output=_Command.MO_REPORT)
    LOGGER.debug((param, result))
    # check_card_no = LAST_BALANCE_CHECK['card_no']
    check_card_no = '0'
    last_balance = '0'
    if response == 0 and '|' in result:
        check_card_no = result.split('|')[1].replace('#', '')
        last_balance = result.split('|')[0]  
    if LAST_BALANCE_CHECK['card_no'] != check_card_no:
        LOGGER.warning(('CARD_NO MISMATCH', check_card_no, LAST_BALANCE_CHECK['card_no'], trxid, result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        get_c2c_failure_settlement(amount, trxid)
        return
    # Add Customer Last Balance Card Check After Topup C2C Failure
    if (int(LAST_BALANCE_CHECK['balance']) + int(amount) - 1500) == int(last_balance):
        param = QPROX['GET_LAST_C2C_REPORT'] + '|' + _Common.C2C_SAM_SLOT + '|'
        _, report = _Command.send_request(param=param, output=_Command.MO_REPORT)
        if _ == 0 and len(report) >= 196:
            c2c_report = '|' + report
            parse_c2c_report(report=c2c_report, reff_no=trxid, amount=amount)
            return
    # Handle Old Applet Correction
    if LAST_C2C_APP_TYPE == '0':
        return topup_offline_mandiri_c2c(amount, trxid)
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    if _response == 0 and len(_result) > 100:
        parse_c2c_report(report=_result, reff_no=trxid, amount=amount)
    else:
        LOGGER.warning((trxid, _result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        get_c2c_failure_settlement(amount, trxid)



def start_mandiri_c2c_force_settlement(amount, trxid):
    if not _Common.C2C_MODE:
            return
    else:
        _Helper.get_thread().apply_async(get_c2c_failure_settlement, (amount, trxid,))



def get_c2c_failure_settlement(amount, trxid):
    param = QPROX['FORCE_SETTLEMENT'] + '|' + LAST_C2C_APP_TYPE + '|'
    # TODO Check Force Settlement Result
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    if _response == 0 and len(_result) > 100:
        parse_c2c_report(report=_result, reff_no=trxid, amount=amount, status='FAILED')
    else:
        LOGGER.warning((trxid, _result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')


# Check Deposit Balance If Failed, When Deducted Hit Correction, If Correction Failed, Hit FOrce Settlement And Store
def topup_offline_mandiri_c2c(amount, trxid='', slot=None):
    global LAST_C2C_APP_TYPE
    if LAST_BALANCE_CHECK['card_no'] in _Common.MANDIRI_CARD_BLOCKED_LIST:
        LOGGER.warning(('Card No: ', LAST_BALANCE_CHECK['card_no'], 'Found in Mandiri Card Blocked Data'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        return
    param = QPROX['TOPUP_C2C'] + '|' + str(amount) #Amount Must Be Full Denom
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    # {"Result":"0000","Command":"026","Parameter":"2000","Response":"|6308603298180000003600030D706E8693EA7B051040100120D0070000384A0000050520120439FF0E00004D0F03DC0500000768C7603298602554826300020D706E8693EA7B510401880110F4010000CE4A0000050520120439FF0E0000020103E7F2E790A","ErrorDesc":"Sukses"}
    # {"Command": "028", "ErrorDesc": "Gagal", "Result": "0290", "Response": "", "Parameter": "0"}
    if _response == 0 and len(_result) >= 196:
        c2c_report = _result
        parse_c2c_report(report=c2c_report, reff_no=trxid, amount=amount)
        return
    try:
        _result_json = json.loads(_result)
        if _result_json["Result"] == "0290":
            param = QPROX['GET_LAST_C2C_REPORT'] + '|' + _Common.C2C_SAM_SLOT + '|'
            _, report = _Command.send_request(param=param, output=_Command.MO_REPORT)
            if _ == 0 and len(report) >= 196:
                c2c_report = '|' + report
                parse_c2c_report(report=c2c_report, reff_no=trxid, amount=amount)
                return
        elif _result_json["Response"] == '83':
            LAST_C2C_APP_TYPE = '1'
        else:
            LAST_C2C_APP_TYPE = '0'
        LOGGER.warning(('result', _result, 'applet_type', LAST_C2C_APP_TYPE, 'TOPUP_C2C_CORRECTION'))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_C2C_CORRECTION')
    except Exception as e:
        LOGGER.warning((e))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')


def topup_offline_mandiri(amount, trxid='', slot=None):
    global INIT_MANDIRI
    if len(INIT_LIST) == 0:
        LOGGER.warning(('INIT_LIST', str(INIT_LIST)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        _Common.NFC_ERROR = 'EMPTY_INIT_LIST'
        return
    if slot is None:
        slot = str(_Common.MANDIRI_ACTIVE)
    param = QPROX['TOPUP'] + '|' + str(amount)
    _response, _result = _Command.send_request(param=param, output=_Command.MO_REPORT)
    if _response == 0 and '|' in _result:
        __data = _result.split('|')
        __status = __data[0]
        __remarks = ''
        if __status == '0000':
            __remarks = __data[5]
        if __status == '6969':
            LOGGER.warning(('TOPUP_FAILED_CARD_NOT_MATCH', LAST_BALANCE_CHECK))
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
        # status='0000' -> success
        # samCardNo='7546130000013640'
        # samPrevBalance='100000'
        # samLastBalance='90000'
        # reportSAM='75461300000136407546130000013640010002EE0003520000647A0F127A0EAE2D944C9D04B5E8816DCE7F381E8480010701000009000009000007010002EE00000088889999E7C0A8568C598500AB3DFE1320FCBDE369D72A9D48B835AB00035204B5E8816D04B5E8816DCE7F380000090000090000754646000000159675464600000015965017CE0054DB8D88'
        # topupCardNo='7546460000001596'
        # topupPrevBalance='1000'
        # topupLastBalance='11000'
        # 0000| -> 0
        # 7546000001023442| -> 1
        # 556900| -> 2
        # 556899| -> 3
        # 1| -> 4
        # 75460000010567757546000001056775010C79B40C81840007D00F42400F3A702BA49F3600B6FFC692431D360F424001070100005A00002F000007010C79B40007D0888899996551465F2B1393685E20873C706ED28A2DB9825BF242CC3F0C818400B6FFC69200B6FFC692431D3600005A00002F000075460000000000480000000000000048E7AADAEBF223F5C4|
        # 7546000001056775| -> 6
        # 8912| -> 7
        # 8913 -> 8
        # topup_last_balance = str(int(__data[2].lstrip('0')) + int(amount))
        __samLastBalance = __data[3].lstrip('0')
        __report_sam = __data[5]
        # if __status == 'FFFE' and __data[2].lstrip('0') == __data[3].lstrip('0'):
        #     # __samLastBalance = str(int(__data[2].lstrip('0')) - int(amount))
        #     __report_sam = 'CARD_NOT_EXIST'
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
            'samLastBalance': __samLastBalance,
            'topupCardNo': __data[6],
            'topupPrevBalance': __data[7].lstrip('0'),
            'topupLastBalance': __data[8].lstrip('0'),
            'status': __status,
            'remarks': __remarks,
        }
        _Common.set_mandiri_uid(slot, __card_uid)
        _Common.store_upload_sam_audit(param)
        # Update to server
        _Common.upload_mandiri_wallet()
    else:
        LOGGER.warning((slot, _result))
        _Common.NFC_ERROR = 'TOPUP_MANDIRI_ERROR'
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')


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
            ka_info_bni(slot=1)
            if attempt == 3 or _Common.BNI_SAM_1_WALLET != 0:
                break
            sleep(1)
        # Second Attempt For SLOT 2
        _attempt = 0
        while True:
            _attempt += 1
            get_card_info(slot=2)
            sleep(1)
            ka_info_bni(slot=2)
            if _attempt == 3 or _Common.BNI_SAM_1_WALLET != 0:
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
# LAST_DKI_STAN = _ConfigParser.get_set_value('TEMPORARY', 'dki^last^topup^stan', '120')
# LAST_DKI_INVOICE_NO = _ConfigParser.get_set_value('TEMPORARY', 'dki^last^topup^invoice', '60')

def get_set_dki_stan():
    dki_stan = _ConfigParser.get_value('TEMPORARY', 'dki^last^topup^stan')
    _Common.log_to_config('TEMPORARY', 'dki^last^topup^stan', str(int(dki_stan)+1))
    return dki_stan


def get_set_dki_invoice():
    dki_invoice = _ConfigParser.get_value('TEMPORARY', 'dki^last^topup^invoice')
    _Common.log_to_config('TEMPORARY', 'dki^last^topup^invoice', str(int(dki_invoice)+1))
    return dki_invoice


# {
# "Result":"0000",
# "Command":"043",
# "Parameter":"80|91009003|000120|000080080088881|000060|200505191908",
# "Response":"9360885090123100|80|93800",
# "ErrorDesc":"Sukses"
# }

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
    else:
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')


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


def topup_offline_bni(amount, trxid, slot=None, attempt=None):
    _slot = 1
    if slot is None:
        slot = _Common.BNI_ACTIVE
        _slot = _Common.BNI_ACTIVE - 1
    if attempt == '5':
        LOGGER.debug(('TOPUP_ATTEMPT_REACHED', str(int(attempt) - 1)))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ATTEMPT_REACHED')
        return
    param = QPROX['INIT_BNI'] + '|' + str(_slot) + '|' + TID_BNI
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((attempt, amount, trxid, slot, result))
    # print('pyt: topup_offline_bni > init_bni : ', result)
    if response == 0 and '12292' not in result:
        # Update : Add slot after value
        _param = QPROX['TOPUP_BNI'] + '|' + str(amount) + '|' + str(_slot)
        _response, _result = _Command.send_request(param=_param, output=_Command.MO_REPORT, wait_for=2)
        LOGGER.debug((attempt, amount, trxid, slot, _result))
        # print('pyt: topup_offline_bni > init_bni > update_bni : ', _result)
        __remarks = ''
        if _response == 0 and '|' in _result:
            # Add Recheck Deposit Balance
            ka_info_bni(slot=_Common.BNI_ACTIVE)
            _result = _result.replace('#', '')
            __data = _result.split('|')
            __status = __data[0]
            if __status == '0000':
                __remarks = __data[5]
            if __status == '6984':
                LOGGER.warning(('BNI_SAM_BALANCE_NOT_SUFFICIENT', slot, _result))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BNI_SAM_BALANCE_NOT_SUFFICIENT|'+str(slot))
                return
            if __status == '6969':
                LOGGER.warning(('TOPUP_FAILED_CARD_NOT_MATCH', LAST_BALANCE_CHECK))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_FAILED_CARD_NOT_MATCH')
                return
            if __status in ERROR_TOPUP.keys():
                __remarks = ERROR_TOPUP[__status]
            __samLastBalance = __data[3].lstrip('0')
            if __samLastBalance != str(_Common.BNI_ACTIVE_WALLET):
                LOGGER.info(('BNI_DEPOSIT_LAST_BALANCE_REPORT_NOT_MATCH', __samLastBalance, str(_Common.BNI_ACTIVE_WALLET)))
                __samLastBalance = str(_Common.BNI_ACTIVE_WALLET)
            __report_sam = __data[5]
            if __status == 'FFFE' and __data[2].lstrip('0') == __data[3].lstrip('0'):
                # __samLastBalance = str(int(__data[2].lstrip('0')) - int(amount))
                __report_sam = 'CARD_NOT_EXIST'
            output = {
                'last_balance': __data[8].lstrip('0'),
                'report_sam': __report_sam,
                'card_no': __data[6],
                'report_ka': 'N/A',
                'bank_id': '2',
                'bank_name': 'BNI',
            }
            update_bni_wallet(slot, amount, __samLastBalance)
            if __status == '0000':
                # Store Topup Success Record Into Local DB
                _Common.local_store_topup_record(output)
            # Add Timeout Response
            if __status == '1004' or __status == '5103' or __status == 'FFFE':
                LOGGER.debug(('TOPUP_TIMEOUT', attempt, __status, _result))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
            else:
                LOGGER.info((str(output)))
                QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit(__status+'|'+json.dumps(output))
            param = {
                'trxid': trxid,
                'samCardNo': __data[1],
                'samCardSlot': slot,
                'samPrevBalance': __data[2].lstrip('0'),
                'samLastBalance': __samLastBalance,
                'topupCardNo': __data[6],
                'topupPrevBalance': __data[7].lstrip('0'),
                'topupLastBalance': __data[8].lstrip('0'),
                'status': __status,
                'remarks': __remarks,
            }
            _Common.store_upload_sam_audit(param)
        else:
            QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
    else:
        LOGGER.warning(('INIT_BNI', result))
        QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        _Common.NFC_ERROR = 'TOPUP_BNI_ERROR'


def start_ka_info():
    _Helper.get_thread().apply_async(ka_info_mandiri)


MANDIRI_DEPOSIT_BALANCE = 0


def c2c_balance_info():
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
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('C2C_BALANCE_INFO|' + str(result))
    else:
        _Common.NFC_ERROR = 'C2C_BALANCE_INFO_MANDIRI_ERROR'
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('C2C_BALANCE_INFO|ERROR')


def ka_info_mandiri(slot=None, caller=''):
    global MANDIRI_DEPOSIT_BALANCE
    if _Common.C2C_MODE is True:
        c2c_balance_info()
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
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|ERROR')


BNI_DEPOSIT_BALANCE = 0


def ka_info_bni(slot=1):
    global BNI_DEPOSIT_BALANCE
    # Slot defined as sequence
    _slot = slot - 1
    param = QPROX['KA_INFO_BNI'] + '|' + str(_slot)
    response, result = _Command.send_request(param=param, output=_Command.MO_REPORT, wait_for=1.5)
    LOGGER.debug((str(slot), result))
    if response == 0 and (result is not None and result != ''):
        BNI_DEPOSIT_BALANCE = int(result.split('|')[0])
        if slot == 1:
            _Common.BNI_SAM_1_WALLET = BNI_DEPOSIT_BALANCE
            _Common.BNI_ACTIVE_WALLET = _Common.BNI_SAM_1_WALLET
        if slot == 2:
            _Common.BNI_SAM_2_WALLET = BNI_DEPOSIT_BALANCE
            _Common.BNI_ACTIVE_WALLET = _Common.BNI_SAM_2_WALLET
        _DAO.create_today_report(_Common.TID)
        _DAO.update_today_summary_multikeys(['bni_deposit_last_balance'], int(_Common.BNI_ACTIVE_WALLET))
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|' + str(result))
    else:
        _Common.NFC_ERROR = 'KA_INFO_BNI_ERROR'
        QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.emit('KA_INFO|ERROR')


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
        _stat, _res = _NetworkAccess.post_to_url(_url, _param)
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


def get_card_info_tapcash():
    # PURSE_DATA_BNI_CONTACTLESS
    # {"Result":"0","Command":"020","Parameter":"0","Response":"000175461700003074850000000001232195AEEADE4A080F4B00285DDCD9B4BA924B00000000010013B288889999040000962F210F4088889999040000962F210F4000000000000000000000ACD44750B49BC46B63D15DC8579D3280","ErrorDesc":"Sukses"}
    param = QPROX['PURSE_DATA_BNI_CONTACTLESS'] + '|'
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
        for applet_type in range(len(_Common.C2C_ADMIN_FEE)):
            param = QPROX['GET_FEE_C2C'] + '|' + str(applet_type) + '|'
            response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
            LOGGER.debug((applet_type, str(response), str(result)))
            # 0D706E8693EA7B160520115936DC050000831E61CB55C30FC36938ED
            if response == 0 and len(result) > 50:
                clean_result = result.strip().replace(' ', '')
                output.append(clean_result)
            else:
                return False
        return output
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def set_c2c_settlement_fee(file):
    attempt = 0
    host_check = _Common.SFTP_C2C['host']
    if _Common.SFTP_C2C['port'] != '22':
        host_check = _Common.SFTP_C2C['host'] + ':18080'
    _url = 'http://'+host_check+'/bridge-service/filecheck.php?content=1&no_correction=1'
    _param = {
        'ext': '.txt',
        'file_path': '/home/' + _Common.SFTP_C2C['user'] + '/' + _Common.SFTP_C2C['path_fee_response'] + '/' + file
    }
    LOGGER.debug((attempt, file, _url, _param))
    while True:
        attempt += 1
        response, result = _NetworkAccess.post_to_url(_url, _param)
        LOGGER.debug((attempt, file, response, result))
        if response == 200 and result['status'] == 0 and result['file'] is True:
            new_c2c_fees = result['content'].split('#')[0]
            if len(new_c2c_fees) != 2:
                continue
            result_fee = []
            for applet_type in range(len(_Common.C2C_ADMIN_FEE)):
                param = QPROX['SET_FEE_C2C'] + '|' + str(applet_type) + '|' + str(new_c2c_fees[applet_type]) + '|'
                response, result = _Command.send_request(param=param, output=_Command.MO_REPORT)
                LOGGER.debug((applet_type, str(response), str(result)))
                # Check Validation of Success Inject Fee
                if response == 0 and result != '6700':
                    result_fee.append(True)
                else:
                    result_fee.append(False)
            if result_fee == [True, True]:
                _Common.log_to_temp_config('last^c2c^set^fee')
                LOGGER.info(('SUCCESS_UPDATE_ADMIN_FEE_C2C'))
                return True
                break
        sleep(15)


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
                QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BNI_ERROR')
        except Exception as e:
            LOGGER.warning(str(e))
            QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|BNI_ERROR')
    else:
        QP_SIGNDLER.SIGNAL_CARD_HISTORY.emit('CARD_HISTORY|ERROR')
        return


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
                'date': datetime.strptime(row[1][:6], '%y%m%d').strftime('%Y-%m-%d'),
                'time': ':'.join(_Helper.strtolist(row[1][6:])),
                'type': '-'.join([_Common.MANDIRI_LOG_LEGEND.get(row[4], ''), row[2]]),
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
    else:
        return card_history
