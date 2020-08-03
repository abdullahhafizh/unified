__author__ = "fitrah.wahyudi.imam@gmail.com"

import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _nNetwork import _NetworkAccess
from _dDevice import _QPROX
from _dDAO import _DAO
from _cConfig import _Common
from _tTools import _Helper
from time import sleep
from _cCommand import _Command
import json


class TopupSignalHandler(QObject):
    __qualname__ = 'TopupSignalHandler'
    SIGNAL_DO_TOPUP_BNI = pyqtSignal(str)
    SIGNAL_CHECK_ONLINE_TOPUP = pyqtSignal(str)
    SIGNAL_DO_ONLINE_TOPUP = pyqtSignal(str)
    SIGNAL_GET_TOPUP_READINESS = pyqtSignal(str)
    SIGNAL_UPDATE_BALANCE_ONLINE = pyqtSignal(str)



TP_SIGNDLER = TopupSignalHandler()
LOGGER = logging.getLogger()

TOPUP_URL = _Common.CORE_HOST
TOPUP_TOKEN = _Common.CORE_TOKEN
TOPUP_MID = _Common.CORE_MID
TOPUP_TID = _Common.TID

MANDIRI_GENERAL_ERROR = '51000'
MANDIRI_NO_PENDING = '51003'
BRI_NO_PENDING = 'ZERO BALANCE'
FW_BANK = _QPROX.FW_BANK
QPROX = _QPROX.QPROX
ERROR_TOPUP = _QPROX.ERROR_TOPUP
# ==========================================================


def start_define_topup_slot_bni():
    _Helper.get_thread().apply_async(define_topup_slot_bni)


BNI_UPDATE_BALANCE_PROCESS = False


def define_topup_slot_bni():
    while True:
        if not BNI_UPDATE_BALANCE_PROCESS:
            if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
                LOGGER.debug(('START_BNI_SAM_AUTO_UPDATE_SLOT_1', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_1_WALLET)))
                TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_1')
                do_topup_deposit_bni(slot=1, force=True)
            if _Common.BNI_SINGLE_SAM is False and _Common.BNI_SAM_2_WALLET <= _Common.BNI_THRESHOLD:
                LOGGER.debug(('START_BNI_SAM_AUTO_UPDATE_SLOT_2', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_2_WALLET)))
                TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_2')
                do_topup_deposit_bni(slot=2, force=True)
        sleep(30)


def start_do_topup_deposit_bni(slot):
    _Helper.get_thread().apply_async(do_topup_deposit_bni, (int(slot),))


def start_do_force_topup_bni():
    slot = _Common.BNI_ACTIVE
    force = True
    _Helper.get_thread().apply_async(do_topup_deposit_bni, (int(slot), force, ))


def do_topup_deposit_bni(slot=1, force=False):
    global BNI_UPDATE_BALANCE_PROCESS
    try:
        _QPROX.ka_info_bni(slot=_Common.BNI_ACTIVE)
        if _Common.BNI_ACTIVE_WALLET > _Common.BNI_THRESHOLD:
            LOGGER.warning((slot, _Common.BNI_ACTIVE_WALLET, _Common.BNI_THRESHOLD))
            return 'DEPOSIT_STILL_SUFFICIENT'
        if force is False and _Common.ALLOW_DO_TOPUP is False:
            LOGGER.warning((slot, _Common.ALLOW_DO_TOPUP))
            return 'TOPUP_NOT_ALLOWED'
        _get_card_data = _QPROX.get_card_info(slot=slot)
        if _get_card_data is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_GET_CARD_INFO_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_GET_CARD_INFO_BNI'
        BNI_UPDATE_BALANCE_PROCESS = True
        _Common.BNI_ACTIVE_WALLET = 0
        _result_pending = pending_balance({
            'card_no': _get_card_data['card_no'],
            'amount': _Common.BNI_TOPUP_AMOUNT,
            'card_tid': _Common.TID_BNI
        })
        if _result_pending is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_PENDING_BALANCE_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_PENDING_BALANCE_BNI'
        _result_ubal = update_balance({
            'card_no': _get_card_data['card_no'],
            'card_info': _get_card_data['card_info'],
            'reff_no': _result_pending['reff_no']
        })
        if _result_ubal is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_UPDATE_BALANCE_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_UPDATE_BALANCE_BNI'
        _send_crypto = _QPROX.bni_crypto_deposit(_get_card_data['card_info'], _result_ubal['dataToCard'], slot=slot)
        if _send_crypto is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_SEND_CRYPTOGRAM_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_SEND_CRYPTOGRAM_BNI'
        else:
            BNI_UPDATE_BALANCE_PROCESS = False
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('SUCCESS_TOPUP_BNI')
            _Common.upload_topup_error(slot, 'RESET')
            return 'SUCCESS_TOPUP_BNI'
    except Exception as e:
        LOGGER.warning((str(slot), str(e)))
        TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_TOPUP_BNI')


def bni_reset_update_balance_master():
    slot = 1
    _Helper.get_thread().apply_async(bni_reset_update_balance, (slot,))


def bni_reset_update_balance_slave():
    slot = 2
    _Helper.get_thread().apply_async(bni_reset_update_balance, (slot,))


def bni_reset_update_balance(slot=1):
    try:
        _get_card_data = _QPROX.get_card_info(slot=slot)
        if _get_card_data is False:
            return 'FAILED_GET_CARD_INFO_BNI'
        _result_pending = pending_balance({
            'card_no': _get_card_data['card_no'],
            'amount': '10',
            'card_tid': _Common.TID_BNI,
            'activation': '1'
        })
        if _result_pending is False:
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_PENDING_BALANCE_BNI'
        _result_ubal = update_balance({
            'card_no': _get_card_data['card_no'],
            'card_info': _get_card_data['card_info'],
            'reff_no': _result_pending['reff_no']
        })
        if _result_ubal is False:
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_UPDATE_BALANCE_BNI'
        _send_crypto = _QPROX.bni_crypto_deposit(_get_card_data['card_info'], _result_ubal['dataToCard'], slot=slot)
        if _send_crypto is False:
            _Common.upload_topup_error(slot, 'ADD')
            return 'FAILED_SEND_CRYPTOGRAM_BNI'
        else:
            _Common.upload_topup_error(slot, 'RESET')
            _Common.ALLOW_DO_TOPUP = True
            return 'SUCCESS_RESET_PENDING_BNI'
    except Exception as e:
        LOGGER.warning((str(slot), str(e)))
        return False


def pending_balance(_param, bank='BNI', mode='TOPUP'):
    if bank == 'BNI' and mode == 'TOPUP':
        try:
            # param must be
            # "token":"<<YOUR API-TOKEN>>",
            # "mid":"<<YOUR MERCHANT_ID>>",
            # "tid":"<<YOUR TERMINAL/DEVICE_ID>>",
            # "amount":"30000",
            # "card_no":"7546990000025583"
            # ---> Need Card Number And Amount
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bni/pending', param=_param)
            LOGGER.debug(('pending_balance', str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
            #    {
            #    "response":{
            #       "code":200,
            #       "message":"Pending Balance Success",
            #       "latency":0.43425321578979,
            #       "host":"172.31.254.247"
            #    },
            #    "data":{
            #       "provider":"BRI-Brizzi",
            #       "amount":"8500",
            #       "card_no":"6013500601505143",
            #       "reff_no_trx":"439206",
            #       "reff_no_topup":"202006051651181591350678",
            #       "pending_balance":"25500",
            #       "trx_time":"2020-06-05 16:51:19",
            #       "suspect_status":false,
            #       "paymentId1":"N\/A",
            #       "paymentId2":"N\/A",
            #       "reff_no":"N\/A",
            #       "open_pending":"N\/A",
            #       "prev_amount":"N\/A"
            #    }
            # }
                return response['data']
            else:
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    elif bank == 'BRI' and mode == 'TOPUP':
        try:
            # param must be
            # "token":"<<YOUR API-TOKEN>>",
            # "mid":"<<YOUR MERCHANT_ID>>",
            # "tid":"<<YOUR TERMINAL/DEVICE_ID>>",
            # "amount":"30000",
            # "card_no":"7546990000025583"
            # ---> Need Card Number And Amount
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bri/pending', param=_param)
            LOGGER.debug(('pending_balance', str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                # {
                #    "response":{
                #       "code":200,
                #       "message":"Pending Balance Success",
                #       "latency":1.5800659656525,
                #       "host":"192.168.2.194"
                #    },
                #    "data":{
                #       "provider_id":"BRI - Brizzi",
                #       "amount":"1",
                #       "card_no":"6013500601505143",
                #       "reff_no_trx":"430279",
                #       "reff_no_topup":"202004201042571587354177",
                #       "pending_balance":"1"
                #    }
                # }
                return response['data']
            else:
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    elif bank == 'MANDIRI' and mode == 'TOPUP_DEPOSIT':
        try:
            # "token":"<<YOUR API-TOKEN>>",
            # "mid":"<<YOUR MERCHANT_ID>>",
            # "tid":"<<YOUR TERMINAL/DEVICE_ID>>",
            # "amount":"30000",
            # "card_no":"7546990000025583"
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            _param['phone'] = '08129420492'
            _param['email'] = 'vm@mdd.co.id'
            # This Below Key Is Mandatory For Topup Deposit C2C TO Reroute Mandiri Cred
            _param['purpose'] = 'TOPUP_DEPOSIT_C2C'
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-mandiri/pending', param=_param)
            LOGGER.debug(('pending_balance', str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                # {
                #    "response":{
                #       "code":200,
                #       "message":"Pending Payment Success",
                #       "latency":1.80788397789,
                #       "host":"192.168.2.194"
                #    },
                #    "data":{
                #       "amount":"1510500",
                #       "paymentId1":"6032981000001750",
                #       "paymentId2":"",
                #       "reff_no":"1588745903",
                #       "trx_time":"2020-05-06 13:18:24"
                #    }
                # }
                return response['data']
            else:
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    else:
        LOGGER.warning(('Unknown', bank, mode))
        return False


def update_balance(_param, bank='BNI', mode='TOPUP'):
    if bank == 'BNI' and mode == 'TOPUP':
        try:
            # param must be
            # "token":"<<YOUR API-TOKEN>>",
            # "mid":"<<YOUR MERCHANT_ID>>",
            # "tid":"<<YOUR TERMINAL/DEVICE_ID>>",
            # "reff_no":"20181207180324000511",
            # "card_info":"0001754699000002558375469900000255835A929C0E8DCEC98A95A574DE68D93CBB0
            # 00000000100000088889999040000002D04C36E88889999040000002D04C36E000000000000000000
            # 0079EC3F7C7EED867EBC676CD434082D2F",
            # "card_no":"7546990000025583"
            # ---> Need Card Number, Card Info, Reff_No
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bni/update', param=_param)
            LOGGER.debug(('update_balance', str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                # {
                # "response":{
                #   "code":200,
                #   "message":"Update Balance Success",
                #   "latency":1.4313230514526
                # },
                # "data":{
                #   "amount":"30000",
                #   "auth_id":"164094",
                #   "dataToCard":"06015F902D04C57100000000000000001C54522709845B42F240343E96F11041"
                # }
                # _Common.ALLOW_DO_TOPUP = True
                return response['data']
            else:
                _Common.ALLOW_DO_TOPUP = False
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    elif bank == 'BRI' and mode == 'TOPUP':
        try:
            response, result = _Command.send_request(param=_param, output=None)
            # {"Result":"0000","Command":"024","Parameter":"01234567|1234567abc|165eea86947a4e9483d1902f93495fc6|3",
            # "Response":"6013500601505143|1000|66030","ErrorDesc":"Sukses"}
            if response == 0 and '|' in result:
                return {
                    'bank': bank,
                    'card_no': result.split('|')[0],
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
            else:
                return False
        except Exception as e:
            LOGGER.warning(str(e))
            return False
    elif bank == 'MANDIRI' and mode == 'TOPUP_DEPOSIT':
        try:        
            response, result = _Command.send_request(param=_param, output=None)
            # if _Common.TEST_MODE is True and _Common.empty(result):
            #   result = '6032111122223333|20000|198000'
            r = result.split('|')
            if response == 0 and result is not None:
                output = {
                    'bank': bank,
                    'card_no': r[0],
                    'topup_amount': r[1],
                    'last_balance': r[2],
                }
                return output
            else:
                return False
        except Exception as e:
            LOGGER.warning(str(e))
            return False
    else:
        LOGGER.warning(('Unknown', bank, mode))
        return False


def reversal_balance(_param, bank='BNI', mode='TOPUP'):
    if bank == 'BNI' and mode == 'TOPUP':
        try:
            # param must be
            # "token":"<<YOUR API-TOKEN>>",
            # "mid":"<<YOUR MERCHANT_ID>>",
            # "tid":"<<YOUR TERMINAL/DEVICE_ID>>",
            # "card_no":"7546990000025583",
            # "amount":"30000",
            # "auth_id":"164094",
            # "card_data":"06015F902D04C57100000000000000001C54522709845B42F240343E96F11041"
            # ---> Need Card Number, Card Data, Amount, Auth ID
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bni/reversal', param=_param)
            LOGGER.debug(('reversal_balance', str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                # {
                # "response":{
                #   "code":200,
                #   "message":"Reversal Balance Success",
                #   "latency":2.8180389404297
                # },
                # "data":{
                #   "card_no":"7546990000025583",
                #   "amount":"30000"
                #   }
                # }
                return response['data']
            else:
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    else:
        LOGGER.warning(('Unknown', bank, mode))
        return False


def start_master_activation_bni():
    slot = 1
    _Helper.get_thread().apply_async(refill_zero_bni, (slot,))


def start_slave_activation_bni():
    slot = 2
    _Helper.get_thread().apply_async(refill_zero_bni, (slot,))


def refill_zero_bni(slot=1):
    _slot = slot - 1
    param = _QPROX.QPROX['REFILL_ZERO'] + '|' + str(_slot) + '|' + _QPROX.TID_BNI
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        _Common.NFC_ERROR = ''
        _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|SUCCESS')
        sleep(2)
        bni_reset_update_balance(slot=slot)
    else:
        if slot == 1:
            _Common.NFC_ERROR = 'REFILL_ZERO_SLOT_1_BNI_ERROR'
        if slot == 2:
            _Common.NFC_ERROR = 'REFILL_ZERO_SLOT_2_BNI_ERROR'
        _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO_ERROR')


def start_check_online_topup(mode, payload):
    _Helper.get_thread().apply_async(ping_online_topup, (mode, payload,))


def ping_online_topup(mode, payload=None, trigger=True):
    if mode == 'BRI':
        if payload == None:
            payload = {
                'card_no': '6013500100006619',
                'auto_number': '1'
            }
        else:
            payload = json.loads(payload)
        param = _Common.serialize_payload(payload)
        status, response = _NetworkAccess.post_to_url(_Common.CORE_HOST + 'topup-bri/card-check', param)
        LOGGER.info((response, str(param)))
        if status == 200 and response['response']['code'] == 200:
            if trigger is True:
                TP_SIGNDLER.SIGNAL_CHECK_ONLINE_TOPUP.emit('ONLINE_TOPUP|'+mode+'|AVAILABLE')
            return True
        else:
            if trigger is True:
                TP_SIGNDLER.SIGNAL_CHECK_ONLINE_TOPUP.emit('ONLINE_TOPUP|'+mode+'|N/A')
            return False
    else:
        if trigger is True:
            TP_SIGNDLER.SIGNAL_CHECK_ONLINE_TOPUP.emit('ONLINE_TOPUP|'+mode+'|N/A')
        return False


def start_get_topup_readiness():
    _Helper.get_thread().apply_async(get_topup_readiness)


def get_topup_readiness():
    ready = {
        'balance_mandiri': str(_Common.MANDIRI_ACTIVE_WALLET),
        'balance_bni': str(_Common.BNI_ACTIVE_WALLET),
        'bni_wallet_1': str(_Common.BNI_SAM_1_WALLET),
        'bni_wallet_2': str(_Common.BNI_SAM_2_WALLET),
        'mandiri': 'AVAILABLE' if (_QPROX.INIT_MANDIRI is True and _Common.MANDIRI_ACTIVE_WALLET > 0) is True else 'N/A',
        'bni': 'AVAILABLE' if (_QPROX.INIT_BNI is True and _Common.BNI_ACTIVE_WALLET > 0) is True else 'N/A',
        'bri': 'N/A',
        'bca': 'N/A',
        'dki': 'N/A',
        'emoney': _Common.TOPUP_AMOUNT_SETTING['emoney'],
        'tapcash': _Common.TOPUP_AMOUNT_SETTING['tapcash'],
        'brizzi': _Common.TOPUP_AMOUNT_SETTING['brizzi'],
        'flazz': _Common.TOPUP_AMOUNT_SETTING['flazz'],
        'jakcard': _Common.TOPUP_AMOUNT_SETTING['jakcard'],
    }
    # Assuming always check card balance first before check topup readiness validation
    if _QPROX.LAST_BALANCE_CHECK['bank_name'] == 'BRI':
        ready['bri'] = 'AVAILABLE' if (_Common.BRI_SAM_ACTIVE is True and ping_online_topup(mode='BRI', trigger=False) is True) else 'N/A'
    LOGGER.info((str(ready)))
    TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit(json.dumps(ready))


def start_update_balance_online(bank):
    _Helper.get_thread().apply_async(update_balance_online, (bank,))


def check_update_balance_bni(card_info):
    if card_info is None:
        return False
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID,
            'reff_no': _Helper.time_string(f='%Y%m%d%H%M%S'),
            'card_info': card_info,
            'card_no': card_info[4:20]
        }
        status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bni/update', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            # {
                # "response":{
                #   "code":200,
                #   "message":"Update Balance Success",
                #   "latency":1.4313230514526
                # },
                # "data":{
                #   "amount":"30000",
                #   "auth_id":"164094",
                #   "dataToCard":"06015F902D04C57100000000000000001C54522709845B42F240343E96F11041"
                # }
            # }
            return response['data']
        elif response['response']['code'] == 400 and 'No Pending Balance' in response['response']['message']:
            return 'NO_PENDING_BALANCE'
        else:
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def update_balance_online(bank):
    if bank is None or bank not in _Common.ALLOWED_BANK_UBAL_ONLINE:
        TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|UNKNOWN_BANK')
        return
    if bank == 'MANDIRI':
        try:            
            param = QPROX['UPDATE_BALANCE_ONLINE_MANDIRI'] + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
            response, result = _Command.send_request(param=param, output=None)
            # if _Common.TEST_MODE is True and _Common.empty(result):
            #   result = '6032111122223333|20000|198000'
            if response == 0 and result is not None:
                output = {
                    'bank': bank,
                    'card_no': result.split('|')[0],
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|SUCCESS|'+json.dumps(output))
            else:
                if MANDIRI_GENERAL_ERROR in result:
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|GENERAL_ERROR')
                elif MANDIRI_NO_PENDING in result:
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|NO_PENDING_BALANCE')
                else:
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
            LOGGER.debug((result, response))
        except Exception as e:
            LOGGER.warning(str(e))
            TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
    elif bank == 'BNI':
        try:
            if _QPROX.LAST_BALANCE_CHECK['able_topup'] in ERROR_TOPUP.keys():
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|INVALID_CARD')
                return
            # Do Action List :
            # - Get Purse Data Tapcash
            card_info = _QPROX.get_card_info_tapcash()
            if card_info is False:
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
                return
            # - Request Update Balance BNI
            crypto_data = check_update_balance_bni(card_info)
            if crypto_data is False:
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|GENERAL_ERROR')
                return
            if crypto_data == 'NO_PENDING_BALANCE':
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|NO_PENDING_BALANCE')
                return
            attempt = 0
            while True:
                attempt+=1
                send_crypto_tapcash = _QPROX.bni_crypto_tapcash(crypto_data['dataToCard'], card_info)
                _Helper.dump(send_crypto_tapcash)
                if send_crypto_tapcash is True:
                # - Send Output as Mandiri Specification            
                    output = {
                        'bank': bank,
                        'card_no': card_info[4:20],
                        'topup_amount': str(crypto_data['amount']),
                        'last_balance': '0',
                    }
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|SUCCESS|'+json.dumps(output))
                    break
                if attempt >= 3:
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
                    break
                sleep(1)
        except Exception as e:
            LOGGER.warning(str(e))
            TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
    elif bank == 'BRI':
        try:
            param = QPROX['UPDATE_BALANCE_ONLINE_BRI'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + _Common.SLOT_BRI + '|'
            response, result = _Command.send_request(param=param, output=None)
            if response == 0 and '|' in result:
                output = {
                    'bank': bank,
                    'card_no': result.split('|')[0],
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|SUCCESS|'+json.dumps(output))
            else:
                if BRI_NO_PENDING in result:
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|NO_PENDING_BALANCE')
                else:
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
            LOGGER.debug((result, response))
        except Exception as e:
            LOGGER.warning(str(e))
            TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
    else:
        TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')


def start_topup_online_bri(cardno, amount):
    bank = 'BRI'
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount,))


def topup_online(bank, cardno, amount):
    # LAST_BALANCE_CHECK = {
    #     'balance': balance,
    #     'card_no': card_no,
    #     'bank_type': result.split('|')[2].replace('#', ''),
    #     'bank_name': bank_name,
    #     'able_topup': '0000',
    # }
    if bank is None or bank not in _Common.ALLOWED_BANK_PENDING_ONLINE:
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        return
    if bank == 'BRI':
        if not _Common.BRI_SAM_ACTIVE:
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR_BRI_SAM_SLOT_NOT_FOUND')
            return
        # last_check = _QPROX.LAST_BALANCE_CHECK
        _param = {
            'card_no': cardno,
            'amount': amount
        }
        pending_result = pending_balance(_param, bank='BRI', mode='TOPUP')
        # pending_result = {
                    #   "amount":"30000",
                    #   "card_no":"7546990000025583",
                    #   "reff_no":"20181207180324000511",
                    #   "provider_id":"BNI_TAPCASH",
                    #   "trx_pin":"12345"
                    #   }
        if not pending_result:
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
            return
        _param = QPROX['UPDATE_BALANCE_ONLINE_BRI'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + _Common.SLOT_BRI + '|'
        update_result = update_balance(_param, bank='BRI', mode='TOPUP')
        if not update_result:
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BRI_UPDATE_BALANCE_ERROR')
            # Add Refund BRI
            if _Common.BRI_AUTO_REFUND is True:
                refund_bri_pending(pending_result)
            return
        # {
        #        'bank': bank,
        #        'card_no': result.split('|')[0],
        #        'topup_amount': result.split('|')[1],
        #        'last_balance': result.split('|')[2],
        #     }
        other_channel_topup = str(0)
        if str(amount) != str(update_result['topup_amount']):
            other_channel_topup = str(int(update_result['topup_amount']) - int(amount))
        output = {
                    'last_balance': update_result['last_balance'],
                    'topup_amount': update_result['topup_amount'],
                    'other_channel_topup': other_channel_topup,
                    'report_sam': 'N/A',
                    'card_no': update_result['card_no'],
                    'report_ka': 'N/A',
                    'bank_id': '3',
                    'bank_name': 'BRI',
            }
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
    elif bank == 'MANDIRI_C2C_DEPOSIT':
        param = {
            'card_no': cardno,
            'amount': amount
        }
        pending_result = pending_balance(param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
        if not pending_result:
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|PENDING_ERROR')
            return False
        # Do Reset Memory Mandiri C2C Wallet To Prevent Usage (Miss Match Card Info)
        prev_balance = _Common.MANDIRI_ACTIVE_WALLET
        _Common.MANDIRI_ACTIVE_WALLET = 0
        _param = QPROX['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
        update_result = update_balance(_param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
        if not update_result:
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|UPDATE_ERROR')
            return False
        if update_result['last_balance'] == update_result['topup_amount']:
            update_result['last_balance'] = str(int(update_result['topup_amount']) + int(prev_balance))
        output = {
                    'prev_balance': prev_balance,
                    'last_balance': update_result['last_balance'],
                    'report_sam': 'N/A',
                    'card_no': update_result['card_no'],
                    'report_ka': 'N/A',
                    'bank_id': '1',
                    'bank_name': 'MANDIRI',
            }
        # Do Update Deposit Balance Value in Memory
        _Common.MANDIRI_ACTIVE_WALLET = int(update_result['last_balance'])
        _Common.MANDIRI_WALLET_1 = int(update_result['last_balance'])
        # Do Upload SAM Refill Status Into BE Asyncronous
        param = {
                'trxid': 'REFILL_SAM',
                'samCardNo': _Common.C2C_DEPOSIT_NO,
                'samCardSlot': _Common.C2C_SAM_SLOT,
                'samPrevBalance': output['prev_balance'],
                'samLastBalance': output['last_balance'],
                'topupCardNo': '',
                'topupPrevBalance': output['prev_balance'],
                'topupLastBalance': output['last_balance'],
                'status': 'REFILL_SUCCESS',
                'remarks': output,
            }
        # Update Audit Summary
        # mandiri_deposit_refill_count              BIGINT DEFAULT 0,
        # mandiri_deposit_refill_amount             BIGINT DEFAULT 0,
        # mandiri_deposit_last_balance              BIGINT DEFAULT 0,
        _DAO.create_today_report(_Common.TID)
        _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_count'], 1)
        _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_amount'], int(amount))
        _DAO.update_today_summary_multikeys(['mandiri_deposit_last_balance'], int(output['last_balance']))
        _Common.store_upload_sam_audit(param)   
        TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|REFILL_SUCCESS')
        return output        
    else:
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
    

def start_do_topup_c2c_deposit():
    bank = 'MANDIRI_C2C_DEPOSIT'
    cardno = _Common.C2C_DEPOSIT_NO
    amount = _Common.C2C_TOPUP_AMOUNT
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount, ))


def refund_bri_pending(data):
    if _Helper.empty(data):
        return False
    LOGGER.info((str(data)))
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID,
            'reff_no_host': data['reff_no_trx'],
            'card_no': data['card_no']
        }
        status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bri/refund', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False
    

def get_mandiri_card_blocked_list():
    if not _Common.MANDIRI_CHECK_CARD_BLOCKED or _Common.MANDIRI_CARD_BLOCKED_URL != '---':
        LOGGER.debug(('MANDIRI_CARD_BLOCKED_LIST DISABLED'))
        _Common.MANDIRI_CARD_BLOCKED_LIST = []
        return False
    try:
        status, response = _NetworkAccess.get_from_url(url=_Common.MANDIRI_CARD_BLOCKED_URL)
        if status == 200 and response['response']['code'] == 200:
            if not _Helper.empty(response['data']['blocked']):
                content = ''
                for data in response['data']['blocked']:
                    content += data + '\n'
                _Common.store_to_temp_data('mandiri_card_blocked_list', content)
                _Common.MANDIRI_CARD_BLOCKED_LIST = response['data']
                LOGGER.info(('MANDIRI_CARD_BLOCKED_LIST UPDATED'))
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False