__author__ = "wahyudi@multidaya.id"

import json
import logging
import os
import datetime
import time
import random
import sys
import shutil
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _ConfigParser, _Common
from _dDAO import _DAO
from _tTools import _Helper
from _nNetwork import _HTTPAccess
from pprint import pprint
from _sService import _UserService, _MDSService
from time import sleep
import subprocess
from operator import itemgetter
import json
# import win32serviceutil
if _Common.IS_WINDOWS:
    import wmi
    import win32com.client as client
    import pythoncom
    import win32print


class KioskSignalHandler(QObject):
    __qualname__ = 'KioskSignalHandler'
    SIGNAL_GET_GUI_VERSION = pyqtSignal(str)
    SIGNAL_GET_KIOSK_NAME = pyqtSignal(str)
    SIGNAL_GET_FILE_LIST = pyqtSignal(str)
    SIGNAL_GET_PAYMENTS = pyqtSignal(str)
    SIGNAL_GET_REFUNDS = pyqtSignal(str)
    SIGNAL_GENERAL = pyqtSignal(str)
    SIGNAL_GET_KIOSK_STATUS = pyqtSignal(str)
    SIGNAL_PRICE_SETTING = pyqtSignal(str)
    SIGNAL_LIST_CASH = pyqtSignal(str)
    SIGNAL_COLLECT_CASH = pyqtSignal(str)
    SIGNAL_BOOKING_SEARCH = pyqtSignal(str)
    SIGNAL_RECREATE_PAYMENT = pyqtSignal(str)
    SIGNAL_ADMIN_KEY = pyqtSignal(str)
    SIGNAL_WALLET_CHECK = pyqtSignal(str)
    SIGNAL_GET_PRODUCT_STOCK = pyqtSignal(str)
    SIGNAL_STORE_TRANSACTION = pyqtSignal(str)
    SIGNAL_GET_TOPUP_AMOUNT = pyqtSignal(str)
    SIGNAL_STORE_TOPUP = pyqtSignal(str)
    SIGNAL_GET_MACHINE_SUMMARY = pyqtSignal(str)
    SIGNAL_GET_PAYMENT_SETTING = pyqtSignal(str)
    SIGNAL_SYNC_ADS_CONTENT = pyqtSignal(str)
    SIGNAL_ADMIN_GET_PRODUCT_STOCK = pyqtSignal(str)
    SIGNAL_PANEL_SETTING = pyqtSignal(str)
    SIGNAL_LOGOUT_OPERATOR = pyqtSignal(str)


K_SIGNDLER = KioskSignalHandler()
LOGGER = logging.getLogger()


def start_use_pending_code(pending_code, reff_no):
    _Helper.get_thread().apply_async(use_pending_code, (pending_code, reff_no,))


# def load_from_temp_config(section='test^section', default=''):
#     return _ConfigParser.get_set_value('TEMPORARY', section, default)

# def log_to_config(option='TEMPORARY', section='last^auth', content=''):
#     content = str(content)
#     _ConfigParser.set_value(option, section, content)


def use_pending_code(pending_code, reff_no):
    usage_attempt = int(_Common.load_from_temp_config(section=pending_code, default='0'))
    usage_attempt += 1
    # Update Usage To Local
    _Common.log_to_config(option='TEMPORARY', section=pending_code, content=str(usage_attempt))
    # Send Update Usage To Server
    _Common.update_usage_retry_code(reff_no)


def get_kiosk_status():
    _Helper.get_thread().apply_async(kiosk_status)


def kiosk_status():
    data = _Common.kiosk_status_data()
    K_SIGNDLER.SIGNAL_GET_KIOSK_STATUS.emit(json.dumps(data))
    sleep(1)
    # Send Card Stock Within Kiosk Status
    get_product_stock()


def load_from_temp_data(section, selected_mode):
    return _Common.load_from_temp_data(temp=section, mode=selected_mode)


def load_previous_kiosk_status():
    try:
        _Common.KIOSK_SETTING = _DAO.init_kiosk()[0]
        _Common.KIOSK_ADMIN = int(_Common.KIOSK_SETTING['defaultAdmin'])
        _Common.KIOSK_MARGIN = int(_Common.KIOSK_SETTING['defaultMargin'])
        _Common.KIOSK_NAME = _Common.KIOSK_SETTING['name']
        _Common.TOPUP_AMOUNT_SETTING = load_from_temp_data('topup-amount-setting', 'json')
        _Common.FEATURE_SETTING = load_from_temp_data('feature-setting', 'json')
        _Common.PAYMENT_SETTING = load_from_temp_data('payment-setting', 'json')
        _Common.REFUND_SETTING = load_from_temp_data('refund-setting', 'json')
        _Common.THEME_SETTING = load_from_temp_data('theme-setting', 'json')
        _Common.ADS_SETTING = load_from_temp_data('ads-setting', 'json')
        _Common.KIOSK_STATUS = 'OFFLINE'
        LOGGER.info(('LOAD_PREVIOUS_SETTING_VALUE'))
    except Exception as e:
        LOGGER.warning(('DATABASE CORRUPT', e))
        print('pyt: DATABASE CORRUPT', str(e))
        sys.exit(99)


def update_kiosk_status(s=400, r=None):
    try:
        if s == 200 and r['result'] == 'OK':
            if 'data' in r.keys() and not _Common.empty(r['data']):
                _Common.KIOSK_SETTING = r['data']['kiosk']
                _Common.KIOSK_NAME = _Common.KIOSK_SETTING['name']
                _Common.KIOSK_MARGIN = int(_Common.KIOSK_SETTING['defaultMargin'])
                _Common.KIOSK_ADMIN = int(_Common.KIOSK_SETTING['defaultAdmin'])
                _Common.PAYMENT_SETTING = r['data']['payment']
                if _Common.IS_WINDOWS:
                    print("pyt: Syncing Payment Setting...")
                    define_device_port_setting(_Common.PAYMENT_SETTING)
                _Common.store_to_temp_data('payment-setting', json.dumps(r['data']['payment']))
                _Common.FEATURE_SETTING = r['data']['feature']
                print("pyt: Syncing Feature Setting...")
                define_feature(_Common.FEATURE_SETTING)
                _Common.THEME_SETTING = r['data']['theme']
                print("pyt: Syncing Theme Setting...")
                build_view_config(_Common.THEME_SETTING)
                _Common.ADS_SETTING = r['data']['ads']
                _Common.store_to_temp_data('ads-setting', json.dumps(r['data']['ads']))
                if 'refund' in r['data'].keys():
                    print("pyt: Syncing Refund Setting...")
                    _Common.REFUND_SETTING = r['data']['refund']
                    _Common.store_to_temp_data('refund-setting', json.dumps(r['data']['refund']))
                _Common.KIOSK_STATUS = 'ONLINE'
                print("pyt: Syncing Kiosk Information...")
                # _DAO.flush_table('Terminal', 'tid <> "'+_Common.KIOSK_SETTING['tid']+'"')
                _DAO.update_kiosk_data(_Common.KIOSK_SETTING)
                LOGGER.info(('UPDATE_KIOSK_DATA', 'SUCCESS'))
                return
        load_previous_kiosk_status()
    except Exception as e:
        LOGGER.warning((e))
        # load_previous_kiosk_status() 
    # finally:
    #     sleep(10)
    #     kiosk_status()
    #     pprint(_Common.KIOSK_SETTING)


def define_feature(d):
    _Common.store_to_temp_data('feature-setting', json.dumps(d))
    if 'multiple_card_shop' in d.keys():
        _ConfigParser.set_value('CD', 'multiple^eject', str(d['multiple_card_shop']))
    if 'search_trx' in d.keys():
        _Common.log_to_temp_config('search^trx', str(d['search_trx']))
    if 'whatsapp_voucher' in d.keys():
        _Common.log_to_temp_config('wa^voucher', str(d['whatsapp_voucher']))
    for k in d.keys():
        if 'ubal_online' in k:
            _Common.log_to_temp_config(k.replace('_', '^'), '0')
            if not _Helper.empty(_Common.ALLOWED_BANK_UBAL_ONLINE):
                _Common.ALLOWED_BANK_UBAL_ONLINE = []
    if 'ubal_online_mandiri' in d.keys() and d['ubal_online_mandiri'] == 1:
        _Common.log_to_temp_config('ubal^online^mandiri', '1')
        _Common.ALLOWED_BANK_UBAL_ONLINE.append('MANDIRI')
    if 'ubal_online_bni' in d.keys() and d['ubal_online_bni'] == 1:
        _Common.log_to_temp_config('ubal^online^bni', '1')
        _Common.ALLOWED_BANK_UBAL_ONLINE.append('BNI')
    if 'ubal_online_bri' in d.keys() and d['ubal_online_bri'] == 1:
        _Common.log_to_temp_config('ubal^online^bri', '1')
        _Common.ALLOWED_BANK_UBAL_ONLINE.append('BRI')
    if 'ubal_online_bca' in d.keys() and d['ubal_online_bca'] == 1:
        _Common.log_to_temp_config('ubal^online^bca', '1')
        _Common.ALLOWED_BANK_UBAL_ONLINE.append('BCA')
    if 'ubal_online_dki' in d.keys() and d['ubal_online_dki'] == 1:
        _Common.log_to_temp_config('ubal^online^dki', '1')
        _Common.ALLOWED_BANK_UBAL_ONLINE.append('DKI')
    _ConfigParser.set_value('GENERAL', 'allowed^ubal^online', '|'.join(_Common.ALLOWED_BANK_UBAL_ONLINE))


def define_device_port_setting(data):
    '''
    [
        {"description": "CASH", "config": "COM2", "payment_method_id": 1, "status": "1", "name": "cash", "tid": "110322"}, 
        {"description": "CARD", "config": "COM3", "payment_method_id": 2, "status": "1", "name": "card", "tid": "110322"}, 
        {"description": "QR OVO", "config": "COM4", "payment_method_id": 4, "status": "1", "name": "ovo", "tid": "110322"}, 
        {"description": "QR LINKAJA", "config": "COM5", "payment_method_id": 7, "status": "1", "name": "linkaja", "tid": "110322"}
        ]
    ''' 
    if _Common.empty(data) is True:
        LOGGER.warning(('EMPTY_DATA_PAYMENT'))
        return
    for c in data: # QR No Need To Store in setting file
        if c['name'] == 'cash':
            _ConfigParser.set_value('BILL', 'port', c['config'])
            _Common.BILL_PORT = c['config']
        if c['name'] == 'card':
            _ConfigParser.set_value('EDC', 'port', c['config'])
            _Common.EDC_PORT = c['config']
        if c['name'] == 'prepaid':
            _ConfigParser.set_value('QPROX_NFC', 'port', c['config'])
            _Common.QPROX_PORT = c['config']


def build_view_config(d):
    _Common.store_to_temp_data('theme-setting', json.dumps(d))
    _Common.THEME_NAME = d['name']
    _Common.log_to_temp_config('theme^name', d['name'])
    
    # Additional Theme Setting
    _Common.MAX_PENDING_CODE_DURATION = d.get('max_pending_code_duration', _Common.MAX_PENDING_CODE_DURATION)
    _Common.log_to_temp_config('max^pending^code^duration', str(d['max_pending_code_duration']))
    _Common.MAX_PENDING_CODE_RETRY = d.get('max_pending_code_retry', _Common.MAX_PENDING_CODE_RETRY)
    _Common.log_to_temp_config('max^pending^code^retry', str(d['max_pending_code_retry']))
    _Common.CUSTOMER_SERVICE_NO = d.get('customer_service_no', _Common.CUSTOMER_SERVICE_NO)
    _Common.log_to_temp_config('customer^service^no', str(d['customer_service_no']))
    # ===

    _Common.VIEW_CONFIG['all_qr_provider'] = [x.lower() for x in _Common.ALL_QR_PROVIDER]
    _Common.VIEW_CONFIG['topup_status'] = d['name'].upper() in _Common.THEME_WITH_TOPUP_STATUS

    config_js = sys.path[0] + '/'+_Common.VIEW_FOLDER+'/config.js'
    content_js = ''
    # Mandiri Update Schedule Time For Timer Trigger
    daily_settle_time = _ConfigParser.get_set_value('MANDIRI', 'daily^settle^time', '02:00')
    content_js += 'var mandiri_update_schedule = "' + daily_settle_time + '";' + os.linesep
    _Common.VIEW_CONFIG['mandiri_update_schedule'] = daily_settle_time
    edc_daily_settle_time = _ConfigParser.get_set_value('EDC', 'daily^settle^time', '23:00')
    content_js += 'var edc_settlement_schedule = "' + edc_daily_settle_time + '";' + os.linesep
    _Common.VIEW_CONFIG['edc_settlement_schedule'] = edc_daily_settle_time

    # Temp Config For Ubal Online
    content_js += 'var bank_ubal_online = ' + json.dumps(_Common.ALLOWED_BANK_UBAL_ONLINE) + ';' + os.linesep
    _Common.VIEW_CONFIG['bank_ubal_online'] = _Common.ALLOWED_BANK_UBAL_ONLINE

    if type(d['master_logo']) != list:
        d['master_logo'] = [d['master_logo']]

    master_logo = []
    for m in d['master_logo']:
        download, image = _HTTPAccess.item_download(m, os.getcwd() + '/'+_Common.VIEW_FOLDER+'/source/logo')
        if download is True or _Common.USE_PREV_THEME:
            master_logo.append(image)
        else:
            continue
    content_js += 'var master_logo = ' + json.dumps(master_logo) + ';' + os.linesep
    _Common.VIEW_CONFIG['master_logo'] = master_logo

    partner_logos = []
    for p in d['partner_logos']:
        download, image = _HTTPAccess.item_download(p, os.getcwd() + '/'+_Common.VIEW_FOLDER+'/source/logo')
        if download is True or _Common.USE_PREV_THEME:
            partner_logos.append(image)
        else:
            continue
    content_js += 'var partner_logos = ' + json.dumps(partner_logos) + ';' + os.linesep
    _Common.VIEW_CONFIG['partner_logos'] = partner_logos

    backgrounds = []
    for b in d['backgrounds']:
        download, image = _HTTPAccess.item_download(b, os.getcwd() + '/'+_Common.VIEW_FOLDER+'/source/background')
        if download is True or _Common.USE_PREV_THEME:
            backgrounds.append(image)
        else:
            continue
    content_js += 'var backgrounds = ' + json.dumps(backgrounds) + ';' + os.linesep
    _Common.VIEW_CONFIG['backgrounds'] = backgrounds

    # Running Text
    if not _Common.empty(d['running_text']):
        content_js += 'var running_text = "' + d['running_text'] + '";' + os.linesep
        _Common.VIEW_CONFIG['running_text'] = d['running_text']

    # Running Text Color
    if not _Common.empty(d['running_text_color']):
        content_js += 'var running_text_color = "' + d['running_text_color'] + '";' + os.linesep
        _Common.VIEW_CONFIG['running_text_color'] = d['running_text_color']
        content_js += 'var text_color = "' + _Common.COLOR_TEXT + '";' + os.linesep
        _Common.VIEW_CONFIG['text_color'] = _Common.COLOR_TEXT
        content_js += 'var frame_color = "' + d['frame_color'] + '";' + os.linesep
        _Common.VIEW_CONFIG['frame_color'] = d['frame_color']
        content_js += 'var background_color = "' +  _Common.COLOR_BACK + '";' + os.linesep
        _Common.VIEW_CONFIG['background_color'] = _Common.COLOR_BACK

    if not _Common.empty(d['whatsapp_no']):
        _Common.THEME_WA_NO = d['whatsapp_no']
        _Common.log_to_temp_config('theme^wa^no', d['whatsapp_no'])
        content_js += 'var whatsapp_no = "' +  d['whatsapp_no'] + '";' + os.linesep
        _Common.VIEW_CONFIG['whatsapp_no'] = d['whatsapp_no']

    if not _Common.empty(d['whatsapp_qr']):
        _Common.THEME_WA_QR = d['whatsapp_qr']
        _Common.log_to_temp_config('theme^wa^qr', d['whatsapp_qr'])
        store, receipt_wa_qr = _HTTPAccess.item_download(d['whatsapp_qr'], os.getcwd() + '/'+_Common.VIEW_FOLDER+'/source')
        if store is True:
            content_js += 'var whatsapp_qr = "source/' + receipt_wa_qr + '";' + os.linesep
            _Common.VIEW_CONFIG['whatsapp_qr'] = "source/" + receipt_wa_qr
    # Add Printer Type
    printer_type = _Common.PRINTER_TYPE.lower()
    content_js += 'var printer_type = "' +  printer_type + '";' + os.linesep
    _Common.VIEW_CONFIG['printer_type'] = printer_type
    # Add Printer Manual Delay Show
    printer_manual_delay = str(_Common.DELAY_MANUAL_PRINT)
    content_js += 'var delay_manual_print = ' +  printer_manual_delay + ';' + os.linesep
    _Common.VIEW_CONFIG['delay_manual_print'] = printer_manual_delay
    # C2C Mode View config
    c2c_mode = '1' if _Common.C2C_MODE is True else '0'
    content_js += 'var c2c_mode = ' +  c2c_mode + ';' + os.linesep
    _Common.VIEW_CONFIG['c2c_mode'] = c2c_mode
    # General QR config
    general_qr = '1' if _Common.GENERAL_QR is True else '0'
    content_js += 'var general_qr = ' +  general_qr + ';' + os.linesep
    _Common.VIEW_CONFIG['general_qr'] = general_qr

    # Over night
    content_js += 'var over_night = ' +  str(_Common.OVER_NIGHT) + ';' + os.linesep
    _Common.VIEW_CONFIG['over_night'] = str(_Common.OVER_NIGHT)

    # Receipt tvc_waiting_time ()default 60 sec)
    content_js += 'var tvc_waiting_time = ' +  str(60) + ';' + os.linesep
    if not _Common.empty(d['tvc_waiting_time']):
        _Common.log_to_temp_config('tvc^waiting^time', str(d['tvc_waiting_time']))
        content_js += 'tvc_waiting_time = ' +  str(d['tvc_waiting_time']) + ';' + os.linesep
        _Common.VIEW_CONFIG['tvc_waiting_time'] = str(d['tvc_waiting_time'])

    if not _Common.empty(_Common.EDC_MOBILE_DURATION):
        content_js += 'var edc_waiting_time = "' +  str(_Common.EDC_MOBILE_DURATION) + '";' + os.linesep
        _Common.VIEW_CONFIG['edc_waiting_time'] = str(_Common.EDC_MOBILE_DURATION)

    # Receipt Logo
    if not _Common.empty(d['receipt_custom_text']):
        _Common.CUSTOM_RECEIPT_TEXT = d['receipt_custom_text'].replace(os.linesep, '|')
        _Common.log_to_config('PRINTER', 'receipt^custom^text', d['receipt_custom_text'])
    store, receipt_logo = _HTTPAccess.item_download(d['receipt_logo'], os.getcwd() + '/_rReceipts')
    if store is True:
        _Common.RECEIPT_LOGO = receipt_logo
        _Common.log_to_config('PRINTER', 'receipt^logo', receipt_logo)
    
    # with open(config_js, 'w+') as config_qml:
    #     config_qml.write(content_js)
    #     config_qml.close()

    _Common.store_to_temp_data('view-config', json.dumps(_Common.VIEW_CONFIG))
    LOGGER.info((config_js, content_js))


def start_define_ads(wait_for=5):
    sleep(wait_for)
    _Helper.get_thread().apply_async(define_ads, (_Common.ADS_SETTING, ))


def define_ads(a):
    if a is None or len(a) == 0:
        LOGGER.warning(("define_ads : ", 'Missing ADS_SETTING'))
        K_SIGNDLER.SIGNAL_SYNC_ADS_CONTENT.emit('SYNC_ADS|MISSING_ADS_SETTING')
        return False
    __metadata = a['metadata']
    __playlist = a['playlist']
    __tvc_path = sys.path[0] + '/_vVideo'
    __tvc_backup = sys.path[0] + '/_tTmp'
    if not os.path.exists(__tvc_path):
        os.makedirs(__tvc_path)
    __current_list = []
    __all_file = os.listdir(__tvc_path)
    for file in __all_file:
        extentions = ('.mp4', '.mov', '.avi', '.mpg', '.mpeg')
        if file.endswith(extentions):
            __current_list.append(file)
    __must_backup = list(set(__current_list) - set(__playlist))
    LOGGER.debug(("current list : ", str(__current_list)))
    LOGGER.debug(("new playlist : ", str(__playlist)))
    LOGGER.debug(("expired media(s) : ", str(__must_backup)))
    # __must_delete = __current_list
    # _Helper.dump(__must_delete)
    if len(__must_backup) > 0 and not _Common.USE_PREV_ADS:
        for d in __must_backup:
            file_expired = os.path.join(__tvc_path, d)
            file_backup = os.path.join(__tvc_backup, d)
            if os.path.exists(file_expired):
                LOGGER.debug(("backup expired media : ", file_expired))
                K_SIGNDLER.SIGNAL_SYNC_ADS_CONTENT.emit('SYNC_ADS|BACKUP_EXPIRED_'+d.upper())
                shutil.copy(file_expired, file_backup)
                os.remove(file_expired)
    __must_download = list(set(__playlist) - set(__current_list))
    while len(__must_download) > 0:
        for l in __must_download:
            media_link = get_metadata_link(l, __metadata)
            LOGGER.debug(("add new media : ", media_link))
            K_SIGNDLER.SIGNAL_SYNC_ADS_CONTENT.emit('SYNC_ADS|ADD_NEW_'+l.upper())
            if media_link is not False:
                stream, media = _HTTPAccess.stream_large_download(media_link, l, _Common.TEMP_FOLDER, __tvc_path)
                if stream is True:
                    LOGGER.debug(("success download new media : ", media))
                    __must_download.remove(l)
    K_SIGNDLER.SIGNAL_SYNC_ADS_CONTENT.emit('SYNC_ADS|SUCCESS')
    return True


def get_metadata_link(media, data):
    if len(data) == 0 or media is None:
        return False
    for x in range(len(data)):
        if media == data[x]['name']:
            return data[x]['path']
    return False


def start_get_price_setting():
    _Helper.get_thread().apply_async(kiosk_price_setting)


def kiosk_price_setting():
    admin_fee = _Common.KIOSK_ADMIN
    if _Common.C2C_MODE is True:
        admin_fee = _Common.C2C_ADMIN_FEE[0] #Assuming Index 0 as Default Fee
    K_SIGNDLER.SIGNAL_PRICE_SETTING.emit(json.dumps({
        'margin': _Common.KIOSK_MARGIN,
        'adminFee': admin_fee,
        'cancelAble': _Common.PAYMENT_CANCEL,
        'confirmAble': _Common.PAYMENT_CONFIRM
    }))


IS_DEV = _Common.TEST_MODE


def rename_file(filename, list_, x):
    for char in list_:
        filename = filename.replace(char, x)
    return filename


def force_rename(file1, file2):
    from shutil import move
    try:
        move(file1, file2)
        return True
    except Exception as e:
        LOGGER.warning((file1, file2, str(e)))
        return False


def get_gui_version():
    _Helper.get_thread().apply_async(gui_version)


def gui_version():
    K_SIGNDLER.SIGNAL_GET_GUI_VERSION.emit(_Common.VERSION)


def get_kiosk_name():
    _Helper.get_thread().apply_async(kiosk_name)


def kiosk_name():
    K_SIGNDLER.SIGNAL_GET_KIOSK_NAME.emit(_Common.KIOSK_NAME)


def update_machine_stat(_url):
    _param = machine_summary()
    LOGGER.info(( _url, str(_param)))
    s, r = _HTTPAccess.post_to_url(url=_url, param=_param)
    return True if s == 200 and r['result'] == 'OK' else False


ERROR_PRINTER = {
    16: 'OUT_OF_PAPER'
}

COMP = None
LAST_SYNC = 'OFFLINE'


def kiosk_get_machine_summary():
    _Helper.get_thread().apply_async(get_machine_summary)

# SELECT IFNULL(SUM(sale), 0) AS __ FROM Transactions WHERE isCollected = 0

def get_machine_summary():
    try:
        result = machine_summary()
        result['total_trx'] = _DAO.get_total_count('TransactionsNew')
        result['today_trx'] = _DAO.get_total_count('TransactionsNew',
                                                   ' strftime("%Y-%m-%d", datetime(createdAt/1000, "unixepoch")) = '
                                                   'date("now") ')
        result['cash_trx'] = _DAO.get_total_count('TransactionsNew', ' paymentType = "CASH" ')
        result['edc_trx'] = _DAO.get_total_count('TransactionsNew', ' paymentType = "DEBIT" ')
        result['edc_not_settle'] = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __ FROM Settlement '
                                                     'WHERE status="EDC|OPEN" ')[0]['__']
        # result['cash_available'] = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash '
        #                                              'WHERE collectedAt is null ')[0]['__']
        # result['all_cashbox'] = _DAO.cashbox_status()        
        result['all_cashbox'] = _Common.get_cash_activity()['total']
        result['cash_available'] = result['all_cashbox']

        # Add Denom Setting
        # result['first_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'first^denom', '10000')
        # result['second_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'second^denom', '20000')
        # result['third_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'third^denom', '50000')
        # result['fourth_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'fourth^denom', '100000')
        # result['fifth_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'fifth^denom', '150000')
        # result['sixth_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'sixth^denom', '200000')
        # result['seventh_denom'] = _ConfigParser.get_set_value('TEMPORARY', 'seventh^denom', '250000')
        # result['admin_fee'] = _Common.KIOSK_ADMIN
        # result['admin_include'] = _ConfigParser.get_set_value('TEMPORARY', 'admin^include', '1')
        # result['printer_setting'] = '1' if _ConfigParser.get_set_value('PRINTER', 'printer^type', 'Default') == 'Default' else '0'
        # result['mdr_treshold'] = _ConfigParser.get_set_value('MANDIRI_C2C', 'minimum^amount', '1000')
        # result['mdr_topup_amount'] = _ConfigParser.get_set_value('MANDIRI_C2C', 'amount^topup', '100000')
        # result['bni_treshold'] = _ConfigParser.get_set_value('BNI', 'amount^minimum', '50000')
        # result['bni_topup_amount'] = _ConfigParser.get_set_value('BNI', 'amount^topup', '500000')
        # if int(result['all_cashbox']) >= int(result['cash_available']):
        #     result['cash_available'] = result['all_cashbox']
        LOGGER.info(('SUCCESS', str(result)))
        K_SIGNDLER.SIGNAL_GET_MACHINE_SUMMARY.emit(json.dumps(result))
    except Exception as e:
        LOGGER.warning(('FAILED', str(e)))


def machine_summary():
    global COMP
    summary = {
        'c_space': '10000',
        'd_space': '10000',
        'ram_space': '2000',
        'cpu_temp': '33',
        'paper_printer': 'NORMAL',
        'gui_version': '1.0',
        'system_version': _Common.SYSTEM_VERSION,
        'on_usage': 'IDLE',
        'edc_error': _Common.EDC_ERROR,
        'nfc_error': _Common.NFC_ERROR,
        'mei_error': _Common.BILL_ERROR,
        'printer_error': _Common.PRINTER_ERROR,
        'scanner_error': _Common.SCANNER_ERROR,
        'webcam_error': _Common.WEBCAM_ERROR,
        'cd1_error': _Common.CD1_ERROR,
        'cd2_error': _Common.CD2_ERROR,
        'cd3_error': _Common.CD3_ERROR,
        'mandiri_wallet': str(_Common.MANDIRI_ACTIVE_WALLET),
        'bni_wallet': str(_Common.BNI_ACTIVE_WALLET),
        'bri_wallet': str(_Common.BRI_WALLET),
        'bca_wallet': str(_Common.BCA_WALLET),
        'dki_wallet': str(_Common.DKI_WALLET),
        'last_sync': str(LAST_SYNC),
        'online_status': str(_Common.KIOSK_STATUS),
        'mandiri_active': str(_Common.MANDIRI_ACTIVE),
        'bni_active': str(_Common.BNI_ACTIVE),
        'mandiri_sam_no': str(_Common.MANDIRI_SAM_NO_1),
        'bni_sam_no': str(_Common.BNI_SAM_1_NO),
        'service_ver': str(_Common.SERVICE_VERSION),
        'theme': str(_Common.THEME_NAME),
        'last_money_inserted': _ConfigParser.get_set_value('BILL', 'last^money^inserted', 'N/A'),
        'mandiri_sam_threshold': str(_Common.MANDIRI_THRESHOLD),
        'bni_sam_threshold': str(_Common.BNI_THRESHOLD),
        # 'current_cash': _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__'],
        'current_cash': _Common.get_cash_activity()['total']
        # 'bni_sam1_no': str(_Common.BNI_SAM_1_NO),
        # 'bni_sam2_no': str(_Common.BNI_SAM_2_NO),
    }
    try:
        summary['gui_version'] = _Common.VERSION
        summary['product_stock'] = _DAO.get_all_product_stock()
        if _Common.IS_WINDOWS:
            pythoncom.CoInitialize()
            COMP = wmi.WMI()
            summary["c_space"] = get_disk_space("C:")
            summary["d_space"] = get_disk_space("D:")
            summary["ram_space"] = get_ram_space()
            summary['paper_printer'] = get_printer_status_v2()
        else:
            # TODO: Add Handler if Linux
            pass
    except Exception as e:
        LOGGER.warning(('FAILED', str(e)))
    finally:
        return summary


def get_ram_space():
    try:
        ram_space = []
        for e in COMP.Win32_OperatingSystem():
            ram_space.append(int(e.FreePhysicalMemory.strip()) / 1024)
            return "%.2f" % ram_space[0]
    except Exception as e:
        LOGGER.warning(("FAILED", str(e)))
        return "%.2f" % -1


def get_disk_space(caption):
    try:
        d_space = []
        for d in COMP.Win32_LogicalDisk(Caption=caption):
            if d.FreeSpace is not None:
                d_space.append(int(d.FreeSpace.strip()) / 1024 / 1024)
                return "%.2f" % d_space[0]
            else:
                return "%.2f" % -1
    except Exception as e:
        LOGGER.warning(("FAILED", caption, str(e)))
        return "%.2f" % -1


def get_printer_status():
    try:
        printer = win32print.OpenPrinter(win32print.GetDefaultPrinter())
        printer_status = win32print.GetPrinter(printer)
        status = int(printer_status[18])
        # status = 16
        win32print.ClosePrinter(printer)
        if status == 0:
            return 'NORMAL'
        elif status == 16:
            return ERROR_PRINTER[status]
        else:
            return 'UNKNOWN_ERROR'
    except Exception as e:
        LOGGER.warning(("FAILED", str(e)))
        return 'NOT_DETECTED'


PRINTER_STATUS_CMD = os.path.join(sys.path[0], '_lLib', 'printer', 'printer.exe')


def get_printer_status_v2():
    try:
        command = PRINTER_STATUS_CMD + " status"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        output = output[0].split(";")
        response = json.loads(output[0])
        if response['Status'] == 0:
            if response['Online'] == 1:
                return 'NORMAL'
            else:
                return 'OFFLINE'
        else:
            return 'UNKNOWN_ERROR'
    except Exception as e:
        LOGGER.warning(("FAILED", str(e)))
        return 'UNKNOWN_ERROR'


def get_cpu_temp():
    variance = random.uniform(0.09, 1.09)
    common = 30
    try:
        pythoncom.CoInitialize()
        comp = wmi.WMI(namespace="root\wmi")
        cpu_temp = []
        for g in comp.MSAcpi_ThermalZoneTemperature():
            cpu_temp.append((int(g.CurrentTemperature) / 10) - 273.15 + variance)
            return "%.2f" % cpu_temp[0]
    except Exception as e:
        LOGGER.warning(("FAILED", str(e)))
        return "%.2f" % (common - variance)
    # return "%.2f" % (common - variance)


def execute_command(command):
    _Helper.execute_console(command)


def post_gui_version():
    _Helper.get_thread().apply_async(gui_info)


def gui_info():
    try:
        # NO-NEED Budled with Kiosk Status
        status, response = _HTTPAccess.post_to_url('box/guiInfo', {"gui_version": str(_Common.VERSION)})
        LOGGER.info(('SUCCESS', str(status), str(response)))
    except Exception as e:
        LOGGER.warning(('FAILED', str(e)))


def get_file_list(dir_):
    _Helper.get_thread().apply_async(file_list, (dir_,))


def file_list(dir_):
    if _Common.empty(dir_):
        LOGGER.warning((dir_, 'MISSING_DIRECTORY'))
        return
    ext_files = '.*'
    if "Video" in str(dir_):
        ext_files = ('.mp4', '.mov', '.avi', '.mpg', '.mpeg')
    elif "Image" in str(dir_):
        ext_files = ('.png', '.jpeg', '.jpg')
    elif "Music" in str(dir_):
        ext_files = ('.mp3', '.ogg', '.wav')
    _dir_ = dir_.replace(".", "")
    try:
        # //qml: Playing List (0) - file:///C:/MDD_KIOSK/_qQML/_vVideo/1. CEGAH COVID - 19 (RUBIK).mp4
        # new_path = 'file:///' + os.getcwd() + dir_
        files = {
            "result": [x for x in os.listdir(sys.path[0] + _dir_) if x.endswith(ext_files)],
            "dir": dir_
        }
        if "Video" in str(dir_):
            # files["old_result"] = files["result"]
            files["playlist"] = _Common.ADS_SETTING['playlist']
            files["count"] = len(files["result"])
        LOGGER.info((_dir_, str(files)))
        K_SIGNDLER.SIGNAL_GET_FILE_LIST.emit(json.dumps(files))
    except Exception as e:
        K_SIGNDLER.SIGNAL_GET_FILE_LIST.emit("ERROR")
        LOGGER.warning((_dir_, str(e)))


def post_tvc_list(list_):
    if list_ is None or list_ == "":
        return
    try:
        #NOTES: NO NEED, PLAYLIST FROM SERVER ALREADY
        status, response = _HTTPAccess.post_to_url('box/tvcList', {"tvclist": list_})
        LOGGER.info(('SUCCESS', response))
    except Exception as e:
        LOGGER.warning(("FAILED", str(e)))


def post_tvc_log(media):
    _Helper.get_thread().apply_async(update_tvc_log, (media,))


def update_tvc_log(media):
    # Function to update the media count locally and keep it for on hour
    if media not in _Common.ADS_SETTING['playlist']:
        LOGGER.debug((media, str(_Common.ADS_SETTING['playlist']), 'MEDIA_NOT_FOUND_IN_PLAYLIST'))
        return
    media_code = '___'+media.replace(' ', '^')
    # _Helper.dump(media_code)
    media_today_path = sys.path[0]+'/_tTmp/'+media_code+'/'+time.strftime("%Y-%m-%d")+'.count'
    # _Helper.dump(media_today_path)
    if not os.path.isdir(sys.path[0]+'/_tTmp/'+media_code):
        os.mkdir(sys.path[0]+'/_tTmp/'+media_code, 777)
    if not os.path.exists(media_today_path):
        count = 1
        with open(media_today_path, 'w+') as c:
            c.write(str(count))
            c.close()
    else:
        last_count = int(open(media_today_path, 'r').read().strip())
        count = last_count + 1
        with open(media_today_path, 'w') as c:
            c.write(str(count))
            c.close()
    last_update_media = int(_ConfigParser.get_set_value('TEMPORARY', media_code, '0'))
    if (last_update_media + (60 * 60 * 1000)) > _Helper.now():
        LOGGER.debug((media, str(count), str(last_update_media), 'SKIP_NEXT_LOOP'))
        return
    else:
        send_tvc_log(media, count, media_code)


def send_tvc_log(media, count, media_code=None):
    if _Common.empty(media):
        LOGGER.warning((media, str(count), 'MISSING_MEDIA_NAME'))
        return
    if _Common.empty(count):
        LOGGER.warning((media, str(count), 'MISSING_MEDIA_COUNT'))
        return
    if media_code is None or media_code[:3] != '___':
        # media_code = media.replace(' ', '^')
        media_code = '___'+media.replace(' ', '^')
    param = {
        "media": media,
        "count": str(count),
        "date": time.strftime("%Y-%m-%d")
    }
    try:
        status, response = _HTTPAccess.post_to_url(_Common.BACKEND_URL+'count/ads', param)
        _Common.log_to_temp_config(media_code, str(_Helper.now()))
        # Not Handling Response Result
        LOGGER.info((media, str(count), status, response))
    except Exception as e:
        LOGGER.warning((media, str(count), str(e)))


def start_get_payments():
    _Helper.get_thread().apply_async(get_payments)


def get_payments():
    K_SIGNDLER.SIGNAL_GET_PAYMENTS.emit(json.dumps(_Common.get_payments()))


def start_get_refunds():
    _Helper.get_thread().apply_async(get_refunds)


def get_refunds():
    if not _Common.REFUND_FEATURE:
        K_SIGNDLER.SIGNAL_GET_REFUNDS.emit('REFUND_DISABLED')
    else:
        K_SIGNDLER.SIGNAL_GET_REFUNDS.emit(json.dumps(_Common.get_refunds()))


FIRST_RUN_FLAG = True


def start_restart_mdd_service():
    global FIRST_RUN_FLAG
    if FIRST_RUN_FLAG is True:
        _Helper.get_thread().apply_async(restart_mdd_service)
        FIRST_RUN_FLAG = False


def restart_mdd_service():
    # os.system('powershell restart-service MDDTopUpService -force')
    # try:
    #     win32serviceutil.RestartService('MDDTopUpService')
    #     return True
    # except Exception as e:
    #     LOGGER.warning((e))
    #     return False
    try:
        # pythoncom.CoInitialize()
        # shell = client.Dispatch("WScript.shell")
        # service_name = 'MDDTopUpService'
        # service_path = '\\'+os.environ['COMPUTERNAME']+'\/'+service_name
        # user = os.getlogin()
        # user_domain = os.environ['USERDOMAIN']
        # commander = os.getcwd() + '/subinacl.exe'
        # argument = 'subinacl.exe  /SERVICE '+service_path+' /GRANT='+user_domain+'\/'+user+'=F'
        # if os.path.exists(commander):
        #     print('pyt: Sending : ', argument)
        #     result = shell.Run(argument)
        #     print('pyt: Result : ', result)
        # command = 'runas /user:administrator powershell -command "Restart-Service MDDTopUpService -Force"'
        # os.system("net stop MDDTopUpService") 
        # sleep(1)
        # os.system("net start MDDTopUpService") 
        # shell.Run(command)
        # shell.SendKeys(admin_pass+"\r\n", 0)
        # script = '/_restartMDDTopupService.bat'
        # process = subprocess.run(sys.path[0] + script, shell=True, stdout=subprocess.PIPE)
        # output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        # LOGGER.info((output))
        # print("pyt: Restarting MDDTopUpService...Success")
        return True
    except Exception as e:
        LOGGER.warning((e))
        print("pyt: Restarting MDDTopUpService...Failed")
        return False
    # LOGGER.info(('[INFO] restart_mdd_service result : ', str(output)))
    # print("pyt : ", output)


def start_get_cash_data():
    _Helper.get_thread().apply_async(list_uncollected_cash)


def list_uncollected_cash():
    list_cash = _DAO.list_uncollected_cash()
    if len(list_cash) == 0:
        K_SIGNDLER.SIGNAL_LIST_CASH.emit('ZERO')
        return
    response = {
        'total': len(list_cash),
        'data': list_cash
    }
    K_SIGNDLER.SIGNAL_LIST_CASH.emit(json.dumps(response))
    LOGGER.info(('SUCCESS', json.dumps(response)))


def start_begin_collect_cash():
    _Helper.get_thread().apply_async(begin_collect_cash)


def begin_collect_cash():
    # Add BILL Device Reset Function
    # if _Common.BILL['status'] is True:
    #     LOGGER.info(('begin_collect_cash', 'call init_bill'))
    #     _BILL.init_bill()
    if not _Helper.is_online('begin_collect_cash'):
        K_SIGNDLER.SIGNAL_COLLECT_CASH.emit('COLLECT_CASH|CONNECTION_ERROR')
        return
    # count_uncollected_cash = _DAO.custom_query(' SELECT IFNULL(count(*), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__']
    count_uncollected_cash = _Common.get_cash_activity()['total']
    if count_uncollected_cash == 0:
        K_SIGNDLER.SIGNAL_COLLECT_CASH.emit('COLLECT_CASH|NOT_FOUND')
        return
    operator = 'OPERATOR'
    if _UserService.USER is not None:
        operator = _UserService.USER['first_name']
    _DAO.mark_uncollected_cash({
            'collectedAt': 19900901,
            'collectedUser': operator
    })
    # list_collect = _DAO.custom_query(" SELECT csid FROM Cash WHERE collectedAt = 19900901 AND collectedUser = '"+operator+"' ")
    # for cash in list_collect:
        # list_collect.append(cash['csid'])
    # Backend Updation Changed Indo Admin Access Report Endpoint
    # post_cash_collection(list_collect, _Helper.now())
    # Generate Admin Data Here
    collection_data = _Common.generate_collection_data()
    K_SIGNDLER.SIGNAL_COLLECT_CASH.emit('COLLECTION_DATA|'+json.dumps(collection_data))
    sleep(1)
    K_SIGNDLER.SIGNAL_COLLECT_CASH.emit('COLLECT_CASH|DONE')


def post_cash_collection(l, t):
    try:
        operator = 'OPERATOR'
        if _UserService.USER is not None:
            operator = _UserService.USER['first_name']
        param = {
            "csid": '|'.join(l),
            "user": operator,
            "updatedAt": t
        }
        status, response = _HTTPAccess.post_to_url(_Common.BACKEND_URL + 'collect/cash', param)
        if status == 200:
            LOGGER.info(("SUCCESS", response))
        else:
            # LOG REQUEST
            _Common.store_request_to_job(name=_Helper.whoami(), url=_Common.BACKEND_URL + 'collect/cash', payload=param)
    except Exception as e:
        LOGGER.warning(("FAILED", str(e)))


def start_adjust_table(p):
    _Helper.get_thread().apply_async(adjust_table, (p,))


def adjust_table(p, t='Receipts'):
    try:
        try:
            count_table = _DAO.check_table({'table': t})
            LOGGER.info(('Count Table ', t, str(count_table)))
        except Exception as e:
            LOGGER.info(('Table Not Found, ', e, 'Adjusting : ', p))
            _DAO.adjust_table(p)
    except Exception as e:
        LOGGER.warning(('FAILED', str(e), t))


def start_alter_table(a):
    _Helper.get_thread().apply_async(alter_table, (a,))


def alter_table(a):
    try:
        _DAO.adjust_table(a)
    except Exception as e:
        LOGGER.warning((e))
        # _Common.online_logger(['Data Alter', a], 'general')


def start_direct_alter_table(s):
    _Helper.get_thread().apply_async(direct_alter_table, (s,))


def direct_alter_table(scripts):
    result = []
    if _Common.empty(scripts):
        LOGGER.warning(('EMPTY ADJUSTMENT SCRIPT'))
        return
    if type(scripts) == list and len(scripts) > 0:
        for script in scripts:
            result.append({'script': script, 'result': _DAO.direct_adjust_table(script=script)})
    else:
        result.append({'script': scripts, 'result': _DAO.direct_adjust_table(script=scripts)})
    LOGGER.info(('RESULT', str(result)))
    return result


TID = _Common.TID


def start_get_admin_key():
    _Helper.get_thread().apply_async(get_admin_key)


def get_admin_key():
    salt = datetime.datetime.now().strftime("%Y%m%d")
    K_SIGNDLER.SIGNAL_ADMIN_KEY.emit(_Common.TID+salt)


def start_check_wallet(amount):
    _Helper.get_thread().apply_async(check_wallet, (amount,))


def check_wallet(amount):
    try:
        param = {"amount": int(amount)}
        status, response = _HTTPAccess.post_to_url(_Common.BACKEND_URL + 'task/check-wallet', param)
        LOGGER.info((response))
        if status == 200 and response is not None:
            K_SIGNDLER.SIGNAL_WALLET_CHECK.emit(json.dumps(response))
        else:
            K_SIGNDLER.SIGNAL_WALLET_CHECK.emit('ERROR')
    except Exception as e:
        LOGGER.warning((e))
        K_SIGNDLER.SIGNAL_WALLET_CHECK.emit('ERROR')


def kiosk_get_product_stock():
    _Helper.get_thread().apply_async(get_product_stock, )


def get_product_stock():
    stock = []
    try:
        check_stock = _DAO.get_product_stock()
        check_stock = sorted(check_stock, key=itemgetter('status'))
        if len(check_stock) > 0:
            stock = check_stock
            for s in stock:
                s['image'] = ''
                if '|' in s['remarks']:
                    s['image'] = s['remarks'].split('|')[1]
                    if 'source/card/' not in s['remarks'].split('|')[1]:
                        s['image'] = 'source/card/' + s['remarks'].split('|')[1]
                    s['remarks'] = s['remarks'].split('|')[0]
        LOGGER.debug((str(stock)))
        K_SIGNDLER.SIGNAL_GET_PRODUCT_STOCK.emit(json.dumps(stock))
        return True
    except Exception as e:
        LOGGER.warning((e))
        K_SIGNDLER.SIGNAL_GET_PRODUCT_STOCK.emit(json.dumps(stock))
        return False


def start_store_transaction_global(param):
    _Helper.get_thread().apply_async(store_transaction_global, (param,))
    # _Helper.get_thread().apply_async(store_transaction_mds, (param,))


GLOBAL_TRANSACTION_DATA = None

# '{"date":"Thursday, March 07, 2019","epoch":1551970698740,"payment":"cash","shop_type":"shop","time":"9:58:18 PM",
# "qty":4,"value":"3000","provider":"Kartu Prabayar","raw":{"init_price":500,"syncFlag":1,"createdAt":1551856851000,
# "stock":99,"pid":"testprod001","name":"Test Product","status":1,"sell_price":750,"stid":"stid001",
# "remarks":"TEST STOCK PRODUCT"},"notes":"DEBUG_TEST - 1551970698879"}'
# '{"date":"Thursday, March 07, 2019","epoch":1551970911009,"payment":"debit","shop_type":"topup","time":"10:01:51 PM",
# "qty":1,"value":"50000","provider":"e-Money Mandiri","raw":{"provider":"e-Money Mandiri","value":"50000"},
# "notes":"DEBUG_TEST - 1551970911187"}')


def get_tpid(string):
    param = {'string': string}
    t = _DAO.get_tpid(param)
    _tpid = t[0]['tpid']
    print('pyt: get transactionType code : ', _tpid)
    return _tpid


def get_payment(string):
    if string == 'debit' or string == 'credit':
        return 'EDC'
    else:
        return string


MEI_HISTORY = ''
CARD_NO = ''
TRX_ID_SALE = ''
PID_SALE = ''
PID_STOCK_SALE = ''


def retry_store_transaction_global():
    _param = json.dumps(GLOBAL_TRANSACTION_DATA)
    _retry = True
    _Helper.get_thread().apply_async(store_transaction_global, (_param, _retry,))


def start_direct_store_transaction_data(payload):
    _Helper.get_thread().apply_async(direct_store_transaction_data, (payload,))


def direct_store_transaction_data(payload):
    global GLOBAL_TRANSACTION_DATA
    GLOBAL_TRANSACTION_DATA = json.loads(payload)


# Must Updated Below
# <bank>_topup_freq                            BIGINT DEFAULT 0,
# <bank>_shop_freq                             BIGINT DEFAULT 0,
# <bank>_transaction_count                     BIGINT DEFAULT 0,
# <bank>_transaction_amount                    BIGINT DEFAULT 0,
# <bank>_card_trx_count                        BIGINT DEFAULT 0,
# <bank>_card_trx_amount                       BIGINT DEFAULT 0,

def update_summary_report(data):
    if _Helper.empty(data) is True:
        return False
    _DAO.create_today_report(_Common.TID)
    bank = _Common.get_bank_name(data.get('provider', ''))
    # Handle Empty Bank name From Bank Id
    if bank == '':
        if 'raw' in data.keys():
            bank_id = data['raw'].get('bid', 0)
            if bank_id != 0 and str(bank_id) in _Common.CODE_BANK.keys():
                bank = _Common.CODE_BANK[str(bank_id)].lower()
    if data['shop_type'] == 'shop':
        _DAO.update_today_summary_multikeys([bank+'_shop_freq', bank+'_card_trx_count'], 1)
        _DAO.update_today_summary(bank+'_card_trx_amount', int(data.get('value', 0)))  
    elif data['shop_type'] == 'topup':
        _DAO.update_today_summary_multikeys([bank+'_topup_freq', bank+'_transaction_count'], 1)
        _DAO.update_today_summary(bank+'_transaction_amount', int(data.get('value', 0)))  
    return True


def store_transaction_mds(param):
    global GLOBAL_TRANSACTION_DATA
    try:
        p = GLOBAL_TRANSACTION_DATA = json.loads(param)
        update_summary = update_summary_report(p)
        LOGGER.info(('UPDATE REPORT SUMMARY', update_summary))
        if p['shop_type'] != 'topup':
            LOGGER.warning(('MDS Store Transaction Failed, Only Support Topup TRX This Time'))
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('ERROR')
            return
        bank_id = _Common.get_bid(p['provider'])
        trx_id = p['shop_type'] + str(p['epoch'])
        if bank_id in [0, 1, 2]: #Mandiri & BNI
            store_result = _MDSService.push_trx_offline(param)
        else:
            store_result = _MDSService.push_trx_online(param)
        if store_result is True:
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('SUCCESS|STORE_TRX-'+trx_id)
        else:
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('PENDING|STORE_TRX-'+trx_id)
    except Exception as e:
        LOGGER.warning((e))
        K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('ERROR|STORE_TRX')


def store_transaction_global(param, retry=False):
    global GLOBAL_TRANSACTION_DATA, TRX_ID_SALE, PID_SALE, CARD_NO, PID_STOCK_SALE
    
    g = GLOBAL_TRANSACTION_DATA = json.loads(param)
    LOGGER.info(('GLOBAL_TRANSACTION_DATA', param))

    try:
        if 'payment_error' in g.keys() or 'process_error' in g.keys():
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('PAYMENT_FAILED_CANCEL_TRIGGERED')
            # Must Stop The Logic Here
            return
        
        # Update Daily Summary Data
        update_summary = update_summary_report(g)
        LOGGER.info(('UPDATE REPORT SUMMARY', update_summary))

        trx_id = TRX_ID_SALE = _Helper.get_uuid()
        product_id = PID_SALE = g['shop_type'] + str(g['epoch'])
        bank_id = _Common.get_bid(g['provider'])            
        
        # Delete Failure/Pending TRX Local Records
        _DAO.delete_transaction_failure({
            'reff_no': product_id,
            'tid': _Common.TID
        })
        
        total_amount = int(g['value']) * int(g['qty'])
        payment_type = get_payment(g['payment'])
        admin_fee = int(g['admin_fee'])
        target_card_no = g['raw'].get('card_no', '')
        # Update Product Stock
        if g['shop_type'] == 'shop':
            admin_fee = 0
            bank_id = g['raw'].get('bid', 0)
            PID_STOCK_SALE = g['raw']['pid']
            # Move Card Stock Reduce To CD Module - 2022-08-04
            check_product = _DAO.check_product_status_by_pid({'pid': g['raw']['pid']})
            # _DAO.update_product_stock(stock_update)
            # LOGGER.debug((trx_id, product_id, str(stock_update)))
            # K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('SUCCESS|UPDATE_PRODUCT_STOCK-' + stock_update['pid']+'-'+str(last_stock))
            # This Product ID Builder For Update Stock in Backend
            product_id = str(product_id) + '|' + str(check_product[0]['pid']) + '|' + str(check_product[0]['stock'])
            # NOTICE: Need For Stock Opname Calculation
            trx_notes = g['raw'].get('stid', '')
            # trx_notes = g['raw']
            # trx_notes['stock_details'] = stock_update
            # Disable Delay Process
            # LOGGER.info(('PROCESS_DELAY 1 Seconds', g['shop_type']))
            # sleep(1)
        if g['shop_type'] == 'topup':
            trx_notes = json.dumps(g['topup_details'])
        
        trace_no = g['payment_details'].get('trx_id', '')
        if trace_no == '':
            trace_no = g['payment_details'].get('invoice_no', '')
            
        # Insert DKI TRX STAN For Topup Jakcard Using Cash
        if g['shop_type'] == 'topup' and g['payment'] == 'cash':
            if g['raw']['bank_name'] == 'DKI':
                g['payment_details']['stan_no'] = _Common.LAST_DKI_STAN
                trace_no = _Common.LAST_DKI_STAN
                
        payment_notes = json.dumps(g['payment_details'])
        # _______________________________________________________________________________________________________
        trx_data = {
            "trxId" : trx_id,
            "tid" : _Common.TID,
            "amount" : total_amount,
            "createdAt" : _Helper.now(),
            "paymentType" : payment_type.upper(),
            "trxType" : g['shop_type'].upper(),
            "paymentNotes" : payment_notes,
            "cardNo" : g['payment_details'].get('card_no', ''),
            "mid" : "",
            "productName" : g['provider'],
            "productId" : product_id,
            "traceNo" : trace_no,
            "adminFee" : admin_fee,
            "baseAmount" : total_amount if admin_fee == 0 else (total_amount - admin_fee),
            "targetCard" : target_card_no,
            "bankId" : bank_id,
            "trxNotes" : trx_notes
        }
        # _______________________________________________________________________________________________________
        
        check_trx = _DAO.check_trx_new(trx_id)
        # Store To Local If Empty
        if len(check_trx) == 0:
            # trx_data['createdAt'] = _Helper.now()
            _DAO.insert_transaction_new(trx_data)
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('SUCCESS|STORE_TRX-' + trx_id)
        # Push To Server
        status, response = _HTTPAccess.post_to_url(url=_Common.BACKEND_URL + 'sync/transaction-new', param=trx_data)
        if status == 200 and response['id'] == trx_id:
            trx_data['key'] = trx_data['trxId']
            _DAO.mark_sync(param=trx_data, _table='TransactionsNew', _key='trxId')
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('SUCCESS|UPLOAD_TRX-' + trx_id)
        else:
            K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('PENDING|UPLOAD_TRX-' + trx_id)
    except Exception as e:
        LOGGER.warning((str(retry), str(e)))
        K_SIGNDLER.SIGNAL_STORE_TRANSACTION.emit('ERROR')
            
            
def start_kiosk_get_topup_amount():
    _Helper.get_thread().apply_async(kiosk_get_topup_amount)


def kiosk_get_topup_amount():
    LOGGER.info((str(_Common.TOPUP_AMOUNT_SETTING)))
    K_SIGNDLER.SIGNAL_GET_TOPUP_AMOUNT.emit(json.dumps(_Common.TOPUP_AMOUNT_SETTING))


def start_kiosk_get_payment_setting():
    _Helper.get_thread().apply_async(kiosk_get_payment_setting)


def kiosk_get_payment_setting():
    # LOGGER.info((str(_Common.PAYMENT_SETTING)))
    K_SIGNDLER.SIGNAL_GET_PAYMENT_SETTING.emit(json.dumps(_Common.PAYMENT_SETTING))


def start_store_topup_transaction(param):
    # Moved Into Each Topup Offline Process
    return


def reset_db_record():
    LOGGER.info(('START_RESET_DB_RECORDS', _Helper.time_string()))
    try:
        _DAO.flush_table('TransactionFailure', ' tid <> "'+_Common.TID+'" ')
        time.sleep(1)
        _DAO.flush_table('TransactionsNew', ' tid <> "'+_Common.TID+'" ')
        time.sleep(1)
        _DAO.flush_table('ProductStock', ' tid <> "'+_Common.TID+'" ')
        time.sleep(1)
        _DAO.flush_table('TopUpRecords', ' syncFlag = 9 AND cardNo LIKE "7546%" ')
        time.sleep(1)
        _DAO.flush_table('TopUpRecords', ' syncFlag = 3 AND cardNo LIKE "6032%" ')
        time.sleep(1)
        _DAO.flush_table('Cash')
        time.sleep(1)
        _DAO.flush_table('Product')
        time.sleep(1)
        _DAO.flush_table('Transactions')
        LOGGER.info(('FINISH_RESET_DB_RECORDS', _Helper.time_string()))
        return 'FIRST_INIT_CLEANUP_SUCCESS'
    except Exception as e:
        LOGGER.warning((str(e)))
        return 'FIRST_INIT_CLEANUP_FAILED'


def user_action_log(log):
    if '[Homepage]' in log:
        LOGGER.info(('[STANDBY IN HOMEPAGE]'))
    else:
        LOGGER.info(('[USER_ACTION]', str(log)))


def system_action_log(log, level='info'):
    if level == 'info':
        LOGGER.info(('[SYSTEM_ACTION]', str(log)))
    elif level == 'debug':
        LOGGER.debug(('[SYSTEM_ACTION]', str(log)))
    else:
        LOGGER.warning(('[SYSTEM_ACTION]', str(log)))


def python_dump(log):
    _Helper.dump(log)


def house_keeping(age_month=1, mode='DATA_FILES'):
    if mode == 'DATA_FILES':
        LOGGER.info(('HOUSE_KEEPING', age_month, mode, _Helper.time_string()))
        print('pyt: [START] HOUSE_KEEPING ' + mode + ' ' +_Helper.time_string())
        _DAO.clean_old_data(tables=['Receipts', 'Settlement', 'SAMAudit', 'SAMRecords',
                                    'TopupRecords', 'TransactionFailure', 'TransactionsNew'],
                            key='createdAt',
                            age_month=age_month)
    expired_seconds = (age_month * 30 * 24 * 60 * 60)
    expired = time.time() - expired_seconds
    paths = ['_pPDF', '_lLog', '_qQr', '_jJob|.done']
    LOGGER.info(('START FILES HOUSE_KEEPING', age_month, paths, expired, mode, _Helper.time_string()))
    print('pyt: [START] HOUSE_KEEPING ' + str(paths) + ' ' + str(expired) + ' ' + mode + ' ' + _Helper.time_string())
    for path in paths:
        ext = '*.*'
        if '|' in path:
            el = path.split('|')
            path = el[0]
            ext = el[1]
        work_dir = os.path.join(sys.path[0], path)
        files = os.listdir(work_dir)
        if ext != '*.*':
            files = [x for x in os.listdir(work_dir) if x.endswith(ext)]
        if len(files) == 0:
            continue
        for f in files:
            file = os.path.join(work_dir, f)
            if os.path.isfile(file):
                stat = os.stat(file)
                file_modification_time = stat.st_mtime
                if file_modification_time < expired and not file.endswith('.log'):
                    LOGGER.debug(('Removing', file, file_modification_time, expired))
                    os.remove(file)
    LOGGER.info(('FINISH DATA/FILES HOUSE_KEEPING', age_month, mode, _Helper.time_string()))
    print('pyt: [FINISH] DATA/FILES HOUSE_KEEPING ' + mode + ' ' +_Helper.time_string())
    return 'HOUSE_KEEPING_' + str(age_month) + '_SUCCESS'


def reset_open_job():
    extentions = ('.process', '.failed', '.failure')
    open_request_jobs = [f for f in os.listdir(_Common.JOB_PATH) if f.endswith(extentions)]
    if (len(open_request_jobs) > 0):
        LOGGER.info(('Reset Open Request Job', open_request_jobs))
        for request_job in open_request_jobs:
            old_file_request = os.path.join(_Common.JOB_PATH, request_job)
            new_file_request = old_file_request.replace('.process', '.request')
            os.rename(old_file_request, new_file_request)
    open_upload_jobs = [f for f in os.listdir(_Common.JOB_PATH) if f.endswith('.process_upload')]
    if (len(open_upload_jobs) > 0):
        LOGGER.info(('Reset Open Upload Job', open_upload_jobs))
        for upload_job in open_upload_jobs:
            old_file_upload = os.path.join(_Common.JOB_PATH, upload_job)
            new_file_upload = old_file_upload.replace('.process_upload', '.upload')
            os.rename(old_file_upload, new_file_upload)


def start_change_setting(key, value):
    _Helper.get_thread().apply_async(change_setting, (key, value,))


def change_setting(key, value):
    # print(_Helper.whoami())
    if '||' in key:
        section = key.split('||')[0]
        option = key.split('||')[1]
        _ConfigParser.set_value(section, option, value)
        if key == 'MANDIRI_C2C||minimum^amount':
            _Common.C2C_THRESHOLD = int(value)
        elif key == 'MANDIRI_C2C||amount^topup':
            _Common.C2C_TOPUP_AMOUNT = value
        elif key == 'BNI||amount^minimum':
            _Common.BNI_THRESHOLD = int(value)
        elif key == 'BNI||amount^topup':
            _Common.BNI_TOPUP_AMOUNT = value
    elif key == 'printer^setting':
        if value == '1':
            value = 'WhatsApp'
        else:
            value = 'Default'
        _ConfigParser.set_value('PRINTER', 'printer^type', value)
    else:
        if value == '1':
            value = '0'
        else:
            value = '1'
        _Common.log_to_temp_config(key, value)
    K_SIGNDLER.SIGNAL_PANEL_SETTING.emit('CHANGE_SETTING|SUCCESS')

    
def remove_failed_trx(trx_id):
    try:  
        _DAO.delete_transaction_failure({
            'reff_no': trx_id,
            'tid': _Common.TID
        })
        return 'DELETE_FAILED_TRX_SUCCESS'
    except Exception as e:
        LOGGER.warning((e))
        return 'DELETE_FAILED_TRX_FAILED'


def start_trigger_explorer():
    _Helper.get_thread().apply_async(trigger_explorer,)
    

def trigger_explorer():
    try:
        subprocess.Popen(r'explorer /select,"C:\"')
        # os.system('explorer.exe')
        K_SIGNDLER.SIGNAL_PANEL_SETTING.emit('EXPLORER|DONE')
    except Exception as e:
        LOGGER.warning((e))
        K_SIGNDLER.SIGNAL_PANEL_SETTING.emit('EXPLORER|ERROR')
        

def start_reset_receipt_count(count):
    _Helper.get_thread().apply_async(reset_receipt_count,(count,))


def reset_receipt_count(count):
    result = _Common.reset_receipt_count(count)
    K_SIGNDLER.SIGNAL_PANEL_SETTING.emit('RESET_PRINTER_PAPER|'+result)
    # if _Common.IS_WINDOWS:
    #     if int(count) == 0:
    #         command = 'start _resetPrinterSpooler.bat'
    #         return _Helper.execute_console(command)
