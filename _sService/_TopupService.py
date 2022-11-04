__author__ = "wahyudi@multidaya.id"

import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _nNetwork import _HTTPAccess
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

TOPUP_URL = _Common.UPDATE_BALANCE_URL_DEV

if _Common.LIVE_MODE is True or _Common.PTR_MODE is True:
    TOPUP_URL = _Common.UPDATE_BALANCE_URL
    
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
QPROX_COMMAND = _QPROX.QPROX
ERROR_TOPUP = _QPROX.ERROR_TOPUP

# _Common.remove_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED')

MDR_DEPOSIT_UPDATE_BALANCE_PROCESS = False
BNI_DEPOSIT_UPDATE_BALANCE_PROCESS = False

LAST_BNI_TOPUP_PARAM = None

BANKS = _Common.BANKS

# ==========================================================

def job_retry_reload_mandiri_deposit(first_run=False):
    # global MDR_DEPOSIT_UPDATE_POSTPONED
    if _Common.exist_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED'):
        LOGGER.warning(('FOUND MDR_DEPOSIT_UPDATE_POSTPONED', str(_Common.load_from_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED', 'json'))))
        return
    mdr_deposit_update_postponed = _Common.load_from_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED', 'json')
    if first_run:
        sleep(5*60) #Sleep 5 Minutes If First Run
    for mdr in [ mdr_deposit_update_postponed ]:
        # 'reff_no'   : param['invoice_no'],
        # 'expirity'  : _Helper.epoch() + (60*60)
        # update_balance_result = False
        while True:
            if MDR_DEPOSIT_UPDATE_BALANCE_PROCESS is True:
                LOGGER.debug(('ANOTHER MDR_DEPOSIT_UPDATE_BALANCE_PROCESS', 'STILL RUNNING'))
                continue
            if mdr['expirity'] <= _Helper.epoch():
                LOGGER.debug(('DO RESET MDR_DEPOSIT_UPDATE_POSTPONED', 'DATA EXPIRED', str(mdr)))
                _Common.remove_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED')
                break
            LOGGER.debug(('PROCESSING', str(mdr)))
            if not _Common.mandiri_sam_status():
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|DEPOSIT_MDR_NOT_ACTIVE')
                continue
            param = QPROX_COMMAND['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
            # trigger = 'SYSTEM_RETRY_'+mdr['reff_no'].upper()
            update_balance_result = update_balance(param, 'MANDIRI', 'TOPUP_DEPOSIT')
            if update_balance_result is not False:
                LOGGER.debug(('DO RESET MDR_DEPOSIT_UPDATE_POSTPONED', 'SUCCESS RETRY', str(mdr)))
                _Common.remove_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED')
                if update_balance_result['last_balance'] == update_balance_result['topup_amount']:
                    update_balance_result['last_balance'] = str(int(update_balance_result['topup_amount']) + int(mdr['prev_balance']))
                output = {
                            # 'prev_wallet': pending_result['prev_wallet'],
                            # 'last_wallet': pending_result['last_wallet'],
                            'prev_balance': mdr['prev_balance'],
                            'last_balance': update_balance_result['last_balance'],
                            'report_sam': 'N/A',
                            'card_no': update_balance_result['card_no'],
                            'report_ka': 'N/A',
                            'bank_id': '1',
                            'bank_name': 'MANDIRI',
                    }
                # Do Update Deposit Balance Value in Memory
                _Common.MANDIRI_ACTIVE_WALLET = int(update_balance_result['last_balance'])
                _Common.MANDIRI_WALLET_1 = int(update_balance_result['last_balance'])
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
                _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_amount'], int(mdr['amount']))
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
                break
            sleep(5*60)


def start_define_topup_slot_bni():
    _Helper.get_thread().apply_async(define_topup_slot_bni)


def define_topup_slot_bni():
    if not BNI_DEPOSIT_UPDATE_BALANCE_PROCESS:
        if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
            LOGGER.debug(('START_BNI_SAM_AUTO_UPDATE_SLOT_1', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_1_WALLET)))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_1')
            do_topup_deposit_bni(slot=1, force=True)
        if _Common.BNI_SINGLE_SAM is False and _Common.BNI_SAM_2_WALLET <= _Common.BNI_THRESHOLD:
            LOGGER.debug(('START_BNI_SAM_AUTO_UPDATE_SLOT_2', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_2_WALLET)))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_2')
            do_topup_deposit_bni(slot=2, force=True)
    else:
        LOGGER.warning(('Another BNI_DEPOSIT_UPDATE_BALANCE_PROCESS Is Running', str(_Common.BNI_THRESHOLD), str(_Common.BNI_SAM_1_WALLET)))


def start_do_topup_deposit_bni(slot):
    _Helper.get_thread().apply_async(do_topup_deposit_bni, (int(slot),))


def start_do_force_topup_bni():
    slot = _Common.BNI_ACTIVE
    force = True
    _Helper.get_thread().apply_async(do_topup_deposit_bni, (int(slot), force, ))


# _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')


def do_topup_deposit_bni(slot=1, force=False, activation=False):
    global BNI_DEPOSIT_UPDATE_BALANCE_PROCESS
    try:
        LOGGER.info(('TRIGGER BNI DEPOSIT RELOAD', _Common.BNI_SAM_1_WALLET, 'BNI THRESHOLD', _Common.BNI_THRESHOLD))
        slot = _Common.BNI_ACTIVE
        if _Common.BNI_SINGLE_SAM is True:
            slot = 1
        # Check Lastest Deposit Balance Removed
        if _Common.BNI_ACTIVE_WALLET > _Common.BNI_THRESHOLD:
            LOGGER.warning(('DEPOSIT_STILL_SUFFICIENT', slot, _Common.BNI_ACTIVE_WALLET, _Common.BNI_THRESHOLD))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_DEPOSIT_STILL_SUFFICIENT')
            return 'DEPOSIT_STILL_SUFFICIENT'
        if _Common.exist_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES'):
            LOGGER.warning(('ANOTHER BNI_DEPOSIT_RELOAD_IN_PROGRES', str(_Common.load_from_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES'))))
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_ANOTHER_BNI_DEPOSIT_RELOAD_IN_PROGRES')
            return 'BNI_DEPOSIT_RELOAD_IN_PROGRES'
        # if force is False and _Common.ALLOW_DO_TOPUP is False:
        #     LOGGER.warning(('TOPUP_NOT_ALLOWED', slot, _Common.ALLOW_DO_TOPUP))
        #     TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_TOPUP_NOT_ALLOWED')
        #     return 'TOPUP_NOT_ALLOWED'
        invoice_no = 'refill'+str(_Helper.epoch())
        _Common.store_to_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES', invoice_no)
        LOGGER.debug(('BNI_DEPOSIT_RELOAD_IN_PROGRES', str(invoice_no)))
        # Add Delay Read Deposit
        sleep(2)
        _get_card_data = _QPROX.get_card_info(slot=slot)
        if _get_card_data is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_GET_CARD_INFO_BNI')
            _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')
            # _Common.upload_topup_error('FAILED_GET_CARD_INFO_BNI', slot, 'ADD')
            _Common.online_logger(['BNI Card Data', _get_card_data], 'general')
            return 'FAILED_GET_CARD_INFO_BNI'
        # prev_balance = _Common.BNI_ACTIVE_WALLET
        if not _Common.BNI_C2C_TRESHOLD_USAGE:
            _Common.BNI_ACTIVE_WALLET = 0
        _result_pending = pending_balance({
            'card_no': _get_card_data['card_no'],
            'amount': _Common.BNI_TOPUP_AMOUNT,
            'invoice_no': invoice_no,
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
            _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')
            # _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Result Pending', _result_pending], 'general')
            return 'FAILED_PENDING_BALANCE_BNI'
        BNI_DEPOSIT_UPDATE_BALANCE_PROCESS = True
        LOGGER.info(('BNI_DEPOSIT_UPDATE_BALANCE_PROCESS', BNI_DEPOSIT_UPDATE_BALANCE_PROCESS))
        # Waiting Another Deposit Update Balance Process
        # wait = 0
        # while True:
        #     wait += 1
        #     if len(_Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS) == 0:
        #         break
        #     if wait >= 3600:
        #         break
        #     sleep(1)
        # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS.append(_Helper.whoami())
        _result_ubal = update_balance({
            'card_no': _get_card_data['card_no'],
            'card_info': _get_card_data['card_info'],
            'reff_no': _result_pending['reff_no'],
            'slot': slot
        })
        if _result_ubal is False:
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_UPDATE_BALANCE_BNI')
            # _Common.upload_topup_error(slot, 'ADD')
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            _Common.online_logger(['BNI Result Ubal', _result_ubal], 'general')
            _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')
            return 'FAILED_UPDATE_BALANCE_BNI'
        _send_crypto = False
        attempt = 0
        while not _send_crypto:
            attempt += 1
            LOGGER.info(('DO_SEND_CRYPTO_BNI_DEPOSIT', attempt))
            _send_crypto = _QPROX.bni_crypto_deposit(_result_ubal['card_info'], _result_ubal['dataToCard'], slot=slot)
            if _send_crypto is not False:
                LOGGER.info(('RESULT_SEND_CRYPTO_BNI_DEPOSIT', str(_send_crypto)))
                break
            if attempt == 3:
                break
            sleep(10)
        BNI_DEPOSIT_UPDATE_BALANCE_PROCESS = False
        LOGGER.info(('BNI_DEPOSIT_UPDATE_BALANCE_PROCESS', BNI_DEPOSIT_UPDATE_BALANCE_PROCESS))
        if _send_crypto is False:
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_SEND_CRYPTOGRAM_BNI')
            # _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Send Crypto', _send_crypto], 'general')
            _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')
            return 'FAILED_SEND_CRYPTOGRAM_BNI'
        else:
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('SUCCESS_TOPUP_BNI')
            # _Common.upload_topup_error(slot, 'RESET')
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
            _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')
            return 'SUCCESS_TOPUP_BNI'
    except Exception as e:
        # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
        LOGGER.warning((str(slot), str(e)))
        TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('FAILED_TOPUP_BNI')
        return 'FAILED_TOPUP_BNI'


def bni_reset_update_balance_master():
    slot = 1
    _Helper.get_thread().apply_async(bni_reset_update_balance, (slot,))


def bni_reset_update_balance_slave():
    slot = 2
    _Helper.get_thread().apply_async(bni_reset_update_balance, (slot,))


def bni_reset_update_balance(slot=1, activation=True):
    global BNI_DEPOSIT_UPDATE_BALANCE_PROCESS
    try:
        slot = _Common.BNI_ACTIVE
        if _Common.BNI_SINGLE_SAM is True:
            slot = 1
        sleep(2)
        _get_card_data = _QPROX.get_card_info(slot=slot)
        if _get_card_data is False:
            return False, 'GET_CARD_DATA_FAILED'
        _result_pending = pending_balance({
            'card_no': _get_card_data['card_no'],
            'amount': '1',
            'card_tid': _Common.TID_BNI,
            'invoice_no': 'activation'+str(_Helper.epoch()),
            'activation': '1'
        })
        if _result_pending is False:
            # _Common.upload_topup_error(slot, 'ADD')
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
        # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS.append(_Helper.whoami())
        BNI_DEPOSIT_UPDATE_BALANCE_PROCESS = True
        LOGGER.info(('BNI_DEPOSIT_UPDATE_BALANCE_PROCESS', BNI_DEPOSIT_UPDATE_BALANCE_PROCESS))
        _result_ubal = update_balance({
                'card_no': _get_card_data['card_no'],
                'card_info': _get_card_data['card_info'],
                'reff_no': _result_pending['reff_no'],
                'slot': slot
            })
        if not activation:
            return _result_ubal
        if _result_ubal is False:
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            # _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Result Ubal', _result_ubal], 'general')
            return False, 'UPDATE_BALANCE_FAILED'
        _send_crypto = False
        attempt = 0
        while not _send_crypto:
            attempt += 1
            LOGGER.info(('DO_SEND_CRYPTO_BNI_DEPOSIT', attempt))
            _send_crypto = _QPROX.bni_crypto_deposit(_get_card_data['card_info'], _result_ubal['dataToCard'], slot=slot)
            if _send_crypto is not False:
                LOGGER.info(('RESULT_SEND_CRYPTO_BNI_DEPOSIT', str(_send_crypto)))
                break
            if attempt == 3:
                break
            sleep(10)
        if _send_crypto is False:
            BNI_DEPOSIT_UPDATE_BALANCE_PROCESS = False
            LOGGER.info(('BNI_DEPOSIT_UPDATE_BALANCE_PROCESS', BNI_DEPOSIT_UPDATE_BALANCE_PROCESS))
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            # _Common.upload_topup_error(slot, 'ADD')
            _Common.online_logger(['BNI Send Crypto', _send_crypto], 'general')
            return False, 'INJECT_CRYPTO_FAILED'
        else:
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            # _Common.upload_topup_error(slot, 'RESET')
            output = {
                'bank': 'BNI',
                'card_no': _get_card_data['card_no'],
                'topup_amount': str(_result_ubal['amount']),
                'last_balance': str(_send_crypto.get('last_balance', 0)),
                'reff_no': _result_ubal['reff_no']
            }
            confirm_bni_topup(output)
            _Common.ALLOW_DO_TOPUP = True
            #Need To Release This To Enable Topup Transaction After Reset Command
            BNI_DEPOSIT_UPDATE_BALANCE_PROCESS = False
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
            _param['priv'] = 'NO_LIMIT'
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bni/pending', param=_param)
            LOGGER.debug((str(_param), str(status), str(response)))
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
                reff_no = _param.get('invoice_no')
                _Common.store_to_temp_data(reff_no+'-last-pending-result', json.dumps(response['data']))
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
            _param['priv'] = 'NO_LIMIT'
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bri/pending', param=_param)
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
                reff_no = _param.get('invoice_no')
                _Common.store_to_temp_data(reff_no+'-last-pending-result', json.dumps(response['data']))
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
            _param['priv'] = 'NO_LIMIT'
            _url = TOPUP_URL
            if _Common.DEV_MODE_TOPUP_BCA:
                _url = _Common.UPDATE_BALANCE_URL_DEV
            status, response = _HTTPAccess.post_to_url(url=_url + 'topup-bca/pending', param=_param)
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
                reff_no = _param.get('invoice_no')
                _Common.store_to_temp_data(reff_no+'-last-pending-result', json.dumps(response['data']))
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
            _param['invoice_no'] = 'refill'+str(_Helper.epoch())
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            _param['phone'] = '08129420492'
            _param['email'] = _Common.THEME_NAME.lower() + '@mdd.co.id'
            # This Below Key Is Mandatory For Topup Deposit C2C TO Reroute Mandiri Cred
            _param['purpose'] = 'TOPUP_DEPOSIT_C2C'
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-mandiri/pending', param=_param)
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
    elif bank == 'DKI' and mode == 'TOPUP':
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
            _param['priv'] = 'NO_LIMIT'
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-dki/pending', param=_param)
            LOGGER.debug((str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                reff_no = _param.get('invoice_no')
                _Common.store_to_temp_data(reff_no+'-last-pending-result', json.dumps(response['data']))
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


def start_deposit_update_balance(bank):
    for __bank in BANKS:
        if __bank == bank:
            if not __bank['STATUS']:
                LOGGER.warning(('DEPOSIT BANK ', bank, ' NOT ACTIVE FOR UPDATE BALANCE'))
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|DEPOSIT_BANK_NOT_ACTIVE')
                return 'DEPOSIT_BANK_NOT_ACTIVE'
    if bank == 'MANDIRI':
        if not _Common.mandiri_sam_status():
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|DEPOSIT_MDR_NOT_ACTIVE')
            return 'DEPOSIT_MDR_NOT_ACTIVE'
        if MDR_DEPOSIT_UPDATE_BALANCE_PROCESS:
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|ANOTHER_PROCESS_STILL_RUNNING')
            return 'ANOTHER_PROCESS_STILL_RUNNING'
        mode = 'TOPUP_DEPOSIT'
        param = QPROX_COMMAND['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
        trigger = 'ADMIN'
        _Helper.get_thread().apply_async(update_balance, (param, bank, mode, trigger))
        return 'TASK_EXECUTED_IN_MACHINE'
    elif bank == 'BNI':
        if not ('---' not in _Common.MID_BNI and len(_Common.MID_BNI) > 3):
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|DEPOSIT_BNI_NOT_ACTIVE')
            return 'DEPOSIT_BNI_NOT_ACTIVE'
        # Disabled Validation Active Thread
        # if BNI_DEPOSIT_UPDATE_BALANCE_PROCESS:
        #     TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|ANOTHER_PROCESS_STILL_RUNNING')
        #     return 'ANOTHER_PROCESS_STILL_RUNNING'
        slot = 1
        _Helper.get_thread().apply_async(auto_refill_zero_bni, (slot,))
        return 'TASK_EXECUTED_IN_MACHINE'


LAST_BRI_ACCESS_TOKEN = ''
LAST_BRI_REFF_NO_HOST = ''


def update_balance(_param, bank='BNI', mode='TOPUP', trigger=None):
    global LAST_BNI_TOPUP_PARAM, LAST_BCA_REFF_ID, LAST_BRI_ACCESS_TOKEN, LAST_BRI_REFF_NO_HOST, MDR_DEPOSIT_UPDATE_BALANCE_PROCESS, BNI_DEPOSIT_UPDATE_BALANCE_PROCESS, MDR_DEPOSIT_UPDATE_POSTPONED
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
            _param['prev_balance'] = '0'
            LAST_BNI_TOPUP_PARAM = _param
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bni/update', param=_param)
            LOGGER.debug((str(_param), str(status), str(response)))
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
                            'invoice_no': 'activation'+str(_Helper.epoch()),
                            'activation': '1'
                        })
                        if _activation_pending is False:
                            # _Common.upload_topup_error(_param['slot'], 'ADD')
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
                service_response = json.loads(result)
                error_result = service_response['Response'].split('|')
                if len(error_result) > 2:
                    LAST_BRI_ACCESS_TOKEN = error_result[1]
                    LOGGER.debug(('LAST_BRI_ACCESS_TOKEN', LAST_BRI_ACCESS_TOKEN))
                    LAST_BRI_REFF_NO_HOST = error_result[2]
                    LOGGER.debug(('LAST_BRI_REFF_NO_HOST', LAST_BRI_REFF_NO_HOST))
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
            last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
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
                    # _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_TOPUP_CORRECTION#RC_'+rc)
                    # Store Local Card Number Here For Futher Reversal Process
                    previous_card_no = last_card_check['card_no']
                    previous_card_data = last_card_check
                    # previous_card_data['refference_id'] = LAST_BCA_REFF_ID
                    _Common.store_to_temp_data(previous_card_no, json.dumps(previous_card_data))
                    reset_bca_session()
                    # Must Return Here To Stop Emit into Front
                    return 'BCA_TOPUP_CORRECTION'
                _Common.online_logger([response, bank, _param], 'general')
                return False
        except Exception as e:
            LOGGER.warning(str(e))
            return False
    elif bank == 'MANDIRI' and mode == 'TOPUP_DEPOSIT':
        MDR_DEPOSIT_UPDATE_BALANCE_PROCESS = True
        LOGGER.debug(('MDR_DEPOSIT_UPDATE_BALANCE_PROCESS', MDR_DEPOSIT_UPDATE_BALANCE_PROCESS))
        message_error = 'UPDATE_ERROR'
        attempt = 0
        try:
            response, result = _Command.send_request(param=_param, output=None)
            LOGGER.debug((bank, mode, attempt, response, result))
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
                response = output
            else:
                if 'No Pending Balance' in result:
                    message_error = 'NO_PENDING_BALANCE'
                response = False
        except Exception as e:
            # _Common.DEPOSIT_UPDATE_BALANCE_IN_PROCESS = []
            LOGGER.warning(str(e))
            response = False
        finally:
            MDR_DEPOSIT_UPDATE_BALANCE_PROCESS = False
            LOGGER.debug(('MDR_DEPOSIT_UPDATE_BALANCE_PROCESS', MDR_DEPOSIT_UPDATE_BALANCE_PROCESS))
            if not _Helper.empty(response):
                # if not _Helper.empty(LAST_MANDIRI_C2C_SUCCESS_RESULT):
                #     prev_balance = LAST_MANDIRI_C2C_SUCCESS_RESULT['prev_deposit_balance']
                #     amount = LAST_MANDIRI_C2C_SUCCESS_RESULT['amount']
                #     if response['last_balance'] == response['topup_amount']:
                #         response['last_balance'] = str(int(response['topup_amount']) + int(prev_balance))
                #     output = {
                #                 'prev_wallet': LAST_MANDIRI_C2C_SUCCESS_RESULT['prev_wallet'],
                #                 'last_wallet': LAST_MANDIRI_C2C_SUCCESS_RESULT['last_wallet'],
                #                 'prev_balance': prev_balance,
                #                 'last_balance': response['last_balance'],
                #                 'report_sam': 'N/A',
                #                 'card_no': LAST_MANDIRI_C2C_SUCCESS_RESULT['card_no'],
                #                 'report_ka': 'N/A',
                #                 'bank_id': '1',
                #                 'bank_name': 'MANDIRI',
                #         }
                #     # Do Update Deposit Balance Value in Memory
                #     _Common.MANDIRI_ACTIVE_WALLET = int(response['last_balance'])
                #     _Common.MANDIRI_WALLET_1 = int(response['last_balance'])
                #     # Do Upload SAM Refill Status Into BE Asyncronous
                #     sam_audit_data = {
                #             'trxid': 'REFILL_SAM',
                #             'samCardNo': _Common.C2C_DEPOSIT_NO,
                #             'samCardSlot': _Common.C2C_SAM_SLOT,
                #             'samPrevBalance': output['prev_balance'],
                #             'samLastBalance': output['last_balance'],
                #             'topupCardNo': '',
                #             'topupPrevBalance': output['prev_balance'],
                #             'topupLastBalance': output['last_balance'],
                #             'status': 'REFILL_SUCCESS',
                #             'remarks': output,
                #         }
                #     _DAO.create_today_report(_Common.TID)
                #     _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_count'], 1)
                #     _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_amount'], int(amount))
                #     _DAO.update_today_summary_multikeys(['mandiri_deposit_last_balance'], int(output['last_balance']))
                #     _Common.store_upload_sam_audit(sam_audit_data)   
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
                # send_kiosk_status()
                if _Common.exist_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED'):
                    LOGGER.debug(('DO RESET MDR_DEPOSIT_UPDATE_POSTPONED'))
                    _Common.remove_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED')
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|SUCCESS')
            else:
                if trigger is not None:
                    TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|'+message_error)                
            return response
    elif bank == 'DKI' and mode == 'TOPUP':
        try:
            _param['token'] = TOPUP_TOKEN
            _param['mid'] = TOPUP_MID
            _param['tid'] = TOPUP_TID
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-dki/update', param=_param)
            LOGGER.debug((str(_param), str(status), str(response)))
            if status == 200 and response['response']['code'] == 200:
                return {
                    'bank': bank,
                    'card_no': _param['card_no'],
                    'topup_amount': _param['amount'],
                    'last_balance': str(int(_param['prev_balance']) + int(_param['amount'])),
                    'data_to_card': response['data']['data_to_card']
                }
            else:
                _Common.online_logger([response, bank, _param], 'general')
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
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bni/reversal', param=_param)
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
    elif bank == 'DKI' and mode == 'TOPUP':
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
            status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-dki/reversal', param=_param)
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
                _Common.remove_temp_data(_param['reff_no'])
                return response['data']
            else:
                _Common.LAST_DKI_ERR_CODE = '52'
                if not _Common.exist_temp_data(_param['reff_no']):
                    _param['endpoint'] = 'topup-dki/reversal'
                    _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-dki/reversal', payload=_param)
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
            # _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|AUTO_ACTIVATION_SUCCESS')
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|SUCCESS')
        else:
            # _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|'+result_message)  
            TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|'+result_message)
    else:
        _Common.ALLOW_DO_TOPUP = True
        # _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.emit('REFILL_ZERO|ERROR_AUTO_ACTIVATION')
        TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|UPDATE_ERROR')


def start_slave_activation_bni():
    slot = 2
    _Helper.get_thread().apply_async(refill_zero_bni, (slot,))


def refill_zero_bni(slot=1):
    _slot = slot - 1
    param = QPROX_COMMAND['REFILL_ZERO'] + '|' + str(_slot) + '|' + _QPROX.TID_BNI
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
    # param = _QPROX.QPROX_COMMAND['RAW_APDU']+'|'+str(4)+'|'+'0084000008'
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
        if payload is None:
            payload = {
                'card_no': '6013500100006619',
                'auto_number': '1'
            }
        else:
            payload = json.loads(payload)
        param = _Common.serialize_payload(payload)
        status, response = _HTTPAccess.post_to_url(_Common.CORE_HOST + 'topup-bri/card-check', param)
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
        if _Helper.empty(_Common.TOPUP_AMOUNT_SETTING):
            _Common.TOPUP_AMOUNT_SETTING = _Common.load_from_temp_data('topup-amount-setting', 'json')
        ready = {
            # 'balance_mds': str(_Common.MDS_WALLET),
            'balance_mandiri': str(_Common.MANDIRI_ACTIVE_WALLET),
            'balance_bni': str(_Common.BNI_ACTIVE_WALLET),
            'bni_wallet_1': str(_Common.BNI_SAM_1_WALLET),
            'bni_wallet_2': str(_Common.BNI_SAM_2_WALLET),
            'mandiri': 'AVAILABLE' if (_QPROX.INIT_MANDIRI is True and _Common.MANDIRI_ACTIVE_WALLET > 0 and not MDR_DEPOSIT_UPDATE_BALANCE_PROCESS) is True else 'N/A',
            'bni': 'AVAILABLE' if (_QPROX.INIT_BNI is True and _Common.BNI_ACTIVE_WALLET > 0 and not BNI_DEPOSIT_UPDATE_BALANCE_PROCESS) is True else 'N/A',
            'bri': 'N/A',
            'bca': 'N/A',
            'dki': 'N/A',
            'emoney': _Common.TOPUP_AMOUNT_SETTING['emoney'],
            'tapcash': _Common.TOPUP_AMOUNT_SETTING['tapcash'],
            'brizzi': _Common.TOPUP_AMOUNT_SETTING['brizzi'],
            'flazz': _Common.TOPUP_AMOUNT_SETTING['flazz'],
            'jakcard': _Common.TOPUP_AMOUNT_SETTING['jakcard'],
            'admin_include': _ConfigParser.get_set_value('TEMPORARY', 'admin^include', '1'),
            'printer_setting': '1' if _ConfigParser.get_set_value('PRINTER', 'printer^type', 'Default') == 'Default' else '0',
        }
        ADMIN_FEE_INCLUDE = True if ready['admin_include'] == '1' else False
        last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
        connection_online = _Common.is_online('get_topup_readiness')
        # Assuming always check card balance first before check topup readiness validation
        if not _Helper.empty(last_card_check):
            if last_card_check['bank_name'] == 'BRI':
                ready['bri'] = 'AVAILABLE' if (_Common.BRI_SAM_ACTIVE is True and connection_online is True) else 'N/A'
            if last_card_check['bank_name'] == 'BCA':
                ready['bca'] = 'AVAILABLE' if (_Common.BCA_TOPUP_ONLINE is True and connection_online is True) else 'N/A'
            if last_card_check['bank_name'] == 'DKI':
                ready['dki'] = 'AVAILABLE' if (_Common.DKI_TOPUP_ONLINE is True and connection_online is True) else 'N/A'
        # if _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
        #     ready['balance_mandiri'] = '999001'
        #     ready['balance_bni'] = '999002'
        #     ready['mandiri'] = 'AVAILABLE'
        #     ready['bni'] = 'AVAILABLE'
        #     ready['bri'] = 'AVAILABLE'
        #     ready['bca'] = 'AVAILABLE'
        #     ready['dki'] = 'AVAILABLE'
        # LOGGER.info((str(ready)))
        TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit(json.dumps(ready))
    except Exception as e:
        LOGGER.warning((str(e)))
        TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit('ERROR')


def start_update_balance_online(bank):
    _Helper.get_thread().apply_async(update_balance_online, (bank,))


def check_update_balance_bni(card_info='', last_balance='0'):
    if card_info is None:
        return False
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID,
            'reff_no': _Helper.time_string(f='%Y%m%d%H%M%S'),
            'card_info': card_info,
            'card_no': card_info[4:20],
            'prev_balance': last_balance
        }
        status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bni/update', param=param)
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
BCA_TOPUP_ONLINE_ERROR = ['8041', '1407', '2B45', 'A8AE', '8386', 'EE31']


def update_balance_online(bank):
    if bank is None or bank not in _Common.ALLOWED_BANK_UBAL_ONLINE:
        TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|UNKNOWN_BANK')
        return
    # last_card_check = _QPROX.LAST_CARD_CHECK
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')

    if bank == 'MANDIRI':
        try:            
            param = QPROX_COMMAND['UPDATE_BALANCE_ONLINE_MANDIRI'] + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|' 
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
            last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
            if last_card_check['able_topup'] in ERROR_TOPUP.keys():
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|INVALID_CARD')
                return
            # Do Action List :
            # - Get Purse Data Tapcash
            card_info = _QPROX.get_card_info_tapcash()
            if card_info is False:
                TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|ERROR')
                return
            # - Request Update Balance BNI
            crypto_data = check_update_balance_bni(card_info, last_card_check['balance'])
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
                # _Helper.dump(send_crypto_tapcash)
                if send_crypto_tapcash is True:
                # - Send Output as Mandiri Specification    
                    last_balance = int(last_card_check['balance']) + int(crypto_data['amount'])
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
            param = QPROX_COMMAND['UPDATE_BALANCE_ONLINE_BRI'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + _Common.SLOT_BRI + '|' 
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
            param = QPROX_COMMAND['UPDATE_BALANCE_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
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
                last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
                previous_card_no = last_card_check['card_no']
                if GENERAL_NO_PENDING in result:
                    _Common.remove_temp_data(previous_card_no)
                    TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|NO_PENDING_BALANCE')
                else:
                    if BCA_KEY_REVERSAL in result:
                        # Store Local Card Number Here For Futher Reversal Process
                        previous_card_data = last_card_check
                        _Common.store_to_temp_data(previous_card_no, json.dumps(previous_card_data))
                        # TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.emit('UPDATE_BALANCE_ONLINE|BCA_NEED_REVERSAL')
                        # param_reversal = QPROX_COMMAND['REVERSAL_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
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
    _QPROX.reset_card_contactless()
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    previous_card_no = last_card_check['card_no']
    previous_card_balance = last_card_check['balance']
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
        LOGGER.warning(('CARD_NO NOT DETECTED', check_card_balance, previous_card_no, trxid))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_TOPUP_CORRECTION#RC_1024')
        return
    if previous_card_no != check_card_balance['card_no']:
        LOGGER.warning(('BCA_CARD_MISSMATCH', trxid, previous_card_no, check_card_balance['card_no']))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_MISSMATCH')
        return
    res_bca_card_info, bca_card_info = _QPROX.bca_card_info()
    if res_bca_card_info is False:
        LOGGER.warning(('BCA_CARD_INFO_FAILED', trxid, bca_card_info))
        bca_card_info = json.loads(bca_card_info)
        # rc = bca_card_info.get('Result', 'FFFF')
        rc = _Common.LAST_READER_ERR_CODE
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_INFO_MISSMATCH#RC_'+rc)
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
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#END')
    confirm_bca_topup({
        'card_data': bca_card_info,
        'card_no': check_card_balance['card_no'],
        'last_balance': check_card_balance['balance']
    })
    

def start_retry_topup_online_bri(amount, trxid):
    _Helper.get_thread().apply_async(retry_topup_online_bri, (amount, trxid,))


def retry_topup_online_bri(amount, trxid):
    _QPROX.reset_card_contactless()
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    previous_card_no = last_card_check['card_no']
    previous_card_balance = last_card_check['balance']
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
        # Card Balance Failed Meaning No Card Presense (Err. 1024)
        LOGGER.warning(('CARD_NO NOT DETECTED', check_card_balance, previous_card_no, trxid))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BRI_TOPUP_CORRECTION#RC_1024')
        return
    if previous_card_no != check_card_balance['card_no']:
        LOGGER.warning(('BRI_CARD_MISSMATCH', trxid, previous_card_no, check_card_balance['card_no']))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_MISSMATCH')
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
                'bank_id': '3',
                'bank_name': 'BRI',
            }
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        _Common.remove_temp_data(trxid)
        _Common.remove_temp_data(previous_card_no)
    else:
        # Call Reversal & Refund BRI
        _param = QPROX_COMMAND['REVERSAL_ONLINE_BRI'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + _Common.SLOT_BRI + '|' + LAST_BRI_ACCESS_TOKEN + '|' + LAST_BRI_REFF_NO_HOST + '|'
        response, result = _Command.send_request(param=_param, output=None)
        # {"Result":"0000","Command":"024","Parameter":"01234567|1234567abc|165eea86947a4e9483d1902f93495fc6|3",
        # "Response":"6013500601505143|1000|66030","ErrorDesc":"Sukses"}
        LOGGER.debug((response, result))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#END')
        refund_bri_pending(LAST_BRI_PENDING_RESULT)
    

def start_retry_topup_online_dki(amount, trxid):
    _Helper.get_thread().apply_async(retry_topup_online_dki, (amount, trxid,))


def retry_topup_online_dki(amount, trxid):
    _QPROX.reset_card_contactless()
    last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
    previous_card_no = last_card_check['card_no']
    previous_card_balance = last_card_check['balance']
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
        LOGGER.warning(('CARD_NO NOT DETECTED', check_card_balance, previous_card_no, trxid))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('DKI_TOPUP_CORRECTION#RC_1024')
        return
    if previous_card_no != check_card_balance['card_no']:
        # Call Reversal DKI
        if _Common.DKI_TOPUP_ONLINE_BY_SERVICE is True:
            _QPROX.reversal_topup_dki_by_service(amount, trxid)
        else:
            reversal_balance({
            'card_no': previous_card_no,
            'reff_no': trxid
        },'DKI', 'TOPUP')
        LOGGER.warning(('DKI_CARD_MISSMATCH', trxid, previous_card_no, check_card_balance['card_no']))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_MISSMATCH')
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
                'bank_id': '5',
                'bank_name': 'DKI',
            }
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
        _Common.remove_temp_data(trxid)
        _Common.remove_temp_data(previous_card_no)
        output['reff_no'] = trxid
        confirm_dki_topup(output)
    else:
        # Call Reversal DKI
        if _Common.DKI_TOPUP_ONLINE_BY_SERVICE is True:
            _QPROX.reversal_topup_dki_by_service(amount, trxid)
        else:
            reversal_balance({
            'card_no': previous_card_no,
            'reff_no': trxid
        },'DKI', 'TOPUP')
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#END')
    
    
def start_topup_online_dki(card_no, amount, trxid):
    if _Common.DKI_TOPUP_ONLINE_BY_SERVICE is True:
        return _QPROX.start_topup_dki_by_service(amount, trxid)
    else:
        bank = 'DKI'
        _Helper.get_thread().apply_async(topup_online, (bank, card_no, amount, trxid))

def start_topup_online_bri(cardno, amount, trxid):
    bank = 'BRI'
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount, trxid))


def start_topup_online_bca(cardno, amount, trxid):
    bank = 'BCA'
    _Helper.get_thread().apply_async(topup_online, (bank, cardno, amount, trxid))


LAST_MANDIRI_C2C_SUCCESS_RESULT = None
LAST_BCA_REFF_ID = ''
LAST_BRI_PENDING_RESULT = None
# MANDIRI_DEPOSIT_RELOAD_IN_PROGRES = []


def topup_online(bank, cardno, amount, trxid=''):
    global LAST_MANDIRI_C2C_SUCCESS_RESULT, LAST_BRI_PENDING_RESULT
    
    try:
        validate_card = _QPROX.revalidate_card(cardno)
        if not validate_card:
            return False
    except Exception as e:
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#CARD_MISSMATCH')
        return False
    # if bank in ['BRI', 'BCA'] and _ConfigParser.get_set_value_temp('TEMPORARY', 'secret^test^code', '0000') == '310587':
    #     sleep(2)
    #     output = {
    #             'last_balance': '999999',
    #             'report_sam': 'DUMMY',
    #             'card_no': _QPROX.LAST_CARD_CHECK['card_no'],
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
    # LAST_CARD_CHECK = {
    #     'balance': balance,
    #     'card_no': card_no,
    #     'bank_type': result.split('|')[2].replace('#', ''),
    #     'bank_name': bank_name,
    #     'able_topup': '0000',
    # }
    try:
        if bank is None or bank not in _Common.ALLOWED_BANK_PENDING_ONLINE:
            LOGGER.warning((bank, 'NOT_ALLOWED_PENDING_ONLINE'))
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#TOPUP_FEATURED_CLOSED')
            return False
        # last_card_check = _QPROX.LAST_CARD_CHECK
        last_card_check = _Common.load_from_temp_data('last-card-check', 'json')

        if bank == 'BRI':
            if not _Common.BRI_SAM_ACTIVE:
                _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#SAM_NOT_ACTIVE')
                return False
            _param = {
                'card_no': cardno,
                'amount': amount,
                'invoice_no': trxid,
                'time': _Helper.epoch('MDS')
            }
            # pending_result = _MDSService.mds_online_topup(bank, _param)
            pending_result = False
            if not _Common.exist_temp_data(trxid):
                _Common.LAST_BRI_ERR_CODE = ''
                pending_result = pending_balance(_param, bank='BRI', mode='TOPUP')
                if not pending_result:
                    _Common.LAST_BRI_ERR_CODE = '30'
                    if _Common.NEW_TOPUP_FAILURE_HANDLER:
                        _QPROX.new_topup_failure_handler('BRI', trxid, amount)
                        return
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#PENDING_TOPUP')
                    return False
                _Common.store_to_temp_data(trxid, json.dumps(_param))
            # _Common.update_to_temp_data('bri-success-pending', trxid)
            _param = QPROX_COMMAND['UPDATE_BALANCE_ONLINE_BRI'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + _Common.SLOT_BRI + '|' 
            update_result = update_balance(_param, bank='BRI', mode='TOPUP')
            if not update_result:
                # _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BRI_UPDATE_BALANCE_ERROR')
                pending_result.update({'err_code': _Common.LAST_READER_ERR_CODE})
                _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(pending_result))
                _Common.LAST_BRI_ERR_CODE = '31'
                if _Common.NEW_TOPUP_FAILURE_HANDLER:
                    pending_result['trxid'] = trxid
                    pending_result['access_token'] = LAST_BRI_ACCESS_TOKEN
                    pending_result['bank_reff_no'] = LAST_BRI_REFF_NO_HOST
                    _QPROX.new_topup_failure_handler('BRI', trxid, amount, pending_result)
                    return
                rc = _Common.LAST_READER_ERR_CODE
                _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BRI_TOPUP_CORRECTION#RC_'+rc)
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
                    if not pending_result:
                        return False
                    pending_result['trxid'] = trxid
                    LAST_BRI_PENDING_RESULT = pending_result
                    # refund_bri_pending(pending_result)
                return False
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
                    'prev_balance': last_card_check['balance'],
                    'deposit_no': 'N/A',
                    'deposit_prev_balance': 'N/A',
                    'deposit_last_balance': 'N/A',
                    'topup_report': 'N/A'
                }
            LOGGER.info((str(output)))
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
            return True
        elif bank == 'BCA':
            # last_check = _QPROX.LAST_CARD_CHECK            
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
            #             _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#PENDING_TOPUP')
            #             return
            #         _Common.store_to_temp_data(trxid, json.dumps(_param))
            # else:
            #     LOGGER.debug(('Previous Failed BCA Reversal Detected For', cardno))
            #     param_reversal = QPROX_COMMAND['REVERSAL_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|' + LAST_BCA_REFF_ID + '|' 
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
                _Common.LAST_BCA_ERR_CODE = ''
                pending_result = pending_balance(_param, bank='BCA', mode='TOPUP')
                # pending_result = _MDSService.mds_online_topup(bank, _param)
                if not pending_result:
                    _Common.LAST_BCA_ERR_CODE = '40'
                    if _Common.NEW_TOPUP_FAILURE_HANDLER:
                        _QPROX.new_topup_failure_handler('BCA', trxid, amount)
                        return False
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#PENDING_TOPUP')
                    return False
                _Common.store_to_temp_data(trxid, json.dumps(_param))
            # if _Common.exist_temp_data(cardno):
            #     _param = QPROX_COMMAND['UPDATE_BALANCE_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            # else:
            #     _param = QPROX_COMMAND['REVERSAL_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            _param = QPROX_COMMAND['UPDATE_BALANCE_ONLINE_BCA'] + '|' + TOPUP_TID + '|' + TOPUP_MID + '|' + TOPUP_TOKEN +  '|'
            update_result = update_balance(_param, bank='BCA', mode='TOPUP')
            # if update_result is False:
            #     _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_UPDATE_BALANCE_ERROR')
            #     return
            if update_result is False or update_result == 'BCA_TOPUP_CORRECTION':
                _Common.LAST_BCA_ERR_CODE = '41'
                if _Common.NEW_TOPUP_FAILURE_HANDLER:            
                    pending_result.update({'err_code': _Common.LAST_READER_ERR_CODE})
                    _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(pending_result))
                    _QPROX.new_topup_failure_handler('BCA', trxid, amount, pending_result)
                    return False
                rc = _Common.LAST_READER_ERR_CODE
                _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BCA_TOPUP_CORRECTION#RC_'+rc)
                return False
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
                    'prev_balance': last_card_check['balance'],
                    'deposit_no': 'N/A',
                    'deposit_prev_balance': 'N/A',
                    'deposit_last_balance': 'N/A',
                    'topup_report': 'N/A'
                }
            LOGGER.info((str(output)))
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
            return True
        elif bank == 'MANDIRI_C2C_DEPOSIT':
            if _Common.MANDIRI_ACTIVE_WALLET > _Common.C2C_THRESHOLD:
                LOGGER.warning(('DEPOSIT_STILL_SUFFICIENT', _Common.MANDIRI_ACTIVE_WALLET, _Common.C2C_THRESHOLD))
                return False
            LOGGER.info(('TRIGGER MANDIRI DEPOSIT RELOAD', _Common.MANDIRI_ACTIVE_WALLET, 'MANDIRI THRESHOLD', _Common.C2C_THRESHOLD))
            invoice_no = 'refill'+str(_Helper.epoch())
            if len(trxid) > 0:
                invoice_no = trxid
            _Common.store_to_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES', invoice_no)
            param = {
                'card_no': cardno,
                'amount': amount,
                'invoice_no': invoice_no,
                'time': _Helper.epoch('MDS')
            }
            # pending_result = _MDSService.mds_online_topup(bank, param)
            pending_result = pending_balance(param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
            if not pending_result:
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|PENDING_ERROR')
                _Common.remove_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES')
                _Common.online_logger([pending_result, bank, cardno, amount], 'general')
                return False
            # Do Reset Memory Mandiri C2C Wallet To Prevent Usage (Miss Match Card Info)
            prev_balance = _Common.MANDIRI_ACTIVE_WALLET
            # param['prev_deposit_balance'] = prev_balance
            # LAST_MANDIRI_C2C_SUCCESS_RESULT = {**param, **pending_result}
            # LAST_MANDIRI_C2C_SUCCESS_RESULT = param.update(pending_result)
            # LOGGER.debug(('LAST_MANDIRI_C2C_SUCCESS_RESULT', str(LAST_MANDIRI_C2C_SUCCESS_RESULT)))
            if not _Common.MDR_C2C_TRESHOLD_USAGE:
                _Common.MANDIRI_ACTIVE_WALLET = 0
            send_kiosk_status()
            _param = QPROX_COMMAND['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
            update_result = update_balance(_param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
            if not update_result:
                mdr_update_postponed_data = {
                        'reff_no'       : param['invoice_no'],
                        'expirity'      : _Helper.epoch() + (60*60),
                        'amount'        : amount,
                        'prev_balance'  : prev_balance
                    }
                LOGGER.info(('MDR_DEPOSIT_UPDATE_POSTPONED', str(mdr_update_postponed_data)))
                _Common.store_to_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED', json.dumps(mdr_update_postponed_data))
                TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.emit('TOPUP_ONLINE_DEPOSIT|UPDATE_ERROR')
                _Helper.get_thread().apply_async(job_retry_reload_mandiri_deposit, (True,))
                _Common.remove_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES')
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
            # Additional Action Update Balance Mandiri
            _Common.remove_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES')
            _Helper.get_thread().apply_async(check_mandiri_deposit_update_balance,)
            return output        
        elif bank == 'DKI':
            _param = {
                'card_no': cardno,
                'amount': amount,
                'reff_no': trxid,
                'invoice_no': trxid,
                'time': _Helper.epoch('MDS')
            }
            # pending_result = _MDSService.mds_online_topup(bank, _param)
            pending_result = False
            if not _Common.exist_temp_data(trxid):
                _Common.LAST_DKI_ERR_CODE = ''
                pending_result = pending_balance(_param, bank='DKI', mode='TOPUP')
                if not pending_result:
                    _Common.LAST_DKI_ERR_CODE = '50'
                    if _Common.NEW_TOPUP_FAILURE_HANDLER:
                        _QPROX.new_topup_failure_handler('DKI', trxid, amount)
                        return False
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#PENDING_TOPUP')
                    return False
                _Common.store_to_temp_data(trxid, json.dumps(_param))
            # _Common.update_to_temp_data('bri-success-pending', trxid)
            __param = QPROX_COMMAND['REQUEST_TOPUP_DKI'] + '|' + amount + '|'
            response, result = _Command.send_request(param=__param, output=None)
            LOGGER.debug((__param, bank, response, result))
            last_card_check = _Common.load_from_temp_data('last-card-check', 'json')

            if response == 0 and '|' in result:
                card_info = result.split('|')[5] + result.split('|')[3] + result.split('|')[4]
                _param['card_info'] = card_info
                _param['prev_balance'] = last_card_check['balance']
                update_result = update_balance(_param, bank='DKI', mode='TOPUP')
                if not update_result:
                    _Common.LAST_DKI_ERR_CODE = '51'
                # _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('BRI_UPDATE_BALANCE_ERROR')
                    if _Common.NEW_TOPUP_FAILURE_HANDLER:
                        pending_result.update({'err_code': _Common.LAST_READER_ERR_CODE})
                        _Common.store_to_temp_data(trxid+'-last-audit-result', json.dumps(pending_result))
                        _QPROX.new_topup_failure_handler('DKI', trxid, amount, pending_result)
                        return False
                    else:
                        rc = _Common.LAST_READER_ERR_CODE
                        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('DKI_TOPUP_CORRECTION#RC_'+rc)
                        return False
                
                ___param = QPROX_COMMAND['CONFIRM_TOPUP_DKI'] + '|' + update_result['data_to_card'] + '|'
                response, result = _Command.send_request(param=___param, output=None)
                LOGGER.debug((___param, bank, response, result))
                # {
                #     "Command": "052",
                #     "ErrorDesc": "Sukses",
                #     "Parameter": "112233445566778800000001B5DDB812",
                #     "Response": "000007D08BB3B702",
                #     "Result": "0000"
                # }
                if response == 0 and len(result) > 3:
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
                            'report_sam': result,
                            'card_no': update_result['card_no'],
                            'report_ka': 'N/A',
                            'bank_id': '5',
                            'bank_name': 'DKI',
                            'prev_balance': last_card_check['balance'],
                            'deposit_no': 'N/A',
                            'deposit_prev_balance': 'N/A',
                            'deposit_last_balance': 'N/A',
                            'topup_report': 'N/A'
                        }
                    LOGGER.info((str(output)))
                    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('0000|'+json.dumps(output))
                    _param['last_balance'] = update_result['last_balance']
                    confirm_dki_topup(_param)
                    # Must Stop Process Here As Success TRX
                    return True        
            # rc = json.loads(result).get('Result', 'FFFF')    
            rc = _Common.LAST_READER_ERR_CODE
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('DKI_TOPUP_CORRECTION#RC_'+rc)
            return False
        else:
            _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#UNKNOW_BID')
            return False
    except Exception as e:
        LOGGER.warning((bank, cardno, amount, e))
        _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.emit('TOPUP_ERROR#GENERAL_EXCEPTION')
        return False
    

def start_do_topup_deposit_mandiri():
    if _Common.exist_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'):
        LOGGER.warning(('ANOTHER MANDIRI_DEPOSIT_RELOAD_IN_PROGRES', str(_Common.load_from_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'))))
        return
    if _Common.exist_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED'):
        LOGGER.warning(('FOUND MDR_DEPOSIT_UPDATE_POSTPONED', str(_Common.load_from_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES', 'json'))))
        return
    if _Common.MANDIRI_ACTIVE_WALLET > _Common.MANDIRI_THRESHOLD:
        LOGGER.warning(('DEPOSIT_STILL_SUFFICIENT', _Common.MANDIRI_ACTIVE_WALLET, _Common.MANDIRI_THRESHOLD))
        return
    bank = 'MANDIRI_C2C_DEPOSIT'
    card_no = _Common.C2C_DEPOSIT_NO
    amount = _Common.C2C_TOPUP_AMOUNT
    trx_id = 'refill'+str(_Helper.now())
    _Helper.get_thread().apply_async(topup_online, (bank, card_no, amount, trx_id))


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
        status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bni/confirm', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            # _Common.remove_temp_data(data['reff_no'])
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
        _url = TOPUP_URL
        if _Common.DEV_MODE_TOPUP_BCA:
            _url = _Common.UPDATE_BALANCE_URL_DEV
        status, response = _HTTPAccess.post_to_url(url=_url + 'topup-bca/confirm', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            # _Common.remove_temp_data(data['reff_no'])
            return True
        else:
            if _Common.LIVE_MODE:
                param['endpoint'] = 'topup-bca/confirm'
                _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-bca/confirm', payload=param)
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False
    

def confirm_dki_topup(data):
    if _Helper.empty(data):
        return False
    LOGGER.info((str(data)))
    try:
        param = {
            'token': TOPUP_TOKEN,
            'mid': TOPUP_MID,
            'tid': TOPUP_TID,
            'card_no': data['card_no'],
            'last_balance': data['last_balance'],
            'reff_no': data['reff_no']
        }
        _url = TOPUP_URL
        status, response = _HTTPAccess.post_to_url(url=_url + 'topup-dki/confirm', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            _Common.remove_temp_data(data['reff_no'])
            return True
        else:
            if _Common.LIVE_MODE:
                param['endpoint'] = 'topup-dki/confirm'
                _Common.store_request_to_job(name=_Helper.whoami(), url=TOPUP_URL + 'topup-dki/confirm', payload=param)
            return False
    except Exception as e:
        LOGGER.warning(str(e))
        return False


def refund_bri_pending(data=None):
    if _Helper.empty(data) or data is None:
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
        status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bri/refund', param=param)
        LOGGER.debug((str(param), str(status), str(response)))
        if status == 200 and response['response']['code'] == 200:
            _Common.remove_temp_data(data['trxid'])
            return True
        else:
            _Common.LAST_BRI_ERR_CODE = '33'
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
        status, response = _HTTPAccess.get_from_url(url=_Common.MANDIRI_CARD_BLOCKED_URL)
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


def get_mdd_card_blocked_list():
    try:
        status, response = _HTTPAccess.get_from_url(url=_Common.BACKEND_URL + 'card/blacklist')
        if status == 200 and response['response']['code'] == 200:
            if not _Helper.empty(response['data']['blacklist']):
                content = ''
                for data in response['data']['blacklist']:
                    content += data + '\n'
                _Common.store_to_temp_data('general_card_blocked_list', content)
                _Common.GENERAL_CARD_BLOCKED_LIST = response['data']['blacklist']
                LOGGER.info(('GENERAL_CARD_BLOCKED_LIST UPDATED'))
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
        status, response = _HTTPAccess.post_to_url(url=TOPUP_URL + 'topup-bca/reset-session', param=param)
        LOGGER.debug((str(status), str(response)))
    except Exception as e:
        LOGGER.warning((e))


def do_topup_deposit_mandiri(override_amount=0):
    # global MANDIRI_DEPOSIT_RELOAD_IN_PROGRES
    # Handle Single Attempt For Auto Reload
    if _Common.exist_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'):
        LOGGER.warning(('ANOTHER MANDIRI_DEPOSIT_RELOAD_IN_PROGRES', str(_Common.load_from_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'))))
        return 'FAILED_ANOTHER_MANDIRI_DEPOSIT_RELOAD_IN_PROGRES'
    if _Common.exist_temp_data('MDR_DEPOSIT_UPDATE_POSTPONED'):
        LOGGER.warning(('FOUND MDR_DEPOSIT_UPDATE_POSTPONED', str(_Common.load_from_temp_data('MANDIRI_DEPOSIT_RELOAD_IN_PROGRES', 'json'))))
        return 'FOUND_MDR_DEPOSIT_UPDATE_POSTPONED'
    _amount = _Common.C2C_TOPUP_AMOUNT
    if override_amount > 0:
        _amount = int(override_amount)
    else:
        if _Common.MANDIRI_ACTIVE_WALLET > _Common.MANDIRI_THRESHOLD:
            LOGGER.warning(('DEPOSIT_STILL_SUFFICIENT', _Common.MANDIRI_ACTIVE_WALLET, _Common.MANDIRI_THRESHOLD))
            return 'DEPOSIT_STILL_SUFFICIENT'
    if MDR_DEPOSIT_UPDATE_BALANCE_PROCESS:
        return 'ANOTHER_TOPUP_PROCESS_STILL_RUNNING'
    bank = 'MANDIRI_C2C_DEPOSIT'
    card_no = _Common.C2C_DEPOSIT_NO
    amount = _amount
    trx_id = 'refill'+str(_Helper.now())
    _Helper.get_thread().apply_async(topup_online, (bank, card_no, amount, trx_id))
    return 'TASK_EXECUTED_IN_MACHINE'


def check_mandiri_deposit_update_balance():
    try:
        prev_balance = _Common.MANDIRI_ACTIVE_WALLET
        if not _Common.MDR_C2C_TRESHOLD_USAGE:
            _Common.MANDIRI_ACTIVE_WALLET = 0
        # send_kiosk_status()
        _param = QPROX_COMMAND['UPDATE_BALANCE_C2C_MANDIRI'] + '|' +  str(_Common.C2C_DEPOSIT_SLOT) + '|' + _Common.TID + '|' + _Common.CORE_MID + '|' + _Common.CORE_TOKEN + '|'
        update_result = update_balance(_param, bank='MANDIRI', mode='TOPUP_DEPOSIT')
        if not update_result:
            print("pyt: check_mandiri_deposit_update_balance "+ str(update_result))
            LOGGER.debug(('UPDATE_BALANCE', str(update_result)))
            result = False
        else:
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
            _DAO.create_today_report(_Common.TID)
            _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_count'], 1)
            _DAO.update_today_summary_multikeys(['mandiri_deposit_refill_amount'], int(update_result['topup_amount']))
            _DAO.update_today_summary_multikeys(['mandiri_deposit_last_balance'], int(output['last_balance']))
            _Common.store_upload_sam_audit(sam_audit_data)   
            send_kiosk_status()
            result = True    
    except Exception as e:
        print("pyt: check_mandiri_deposit_update_balance "+ str(e))
        LOGGER.warning((e))
        result = False
    finally:
        _QPROX.mdr_c2c_balance_info()
        return result


def start_check_topup_readiness():
    _Helper.get_thread().apply_async(check_topup_readiness)


def check_topup_readiness():
    try:
        ping_status = _HTTPAccess.is_online_by_ip(source=_Helper.whoami())
        ready = {
            'balance_mandiri': str(_Common.MANDIRI_ACTIVE_WALLET),
            'balance_bni': str(_Common.BNI_ACTIVE_WALLET),
            'mandiri': 'AVAILABLE' if (_QPROX.INIT_MANDIRI is True and _Common.MANDIRI_ACTIVE_WALLET > 0 and not MDR_DEPOSIT_UPDATE_BALANCE_PROCESS) is True else 'N/A',
            'bni': 'AVAILABLE' if (_QPROX.INIT_BNI is True and _Common.BNI_ACTIVE_WALLET > 0 and not BNI_DEPOSIT_UPDATE_BALANCE_PROCESS) is True else 'N/A',
            'bri': 'AVAILABLE' if (_Common.BRI_SAM_ACTIVE is True and ping_status) else 'N/A',
            'bca': 'AVAILABLE' if (_Common.BCA_TOPUP_ONLINE is True and ping_status) else 'N/A',
            'dki': 'AVAILABLE' if (_Common.DKI_TOPUP_ONLINE_BY_SERVICE is True or _Common.DKI_TOPUP_ONLINE is True) and  ping_status else 'N/A',
        }
        TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit(json.dumps(ready))
    except Exception as e:
        LOGGER.warning((str(e)))
        TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.emit('ERROR')
