__author__ = "wahyudi@multidaya.id"

import logging
from time import sleep
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _Common
from _dDAO import _DAO
from _tTools import _Helper
from _nNetwork import _NetworkAccess
from _sService import _UserService
from _sService import _KioskService
import json
from operator import itemgetter



class ProductSignalHandler(QObject):
    __qualname__ = 'ProductSignalHandler'
    SIGNAL_CHANGE_STOCK = pyqtSignal(str)
    SIGNAL_CHECK_VOUCHER = pyqtSignal(str)
    SIGNAL_USE_VOUCHER = pyqtSignal(str)


PR_SIGNDLER = ProductSignalHandler()
LOGGER = logging.getLogger()
BACKEND_URL = _Common.BACKEND_URL


def start_change_product_stock(payload):
    _Helper.get_thread().apply_async(change_product_stock, (payload,))


CARD_STOCK_UPDATE = []


def change_product_stock(payload):
    global CARD_STOCK_UPDATE
    if not _Helper.is_online('change_product_stock'):
        PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT|CONNECTION_ERROR')
        return
    try:
        payload = json.loads(payload)    
        #Add Handle Limit Update Stock Duration From Previous
        last_port_update_time = _Common.load_from_temp_config('last^slot^'+payload['port'].replace('10', '')+'^update^time', '0')
        if int(last_port_update_time) > 0 and _Common.LIMIT_CARD_OPNAME_DURATION_HOURS > 0:
            allowed_update_port_time = int(last_port_update_time) + (_Common.LIMIT_CARD_OPNAME_DURATION_HOURS * 3600 * 1000)
            if _Helper.now() < allowed_update_port_time:
                PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT|UPDATE_STOCK_DURATION_LIMIT|'+str(_Common.LIMIT_CARD_OPNAME_DURATION_HOURS))
                return
        # // {
        # //  port: selectedSlot,
        # //  init_stock: initStockInput,
        # //  add_stock: addStockInput,
        # //  last_stock: parseInt(initStockInput) + parseInt(addStockInput),
        # //  type: 'changeStock'
        # // }
        check_product = _DAO.custom_query(' SELECT * FROM ProductStock WHERE status='+payload['port']+' ')
        if len(check_product) == 0:
            PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT|STID_NOT_FOUND')
            return
        payload['stock'] = str(payload['last_stock'])
        operator = 'OPERATOR'
        if _UserService.USER is not None:
            operator = _UserService.USER['first_name']
        _stid = check_product[0]['stid']
        if _stid not in CARD_STOCK_UPDATE:
            CARD_STOCK_UPDATE.append(_stid)
        _param = {
            'port': payload['port'],
            'stock': payload['stock'],
            'stid': _stid,
            'user': operator
        }
        # Record Local Change
        _Common.LAST_UPDATED_STOCK.append(check_product[0])
        # Log Change To Local
        _DAO.custom_update(' UPDATE ProductStock SET stock=' + payload['stock'] + ' WHERE stid="'+_stid+'" ')
        _Common.log_to_temp_config('last^stock^slot^'+payload['port'].replace('10', ''), payload['stock'])
        _Common.log_to_temp_config('last^add^stock^slot^'+payload['port'].replace('10', ''), payload['add_stock'])
        _Common.log_to_temp_config('last^stock^opname^slot^'+payload['port'].replace('10', ''), payload['init_stock'])
        # Send Signal Into View&&
        _KioskService.kiosk_get_product_stock()
        # Change Stock Updation To Backend
        status, response = _NetworkAccess.post_to_url(url=BACKEND_URL + 'change/product-stock', param=_param)
        # LOGGER.info((str(_param), str(response)))
        if status == 200 and response['result'] == 'OK':
            _Common.log_to_temp_config('last^slot^'+payload['port'].replace('10', '')+'^update^time', str(_Helper.now()))
            # _KioskService.kiosk_get_product_stock()
            PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT_STOCK|SUCCESS|'+json.dumps(_param))
            len_product = int(_DAO.custom_query(' SELECT count(*) AS __ FROM ProductStock WHERE stid IS NOT NULL ')[0]['__'])
            if len_product == len(CARD_STOCK_UPDATE):
                sleep(1)
                PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT_STOCK|COMPLETE')
                CARD_STOCK_UPDATE = []
        else:
            PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT_STOCK|ERROR')
    except Exception as e:
        LOGGER.warning(('change_product_stock', e))
        PR_SIGNDLER.SIGNAL_CHANGE_STOCK.emit('CHANGE_PRODUCT_STOCK|ERROR')


def kiosk_get_product_stock():
    _url = BACKEND_URL + 'get/product-stock'
    if _Helper.is_online(source='start_get_product_stock') is True:
        s, r = _NetworkAccess.get_from_url(url=_url)
        if s == 200 and r['result'] == 'OK':
            products = r['data']
            products = sorted(products, key=itemgetter('status'))
            _DAO.flush_table('ProductStock')
            for product in products:
                _DAO.insert_product_stock(product)
            _KioskService.get_product_stock()


def start_check_voucher(voucher):
    _Helper.get_thread().apply_async(check_voucher, (voucher,))


def check_voucher(voucher):
    if _Common.empty(voucher):
        LOGGER.warning((str(voucher), 'MISSING_VOUCHER_NUMBER'))
        PR_SIGNDLER.SIGNAL_CHECK_VOUCHER.emit('CHECK_VOUCHER|MISSING_VOUCHER_NUMBER')
        return
    payload = {
        'vcode': voucher
    }
    try:
        url = _Common.BACKEND_URL+'ppob/voucher/check'
        s, r = _NetworkAccess.post_to_url(url=url, param=payload)
        if s == 200 and r['result'] == 'OK' and r['data']['Response'] == '0':
            product_id = r['data']['product']
            check_product = _DAO.check_product_status_by_pid({'pid': product_id})
            if len(check_product) > 0:
                output = {
                    'voucher': voucher,
                    'mode': 'card_collection',
                    'product': product_id,
                    'qty': r['data']['qty_available'],
                    'voucher_details': r['data'],
                    'card': check_product[0],
                    'slot': check_product[0]['status']
                }
                PR_SIGNDLER.SIGNAL_CHECK_VOUCHER.emit('CHECK_VOUCHER|' + json.dumps(output))
            else:
                PR_SIGNDLER.SIGNAL_CHECK_VOUCHER.emit('CHECK_VOUCHER|EMPTY')
        else:
            PR_SIGNDLER.SIGNAL_CHECK_VOUCHER.emit('CHECK_VOUCHER|ERROR')
        LOGGER.debug((str(payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(payload), str(e)))
        PR_SIGNDLER.SIGNAL_CHECK_VOUCHER.emit('CHECK_VOUCHER|ERROR')


def start_use_voucher(voucher, reff_no):
    _Helper.get_thread().apply_async(use_voucher, (voucher, reff_no,))


def use_voucher(voucher, reff_no):
    if _Common.empty(voucher):
        LOGGER.warning((str(voucher), 'MISSING_VOUCHER_NUMBER'))
        PR_SIGNDLER.SIGNAL_USE_VOUCHER.emit('USE_VOUCHER|MISSING_VOUCHER_NUMBER')
        return
    if _Common.empty(reff_no):
        LOGGER.warning((str(reff_no), 'MISSING_REFF_NO'))
        PR_SIGNDLER.SIGNAL_USE_VOUCHER.emit('USE_VOUCHER|MISSING_REFF_NO')
        return
    product_id = reff_no.split('-')[1]
    __payload = {
            'vcode': voucher,
            'note_ref': reff_no,
            'pid': product_id,
        }
    product_stock = _DAO.check_product_status_by_pid({'pid': product_id})
    # Use Direct Deduct On CD Module - 2022-08-04
    if len(product_stock) > 0:
        __payload['last_stock'] = product_stock[0]['stock']
        __payload['slot'] = product_stock[0]['status']
        _Common.store_redeem_activity(voucher, str(__payload['slot']))
    try:
        __url = _Common.BACKEND_URL+'ppob/voucher/use'
        s, r = _NetworkAccess.post_to_url(url=__url, param=__payload)
        if s == 200 and r['result'] == 'OK' and r['data'] is not None:
            PR_SIGNDLER.SIGNAL_USE_VOUCHER.emit('USE_VOUCHER|' + json.dumps(r['data']))
        else:
            # Add Retry Send If Got Issue When Sending Voucher Usage
            _Common.store_request_to_job(name=_Helper.whoami(), url=__url, payload=__payload)
            PR_SIGNDLER.SIGNAL_USE_VOUCHER.emit('USE_VOUCHER|PENDING')
        LOGGER.debug((str(__payload), str(r)))
    except Exception as e:
        LOGGER.warning((str(__payload), str(e)))
        PR_SIGNDLER.SIGNAL_USE_VOUCHER.emit('USE_VOUCHER|ERROR')
