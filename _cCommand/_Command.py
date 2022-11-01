__author__ = "wahyudi@multidaya.id"

import logging
import os
import threading
from _cConfig import _ConfigParser
from _cConfig import _Common
import json
import platform
from _nNetwork import _HTTPAccess
from _mModule._InterfacePrepaidDLL import send_command as module_command


LOCK = threading.Lock()
LOGGER = logging.getLogger()
GET_PATH = _ConfigParser.get_value("TERMINAL", "path")
if 'Windows-7' in platform.platform():
    DISK = 'D'
else:
    DISK = 'C'
PATH = os.path.join(DISK+':\\', GET_PATH) if GET_PATH is not None else DISK + ':\\_SOCKET_'
MI_GUI = os.path.join(PATH, 'MI_GUI.txt')
MO_BALANCE = os.path.join(PATH, 'MO_BALANCE.txt')
MO_KA_INFO = os.path.join(PATH, 'MO_KA_INFO.txt')
MO_ERROR = os.path.join(PATH, 'MO_ERROR.txt')
MO_REPORT = os.path.join(PATH, 'MO_REPORT.txt')
MO_STATUS = os.path.join(PATH, 'MO_STATUS.txt')
MO_LIST = {
    'ERROR': MO_ERROR,
    'REPORT': MO_REPORT,
    'KA_INFO': MO_KA_INFO,
    'BALANCE': MO_BALANCE,
    'STATUS': MO_STATUS
}
MAX_TRIAL = 3
BUFFER = 2048
WAITING_TIME = 0.5

LOCAL_URL = _Common.SERVICE_URL
FLASK_URL = _Common.FLASK_URL
# http://localhost:9000/Service/GET?type=json&cmd=000&param=com4


def set_output(p):
    __p = p[3:-1] if p[-1] == '|' else p[3:]
    if __p[0] == '|':
        __p = __p[1:]
    return __p


def send_request(param=None, output=None, responding=True, flushing=MO_STATUS, wait_for=None, verify=False):
    __unused_param = {
        'output': output,
        'responding': responding,
        'flushing': flushing,
        'wait_for': wait_for,
        'verify': verify
    }
    if param is None:
        return -1, 'MISSING_PARAM'
    ___cmd = param[:3]
    if len(param) <= 4:
        ___param = "0"
    else:
        ___param = set_output(param)
    special_timeout_command = {
        "UPDATE_BALANCE_ONLINE_MANDIRI": "019", #Update Balance Online Mandiri
        "UPDATE_BALANCE_ONLINE_BRI": "024", #BRI UBAL ONLINE
        "UPDATE_BALANCE_C2C_MANDIRI": "035", #Update Balance Online Mandiri For C2C Deposit Slot, TID, MID, Token
        "TOPUP_ONLINE_DKI": "043", #"Send amount|TID|STAN|MID|InoviceNO|ReffNO "
        "UPDATE_BALANCE_ONLINE_BCA": "044", #BCA UBAL ONLINE TID, MID, Token
        "REVERSAL_ONLINE_BCA": "045", #BCA REVERSAL TID, MID, Token
        "REVERSAL_ONLINE_BRI": "049", #parameter sm dengan update balance bri nya
        "REVERSAL_ONLINE_DKI": "050" #parameter sm dengan top up dki nya
    }
    base_timeout = 60
    if ___cmd in special_timeout_command.values():
        base_timeout = 180
    service_url = LOCAL_URL
    if ___cmd[0] == '0' or ___cmd == 'ST0':
        ___stat, ___resp = 200, module_command(cmd=___cmd, param=___param)
    # elif ___cmd[0] == '5':
    #     # Call GRG Interface Command
    #     ___stat, ___resp = 200, grg_command(cmd=___cmd, param=___param)
    else:
        ___stat, ___resp = _HTTPAccess.get_local(
            url=service_url + ___cmd + '&param=' + ___param,
            __timeout=base_timeout
            )
    # Parse Result
    if ___stat == 200:
        # {"Result":"0","Command":"000","Parameter":"com4","Response":null,"ErrorDesc":"Sukses"}
        if ___resp.get('Command') == ___cmd and ___resp.get('Result') in ['0', '0000'] and ___resp.get('ErrorDesc') != 'Gagal':
            ___output = ___resp.get('Response') if ___resp.get('Response') is not None else ___resp.get('Result')
            # if output is None:
            #     ___output = ___resp.get('Result')
            return 0, ___output
        else:
            _Common.online_logger([___resp], 'service')
            return -1, json.dumps(___resp)
    else:
        _Common.online_logger([___resp], 'service')
        return -1, json.dumps(___resp)

