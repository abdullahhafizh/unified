__author__ = "fitrah.wahyudi.imam@gmail.com"

import logging
from _cConfig import _ConfigParser
from _tTools import _Helper
from _nNetwork import _NetworkAccess
from _dDAO import _DAO
from time import *
import os
import sys
import json
import re


LOGGER = logging.getLogger()


def get_config_value(option='', section='TEMPORARY', digit=False):
    if len(option) == 0:
        return
    if digit is True:
        return int(_ConfigParser.get_value(section, option))
    else:
        return str(_ConfigParser.get_value(section, option))


BACKEND_URL = _ConfigParser.get_set_value('GENERAL', 'backend^server', '---')
LIVE_MODE = True if _ConfigParser.get_set_value('GENERAL', 'mode', 'live') == 'live' else False
TEST_MODE = not LIVE_MODE
RELOAD_SERVICE = True if _ConfigParser.get_set_value('GENERAL', 'reload^service', '0') == '1' else False
TID = _ConfigParser.get_set_value('GENERAL', 'tid', '---')

QPROX_PORT = _ConfigParser.get_set_value('QPROX_NFC', 'port', 'COM')

EDC_PORT = get_config_value('port', 'EDC')
EDC_TYPE = _ConfigParser.get_set_value('EDC', 'type', 'UPT-IUR')
EDC_DEBIT_ONLY = True if _ConfigParser.get_set_value('EDC', 'debit^only', '1') == '1' else False
MEI_PORT = get_config_value('port', 'MEI')
BILL_PORT = get_config_value('port', 'BILL')
BILL_TYPE = _ConfigParser.get_set_value('BILL', 'type', 'GRG')
BILL_RESTRICTED_NOTES = _ConfigParser.get_set_value('BILL', 'not^allowed^denom', '1000|2000|5000')

CD_PORT1 = _ConfigParser.get_set_value('CD', 'port1', 'COM')
CD_PORT2 = _ConfigParser.get_set_value('CD', 'port2', 'COM')
CD_PORT3 = _ConfigParser.get_set_value('CD', 'port3', 'COM')

PRINTER_PORT = _ConfigParser.get_set_value('PRINTER', 'port', 'COM')
PRINTER_BAUDRATE = _ConfigParser.get_set_value('PRINTER', 'baudrate', '15200')

MID_MAN = _ConfigParser.get_set_value('MANDIRI', 'mid', '---')
TID_MAN = _ConfigParser.get_set_value('MANDIRI', 'tid', '---')
SAM_MAN = _ConfigParser.get_set_value('MANDIRI', 'sam^pin', '---')
MANDIRI_THRESHOLD = int(_ConfigParser.get_set_value('MANDIRI', 'amount^minimum', '50000'))

MID_BNI = _ConfigParser.get_set_value('BNI', 'mid', '---')
TID_BNI = _ConfigParser.get_set_value('BNI', 'tid', '---')
MC_BNI = _ConfigParser.get_set_value('BNI', 'merried^code', '---')
SAM1_BNI = _ConfigParser.get_set_value('BNI', 'sam1^slot', '---')
SAM2_BNI = _ConfigParser.get_set_value('BNI', 'sam2^slot', '---')
BNI_TOPUP_AMOUNT = _ConfigParser.get_set_value('BNI', 'amount^topup', '500000')
BNI_THRESHOLD = int(_ConfigParser.get_set_value('BNI', 'amount^minimum', '50000'))

MID_BRI = _ConfigParser.get_set_value('BRI', 'mid', '---')
TID_BRI = _ConfigParser.get_set_value('BRI', 'tid', '---')
PROCODE_BRI = _ConfigParser.get_set_value('BRI', 'procode', '---')
SLOT_BRI = _ConfigParser.get_set_value('BRI', 'sam^slot', '3')

MID_BCA = _ConfigParser.get_set_value('BCA', 'mid', '---')
TID_BCA = _ConfigParser.get_set_value('BCA', 'tid', '---')
SLOT_BCA = _ConfigParser.get_set_value('BCA', 'sam^slot', '---')

C2C_MODE = True if _ConfigParser.get_set_value('MANDIRI_C2C', 'mode', '0') == '1' else False
C2C_MACTROS = _ConfigParser.get_set_value('MANDIRI_C2C', 'mactros', '0000000000000000')
C2C_MID = _ConfigParser.get_set_value('MANDIRI_C2C', 'mid', '---')
_ConfigParser.get_set_value('MANDIRI_C2C', '#mactros^info', 'must_be_16_chars')
C2C_TID_NEW_APP = _ConfigParser.get_set_value('MANDIRI_C2C', 'tid^new^app', '---')
C2C_SAM_SLOT = _ConfigParser.get_set_value('MANDIRI_C2C', 'sam^slot', '---')
C2C_THRESHOLD = _ConfigParser.get_set_value('MANDIRI_C2C', 'minimum^amount', '---')


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
IS_PIR = True if _ConfigParser.get_set_value('GENERAL', 'pir^usage', '0') == '1' else False
TEMP_FOLDER = sys.path[0] + '/_tTmp/'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Temporary Update Balance Config Hardcoded (Filled With Bank Name)
ALLOWED_BANK_UBAL_ONLINE = ['MANDIRI', 'BNI']

MANDIRI_FORCE_PRODUCTION_SAM = True if _ConfigParser.get_set_value('GENERAL', 'mandiri^sam^production', '0') == '1' else False


def clean_white_space(s):
    return re.sub(r'\s+', '', s)


def init_temp_data():
    global TEMP_FOLDER
    if not os.path.exists(sys.path[0] + '/_tTmp/'):
        os.makedirs(sys.path[0] + '/_tTmp/')
    TEMP_FOLDER = sys.path[0] + '/_tTmp/'


def store_to_temp_data(temp, content):
    if '.data' not in temp:
        temp = temp + '.data'
    temp_path = os.path.join(TEMP_FOLDER, temp)
    if len(clean_white_space(content)) == 0:
        content = '{}'
    with open(temp_path, 'w+') as t:
        t.write(content)
        t.close()


def load_from_temp_data(temp, mode='text'):
    if '.data' not in temp:
        temp = temp + '.data'
    temp_path = os.path.join(TEMP_FOLDER, temp)
    if not os.path.exists(temp_path):
        with open(temp_path, 'w+') as t:
            t.write('{}')
            t.close()
    content = open(temp_path, 'r').read().strip()
    if len(clean_white_space(content)) == 0:
        os.remove(temp_path)
        store_to_temp_data(temp_path, '{}')
        content = '{}'
    if mode == 'json':
        return json.loads(content)
    return content


TOPUP_AMOUNT_SETTING = None
FEATURE_SETTING = load_from_temp_data('feature-setting', 'json')
PAYMENT_SETTING = load_from_temp_data('payment-setting', 'json')
REFUND_SETTING = load_from_temp_data('refund-setting', 'json')
THEME_SETTING = load_from_temp_data('theme-setting', 'json')
ADS_SETTING = load_from_temp_data('ads-setting', 'json')
THEME_NAME = _ConfigParser.get_set_value('TEMPORARY', 'theme^name', '---')
REPO_USERNAME = _ConfigParser.get_set_value('REPOSITORY', 'username', 'developer')
REPO_PASSWORD = _ConfigParser.get_set_value('REPOSITORY', 'password', 'Mdd*123#')
SERVICE_VERSION = _ConfigParser.get_set_value('TEMPORARY', 'service^version', '---')
COLOR_TEXT = _ConfigParser.get_set_value('TEMPORARY', 'color^text', 'white')
COLOR_BACK = _ConfigParser.get_set_value('TEMPORARY', 'color^back', 'black')

QR_HOST = _ConfigParser.get_set_value('QR', 'qr^host', 'http://apiv2.mdd.co.id:10107/v1/')
QR_TOKEN = _ConfigParser.get_set_value('QR', 'qr^token', 'e6f092a0fa88d9cac8dac3d2162f1450')
QR_MID = _ConfigParser.get_set_value('QR', 'qr^mid', '000972721511382bf739669cce165808')

CORE_HOST = QR_HOST
CORE_TOKEN = QR_TOKEN
CORE_MID = QR_MID

STORE_QR_TO_LOCAL = True if _ConfigParser.get_set_value('QR', 'store^local', '1') == '1' else False
QR_PAYMENT_TIME = int(_ConfigParser.get_set_value('QR', 'payment^time', '300'))
QR_STORE_PATH = os.path.join(sys.path[0], '_qQr')
if not os.path.exists(QR_STORE_PATH):
    os.makedirs(QR_STORE_PATH)


QR_NON_DIRECT_PAY = ['GOPAY', 'DANA', 'LINKAJA', 'SHOPEEPAY']
QR_DIRECT_PAY = ['OVO']
# Hardcoded Env Status
QR_PROD_STATE = {
    'GOPAY': True,
    'DANA': True,
    'LINKAJA': True,
    'SHOPEEPAY': True,
    'OVO': True
}

ENDPOINT_SUCCESS_BY_HTTP_HEADER = [
    'settlement/submit', 
    'refund/global',
    'cancel-payment',

    ]

# APIV2 Credentials For Topup   
TOPUP_URL = 'http://apiv2.mdd.co.id:10107/'
TOPUP_TOKEN = 'ab247c99e983d0c0d0772246ccb465e8'
TOPUP_MID = '1e931ee42dc9d826ff945851782f0942'


def serialize_payload(data, specification='MDD_CORE_API'):
    if specification == 'MDD_CORE_API':
        data['token'] = CORE_TOKEN
        data['mid'] = CORE_MID
        data['tid'] = TID
        if 'trx_id' in data.keys():
            data['trx_id'] = data['trx_id'] + '-' + TID
        _Helper.dump(data)
    return data


def get_service_version():
    global SERVICE_VERSION
    ___stat = -1
    ___resp = None
    try:
        # sleep(3)
        ___stat, ___resp = _NetworkAccess.get_local(SERVICE_URL + '999&param=0')
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

LAST_AUTH = int(_ConfigParser.get_set_value('TEMPORARY', 'last^auth', '0'))
LAST_UPDATE = int(_ConfigParser.get_set_value('TEMPORARY', 'last^update', '0'))
LAST_GET_PPOB = int(_ConfigParser.get_set_value('TEMPORARY', 'last^get^ppob', '0'))


BANKS = [{
    "BANK": "MANDIRI",
    "STATUS": True if ('---' not in MID_MAN and len(MID_MAN) > 3) else False,
    "MID": MID_MAN,
    "TID": TID_MAN,
    "SAM": SAM_MAN,
    "C2C_MODE": C2C_MODE
}, {
    "BANK": "BNI",
    "STATUS": True if ('---' not in MID_BNI and len(MID_BNI) > 3) else False,
    "MID": MID_BNI,
    "TID": TID_BNI,
    "MC": MC_BNI,
    "SAM1": SAM1_BNI,
    "SAM2": SAM2_BNI,
    "MIN_AMOUNT": BNI_THRESHOLD,
    "DEFAULT_TOPUP": BNI_TOPUP_AMOUNT
}, {
    "BANK": "BRI",
    "STATUS": True if ('---' not in MID_BRI and len(MID_BRI) > 3) else False,
    "MID": MID_BRI,
    "TID": TID_BRI,
    "PROCODE": PROCODE_BRI
}, {
    "BANK": "BCA",
    "STATUS": True if ('---' not in MID_BCA and len(MID_BCA) > 3) else False,
    "MID": MID_BCA,
    "TID": TID_BCA,
}]

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

SFTP_C2C = {
    'status': C2C_MODE,
    'host': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^host', '---'),
    'user': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^user', '---'),
    'pass': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^pass', '---'),
    'port': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^port', '---'),
    'path': _ConfigParser.get_set_value('MANDIRI_C2C', 'c2c^path', '---'),
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
MANDIRI_NO_1 = _ConfigParser.get_set_value('MANDIRI', 'sam1^uid', '---')
MANDIRI_NO_2 = _ConfigParser.get_set_value('MANDIRI', 'sam2^uid', '---')
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
CD1_ERROR = ''
CD2_ERROR = ''
CD3_ERROR = ''

RECEIPT_PRINT_COUNT = int(_ConfigParser.get_set_value('PRINTER', 'receipt^print^count', '0'))
RECEIPT_PRINT_LIMIT = int(_ConfigParser.get_set_value('PRINTER', 'receipt^print^limit', '1800'))
if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT:
    PRINTER_ERROR = 'PAPER_ROLL_WARNING'
RECEIPT_LOGO = _ConfigParser.get_set_value('PRINTER', 'receipt^logo', 'mandiri_logo.gif')
CUSTOM_RECEIPT_TEXT = _ConfigParser.get_set_value('PRINTER', 'receipt^custom^text', '')
PRINTER_TYPE = _ConfigParser.get_set_value('PRINTER', 'printer^type', 'Default')

EDC_PRINT_ON_LAST = True if _ConfigParser.get_set_value('EDC', 'print^last', '1') == '1' else False
LAST_EDC_TRX_RECEIPT = None

ALLOWED_SYNC_TASK = [
    'sync_product_data',
    'sync_pending_refund',
    'sync_task',
    # 'sync_settlement_data', -> Disable This, Settlement Data Will be send to Kiosk Backend Not SMT Anymore
    'sync_sam_audit',
    'sync_data_transaction_failure',
    'sync_data_transaction',
    'sync_topup_records',
    'sync_machine_status'

]


JOB_PATH = os.path.join(sys.path[0], '_jJob')
if not os.path.exists(JOB_PATH):
    os.makedirs(JOB_PATH)


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


def log_to_temp_config(section='last^auth', content=''):
    global LAST_AUTH, LAST_UPDATE
    __timestamp = _Helper.now()
    if section == 'last^auth':
        LAST_AUTH = __timestamp
        content = str(__timestamp)
    elif section == 'last^update':
        LAST_UPDATE = __timestamp
        content = str(__timestamp)
    else:
        content = str(content)
    _ConfigParser.set_value('TEMPORARY', section, content)


def log_to_config(option='TEMPORARY', section='last^auth', content=''):
    content = str(content)
    _ConfigParser.set_value(option, section, content)


def update_receipt_count():
    global PRINTER_ERROR, RECEIPT_PRINT_COUNT
    RECEIPT_PRINT_COUNT = RECEIPT_PRINT_COUNT + 1
    log_to_config('PRINTER', 'receipt^print^count', str(RECEIPT_PRINT_COUNT))
    if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT:
        PRINTER_ERROR = 'PAPER_ROLL_WARNING'


def start_reset_receipt_count(count):
    _Helper.get_pool().apply_async(reset_receipt_count, (count,))


def reset_receipt_count(count):
    global PRINTER_ERROR, RECEIPT_PRINT_COUNT
    RECEIPT_PRINT_COUNT = int(count)
    log_to_config('PRINTER', 'receipt^print^count', str(RECEIPT_PRINT_COUNT))
    if RECEIPT_PRINT_COUNT >= RECEIPT_PRINT_LIMIT:
        PRINTER_ERROR = 'PAPER_ROLL_WARNING'
    else:
        PRINTER_ERROR = ''


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
    global MANDIRI_NO_1, MANDIRI_NO_2
    if slot == '1':
        MANDIRI_NO_1 = uid
        _ConfigParser.set_value('MANDIRI', 'sam1^uid', uid)
    if slot == '2':
        MANDIRI_NO_2 = uid
        _ConfigParser.set_value('MANDIRI', 'sam2^uid', uid)


def set_bni_sam_no(slot, no):
    global BNI_SAM_1_NO, BNI_SAM_2_NO
    if slot == '1':
        BNI_SAM_1_NO = no
        _ConfigParser.set_value('BNI', 'sam1^no', no)
    if slot == '2':
        BNI_SAM_2_NO = no
        _ConfigParser.set_value('BNI', 'sam2^no', no)


def digit_in(s):
    return any(i.isdigit() for i in s)


QPROX = {
    "port": QPROX_PORT,
    "status": True if QPROX_PORT is not None and digit_in(QPROX_PORT) is True else False,
    # "bank_config": BANKS
}
EDC = {
    "port": EDC_PORT,
    "status": True if EDC_PORT is not None and digit_in(EDC_PORT) is True else False
}
MEI = {
    "port": MEI_PORT,
    "status": True if MEI_PORT is not None and digit_in(MEI_PORT) is True else False
}
# BILL Device Type For GRG / NV
BILL = {
    "port": BILL_PORT,
    "type": BILL_TYPE,
    "status": True if BILL_PORT is not None and digit_in(BILL_PORT) is True else False
}
# Handling MEI VS BILL Duplicate Port Activation
if BILL['status'] is True:
    MEI['status'] = False
    MEI_PORT = _ConfigParser.set_value('MEI', 'port', 'COM')
    MEI['port'] = MEI_PORT
    
CD = {
    "port1": CD_PORT1,
    "port2": CD_PORT2,
    "port3": CD_PORT3,
    "status": True if CD_PORT1 is not None and digit_in(CD_PORT1) is True else False,
    "list_port": CD_PORT_LIST
}

CD_READINESS = {
    "port1": 'N/A',
    "port2": 'N/A',
    "port3": 'N/A',
}

SMT_CONFIG = dict()


def start_get_devices():
    _Helper.get_pool().apply_async(get_devices)


def get_devices():
    # LOGGER.info(('[INFO] get_devices', DEVICES))
    return {"QPROX": QPROX, "EDC": EDC, "MEI": MEI, "CD": CD, "BILL": BILL}


def get_payments():
    return {
        "QPROX": "AVAILABLE" if QPROX["status"] is True else "NOT_AVAILABLE",
        "EDC": "AVAILABLE" if (EDC["status"] is True and check_payment('card') is True) else "NOT_AVAILABLE",
        "CD": "AVAILABLE" if CD["status"] is True else "NOT_AVAILABLE",
        "MEI": "AVAILABLE" if (MEI["status"] is True and check_payment('cash') is True) else "NOT_AVAILABLE",
        "BILL": "AVAILABLE" if (BILL["status"] is True and check_payment('cash') is True) else "NOT_AVAILABLE",
        "QR_OVO": "AVAILABLE" if check_payment('ovo') is True else "NOT_AVAILABLE",
        "QR_DANA": "AVAILABLE" if check_payment('dana') is True else "NOT_AVAILABLE",
        "QR_GOPAY": "AVAILABLE" if check_payment('gopay') is True else "NOT_AVAILABLE",
        "QR_LINKAJA": "AVAILABLE" if check_payment('linkaja') is True else "NOT_AVAILABLE",
        "QR_SHOPEEPAY": "AVAILABLE" if check_payment('shopeepay') is True else "NOT_AVAILABLE",
    }


def get_refunds():
    if len(REFUND_SETTING) == 0 or empty(REFUND_SETTING) is True:
        return {
            "MANUAL": "AVAILABLE",
            "DIVA": "AVAILABLE",
            "LINKAJA": "NOT_AVAILABLE",
            "OVO": "NOT_AVAILABLE",
            "GOPAY": "NOT_AVAILABLE",
            "DANA": "NOT_AVAILABLE",
            "SHOPEEPAY": "NOT_AVAILABLE",
            "MIN_AMOUNT": int(_ConfigParser.get_set_value('GENERAL', 'min^refund^amount', '2500')),
            "DETAILS": []
        }
    else: 
        return {
            "MANUAL": "AVAILABLE" if check_refund('manual') is True else "NOT_AVAILABLE",
            "DIVA": "AVAILABLE" if check_refund('diva') is True else "NOT_AVAILABLE",
            "LINKAJA": "AVAILABLE" if check_refund('linkaja') is True else "NOT_AVAILABLE",
            "OVO": "AVAILABLE" if check_refund('ovo') is True else "NOT_AVAILABLE",
            "GOPAY": "AVAILABLE" if check_refund('gopay') is True else "NOT_AVAILABLE",
            "DANA": "AVAILABLE" if check_refund('dana') is True else "NOT_AVAILABLE",
            "SHOPEEPAY": "AVAILABLE" if check_refund('shopeepay') is True else "NOT_AVAILABLE",
            "MIN_AMOUNT": int(_ConfigParser.get_set_value('GENERAL', 'min^refund^amount', '2500')),
            "DETAILS": REFUND_SETTING
        }


FORCE_ALLOWED_REFUND_METHOD = ["MANUAL", "DIVA", "LINKAJA"]


def check_refund(name='ovo'):
    if len(REFUND_SETTING) == 0 or empty(REFUND_SETTING) is True:
        return False
    for x in range(len(REFUND_SETTING)):
        if REFUND_SETTING[x]['name'].lower() == name and REFUND_SETTING[x]['name'] in FORCE_ALLOWED_REFUND_METHOD:
            return True
    return False


def check_payment(name='ovo'):
    if len(PAYMENT_SETTING) == 0 or empty(PAYMENT_SETTING) is True:
        return False
    for x in range(len(PAYMENT_SETTING)):
        if PAYMENT_SETTING[x]['name'].lower() == name:
            return True
    return False


def start_upload_device_state(device, status):
    _Helper.get_pool().apply_async(upload_device_state, (device, status,))


def upload_device_state(device, status):
    if device not in ['nfc', 'mei', 'edc', 'printer', 'scanner', 'webcam', 'cd1', 'cd2', 'cd3']:
        LOGGER.warning(('device not in known_list', device, status))
        return False
    try:
        param = {
            "device": device,
            "state": status
        }
        status, response = _NetworkAccess.post_to_url(BACKEND_URL + 'change/device-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_upload_mandiri_wallet():
    _Helper.get_pool().apply_async(upload_mandiri_wallet)


def upload_mandiri_wallet():
    try:
        param = {
            'bank_name': 'MANDIRI',
            'active_wallet': MANDIRI_ACTIVE,
            'bank_tid': TID_MAN,
            'bank_mid': MID_MAN,
            'wallet_1': MANDIRI_WALLET_1,
            "wallet_2": MANDIRI_WALLET_2,
            "card_no_1": MANDIRI_NO_1,
            "card_no_2": MANDIRI_NO_2
        }
        status, response = _NetworkAccess.post_to_url(BACKEND_URL + 'update/wallet-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_upload_bni_wallet():
    _Helper.get_pool().apply_async(upload_bni_wallet)


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
        status, response = _NetworkAccess.post_to_url(BACKEND_URL + 'update/wallet-state', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['result'] == 'OK':
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


# def start_upload_failed_trx():
#     _Tools.get_pool().apply_async(store_upload_failed_trx)


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
            'remarks': remarks,
        }
        # check_trx = _DAO.check_trx_failure(trxid)
        # if len(check_trx) == 0:
        #     _DAO.insert_transaction_failure(__param)
        status, response = _NetworkAccess.post_to_url(BACKEND_URL + 'sync/transaction-failure', __param)
        LOGGER.info((response, str(__param)))
        if status == 200 and response['result'] == 'OK':
            # __param['key'] = __param['trxid']
            # _DAO.mark_sync(param=__param, _table='TransactionFailure', _key='trxid')
            return True
        else:
            store_request_to_job(name=_Helper.whoami(), url=BACKEND_URL+'sync/transaction-failure', payload=__param)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


# def start_upload_admin_access(aid, username, cash_collection, edc_settlement, card_adjustment, remarks):
#     _Tools.get_pool().apply_async(upload_admin_access, (aid, username, cash_collection, edc_settlement,
#                                                         card_adjustment, remarks,))


def upload_admin_access(aid, username, cash_collection='', edc_settlement='', card_adjustment='', remarks=''):
    try:
        param = {
            'aid': aid,
            'username': username,
            'cash_collection': cash_collection,
            'edc_settlement': edc_settlement,
            'card_adjustment': card_adjustment,
            'remarks': remarks,
        }
        status, response = _NetworkAccess.post_to_url(BACKEND_URL+'sync/access-report', param)
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
    _Helper.get_pool().apply_async(upload_topup_error, (__slot, __type,))


def upload_topup_error(__slot, __type):
    try:
        param = {
            'slot': __slot,
            'type': __type
        }
        status, response = _NetworkAccess.post_to_url(BACKEND_URL+'update/topup-state', param)
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
    sleep(3)
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
        }
        # _DAO.insert_sam_audit(param)
        status, response = _NetworkAccess.post_to_url(BACKEND_URL+'sync/sam-audit', param)
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

