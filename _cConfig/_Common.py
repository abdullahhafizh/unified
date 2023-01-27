__author__ = "wahyudi@multidaya.id"

import logging
from _cConfig import _ConfigParser
from _tTools import _Helper
from _nNetwork import _HTTPAccess
from _dDAO import _DAO
from time import *
import os
import sys
import json
import re
from sentry_sdk import capture_exception
import platform
import subprocess
# from sentry_sdk import capture_exception

IS_LINUX = platform.system() == 'Linux'
IS_WINDOWS = not IS_LINUX

SYSTEM_VERSION = sys.version_info
MINIMUM_SYSTEM_VERSION = (3, 8)

LOGGER = logging.getLogger()


def validate_system_version():
    LOGGER.debug(('SYSTEM_VERSION', MINIMUM_SYSTEM_VERSION, SYSTEM_VERSION))
    return SYSTEM_VERSION >= MINIMUM_SYSTEM_VERSION


def chatbot_feature():
    return validate_system_version() and (IS_LINUX or '15.2.3' not in VERSION)


def support_multimedia():
    return SYSTEM_VERSION < MINIMUM_SYSTEM_VERSION and IS_WINDOWS


def get_config_value(option='', section='TEMPORARY', digit=False):
    if len(option) == 0:
        return
    if digit is True:
        return int(_ConfigParser.get_value(section, option))
    else:
        return str(_ConfigParser.get_value(section, option))


def digit_in(s):
    return any(i.isdigit() for i in s)


def clean_white_space(s):
    return re.sub(r'\s+', '', s)

VIEW_FOLDER = '_qQML/'
APP_MODE = _ConfigParser.get_set_value('GENERAL', 'mode', 'live')
LIVE_MODE = True if APP_MODE == 'live' else False
BACKEND_URL = _ConfigParser.get_set_value('GENERAL', 'backend^server', 'http://vm-api.mdd.co.id:11199/kiosk-api/v2/')
TEST_MODE = not LIVE_MODE
if LIVE_MODE is True:
    BACKEND_URL = 'http://vm-service.mdd.co.id:471/kiosk-api/v2/'
    _ConfigParser.set_value('GENERAL', 'backend^server', BACKEND_URL)
    os.system('git checkout live')
if TEST_MODE is True:
    BACKEND_URL = 'http://vm-api.mdd.co.id:11199/kiosk-api/v2/'
    _ConfigParser.set_value('GENERAL', 'backend^server', BACKEND_URL)
    os.system('git checkout ' +APP_MODE)

PTR_MODE = True if _ConfigParser.get_set_value('GENERAL', 'pir^usage', '0') == '1' else False

OVER_NIGHT = int(_ConfigParser.get_set_value('GENERAL', 'over^night', '22'))
RELOAD_SERVICE = True if _ConfigParser.get_set_value('GENERAL', 'reload^service', '0') == '1' else False
REFUND_FEATURE = True if _ConfigParser.get_set_value('GENERAL', 'refund^feature', '1') == '1' else False
TID = _ConfigParser.get_set_value('GENERAL', 'tid', '---')
TERMINAL_TOKEN = _ConfigParser.get_set_value('GENERAL', 'token', '---')

USE_PREV_THEME = True if _ConfigParser.get_set_value('GENERAL', 'use^prev^theme', '1') == '1' else False
USE_PREV_ADS = True if _ConfigParser.get_set_value('GENERAL', 'use^prev^ads', '0') == '1' else False

INTERRACTIVE_HOST = _ConfigParser.get_set_value('GENERAL', 'interractive^host', 'wss://socket-chat.multidaya.id')
if LIVE_MODE or PTR_MODE:
    INTERRACTIVE_HOST = 'wss://socket-chat.multidaya.id'

# Initiate Network Header
# HEADER = get_header()
_HTTPAccess.HEADER = _HTTPAccess.get_header(TID, TERMINAL_TOKEN)

QPROX_PORT = _ConfigParser.get_set_value('QPROX_NFC', 'port', 'COM')
INIT_DELAY_TIME = 2
# _ConfigParser.get_set_value('QPROX_NFC', 'init^delay^time', '5')

EDC_PORT = get_config_value('port', 'EDC')
EDC_TYPE = _ConfigParser.get_set_value('EDC', 'type', 'UPT-IUR')
EDC_SERIAL_NO = _ConfigParser.get_set_value('EDC', 'serial^no', ('0'*16))
EDC_MOBILE_DURATION = int(_ConfigParser.get_set_value('EDC', 'payment^duration', '180'))
EDC_MOBILE_DIRECT_MODE = _ConfigParser.get_set_value('EDC', 'payment^direct^mode', '1')
EDC_DEBIT_ONLY = True if _ConfigParser.get_set_value('EDC', 'debit^only', '1') == '1' else False

MEI_PORT = get_config_value('port', 'MEI')
BILL_PORT = get_config_value('port', 'BILL')
BILL_TYPE = _ConfigParser.get_value('BILL', 'type')
BILL_NATIVE_MODULE = True
BILL_LIBRARY_DEBUG = True if _ConfigParser.get_set_value('BILL', 'library^debug', '0') == '1' else False
BILL_RESTRICTED_NOTES = _ConfigParser.get_set_value('BILL', 'not^allowed^denom', '1000|2000|5000')
BILL_STORE_DELAY= int(_ConfigParser.get_set_value('BILL', 'store^money^delay', '2'))
BILL_DIRECT_READ_NOTE =  True if _ConfigParser.get_set_value('BILL', 'direct^read^note', '1') == '1' else False
# Hardcoded Active Bill Notes
BILL_ACTIVE_NOTES = ['5000', '10000', '20000', '50000', '75000', '100000']
# Handle Single Denom For Spesific Transaction Type
BILL_SINGLE_DENOM_TRX = _ConfigParser.get_set_value('BILL', 'single^denom^trx', 'topup').split('|')
BILL_SINGLE_DENOM_TYPE = 'GRG|MEI|NV'.split('|')

AMQP_ENABLE = True if _ConfigParser.get_set_value('AMQP', 'active', '0') == '1' else False
AMQP_HOST = _ConfigParser.get_set_value('AMQP', 'host', 'amqp.mdd.co.id')
AMQP_PORT = _ConfigParser.get_set_value('AMQP', 'port', '5672')
AMQP_USER = _ConfigParser.get_set_value('AMQP', 'user', 'kiosk')
AMQP_PASS = _ConfigParser.get_set_value('AMQP', 'pass', 'kiosk')

CD_PORT1 = _ConfigParser.get_set_value('CD', 'port1', 'COM')
CD_PORT2 = _ConfigParser.get_set_value('CD', 'port2', 'COM')
CD_PORT3 = _ConfigParser.get_set_value('CD', 'port3', 'COM')
CD_PORT4 = _ConfigParser.get_set_value('CD', 'port4', 'COM')
CD_PORT5 = _ConfigParser.get_set_value('CD', 'port5', 'COM')
CD_PORT6 = _ConfigParser.get_set_value('CD', 'port6', 'COM')

CD_PORT1_TYPE = _ConfigParser.get_set_value('CD', 'port1^type', 'OLD')
CD_PORT2_TYPE = _ConfigParser.get_set_value('CD', 'port2^type', 'OLD')
CD_PORT3_TYPE = _ConfigParser.get_set_value('CD', 'port3^type', 'OLD')
CD_PORT4_TYPE = _ConfigParser.get_set_value('CD', 'port4^type', 'OLD')
CD_PORT5_TYPE = _ConfigParser.get_set_value('CD', 'port5^type', 'OLD')
CD_PORT6_TYPE = _ConfigParser.get_set_value('CD', 'port6^type', 'OLD')

CD_TYPES = {
    CD_PORT1: CD_PORT1_TYPE,
    CD_PORT2: CD_PORT2_TYPE,
    CD_PORT3: CD_PORT3_TYPE,
    CD_PORT4: CD_PORT4_TYPE,
    CD_PORT5: CD_PORT5_TYPE,
    CD_PORT6: CD_PORT6_TYPE,
}

# Disable CD Init For Old & New Type
# CD Coneection Cannot Be Verified For Old Type
CD_DISABLE_CHECK_STATUS = True

LOGGER.info((CD_TYPES))

PRINTER_PORT = _ConfigParser.get_set_value('PRINTER', 'port', 'COM')
PRINTER_BAUDRATE = _ConfigParser.get_set_value('PRINTER', 'baudrate', '15200')
PRINTER_NEW_LAYOUT = True if _ConfigParser.get_set_value('PRINTER', 'new^layout', '0') == '1' else False
PRINTER_PAPER_TYPE = _ConfigParser.get_set_value('PRINTER', 'printer^paper^type', '80mm')

ALLOW_REPRINT_RECEIPT = True if _ConfigParser.get_set_value('PRINTER', 'allow^reprint^receipt', '0') == '1' else False


def load_from_temp_config(section='test^section', default=''):
    section = str(section)
    default = str(default)
    return _ConfigParser.get_set_value('TEMPORARY', section, default)


def log_to_config(option='TEMPORARY', section='last^auth', content=''):
    content = str(content)
    section = str(section)
    LOGGER.info((option, section, content))
    _ConfigParser.set_value(option, section, content)


def linux_get_printer_address():
    global PRINTER_PORT
    try:
        output = subprocess.Popen('ls -l /dev/usb/lp*',shell=True, stdout=subprocess.PIPE).communicate()[0]
        addr = output.split()[-1].decode('utf-8').split('/dev/usb')[-1]
        printer = '/dev/usb' + addr
        _ConfigParser.set_value('PRINTER', 'port', printer)
        PRINTER_PORT = printer
        print('pyt: Found Printer : ' + PRINTER_PORT)
    except Exception as e:
        print('pyt: Failed Detect Printer : ' + str(e))

# Add Auto Detect Printer Address
if IS_LINUX:
    linux_get_printer_address()


MID_MAN = _ConfigParser.get_set_value('MANDIRI', 'mid', '---')
TID_MAN = _ConfigParser.get_set_value('MANDIRI', 'tid', '---')
SAM_MAN = _ConfigParser.get_set_value('MANDIRI', 'sam^pin', '---')
MANDIRI_THRESHOLD = int(_ConfigParser.get_set_value('MANDIRI', 'amount^minimum', '50000'))

MID_BNI = _ConfigParser.get_set_value('BNI', 'mid', '---')
TID_BNI = _ConfigParser.get_set_value('BNI', 'tid', '---')
MC_BNI = _ConfigParser.get_set_value('BNI', 'merried^code', '---')
SLOT_SAM1_BNI = _ConfigParser.get_set_value('BNI', 'sam1^slot', '---')
SLOT_SAM2_BNI = _ConfigParser.get_set_value('BNI', 'sam2^slot', '---')
BNI_TOPUP_AMOUNT = _ConfigParser.get_set_value('BNI', 'amount^topup', '500000')
BNI_THRESHOLD = int(_ConfigParser.get_set_value('BNI', 'amount^minimum', '50000'))
# BNI_ACTIVATION_RETRY = _ConfigParser.get_set_value('BNI', 'activation^retry', '5')
BNI_ACTIVATION_RETRY = '3'
BNI_GET_REFERENCE_TIMEOUT = _ConfigParser.get_set_value('BNI', 'get^reference^timeout^minute', '30')
URL_BNI_ACTIVATION = _ConfigParser.get_set_value('BNI', 'url^activation', 'http://axa.mdd.co.id:5000/')
BNI_REMOTE_ACTIVATION = _ConfigParser.get_set_value('BNI', 'remote^activation', '0')

if LIVE_MODE is True:
    # if not PTR_MODE:
        # URL_BNI_ACTIVATION = 'http://axa.mdd.co.id:5000/'
        # _ConfigParser.set_value('BNI', 'url^activation', URL_BNI_ACTIVATION)
    BNI_REMOTE_ACTIVATION = True
    _ConfigParser.set_value('BNI', 'remote^activation', '1')
    
BNI_C2C_TRESHOLD_USAGE = True if _ConfigParser.get_set_value('BNI', 'treshold^usage', '0') == '1' else False

MID_BRI = _ConfigParser.get_set_value('BRI', 'mid', '---')
TID_BRI = _ConfigParser.get_set_value('BRI', 'tid', '---')
PROCODE_BRI = _ConfigParser.get_set_value('BRI', 'procode', '---')
SLOT_BRI = _ConfigParser.get_set_value('BRI', 'sam^slot', '---')
BRI_AUTO_REFUND = True if _ConfigParser.get_set_value('BRI', 'auto^refund', '1') == '1' else False
BRI_SAM_ACTIVE = digit_in(SLOT_BRI) and len(SLOT_BRI) == 1

MID_BCA = _ConfigParser.get_set_value('BCA', 'mid', '---')
TID_BCA = _ConfigParser.get_set_value('BCA', 'tid', '---')
MID_TOPUP_BCA = _ConfigParser.get_set_value('BCA', 'mid^topup', '000942678')
TID_TOPUP_BCA = _ConfigParser.get_set_value('BCA', 'tid^topup', 'ELZSYB01')


if not LIVE_MODE:
    # Force Set MID/TID BCA On Development Stage
    MID_BCA = '000942678'
    _ConfigParser.set_value('BCA', 'mid^topup', '000942678')
    TID_BCA = 'ELZSYB01'
    _ConfigParser.set_value('BCA', 'tid^topup', 'ELZSYB01')


DEV_MODE_TOPUP_BCA = True if TID_TOPUP_BCA == 'ELZSYB01' else False
SLOT_BCA = _ConfigParser.get_set_value('BCA', 'sam^slot', '---')


def bca_topup_online_validation():
    if '-' in MID_TOPUP_BCA:
        return False
    if not MID_TOPUP_BCA.isdigit():
        return False
    if '-' in TID_TOPUP_BCA:
        return False
    if len(MID_TOPUP_BCA) != 9:
        return False
    if len(TID_TOPUP_BCA) != 8:
        return False
    if TID_TOPUP_BCA[0] != 'E':
        return False
    return True


BCA_TOPUP_ONLINE = False

MID_TOPUP_ONLINE_DKI = _ConfigParser.get_set_value('DKI', 'mid^topup', '---')
TID_TOPUP_ONLINE_DKI = _ConfigParser.get_set_value('DKI', 'tid^topup', '---')
MID_DKI = _ConfigParser.get_set_value('DKI', 'mid', '---')
TID_DKI = _ConfigParser.get_set_value('DKI', 'tid', '---')

LAST_DKI_STAN = _ConfigParser.get_set_value('TEMPORARY', 'dki^last^topup^stan', '121')
LAST_DKI_INVOICE_NO = _ConfigParser.get_set_value('TEMPORARY', 'dki^last^topup^invoice', '61')
# DKI_TOPUP_ONLINE_BY_SERVICE = True if (_ConfigParser.get_set_value('DKI', 'service^library', '0') == '1') else False
# Disable DKI Topup Using Old Service Library
DKI_TOPUP_ONLINE_BY_SERVICE = False
_ConfigParser.set_value('DKI', 'service^library', '0')
DKI_TOPUP_ONLINE = True if MID_TOPUP_ONLINE_DKI != '---' else False


C2C_MODE = True if _ConfigParser.get_set_value('MANDIRI_C2C', 'mode', '0') == '1' else False
C2C_MACTROS = _ConfigParser.get_set_value('MANDIRI_C2C', 'mactros', '0000000000000000')
C2C_MID = _ConfigParser.get_set_value('MANDIRI_C2C', 'mid', '---')
C2C_TID = _ConfigParser.get_set_value('MANDIRI_C2C', 'tid', '---')
C2C_SAM_PIN = _ConfigParser.get_set_value('MANDIRI_C2C', 'sam^pin', '---')
C2C_SAM_SLOT = _ConfigParser.get_set_value('MANDIRI_C2C', 'sam^slot', '1')
C2C_THRESHOLD = int(_ConfigParser.get_set_value('MANDIRI_C2C', 'minimum^amount', '1000'))
C2C_TOPUP_AMOUNT = _ConfigParser.get_set_value('MANDIRI_C2C', 'amount^topup', '100000')
C2C_DEPOSIT_NO = _ConfigParser.get_set_value('TEMPORARY', 'c2c^card^no', '6032000000000000')
C2C_DEPOSIT_UID = _ConfigParser.get_set_value('TEMPORARY', 'c2c^card^uid', '---')
C2C_DEPOSIT_SLOT = _ConfigParser.get_set_value('MANDIRI_C2C', 'deposit^slot', '2')
C2C_DEPOSIT_UPDATE_LOOP = int(_ConfigParser.get_set_value('MANDIRI_C2C', 'deposit^update^loop', '300'))
C2C_DEPOSIT_UPDATE_MAX_LOOP = int(_ConfigParser.get_set_value('MANDIRI_C2C', 'deposit^update^max^loop', '10'))
# Must Be Set From Process Update Fee C2C [OLD, NEW]
C2C_ADMIN_FEE = [1500, 1500]
MDR_C2C_TRESHOLD_USAGE = True if _ConfigParser.get_set_value('MANDIRI_C2C', 'treshold^usage', '0') == '1' else False

# GENERATE INFO
INFOS = [
    'Please Remove [TERMINAL] Option If Still Exist',
    'Please Remove [QPROX] Option If Still Exist'
    'Please Remove [TEMPORARY] Option If Still Exist',
    'Please Remove [GRG] Option If Still Exist',
    '[GENERAL]-allowed^ubal^online -> Define Default Bank Which Allowed Update Balance Online',
    '[GENERAL]-mode -> Define Application Repository Mode live or develop',
    '[GENERAL]-mandiri^sam^production -> When Using Develop Mode For Testing, But Keep Using Mandiri KA Deposit Production',
    '[GENERAL]-refund^feature -> Disable Refund Feature And Set Default To Whatsapp',
    '[BILL]-type -> Define Type Of Bill Acceptor Which is used NV or GRG',
    '[BILL]-not^allowed^denom -> Define Not Allowed Notes/Denom',
    '[BILL]-store^money^delay -> Define Delay Waiting Time in second For Each Notes Storing',
    '[BILL]-service^library -> Define Library To Handle NV Bill Acceptor 1(MDDTopupService) or 0(NV200)',
    '[MANDIRI]-daily^settle^time -> Define Specific Time For Mandiri Deposit KA Auto Settlement',
    '[BRI]-procode -> The Merchant Agreement Code, For Purchase Settlement Purpose',
    '[MANDIRI_C2C]-mactros -> TID+MID Purchase Padded with 0, Total Must Be 16 Chars',
    '[MANDIRI_C2C]-amount^topup -> Nominal Topup Amount For C2C Deposit. Set Maximum to 90 Procentagep of Card Max. Limit',
    '[MANDIRI_C2C]-minimum^amount -> Deposit Treshold To Do Auto-Settlement/Reload Balance',
    '[MANDIRI_C2C]-c2c^path^settlement -> Define Host Path To Put Settlement File',
    '[MANDIRI_C2C]-c2c^path^fee -> Define Host Path To Put Settlement Fee File',
    '[MANDIRI_C2C]-c2c^path^resp^fee ->  Define Host Path To Get Response Settlement Fee File',
    '[MANDIRI_C2C]-sam^slot ->  Mandiri SAM Actual Slot in Reader',
    '[MANDIRI_C2C]-deposit^slot ->  C2C Deposit Actual Slot in Reader',
    '[MANDIRI_C2C]-deposit^update^loop ->  C2C Deposit Update Loop in Seconds',
    '[MANDIRI_C2C]-deposit^update^max^loop ->  C2C Deposit Maximum Loop Attempt Per Event Update',
    '[EDC]-type -> Define EDC Type UPT-IUR/MOBILE-ANDROID',
    '[EDC]-serial^no -> Define Serial No of Mobile Android EDC',
] 


# Disable This Unised Info (never Read) On Setting.ini
# for i in range(len(INFOS)):
#     _ConfigParser.set_value('INFO', str(i+1), INFOS[i])


VERSION = open(os.path.join(os.getcwd(), 'kiosk.ver'), 'r').read().strip()

KIOSK_NAME = "---"
KIOSK_STATUS = 'ONLINE'
KIOSK_REAL_STATUS = 'ONLINE'
KIOSK_SETTING = []
KIOSK_MARGIN = 3
KIOSK_ADMIN = 1500
PRINTER_STATUS = "NORMAL"
PAYMENT_CANCEL = _ConfigParser.get_set_value('GENERAL', 'payment^cancel', '1')
EXCEED_PAYMENT = _ConfigParser.get_set_value('GENERAL', 'exceed^payment', '0')
ALLOW_EXCEED_PAYMENT = True if EXCEED_PAYMENT == '1' else False
PAYMENT_CONFIRM = _ConfigParser.get_set_value('GENERAL', 'payment^confirm', '0')
SSL_VERIFY = True if _ConfigParser.get_set_value('GENERAL', 'ssl^verify', '0') == '1' else False

DISABLE_SENTRY_LOGGING = True if _ConfigParser.get_set_value('GENERAL', 'disable^sentry^logging', '1') == '1' else False
# NEW_TOPUP_FAILURE_HANDLER = True if _ConfigParser.get_set_value('GENERAL', 'new^topup^failure^handler', '1') == '1' else False
NEW_TOPUP_FAILURE_HANDLER = True

TEMP_FOLDER = sys.path[0] + '/_tTmp/'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Handling Update Balance Online From Defined Bank Name
UPDATE_ONLINE_FEATURE = _ConfigParser.get_set_value('GENERAL', 'allowed^ubal^online', 'MANDIRI|BNI|BRI')
ALLOWED_BANK_UBAL_ONLINE = UPDATE_ONLINE_FEATURE.split('|')

# Hardcoded Config For Bank Feature
ALLOWED_BANK_PENDING_ONLINE = ['BRI', 'MANDIRI', 'MANDIRI_C2C_DEPOSIT', 'BCA', 'DKI']
# CONFIG_ALLOWED_BANK_CHECK_CARD_LOG = _ConfigParser.get_set_value('GENERAL', 'allowed^card^history', 'MANDIRI|BNI')
CONFIG_ALLOWED_BANK_CHECK_CARD_LOG = 'MANDIRI|BNI|BRI|DKI'
ALLOWED_BANK_CHECK_CARD_LOG = CONFIG_ALLOWED_BANK_CHECK_CARD_LOG.split('|')

MANDIRI_FORCE_PRODUCTION_SAM = True if _ConfigParser.get_set_value('GENERAL', 'mandiri^sam^production', '0') == '1' else False
MANDIRI_CLOSE_TOPUP_BIN_RANGE = _ConfigParser.get_set_value('MANDIRI_C2C', 'blocked^bin^card', '6032984098').split('|')

LAST_INSERT_CASH_TIMESTAMP = None

JOB_PATH = os.path.join(sys.path[0], '_jJob')
if not os.path.exists(JOB_PATH):
    os.makedirs(JOB_PATH)

CASHBOX_PATH = os.path.join(sys.path[0], '_cCashbox')
if not os.path.exists(CASHBOX_PATH):
    os.makedirs(CASHBOX_PATH)

REDEEM_PATH = os.path.join(sys.path[0], '_rRedeem')
if not os.path.exists(REDEEM_PATH):
    os.makedirs(REDEEM_PATH)
    
STOCK_OPNAME_PATH = os.path.join(sys.path[0], '_sStockOpname')
if not os.path.exists(STOCK_OPNAME_PATH):
    os.makedirs(STOCK_OPNAME_PATH)
    

def first_do_card_opname():
    files = [x for x in os.listdir(STOCK_OPNAME_PATH) if x.endswith('.stock')] 
    return len(files) == 0


def store_redeem_activity(voucher, slot):
    try:
        redeem_status_file = os.path.join(REDEEM_PATH, 'redeem.status')
        LOGGER.info((redeem_status_file, voucher, slot))
        with open(redeem_status_file, 'a') as c:
            c.write(','.join([_Helper.time_string(), voucher, slot]) + os.linesep)
            c.close()
        return True
    except Exception as e:
        LOGGER.warning((e))
        return False


def archive_redeem_activity(backup_file):
    redeem_status_file = os.path.join(REDEEM_PATH, 'redeem.status')
    if not os.path.exists(redeem_status_file):
        LOGGER.warning(('REDEEM_STATUS_FILE_NOT_FOUND', REDEEM_PATH))
        return False
    backup_file = os.path.join(REDEEM_PATH, backup_file)
    os.rename(redeem_status_file, backup_file)
    LOGGER.info(('BACKUP_REDEEM_ACTIVITY', redeem_status_file, backup_file))
    with open(redeem_status_file, 'w') as c:
        LOGGER.info(('REINIT_REDEEM_ACTIVITY', redeem_status_file))
        pass
    return True


def get_redeem_activity(keyword=None, trx_output=False):
    output = {
        'total': 0,
        'slots': [],
        'summary': {},
        'voucher_list': []
    }
    try:
        redeem_status_file = os.path.join(REDEEM_PATH, 'redeem.status')
        if not os.path.exists(redeem_status_file):
            LOGGER.warning(('REDEEM_STATUS_FILE_NOT_FOUND', str(redeem_status_file)))
            return output 
        redeem_status = open(redeem_status_file, 'r').readlines()
        if len(redeem_status) == 0:
            LOGGER.warning(('REDEEM_STATUS_NOT_FOUND', str(redeem_status)))
            return output
        # LOGGER.debug((cash_status))
        output['total'] = len(redeem_status)
        all_slots = []
        for data in redeem_status:
            row = data.rstrip()
            rows = row.split(',')
            if len(rows) >= 2:
                trx_type = rows[1]
                if trx_output is True:
                    if trx_type not in output['voucher_list']:
                        output['voucher_list'].append(trx_type)
                slots = rows[2]
                if keyword is None:
                    all_slots.append(slots)
                    if slots not in output['slots']:
                        output['slots'].append(slots)
                else:
                    output['keyword'] = keyword
                    if keyword in trx_type:
                        all_slots.append(slots)
                        if slots not in output['slots']:
                            output['slots'].append(slots)
                    # LOGGER.debug((row, slots, output['slots']))
        summary = {}
        for n in output['slots']:
            # summary[n] = all_slots.count(n)
            summary.update({n:all_slots.count(n)})
            # LOGGER.debug((n, summary[n]))
        # sorted_summary = {k : summary[k] for k in sorted(summary) if int(k) < 100000}
        output['summary'] = summary
        LOGGER.info(('REDEEM_STATUS', str(output)))
    except Exception as e:
        LOGGER.warning((e))
    finally:
        return output


def store_notes_activity(notes, trxid):
    global LAST_INSERT_CASH_TIMESTAMP
    try:
        cash_status_file = os.path.join(CASHBOX_PATH, 'cashbox.status')
        LOGGER.info((cash_status_file, trxid, notes))
        with open(cash_status_file, 'a') as c:
            c.write(','.join([_Helper.time_string(), trxid, notes]) + os.linesep)
            c.close()
        LAST_INSERT_CASH_TIMESTAMP = _Helper.time_string(f='%Y%m%d%H%M%S')
        return True
    except Exception as e:
        LOGGER.warning((e))
        return False


def store_bulk_notes_activity(rows=[]):
    if len(rows) == 0:
        LOGGER.warning(('NO_DATA_FOUND'))
        return
    cash_status_file = os.path.join(CASHBOX_PATH, 'cashbox.status')
    # LOGGER.info((cash_status_file, trxid, notes))
    with open(cash_status_file, 'a') as c:
        for row in rows:
            c.write(row + os.linesep)
        c.close()
    

def init_cash_activity():
    cash_activity = get_cash_activity()['total']
    cash_trx = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__']
    if cash_activity == 0 and cash_trx > 0:
        LOGGER.info(('START INITIATING CASH ACTIVITY', cash_activity, cash_trx))
        rows = _DAO.custom_query(" SELECT DATETIME(ROUND(createdAt / 1000), 'unixepoch') as date, pid as trxid, amount as note FROM Cash WHERE collectedAt is null ")
        init_data = []
        total_amount = 0
        for row in rows:
            total_amount += int(row['note'])
            init_data.append(",".join([str(row['date']), str(row['trxid']), str(row['note'])]))
            # init_data.append(",".join(row.values()))
        LOGGER.info(('TOTAL INITIATING CASH DATA', len(init_data), total_amount))
        store_bulk_notes_activity(init_data)
    else:
        LOGGER.info(('CASH ACTIVITY ALREADY EXIST', cash_activity, cash_trx))


def get_cash_activity(keyword=None, trx_output=False):
    output = {
        'total': 0,
        'notes': [],
        'summary': {},
        'trx_list': []
    }
    try:
        cash_status_file = os.path.join(CASHBOX_PATH, 'cashbox.status')
        if not os.path.exists(cash_status_file):
            with open(cash_status_file, 'w+') as c:
                c.close()
        cash_status = open(cash_status_file, 'r').readlines()
        if len(cash_status) == 0:
            LOGGER.warning(('CASH_STATUS_NOT_FOUND', str(cash_status)))
            return output
        # LOGGER.debug((cash_status))
        all_notes = []
        for data in cash_status:
            row = data.rstrip()
            rows = row.split(',')
            if len(rows) >= 2:
                trx_type = rows[1]
                if trx_output is True:
                    if trx_type not in output['trx_list']:
                        output['trx_list'].append(trx_type)
                notes = rows[2]
                if keyword is None:
                    all_notes.append(notes)
                    if digit_in(notes) is True:
                        output['total'] += int(notes)
                    if notes not in output['notes']:
                        output['notes'].append(notes)
                else:
                    output['keyword'] = keyword
                    if keyword in trx_type:
                        all_notes.append(notes)
                        if digit_in(notes) is True:
                            output['total'] += int(notes)
                        if notes not in output['notes']:
                            output['notes'].append(notes)
                    # LOGGER.debug((row, notes, output['notes']))
        summary = {}
        for n in output['notes']:
            # summary[n] = all_notes.count(n)
            summary.update({n:all_notes.count(n)})
            # LOGGER.debug((n, summary[n]))
        # sorted_summary = {k : summary[k] for k in sorted(summary) if int(k) < 100000}
        # Manual Add Denom 100.000 In Last Order
        # if summary.get('100000', 0) > 0:
            # sorted_summary.update({'100000': summary.get('100000', 0)})
        output['summary'] = summary
        LOGGER.info(('CASH_STATUS', str(output)))
    except Exception as e:
        LOGGER.warning((e))
    finally:
        return output
    

def backup_cash_activity(collection_file):
    cash_status_file = os.path.join(CASHBOX_PATH, 'cashbox.status')
    if not os.path.exists(cash_status_file):
        LOGGER.warning(('CASH_STATUS_FILE_NOT_FOUND', CASHBOX_PATH))
        return False
    # collection_file = cash_status_file.replace('status', collection_id)
    collection_file = os.path.join(CASHBOX_PATH, collection_file)
    os.rename(cash_status_file, collection_file)
    LOGGER.info(('BACKUP_CASH_ACTIVITY', cash_status_file, collection_file))
    return True


def init_temp_data():
    global TEMP_FOLDER
    if not os.path.exists(sys.path[0] + '/_tTmp/'):
        os.makedirs(sys.path[0] + '/_tTmp/')
    TEMP_FOLDER = sys.path[0] + '/_tTmp/'


def store_to_temp_data(temp, content, log=True):
    if log is True:
        LOGGER.info((temp, content))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_path = os.path.join(TEMP_FOLDER, temp)
    if type(content) != str:
        content = json.dumps(content)
    if len(clean_white_space(content)) == 0:
        content = '{}'
    with open(temp_path, 'w+') as t:
        t.write(content)
        t.close()
        

def store_stock_opname(key, content):
    LOGGER.info((key, content))
    if '.stock' not in key:
        key = key + '.stock'
    key_path = os.path.join(STOCK_OPNAME_PATH, key)
    if len(clean_white_space(content)) == 0:
        content = '[]'
    with open(key_path, 'w+') as t:
        t.write(content)
        t.close()
    

def load_stock_opname(key):
    LOGGER.info((key))
    if '.stock' not in key:
        key = key + '.stock'
    key_path = os.path.join(STOCK_OPNAME_PATH, key)
    if not os.path.exists(key_path):
        with open(key_path, 'w+') as t:
            t.write('[]')
            t.close()
    content = open(key_path, 'r').read().strip()
    return json.loads(content)


def remove_temp_data(temp):
    LOGGER.info((temp))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_file = os.path.join(TEMP_FOLDER, temp)
    if os.path.isfile(temp_file):
        os.remove(temp_file)


def exist_temp_data(temp):
    LOGGER.info((temp))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_file = os.path.join(TEMP_FOLDER, temp)
    if os.path.isfile(temp_file):
        return True
    return False


def load_from_temp_data(temp, mode='text', force_path=None):
    LOGGER.info((temp))
    if '.data' not in temp:
        temp = temp + '.data'
    temp_path = os.path.join(TEMP_FOLDER, temp)
    if force_path is not None:
        temp_path = os.path.join(force_path, temp)
    if not os.path.exists(temp_path):
        with open(temp_path, 'w+') as t:
            if mode == 'json':
                t.write('{}')
            else:
                t.write(' ')
            t.close()
    content = open(temp_path, 'r').read().strip()
    if len(clean_white_space(content)) == 0:
        os.remove(temp_path)
        store_to_temp_data(temp_path, '{}')
        content = '{}'
    if mode == 'json':
        return json.loads(content)
    return content


TOPUP_AMOUNT_SETTING = load_from_temp_data('topup-amount-setting', 'json')
FEATURE_SETTING = load_from_temp_data('feature-setting', 'json')
PAYMENT_SETTING = load_from_temp_data('payment-setting', 'json')
REFUND_SETTING = load_from_temp_data('refund-setting', 'json')
THEME_SETTING = load_from_temp_data('theme-setting', 'json')
ADS_SETTING = load_from_temp_data('ads-setting', 'json')

VIEW_CONFIG = load_from_temp_data('view-config', 'json')
TJ_VIEW_CONFIG = load_from_temp_data('tj-view-config', 'json', sys.path[0] + '/_cConfig/')
KAI_VIEW_CONFIG = load_from_temp_data('kci-view-config', 'json', sys.path[0] + '/_cConfig/')

THEME_NAME = _ConfigParser.get_set_value('TEMPORARY', 'theme^name', '---')
# Handle External Customer Service Information
EXT_CS_INFO = None

PRINTER_TYPE = _ConfigParser.get_set_value('PRINTER', 'printer^type', 'Default')
ERECEIPT_URL = _ConfigParser.get_set_value('PRINTER', 'ereceipt^url', 'http://erg.elebox.id/ereceipt/create')
ERECEIPT_ASYNC_MODE = True if _ConfigParser.get_set_value('PRINTER', 'ereceipt^async^mode', '1') == '1' else False
ERECEIPT_QR_HOST = _ConfigParser.get_set_value('PRINTER', 'ereceipt^qr^host', 'http://apiv2.mdd.co.id:2020/')


# Re-write view config if missing
if len(VIEW_CONFIG.keys()) == 0:
    if THEME_NAME.lower() == 'transjakarta':
        VIEW_CONFIG = TJ_VIEW_CONFIG
    if THEME_NAME.lower() in ['kai', 'kci']:
        VIEW_CONFIG = KAI_VIEW_CONFIG
        
VIEW_CONFIG['ui_simplify'] =  True if _ConfigParser.get_set_value('GENERAL', 'ui^simplify', '1') == '1' else False
VIEW_CONFIG['page_timer'] =  int(_ConfigParser.get_set_value('GENERAL', 'page^timer', '90'))
VIEW_CONFIG['tnc_timer'] =  int(_ConfigParser.get_set_value('GENERAL', 'tnc^timer', '4'))
VIEW_CONFIG['success_page_timer'] =  int(_ConfigParser.get_set_value('GENERAL', 'success^page^timer', '7'))
VIEW_CONFIG['failure_page_timer'] =  int(_ConfigParser.get_set_value('GENERAL', 'failure^page^timer', '5'))
VIEW_CONFIG['promo_check'] =  True if _ConfigParser.get_set_value('GENERAL', 'promo^check', '0') == '1' else False
VIEW_CONFIG['host_qr_generator'] =  _ConfigParser.get_set_value('GENERAL', 'host^qr^generator', '---')
VIEW_CONFIG['disable_print_on_cancel'] = True if _ConfigParser.get_set_value('EDC', 'disable^print^on^cancel', '1') == '1' else False
VIEW_CONFIG['ping_interval'] =  int(_ConfigParser.get_set_value('GENERAL', 'ping^interval', '3'))
VIEW_CONFIG['single_denom_trx'] =  BILL_SINGLE_DENOM_TRX
VIEW_CONFIG['single_denom_type'] =  BILL_SINGLE_DENOM_TYPE
VIEW_CONFIG['support_multimedia'] = support_multimedia()
VIEW_CONFIG['payment_cancel'] = True if PAYMENT_CANCEL == '1' else False
VIEW_CONFIG['theme_name'] = THEME_NAME
VIEW_CONFIG['printer_type'] = PRINTER_TYPE

THEME_WA_NO = _ConfigParser.get_set_value('TEMPORARY', 'theme^wa^no', '---')
THEME_WA_QR = _ConfigParser.get_set_value('TEMPORARY', 'theme^wa^url', '---')

MAX_PENDING_CODE_RETRY = int(_ConfigParser.get_set_value('TEMPORARY', 'max^pending^code^retry', '7'))
MAX_PENDING_CODE_DURATION = int(_ConfigParser.get_set_value('TEMPORARY', 'max^pending^code^duration', '2'))
CUSTOMER_SERVICE_NO = _ConfigParser.get_set_value('TEMPORARY', 'customer^service^no', '082124999951')

REPO_USERNAME = _ConfigParser.get_set_value('REPOSITORY', 'username', 'developer')
REPO_PASSWORD = _ConfigParser.get_set_value('REPOSITORY', 'password', 'Mdd*123#')
SERVICE_VERSION = _ConfigParser.get_set_value('TEMPORARY', 'service^version', '---')
COLOR_TEXT = _ConfigParser.get_set_value('TEMPORARY', 'color^text', 'white')
COLOR_BACK = _ConfigParser.get_set_value('TEMPORARY', 'color^back', 'black')

UPDATE_BALANCE_URL_DEV = 'http://192.168.8.60:28194/v1/'
UPDATE_BALANCE_URL = _ConfigParser.get_set_value('GENERAL', 'update^balance^url', 'http://apiv2.mdd.co.id:2020/v1/')

QR_HOST = _ConfigParser.get_set_value('QR', 'qr^host', 'http://apiv2.mdd.co.id:10107/v1/')
QR_TOKEN = _ConfigParser.get_set_value('QR', 'qr^token', 'e6f092a0fa88d9cac8dac3d2162f1450')
QR_MID = _ConfigParser.get_set_value('QR', 'qr^mid', '000972721511382bf739669cce165808')
QRIS_RECEIPT = _ConfigParser.get_set_value('QR', 'qris^receipt', 'BCA-QRIS|DUWIT').split('|')
GENERAL_QR = True if _ConfigParser.get_set_value('QR', 'general^qr', '1') == '1' else False

CORE_HOST = QR_HOST
CORE_TOKEN = QR_TOKEN
CORE_MID = QR_MID
EDC_ECR_URL = 'https://edc-ecr.mdd.co.id/voldemort-'+CORE_MID 

API_HOST = CORE_HOST.replace('v1/', 'ping')


if PTR_MODE:
    EDC_ECR_URL = 'http://edc-ecr.mdd.co.id/voldemort-'+CORE_MID 


# STORE_QR_TO_LOCAL = True if _ConfigParser.get_set_value('QR', 'store^local', '1') == '1' else False
# Force Stop QR Local Store Due To Mismatch Sys Path - 2022-08-07
STORE_QR_TO_LOCAL = False

QR_PAYMENT_TIME = int(_ConfigParser.get_set_value('QR', 'payment^time', '300'))
QR_STORE_PATH = os.path.join(sys.path[0], '_qQr')
if not os.path.exists(QR_STORE_PATH):
    os.makedirs(QR_STORE_PATH)


QR_NON_DIRECT_PAY = ['GOPAY', 'DANA', 'LINKAJA', 'SHOPEEPAY', 'JAKONE', 'BCA-QRIS', 'BNI-QRIS', 'DUWIT']
QR_DIRECT_PAY = ['OVO']
ALL_QR_PROVIDER = QR_DIRECT_PAY + QR_NON_DIRECT_PAY
# Hardcoded Env Status
QR_PROD_STATE = {
    'BNI-QRIS': True,
    'DUWIT': False,
    'BCA-QRIS': False,
    'JAKONE': True,
    'GOPAY': True,
    'DANA': True,
    'LINKAJA': True,
    'SHOPEEPAY': True,
    'OVO': True,
}

ENDPOINT_SUCCESS_BY_200_HTTP_HEADER = [
    'settlement/submit', 
    'refund/global',
    'cancel-payment',
    'do-settlement',
    'ereceipt/create',
    'topup-dki/reversal',
    'topup-dki/confirm',
    'topup-bni/confirm',
    'topup-bca/confirm',
    'topup-bca/reversal',
    'topup-bri/confirm',
    'topup-bri/reversal',
    ]

ENDPOINT_SUCCESS_BY_ANY_HTTP_HEADER = [
    'cancel-payment',
    ]


def serialize_payload(data, specification='MDD_CORE_API'):
    if specification == 'MDD_CORE_API':
        data['token'] = CORE_TOKEN
        data['mid'] = CORE_MID
        data['tid'] = TID
        if 'trx_id' in data.keys() and '-' not in data['trx_id']:
            data['trx_id'] = data['trx_id'] + '-' + TID
        # _Helper.dump(data)
    return data


def get_service_version():
    global SERVICE_VERSION
    ___stat = -1
    ___resp = None
    try:
        # sleep(3)
        ___stat, ___resp = _HTTPAccess.get_local(SERVICE_URL + '999&param=0')
        if ___stat == 200:
            SERVICE_VERSION = ___resp['Response']
            log_to_temp_config('service^version', SERVICE_VERSION)
    except Exception as e:
        LOGGER.warning((___stat, ___resp, e))
    finally:
        return SERVICE_VERSION


BNI_ACTIVE_WALLET = 0

CD_PORT_LIST = {
    '101': CD_PORT1,
    '102': CD_PORT2,
    '103': CD_PORT3,
    '104': CD_PORT4,
    '105': CD_PORT5,
    '106': CD_PORT6,
}

BID = {
    'MANDIRI': '1',
    'BNI': '2',
    'BRI': '3',
    'BCA': '4'
}

# Harcoded Setting
ADJUST_AMOUNT_MINIMUM = 0
TRIGGER_MANUAL_TOPUP = True
ALLOW_DO_TOPUP = True
EDC_SETTLEMENT_RUNNING = False

SERVICE_URL = 'http://localhost:9000/Service/GET?type=json&cmd='
FLASK_URL = 'http://localhost:5000/send_command?cmd='
TOPUP_SERVICE_ENABLE = True if _ConfigParser.get_set_value('GENERAL', 'topup^service', '0') == '1' else False

LAST_AUTH = int(_ConfigParser.get_set_value('TEMPORARY', 'last^auth', '0'))
LAST_UPDATE = int(_ConfigParser.get_set_value('TEMPORARY', 'last^update', '0'))
LAST_GET_PPOB = int(_ConfigParser.get_set_value('TEMPORARY', 'last^get^ppob', '0'))
LAST_C2C_SET_FEE = int(_ConfigParser.get_set_value('TEMPORARY', 'last^c2c^set^fee', '0'))


def mandiri_sam_status():
    if not C2C_MODE:
        if '---' not in MID_MAN and len(MID_MAN) > 3:
            return True
        else:
            return False
    else:
        if '---' in C2C_MID:
            _ConfigParser.set_value('MANDIRI_C2C', 'mode', '0')
            return False
        if '---' in C2C_TID:
            _ConfigParser.set_value('MANDIRI_C2C', 'mode', '0')
            return False
        return C2C_MODE


BANKS = [{
    "BANK": "MANDIRI",
    "TOPUP_CHANNEL": "OFFLINE",
    "STATUS": mandiri_sam_status(),
    "MID": C2C_MID if C2C_MODE is True else MID_MAN,
    "TID": C2C_TID if C2C_MODE is True else TID_MAN,
    "SAM": C2C_SAM_PIN if C2C_MODE is True else SAM_MAN,
}, {
    "BANK": "BNI",
    "TOPUP_CHANNEL": "OFFLINE",
    "STATUS": True if ('---' not in MID_BNI and len(MID_BNI) > 3) else False,
    "MID": MID_BNI,
    "TID": TID_BNI,
    "MC": MC_BNI,
    "SAM1": SLOT_SAM1_BNI,
    "SAM2": SLOT_SAM2_BNI,
    "MIN_AMOUNT": BNI_THRESHOLD,
    "DEFAULT_TOPUP": BNI_TOPUP_AMOUNT
}, {
    "BANK": "BRI",
    "TOPUP_CHANNEL": "ONLINE",
    "STATUS": True if ('---' not in MID_BRI and len(MID_BRI) > 3) else False,
    "MID": MID_BRI,
    "TID": TID_BRI,
    "PROCODE": PROCODE_BRI
}, {
    "BANK": "BCA",
    "TOPUP_CHANNEL": "ONLINE",
    "STATUS": True if ('---' not in MID_BCA and len(MID_BCA) > 3) else False,
    "MID": MID_BCA,
    "TID": TID_BCA,
}, {
    "BANK": "DKI",
    "TOPUP_CHANNEL": "ONLINE",
    "STATUS": True if ('---' not in TID_DKI and len(MID_DKI) > 3) else False,
    "MID": MID_DKI,
    "TID": TID_DKI,
}]


TOPUP_ONLINE_BANK = [b for b in BANKS if b['TOPUP_CHANNEL'] == 'ONLINE']

SFTP_MANDIRI = {
    'status': True,
    'host': _ConfigParser.get_set_value('SFTP', 'mdr^host', '103.28.14.188'),
    'user': _ConfigParser.get_set_value('SFTP', 'mdr^user', 'tj-kiosk'),
    'pass': _ConfigParser.get_set_value('SFTP', 'mdr^pass', 'tj-kiosk123'),
    'port': _ConfigParser.get_set_value('SFTP', 'mdr^port', '22222'),
    'path': _ConfigParser.get_set_value('SFTP', 'mdr^path', '/home/mdd/TopUpOffline'),
}

SFTP_BNI = {
    'status': True,
    'host': _ConfigParser.get_set_value('SFTP', 'bni^host', '103.28.14.188'),
    'user': _ConfigParser.get_set_value('SFTP', 'bni^user', 'tj-kiosk'),
    'pass': _ConfigParser.get_set_value('SFTP', 'bni^pass', 'tj-kiosk123'),
    'port': _ConfigParser.get_set_value('SFTP', 'bni^port', '22222'),
    'path': _ConfigParser.get_set_value('SFTP', 'bni^path', '/home/tj-kiosk/topup/bni/'),
}


C2C_PATH = _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^path', '/tb/')
SFTP_C2C = {
    'status': C2C_MODE,
    'host': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^host', '103.28.14.188'),
    'user': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^user', 'tbuser'),
    'pass': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^pass', 'tbuser*123'),
    'port': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^port', '22222'),
    'path': C2C_PATH,
    'path_settlement': C2C_PATH + _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^path^settlement', 'settlement_tb_dev'),
    'path_fee': C2C_PATH + _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^path^fee', 'fee_tb_dev'),
    'path_fee_response': C2C_PATH + _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^path^resp^fee', 'resp_fee_tb_dev'),
}

FTP_C2C = SFTP_C2C


FTP = {
    'status': False,
    'host': '---',
    'user': '---',
    'pass': '---',
    'port': '21',
    'path': ''

}

KA_PIN1 = _ConfigParser.get_set_value('MANDIRI', 'ka^pin1', '---')
KA_PIN2 = _ConfigParser.get_set_value('MANDIRI', 'ka^pin2', '---')
KL_PIN = _ConfigParser.get_set_value('MANDIRI', 'kl^pin', '---')
KA_NIK = _ConfigParser.get_set_value('MANDIRI', 'ka^nik', '2345')

MANDIRI_WALLET_1 = 0
MANDIRI_WALLET_2 = 0
MANDIRI_ACTIVE_WALLET = 0
MANDIRI_SAM_NO_1 = _ConfigParser.get_set_value('MANDIRI', 'sam1^uid', '---')
# Add assumption MANDIRI_SAM_NO_1 is C2C_DEPOSIT_NO When C2C_MODE is ON
if C2C_MODE is True:
    MANDIRI_SAM_NO_1 = C2C_DEPOSIT_NO
MANDIRI_SAM_NO_2 = _ConfigParser.get_set_value('MANDIRI', 'sam2^uid', '---')
MANDIRI_REVERSE_SLOT_MODE = False
MANDIRI_SINGLE_SAM = True if _ConfigParser.get_set_value('MANDIRI', 'single^sam', '1') == '1' else False
if MANDIRI_SINGLE_SAM is True:
    _ConfigParser.set_value('MANDIRI', 'active^slot', '1')
MANDIRI_ACTIVE = int(_ConfigParser.get_set_value('MANDIRI', 'active^slot', '1'))

BNI_SAM_1_WALLET = 0
BNI_SAM_2_WALLET = 0
BNI_SINGLE_SAM = True if _ConfigParser.get_set_value('BNI', 'single^sam', '1') == '1' else False
# if BNI_SINGLE_SAM is True:
#     _ConfigParser.set_value('BNI', 'active^slot', '2')
BNI_ACTIVE = int(_ConfigParser.get_set_value('BNI', 'active^slot', '1'))
BRI_WALLET = 0
BCA_WALLET = 0
DKI_WALLET = 0

BNI_SAM_1_NO = _ConfigParser.get_set_value('BNI', 'sam1^no', '---')
BNI_SAM_2_NO = _ConfigParser.get_set_value('BNI', 'sam2^no', '---')

EDC_ERROR = ''
NFC_ERROR = ''
BILL_ERROR = ''
PRINTER_ERROR = ''
SCANNER_ERROR = ''
WEBCAM_ERROR = ''

# Load From Temp Config Data
CD1_ERROR = load_from_temp_config('cd1^error')
CD2_ERROR = load_from_temp_config('cd2^error')
CD3_ERROR = load_from_temp_config('cd3^error')
CD4_ERROR = load_from_temp_config('cd4^error')
CD5_ERROR = load_from_temp_config('cd5^error')
CD6_ERROR = load_from_temp_config('cd6^error')


RECEIPT_PRINT_COUNT = int(_ConfigParser.get_set_value('PRINTER', 'receipt^print^count', '0'))
RECEIPT_PRINT_LIMIT = int(_ConfigParser.get_set_value('PRINTER', 'receipt^print^limit', '750'))
DELAY_MANUAL_PRINT = int(_ConfigParser.get_set_value('PRINTER', 'delay^manual^print', '10'))
if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT:
    PRINTER_ERROR = 'PAPER_ROLL_WARNING (' + str(RECEIPT_PRINT_COUNT) + ')'
    # PRINTER_STATUS = 'PAPER_ROLL_WARNING'
RECEIPT_LOGO = _ConfigParser.get_set_value('PRINTER', 'receipt^logo', 'mandiri_logo.gif')
CUSTOM_RECEIPT_TEXT = _ConfigParser.get_set_value('PRINTER', 'receipt^custom^text', '')

EDC_PRINT_ON_LAST = True if _ConfigParser.get_set_value('EDC', 'print^last', '1') == '1' else False
EDC_ANDROID_MODE = True if EDC_TYPE == 'MOBILE-ANDROID' else False
LAST_EDC_TRX_RECEIPT = None

LAST_READER_ERR_CODE = '0000'

LAST_BCA_ERR_CODE = ''
LAST_BCA_REFF_ID = ''

LAST_BCA_REVERSAL_RESULT = ''
LAST_DKI_ERR_CODE = ''
LAST_BRI_ERR_CODE = ''

LAST_PPOB_TRX = None

DISABLE_CARD_RETRY_CODE = True if _ConfigParser.get_set_value('GENERAL', 'disable^card^retry^code', '1') == '1' else False
DISABLE_SYNC_DEVICE_STATE = True if _ConfigParser.get_set_value('GENERAL', 'disable^sync^device^state', '1') == '1' else False

ALLOWED_SYNC_TASK = [
    'sync_product_data',
    # 'sync_pending_refund',
    'sync_task',
    'sync_settlement_bni',
    # 'sync_sam_audit',
    'sync_data_transaction_failure',
    'sync_data_transaction',
    'sync_topup_records',
    # 'sync_machine_status',
    # 'validate_update_balance_c2c'

]

def store_request_to_job(name='', url='', payload=''):
    if empty(name) is True or empty(url) is True or empty(payload) is True:
        print('pyt: Missing Parameter in Logging Request..! ' + _Helper.time_string() + ' : ' + _Helper.whoami())
        return
    filename = _Helper.time_string(f='%Y%m%d%H%M%S___') + name
    log = {
        'url'       : url,
        'payload'   : payload
    }
    LOGGER.debug((filename, str(log)))
    print('pyt: Logging Request..! ' + _Helper.time_string() + ' : ' + filename)
    log_to_file(content=log, path=JOB_PATH, filename=filename)



def store_upload_to_job(name='', host='', data=''):
    if empty(name) is True or empty(host) is True or empty(data) is True:
        print('pyt: Missing Parameter in Logging Upload..! ' + _Helper.time_string() + ' : ' + _Helper.whoami())
        return
    filename = _Helper.time_string(f='%Y%m%d%H%M%S___') + name
    log = {
        'host'      : host,
        'data'      : data
    }
    LOGGER.debug((filename, str(log)))
    print('pyt: Logging Upload..! ' + _Helper.time_string() + ' : ' + filename)
    log_to_file(content=log, path=JOB_PATH, filename=filename, default_ext='.upload')


def log_to_file(content='', path='', filename='', default_ext='.request'):
    if empty(content) is True or empty(filename) is True:
        print('pyt: Missing Parameter in Logging File..! ' + _Helper.time_string() + ' : ' + _Helper.whoami())
        return
    if empty(path) is True:
        path = TEMP_FOLDER
    if not os.path.exists(path):
        os.makedirs(path)
    if '.' not in filename:
        filename = filename + default_ext
    log_file = os.path.join(path, filename)
    if type(content) != str:
        content = json.dumps(content)
    with open(log_file, 'w+') as file_logging:
        print('pyt: Create Logging File..! ' + _Helper.time_string() + ' : ' + log_file)
        file_logging.write(content)
        file_logging.close()


# LAST_C2C_SET_FEE = int(_ConfigParser.get_set_value('TEMPORARY', 'last^c2c^set^fee', '0'))


def log_to_temp_config(section='last^auth', content=''):
    global LAST_AUTH, LAST_UPDATE, LAST_C2C_SET_FEE
    __timestamp = _Helper.now()
    if section == 'last^auth':
        LAST_AUTH = __timestamp
        content = str(__timestamp)
    elif section == 'last^update':
        LAST_UPDATE = __timestamp
        content = str(__timestamp)
    elif section == 'last^c2c^set^fee':
        LAST_C2C_SET_FEE = __timestamp
        content = str(__timestamp)
    else:
        content = str(content)
    log_to_config('TEMPORARY', section, content)
    

def load_from_custom_config(option='BILL', section='last^money^inserted', default=''):
    return _ConfigParser.get_set_value(option, section, default)


def update_receipt_count():
    global PRINTER_ERROR, RECEIPT_PRINT_COUNT
    RECEIPT_PRINT_COUNT = RECEIPT_PRINT_COUNT + 1
    log_to_config('PRINTER', 'receipt^print^count', str(RECEIPT_PRINT_COUNT))
    if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT:
        PRINTER_ERROR = 'PAPER_ROLL_WARNING (' + str(RECEIPT_PRINT_COUNT) + ')'


def start_reset_receipt_count(count):
    _Helper.get_thread().apply_async(reset_receipt_count, (count,))


def reset_paper_roll():
    return reset_receipt_count('0')


def reset_receipt_count(count):
    global PRINTER_ERROR, RECEIPT_PRINT_COUNT
    RECEIPT_PRINT_COUNT = int(count)
    log_to_config('PRINTER', 'receipt^print^count', str(RECEIPT_PRINT_COUNT))
    if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT:
        PRINTER_ERROR = 'PAPER_ROLL_WARNING (' + str(RECEIPT_PRINT_COUNT) + ')'
        return 'PAPER_ROLL_NOT_RESET'
    else:
        PRINTER_ERROR = ''
        return 'PAPER_ROLL_RESET'



def active_auth_session():
    if LAST_AUTH > 0:
        today = _Helper.today_time()
        current = (LAST_AUTH/1000)
        return True if (today+86400) > current else False
    else:
        return False


def last_update_attempt():
    if LAST_UPDATE > 0:
        today = _Helper.today_time()
        current = (LAST_UPDATE/1000)
        return True if (today+86400) > current else False
    else:
        return False


def mandiri_single_sam():
    return MANDIRI_SINGLE_SAM


def bni_single_sam():
    return BNI_SINGLE_SAM


def set_mandiri_uid(slot, uid):
    global MANDIRI_SAM_NO_1, MANDIRI_SAM_NO_2
    if slot == '1':
        MANDIRI_SAM_NO_1 = uid
        _ConfigParser.set_value('MANDIRI', 'sam1^uid', uid)
    if slot == '2':
        MANDIRI_SAM_NO_2 = uid
        _ConfigParser.set_value('MANDIRI', 'sam2^uid', uid)


def set_bni_sam_no(slot, no):
    global BNI_SAM_1_NO, BNI_SAM_2_NO
    if slot == '1':
        BNI_SAM_1_NO = no
        _ConfigParser.set_value('BNI', 'sam1^no', no)
    if slot == '2':
        BNI_SAM_2_NO = no
        _ConfigParser.set_value('BNI', 'sam2^no', no)


QPROX = {
    "port": QPROX_PORT,
    "status": True if QPROX_PORT is not None and digit_in(QPROX_PORT) is True else False,
    # "bank_config": BANKS
}

def get_edc_availability():
    if EDC_ANDROID_MODE is True:
        if EDC_SERIAL_NO == ('0'*16):
            return False
        return True
    elif EDC_PORT is not None and digit_in(EDC_PORT):
        return True
    else:
        return False


EDC = {
    "port": EDC_PORT,
    "type": EDC_TYPE,
    "sn": EDC_SERIAL_NO,
    "mobile": EDC_ANDROID_MODE,
    "status": get_edc_availability()
}
MEI = {
    "port": MEI_PORT,
    "status": True if MEI_PORT is not None and digit_in(MEI_PORT) is True else False
}
# BILL Device Type For GRG / NV / MEI
BILL = {
    "port": BILL_PORT,
    "type": BILL_TYPE,
    "status": True if BILL_PORT is not None and digit_in(BILL_PORT) is True else False
}

VIEW_CONFIG['bill_type'] = BILL_TYPE

# Handling MEI VS BILL Duplicate Port Activation
if BILL['status'] is True:
    MEI['status'] = False
    MEI_PORT = _ConfigParser.set_value('MEI', 'port', 'COM')
    MEI['port'] = MEI_PORT
    
CD = {
    "cd1": CD_PORT1,
    "cd2": CD_PORT2,
    "cd3": CD_PORT3,
    "cd4": CD_PORT4,
    "cd5": CD_PORT5,
    "cd6": CD_PORT6,
    "status": True,
    "list_port": CD_PORT_LIST
}

CD_READINESS = {
    "cd1": 'N/A',
    "cd2": 'N/A',
    "cd3": 'N/A',
    "cd4": 'N/A',
    "cd5": 'N/A',
    "cd6": 'N/A',
}

SMT_CONFIG = dict()

FW_BANK = {
    '0': 'MANDIRI',
    '8': 'MANDIRI', #New Applet Mandiri
    '1': 'BRI', #BRI JAVA
    '2': 'BRI', #BRI Desfire
    '3': 'BNI',
    '4': 'DKI',
    '5': 'BCA',
    '7': 'DKI'
}

CODE_BANK = {
    '1': 'MANDIRI',
    '2': 'BNI',
    '3': 'BRI',
    '4': 'BCA',
    '5': 'DKI',
    '6': 'MEGA',
    '7': 'NOBU',
    '8': 'BTN'
}

CODE_BANK_BY_NAME = dict((v, k) for k, v in CODE_BANK.items())

BRI_LOG_LEGEND = {
    'EB': 'PURCHASE', # Payment
    'EC': 'TOPUP', # Topup Online
    'EF': 'DEPOSIT', # Aktivasi Deposit
    'ED': 'VOID',
    '5F': 'REACTIVATE', #Reaktivasi
    'BE': 'No More Logs',
    'AF': 'Found Next Log' 
}

MANDIRI_LOG_LEGEND = {
    '1200': 'PURCHASE',
    '1500': 'TOPUP', #150
    '1000': 'TOPUP', #100
    '1100': 'TOPUP', #110
    '4352': 'TOPUP', #
    '4608': 'PURCHASE'
}
# Actual From Mandiri
# 0100 -> TOPUP
# 0110 -> TOPUP
# 0150 -> TOPUP
# 0120 -> SALE

BNI_LOG_LEGEND = {
    '01': 'PURCHASE',
    '06': 'TOPUP',
    '04': 'DIRECT TOPUP'
}

DKI_LOG_LEGEND = {
    '05': 'PURCHASE',
    '01': 'PURCHASE',
    '02': 'TOPUP'
}

def start_get_devices():
    _Helper.get_thread().apply_async(get_devices)


def get_devices():
    # LOGGER.info(('[INFO] get_devices', DEVICES))
    return {"QPROX": QPROX, "EDC": EDC, "MEI": MEI, "CD": CD, "BILL": BILL}


def start_get_printer_status():
    _Helper.get_thread().apply_async(get_printer_status)


def get_printer_status():
    # LOGGER.info(('[INFO] get_devices', DEVICES))
    return 'WARNING' if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT else 'OK'


def get_payments():
    # EDC : Still Need To Enable EDC From Backend Dashboard
    return {
        "QPROX": "AVAILABLE" if QPROX["status"] is True else "NOT_AVAILABLE",
        "EDC": "AVAILABLE" if (EDC["status"] is True and check_payment('card') is True) else "NOT_AVAILABLE",
        "CD": "AVAILABLE" if CD["status"] is True else "NOT_AVAILABLE",
        "MEI": "AVAILABLE" if (MEI["status"] is True and check_payment('cash') is True) else "NOT_AVAILABLE",
        "BILL": check_bill_status(),
        "QR_OVO": "AVAILABLE" if check_payment('ovo') is True else "NOT_AVAILABLE",
        "QR_DANA": "AVAILABLE" if check_payment('dana') is True else "NOT_AVAILABLE",
        "QR_GOPAY": "AVAILABLE" if check_payment('gopay') is True else "NOT_AVAILABLE",
        "QR_DUWIT": "AVAILABLE" if check_payment('duwit') is True else "NOT_AVAILABLE",
        "QR_LINKAJA": "AVAILABLE" if check_payment('linkaja') is True else "NOT_AVAILABLE",
        "QR_SHOPEEPAY": "AVAILABLE" if check_payment('shopeepay') is True else "NOT_AVAILABLE",
        "QR_JAKONE": "AVAILABLE" if check_payment('jakone') is True else "NOT_AVAILABLE",
        "QR_BCA": "AVAILABLE" if check_payment('bca-qris') is True else "NOT_AVAILABLE",
        "QR_BNI": "AVAILABLE" if check_payment('bni-qris') is True else "NOT_AVAILABLE",
        "PRINTER_STATUS": get_printer_status()
    }
    

def check_bill_status():
    last_status_bill = load_from_custom_config('BILL', 'last^money^inserted')
    if last_status_bill == 'FULL':
        return 'CASHBOX_FULL'
    if BILL["status"] is not True:
        return 'NOT_AVAILABLE'
    if check_payment('cash') is not True:
        return 'NOT_AVAILABLE'
    return 'AVAILABLE'


def get_refunds():
    if len(REFUND_SETTING) == 0 or empty(REFUND_SETTING) is True:
        return {
            "MANUAL": "AVAILABLE",
            "DIVA": "AVAILABLE",
            "CS": "AVAILABLE",
            "LINKAJA": "NOT_AVAILABLE",
            "OVO": "NOT_AVAILABLE",
            "GOPAY": "NOT_AVAILABLE",
            "DANA": "NOT_AVAILABLE",
            "SHOPEEPAY": "NOT_AVAILABLE",
            "JAKONE": "NOT_AVAILABLE",
            "MIN_AMOUNT": int(_ConfigParser.get_set_value('GENERAL', 'min^refund^amount', '2500')),
            "DETAILS": []
        }
    else: 
        return {
            "MANUAL": "AVAILABLE" if check_refund('manual') is True else "NOT_AVAILABLE",
            "DIVA": "AVAILABLE" if check_refund('diva') is True else "NOT_AVAILABLE",
            "CS": "AVAILABLE" if check_refund('customer-service') is True else "NOT_AVAILABLE",
            "LINKAJA": "AVAILABLE" if check_refund('linkaja') is True else "NOT_AVAILABLE",
            "OVO": "AVAILABLE" if check_refund('ovo') is True else "NOT_AVAILABLE",
            "GOPAY": "AVAILABLE" if check_refund('gopay') is True else "NOT_AVAILABLE",
            "DANA": "AVAILABLE" if check_refund('dana') is True else "NOT_AVAILABLE",
            "SHOPEEPAY": "AVAILABLE" if check_refund('shopeepay') is True else "NOT_AVAILABLE", 
            "JAKONE": "AVAILABLE" if check_refund('jakone') is True else "NOT_AVAILABLE",
            "MIN_AMOUNT": int(_ConfigParser.get_set_value('GENERAL', 'min^refund^amount', '2500')),
            "DETAILS": REFUND_SETTING
        }


FORCE_ALLOWED_REFUND_METHOD = ["MANUAL", "DIVA", "LINKAJA", "CUSTOMER-SERVICE"]

MANDIRI_CARD_BLOCKED_LIST = load_from_temp_data('mandiri_card_blocked_list', 'text').split('\n')
MANDIRI_CHECK_CARD_BLOCKED = True 
_ConfigParser.set_value('GENERAL', 'mandiri^card^blocked', '1')
MANDIRI_CARD_BLOCKED_URL = _ConfigParser.get_set_value('GENERAL', 'mandiri^card^blocked^url', 'https://prepaid-service.mdd.co.id/topup-mandiri/blacklist')
if '---' in MANDIRI_CARD_BLOCKED_URL:
    _ConfigParser.set_value('GENERAL', 'mandiri^card^blocked^url', 'https://prepaid-service.mdd.co.id/topup-mandiri/blacklist')

GENERAL_CARD_BLOCKED_LIST = load_from_temp_data('general_card_blocked_list', 'text').split('\n')

DAILY_SYNC_SUMMARY_TIME = _ConfigParser.get_set_value('GENERAL', 'daily^sync^summary^time', '23:55')
DAILY_C2C_SETTLEMENT_TIME = _ConfigParser.get_set_value('GENERAL', 'daily^c2c^settlement^time', '23:59')
DAILY_REBOOT_TIME = _ConfigParser.get_set_value('GENERAL', 'daily^reboot^time', '02:30')


def check_refund(name='ovo'):
    if len(REFUND_SETTING) == 0 or empty(REFUND_SETTING) is True:
        return False
    for x in range(len(REFUND_SETTING)):
        if REFUND_SETTING[x]['name'].lower() == name and REFUND_SETTING[x]['name'] in FORCE_ALLOWED_REFUND_METHOD:
            return True
    return False


def check_refund_fee(name='ovo'):
    fee = 0
    for x in range(len(REFUND_SETTING)):
        if REFUND_SETTING[x]['name'].lower() == name.lower():
            fee = int(REFUND_SETTING[x]['admin_fee'])
            if int(REFUND_SETTING[x]['custom_admin_fee']) > 0:
                fee = int(REFUND_SETTING[x]['custom_admin_fee'])
            break
    return fee


def check_payment(name='ovo'):
    if len(PAYMENT_SETTING) == 0 or empty(PAYMENT_SETTING) is True:
        return False
    for x in range(len(PAYMENT_SETTING)):
        if PAYMENT_SETTING[x]['name'].lower() == name:
            if name == 'cash' and BILL_ERROR == 'CASHBOX_FULL':
                return False
            return True
    return False


def start_upload_device_state(device, status):
    _Helper.get_thread().apply_async(upload_device_state, (device, status,))


def upload_device_state(device, status):
    if DISABLE_SYNC_DEVICE_STATE or device not in ['nfc', 'mei', 'edc', 'printer', 'scanner', 'webcam', 'cd1', 'cd2', 'cd3', 'cd4', 'cd5', 'cd6']:
        return False
    try:
        param = {
            "device": device,
            "state": status
        }
        status, response = _HTTPAccess.post_to_url(BACKEND_URL + 'change/device-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False
    
    
def start_update_usage_retry_code(trxid):
    _Helper.get_thread().apply_async(update_usage_retry_code, (trxid, ))


def update_usage_retry_code(trxid):
    try:
        __param = {
            "trx_id": trxid,
        }
        status, response = _HTTPAccess.post_to_url(BACKEND_URL + 'sync/usage-pending-code', __param)
        LOGGER.info((response, str(__param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            __param['endpoint'] = 'sync/usage-pending-code'
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'sync/usage-pending-code', payload=__param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_upload_mandiri_wallet():
    _Helper.get_thread().apply_async(upload_mandiri_wallet)


def upload_mandiri_wallet():
    try:
        param = {
            'bank_name': 'MANDIRI',
            'active_wallet': MANDIRI_ACTIVE,
            'bank_tid': TID_MAN,
            'bank_mid': MID_MAN,
            'wallet_1': MANDIRI_WALLET_1,
            "wallet_2": MANDIRI_WALLET_2,
            "card_no_1": MANDIRI_SAM_NO_1,
            "card_no_2": MANDIRI_SAM_NO_2
        }
        if C2C_MODE is True:
            param['card_no_1'] = C2C_DEPOSIT_NO
            param['wallet_1'] = MANDIRI_ACTIVE_WALLET
        status, response = _HTTPAccess.post_to_url(BACKEND_URL + 'update/wallet-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_upload_bni_wallet():
    _Helper.get_thread().apply_async(upload_bni_wallet)


def upload_bni_wallet():
    try:
        param = {
            'bank_name': 'BNI',
            'active_wallet': BNI_ACTIVE,
            'bank_tid': TID_BNI,
            'bank_mid': MID_BNI,
            'wallet_1': BNI_SAM_1_WALLET,
            "wallet_2": BNI_SAM_2_WALLET,
            "card_no_1": BNI_SAM_1_NO,
            "card_no_2": BNI_SAM_2_NO
        }
        status, response = _HTTPAccess.post_to_url(BACKEND_URL + 'update/wallet-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


# def start_upload_failed_trx():
#     _Tools.get_thread().apply_async(store_upload_failed_trx)


def store_upload_failed_trx(trxid, pid='', amount=0, failure_type='', payment_method='', remarks=''):
    try:
        __param = {
            'trxid': trxid,
            'tid': TID,
            'mid': '',
            'pid': pid,
            'amount': amount,
            'cardNo': '',
            'failureType': failure_type,
            'paymentMethod': payment_method,
            'remarks': remarks
        }
        if payment_method.lower() in ['dana', 'shopeepay', 'jakone', 'linkaja', 'gopay', 'shopee', 'bca-qris', 'bni-qris']:
            remarks = json.loads(remarks)
            remarks['host_trx_id'] = LAST_QR_PAYMENT_HOST_TRX_ID
            remarks = json.dumps(remarks)
            __param['remarks'] = remarks
        
        if 'topup' in trxid:
            last_card_check = load_from_temp_data('last-card-check', 'json')

            __param['remarks2'] = load_from_temp_data(trxid+'-last-pending-result', 'json')
            __param['remarks3'] = load_from_temp_data(trxid+'-last-audit-result', 'json')
            # Add Other Details 
            # __param['remarks3']['last_card_no'] = last_card_check.get('card_no', '')
            if type(__param['remarks3']) != dict: __param['remarks3'] = {}
            __param['remarks3']['last_card_check'] = last_card_check
            
        
        # Only Store Pending Transaction To Transaction Failure Table
        if failure_type in ['PENDING_TRANSACTION', 'TOPUP_FAILURE_03']:
            _DAO.delete_transaction_failure({
                'reff_no': trxid,
                'tid': TID,            
            })
            _DAO.insert_transaction_failure(__param)
            # Auto Assign syncFlag
            __param['key'] = __param['trxid']
            _DAO.mark_sync(param=__param, _table='TransactionFailure', _key='trxid')         

        status, response = _HTTPAccess.post_to_url(BACKEND_URL + 'sync/transaction-failure', __param)
        LOGGER.info((response, str(__param)))
        if status == 200 and response['result'] == 'OK':
            # __param['key'] = __param['trxid']
            # _DAO.mark_sync(param=__param, _table='TransactionFailure', _key='trxid')
            return True
        else:
            __param['endpoint'] = 'sync/transaction-failure'
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'sync/transaction-failure', payload=__param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


# def start_upload_admin_access(aid, username, cash_collection, edc_settlement, card_adjustment, remarks):
#     _Tools.get_thread().apply_async(upload_admin_access, (aid, username, cash_collection, edc_settlement,
#                                                         card_adjustment, remarks,))


def upload_admin_access(aid, username, cash_collection='', edc_settlement='', card_adjustment='', remarks='', trx_list=''):
    try:
        param = {
            'aid': aid,
            'username': username,
            'cash_collection': cash_collection,
            'edc_settlement': edc_settlement,
            'card_adjustment': card_adjustment,
            'remarks': remarks,
            'trx_list': trx_list,
            'collect_time': _Helper.time_string()
        }
        status, response = _HTTPAccess.post_to_url(BACKEND_URL+'sync/access-report', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'sync/access-report', payload=param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_upload_topup_error(__slot, __type):
    _Helper.get_thread().apply_async(upload_topup_error, (__slot, __type,))


def upload_topup_error(__slot, __type):
    try:
        param = {
            'slot': __slot,
            'type': __type
        }
        status, response = _HTTPAccess.post_to_url(BACKEND_URL+'update/topup-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'update/topup-state', payload=param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def store_upload_sam_audit(param):
    sleep(1)
    _table_ = 'SAMAudit'
    try:
        param = {
            'lid': _Helper.get_uuid(),
            'trxid': param['trxid'],
            'samCardNo': param['samCardNo'],
            'samCardSlot': param['samCardSlot'],
            'samPrevBalance': param['samPrevBalance'],
            'samLastBalance': param['samLastBalance'],
            'topupCardNo': param['topupCardNo'],
            'topupPrevBalance': param['topupPrevBalance'],
            'topupLastBalance': param['topupLastBalance'],
            'status': param['status'],
            'remarks': param['remarks'],
            'createdAt': _Helper.now()
        }
        # _DAO.insert_sam_audit(param)
        status, response = _HTTPAccess.post_to_url(BACKEND_URL+'sync/sam-audit', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            # param['key'] = param['lid']
            # _DAO.mark_sync(param=param, _table=_table_, _key='lid')
            return True
        else:
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'sync/sam-audit', payload=param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def sam_to_slot(no, bank='BNI'):
    global BNI_ACTIVE
    if bank == 'BNI':
        BNI_ACTIVE = int(no)
        save_sam_config()
        LOGGER.info(('[REMOTE]', 'sam_to_slot', str(no)))
        return 'SUCCESS_SWITCH_TO_SAM_'+str(no)
    else:
        return 'UNKNOWN_BANK'


def save_sam_config(bank='BNI'):
    if bank == 'BNI':
        _ConfigParser.set_value('BNI', 'active^slot', str(BNI_ACTIVE))
    elif bank == 'MANDIRI':
        _ConfigParser.set_value('MANDIRI', 'active^slot', str(MANDIRI_ACTIVE))


def get_active_sam(bank='MANDIRI', reverse=False):
    if bank == 'MANDIRI':
        if MANDIRI_REVERSE_SLOT_MODE is True or reverse is True:
            if MANDIRI_ACTIVE == 1:
                return '2'
            elif MANDIRI_ACTIVE == 2:
                return '1'
        else:
            return str(MANDIRI_ACTIVE)
    else:
        return


def empty(s):
    return _Helper.empty(s)


def local_store_topup_record(param):
    if _Helper.empty(param):
        return False
    topup_record = {
        'rid': _Helper.get_uuid(),
        'trxid': '',
        'cardNo': param['card_no'],
        'balance': param['last_balance'],
        'reportSAM': param['report_sam'],
        'reportKA': param['report_ka'],
        'status': 1,
        'remarks': json.dumps(param)
    }
    _DAO.insert_topup_record(topup_record)
    topup_record['key'] = topup_record['rid']
    _DAO.mark_sync(param=topup_record, _table='TopUpRecords', _key='rid')
    return topup_record['rid']


LAST_CARD_LOG_HISTORY = []

# header = {
#         'Accept': '*/*',
#         'Accept-Encoding': 'gzip, deflate',
#         'Connection': 'close',
#         'Content-Type': 'application/json',
#         'tid': TID,
#         'token': TOKEN,
#         'unique': DISK_SERIAL_NUMBER,
#         'User-Agent': 'MDD Vending Machine ID ['+TID+']'
#     }

# Translate product provider property into Bank ID to those who contains bank name
def get_bid(provider=''):
    if 'mandiri' in provider.lower():
        return 1
    elif 'bni' in provider.lower():
        return 2
    elif 'bri' in provider.lower():
        return 3
    elif 'bca' in provider.lower():
        return 4
    elif 'dki' in provider.lower():
        return 5
    elif 'mega' in provider.lower():
        return 6
    elif 'nobu' in provider.lower():
        return 7
    elif 'btn' in provider.lower():
        return 8
    else:
        return 0


def get_bank_name(provider=''):
    if 'mandiri' in provider.lower():
        return 'mandiri'
    elif 'bni' in provider.lower():
        return 'bni'
    elif 'bri' in provider.lower():
        return 'bri'
    elif 'bca' in provider.lower():
        return 'bca'
    elif 'dki' in provider.lower():
        return 'dki'
    elif 'mega' in provider.lower():
        return 'mega'
    elif 'nobu' in provider.lower():
        return 'nobu'
    elif 'btn' in provider.lower():
        return 'btn'
    else:
        return ''


REFUND_LEGEND = {
    'DIVA': 'WHATSAPP',
    'OPERATOR': 'CUSTOMER SERVICE',
    'LA': 'LINKAJA'
}


def serialize_refund(refund):
    return REFUND_LEGEND.get(refund, refund)


class KioskServiceErrorResponse(Exception):
    def __init__(self, message):
        super().__init__(message)


class KioskGeneralError(Exception):
    def __init__(self, message):
        super().__init__(message)


class KioskConnectionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class KioskDeviceError(Exception):
    def __init__(self, message):
        super().__init__(message)


def serialize_error_message(e):
    if type(e) == list:
        m = []
        for element in e:
            m.append(str(element))
        e = "-".join(m)
    if type(e) != str:
        e = str(e)
    return " | ".join([TID, KIOSK_NAME, _Helper.time_string(), e])


def online_logger(e='', mode='service'):
    # _Helper.get_thread().apply_async(async_online_logger, (e, mode,))
    async_online_logger(e, mode)


def async_online_logger(e='', mode='service'):
    # pass
    if DISABLE_SENTRY_LOGGING:
        return
    e = serialize_error_message(e)
    if mode == 'service':
        capture_exception(KioskServiceErrorResponse(e))
    elif mode == 'connection':
        capture_exception(KioskConnectionError(e))
    elif mode == 'device':
        capture_exception(KioskDeviceError(e))
    else:
        capture_exception(KioskGeneralError(e))


LAST_UPDATED_STOCK = []
COLLECTION_DATA = []


def generate_collection_data():
    global COLLECTION_DATA, LAST_UPDATED_STOCK
    __ = dict()
    try:
        # Old Data Query Will be no longer valid after full implementing New TRX Model
        # __['trx_top10k'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale = 10000 AND isCollected = 0 AND pid like "topup%" ')[0]['__']
        # __['trx_top20k'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale = 20000 AND isCollected = 0 AND pid like "topup%" ')[0]['__']
        # __['trx_top50k'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale = 50000 AND isCollected = 0 AND pid like "topup%" ')[0]['__']
        # __['trx_top100k'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale = 100000 AND isCollected = 0 AND pid like "topup%" ')[0]['__']        
        # __['trx_top200k'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale = 200000 AND isCollected = 0 AND pid like "topup%" ')[0]['__']
        # __['trx_xdenom'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale NOT IN (10000, 20000, 50000, 100000, 200000) AND isCollected = 0 AND pid like "topup%" ')[0]['__']        
        # __['amt_top10k'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND sale = 10000 AND pid like "topup%"')[0]['__']
        # __['amt_top20k'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND sale = 20000 AND pid like "topup%"')[0]['__']
        # __['amt_top50k'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND sale = 50000 AND pid like "topup%" ')[0]['__']
        # __['amt_top100k'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND sale = 100000 AND pid like "topup%" ')[0]['__']
        # __['amt_top200k'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND sale = 200000 AND pid like "topup%" ')[0]['__']
        # __['amt_xdenom'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND sale NOT IN (10000, 20000, 50000, 100000, 200000) AND pid like "topup%" ')[0]['__']
        __['trx_top10k'] = 0
        __['trx_top20k'] = 0
        __['trx_top50k'] = 0
        __['trx_top100k'] = 0    
        __['trx_top200k'] = 0
        __['trx_xdenom'] = 0 
        __['amt_top10k'] = 0
        __['amt_top20k'] = 0
        __['amt_top50k'] = 0
        __['amt_top100k'] = 0
        __['amt_top200k'] = 0
        __['amt_xdenom'] = 0

        __['slot1'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 101 ')[0]['__']
        __['slot2'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 102 ')[0]['__']
        __['slot3'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 103 ')[0]['__']
        __['slot4'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 104 ')[0]['__']
        # __['all_cash'] = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __ FROM Cash WHERE collectedAt = 19900901 ')[0]['__']        
        # ' current_cash': _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__'],

        # __['all_cashbox'] = _DAO.cashbox_status()    
        cash_activity = get_cash_activity(trx_output=True)
        __['all_cash'] = cash_activity['total']
        __['all_cashbox'] = cash_activity['total']
        __['cash_activity'] = cash_activity
        # __['all_cashbox_history'] = ''
        # if int(__['all_cashbox']) > 0:
        #     cashbox_history = _DAO.cashbox_history()  
        #     if len(cashbox_history) > 0:
        #         if '__' in cashbox_history[0].keys():
        #             __['all_cashbox_history'] = cashbox_history[0]['__']
        __['all_cards'] = _DAO.custom_query(' SELECT pid, sell_price FROM ProductStock ')
        # __['ppob_cash'] = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __ FROM Cash WHERE pid LIKE "ppob%" AND collectedAt = 19900901 ')[0]['__']    
        __['ppob_cash'] =  get_cash_activity(keyword='ppob')['total']
        # __data['amt_card'] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE '
        #                                        ' bankMid = "" AND bankTid = "" AND sale > ' + str(CARD_SALE) +
        #                                        ' AND  pid like "shop%" ')[0]['__']
        # __data['trx_card'] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE sale > ' + str(CARD_SALE) +
        #                                        ' AND bankMid = "" AND bankTid = "" AND pid like "shop%" ')[0]['__']
        __['amt_card'] = 0
        __['trx_card'] = 0
        __['card_trx_summary'] = []
        # Old Data Query Will be no longer valid after full implementing New TRX Model
        if len(__['all_cards']) > 0:
            for card in __['all_cards']:
                pid = card['pid']
                price = card['sell_price']
                __['amt_card_'+str(pid)] = _DAO.custom_query(' SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0 AND pidStock = "' + str(pid) +'" ')[0]['__']
                __['amt_card'] += __['amt_card_'+str(pid)]
                __['trx_card_'+str(pid)] = _DAO.custom_query(' SELECT count(*) AS __ FROM Transactions WHERE amount = ' + str(price) +
                                                            ' AND isCollected = 0 AND pidStock = "'+str(pid)+'" ')[0]['__']
                __['trx_card'] += __['trx_card_'+str(pid)]
                __['card_trx_summary'].append({
                    'pid': pid,
                    'price': price,
                    'count': __['trx_card_'+str(pid)],
                    'amount': __['amt_card_'+str(pid)]
                })
            # SELECT sum(amount) as total FROM Cash WHERE collectedAt is null
        __['all_amount'] = int(__['amt_card']) + int(__['amt_top10k']) + int(__['amt_top20k']) + int(__['amt_top50k']) + int(__['amt_top100k']) + int(__['amt_top200k']) + int(__['amt_xdenom'])
        __['failed_amount'] = 0
        # Redefine All Cashbox From All Cash in Casset Not From Transaction
        # if int(__['all_cashbox']) >= int(__['all_cash']):
        #     LOGGER.warning(('CASHBOX VS TRX DATA NOT MATCH', __['all_cashbox'], __['all_cash']))
        #     __['all_cash'] = __['all_cashbox']
        if int(__['all_cash']) > (int(__['all_amount']) + int(__['ppob_cash'])):
            __['failed_amount'] = int(__['all_cash']) - (int(__['all_amount']) + int(__['ppob_cash']))
        __['init_slot1'] = __['slot1']
        __['init_slot2'] = __['slot2']
        __['init_slot3'] = __['slot3']
        __['init_slot4'] = __['slot4']
        __['sam_1_balance'] = '0'
        __['sam_2_balance'] = '0'
        __['notes_summary'] = ''
        __['trx_list'] = []
        __['total_notes'] = 0
        __notes = []
        # Old Data Query Will be no longer valid after full implementing New TRX Model
        # {'trx_top20k': 187, 'slot3': 25, 'all_cash': 14930000, 'amt_xdenom': 0, 'slot4': 0, 'amt_top50k': 4400000, 'amt_top20k': 3740000, 'trx_xdenom': 0, 'trx_top200k': 0, 'trx_top50k': 88, 'trx_top10k': 307, 'amt_top200k': 0, 'slot1': 19, 'amt_top10k': 3070000, 'amt_top100k': 2700000, 'trx_top100k': 27, 'slot2': 14, 'all_cashbox': 0}
        # __all_payment_notes = _DAO.custom_query(' SELECT paymentNotes AS note FROM Transactions WHERE paymentType = "MEI"  AND isCollected = 0 ')
        # if len(__all_payment_notes) > 0:
        #     for money in __all_payment_notes:
        #         __notes.append(json.loads(money['note'])['history'])
        #     __['notes_summary'] = '|'.join(__notes)
        #     __['total_notes'] = len(__['notes_summary'].split('|'))
        # __all_cash_trx_list = _DAO.custom_query(' SELECT pid FROM Cash WHERE collectedAt = 19900901 ')
        # if len(__all_cash_trx_list) > 0:
        #     for trx_list in __all_cash_trx_list:
        #         __['trx_list'].append(trx_list['pid'])
        #     __['trx_list'] = ','.join(__['trx_list'])    
        for n in cash_activity['summary'].keys():
            q = int(cash_activity['summary'][n])
            __notes.extend([n]*q)
        __['notes_summary'] = '|'.join(__notes)
        __['total_notes'] = len(__['notes_summary'].split('|'))
        __['trx_list'] = ','.join(cash_activity['trx_list'])
        # Status Bank BNI in Global
        __['sam_1_balance'] = str(MANDIRI_ACTIVE_WALLET)
        __['sam_2_balance'] = str(BNI_ACTIVE_WALLET)
        __['card_adjustment'] = ''
        if len(LAST_UPDATED_STOCK) > 0:
            __['card_adjustment'] = json.dumps(LAST_UPDATED_STOCK)
            for update in LAST_UPDATED_STOCK:
                if update['status'] == 101:
                    __['init_slot1'] = update['stock']
                if update['status'] == 102:
                    __['init_slot2'] = update['stock']
                if update['status'] == 103:
                    __['init_slot3'] = update['stock']
                if update['status'] == 104:
                    __['init_slot4'] = update['stock']
        __['collect_time'] = _Helper.time_string()
        BILL_ERROR = ''
        _ConfigParser.set_value('BILL', 'last^money^inserted', 'N/A'),
        COLLECTION_DATA = __
    except Exception as e:
        LOGGER.warning(str(e))
    finally:
        LOGGER.debug(str(__))
        return __


# SHOP 
# {'details': '{"date":"08/06/20","epoch":1591589266780,"payment":"cash","shop_type":"shop","time":"11:07:46","qty":1,"value":"5000","provider":"Test Card 2","admin_fee":"0","status":102,"raw":{"stock":74,"image":"source/card/20200306163800DF0FfQIKJ31s6ZEt33.png","remarks":"Test Card 2","init_price":5000,"pid":"dfaw2","stid":"dfaw2-102-001122334455","tid":"001122334455","syncFlag":1,"name":"Test Card 2","status":102,"createdAt":1591589169000,"sell_price":5000},"payment_details":{"total":"10000","history":"10000"},"payment_received":"10000"}', 'name': 'Test Card 2', 'price': 5000, 'syncFlag': 0, 'createdAt': 1591589279000, 'status': 1, 'pid': 'shop1591589266780'}

# TOPUP
# {'createdAt': 1591585430000, 'status': 1, 'pid': 'topup1591585396411', 'syncFlag': 0, 'name': 'e-Money Mandiri', 'details': '{"date":"08/06/20","epoch":1591585396411,"payment":"cash","shop_type":"topup","time":"10:03:16","qty":1,"value":"2000","provider":"e-Money Mandiri","admin_fee":1500,"raw":{"admin_fee":1500,"bank_name":"MANDIRI","bank_type":"0","card_no":"6032984075869341","prev_balance":"108110","provider":"e-Money Mandiri","value":"2000"},"status":"1","final_balance":"108610","denom":"500","payment_details":{"history":"10000","total":"10000"},"payment_received":"10000","topup_details":{"bank_name":"MANDIRI","card_no":"6032984075869341","bank_id":"1","report_sam":"603298407586934100770D706E86B69161010101000110F401000042A80100080620100326000000060006831D21CF","c2c_mode":"1","last_balance":"108610","report_ka":"603298180000008500030D706E86B69161510101880120D0070000C02D080008062010032600000006240003DC05000042BC14"}}'


def check_retry_able(data):
    if _Helper.empty(data) is True:
        return 0
    if data.get('shop_type') == 'ppob':
        if is_online(_Helper.whoami()+'_ppob'):
            return 1
        else:
            return 0
    elif data.get('shop_type') == 'shop':
        try:
            if DISABLE_CARD_RETRY_CODE is True:
                return 0
            slot_cd = data.get('raw').get('status')
            check_stock = _DAO.get_product_stock_by_slot_status(slot_cd)
            if len(check_stock) == 0:
                return 0
            if check_stock[0]['stock'] == 0:
                return 0
            return 1
        except Exception as e:
            LOGGER.warning((e))
            return 0
    elif data.get('shop_type') == 'topup':
        #  globalCart = {
        #     value: selectedDenom.toString(),
        #     provider: provider,
        #     admin_fee: adminFee,
        #     card_no: cardData.card_no,
        #     prev_balance: cardData.balance,
        #     bank_type: cardData.bank_type,
        #     bank_name: cardData.bank_name,
        # }
        # var final_balance = parseInt(cardData.balance) + parseInt(selectedDenom)
        # details.qty = 1;
        # details.value = selectedDenom.toString();
        # details.provider = provider;
        # details.admin_fee = adminFee;
        # details.raw = globalCart;
        # details.status = '1';
        # details.final_balance = final_balance.toString();
        # details.denom = selectedDenom.toString();
        # Disabled Can Change Topup Provider | 2022-04-06
        try:
            raw = data.get('raw')
            # Topup DKI, BRI & BCA Retry Validation Also User Connection Status
            if is_online(_Helper.whoami()+'_topup') and raw.get('bank_name') in ['BRI', 'BCA', 'DKI']:
                return 1
            topup_value = int(data.get('value', '0'))
            if MANDIRI_ACTIVE_WALLET > topup_value and raw.get('bank_name') in ['MANDIRI']:
                return 1
            if BNI_ACTIVE_WALLET > topup_value and raw.get('bank_name') in ['BNI']:
                return 1
            return 0
        except Exception as e:
            LOGGER.warning((e))
            return 0
    else:
        return 0


LAST_QR_PAYMENT_HOST_TRX_ID = None


def generate_stock_change_data():
    global LAST_UPDATED_STOCK
    __ = dict()
    try:
        __['slot1'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 101 ')[0]['__']
        __['slot2'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 102 ')[0]['__']
        __['slot3'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 103 ')[0]['__']
        __['slot4'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 104 ')[0]['__']
        __['init_slot1'] = __['slot1']
        __['init_slot2'] = __['slot2']
        __['init_slot3'] = __['slot3']
        __['init_slot4'] = __['slot4']
        __['sam_1_balance'] = str(MANDIRI_ACTIVE_WALLET)
        __['sam_2_balance'] = str(BNI_ACTIVE_WALLET)
        if len(LAST_UPDATED_STOCK) > 0:
            for update in LAST_UPDATED_STOCK:
                if update['status'] == 101:
                    __['init_slot1'] = update['stock']
                if update['status'] == 102:
                    __['init_slot2'] = update['stock']
                if update['status'] == 103:
                    __['init_slot3'] = update['stock']
                if update['status'] == 104:
                    __['init_slot4'] = update['stock']
        __['change_stock_time'] = _Helper.time_string()
    except Exception as e:
        LOGGER.warning(str(e))
    finally:
        LOGGER.debug(str(__))
        return __


DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []

PRINT_LOGO_MAPPING = {
    'transjakarta': 'tj-logo',
    'kai': 'kai-logo'
}

THEME_WITH_TOPUP_STATUS = ['TRANSJAKARTA', 'TEST']


def logo_theme(theme):
    if theme not in PRINT_LOGO_MAPPING.keys():
        return 'tj-logo'
    return PRINT_LOGO_MAPPING[theme]

PRINT_COMPANY_MAPPING = {
    'transjakarta': 'TJ',
    'kai': 'KAI',
    'jmto': 'JMTO',
    'jmrb': 'JMRB',
    'lms': 'LMS',
    'uns': 'UNS',
}

def company_theme(theme):
    if theme not in PRINT_COMPANY_MAPPING.keys():
        return theme.upper() #Add Default Theme To Name of Ereceipt
    return PRINT_COMPANY_MAPPING[theme]


def kiosk_status_data():
    mandiri_active_wallet = MANDIRI_ACTIVE_WALLET
    bni_active_wallet = BNI_ACTIVE_WALLET
    # if _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
    #     mandiri_active_wallet = '999001'
    #     bni_active_wallet = '999002'
    try:
        data = {
            'name': KIOSK_NAME,
            'version': VERSION,
            'status': KIOSK_STATUS,
            'tid': TID,
            'mandiri_wallet': mandiri_active_wallet,
            'bni_wallet': bni_active_wallet,
            'payment': PAYMENT_SETTING,
            'feature': FEATURE_SETTING,
            'last_money_inserted': _ConfigParser.get_value('BILL', 'last^money^inserted'),
            'refund_feature': _ConfigParser.get_value('GENERAL', 'refund^feature'),
            # Add Denom Setting
            # 'first_denom': _ConfigParser.get_set_value('TEMPORARY', 'first^denom', '10000'),
            # 'second_denom': _ConfigParser.get_set_value('TEMPORARY', 'second^denom', '20000'),
            # 'third_denom': _ConfigParser.get_set_value('TEMPORARY', 'third^denom', '50000'),
            # 'fourth_denom': _ConfigParser.get_set_value('TEMPORARY', 'fourth^denom', '100000'),
            # 'fifth_denom': _ConfigParser.get_set_value('TEMPORARY', 'fifth^denom', '150000'),
            # 'sixth_denom': _ConfigParser.get_set_value('TEMPORARY', 'sixth^denom', '200000'),
            # 'seventh_denom': _ConfigParser.get_set_value('TEMPORARY', 'seventh^denom', '250000'),
            # 'admin_include': _ConfigParser.get_set_value('TEMPORARY', 'admin^include', '1'),
            # 'printer_setting': '1' if _ConfigParser.get_set_value('PRINTER', 'printer^type', 'Default') == 'Default' else '0',
            'admin_fee': KIOSK_ADMIN,
            'printer_status': get_printer_status(),
            'maintenance_mode': '1' if MAINTENANCE_MODE else '0'
            # 'operator_name': '' if LOGGED_OPERATOR is None else LOGGED_OPERATOR['first_name']
        }
        return data
    except Exception as e:
        return {}


MDS_TOKEN = ''
MDS_SESSION = 'N/A'
MDS_MID = TERMINAL_TOKEN
MDS_WALLET = 0

LOGGED_OPERATOR = None

LAST_BCA_ONLINE_PENDING = ''
LAST_BRI_ONLINE_PENDING = ''


def validate_duration_pending_code(timestamp):
    # if _Helper.empty(time): 
    #     return False
    duration = (MAX_PENDING_CODE_DURATION * 24 * 60 * 60)
    limit_timestamp = int(timestamp) + duration
    LOGGER.info(('Time Duration Day - Epoch', MAX_PENDING_CODE_DURATION, duration))
    LOGGER.info(('Limit Timestamp', limit_timestamp))
    current_time = time()
    LOGGER.info(('Current Timestamp', current_time))
    if current_time >=  limit_timestamp:
        return False
    return True


def validate_usage_pending_code(reff_no):
    usage_attempt = int(load_from_temp_config(section=reff_no, default='0'))
    if usage_attempt == 0:
        return True
    elif MAX_PENDING_CODE_RETRY > usage_attempt:
        return True
    else:
        return False


IDLE_MODE = True
MAINTENANCE_MODE = False
IS_ONLINE = False
ECO_MODE = True if _ConfigParser.get_set_value('GENERAL', 'eco^mode', '0') == '1' else False



def is_online(source=''):
    global IS_ONLINE
    if not LIVE_MODE:
        LOGGER.info((source, IS_ONLINE))
    # Hit Actual Ping Into Host If Only in Maintenance Mode
    if MAINTENANCE_MODE or not ECO_MODE:
        IS_ONLINE = _Helper.is_online(source)
    return IS_ONLINE


LIMIT_CARD_OPNAME_DURATION_HOURS = int(_ConfigParser.get_set_value('CD', 'stock^opname^duration^hours', '6'))


def get_redeem_status_by_slot(slot_no):
    if slot_no[:2] != '10':
        slot_no = '10'+slot_no
    redeem_status = get_redeem_activity()
    return redeem_status['summary'].get(slot_no, 0)


def generate_card_preload_data(operator, struct_id):
    # '- Init Stock : ' + str(s['init_stock_'+slot]), 0, 0, 'L')
    # '- Card Sale  : ' + str(s['sale_stock_'+slot]), 0, 0, 'L')
    # '- WA Redeem  : ' + str(s['wa_redeem_'+slot]), 0, 0, 'L')
    # '- Last Stock : ' + str(s['last_stock_'+slot]), 0, 0, 'L')
    # '- Add Stock  : ' + str(s['add_stock_'+slot]), 0, 0, 'L')
    # '- Diff Stock : ' + str(s['diff_stock_'+slot]), 0, 0, 'L')
    data = {}
    stock_opname = []
    products = _DAO.custom_query(' SELECT * FROM ProductStock WHERE stid IS NOT NULL ')
    first_opname = first_do_card_opname()
    if len(products) > 0:
        for p in products:
            slot = str(p['status']).replace('10', '')
            data['id_stock_'+slot] = p['stid']
            data['pid_stock_'+slot] = p['pid']
            data['init_stock_'+slot] = 0
            data['add_stock_'+slot] = int(load_from_temp_config('last^add^stock^slot^'+slot, '0'))
            data['sale_stock_'+slot] = 0
            data['wa_redeem_'+slot] = 0
            data['last_stock_'+slot] = int(load_from_temp_config('last^stock^opname^slot^'+slot, '0'))
            data['last_input_stock_'+slot] = int(load_from_temp_config('last^stock^opname^slot^'+slot, '0'))
            data['final_stock_'+slot] = int(data['last_stock_'+slot]) + int(data['add_stock_'+slot])
            data['diff_stock_'+slot] = 0
            if not first_opname:     
                # a = init stock
                # b = sale
                # c = redeem
                # d = last stock (a-b-c) seharusnya
                # e = last input stock (actual)
                # f = diff (d-e)
                # g = add stock
                # h = final stock (e + g)
                data['init_stock_'+slot] = int(load_from_temp_config('stock^opname^slot^'+slot, '0'))
                data['sale_stock_'+slot] = _DAO.custom_query(' SELECT count(*) AS __ FROM TransactionsNew WHERE trxType = "SHOP" AND mid = "" AND trxNotes = "' + p['stid'] + '" ')[0]['__']
                data['wa_redeem_'+slot] = get_redeem_status_by_slot(slot)
                data['last_stock_'+slot] = int(data['init_stock_'+slot]) - int(data['sale_stock_'+slot]) - int(data['wa_redeem_'+slot])
                data['diff_stock_'+slot] = int(data['last_stock_'+slot]) - int(data['last_input_stock_'+slot])
                data['final_stock_'+slot] = int(data['last_input_stock_'+slot]) + int(data['add_stock_'+slot])            
            i = 0
            while True:
                i += 1
                sleep(.5)
                log_to_temp_config('stock^opname^slot^'+slot, str(data['final_stock_'+slot]))
                if (i == 2):
                    break
            
            stock_opname.append({
                "slot": p['status'],
                "reload_id": struct_id,
                "tid": TID,
                "pid": p['pid'],
                "init_stock": data['init_stock_'+slot],
                "sale": data['sale_stock_'+slot],   
                "redeem": data['wa_redeem_'+slot],
                # Re-define Last Stock
                "last_stock": data['last_input_stock_'+slot],
                "add_stock": data['add_stock_'+slot],
                "diff": data['diff_stock_'+slot],
                "preload_at": _Helper.time_string(),
                "operator": operator,
                "remarks": json.dumps(p),
                "created_at": _Helper.now()
            })
    # Reset Flagging Calculation For Next Opname
    _DAO.custom_update(' UPDATE TransactionsNew SET mid = "'+struct_id+'" WHERE trxType = "SHOP" AND mid = "" ')
    LOGGER.debug(('CARD_STOCK_OPNAME_DATA', str(data)))
    store_stock_opname(struct_id, json.dumps(stock_opname))
    archive_redeem_activity(struct_id+'.redeem')
    return data


def send_stock_opname(key):
    data = load_stock_opname(key)
    if len(data) == 0:
        LOGGER.warning(('STOCK_OPNAME_DATA_NOT_FOUND', key))
        return False
    try:
        param = {
            'data': json.dumps(data)
        }
        status, response = _HTTPAccess.post_to_url(BACKEND_URL+'sync/card-preload', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'sync/card-preload', payload=param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def single_denom_trx_detected(trxid):
    # Must Be Match With Pattern And Bill Type
    return _Helper.get_char_from(trxid) in BILL_SINGLE_DENOM_TRX and BILL_TYPE in BILL_SINGLE_DENOM_TYPE


# New Feature Override
CARD_SALE_FEATURES = {
    '1': True if _ConfigParser.get_set_value('FEATURES', 'card^sale^mdr', '1') == '1' else False,
    '2': True if _ConfigParser.get_set_value('FEATURES', 'card^sale^bni', '1') == '1' else False,
    '3': True if _ConfigParser.get_set_value('FEATURES', 'card^sale^bri', '1') == '1' else False,
    '4': True if _ConfigParser.get_set_value('FEATURES', 'card^sale^bca', '1') == '1' else False,
    '5': True if _ConfigParser.get_set_value('FEATURES', 'card^sale^dki', '1') == '1' else False,
}

CARD_TOPUP_FEATURES = {
    'MANDIRI': True if _ConfigParser.get_set_value('FEATURES', 'card^topup^mdr', '1') == '1' else False,
    'BNI': True if _ConfigParser.get_set_value('FEATURES', 'card^topup^bni', '1') == '1' else False,
    'BRI': True if _ConfigParser.get_set_value('FEATURES', 'card^topup^bri', '1') == '1' else False,
    'BCA': True if _ConfigParser.get_set_value('FEATURES', 'card^topup^bca', '1') == '1' else False,
    'DKI': True if _ConfigParser.get_set_value('FEATURES', 'card^topup^dki', '1') == '1' else False,
}

LAST_TOPUP_TRXID = ''