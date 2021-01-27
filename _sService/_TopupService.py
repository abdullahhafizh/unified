__author__ = "fitrah.wahyudi.imam@gmail.com"

import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _nNetwork import _NetworkAccess
from _dDevice import _QPROX
from _dDAO import _DAO
from _cConfig import _Common, _ConfigParser
from _tTools import _Helper
from time import sleep
from _cCommand import _Command
import json
from _sService import _BniActivationCommand, _MDSService
import traceback


class TopupSignalHandler(QObject):
    __qualname__ = 'TopupSignalHandler'
    SIGNAL_DO_TOPUP_BNI = pyqtSignal(str)
    SIGNAL_CHECK_ONLINE_TOPUP = pyqtSignal(str)
    SIGNAL_DO_ONLINE_TOPUP = pyqtSignal(str)
    SIGNAL_GET_TOPUP_READINESS = pyqtSignal(str)
    SIGNAL_UPDATE_BALANCE_ONLINE = pyqtSignal(str)
    SIGNAL_CHANGE_DENOM = pyqtSignal(str)
    SIGNAL_GET_KIOSK_STATUS = pyqtSignal(str)


TP_SIGNDLER = TopupSignalHandler()
LOGGER = logging.getLogger()

TOPUP_URL = _Common.CORE_HOST
TOPUP_TOKEN = _Common.CORE_TOKEN
TOPUP_MID = _Common.CORE_MID
TOPUP_TID = _Common.TID
TOPUP_ADMIN_FEE = _Common.C2C_ADMIN_FEE[0]
ADMIN_FEE_INCLUDE = True

MANDIRI_GENERAL_ERROR = '51000'
MANDIRI_NO_PENDING = '51003'
BRI_NO_PENDING = 'ZERO BALANCE'
GENERAL_NO_PENDING = 'No Pending Balance'
FW_BANK = _QPROX.FW_BANK
QPROX = _QPROX.QPROX
ERROR_TOPUP = _QPROX.ERROR_TOPUP
BNI_UPDATE_BALANCE_PROCESS = False
LAST_BNI_TOPUP_PARAM = None

# ==========================================================


def start_define_topup_slot_bni():
    _Helper.get_thread().apply_async(define_topup_slot_bni)


def define_topup_slot_bni():
    if not BNI_UPDATE_BALANCE_PROCESS:
        if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
            LOGGER.debug(('START_BNI_SAM_AUTO_UPDATE_SLOT_1', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_1_WALLET)))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_1')
            do_topup_deposit_bni(slot=1, force=True)
        if _Common.BNI_SINGLE_SAM is False and _Common.BNI_SAM_2_WALLET <= _Common.BNI_THRESHOLD:
            LOGGER.debug(('START_BNI_SAM_AUTO_UPDATE_SLOT_2', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_2_WALLET)))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_2')
            do_topup_deposit_bni(slot=2, force=True)
    else:
        LOGGER.warning(('Another BNI_UPDATE_BALANCE_PROCESS Is Running', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_1_WALLET)))


def start_do_topup_deposit_bni(slot):
    _Helper.get_thread().apply_async(do_topup_deposit_bni, (int(slot),))


def start_do_force_topup_bni():
    slot = _Common.BNI_ACTIVE
    force = True
    _Helper.get_thread().apply_async(do_topup_deposit_bni, (int(slot), force, ))


def do_topup_deposit_bni(slot=1, force=False, activation=False):
    global BNI_UPDATE_BALANCE_PROCESS
    try:
        _QPROX.ka_info_bni(slot=_Common.BNI_ACTIVE)
        if _Common.BNI_ACTIVE_WALLET > _Common.BNI_THRESHOLD:
            LOGGER.warning(('DEPOSIT_STILL_SUFFICIENT', slot, _Common.BNI_ACTIVE_WALLET, _Common.BNI_THRESHOLD))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_DEPOSIT_STILL_SUFFICIENT')
            return 'DEPOSIT_STILL_SUFFICIENT'
        # if force is False and _Common.ALLOW_DO_TOPUP is False:
        #     LOGGER.warning(('TOPUP_NOT_ALLOWED', slot, _Common.ALLOW_DO_TOPUP))
        #     TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_TOPUP_NOT_ALLOWED')
        #     return 'TOPUP_NOT_ALLOWED'
        _get_card_data = _QPROX.get_card_info(slot=slot)
        if _get_card_data is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_GET_CARD_INFO_BNI')
            _Common.upload_topup_error('FAILED_GET_CARD_INFO_BNI', slot, 'ADD')
            _Common.online_logger(['BNI Card Data', _get_card_data], 'general')
            return 'FAILED_GET_CARD_INFO_BNI'
        BNI_UPDATE_BALANCE_PROCESS = True
        # prev_balance = _Common.BNI_ACTIVE_WALLET
        _Common.BNI_ACTIVE_WALLET = 0
        _result_pending = pending_balance({
            'card_no': _get_card_data['card_no'],
            'amount': _Common.BNI_TOPUP_AMOUNT,
            'card_tid': _Common.TID_BNI
        })
        # _param_pending = {
        #     'card_no': _get_card_data['card_no'],
        #     'amount': _Common.BNI_TOPUP_AMOUNT,
        #     'card_tid': _Common.TID_BNI,
        #     'invoice_no': 'bni-c2c'+str(_Helper.epoch()),
        #     'time': _Helper.epoch('MDS')
        # }
        # _result_pending = _MDSService.mds_online_topup('BNI', _param_pending)
        if _result_pending is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_PENDING_BALANCE_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            # _Common.online_logger(['BNI Result Pending', _result_pending], 'general')
            return 'FAILED_PENDING_BALANCE_BNI'
        # Waiting Another Deposit Update Balance Process
        wait = 0
        while True:
            wait += 1
            if len(_Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS) == 0:
                break
            if wait >= 3600:
                break
            sleep(1)
        _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS.append(_Helper.whoami())
        _result_ubal = update_balance({
            'card_no': _get_card_data['card_no'],
            'card_info': _get_card_data['card_info'],
            'reff_no': _result_pending['reff_no'],
            'slot': slot
        })
        if _result_ubal is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_UPDATE_BALANCE_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            # _Common.online_logger(['BNI Result Ubal', _result_ubal], 'general')
            return 'FAILED_UPDATE_BALANCE_BNI'
        _send_crypto = _QPROX.bni_crypto_deposit(_result_ubal['card_info'], _result_ubal['dataToCard'], slot=slot)
        if _send_crypto is False:
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_SEND_CRYPTOGRAM_BNI')
            _Common.upload_topup_error(slot, 'ADD')
            # _Common.online_logger(['BNI Send Crypto', _send_crypto], 'general')
            return 'FAILED_SEND_CRYPTOGRAM_BNI'
        else:
            BNI_UPDATE_BALANCE_PROCESS = False
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('SUCCESS_TOPUP_BNI')
            _Common.upload_topup_error(slot, 'RESET')
            # topup_deposit_data = {
            #     "invoice_number": _param_pending['invoice_no'],
            #     "host_reff_number": _result_pending['reff_no'],
            #     "amount": _param_pending['amount'],
            #     "last_deposit": _send_crypto['last_deposit'],
            #     "prev_deposit": _send_crypto['prev_deposit'],
            #     "prev_wallet": _result_pending['prev_wallet'],
            #     "last_wallet": _result_pending['last_wallet'],
            #     "card_no": _param_pending['card_no'],
            #     "transaction_status": 'SUCCESS',
            #     "session_id": _Helper.time_string('%Y%m%d'),
            #     "bank_mid": _Common.MID_BNI,
            #     "bank_tid": _Common.TID_BNI,
            # }
            # _MDSService.start_push_trx_deposit(topup_deposit_data)
            # last_balance = int(prev_balance) + int(_result_ubal['amount'])
            output = {
                'bank': 'BNI',
                'card_no': _get_card_data['card_no'],
                'topup_amount': str(_result_ubal['amount']),
                'last_balance': str(_send_crypto.get('last_balance', 0)),
                'reff_no': _result_ubal['reff_no']
            }
            confirm_bni_topup(output)
            send_kiosk_status()
            return 'SUCCESS_TOPUP_BNI'
    except Exception as e:
        _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
        LOGGER.warning((str(slot), str(e)))
        TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_TOPUP_BNI')


def bni_reset_update_balance_master():
    slot = 1
    _Helper.get_thread().apply_async(bni_reset_update_balance, (slot,))


def bni_reset_update_balance_slave():
    slot = 2
    _Helper.get_thread().apply_async(bni_reset_update_balance, (slot,))


def bni_reset_update_balance(slot=1, activation=True):
    try:
        _get_card_data = _QPROX.get_card_info(slot=slot)
        if _get_card_data is False:
            return False, 'GET_CARD_DATA_FAILED'
        _result_pending = pending_balance({
            'card_no': _get_card_data['card_no'],
            'amount': '1',
            'card_tid': _Common.TID_BNI,
            'activation': '1'
        })
        if _result_pending is False:
            _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Pending Result', _result_pending], 'general')
            return False, 'ACTIVATION_PENDING_FAILED'
        # Waiting Another Deposit Update Balance Process
        # wait = 0
        # while True:
        #     wait += 1
        #     if len(_Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS) == 0:
        #         break
        #     if wait >= 3600:
        #         break
        #     sleep(1)
        _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS.append(_Helper.whoami())
        _result_ubal = update_balance({
                'card_no': _get_card_data['card_no'],
                'card_info': _get_card_data['card_info'],
                'reff_no': _result_pending['reff_no'],
                'slot': slot
            })
        if not activation:
            return _result_ubal
        if _result_ubal is False:
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Result Ubal', _result_ubal], 'general')
            return False, 'UPDATE_BALANCE_FAILED'
        _send_crypto = _QPROX.bni_crypto_deposit(_get_card_data['card_info'], _result_ubal['dataToCard'], slot=slot)
        if _send_crypto is False:
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Send Crypto', _send_crypto], 'general')
            return False, 'INJECT_CRYPTO_FAILED'
        else:
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            _Common.upload_topup_error(slot, 'RESET')
            _Common.ALLOW_DO_TOPUP = True
            return True, 'RESET_SUCCESS'
    except Exception as e:
        LOGGER.warning((str(slot), str(e)))
        return False, 'SOMETHING_WENT_WRONG'


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
                _Common.online_logger([response, bank, _param], 'general')
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
            LOGGER.debug((str(_param), str(status), str(response)))
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
                _Common.online_logger([response, bank, _param], 'general')
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    elif bank == 'BCA' and mode == 'TOPUP':
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
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bca/pending', param=_param)
            LOGGER.debug((str(_param), str(status), str(response)))
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
                _Common.online_logger([response, bank, _param], 'general')
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
            _param['email'] = _Common.THEME_NAME.lower() + '@mdd.co.id'
            # This Below Key Is Mandatory For Topup Deposit C2C TO Reroute Mandiri Cred
            _param['purpose'] = 'TOPUP_DEPOSIT_C2C'
            status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-mandiri/pending', param=_param)
            LOGGER.debug((str(_param), str(status), str(response)))
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
                _Common.online_logger([response, bank, _param], 'general')
                return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    else:
        LOGGER.warning(('Unknown', bank, mode))
        return False


BNI_REMOTE_ACTIVATION = _Common.BNI_REMOTE_ACTIVATION


def start_deposit_update_balance():
    bank = 'MANDIRI'
    mode = 'TOPUP_DEPOSIT'
    param = QPROX['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
    trigger = 'ADMIN'
    _Helper.get_thread().apply_async(update_balance, (param, bank, mode, trigger))


def update_balance(_param, bank='BNI', mode='TOPUP', trigger=None):
    global LAST_BNI_TOPUP_PARAM, LAST_BCA_REFF_ID
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
            LAST_BNI_TOPUP_PARAM = _param
            while True:
                status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bni/update', param=_param)
                if status != 404:
                    break
                sleep(1)
            LOGGER.debug(('update_balance', str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                response['data']['card_info'] = _param['card_info']
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
                if response['data']['errorCode']=='05' and response['data']['errorDescription'] == 'General error' and BNI_REMOTE_ACTIVATION:
                    bni = _BniActivationCommand.BniActivate()
                    bni_act_resp, bni_act_result = bni.activate_bni_sequence()
                    LOGGER.debug(('remote_deposit_activation_bni', str(bni_act_resp), str(bni_act_result)))
                    if bni_act_resp == 0:
                        while True:
                            _renew_card_data = _QPROX.get_card_info(slot=_param['slot'])
                            if _renew_card_data is not False:
                                break
                            sleep(1)
                        # return update_balance(_param, bank, mode, False)
                        _activation_pending = pending_balance({
                            'card_no': _param['card_no'],
                            'amount': '1',
                            'card_tid': _Common.TID_BNI,
                            'activation': '1'
                        })
                        if _activation_pending is False:
                            _Common.upload_topup_error(_param['slot'], 'ADD')
                            _Common.online_logger(['BNI Activation Pending Result', _activation_pending], 'general')
                            return False
                        return update_balance({
                            'card_no': _renew_card_data['card_no'],
                            'card_info': _renew_card_data['card_info'],
                            'reff_no': _activation_pending['reff_no'],
                            'slot': _param['slot']
                        })
                    else:
                        response['data']['bni_activation_response'] = bni_act_resp
                        response['data']['bni_activation_result'] = bni_act_result
                        _Common.ALLOW_DO_TOPUP = False
                        _Common.online_logger([response, bank, _param], 'general')
                        return False
                else:
                    _Common.ALLOW_DO_TOPUP = False
                    _Common.online_logger([response, bank, _param], 'general')
                    return False
        except Exception as e:
            LOGGER.warning((bank, mode, e))
            return False
    elif bank == 'BRI' and mode == 'TOPUP':
        try:
            response, result = _Command.send_request(param=_param, output=None)
            # {"Result":"0000","Command":"024","Parameter":"01234567|1234567abc|165eea86947a4e9483d1902f93495fc6|3",
            # "Response":"6013500601505143|1000|66030","ErrorDesc":"Sukses"}
            LOGGER.debug((_param, bank, mode, response, result))
            if response == 0 and '|' in result:
                card_no = result.split('|')[0]
                # _Common.remove_temp_data(card_no)
                return {
                    'bank': bank,
                    'card_no': card_no,
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
            else:
                _Common.online_logger([response, bank, _param], 'general')
                return False
        except Exception as e:
            LOGGER.warning(str(e))
            return False
    elif bank == 'BCA' and mode == 'TOPUP':
        try:
            response, result = _Command.send_request(param=_param, output=None)
            # {"Result":"0000","Command":"024","Parameter":"01234567|1234567abc|165eea86947a4e9483d1902f93495fc6|3",
            # "Response":"0145000100018635|20000|298500|01010124014500010001863500298500000200002021011105192209013149124254455354444556454C5A5359423031885000942678845E374B6E1B1C4B8A025E180B1B0202180B1C1B373D4E1B5E6E026E27276E5E1C4B4B5E4E4B4B8A0B1C4E378A8A4B278A4B1B1C4E5E02023D1B4B27370B5E378A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4E278A4B844E378482820B3D828A0B840B4E274B8A6E3718820B020B0B3D4B8A848A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4EF4C2998190093B0DB181","ErrorDesc":"Sukses"}
            LOGGER.debug((_param, bank, mode, response, result))
            if response == 0 and '|' in result:
                return {
                    'bank': bank,
                    # 'refference_id': result.split('|')[0],
                    'card_no': result.split('|')[0],
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
            else:
                # 161037128387|BCATopup2_Failed_Card_Reversal_Failed
                service_response = json.loads(result)
                # if 'Response' in service_response.keys():
                #     if '|' in service_response['Response']:
                #         result = service_response['Response'].split('|')[1]
                #         LAST_BCA_REFF_ID = service_response['Response'].split('|')[0]
                #         LOGGER.debug(('Setting Value', 'LAST_BCA_REFF_ID', LAST_BCA_REFF_ID))
                if service_response['Result'] in BCA_TOPUP_ONLINE_ERROR or BCA_KEY_REVERSAL in result:
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_PARTIAL_ERROR')
                    # Store Local Card Number Here For Futher Reversal Process
                    previous_card_no = _QPROX.LAST_BALANCE_CHECK['card_no']
                    previous_card_data = _QPROX.LAST_BALANCE_CHECK
                    # previous_card_data['refference_id'] = LAST_BCA_REFF_ID
                    _Common.store_to_temp_data(previous_card_no, json.dumps(previous_card_data))
                    reset_bca_session()
                    return
                _Common.online_logger([response, bank, _param], 'general')
                return False
        except Exception as e:
            LOGGER.warning(str(e))
            return False
    elif bank == 'MANDIRI' and mode == 'TOPUP_DEPOSIT':
        message_error = 'UPDATE_ERROR'
        try:
            response, result = _Command.send_request(param=_param, output=None)
            LOGGER.debug((bank, mode, response, result))
            # if _Common.TEST_MODE is True and _Common.empty(result):
            #   result = '6032111122223333|20000|198000'
            r = result.split('|')
            if response == 0 and result is not None:
                _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
                output = {
                    'bank': bank,
                    'card_no': r[0],
                    'topup_amount': r[1],
                    'last_balance': r[2],
                }
                response = output
            else:
                if 'No Pending Balance' in result:
                    message_error = 'NO_PENDING_BALANCE'
                response = False
        except Exception as e:
            _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            LOGGER.warning(str(e))
            response = False
        finally:
            if not _Helper.empty(response):
                if not _Helper.empty(LAST_MANDIRI_C2C_SUCCESS_RESULT):
                    prev_balance = LAST_MANDIRI_C2C_SUCCESS_RESULT['prev_deposit_balance']
                    amount = LAST_MANDIRI_C2C_SUCCESS_RESULT['amount']
                    if response['last_balance'] == response['topup_amount']:
                        response['last_balance'] = str(int(response['topup_amount']) + int(prev_balance))
                    output = {
                                'prev_wallet': LAST_MANDIRI_C2C_SUCCESS_RESULT['prev_wallet'],
                                'last_wallet': LAST_MANDIRI_C2C_SUCCESS_RESULT['last_wallet'],
                                'prev_balance': prev_balance,
                                'last_balance': response['last_balance'],
                                'report_sam': 'N/A',
                                'card_no': LAST_MANDIRI_C2C_SUCCESS_RESULT['card_no'],
                                'report_ka': 'N/A',
                                'bank_id': '1',
                                'bank_name': 'MANDIRI',
                        }
                    # Do Update Deposit Balance Value in Memory
                    _Common.MANDIRI_ACTIVE_WALLET = int(response['last_balance'])
                    _Common.MANDIRI_WALLET_1 = int(response['last_balance'])
                    # Do Upload SAM Refill Status Into BE Asyncronous
                    sam_audit_data = {
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
                    _DAO.create_today_report(_Common.TID)
                    _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_count'], 1)
                    _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_amount'], int(amount))
                    _DAO.update_today_summary_multikeys(['mandiri_deposit_last_balance'], int(output['last_balance']))
                    _Common.store_upload_sam_audit(sam_audit_data)   
                    # topup_deposit_data = {
                    #     "invoice_number": LAST_MANDIRI_C2C_SUCCESS_RESULT['invoice_no'],
                    #     "host_reff_number": LAST_MANDIRI_C2C_SUCCESS_RESULT['time'],
                    #     "amount": amount,
                    #     "last_deposit": output['last_balance'],
                    #     "prev_deposit": output['prev_balance'],
                    #     "prev_wallet": LAST_MANDIRI_C2C_SUCCESS_RESULT['prev_wallet'],
                    #     "last_wallet": LAST_MANDIRI_C2C_SUCCESS_RESULT['last_wallet'],
                    #     "card_no": LAST_MANDIRI_C2C_SUCCESS_RESULT['card_no'],
                    #     "transaction_status": 'SUCCESS',
                    #     "session_id": _Helper.time_string('%Y%m%d'),
                    #     "bank_mid": _Common.C2C_MID,
                    #     "bank_tid": _Common.C2C_TID,
                    # }
                    # _MDSService.start_push_trx_deposit(topup_deposit_data)
                send_kiosk_status()
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|SUCCESS')
            else:
                if trigger is not None:
                    TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|'+message_error)
            return response
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
    _Helper.get_thread().apply_async(auto_refill_zero_bni, (slot,))
    
    
def auto_refill_zero_bni(slot):
    bni = _BniActivationCommand.BniActivate()
    bni_act_resp, bni_act_result = bni.activate_bni_sequence()
    LOGGER.debug(('remote_deposit_activation_bni', str(bni_act_resp), str(bni_act_result)))
    if bni_act_resp == 0:
        reset_result, result_message = bni_reset_update_balance(slot=1, activation=True)
        if reset_result is True:
            _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|AUTO_ACTIVATION_SUCCESS')
        else:
            _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|'+result_message)  
    else:
        _Common.ALLOW_DO_TOPUP = True
        _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|ERROR_AUTO_ACTIVATION')


def start_slave_activation_bni():
    slot = 2
    _Helper.get_thread().apply_async(refill_zero_bni, (slot,))


def refill_zero_bni(slot=1):
    _slot = slot - 1
    param = _QPROX.QPROX['REFILL_ZERO'] + '|' + str(_slot) + '|' + _QPROX.TID_BNI
    response, result = _Command.send_request(param=param, output=None)
    if response == 0:
        _Common.NFC_ERROR = ''
        sleep(2)
        reset_result, result_message = bni_reset_update_balance(slot=1, activation=True)
        if reset_result is True:
            _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|SUCCESS')
        else:
            _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|'+result_message)
    else:
        if slot == 1:
            _Common.NFC_ERROR = 'REFILL_ZERO_SLOT_1_BNI_ERROR'
        if slot == 2:
            _Common.NFC_ERROR = 'REFILL_ZERO_SLOT_2_BNI_ERROR'
        _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO_ERROR')


def remote_deposit_activation_bni(slot=1):
    _slot = slot - 1
    # param = _QPROX.QPROX['RAW_APDU']+'|'+str(4)+'|'+'0084000008'
    # bni = _BniActivationCommand.BniActivate()
    # response, result = bni.activate_bni_sequence()
    # response, result = bni.activate_bni_sequence()
    try:
        activation_result = False
        bni = _BniActivationCommand.BniActivate()
        bni_act_resp, bni_act_result = bni.activate_bni_sequence()
        LOGGER.debug((str(bni_act_resp), str(bni_act_result)))
        if bni_act_resp == 0:
            _param = LAST_BNI_TOPUP_PARAM
            activation_result = update_balance(_param, 'BNI', 'TOPUP', False)
        else:
            _Common.ALLOW_DO_TOPUP = False
            _Common.online_logger([bni_act_result, 'BNI', _param], 'general')
            activation_result = False
        LOGGER.debug((str(activation_result)))        
        sleep(1)
    except Exception as e:
        LOGGER.debug((traceback.format_exc()))


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
    global ADMIN_FEE_INCLUDE
    try:
        ready = {
            # 'balance_mds': str(_Common.MDS_WALLET),
            'balance_mandiri': str(_Common.MANDIRI_ACTIVE_WALLET),
            'balance_bni': str(_Common.BNI_ACTIVE_WALLET),
            'bni_wallet_1': str(_Common.BNI_SAM_1_WALLET),
            'bni_wallet_2': str(_Common.BNI_SAM_2_WALLET),
            'mandiri': 'AVAILABLE' if (_QPROX.INIT_MANDIRI is True and _Common.MANDIRI_ACTIVE_WALLET > 0) is True else 'N/A',
            'bni': 'AVAILABLE' if (_QPROX.INIT_BNI is True and _Common.BNI_ACTIVE_WALLET > 0) is True else 'N/A',
            'bri': 'N/A',
            'bca': 'N/A',
            'dki': 'AVAILABLE' if (_Common.DKI_TOPUP_ONLINE_BY_SERVICE is True) else 'N/A',
            'emoney': _Common.TOPUP_AMOUNT_SETTING['emoney'],
            'tapcash': _Common.TOPUP_AMOUNT_SETTING['tapcash'],
            'brizzi': _Common.TOPUP_AMOUNT_SETTING['brizzi'],
            'flazz': _Common.TOPUP_AMOUNT_SETTING['flazz'],
            'jakcard': _Common.TOPUP_AMOUNT_SETTING['jakcard'],
            'admin_include': _ConfigParser.get_set_value('TEMPORARY', 'admin^include', '1'),
            'printer_setting': '1' if _ConfigParser.get_set_value('PRINTER', 'printer^type', 'Default') == 'Default' else '0',
        }
        ADMIN_FEE_INCLUDE = True if ready['admin_include'] == '1' else False
        # Assuming always check card balance first before check topup readiness validation
        if _QPROX.LAST_BALANCE_CHECK['bank_name'] == 'BRI':
            ready['bri'] = 'AVAILABLE' if (_Common.BRI_SAM_ACTIVE is True and ping_online_topup(mode='BRI', trigger=False) is True) else 'N/A'
        if _QPROX.LAST_BALANCE_CHECK['bank_name'] == 'BCA':
            ready['bca'] = 'AVAILABLE' if _Common.BCA_TOPUP_ONLINE is True else 'N/A'
        # if _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
        #     ready['balance_mandiri'] = '999001'
        #     ready['balance_bni'] = '999002'
        #     ready['mandiri'] = 'AVAILABLE'
        #     ready['bni'] = 'AVAILABLE'
        #     ready['bri'] = 'AVAILABLE'
        #     ready['bca'] = 'AVAILABLE'
        #     ready['dki'] = 'AVAILABLE'
        LOGGER.info((str(ready)))
        TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit(json.dumps(ready))
    except Exception as e:
        LOGGER.warning((str(e)))
        TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit('ERROR')


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


BCA_KEY_REVERSAL = 'UpdateAPI_Failed_Reversal_Success' #'BCATopup1_Failed'
BCA_KEY_PARTIAL = 'UpdateAPI_Failed_Card_Reversal_Failed' #'BCATopup1_Failed'
BCA_TOPUP_ONLINE_ERROR = ['8041', '1407', '2B45']


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
                    last_balance = int(_QPROX.LAST_BALANCE_CHECK['balance']) + int(crypto_data['amount'])
                    output = {
                        'bank': bank,
                        'card_no': card_info[4:20],
                        'topup_amount': str(crypto_data['amount']),
                        'last_balance': str(last_balance),
                        'reff_no': crypto_data.get('reff_no', _Helper.time_string(f='%Y%m%d%H%M%S'))
                    }
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|SUCCESS|'+json.dumps(output))
                    confirm_bni_topup(output)
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
                card_no = result.split('|')[0]
                output = {
                    'bank': bank,
                    'card_no': card_no,
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
                # _Common.remove_temp_data(card_no)
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
    elif bank == 'BCA':
        try:
            param = QPROX['UPDATE_BALANCE_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            response, result = _Command.send_request(param=param, output=None)
            # result : "161037084533|0145000100018635|20000|298500|01010124014500010001863500298500000200002021011105192209013149124254455354444556454C5A5359423031885000942678845E374B6E1B1C4B8A025E180B1B0202180B1C1B373D4E1B5E6E026E27276E5E1C4B4B5E4E4B4B8A0B1C4E378A8A4B278A4B1B1C4E5E02023D1B4B27370B5E378A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4E278A4B844E378482820B3D828A0B840B4E274B8A6E3718820B020B0B3D4B8A848A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4E8A4B0B060B1B848A18843D5E06183D4EF4C2998190093B0DB181","ErrorDesc":"Sukses"}
            if response == 0 and '|' in result:
                card_no = result.split('|')[0]
                output = {
                    'bank': bank,
                    'card_no': card_no,
                    # 'refference_id': result.split('|')[0],
                    'topup_amount': result.split('|')[1],
                    'last_balance': result.split('|')[2],
                }
                _Common.remove_temp_data(card_no)
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|SUCCESS|'+json.dumps(output))
            else:
                if GENERAL_NO_PENDING in result:
                    _Common.remove_temp_data(card_no)
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|NO_PENDING_BALANCE')
                else:
                    if BCA_KEY_REVERSAL in result:
                        # Store Local Card Number Here For Futher Reversal Process
                        previous_card_no = _QPROX.LAST_BALANCE_CHECK['card_no']
                        previous_card_data = _QPROX.LAST_BALANCE_CHECK
                        _Common.store_to_temp_data(previous_card_no, json.dumps(previous_card_data))
                        # TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|BCA_NEED_REVERSAL')
                        # param_reversal = QPROX['REVERSAL_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
                        # response_reversal, result_reversal = _Command.send_request(param=param, output=None)
                        # LOGGER.debug((param_reversal, response_reversal, result_reversal))
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
            LOGGER.debug((result, response))
        except Exception as e:
            LOGGER.warning(str(e))
            TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
    else:
        TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')


def start_retry_topup_online_bca(amount, trxid):
    _Helper.get_thread().apply_async(retry_topup_online_bca, (amount, trxid,))


def retry_topup_online_bca(amount, trxid):
    previous_card_no = _QPROX.LAST_BALANCE_CHECK['card_no']
    previous_card_balance = _QPROX.LAST_BALANCE_CHECK['balance']
    check_card_balance = _QPROX.direct_card_balance()
    #  output = {
    #     'balance': balance,
    #     'card_no': card_no,
    #     'bank_type': bank_type,
    #     'bank_name': bank_name,
    #     # 'able_topup': result.split('|')[3].replace('#', ''),
    #     'able_check_log': able_check_log,
    #     'able_topup': '0000', #Force Allowed Topup For All Non BNI
    # }
    if not check_card_balance:
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_PARTIAL_ERROR')
        return
    if previous_card_no != check_card_balance['card_no']:
        LOGGER.warning(('BCA_CARD_MISSMATCH', trxid, previous_card_no, check_card_balance['card_no']))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        return
    bca_card_info = _QPROX.bca_card_info()
    if bca_card_info is False:
        LOGGER.warning(('BCA_CARD_INFO_FAILED', trxid, bca_card_info))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
        return
    if int(amount) + int(previous_card_balance) == int(check_card_balance['balance']):
        # Success Topup Here
        output = {
                # 'prev_wallet': pending_result['prev_wallet'],
                # 'last_wallet': pending_result['last_wallet'],
                'last_balance': check_card_balance['balance'],
                'topup_amount': amount,
                'other_channel_topup': str(0),
                'report_sam': 'N/A',
                'card_no': check_card_balance['card_no'],
                'report_ka': 'N/A',
                'bank_id': '4',
                'bank_name': 'BCA',
            }
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        _Common.remove_temp_data(trxid)
        _Common.remove_temp_data(previous_card_no)
    else:
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
    confirm_bca_topup({
        'card_data': bca_card_info,
        'card_no': check_card_balance['card_no'],
        'last_balance': check_card_balance['balance']
    })
    
    
def start_topup_online_dki(amount, trxid):
    if _Common.DKI_TOPUP_ONLINE_BY_SERVICE is True:
        return _QPROX.start_topup_dki_by_service(amount, trxid)
    else:
        LOGGER.warning(('NO AVAILABLE DKI TOPUP SERVICE DEFINED'))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')


def start_topup_online_bri(cardno, amount, trxid):
    bank = 'BRI'
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount, trxid,))


def start_topup_online_bca(cardno, amount, trxid):
    bank = 'BCA'
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount, trxid,))


LAST_MANDIRI_C2C_SUCCESS_RESULT = None
LAST_BCA_REFF_ID = ''


def topup_online(bank, cardno, amount, trxid=''):
    global LAST_MANDIRI_C2C_SUCCESS_RESULT
    # if bank in ['BRI', 'BCA'] and _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
    #     sleep(2)
    #     output = {
    #             'last_balance': '999999',
    #             'report_sam': 'DUMMY',
    #             'card_no': _QPROX.LAST_BALANCE_CHECK['card_no'],
    #             'report_ka': 'DUMMY',
    #             'bank_id': '3' if bank == 'BRI' else '4',
    #             'bank_name': bank,
    #             'dummy_trx': '1',
    #             'prev_wallet': _Common.MDS_WALLET
    #         }
    #     _MDSService.do_deduct_wallet({
    #         'amount': amount,
    #         'trx_ref': trxid,
    #         'trx_desc': " ".join(['Dummy Topup Online Prepaid', bank, output['card_no']])
    #     })
    #     output['last_wallet'] = _Common.MDS_WALLET
    #     _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
    #     return
    # LAST_BALANCE_CHECK = {
    #     'balance': balance,
    #     'card_no': card_no,
    #     'bank_type': result.split('|')[2].replace('#', ''),
    #     'bank_name': bank_name,
    #     'able_topup': '0000',
    # }
    try:
        if bank is None or bank not in _Common.ALLOWED_BANK_PENDING_ONLINE:
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
            return
        last_card_check = _QPROX.LAST_BALANCE_CHECK
        if bank == 'BRI':
            if not _Common.BRI_SAM_ACTIVE:
                _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR_BRI_SAM_SLOT_NOT_FOUND')
                return
            _param = {
                'card_no': cardno,
                'amount': amount,
                'invoice_no': trxid,
                'time': _Helper.epoch('MDS')
            }
            # pending_result = _MDSService.mds_online_topup(bank, _param)
            if not _Common.exist_temp_data(trxid):
                pending_result = pending_balance(_param, bank='BRI', mode='TOPUP')
                if not pending_result:
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
                    return
                _Common.store_to_temp_data(trxid, json.dumps(_param))
            # _Common.update_to_temp_data('bri-success-pending', trxid)
            _param = QPROX['UPDATE_BALANCE_ONLINE_BRI'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + _Common.SLOT_BRI + '|'
            update_result = update_balance(_param, bank='BRI', mode='TOPUP')
            if not update_result:
                _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BRI_UPDATE_BALANCE_ERROR')
                # Keep Push Data To MDS as Failure
                # failed_data = {
                #     "invoice_number": _param['invoice_no'],
                #     "transaction_status": 'UPDATE_BALANCE_FAILED',
                #     "card_number": _param['card_no'],
                #     "initial_balance": last_card_check['balance'],
                #     "last_balance": last_card_check['balance'],
                #     "amount_topup": str(_param['amount']),
                #     "paid_amount": str(int(_param['amount']) + int(TOPUP_ADMIN_FEE)) if not ADMIN_FEE_INCLUDE else str(_param['amount']),
                #     "admin_fee": TOPUP_ADMIN_FEE,
                #     "bank_name": bank,
                #     "device_timestamp": str(_param['time']),
                #     "host_reff_number": str(_param['time']),
                #     "initial_wallet": pending_result['prev_wallet'],
                #     "last_wallet": pending_result['last_wallet'],
                #     "session_id": _Helper.time_string(f='%d%m%y'),
                # }
                # _MDSService.start_push_trx_online(json.dumps(failed_data))
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
            _Common.remove_temp_data(trxid)
            other_channel_topup = str(0)
            if str(amount) != str(update_result['topup_amount']):
                other_channel_topup = str(int(update_result['topup_amount']) - int(amount))
            output = {
                        # 'prev_wallet': pending_result['prev_wallet'],
                        # 'last_wallet': pending_result['last_wallet'],
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
        elif bank == 'BCA':
            # last_check = _QPROX.LAST_BALANCE_CHECK            
            _param = {
                'card_no': cardno,
                'amount': amount,
                'invoice_no': trxid,
                'time': _Helper.epoch('MDS')
            }
            # if not _Common.exist_temp_data(cardno):
            #     if not _Common.exist_temp_data(trxid):
            #         pending_result = pending_balance(_param, bank='BCA', mode='TOPUP')
            #         # pending_result = _MDSService.mds_online_topup(bank, _param)
            #         if not pending_result:
            #             _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
            #             return
            #         _Common.store_to_temp_data(trxid, json.dumps(_param))
            # else:
            #     LOGGER.debug(('Previous Failed BCA Reversal Detected For', cardno))
            #     param_reversal = QPROX['REVERSAL_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + LAST_BCA_REFF_ID + '|' 
            #     response_reversal, result_reversal = _Command.send_request(param=param_reversal, output=None)
            #     if response_reversal == 0 and '|' in result_reversal:
            #         LOGGER.debug(('Success BCA Reversal For This Card Number', cardno, result_reversal))
            #         _Common.remove_temp_data(cardno)
            #         _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_UPDATE_BALANCE_ERROR')
            #         return
            #     else:
            #         LOGGER.warning(('Failed BCA Reversal For This Card Number', cardno, result_reversal))
            #         _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_UPDATE_BALANCE_ERROR')
            #         return
            if not _Common.exist_temp_data(trxid):
                pending_result = pending_balance(_param, bank='BCA', mode='TOPUP')
                # pending_result = _MDSService.mds_online_topup(bank, _param)
                if not pending_result:
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
                    return
                _Common.store_to_temp_data(trxid, json.dumps(_param))
            # if _Common.exist_temp_data(cardno):
            #     _param = QPROX['UPDATE_BALANCE_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            # else:
            #     _param = QPROX['REVERSAL_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            _param = QPROX['UPDATE_BALANCE_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            update_result = update_balance(_param, bank='BCA', mode='TOPUP')
            if not update_result:
                _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_UPDATE_BALANCE_ERROR')
                return
            _Common.remove_temp_data(trxid)
            if _Common.exist_temp_data(cardno):
                _Common.remove_temp_data(cardno)
                # Keep Push Data To MDS as Failure
                # failed_data = {
                #     "invoice_number": _param['invoice_no'],
                #     "transaction_status": 'UPDATE_BALANCE_FAILED',
                #     "card_number": _param['card_no'],
                #     "initial_balance": last_card_check['balance'],
                #     "last_balance": last_card_check['balance'],
                #     "amount_topup": str(_param['amount']),
                #     "paid_amount": str(int(_param['amount']) + int(TOPUP_ADMIN_FEE)) if not ADMIN_FEE_INCLUDE else str(_param['amount']),
                #     "admin_fee": TOPUP_ADMIN_FEE,
                #     "bank_name": bank,
                #     "device_timestamp": str(_param['time']),
                #     "host_reff_number": str(_param['time']),
                #     "initial_wallet": pending_result['prev_wallet'],
                #     "last_wallet": pending_result['last_wallet'],
                #     "session_id": _Helper.time_string(f='%d%m%y'),
                # }
                # _MDSService.start_push_trx_online(json.dumps(failed_data))
                # return
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
                        # 'prev_wallet': pending_result['prev_wallet'],
                        # 'last_wallet': pending_result['last_wallet'],
                        'last_balance': update_result['last_balance'],
                        'topup_amount': update_result['topup_amount'],
                        'other_channel_topup': other_channel_topup,
                        'report_sam': 'N/A',
                        'card_no': update_result['card_no'],
                        'report_ka': 'N/A',
                        'bank_id': '4',
                        'bank_name': 'BCA',
                }
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        elif bank == 'MANDIRI_C2C_DEPOSIT':
            param = {
                'card_no': cardno,
                'amount': amount,
                'invoice_no': 'mdr-c2c'+str(_Helper.epoch()),
                'time': _Helper.epoch('MDS')
            }
            # pending_result = _MDSService.mds_online_topup(bank, param)
            pending_result = pending_balance(param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
            if not pending_result:
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|PENDING_ERROR')
                _Common.online_logger([pending_result, bank, cardno, amount], 'general')
                return False
            # Do Reset Memory Mandiri C2C Wallet To Prevent Usage (Miss Match Card Info)
            prev_balance = _Common.MANDIRI_ACTIVE_WALLET
            # param['prev_deposit_balance'] = prev_balance
            # LAST_MANDIRI_C2C_SUCCESS_RESULT = {**param, **pending_result}
            LAST_MANDIRI_C2C_SUCCESS_RESULT = param.update(pending_result)
            # LOGGER.debug(('LAST_MANDIRI_C2C_SUCCESS_RESULT', str(LAST_MANDIRI_C2C_SUCCESS_RESULT)))
            _Common.MANDIRI_ACTIVE_WALLET = 0
            send_kiosk_status()
            _param = QPROX['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
            update_result = update_balance(_param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
            if not update_result:
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|UPDATE_ERROR')
                _Common.online_logger([update_result, bank, cardno, amount], 'general')
                return False
            if update_result['last_balance'] == update_result['topup_amount']:
                update_result['last_balance'] = str(int(update_result['topup_amount']) + int(prev_balance))
            output = {
                        # 'prev_wallet': pending_result['prev_wallet'],
                        # 'last_wallet': pending_result['last_wallet'],
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
            sam_audit_data = {
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
            _Common.store_upload_sam_audit(sam_audit_data)   
            # topup_deposit_data = {
            #     "invoice_number": param['invoice_no'],
            #     "host_reff_number": param['time'],
            #     "amount": amount,
            #     "last_deposit": output['last_balance'],
            #     "prev_deposit": output['prev_balance'],
            #     "prev_wallet": pending_result['prev_wallet'],
            #     "last_wallet": pending_result['last_wallet'],
            #     "card_no": update_result['card_no'],
            #     "transaction_status": 'SUCCESS',
            #     "session_id": _Helper.time_string('%Y%m%d'),
            #     "bank_mid": _Common.C2C_MID,
            #     "bank_tid": _Common.C2C_TID,
            # }
            # _MDSService.start_push_trx_deposit(topup_deposit_data)
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|REFILL_SUCCESS')
            send_kiosk_status()
            return output        
        else:
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
    except Exception as e:
        LOGGER.warning((bank, cardno, amount, e))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP|ERROR')
    

def start_do_topup_c2c_deposit():
    bank = 'MANDIRI_C2C_DEPOSIT'
    cardno = _Common.C2C_DEPOSIT_NO
    amount = _Common.C2C_TOPUP_AMOUNT
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount, ))


def confirm_bni_topup(data):
    if _Helper.empty(data):
        return False
    LOGGER.info((str(data)))
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID,
            'reff_no': data['reff_no'],
            'card_no': data['card_no'],
            'last_balance': data['last_balance']
        }
        status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bni/confirm', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = 'topup-bni/confirm'
            _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-bni/confirm', payload=param)
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def confirm_bca_topup(data):
    if _Helper.empty(data):
        return False
    LOGGER.info((str(data)))
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID,
            'card_data': data['card_data'],
            'card_no': data['card_no'],
            'last_balance': data['last_balance']
        }
        status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bca/confirm', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = 'topup-bca/confirm'
            _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-bca/confirm', payload=param)
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


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
            # _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-bri/refund', payload=param)
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False
    

def get_mandiri_card_blocked_list():
    if not _Common.MANDIRI_CHECK_CARD_BLOCKED or _Common.MANDIRI_CARD_BLOCKED_URL == '---':
        LOGGER.debug(('MANDIRI_CARD_BLOCKED_LIST DISABLED'))
        _Common.MANDIRI_CARD_BLOCKED_LIST = []
        return False
    try:
        status, response = _NetworkAccess.get_from_url(url=_Common.MANDIRI_CARD_BLOCKED_URL)
        if status == 200 and response['response']['code'] == 200:
            if not _Helper.empty(response['data']['blacklist']):
                content = ''
                for data in response['data']['blacklist']:
                    content += data + '\n'
                _Common.store_to_temp_data('mandiri_card_blocked_list', content)
                _Common.MANDIRI_CARD_BLOCKED_LIST = response['data']['blacklist']
                LOGGER.info(('MANDIRI_CARD_BLOCKED_LIST UPDATED'))
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def start_change_denom(seq, amount):
    _Helper.get_thread().apply_async(change_denom, (seq, amount),)


def change_denom(seq, amount):
    # print(_Helper.whoami())
    result = _Common.change_denom(seq, amount)
    if result is True:
        TP_SIGNDLER.SIGNAL_CHANGE_DENOM.emit('TOPUP_CHANGE_DENOM|SUCCESS')
    else:
        TP_SIGNDLER.SIGNAL_CHANGE_DENOM.emit('TOPUP_CHANGE_DENOM|ERROR')


def send_kiosk_status():
    data = _Common.kiosk_status_data()
    TP_SIGNDLER.SIGNAL_GET_KIOSK_STATUS.emit(json.dumps(data))
    

def reset_bca_session():
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID
        }
        status, response = _NetworkAccess.post_to_url(url=TOPUP_URL + 'topup-bca/reset-session', param=param)
        LOGGER.debug((str(status), str(response)))
    except Exception as e:
        LOGGER.warning((e))
