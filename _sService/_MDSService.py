__author__ = "fitrah.wahyudi.imam@gmail.com"

import json
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _Common
from _tTools import _Helper
from _nNetwork import _NetworkAccess
import sys
from operator import itemgetter
from time import sleep


class MDSSignalHandler(QObject):
    __qualname__ = 'MDSSignalHandler'
    SIGNAL_MDS_LOGIN = pyqtSignal(str)
    SIGNAL_MDS_WALLET_BALANCE = pyqtSignal(str)
    SIGNAL_MDS_REGISTER_WALLET = pyqtSignal(str)


MDS_SIGNDLER = MDSSignalHandler()

LOGGER = logging.getLogger()

# MDS GROUP CREDENTIAL
MDS_USER_GROUP = 'tablet-unikpos'
MDS_GROUP_PASS = 'mdd*123'

MDS_HOST = 'https://api-prod.multidaya.id'
if _Common.TEST_MODE:
    MDS_HOST = 'https://api-dev.mdd.co.id' 


def start_mds_login():
    _Helper.get_thread().apply_async(mds_login)


def master_login(master=False):
    payload = {
        'username': MDS_USER_GROUP,
        'password': MDS_GROUP_PASS
    }
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/auth-service/v1/login', param=payload)
    LOGGER.debug((status, response))
    if status == 200 and response['response']['code'] == 200:
        return response['data']['access_token']
    return False


def mds_login():
    payload = {
        'username': _Common.TID,
        "password": _Common.TID+'*un1k',
    }
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/auth-service/v1/login', param=payload)
    LOGGER.debug((status, response))
    # {
    #     "response": {
    #         "code": 200,
    #         "message": "Login success",
    #         "latency": 0.2521390914916992,
    #         "host": "172.18.0.6"
    #     },
    #     "data": {
    #         "name": "TABLET UNIKPOS",
    #         "username": "tablet-unikpos",
    #         "auth_level": "MERCHANT_GROUP",
    #         "gid": "TABLET_UNIKPOS",
    #         "mid": "TABLET_UNIKPOS",
    #         "expired_at": 1607074553,
    #         "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJhdXRoLXNlcnZpY2U6MS4wLjAiLCJzdWIiOnsibmFtZSI6IlRBQkxFVCBVTklLUE9TIiwidXNlcm5hbWUiOiJ0YWJsZXQtdW5pa3BvcyIsImF1dGhfbGV2ZWwiOiJNRVJDSEFOVF9HUk9VUCIsIm1pZCI6IlRBQkxFVF9VTklLUE9TIn0sImlhdCI6MTYwNjk4ODE1MywiZXhwIjoxNjA3MDc0NTUzLCJuYmYiOjE2MDY5ODgxNTV9.gHx7MS8f0u9B-7iaXTzuwvTzQ65VjY9SB9037tYn5GR7IZjm_vZKvNV4aqQ9QqdY0Cvn68ro4XIx94GE3fB9oUH4epVvCvlUeOYhLaT0UYJcZYmJ568qpNmMJuk8oWIeNjk2y52gPBC5h1DSRGkQbXiyjwxqxsYkQS-k38PZ-u2ToXNFgnNr8eGGWgXB28oQOmZtkH6n1Z430dRybL3S6IW_6SKhq274NvCbglFUL44ymwhAzaWiwAuufxGbWu0V7ODBVdUpX_J-RfN5p0hgJB5r96YIfgKOn9aBzfr_nleCaSR300nW0fyaEWarnxxeVYOQlE7aJGdC6S436_uOZA",
    #         "refresh_token": "2613782a55196d2df36253a03e5f2d93cce2f9226a65ff8912f06d52c4c653fa"
    #     }
    # }
    # {
    #     "response": {
    #         "code": 400,
    #         "message": "Wrong username or password",
    #         "latency": 0.036904096603393555,
    #         "host": "172.18.0.6"
    #     },
    #     "data": {}
    # }
    if status == 200 and response['response']['code'] == 200:
        _Common.MDS_TOKEN = response['data']['access_token']
        if merchant_config() is False:
            register_merchant()
        MDS_SIGNDLER.SIGNAL_MDS_LOGIN.emit('MDS_LOGIN|SUCCESS')
        return True
    if status == 200 and response['response']['code'] == 400 and 'Wrong username or password' in response['response']['message']:
        if mds_register() is True:
            mds_login()
    MDS_SIGNDLER.SIGNAL_MDS_LOGIN.emit('MDS_LOGIN|ERROR')
    return False
    

def merchant_config():
    header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer: '+_Common.MDS_TOKEN
    }
    payload = {
        'mid': _Common.MDS_MID
    }
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/merchant-service/v1/get-merchant-config-2', param=payload, header=header)
    LOGGER.debug((status, response))
    if status == 200 and response['response']['code'] == 200 and 'Merchant Configuration Found' in response['response']['message']:
        return True
    return False


def mds_register():
    payload = {
        "username": _Common.TID,
        "password": _Common.TID+'*un1k',
        "name": _Common.KIOSK_NAME,
        "mid": _Common.MDS_MID,
        "auth_level": "MERCHANT"
    } 
    master_token = master_login()
    if _Helper.empty(master_token):
        LOGGER.warning(('MDS Register Failed'))
        return False
    header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer: '+master_token
    }
    sleep(2.5)
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/auth-service/v1/user/create', param=payload, header=header)
    LOGGER.debug((status, response))
    # {
    #     "response": {
    #         "code": 200,
    #         "message": "User created",
    #         "latency": 0.7470471858978271,
    #         "host": "172.18.0.6"
    #     },
    #     "data": {
    #         "id_user": 1606989263,
    #         "username": "TEST-123456",
    #         "name": "Test Terminal",
    #         "auth_level": "MERCHANT",
    #         "created_by": "tablet-unikpos",
    #         "created_at": "2020-12-03 16:54:23"
    #     }
    # }

    # {
    #   "response": {
    #         "code": 400,
    #         "message": "Wrong parameters:|The username has already been taken.",
    #         "latency": 0.038717031478881836,
    #         "host": "172.18.0.6"
    #     },
    #     "data": {}
    # }
    if status == 200 and response['response']['code'] == 200:
        _Common.log_to_temp_config('mds^user^id', response['data']['id_user'])
        if merchant_config() is False:
            register_merchant()
        register_wallet(_Common.MDS_MID)
        return True
    elif status == 200 and response['response']['code'] == 400 and 'username has already been taken' in response['response']['message']:
        return True
    return False


def register_wallet():
    if _Helper.empty(_Common.MDS_TOKEN):
        LOGGER.warning(('Empty Token, MDS Register Wallet Failed'))
        return False
    header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer: '+_Common.MDS_TOKEN
    }
    # {
    #     "response": {
    #         "code": 200,
    #         "message": "Wallet created",
    #         "latency": 0.13592100143432617,
    #         "host": "172.18.0.7"
    #     },
    #     "data": {
    #         "wallet_id": 863
    #     }
    # }
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/wallet-service/v1/create-wallet', header=header)
    LOGGER.debug((status, response))
    if status == 200 and response['response']['code'] == 200 and 'Wallet created' in response['response']['message']:
        _Common.log_to_temp_config('mds^wallet^id', str(response['data']['wallet_id']))
        return True
    return False


def register_merchant():
    if _Helper.empty(_Common.MDS_TOKEN):
        LOGGER.warning(('Empty Token, MDS Register Merchant Failed'))
        return False
    header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer: '+_Common.MDS_TOKEN
    }
    payload = {
        'name': 'Tablet Unik ' + _Common.TID,
        'phone': '081' + _Common.TID.zfill(10),
        'email': _Common.TID+'@multidaya.id',
        'address': 'AXA Tower',
        'pic': 'Tablet Unikpos',
        'type': 'Individual',
        'mid': _Common.MDS_MID
    }
    sleep(2.5)
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/merchant-service/v1/create-merchant-2', param=payload, header=header)
    LOGGER.debug((status, response))
    if status == 200 and response['response']['code'] == 200 and 'Merchant Register Success' in response['response']['message']:
        return True
    return False
    

def start_get_mds_wallet():
    _Helper.get_thread().apply_async(get_mds_wallet)


def get_mds_wallet():
    if _Helper.empty(_Common.MDS_TOKEN):
        LOGGER.warning(('Empty Token, MDS Get Wallet Failed'))
        MDS_SIGNDLER.SIGNAL_MDS_WALLET_BALANCE.emit('MDS_WALLET|0')
        return
    header = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer: '+_Common.MDS_TOKEN
    }
    # {
    #     "response": {
    #         "code": 200,
    #         "message": "Get balance success",
    #         "latency": 1.9398231506347656,
    #         "host": "172.18.0.8"
    #     },
    #     "data": {
    #         "wallet_balance": 0
    #     }
    # }
    status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/wallet-service/v1/get-balance', header=header)
    LOGGER.debug((status, response))
    if status == 200 and response['response']['code'] == 200:
        _Common.MDS_WALLET = int(response['data']['wallet_balance'])
        MDS_SIGNDLER.SIGNAL_MDS_WALLET_BALANCE.emit('MDS_WALLET|'+str(response['data']['wallet_balance']))
    elif response['response']['code'] == 400 and 'Get balance failed' in response['response']['message']:
        register_wallet()
        MDS_SIGNDLER.SIGNAL_MDS_WALLET_BALANCE.emit('MDS_WALLET|0')
    else:
        MDS_SIGNDLER.SIGNAL_MDS_WALLET_BALANCE.emit('MDS_WALLET|0')


def start_mds_sync_config():
    _Helper.get_thread().apply_async(mds_sync_config)


def mds_sync_config():
    try:
        payload = {
            'sn': _Common.TID,
            'mid': _Common.MDS_MID,
            'mandiri_mid': '' if _Common.MID_MAN == '---' else _Common.MID_MAN,
            'mandiri_tid': '' if _Common.TID_MAN == '---' else _Common.TID_MAN,
            'mandiri_pin': '' if _Common.SAM_MAN == '---' else _Common.SAM_MAN,
            'bni_mid': '' if _Common.MID_BNI == '---' else _Common.MID_BNI,
            'bni_tid': '' if _Common.TID_BNI == '---' else _Common.TID_BNI,
            'bni_mc': '' if _Common.MC_BNI == '---' else _Common.MC_BNI,
            'bni_c2c_master_key': '',
            'bni_c2c_mid': '',
            'bni_c2c_tid': '',
            'bni_c2c_initial_vector': '',
            'bni_c2c_pin': '',
            'bri_mid': '' if _Common.MID_BRI == '---' else _Common.MID_BRI,
            'bri_tid': '' if _Common.TID_BRI == '---' else _Common.TID_BRI,
            'bri_procode': '' if _Common.PROCODE_BRI == '---' else _Common.PROCODE_BRI,
            'bca_mid': '' if _Common.MID_BCA == '---' else _Common.MID_BCA,
            'bca_tid': '' if _Common.TID_BCA == '---' else _Common.TID_BCA,
            'dki_mid': '' if _Common.MID_DKI == '---' else _Common.MID_DKI,
            'dki_tid': '' if _Common.TID_DKI == '---' else _Common.TID_DKI,
            'dki_stan_start': _Common.LAST_DKI_STAN,
            'c2c_pin_sam': '' if _Common.C2C_SAM_PIN == '---' else _Common.C2C_SAM_PIN,
            'c2c_pin_ka': '' if _Common.SAM_MAN == '---' else _Common.SAM_MAN,
            'c2c_mactros': _Common.C2C_MACTROS,
            'c2c_mid': '' if _Common.C2C_MID == '---' else _Common.C2C_MID,
            'c2c_tid': '' if _Common.C2C_TID == '---' else _Common.C2C_TID,
            'merchant_name': 'TABLET UNIK - ' + _Common.KIOSK_NAME,
            'merchant_logo': '',
            'merchant_address': 'AXA Tower',
            'merchant_gate_name': _Common.KIOSK_NAME,
            'debug_token': '',
            'user_device': '',
            'pass_device': '',
            'user_tech': '',
            'pass_tech': '',
            'user_diva': '',
            'pass_diva': ''
        }
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        sleep(2.5)
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+'/device-service/edc-config/sync', param=payload, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            LOGGER.info(('MDS Device Sync Success', response['response']['message']))
            return True
        else:
            LOGGER.warning(('MDS Device Sync Failed', response['response']['message']))
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_push_trx_online(payload):
    _Helper.get_thread().apply_async(push_trx_online, (payload,))


# Sample Topup Records
# BNI
# {"date":"30/11/20","epoch":1606718904559311,"payment":"LinkAja","shop_type":"topup","time":"13:48:24","qty":1,"value":"2000",
# "provider":"Tapcash BNI","admin_fee":1500,"raw":{"admin_fee":1500,"bank_name":"BNI","bank_type":"3","card_no":"7546080000681096",
# "prev_balance":"5045","provider":"Tapcash BNI","value":"2000"},"status":"1","final_balance":"5545","denom":"500",
# "payment_details":{"trx_type":"026","provider":"LinkAja","mid":"000972721511382bf739669cce165808","status":"SUCCESS","amount":2000,"msisdn":"6283806932497","host_trx_date":"20201130134835","trx_id":"topup1606718904559311-17","host_reff_no":"7KU6T6MXYM","tid":"17092001"},
# "payment_received":"2000","topup_details":{"report_ka":"N/A","bank_id":"2","report_sam":"754608000068109600000000A708428E020013B50015A90001F40065D30063DF30BEFF5AD461A18B2BFD82190F424002070100002B000011000007010013B500000088889999D98A649075AE6466D8A28EFF10CB15F44BAFAFBF93DE2BCD0015A9D461A18B2BD461A18B2BFD821900002B00001100007546990000042042754699000004204272FEF0AFF54E358A",
# "bank_name":"BNI","last_balance":"5545","card_no":"7546080000681096"}}
# MANDIRI
#{"date":"30/11/20","epoch":1606718033570981,"payment":"cash","shop_type":"topup","time":"13:33:53","qty":1,"value":"2000","provider":"e-Money Mandiri",
# "admin_fee":1500,"raw":{"admin_fee":1500,"bank_name":"MANDIRI","bank_type":"0","card_no":"6032982702000215","prev_balance":"54317","provider":"e-Money Mandiri",
# "value":"2000"},"status":"1","final_balance":"54817","denom":"500","payment_details":{"history":"10000","total":"10000"},"payment_received":"10000",
# "topup_details":{"report_ka":"603298180000246100030D706E86B7B891011404000120D007000090692F003011201334111F010000A40103DC0500001723AB","bank_id":"1",
# "report_sam":"603298270200021500030D706E86B7B891511404880110F401000021D600003011201334111F0100006700036F4710","bank_name":"MANDIRI","last_balance":54817,
# "card_no":"6032982702000215","c2c_mode":"1"}}
# BRI
# {"denom":"500","epoch":1606717829562377,"date":"30/11/20","receipt_title":"Transaksi Sukses","final_balance":"5826","payment_received":"10000",
# "payment":"cash","value":"2000","qty":1,"raw":{"admin_fee":1500,"bank_name":"BRI","bank_type":"2","card_no":"6013500433185031","prev_balance":"5326",
# "provider":"Brizzi BRI","value":"2000"},"provider":"Brizzi BRI","admin_fee":1500,"status":"1","shop_type":"topup","time":"13:30:29",
# "payment_details":{"history":"10000","total":"10000"},"topup_details":{"report_ka":"N/A","topup_amount":"500","report_sam":"N/A","bank_id":"3",
# "bank_name":"BRI","last_balance":"5826","card_no":"6013500433185031","other_channel_topup":"0"}}


def push_trx_online(payload):
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, MDS Push Online TRX Failed'))
    #     return False
    try:
        payload = json.loads(payload)
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "tid": _Common.TID,
            "device_id": _Common.TID,
            "bank_mid": "N/A",
            "bank_tid": "N/A",
            "gate_name": _Common.KIOSK_NAME,
        }
        if 'transaction_status' in payload.keys():
            # param = {**param, **payload}
            param = param.update(payload)
        else:
            new_param = {
                "invoice_number": str(payload['shop_type']) + str(payload['epoch']),
                "transaction_status": "SUCCESS" if payload['status'] == '1' else 'FAILED',
                "card_number": payload['raw']['card_no'],
                "initial_balance": payload['raw']['prev_balance'],
                "amount_topup": payload['denom'],
                "paid_amount": payload['price'],
                "admin_fee": payload['admin_fee'],
                "last_balance": payload['final_balance'],
                "bank_name": payload['raw']['bank_name'],
                "device_timestamp": str(payload['epoch'])[:13],
                "host_reff_number": str(payload['epoch']),
                "initial_wallet": payload['topup_details']['prev_wallet'],
                "last_wallet": payload['topup_details']['last_wallet'],
                "session_id": _Common.MDS_SESSION,
            }
            # param = {**param, **new_param}
            param = param.update(new_param)
        endpoint = '/unik-tablet-service/v1/push-trx/topup-online'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False
    

def start_push_trx_offline(payload):
    _Helper.get_thread().apply_async(push_trx_offline, (payload,))


def push_trx_offline(payload):
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, MDS Push Offline TRX Failed'))
    #     return False
    try:
        payload = json.loads(payload)
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "tid": _Common.TID,
            "gate_name": _Common.KIOSK_NAME,
            "device_id": _Common.TID,
            "deposit_prev_balance_idle": "0",
            "deposit_last_balance_idle": "0",
            "slot_active": "1",
            "session_id": _Common.MDS_SESSION,

        }
        report_type = 'TOPUP'
        card_force_report = payload['topup_details']['report_sam'] if payload['raw']['bank_name'] == 'BNI' else payload['topup_details']['report_ka'] + payload['topup_details']['report_sam']
        if 'card_force_report' in payload.keys():
            card_force_report = payload['card_force_report']
            report_type = 'FORCE SETTLEMENT'
            # param = {**param, **payload}
            param = param.update(payload)
        else:
            new_param = {
                "trx_id": str(payload['shop_type']) + str(payload['epoch']),
                "admin_fee": payload['admin_fee'],
                "card_force_report": card_force_report,
                "bank_name": payload['raw']['bank_name'],
                "report_type": report_type,
                "last_balance": payload['final_balance'],
                "initial_balance": payload['raw']['prev_balance'],
                "bank_mid": _Common.C2C_MID if payload['raw']['bank_name'] == 'MANDIRI' else _Common.MID_BNI,
                "bank_tid": _Common.C2C_TID if payload['raw']['bank_name'] == 'MANDIRI' else _Common.TID_BNI,
                "card_number": payload['raw']['card_no'],
                "card_report": payload['topup_details']['report_sam'] if payload['raw']['bank_name'] == 'BNI' else payload['topup_details']['report_ka'] + payload['topup_details']['report_sam'],
                "amount": payload['denom'],
                "paid_amount": payload['price'],
                "settlement_id": _Common.MDS_SESSION,
                "device_timestamp": str(payload['epoch'])[:13],
                "deposit_prev_balance": payload['topup_details']['prev_deposit'],
                "deposit_last_balance": payload['topup_details']['last_deposit'],
            }
            param = param.update(new_param)
        endpoint = '/unik-tablet-service/v1/push-trx/topup-offline'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_push_trx_deposit(payload):
    _Helper.get_thread().apply_async(push_trx_deposit, (payload,))


def push_trx_deposit(payload):
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, MDS Push Deposit TRX Failed'))
    #     return False
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "tid": _Common.TID,
            "device_id": _Common.TID,
            "invoice_number": payload['invoice_number'],
            "host_reff_number": payload['host_reff_number'],
            "amount_topup": payload['amount'],
            "deposit_last_balance": payload['last_deposit'],
            "deposit_initial_balance": payload['prev_deposit'],
            "balance_wallet_before": payload['prev_wallet'],
            "balance_wallet_after": payload['last_wallet'],
            "card_number": payload['card_no'],
            "timestamp": _Helper.epoch('MDS'),
            "transaction_status": payload['transaction_status'],
            # "settlement_id": "N/A",
            # "settlement_filename": "N/A",
            # "settlement_uploaded_timestamp": "N/A",
            "session_id": _Common.MDS_SESSION,
            "gate_name": _Common.KIOSK_NAME,
            "bank_mid": payload['bank_mid'],
            "bank_tid": payload['bank_tid'],
            "slot_active": "1"
        }
        endpoint = '/unik-tablet-service/v1/push-trx/topup-deposit'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_push_settlement_data(payload):
    _Helper.get_thread().apply_async(push_settlement_data, (payload,))


def push_settlement_data(payload):
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, MDS Push Settlement Failed'))
    #     return False
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "tid": _Common.TID,
            "device_id": _Common.TID,
            "id": payload['id'],
            "file_name": payload['file_name'],
            "header": payload['header'],
            "body": payload['body'],
            "footer": payload['footer'],
            "created_date": payload['created_date'],
            "created_time": payload['created_time'],
            "uploaded_date": payload['uploaded_date'],
            "uploaded_time": payload['uploaded_time'],
            "count_transaction": payload['count_transaction'],
            "total_transaction": payload['total_transaction'],
            "device_timestamp": _Helper.epoch('MDS'),
            "bank_tid": payload['bank_tid'],
            "bank_mid": payload['bank_mid'],
            "session_id": _Common.MDS_SESSION,
            "gate_name": _Common.KIOSK_NAME,
            "slot_active": "1"
        }
        endpoint = '/unik-tablet-service/v1/push-trx/c2c-settlement'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_push_trx_qr(payload):
    _Helper.get_thread().apply_async(push_trx_qr, (payload,))


def push_trx_qr(payload):
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, MDS Push QR TRX Failed'))
    #     return False
    try:
        payload = json.loads(payload)
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "tid": _Common.TID,
            "transaction_id": str(payload['shop_type']) + str(payload['epoch']),
            "amount": str(payload['payment_received']),
            "host_timestamp": str(payload['epoch'])[:13],
            "device_timestamp": str(payload['epoch'])[:13],
            "reff_number": payload['reff_no'],
            "session_id": _Common.MDS_SESSION,
            "qr_provider": payload['payment'].upper()
        }
        endpoint = '/unik-tablet-service/v1/push-trx/qr'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_sync_session():
    _Helper.get_thread().apply_async(sync_session,)


LAST_LOGOUT_TIME = ''


def sync_session():
    global LAST_LOGOUT_TIME
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, MDS Push QR TRX Failed'))
    #     return False
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "nip": _Common.MDS_SESSION,
            "staff_name": _Common.LOGGED_OPERATOR['first_name'],
            "shift": _Helper.time_string('%Y%m%d%H'),
            "login_time": _Common.LOGGED_OPERATOR['login_time'],
            "logout_time": LAST_LOGOUT_TIME,
            "initial_wallet_balance": _Common.LOGGED_OPERATOR['init_wallet'],
            "last_wallet_balance": _Common.MDS_WALLET,
            "device_id": _Common.TID,
            "device_timestamp": _Helper.epoch('MDS'),
            "gate_name": _Common.KIOSK_NAME,
        }
        
        endpoint = '/unik-tablet-service/v1/push-trx/session-transaction'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            return True
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_mds_online_topup(payload):
    _Helper.get_thread().apply_async(mds_online_topup, (payload,))


MDS_TOPUP_CHANNEL = {
    'MANDIRI': 'emoney-mandiri',
    'MANDIRI_C2C_DEPOSIT': 'emoney-mandiri',
    'BNI': 'tapcash-bni',
    'BRI': 'brizzi-bri',
    'BCA': 'flazz-bca'
}

def mds_online_topup(bank=None, data=[]):
    if bank is None or bank not in MDS_TOPUP_CHANNEL.keys():
        LOGGER.warning(('MDS Topup Error, Unknown Bank Detected'))
        return False
    if _Helper.empty(_Common.MDS_TOKEN):
        LOGGER.warning(('Empty Token, MDS ' +bank+ ' Online Topup Failed'))
        return False
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "card_number": data['card_no'],
            "device_id": _Common.TID,
            "device_timestamp": data['time'],
            "invoice_num": data['invoice_no'],
            "paid_amount": data['amount']
        }
        channel = MDS_TOPUP_CHANNEL[bank]
        endpoint = '/unik-tablet-service/v1/'+channel+'/topup'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200 and 'TOPUP APPROVED.' in response['response']['message']:
            _Common.MDS_WALLET = int(response['data']['last_wallet'])
            return response['data']
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def do_deduct_wallet(data):
    if _Helper.empty(data):
        LOGGER.warning(('Empty Deduct Data, Wallet Deduct Failed'))
        return False
    # if _Helper.empty(_Common.MDS_TOKEN):
    #     LOGGER.warning(('Empty Token, Wallet Deduct Failed'))
    #     return False
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            'amount': data['amount'],
            'trx_ref': data['trx_ref'],
            'trx_desc': data['trx_desc']
        }
        endpoint = '/wallet-service/v1/deduct-wallet'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header, log=_Common.TEST_MODE)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200 and 'Deduct success' in response['response']['message']:
            _Common.MDS_WALLET = int(response['data']['wallet_balance'])
        else:
            param['endpoint'] = endpoint
            _Common.store_request_to_job(name=_Helper.whoami(), url=MDS_HOST+endpoint, payload=param, header=header)
        return True
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_generate_summary_trx():
    _Helper.get_thread().apply_async(generate_summary_trx,)


def generate_summary_trx():
    global LAST_LOGOUT_TIME
    
    if _Helper.empty(_Common.MDS_TOKEN):
        LOGGER.warning(('Empty Token, MDS Push Summary TRX Failed'))
        return False
    LAST_LOGOUT_TIME = _Helper.time_string('%d/%m/%Y %H:%M')
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "device_id": _Common.TID,
            "session_id": _Common.MDS_SESSION,
            "summary_id": _Helper.epoch(),
            "open_time": _Common.LOGGED_OPERATOR['login_time'],
            "close_time": LAST_LOGOUT_TIME,
            "reff_number": _Helper.get_uuid(),
            "staff_id": _Common.LOGGED_OPERATOR['username'],
            "shift_id": _Helper.time_string('%Y%m%d%H'),
            "mdr_deposit_init_balance": _Common.LOGGED_OPERATOR['mdr_init_deposit'],
            "mdr_deposit_last_balance": _Common.MANDIRI_ACTIVE_WALLET,
            "bni_deposit_init_balance": _Common.LOGGED_OPERATOR['bni_init_deposit'],
            "bni_deposit_last_balance": _Common.BNI_ACTIVE_WALLET,
            "device_timestamp": _Helper.epoch('MDS'),
            "gate_name": _Common.KIOSK_NAME,
        }
        
        endpoint = '/unik-tablet-service/v1/push-trx/summary-transaction'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            response['data']['operator_name'] = _Common.LOGGED_OPERATOR['first_name']
            response['data']['init_wallet_balance'] = _Common.LOGGED_OPERATOR['init_wallet']
            response['data']['last_wallet_balance'] = _Common.MDS_WALLET
            return response['data']
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False


def dummy_summary_trx():
    global LAST_LOGOUT_TIME
    
    LAST_LOGOUT_TIME = _Helper.time_string('%d/%m/%Y %H:%M')
    try:
        header = {
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer: '+_Common.MDS_TOKEN
        }
        param = {
            "device_id": "18000101",
            "session_id": "yudi123",
            "mid": "47781c18b952b0fa34b135349d324908"
        }
        endpoint = '/unik-tablet-service/v1/get-trx/summary-transaction-2'
        status, response = _NetworkAccess.post_to_url(url=MDS_HOST+endpoint, param=param, header=header)
        LOGGER.debug((status, response))
        if status == 200 and response['response']['code'] == 200:
            response['data']['operator_name'] = _Common.LOGGED_OPERATOR['first_name']
            response['data']['init_wallet_balance'] = _Common.LOGGED_OPERATOR['init_wallet']
            response['data']['last_wallet_balance'] = _Common.MDS_WALLET
            return response['data']
        else:
            return False
    except Exception as e:
        LOGGER.warning((e))
        return False
