__author__ = 'wahyudi@multidaya.id'

import os
import sys
from _tTools import _Helper
from _dDAO import _DAO
from time import sleep
from _cConfig import _Common
from _nNetwork import _HTTPAccess, _SFTPAccess, _FTPAccess
import logging
from _sService import _KioskService
from _dDevice import _EDC
from _dDevice import _QPROX
import json
from _sService import _UserService
from _sService import _SettlementService
from _sService import _TopupService
from _sService import _UpdateAppService
from operator import itemgetter
import subprocess
from _tTools import _SalePrintTool


LOGGER = logging.getLogger()
SETTING_PARAM = []


def start_sync_machine(url, param):
    _Helper.get_thread().apply_async(sync_machine, (url, param,))


def sync_machine(url, param):
    global SETTING_PARAM
    SETTING_PARAM = param
    attempt = 0
    while True:
        attempt += 1
        try:
            status, response = _HTTPAccess.get_from_url(url=url, force=True)
            if status == 200:
                print('pyt: sync_machine ' + _Helper.time_string() + ' Connected To Backend')
                _Common.KIOSK_STATUS = 'ONLINE'
                _KioskService.LAST_SYNC = _Helper.time_string()
            else:
                print('pyt: sync_machine ' + _Helper.time_string() + ' Disconnected From Backend')
                _Common.KIOSK_STATUS = 'OFFLINE'
            if attempt == 1:
                print('pyt: sync_machine ' + _Helper.time_string() + ' Setting Initiation From Backend')
                s, r = _HTTPAccess.post_to_url(url=_Common.BACKEND_URL + 'get/setting', param=SETTING_PARAM)
                _KioskService.update_kiosk_status(s, r)
                _DAO.create_today_report(_Common.TID)
            # if attempt > 1:
            if attempt > 1 and _Common.IDLE_MODE is True:
                __url = _Common.BACKEND_URL + 'kiosk/status'
                __param = _KioskService.machine_summary()
                __param['on_usage'] = 'IDLE' if _Common.IDLE_MODE is True else 'ON_USED'
                # LOGGER.info((__url, str(__param)))
                # print('pyt: sync_machine_status ' + _Helper.time_string() + ' Backend Trigger...')
                _HTTPAccess.post_to_url(url=__url, param=__param, custom_timeout=3)
        except Exception as e:
            LOGGER.debug(e)         
        finally:
            if _Common.DAILY_C2C_SETTLEMENT_TIME == _Helper.time_string('%H:%M'):
                _SettlementService.start_daily_mandiri_c2c_settlement()    
            if _Common.DAILY_SYNC_SUMMARY_TIME == _Helper.time_string('%H:%M'):
                while True:
                    if send_daily_summary() is True:
                        break
            # Add Daily Reboot Time Local Setting
            if _Common.DAILY_REBOOT_TIME == _Helper.time_string('%H:%M'):
                LOGGER.info(('Trigger Daily Reboot Time (Countdown 30)', _Common.DAILY_REBOOT_TIME, _Helper.time_string()))            
                sleep(30)
                if _Common. IS_WINDOWS:
                    _KioskService.execute_command('shutdown -r -f -t 0')
                else:
                    _KioskService.execute_command('reboot now')
                # _KioskService.kiosk_status()
        sleep(30.50)
        
def start_send_battery_status():
    _Helper.get_thread().apply_async(send_battery_status,)


def send_battery_status():
    while True:
        _KioskService.send_battery_status()
        sleep(10)


def send_daily_summary():
    try:
        payload = _DAO.get_today_report(_Common.TID)
        sleep(1)
        _QPROX.mdr_c2c_balance_info()
        payload['mandiri_deposit_last_balance'] = _Common.MANDIRI_ACTIVE_WALLET
        sleep(1)
        _QPROX.bni_c2c_balance_info()
        payload['bni_deposit_last_balance'] = _Common.BNI_ACTIVE_WALLET
        # payload['last_stock_cash'] = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__']
        payload['last_stock_cash'] = _Common.get_cash_activity()['total']
        payload['last_stock_slot_1'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 101 ')[0]['__']
        payload['last_stock_slot_2'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 102 ')[0]['__']
        payload['last_stock_slot_3'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 103 ')[0]['__']
        payload['last_stock_slot_4'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 104 ')[0]['__']
        url = _Common.BACKEND_URL + 'sync/daily-summary'
        if len(payload) > 0:
            _DAO.mark_today_report(_Common.TID)
            s, r = _HTTPAccess.post_to_url(url=url, param=payload)
            print('pyt: PROCESSING TODAY REPORT ' + _Helper.time_string())
            if s != 200 or r.get('result') != 'OK':
                payload['endpoint'] = 'sync/daily-summary'
                _Common.store_request_to_job(name=_Helper.whoami(), url=url, payload=payload)
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning(e)
        return False
    

def send_all_not_synced_daily_report():
    while True:
        try:
            reports = _DAO.get_all_unsynced_report(_Common.TID)
            if len(reports) > 0:
                for report in reports:
                    if report['report_date'] == _Helper.time_string(f='%Y-%m-%d'):
                        continue
                    report['mandiri_deposit_last_balance'] = -1
                    report['bni_deposit_last_balance'] = -1
                    report['last_stock_cash'] = -1
                    report['last_stock_slot_1'] = -1
                    report['last_stock_slot_2'] = -1
                    report['last_stock_slot_3'] = -1
                    report['last_stock_slot_4'] = -1
                    url = _Common.BACKEND_URL + 'sync/daily-summary'
                    s, r = _HTTPAccess.post_to_url(url=url, param=report)
                    print('pyt: PROCESSING ' + report['report_date'] + ' ' + _Helper.time_string())
                    LOGGER.debug('PROCESSING ' + report['report_date'] + ' ' + _Helper.time_string())
                    if s == 200 and r.get('result') == 'OK':
                        _DAO.mark_synced_report(_Common.TID, report['report_date'])
                        print('pyt: SUCCESS SYNCED ' + report['report_date'] + ' ' + _Helper.time_string())
                        LOGGER.info('SUCCESS SYNCED ' + report['report_date'] + ' ' + _Helper.time_string())
                    continue
        except Exception as e:
            LOGGER.warning(e)
        sleep(60*30)


def start_send_all_not_synced_daily_report():
    _Helper.get_thread().apply_async(send_all_not_synced_daily_report)


def start_idle_mode():
    _Helper.get_thread().apply_async(change_idle_mode, ('START',))


def stop_idle_mode():
    _Helper.get_thread().apply_async(change_idle_mode, ('STOP',))


def change_idle_mode(s):
    if s == 'START':
        _Common.IDLE_MODE = True
        _UserService.USER = None
    elif s == 'STOP':
        _Common.IDLE_MODE = False


def start_sync_machine_status():
    _Helper.get_thread().apply_async(sync_machine_status)


# Disabled
def sync_machine_status():
    __url = _Common.BACKEND_URL + 'kiosk/status'
    __param = dict()
    while True:
        try:
            if _Helper.is_online(source='sync_machine_status') is True and _Common.IDLE_MODE is True:
                __param = _KioskService.machine_summary()
                __param['on_usage'] = 'IDLE' if _Common.IDLE_MODE is True else 'ON_USED'
                # LOGGER.info((__url, str(__param)))
                print('pyt: sync_machine_status ' + _Helper.time_string() + ' Backend Trigger...')
                _HTTPAccess.post_to_url(url=__url, param=__param, custom_timeout=3)
            else:
                LOGGER.debug(('Sending Kiosk Status : ', str(_Common.IDLE_MODE)))
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(59.59)


def start_do_pending_request_job():
    _Helper.get_thread().apply_async(do_pending_request_job)


def do_pending_request_job():
    while True:
        pending_jobs = [f for f in os.listdir(_Common.JOB_PATH) if f.endswith('.request')]
        # print('pyt: count pending_jobs : ' + str(len(pending_jobs)))
        # LOGGER.info(('count', len(pending_jobs)))
        if len(pending_jobs) > 0 and _Common.IDLE_MODE is True:
            # pending_jobs = pending_jobs.sort()
            for p in pending_jobs:
                try:
                    jobs_path = os.path.join(_Common.JOB_PATH, p)
                    content = open(jobs_path, 'r').read().strip()
                    if len(_Common.clean_white_space(content)) == 0:
                        os.remove(jobs_path)
                        continue
                    job = json.loads(content)
                    __url = job['url']
                    __param = job['payload']
                    __endpoint = job['payload'].get('endpoint')
                    if _Helper.empty(__endpoint):
                        __endpoint = _Helper.url_to_endpoint(__url)
                        # jobs_path_failed = jobs_path.replace('.request', '.failed')
                        # os.rename(jobs_path, jobs_path_failed)
                        # continue
                    jobs_path_process = jobs_path.replace('.request', '.process')
                    os.rename(jobs_path, jobs_path_process)
                    if 'header' in job:
                        # header = {
                        #     'Accept': '*/*',
                        #     'Content-Type': 'application/json',
                        #     'Authorization': 'Bearer: '+_Common.MDS_TOKEN
                        # }
                        __header = job['header']
                        if not _Helper.empty(_Common.MDS_TOKEN):
                            __header['Authorization'] = 'Bearer: '+_Common.MDS_TOKEN
                        status, response = _HTTPAccess.post_to_url(url=__url, param=__param, header=__header)
                    else:
                        status, response = _HTTPAccess.post_to_url(url=__url, param=__param)
                    if 'result' not in response.keys():
                        response['result'] = status
                    # LOGGER.debug((p, __url, __param, status, response))
                    # print('pyt: [DEBUG] ' + ' '.join([p, _Helper.time_string(), str(status), str(response)]))
                    if status == 200 and (__endpoint in _Common.ENDPOINT_SUCCESS_BY_200_HTTP_HEADER or response['result'] == 'OK'):
                        jobs_path_done = jobs_path_process.replace('.process', '.done')
                        os.rename(jobs_path_process, jobs_path_done)
                        LOGGER.debug((jobs_path_process, jobs_path_done))
                    elif status == 400 and __endpoint in _Common.ENDPOINT_SUCCESS_BY_ANY_HTTP_HEADER:
                        jobs_path_done = jobs_path_process.replace('.process', '.done')
                        os.rename(jobs_path_process, jobs_path_done)
                        LOGGER.debug(('Force Success', str(_Common.ENDPOINT_SUCCESS_BY_ANY_HTTP_HEADER), jobs_path_process, jobs_path_done))
                    else:
                        LOGGER.warning((p, status, response))
                        jobs_path_reopen = jobs_path_process.replace('.process', '.request')
                        os.rename(jobs_path_process, jobs_path_reopen)
                except Exception as e:
                    LOGGER.warning((e, p))
                continue
        sleep(61.61)


def start_do_pending_upload_job():
    _Helper.get_thread().apply_async(do_pending_upload_job)


def do_pending_upload_job():
    while True:
        pending_jobs = [f for f in os.listdir(_Common.JOB_PATH) if f.endswith('.upload')]
        # print('pyt: count pending_jobs : ' + str(len(pending_jobs)))
        # LOGGER.info(('count', len(pending_jobs)))
        if len(pending_jobs) > 0:
            try:
                for p in pending_jobs:
                    jobs_path = os.path.join(_Common.JOB_PATH, p)
                    content = open(jobs_path, 'r').read().strip()
                    if len(_Common.clean_white_space(content)) == 0:
                        os.remove(jobs_path)
                        continue
                    job = json.loads(content)
                    host = job['host']
                    data = job['data']
                    # BNI Data
                    # reupload = {
                    #     'bank': bank, 
                    #     'filename': _param['filename'],
                    #     'path_file': _param['path_file'],
                    # }
                    # Mandiri Data
                    # reupload = {
                    #     'bank': bank, 
                    #     'filename': [_param_sett['filename'], _file_ok],
                    #     'local_path':  _param_sett['path_file'],
                    #     'remote_path':  _Common.SFTP_C2C['path_settlement'],
                    # }
                    jobs_path_process = jobs_path.replace('.upload', '.process_upload')
                    os.rename(jobs_path, jobs_path_process)
                    if host == 'BNI':
                        _SFTPAccess.HOST_BID = 2
                        result = _SFTPAccess.send_file(data['filename'], local_path=data['path_file'], remote_path=None)
                    elif host == 'MANDIRI_C2C':
                        _SFTPAccess.HOST_BID = 0
                        result = _SFTPAccess.send_file(data['filename'], local_path=data['local_path'], remote_path=data['remote_path'])
                    else:
                        result = False
                    LOGGER.debug((p, host, data, result))
                    if result['success'] is True:
                        jobs_path_done = jobs_path_process.replace('.process_upload', '.done')
                        os.rename(jobs_path_process, jobs_path_done)
                        LOGGER.debug((jobs_path_process, jobs_path_done))
                    else:
                        jobs_path_reopen = jobs_path_process.replace('.process_upload', '.upload')
                        os.rename(jobs_path_process, jobs_path_reopen)
                    continue
            except Exception as e:
                LOGGER.warning(e)
        sleep(122.122)


def start_kiosk_sync():
    _Helper.get_thread().apply_async(kiosk_sync)


def start_kiosk_data_sync():
    _Helper.get_thread().apply_async(kiosk_data_sync)


def kiosk_data_sync():
    print("pyt: Start Syncing Product Stock...")
    sync_product_stock()
    print("pyt: Start Syncing Product Data...")
    sync_product_data()
    print("pyt: Start Syncing Shop Data Records ...")
    sync_data_transaction()
    print("pyt: Start Syncing Failed Shop Data Records ...")
    sync_data_transaction_failure()


def start_kiosk_topup_sync():
    _Helper.get_thread().apply_async(kiosk_topup_sync)


def kiosk_topup_sync():
    print("pyt: Start Syncing SAM Audit Records ...")
    sync_sam_audit()
    print("pyt: Start Syncing Topup Amount...")
    sync_topup_amount()
    print("pyt: Start Syncing Topup Data Records...")
    sync_topup_records()


def kiosk_sync():
    print("pyt: Start Syncing Remote Task...")
    sync_task()
    print("pyt: Start Syncing Machine Status...")
    sync_machine_status()
    print("pyt: Start Syncing Pending Refund...")
    sync_pending_refund()
    print("pyt: Start Syncing Product Stock...")
    sync_product_stock()
    print("pyt: Start Syncing Product Data...")
    sync_product_data()
    print("pyt: Start Syncing Topup Amount...")
    sync_topup_amount()
    print("pyt: Start Syncing Topup Data Records...")
    sync_topup_records()
    print("pyt: Start Syncing Shop Data Records ...")
    sync_data_transaction()
    print("pyt: Start Syncing Failed Shop Data Records ...")
    sync_data_transaction_failure()
    print("pyt: Start Syncing SAM Audit Records ...")
    sync_sam_audit()


def start_sync_topup_records():
    _Helper.get_thread().apply_async(sync_topup_records)


def sync_topup_records():
    url = _Common.BACKEND_URL + 'sync/topup-records'
    _table_ = 'TopUpRecords'
    while True:
        try:
            if _Helper.is_online(source='sync_topup_records') is True and _Common.IDLE_MODE is True:
                topup_records = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(topup_records) > 0:
                    print('pyt: sync_topup_records ' + _Helper.time_string() + ' Re-Sync Topup Records Data...')
                    for t in topup_records:
                        status, response = _HTTPAccess.post_to_url(url=url, param=t)
                        # LOGGER.info(('sync_topup_records', json.dumps(t), str(status), str(response)))
                        if status == 200 and response['id'] == t['rid']:
                            LOGGER.info(response)
                            t['key'] = t['rid']
                            _DAO.mark_sync(param=t, _table=_table_, _key='rid')
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(44.55)


def start_sync_data_transaction():
    _Helper.get_thread().apply_async(sync_data_transaction)


def sync_data_transaction():
    url = _Common.BACKEND_URL + 'sync/transaction-new'
    _table_ = 'TransactionsNew'
    while True:
        try:
            if _Helper.is_online(source='sync_data_transaction') is True:
                transactions = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(transactions) > 0:
                    # print('pyt: sync_data_transaction ' + _Helper.time_string() + ' Re-Sync Transaction Data...')
                    for t in transactions:
                        # Revert Flag Validation mid for Sale Calculation If Not Synced Before
                        t['mid'] = ''
                        status, response = _HTTPAccess.post_to_url(url=url, param=t)
                        if status == 200 and response['id'] == t['trxId']:
                            LOGGER.info(response)
                            t['key'] = t['trxId']
                            _DAO.mark_sync(param=t, _table=_table_, _key='trxId')
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(10.10)
        

def sync_data_transaction_old():
    url = _Common.BACKEND_URL + 'sync/transaction-topup'
    _table_ = 'Transactions'
    while True:
        try:
            if _Helper.is_online(source='sync_data_transaction') is True and _Common.IDLE_MODE is True:
                transactions = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(transactions) > 0:
                    # print('pyt: sync_data_transaction ' + _Helper.time_string() + ' Re-Sync Transaction Data...')
                    for t in transactions:
                        status, response = _HTTPAccess.post_to_url(url=url, param=t)
                        if status == 200 and response['id'] == t['trxid']:
                            LOGGER.info(response)
                            t['key'] = t['trxid']
                            _DAO.mark_sync(param=t, _table=_table_, _key='trxid')
                            _DAO.update_product_status(param={'status': 1, 'pid': t['pid']})
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(88.99)


def start_sync_data_transaction_failure():
    _Helper.get_thread().apply_async(sync_data_transaction_failure)


def sync_data_transaction_failure():
    url = _Common.BACKEND_URL + 'sync/transaction-failure'
    _table_ = 'TransactionFailure'
    while True:
        try:
            if _Helper.is_online(source='sync_data_transaction_failure') is True and _Common.IDLE_MODE is True:
                transaction_failures = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(transaction_failures) > 0:
                    # print('pyt: sync_data_transaction_failure ' + _Helper.time_string() + ' Re-Sync Transaction Failure Data...')
                    for t in transaction_failures:
                        status, response = _HTTPAccess.post_to_url(url=url, param=t)
                        if status == 200 and response['id'] == t['trxid']:
                            LOGGER.info(response)
                            t['key'] = t['trxid']
                            _DAO.mark_sync(param=t, _table=_table_, _key='trxid')
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(77.88)


def start_sync_product_data():
    _Helper.get_thread().apply_async(sync_product_data)


def sync_product_data():
    url = _Common.BACKEND_URL + 'sync/product'
    _table_ = 'Product'
    while True:
        try:
            if _Helper.is_online(source='sync_product_data') is True and _Common.IDLE_MODE is True:
                products = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(products) > 0:
                    # print('pyt: sync_product_data ' + _Helper.time_string() + ' Re-Sync Product Data...')
                    for p in products:
                        status, response = _HTTPAccess.post_to_url(url=url, param=p)
                        if status == 200 and response['id'] == p['pid']:
                            LOGGER.info(response)
                            p['key'] = p['pid']
                            _DAO.mark_sync(param=p, _table=_table_, _key='pid')
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(55.66)


def start_sync_sam_audit():
    _Helper.get_thread().apply_async(sync_sam_audit)

# Disabled
def sync_sam_audit():
    url = _Common.BACKEND_URL + 'sync/sam-audit'
    _table_ = 'SAMAudit'
    while True:
        try:
            if _Helper.is_online(source='sync_sam_audit') is True and _Common.IDLE_MODE is True:
                audits = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(audits) > 0:
                    # print('pyt: sync_sam_audit ' + _Helper.time_string() + ' Re-Sync SAM Audit...')
                    for a in audits:
                        status, response = _HTTPAccess.post_to_url(url=url, param=a)
                        if status == 200 and response['id'] == a['lid']:
                            LOGGER.info(response)
                            a['key'] = a['lid']
                            _DAO.mark_sync(param=a, _table=_table_, _key='lid')
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(77.7)


def start_sync_settlement_bni():
    bank = 'BNI'
    _Helper.get_thread().apply_async(sync_settlement_bni, (bank,))


def sync_settlement_bni(bank):
    # _url = _Common.SMT_CONFIG['full_url']
    # # Do BNI Settlement Creation Every +- 15 Minutes
    # _SettlementService.start_do_bni_topup_settlement()
    # _table_ = 'Settlement'
    while True:
        try:
            if _Helper.is_online(source='sync_settlement_bni') is True and _Common.IDLE_MODE is True:
                _SettlementService.start_do_bni_topup_settlement()
            # Do BNI Settlement Creation Every +- 15 Minutes
            # if _Helper.is_online(source='sync_settlement_bni') is True and _Common.IDLE_MODE is True:
            #     settlements = _DAO.custom_query(' SELECT * FROM ' + _table_ +
            #                                     ' WHERE status = "TOPUP_PREPAID|OPEN" AND createdAt > 1554783163354 ')
            #     if len(settlements) > 0:
            #         print('pyt: sync_settlement_bni ' + _Helper.time_string() + ' Re-Sync Settlement Data...')
            #         for s in settlements:
            #             _param = {
            #                 'mid': _Common.SMT_CONFIG['mid'],
            #                 'token': _Common.SMT_CONFIG['token'],
            #                 'tid': 'MDD-VM'+_Common.TID,
            #                 'path_file': os.path.join(sys.path[0], '_rRemoteFiles', s['filename']),
            #                 'filename': s['filename'],
            #                 'row': s['row'],
            #                 'amount': s['amount'],
            #                 'bank': bank,
            #                 'bid': _Common.BID[bank],
            #                 'settlement_created_at': datetime.fromtimestamp(s['createdAt']).strftime('%Y-%m-%d %H:%M:%S')
            #             }
            #             status, response = _NetworkAccess.post_to_url(url=_url, param=_param)
            #             if status == 200 and response['response']['code'] == 200:
            #                 _DAO.update_settlement({'sid': s['sid'], 'status': 'TOPUP_PREPAID|CLOSED'})
            #                 LOGGER.info(response)
            #             else:
            #                 LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning((e), bank)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(900.1010)


def start_sync_task():
    _Helper.get_thread().apply_async(sync_task)


def sync_task():
    _url = _Common.BACKEND_URL + 'task/check'
    while True:
        try:
            if _Helper.is_online(source='sync_task') is True and _Common.IDLE_MODE is True:
                status, response = _HTTPAccess.get_from_url(url=_url, log=False)
                if status == 200 and response['result'] == 'OK':
                    if len(response['data']) > 0:
                        handle_tasks(response['data'])
                    else:
                        print('pyt: sync_task ' + _Helper.time_string() + ' No Remote Task Given..!')
                else:
                    print('pyt: sync_task ' + _Helper.time_string() + ' Failed To Check Remote Task..!')
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(33.33)


def start_sync_pending_refund():
    _Helper.get_thread().apply_async(sync_pending_refund)


# Disabled
def sync_pending_refund():
    _url = _Common.BACKEND_URL + 'refund/global'
    while True:
        try:
            pendings = _DAO.get_pending_refund()
            if len(pendings) > 0:
                for p in pendings:
                    _param = {
                        'customer_login'    : p['customer'],
                        'amount'            : str(p['amount']),
                        'reff_no'           : p['trxid'],
                        'channel'           : p['channel'],
                        'remarks'           : json.loads(p['remarks'])
                    } 
                    s, r = _HTTPAccess.post_to_url(url=_url, param=_param)
                    if s == 200 and r['data'] is not None:
                        _DAO.update_pending_refund({
                            'trxid'         : p['trxid'],
                            'remarks'       : json.dumps(r)
                        })                            
                        if r['result'] == 'OK': 
                            print('pyt: sync_pending_refund ' + _Helper.time_string() + ' ['+p['trxid']+'] SUCCESS RELEASED')
                        else:
                            print('pyt: sync_pending_refund ' + _Helper.time_string() + ' ['+p['trxid']+'] TRIGGERED')
                    else:
                        print('pyt: sync_pending_refund ' + _Helper.time_string() + ' ['+p['trxid']+'] FAILED')
            else:
                print('pyt: sync_pending_refund ' + _Helper.time_string() + ' NO PENDING')
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(15.15)


CHATBOT_COMMANDS = [
    'RESET_PAPER_ROLL',
    'REMOVE_FAILED_TRX <TRX_ID>',
    # 'EDC_CLEAR_BATCH',
    # 'EDC_SETTLEMENT',
    # 'RESET_DB',
    # 'DO_TOPUP_BNI_<SLOT>',
    # 'DO_SETTLEMENT_MANDIRI',
    # 'SAM_TO_SLOT_<SLOT>',
    # 'RESET_STOCK_PRODUCT',
    # 'UPDATE_STOCK_PRODUCT', 
    # 'REMOTE_UPDATE_STOCK',
    # 'RESET_OFFLINE_USER',
    # 'HOUSE_KEEPING_<COUNT_MONTH>',
    # 'REFRESH_PPOB_PRODUCT',
    # 'UPDATE_BALANCE_MANDIRI',
    # 'UPDATE_BALANCE_BNI', 
    # 'TRIGGER_TOPUP_1_BNI',
    # 'TRIGGER_TOPUP_1_MANDIRI',
    # 'TOPUP_DEPOSIT_MANDIRI',
    # 'TOPUP_DEPOSIT_BNI',
    # 'RELEASE_BNI_DEPOSIT_LOCK',
    # 'REPRINT_LAST_TRX',
    'CHECK_TIME',
    'TERMINAL_STATUS',
    'MAINTENANCE_ON',
    'MAINTENANCE_OFF',
    'CD_STATUS',
    'PRINTER_STATUS',
    'BILL_STATUS',
    'TRX_STATUS <TRX_ID>',
    'CASH_STATUS <TRX_ID>',
    'TOPUP_AMOUNT_SETTING',
    'FEATURE_SETTING',
    'PAYMENT_SETTING',
    # 'REFUND_SETTING',  
    'THEME_SETTING',
    # 'ADS_SETTING',
    
]

# TOPUP_AMOUNT_SETTING = load_from_temp_data('topup-amount-setting', 'json')
# FEATURE_SETTING = load_from_temp_data('feature-setting', 'json')
# PAYMENT_SETTING = load_from_temp_data('payment-setting', 'json')
# REFUND_SETTING = load_from_temp_data('refund-setting', 'json')
# THEME_SETTING = load_from_temp_data('theme-setting', 'json')
# ADS_SETTING = load_from_temp_data('ads-setting', 'json')

# Call Here, Not For Iterable
CHATBOT_COMMANDS.sort()


def available_commands():
    return CHATBOT_COMMANDS


def validate_command(t):
    try:
        for c in CHATBOT_COMMANDS:
            # Serialize Command Name
            if len(c.split(' ')) > 1: c = c.split(' ')[0]
            if len(t.split('|')) > 1: t = t.split('|')[0]
            if c == t:
                return True
            if t in c:
                return True
        return False
    except Exception as e:
        print(e)
        LOGGER.warning((e))
        return False
    


def handle_tasks(tasks):
    if len(tasks) == 0:
        return 'EMPTY_TASK'
    '''
    {
        "no": 1,
        "tid": "110321",
        "taskName": "REBOOT",
        "status": "OPEN",
        "result": null,
        "createdAt": "2018-04-14 00:00:00",
        "initedAt": "2018-04-14 23:38:46",
        "updatedAt": null,
        "userId": null
    }
    '''
    for task in tasks:
        # print(('pyt: GIVEN REMOTE TASK', str(task)))
        if task.get('mode') == 'CHATBOT':
            if not validate_command(task['taskName']):
                return 'NOT_SUPPORTED'
        # Handling Commands
        print('pyt: EXECUTING TASK', task['taskName'])
        if task['taskName'] == 'REBOOT':
            if _Common.IDLE_MODE is True:
                result = 'EXECUTED_INTO_MACHINE'
                _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('REBOOT')
                update_task(task, result)
                sleep(30)
                _KioskService.execute_command('shutdown -r -f -t 0')
            else:
                result = 'FAILED_EXECUTED_VM_ON_USED'
                return update_task(task, result)
        elif task['taskName'] == 'FORCE_REBOOT':
            result = 'EXECUTED_INTO_MACHINE'
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('REBOOT')
            update_task(task, result)
            sleep(30)
            _KioskService.execute_command('shutdown -r -f -t 0')
        elif task['taskName'] == 'RESET_PAPER_ROLL':
            result = _Common.reset_paper_roll()
            return update_task(task, result)
        elif 'REMOVE_FAILED_TRX|' in task['taskName']:
            trx_id = task['taskName'].split('|')[1]
            result = _KioskService.remove_failed_trx(trx_id)
            return update_task(task, result)
        elif task['taskName'] == 'EDC_CLEAR_BATCH':
            result = _EDC.void_settlement_data()
            return update_task(task, result)
        elif task['taskName'] == 'EDC_SETTLEMENT':
            result = _EDC.backend_edc_settlement()
            return update_task(task, result)
        elif task['taskName'] == 'RESET_DB':
            result = _KioskService.reset_db_record()
            return update_task(task, result)
        elif 'DO_TOPUP_BNI_' in task['taskName']:
            _slot = int(task['taskName'][-1])
            result = _TopupService.do_topup_deposit_bni(slot=_slot, force=True)
            return update_task(task, result)
        elif task['taskName'] == 'DO_SETTLEMENT_MANDIRI':
            result = 'FAILED_EXECUTED_VM_ON_USED'
            if _Common.IDLE_MODE is True:
                _SettlementService.start_reset_mandiri_settlement()
                result = 'TRIGGERED_INTO_SYSTEM'
            return update_task(task, result)
        elif 'SAM_TO_SLOT_' in task['taskName']:
            _slot = task['taskName'][-1]
            result = _Common.sam_to_slot(_slot)
            return update_task(task, result)
        elif task['taskName'] == 'APP_UPDATE':
            result = _UpdateAppService.start_do_update()
            update_task(task, result)
            if result == 'APP_UPDATE|SUCCESS':
                _KioskService.execute_command('shutdown -r -f -t 0')
        elif task['taskName'] == 'RESET_STOCK_PRODUCT':
            _DAO.clear_stock_product()
            return update_task(task, 'RESET_STOCK_PRODUCT_SUCCESS')
        elif task['taskName'] in ['UPDATE_STOCK_PRODUCT', 'REMOTE_UPDATE_STOCK']:
            result = sync_product_stock()
            return update_task(task, result)
        elif task['taskName'] == 'UPDATE_KIOSK':
            update_task(task)
            _url = _Common.BACKEND_URL + 'get/setting'
            LOGGER.info((_url, str(SETTING_PARAM)))
            s, r = _HTTPAccess.post_to_url(url=_url, param=SETTING_PARAM)
            # if s == 200 and r['result'] == 'OK':
            _KioskService.update_kiosk_status(s, r)
        elif 'RESET_OFFLINE_USER|' in task['taskName']:
            __hash = task['taskName'].split('|')[1]
            result = _UserService.reset_offline_user(__hash)
            return update_task(task, result)
        elif 'HOUSE_KEEPING_' in task['taskName']:
            age_month = int(task['taskName'][-1])
            result = _KioskService.house_keeping(age_month)
            return update_task(task, result)
        elif task['taskName'] == 'REFRESH_PPOB_PRODUCT':
            result = 'TRIGGERED_INTO_SYSTEM'
            _Common.log_to_temp_config('last^get^ppob', '0')
            return update_task(task, result)
        # New Task Here, Start Version 14.0.A-GLOBAL
        elif 'CONSOLE|' in task['taskName']:
            command = task['taskName'].split('|')[1]
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            return update_task(task, result)
        elif task['taskName'] == 'UPDATE_BALANCE_MANDIRI':
            result = _TopupService.start_deposit_update_balance('MANDIRI')
            return update_task(task, result)
        elif task['taskName'] in ['UPDATE_BALANCE_BNI', 'TRIGGER_TOPUP_1_BNI']:
            result = _TopupService.start_deposit_update_balance('BNI')
            return update_task(task, result)
        elif task['taskName'] == 'TRIGGER_TOPUP_1_MANDIRI':
            result = _TopupService.do_topup_deposit_mandiri(override_amount=1)
            return update_task(task, result)
        elif task['taskName'] == 'TOPUP_DEPOSIT_MANDIRI':
            result = _TopupService.do_topup_deposit_mandiri()
            return update_task(task, result)
        elif task['taskName'] == 'TOPUP_DEPOSIT_BNI':
            result = _TopupService.do_topup_deposit_bni(slot=1)
            return update_task(task, result)
        elif task['taskName'] == 'RELEASE_BNI_DEPOSIT_LOCK':
            _Common.remove_temp_data('BNI_DEPOSIT_RELOAD_IN_PROGRES')
            result = 'SUCCESS_REMOVE_FILE'
            return update_task(task, result)
        elif 'FORCE_LAST_STOCK' in task['taskName']:
            # 'taskName' => "|".join(['FORCE_LAST_STOCK', $reloadData->slot, $last_stock]),
            result = 'INVALID_ARGUMENTS'
            if len(task['taskName'].split('|')) >= 3:
                slot = task['taskName'].split('|')[1].replace('10', '')
                stock = task['taskName'].split('|')[2]
                result = 'TRIGGERED_INTO_SYSTEM'
                _Common.log_to_temp_config('stock^opname^slot^'+slot, stock)
                # Add Clear Data Product Stock -> In Order To Force Sync Card
                _DAO.custom_update("UPDATE ProductStock SET stock = 0")
            return update_task(task, result)
        # Add Other Command Identifier
        # elif task['taskName'] == 'REPRINT_LAST_TRX':
        #     result = _SalePrintTool.reprint_last_receipt('trx')
            return update_task(task, result)
        elif task['taskName'] == 'CHECK_TIME':
            result = _Helper.time_string()
            return update_task(task, result)
        elif task['taskName'] == 'TERMINAL_STATUS':
            result = _KioskService.machine_summary()
            return update_task(task, result)
        elif task['taskName'] == 'MAINTENANCE_ON':
            if _Common.MAINTENANCE_MODE:
                result = 'MAINTENANCE_MODE_STILL_ACTIVE'
            else:
                _Common.MAINTENANCE_MODE = True
                _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('MAINTENANCE_MODE_ON')
                result = 'MAINTENANCE_MODE_ACTIVATED'
            return update_task(task, result)
        elif task['taskName'] == 'MAINTENANCE_OFF':
            if not _Common.MAINTENANCE_MODE:
                result = 'MAINTENANCE_MODE_NOT_ACTIVE'
            else:
                _Common.MAINTENANCE_MODE = False
                _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('MAINTENANCE_MODE_OFF')
                result = 'MAINTENANCE_MODE_DISABLED'
            return update_task(task, result)
        elif task['taskName'] == 'CD_STATUS':
            result = _Common.CD_TYPES
            result = result.update({
                'cd1_error': _Common.CD1_ERROR,
                'cd2_error': _Common.CD2_ERROR,
                'cd3_error': _Common.CD3_ERROR,
                'cd4_error': _Common.CD4_ERROR,
                'cd5_error': _Common.CD5_ERROR,
                'cd6_error': _Common.CD6_ERROR,
            })
            return update_task(task, result)
        elif task['taskName'] == 'PRINTER_STATUS':
            result = {
                'type': _Common.PRINTER_TYPE,
                'paper_type': _Common.PRINTER_PAPER_TYPE,
                'error': _Common.PRINTER_ERROR,
                'status': _Common.get_printer_status(),
                'paper_count': _Common.RECEIPT_PRINT_COUNT,
                'paper_threshold': _Common.RECEIPT_PRINT_LIMIT,
            }
            return update_task(task, result)
        elif task['taskName'] == 'BILL_STATUS':
            result = {
                'type': _Common.BILL_TYPE,
                'port': _Common.BILL_PORT,
                'error': _Common.BILL_ERROR,
                'status': _Common.check_bill_status(),
                'cashbox_count': _Common.get_cash_activity(),
                'last_money_inserted': _Common.load_from_custom_config('BILL', 'last^money^inserted'),
            }
            return update_task(task, result)
        elif task['taskName'] == 'TOPUP_AMOUNT_SETTING':
            result = _Common.TOPUP_AMOUNT_SETTING
            return update_task(task, result)
        elif task['taskName'] == 'FEATURE_SETTING':
            result = _Common.FEATURE_SETTING
            return update_task(task, result)
        elif task['taskName'] == 'PAYMENT_SETTING':
            result = _Common.PAYMENT_SETTING
            return update_task(task, result)
        elif task['taskName'] == 'THEME_SETTING':
            result = _Common.THEME_SETTING
            return update_task(task, result)
        elif 'TRX_STATUS|' in task['taskName']:
            trx_id = task['taskName'].split('|')[1]
            trx_success = _DAO.custom_query('SELECT * FROM TransactionsNew WHERE productId = "'+trx_id+'"')
            if len(trx_success) > 0:
                result = trx_success[0]
                result['trx_status'] = 'SUCCESS'
                return update_task(task, result)
            trx_failed = _DAO.custom_query('SELECT * FROM TransactionFailure WHERE trxid = "'+trx_id+'"')
            if len(trx_failed) > 0:
                result = trx_failed[0]
                result['trx_status'] = 'PENDING'
                return update_task(task, result)
            result = 'TRX_NOT_FOUND'
            return update_task(task, result)
        elif 'CASH_STATUS|' in task['taskName']:
            trx_id = task['taskName'].split('|')[1]
            result = _Common.get_cash_activity(keyword=trx_id)
            return update_task(task, result)
        
        else:
            result = 'NOT_UNDERSTAND'
            return update_task(task, result)


def update_task(task, result='TRIGGERED_TO_SYSTEM'):
    if task.get('mode') == 'CHATBOT':
        return result
    # Update Remote Task Into Host By API
    _url = _Common.BACKEND_URL + 'task/finish'
    task['result'] = result
    while True:
        status, response = _HTTPAccess.post_to_url(url=_url, param=task)
        if status == 200 and response['result'] == 'OK':
            return True
        sleep(11.1)


def start_sync_product_stock():
    _Helper.get_thread().apply_async(sync_product_stock)


def sync_product_stock():
    _url = _Common.BACKEND_URL + 'get/product-stock'
    if _Helper.is_online(source='start_sync_product_stock') is True:
        s, r = _HTTPAccess.get_from_url(url=_url)
        if s == 200 and r['result'] == 'OK':
            products = r['data']
            products = sorted(products, key=itemgetter('status'))
            _DAO.flush_table('ProductStock')
            for product in products:
                if product['url_image'] is not None:
                    image_url = product['url_image']
                    download, image = _HTTPAccess.item_download(image_url, os.getcwd() + '/_qQML/source/card')
                    if download is True:
                        product['remarks'] = product['remarks'] + '|' + 'source/card/' + image
                _DAO.insert_product_stock(product)
            if _KioskService.get_product_stock() is True:
                _KioskService.K_SIGNDLER.SIGNAL_ADMIN_GET_PRODUCT_STOCK.emit('SYNC_PRODUCT_STOCK|SUCCESS')
                return 'UPDATE_STOCK_SUCCESS'
            else:
                _KioskService.K_SIGNDLER.SIGNAL_ADMIN_GET_PRODUCT_STOCK.emit('SYNC_PRODUCT_STOCK|PENDING')
                return 'UPDATE_STOCK_PENDING'
        else:
            _KioskService.K_SIGNDLER.SIGNAL_ADMIN_GET_PRODUCT_STOCK.emit('SYNC_PRODUCT_STOCK|ERROR')
            return 'UPDATE_STOCK_FAILED_UNKNOWN_ERROR'
    else:
        _KioskService.K_SIGNDLER.SIGNAL_ADMIN_GET_PRODUCT_STOCK.emit('SYNC_PRODUCT_STOCK|NO_CONNECTION')
        return 'UPDATE_STOCK_FAILED_NO_CONNECTION'


def start_sync_topup_amount():
    _Helper.get_thread().apply_async(sync_topup_amount)


def sync_topup_amount():
    _url = _Common.BACKEND_URL + 'get/topup-amount'
    while True:
        if _Helper.is_online(source='sync_topup_amount') is True and _Common.IDLE_MODE is True:
            s, r = _HTTPAccess.get_from_url(url=_url)
            if s == 200 and r['result'] == 'OK':
                _Common.TOPUP_AMOUNT_SETTING = r['data']
                _Common.store_to_temp_data('topup-amount-setting', json.dumps(r['data']))
                _KioskService.K_SIGNDLER.SIGNAL_GET_TOPUP_AMOUNT.emit('SYNC_TOPUP_AMOUNT|SUCCESS')
            else:
                _KioskService.K_SIGNDLER.SIGNAL_GET_TOPUP_AMOUNT.emit('SYNC_TOPUP_AMOUNT|FAILED')
        if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
            LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
            break
        sleep(333.3)


def get_amount(idx, listx):
    output = 0
    try:
        output = listx[idx]
    except IndexError:
        output = 0
    finally:
        return output


def start_check_bni_deposit():
    _Helper.get_thread().apply_async(check_bni_deposit)


def check_bni_deposit():
    # Triggered After Success Transaction
    LOGGER.info(('BNI DEPOSIT', _Common.BNI_SAM_1_WALLET, 'BNI THRESHOLD', _Common.BNI_THRESHOLD))
    if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
        _TopupService.TP_SIGNDLER.MANUAL_DEPOSIT_REFILL.emit('MEMULAI_TOPUP_DEPOSIT_BNI')
        _TopupService.do_topup_deposit_bni(slot=1)
    else:
        _TopupService.TP_SIGNDLER.MANUAL_DEPOSIT_REFILL.emit('DEPOSIT_BNI_MASIH_CUKUP')

