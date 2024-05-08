__author__ = "wahyudi@multidaya.id"

import json
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _Common
from _tTools import _Helper
from _nNetwork import _HTTPAccess
import sys
from operator import itemgetter
from _dDAO import _DAO
from _dDevice import _EDC
from _sService import _QRPaymentService

# import os


class PPOBSignalHandler(QObject):
    __qualname__ = 'PPOBSignalHandler'
    SIGNAL_GET_PRODUCTS = pyqtSignal(str)
    SIGNAL_CHECK_PPOB = pyqtSignal(str)
    SIGNAL_TRX_PPOB = pyqtSignal(str)
    SIGNAL_TRX_CHECK = pyqtSignal(str)
    SIGNAL_CHECK_BALANCE = pyqtSignal(str)
    SIGNAL_CHECK_CUSTOMER = pyqtSignal(str)
    SIGNAL_TRANSFER_BALANCE = pyqtSignal(str)


PPOB_SIGNDLER = PPOBSignalHandler()
LOGGER = logging.getLogger()


def start_get_ppob_product():
    _Helper.get_thread().apply_async(get_ppob_product)


def start_init_ppob_product():
    signal = False
    _Helper.get_thread().apply_async(get_ppob_product, (signal,))


def get_ppob_product(signal=True):
    _check_prev_ppob = _Common.load_from_temp_data(temp='ppob-product', mode='json')
    _last_get_product = _Common.get_config_value('last^get^ppob', digit=True)
    if ( _last_get_product + (3 * 24 * 60 * 60 * 1000)) > _Helper.now() and not _Common.empty(_check_prev_ppob):
        products = _check_prev_ppob
    else:
        s, r = _HTTPAccess.get_from_url(url=_Common.BACKEND_URL+'get/product', log=False)
        if s == 200 and r['result'] == 'OK':
            products = r['data']
            _Common.LAST_GET_PPOB = _Helper.now()
            _Common.log_to_temp_config('last^get^ppob', _Common.LAST_GET_PPOB)
            _Common.store_to_temp_data(temp='ppob-product', content=json.dumps(products), log=False)
        else:
            products = _Common.load_from_temp_data(temp='ppob-product', mode='json')
    # products = store_image_item(products)
    products = sorted(products, key=itemgetter('status'))
    if signal is True:
        PPOB_SIGNDLER.SIGNAL_GET_PRODUCTS.emit(json.dumps(products))


def store_image_item(products):
    for p in range(len(products)):
        old_path_category = products[p]['category_url']
        new_path_category = sys.path[0]+'/'+_Common.VIEW_FOLDER+'/source/ppob_category'
        store_category, category = _HTTPAccess.item_download(old_path_category, new_path_category)
        if store_category is True:
            products[p]['category_url'] = 'source/ppob_category/'+category
        operator = products[p]['operator']
        old_path_icon = 'https://api.trendpos.id/mcash/icon?operator='+operator.lower()
        new_path_icon = sys.path[0]+'/'+_Common.VIEW_FOLDER+'/source/ppob_icon'
        store_icon, icon = _HTTPAccess.item_download(old_path_icon, new_path_icon, name=operator+'.png')
        if store_icon is True:
            products[p]['icon_url'] = 'source/ppob_icon/'+icon
    return products


def start_check_ppob_product(msisdn, product_id):
    _Helper.get_thread().apply_async(check_ppob_product, (msisdn, product_id,))


def check_ppob_product(msisdn='', product_id=''):
    if _Common.empty(msisdn):
        LOGGER.warning((msisdn, product_id, 'MISSING_MSISDN'))
        PPOB_SIGNDLER.SIGNAL_CHECK_PPOB.emit('PPOB_CHECK|MISSING_MSISDN')
        return
    if _Common.empty(product_id):
        LOGGER.warning((msisdn, product_id, 'MISSING_PRODUCT_ID'))
        PPOB_SIGNDLER.SIGNAL_CHECK_PPOB.emit('PPOB_CHECK|MISSING_PRODUCT_ID')
        return
    try:
        # mcash/cek/TELKOM/161101001530
        # mcash/cek/BPJS/0001264047118
        # mcash/cek/PLN/173000000485
        # mcash/cek/MATRIX/08164300888
        # mcash/cek/PALYJA/000603544
        param = {
            'msisdn': msisdn,
            'product_id': product_id,
            'reff_no': _Common.TID+"-"+_Helper.time_string('%Y%m%d%H%M%S')
        }
        s, r = _HTTPAccess.post_to_url(url=_Common.BACKEND_URL+'ppob/check', param=param)
        if s == 200 and r['result'] == 'OK':
            output = r['data']
            customer_name = ''
            prod_desc = ''
            total_pay = 0
            payable = 0
            if 'BERHASIL' in output['msg']:
                customer_name = extract_customer_name(msisdn, output['msg'])
                if product_id == 'OMNITSEL':
                    customer_name = extract_prod_desc(msisdn, output['msg'])
                total_pay = int(output['ori_amount']) + int(output['admin_fee'])
                payable = 1
            output['product_id'] = product_id
            output['customer'] = customer_name
            output['total'] = total_pay
            output['payable'] = payable
            output['msisdn'] = msisdn
            output['category'] = product_id
            # _Helper.dump(output)
            PPOB_SIGNDLER.SIGNAL_CHECK_PPOB.emit('PPOB_CHECK|' + json.dumps(output))
        else:
            PPOB_SIGNDLER.SIGNAL_CHECK_PPOB.emit('PPOB_CHECK|ERROR')
        LOGGER.debug((msisdn, product_id, str(r)))
    except Exception as e:
        LOGGER.warning((msisdn, product_id, str(e)))
        PPOB_SIGNDLER.SIGNAL_CHECK_PPOB.emit('PPOB_CHECK|ERROR')


def extract_customer_name(key, message):
    customer = ''
    if 'GAGAL' in message:
        return customer
    key = key[:-2]
    idx = message.find(key)
    if idx < 0:
        return customer
    clean_message = message[idx:].split(' adalah')[0]
    messages = clean_message.split(' ')
    c = []
    for m in messages:
        if m not in [' -a-n', 'adalah'] and not m.isdigit() and messages[0] != m and len(m) > 1:
            c.append(m)
    customer = ' '.join(c)
    return customer


def extract_prod_desc(key, message):
    desc = ''
    if 'GAGAL' in message:
        return desc
    key = key[:-2]
    idx = message.find(key)
    if idx < 0:
        return desc
    clean_message = message[idx:].split(' adalah')[0]
    messages = clean_message.split(' ')
    c = []
    for m in messages:
        if m not in [' -a-n', 'adalah'] and messages[0] != m and len(m) > 1:
            c.append(m)
    desc = ' '.join(c)
    return desc


def start_do_pay_ppob(payload):
    mode = 'PAY'
    _Helper.get_thread().apply_async(do_trx_ppob, (payload, mode,))


def start_do_topup_ppob(payload):
    mode = 'TOPUP'
    _Helper.get_thread().apply_async(do_trx_ppob, (payload, mode,))


def do_trx_ppob(payload, mode='PAY'):
    # product_id,msisdn,amount,reff_no,payment_type,product_category,operator
    try:
        payload = json.loads(payload)
        if _Common.empty(payload['msisdn']):
            LOGGER.warning((str(payload), 'MISSING_MSISDN'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_MSISDN')
            return
        if _Common.empty(payload['product_id']):
            LOGGER.warning((str(payload), 'MISSING_PRODUCT_ID'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_PRODUCT_ID')
            return
        if _Common.empty(payload['amount']):
            LOGGER.warning((str(payload), 'MISSING_AMOUNT'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_AMOUNT')
            return
        if _Common.empty(payload['reff_no']):
            LOGGER.warning((str(payload), 'MISSING_REFF_NO'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_REFF_NO')
            return
        if _Common.empty(payload['product_category']):
            LOGGER.warning((str(payload), 'MISSING_PRODUCT_CATEGORY'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_PRODUCT_CATEGORY')
            return
        if _Common.empty(payload['payment_type']):
            LOGGER.warning((str(payload), 'MISSING_PAYMENT_TYPE'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_PAYMENT_TYPE')
            return
        if _Common.empty(payload['operator']):
            LOGGER.warning((str(payload), 'MISSING_OPERATOR'))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|MISSING_OPERATOR')
            return
        if _Common.LAST_PPOB_TRX is not None and _Common.LAST_PPOB_TRX['payload'] == payload:
            if not _Common.LAST_PPOB_TRX['error']:
                PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|' + json.dumps(_Common.LAST_PPOB_TRX['result']))
            else:
                PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|ERROR')
            LOGGER.warning(('Duplicate PPOB TRX Payload', str(_Common.LAST_PPOB_TRX)))
            return
        _Helper.dump(payload)
        # NOTICE: Handling OVO Include Admin Fee
        if 'product_channel' in payload.keys():
            if payload['product_channel'] == 'MDD' and payload['operator'] == 'CASHIN OVO':
                payload['amount'] = str(int(payload['amount']) + 1500)
        # =================================
        url = _Common.BACKEND_URL+'ppob/pay'
        if mode == 'TOPUP':
            url = _Common.BACKEND_URL+'ppob/topup'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        _Common.LAST_PPOB_TRX = {
            'payload': payload,
            'result': r,
            'error': True
        }
        if s == 200 and r['result'] == 'OK' and r['data'] is not None:
            _Common.LAST_PPOB_TRX['result'] = r['data']
            _Common.LAST_PPOB_TRX['error'] = False
            LOGGER.info(('Store Last PPOB TRX', str(_Common.LAST_PPOB_TRX)))
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|' + json.dumps(r['data']))
            LOGGER.debug((str(payload), mode, str(r)))
            # Remove TRX Failure Under This reff_no
            _DAO.delete_transaction_failure({
                'reff_no': payload['reff_no'],
                'tid': _Common.TID,            
            })
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|ERROR')
            LOGGER.warning((str(payload), mode, str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), mode, str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PPOB_TRX|ERROR')


def start_check_status_trx(reff_no):
    _Helper.get_thread().apply_async(do_check_trx, (reff_no,))


def do_check_trx(reff_no):
    if _Common.empty(reff_no):
        LOGGER.warning((str(reff_no), 'MISSING_REFF_NO'))
        PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_CHECK|MISSING_REFF_NO')
        return
    # Add Check Local TRX Here
    payload = {
        'reff_no': reff_no,
        'tid': _Common.TID
    }
    try:
        pending_record = _DAO.get_transaction_failure(param=payload)
        # LOGGER.debug(('pending_record', str(pending_record)))
        if len(pending_record) > 0:
            data = pending_record.__getitem__(0)
            time_stamp = data.get('createdAt')/1000
            remarks = json.loads(data.get('remarks'))
            remarks.pop('payment_error')
            remarks.pop('process_error')
            r = {
                'date': _Helper.convert_epoch(time_stamp),
                'category': remarks.get('shop_type', '').upper(),
                'trx_id': data.get('trxid'),
                'payment_method': data.get('paymentMethod'),
                'product_id': data.get('trxid'),
                'receipt_amount': remarks.get('payment_received'),
                'amount': remarks.get('value'),
                'status': 'PENDING',
                'source': data.get('failureType'),
                'remarks': remarks,
                'retry_able': _Common.check_retry_able(remarks),
                'show_info_cs': 0,
                'promo_data': get_promo_data(data.get('trxid'))
            }
            LOGGER.info(('INITIAL RETRY_ABLE', r['retry_able']))
            LOGGER.info(('START VALIDATE PAYMENT'))
            # Add Debit & QR Payment Check
            # Serialise QR Provider Name
            if ' ' in r['payment_method'].upper():
                # QRIS BNI to BNI-QRIS / QRIS BCA to BCA-QRIS
                r['payment_method'] = r['payment_method'].split(' ')[1] + '-QRIS'
            ext_channel = list(_Common.QR_PROD_STATE.keys())
            ext_channel.append('DEBIT')
            if r['payment_method'].upper() in ext_channel:
                r['retry_able'] = 0
                r['status'] = 'FAILED'
                check_trx_id = remarks.get('host_trx_id', r['product_id'])
                qr_provider = remarks.get('init_payment', r['payment_method'])
                if ' ' in qr_provider.upper():
                    # QRIS BNI to BNI-QRIS / QRIS BCA to BCA-QRIS
                    qr_provider = qr_provider.split(' ')[1] + '-QRIS'
                status, result = validate_payment_history(
                    payment_method = r['payment_method'], 
                    trx_id = check_trx_id,
                    provider = qr_provider.lower()
                    )
                if status is True:
                    remarks['payment_received'] = str(result['amount'])
                    remarks['payment_details'] = result
                    r['status'] = 'PENDING'
                    r['receipt_amount'] = str(result['amount'])
                    if r['payment_method'].lower() != 'debit':
                        if not _Helper.empty(result.get('provider', None)):
                            r['payment_method'] = result['provider']
                    r['retry_able'] = _Common.check_retry_able(remarks)
                    r['remarks'] = remarks
                else:
                    if r['payment_method'].lower() in ['debit']:
                        r['status'] = 'FAILED - Transaksi Debit Gagal'
            
            valid_duration = _Common.validate_duration_pending_code(time_stamp)
            LOGGER.info(('START CHECK DURATION', valid_duration))
            # Add Validation Max Duration (_Common.MAX_PENDING_CODE_DURATION)
            if not _Common.validate_duration_pending_code(time_stamp):
                r['retry_able'] = 0
                r['status'] = 'ALREADY EXPIRED'
                r['show_info_cs'] = 1
            valid_usage = _Common.validate_usage_pending_code(reff_no)
            LOGGER.info(('START CHECK USAGE', valid_usage))
            # Add Validation Max Retry Attempts (_Common.MAX_PENDING_CODE_RETRY)
            if not valid_usage:
                r['retry_able'] = 0
                r['status'] = 'MAX ATTEMPT EXCEEDED'
                r['show_info_cs'] = 1
            LOGGER.info(('CHECK_TRX_DATA', json.dumps(r)))
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_CHECK|' + json.dumps(r))
            del remarks
            del data
            return
        # Do check TRX server-side
        url = _Common.BACKEND_URL+'ppob/trx/detail'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK':
            # created_at as date','amount','pid as product_id','payment_method','tid','remarks','trxid as trx_id
            data = r['data']
            remarks = data.get('remarks')
            # remarks.pop('payment_error')
            # remarks.pop('process_error')
            # data['remarks'] = remarks
            # Force Close Retry TRX From Online
            if data['payment_method'] is None:
                data['payment_method'] = remarks.get('payment', '').replace('-', ' ')
            # Keep Check Actual Status To Server For Reprint Purpose (Set On Setting File)
            reprint_status = False
            if _Common.ALLOW_REPRINT_RECEIPT is True:
                check_trx_id = remarks.get('host_trx_id', data['product_id'])
                reprint_status, result = validate_payment_history(
                    payment_method=data['payment_method'], 
                    trx_id=check_trx_id,
                    provider=data['payment_method'].lower()
                )
            data['reprint_status'] = reprint_status
            data['retry_able'] = 0
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_CHECK|' + json.dumps(data))
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_CHECK|TRX_NOT_FOUND')
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_CHECK|TRX_NOT_FOUND')
        

def start_do_parking_inquiry(ticket_no):
    _Helper.get_thread().apply_async(do_parking_inquiry, (ticket_no,))


def do_parking_inquiry(ticket_no):
    try:
        url = _Common.PARKOUR_URL+'/api/pas/get_ticket'
        payload = {
                'p1': ticket_no,
                'p2': _Common.PARKOUR_SITE_ID,
                'ticket': ticket_no,
                'site_id': _Common.PARKOUR_SITE_ID
            }
        s, r = _HTTPAccess.post_to_url(url=url, param=payload, header=_HTTPAccess.get_header(
            {
                'tid': _Common.TID,
                'token': _Common.TERMINAL_TOKEN,
                'X-Signature': _Helper.to_md5(''.join([payload['ticket'], 'parkour', payload['site_id']]))
            }
        ))
        if s == 200 and r.get('code') == '00' and r.get('ticketstatus') == 'VALID'and r.get('paymentstatus') == 'UNPAID':
            data = r
            # {
            #     "ticket": "PMRSBD1131450800754",
            #     "ticketstatus": "VALID",
            #     "intime": "2024-04-15 08:38:00",
            #     "duration": "12878",
            #     "tarif": "99000",
            #     "vehicletype": "Mobil",
            #     "outtime": "",
            #     "graceperiod": "0",
            #     "location": "New Parkour RSHS Bandung",
            #     "paymentstatus": "UNPAID",
            #     "code": "00",
            #     "message": "Ticket Found!",
            #     "platenumber": "",
            #     "address": "Jl. Pasteur No.38, Pasteur, Kec. Sukajadi, Kota Bandung, Jawa Barat  ",
            #     "timenow": "2024-04-24T07:15:03+07:00"
            #   }
            data['duration_hour'] = _Helper.convert_minutes(r['duration'])
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PARKING_INQUIRY|'+json.dumps(data))
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PARKING_INQUIRY|ERROR')
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PARKING_INQUIRY|ERROR')
        
        
def start_do_parking_payment(payload):
    _Helper.get_thread().apply_async(do_parking_payment, (payload,))
    

def do_parking_payment(payload):
    payload = json.loads(payload)
    try:
        url = _Common.PARKOUR_URL+'/api/pas/payment_ticket'
        payload['site_id'] = _Common.PARKOUR_SITE_ID
        # {
        #     "ticket": "PM1139083180809",
        #     "tarif": "2000",
        #     "paymentreferenceid": "PM1139083180809-1713909922846",
        #     "paymentmethod": "gopay",
        #     "customerphone": "N/A"
        # }
        s, r = _HTTPAccess.post_to_url(url=url, param=payload, header=_HTTPAccess.get_header(
            {
                'tid': _Common.TID,
                'token': _Common.TERMINAL_TOKEN,
                'X-Signature': _Helper.to_md5(''.join([payload['ticket'], 'parkour', payload['site_id']]))
            }
        ))
        if s == 200 and r.get('code') == '00' and r.get('ticketstatus') == 'VALID'and r.get('paymentstatus') == 'PAID':
            data = r
            # paymentreferenceid as trx_id
            # {
            #     "ticket": "PM1139083180809",
            #     "ticketstatus": "VALID",
            #     "intime": "2024-04-24 04:38:38",
            #     "duration": "28",
            #     "tarif": "2000",
            #     "vehicletype": "MOTORCYCLE",
            #     "outtime": "2024-04-24 05:38:38",
            #     "graceperiod": "0",
            #     "location": "IGF Parking Masjid Istiqlal",
            #     "paymentstatus": "PAID",
            #     "code": "00",
            #     "message": "Payment Success!",
            #     "paymentreferenceid": "PM1139083180809-1713909922846",
            #     "transactionstatus": "0",
            #     "paymentmethod": "gopay",
            #     "customerphone": "N/A",
            #     "platenumber": "",
            #     "address": "Pasar Baru Central Jakarta ",
            #     "outgraceperiod": "2024-04-24 05:38:38"
            # }
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PARKING_PAYMENT|'+json.dumps(data))
            _Common.sync_parking_transaction(data)
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PARKING_PAYMENT|ERROR')
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_PPOB.emit('PARKING_PAYMENT|ERROR')


def start_do_inquiry_trx(payload):
    _Helper.get_thread().apply_async(do_inquiry_trx, (payload,))


def do_inquiry_trx(payload):
    payload = json.loads(payload)
    _Helper.dump(payload)
    try:
        url = _Common.BACKEND_URL+'ppob/trx/inquiry'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK':
            data = payload
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_INQUIRY|OK|'+json.dumps(data))
        elif s == 200 and r['result'] == 'SUSPECT':
            data = {
                'payload': payload,
                'suspect': r['data']
            }
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_INQUIRY|SUSPECT|'+json.dumps(data))
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_INQUIRY|ERROR')
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('TRX_INQUIRY|ERROR')


def validate_payment_history(payment_method='QR', trx_id=None, provider='shopeepay'):
    LOGGER.info((payment_method, trx_id, provider))
    if _Helper.empty(trx_id) is True:
        return False, None
    if payment_method.lower() == 'debit':
        result, data = _EDC.edc_mobile_check_payment(trx_id)
        edc_payment_result = data.get('status', 'FAILED')
        if edc_payment_result != 'SUCCESS':
            result = False
        return result, data
    else:
        return _QRPaymentService.one_time_check_qr(trx_id=trx_id, mode=provider)


def start_check_diva_balance(username):
    _Helper.get_thread().apply_async(check_diva_balance, (username,))


def check_diva_balance(username):
    if _Common.empty(username):
        LOGGER.warning((str(username), 'MISSING_USERNAME'))
        PPOB_SIGNDLER.SIGNAL_CHECK_BALANCE.emit('BALANCE_CHECK|MISSING_USERNAME')
        return
    payload = {
        'customer_login': username
    }
    try:
        url = _Common.BACKEND_URL+'diva/inquiry'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK' and r['data'] is not None:
            PPOB_SIGNDLER.SIGNAL_CHECK_BALANCE.emit('BALANCE_CHECK|' + json.dumps(r['data']))
        else:
            PPOB_SIGNDLER.SIGNAL_CHECK_BALANCE.emit('BALANCE_CHECK|ERROR')
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        PPOB_SIGNDLER.SIGNAL_CHECK_BALANCE.emit('BALANCE_CHECK|ERROR')


def start_global_refund_balance(payload):
    _Helper.get_thread().apply_async(global_refund_balance, (payload,))


LAST_TRANSFER_REFF_NO = ''


def start_trigger_global_refund(payload):
    store_only = True
    _Helper.get_thread().apply_async(global_refund_balance, (payload, store_only,))


def global_refund_balance(payload, store_only=False):
    global LAST_TRANSFER_REFF_NO
    payload = json.loads(payload)
    if _Common.empty(payload['reff_no']):
        LOGGER.warning((str(payload), 'MISSING_REFF_NO'))
        if not store_only:
            PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|MISSING_REFF_NO')
        return
    if LAST_TRANSFER_REFF_NO == payload['reff_no']:
        LOGGER.warning((str(payload), LAST_TRANSFER_REFF_NO, 'DUPLICATE_REFF_NO'))
        # PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|DUPLICATE_REFF_NO')
        return
    if _Common.exist_temp_data(payload['reff_no']):
        prev_data = _Common.load_from_temp_data(payload['reff_no'])
        LOGGER.warning((str(payload), str(prev_data), 'TOPUP_REFF_NO_PENDING_SUCCESS'))
        PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|TOPUP_REFF_NO_PENDING_SUCCESS')
        return
    if _Common.empty(payload['customer']):
        LOGGER.warning((str(payload), 'MISSING_CUSTOMER'))
        if not store_only:
            PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|MISSING_CUSTOMER')
        return
    if _Common.empty(payload['amount']):
        LOGGER.warning((str(payload), 'MISSING_AMOUNT'))
        if not store_only:
            PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|MISSING_AMOUNT')
        return
    if 'channel' not in payload.keys():
        LOGGER.warning((str(payload), 'MISSING_CHANNEL'))
        if not store_only:
            PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|MISSING_CHANNEL')
        return
    payload['customer_login'] = payload['customer']
    try:
        url = _Common.BACKEND_URL+'refund/global'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200:
            if r['result'] == 'OK':
                LAST_TRANSFER_REFF_NO = payload['reff_no']
                if not store_only:
                    PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|SUCCESS')
            else:
                if not store_only:
                    PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|PENDING')
        else:
            # amount: refund_amount.toString(),
            # customer: customerPhone,
            # reff_no: details.shop_type + details.epoch.toString(),
            # remarks: details,
            # mode: refundMode,
            # payment: details.payment
            # store_pending_refund(payload)
            payload['endpoint'] = 'refund/global'
            _Common.store_request_to_job(name=_Helper.whoami(), url=url, payload=payload)
            if not store_only:
                PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|ERROR')
        # LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        if not store_only:
            PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.emit('TRANSFER_BALANCE|ERROR')


def store_pending_refund(payload):
    if _Common.empty(payload) is True:
        return
    data = {
        'tid'           : _Common.TID,
        'trxid'         : payload['reff_no'],
        'amount'        : int(payload['amount']),
        'customer'      : payload['customer'],
        'refundType'    : str(payload['mode']),
        'channel'       : payload['channel'],
        'paymentType'   : payload['payment'],
        'remarks'       : json.dumps(payload['remarks'])
        }
    _DAO.insert_pending_refund(data)


def start_do_check_customer(payload, mode):
    _Helper.get_thread().apply_async(do_check_customer, (payload, mode,))


def do_check_customer(payload, mode='CASHIN OVO'):
    # msisdn,amount,reff_no,operator
    try:
        payload = json.loads(payload)
        # _Helper.dump(payload)
        url = _Common.BACKEND_URL+'ppob/check-customer'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK' and r['data'] is not None:
            PPOB_SIGNDLER.SIGNAL_CHECK_CUSTOMER.emit('CHECK_CUSTOMER|' + json.dumps(r['data']))
            LOGGER.debug((str(payload), mode, str(r)))
        elif s == 400 and r['result'] == 'BAD' and r['data'] is not None:
            PPOB_SIGNDLER.SIGNAL_CHECK_CUSTOMER.emit('CHECK_CUSTOMER|' + json.dumps(r['data']))
            LOGGER.debug((str(payload), mode, str(r)))
        else:
            PPOB_SIGNDLER.SIGNAL_CHECK_CUSTOMER.emit('CHECK_CUSTOMER|ERROR')
            LOGGER.warning((str(payload), mode, str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), mode, str(e)))
        PPOB_SIGNDLER.SIGNAL_CHECK_CUSTOMER.emit('CHECK_CUSTOMER|ERROR')


def start_check_detail_trx_status(payload, mode):
    _Helper.get_thread().apply_async(check_detail_trx_status, (payload, mode,))


def check_detail_trx_status(payload, mode='CASHIN OVO'):
    # msisdn,amount,reff_no,operator
    try:
        payload = json.loads(payload)
        # _Helper.dump(payload)
        url = _Common.BACKEND_URL+'ppob/trx-status'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK' and r['data'] is not None:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('CHECK_TRX_STATUS|' + json.dumps(r['data']))
            LOGGER.debug((str(payload), mode, str(r)))
        elif s == 400 and r['result'] == 'BAD' and r['data'] is not None:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('CHECK_TRX_STATUS|' + json.dumps(r['data']))
            LOGGER.debug((str(payload), mode, str(r)))
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('CHECK_TRX_STATUS|ERROR')
            LOGGER.warning((str(payload), mode, str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), mode, str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('CHECK_TRX_STATUS|ERROR')



def start_do_inquiry_promo(payload):
    _Helper.get_thread().apply_async(do_inquiry_promo, (payload,))


LAST_PROMO = []


def get_promo_data(trxid):
    if len(LAST_PROMO) == 0:
        return None
    for promo in LAST_PROMO:
        if promo['trx_id'] == trxid:
            return promo
    return None


def do_inquiry_promo(payload):
    global LAST_PROMO
    payload = json.loads(payload)
    try:
        url = _Common.BACKEND_URL+'promo/check'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload, custom_timeout=5)
        if s == 200 and r['result'] == 'OK':
            data = r['data']
            if int(data.get('receive_discount', 0)) > 0:
                data['trx_id'] = str(data.get('shop_type')) + str(data.get('epoch'))
                LAST_PROMO.append(data)
                PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PROMO_INQUIRY|AVAILABLE|'+json.dumps(data))
            else:
                PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PROMO_INQUIRY|NOT_FOUND|'+json.dumps(data))
        else:
            PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PROMO_INQUIRY|ERROR|'+json.dumps(payload))
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(e)))
        PPOB_SIGNDLER.SIGNAL_TRX_CHECK.emit('PROMO_INQUIRY|ERROR|'+json.dumps(payload))
        


def start_do_confirm_promo(payload):
    _Helper.get_thread().apply_async(do_confirm_promo, (payload,))


def do_confirm_promo(payload):
    payload = json.loads(payload)
    try:
        url = _Common.BACKEND_URL+'promo/use'
        s, r = _HTTPAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK':
            LOGGER.info((str(payload), str(r)))
        else:
            LOGGER.warning((str(payload), str(r)))
            payload['endpoint'] = 'promo/use'
            _Common.store_request_to_job(name=_Helper.whoami(), url=url, payload=payload)
    except Exception as e:
        LOGGER.warning((str(e)))
