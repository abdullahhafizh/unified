__author__ = 'fitrah.wahyudi.imam@gmail.com'
import os
import sys
from _tTools import _Helper
from _dDAO import _DAO
from time import sleep
from _cConfig import _ConfigParser, _Common
from _nNetwork import _NetworkAccess, _SFTPAccess, _FTPAccess
import logging
from _sService import _KioskService
from _dDevice import _EDC
from _dDevice import _BILL
from _dDevice import _QPROX
# from operator import itemgetter
import json
from _sService import _UserService
from _sService import _SettlementService
from _sService import _TopupService
from _sService import _UpdateAppService
from datetime import datetime
from operator import itemgetter


LOGGER = logging.getLogger()
SETTING_PARAM = []


def start_check_connection(url, param):
    _Helper.get_thread().apply_async(check_connection, (url, param,))


def check_connection(url, param):
    global SETTING_PARAM
    SETTING_PARAM = param
    modulus = 0
    while True:
        modulus += 1
        try:
            status, response = _NetworkAccess.get_from_url(url=url, force=True)
            if status == 200:
                print('pyt: check_connection ' + _Helper.time_string() + ' Connected To Backend')
                _Common.KIOSK_STATUS = 'ONLINE'
                _KioskService.LAST_SYNC = _Helper.time_string()
            else:
                print('pyt: check_connection ' + _Helper.time_string() + ' Disconnected From Backend')
                _Common.KIOSK_STATUS = 'OFFLINE'
            if modulus == 1:
                print('pyt: check_connection ' + _Helper.time_string() + ' Setting Initiation From Backend')
                s, r = _NetworkAccess.post_to_url(url=_Common.BACKEND_URL + 'get/setting', param=SETTING_PARAM)
                _KioskService.update_kiosk_status(s, r)
                _DAO.create_today_report(_Common.TID)
            if _Common.DAILY_SYNC_SUMMARY_TIME in _Helper.time_string():
                send_daily_summary()
            # Add Daily Reboot Time Local Setting
            if _Common.DAILY_REBOOT_TIME in _Helper.time_string():
                LOGGER.info(('Trigger Daily Reboot Time (Countdown 30)', _Common.DAILY_REBOOT_TIME, _Helper.time_string()))            
                sleep(30)
                _KioskService.execute_command('shutdown -r -f -t 0')
                # _KioskService.kiosk_status()
        except Exception as e:
            LOGGER.debug(e)            
        sleep(59.9)


def send_daily_summary():
    _QPROX.ka_info_mandiri()
    sleep(1)
    _QPROX.ka_info_bni()
    sleep(1)
    payload = _DAO.get_today_report(_Common.TID)
    payload['last_stock_cash'] = _DAO.custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cash WHERE collectedAt is null ')[0]['__']
    payload['last_stock_slot_1'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 101 ')[0]['__']
    payload['last_stock_slot_2'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 102 ')[0]['__']
    payload['last_stock_slot_3'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 103 ')[0]['__']
    payload['last_stock_slot_4'] = _DAO.custom_query(' SELECT IFNULL(SUM(stock), 0) AS __ FROM ProductStock WHERE status = 104 ')[0]['__']
    # Move Into Each Daily Summary
    # payload['mandiri_deposit_last_balance'] = _Common.MANDIRI_ACTIVE_WALLET
    # payload['bni_deposit_last_balance'] = _Common.BNI_ACTIVE_WALLET
    url = _Common.BACKEND_URL + 'sync/daily-summary'
    if len(payload) > 0:
        _DAO.mark_today_report(_Common.TID)
        s, r = _NetworkAccess.post_to_url(url=url, param=payload)
        print('pyt: send_daily_summary ' + _Helper.time_string())
        if s != 200 or r.get('result') != 'OK':
            payload['endpoint'] = 'sync/daily-summary'
            _Common.store_request_to_job(name=_Helper.whoami(), url=url, payload=payload)


def start_idle_mode():
    _Helper.get_thread().apply_async(change_idle_mode, ('START',))


def stop_idle_mode():
    _Helper.get_thread().apply_async(change_idle_mode, ('STOP',))


def change_idle_mode(s):
    global IDLE_MODE
    if s == 'START':
        IDLE_MODE = True
        _UserService.USER = None
    elif s == 'STOP':
        IDLE_MODE = False


IDLE_MODE = True


def start_sync_machine_status():
    _Helper.get_thread().apply_async(sync_machine_status)


def sync_machine_status():
    __url = _Common.BACKEND_URL + 'kiosk/status'
    __param = dict()
    while True:
        try:
            if _Helper.is_online(source='sync_machine_status') is True and IDLE_MODE is True:
                __param = _KioskService.machine_summary()
                __param['on_usage'] = 'IDLE' if IDLE_MODE is True else 'ON_USED'
                # LOGGER.info((__url, str(__param)))
                print('pyt: sync_machine_status ' + _Helper.time_string() + ' Backend Trigger...')
                _NetworkAccess.post_to_url(url=__url, param=__param, custom_timeout=3)
            else:
                LOGGER.debug(('Sending Kiosk Status : ', str(IDLE_MODE)))
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(33.3)


def start_do_pending_request_job():
    _Helper.get_thread().apply_async(do_pending_request_job)


def do_pending_request_job():
    while True:
        pending_jobs = [f for f in os.listdir(_Common.JOB_PATH) if f.endswith('.request')]
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
                    __url = job['url']
                    __param = job['payload']
                    __endpoint = job['payload'].get('endpoint')
                    LOGGER.debug((p, __url, __param))
                    jobs_path_process = jobs_path.replace('.request', '.process')
                    os.rename(jobs_path, jobs_path_process)
                    status, response = _NetworkAccess.post_to_url(url=__url, param=__param)
                    print('pyt: [DEBUG] ' + ' '.join([p, _Helper.time_string(), str(status), str(response)]))
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
                    continue
            except Exception as e:
                LOGGER.warning(e)
        sleep(15.15)



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
                        result = _SFTPAccess.send_file(data['filename'], local_path=data['path_file'], remote_path=None)
                    elif host == 'MANDIRI_C2C':
                        result = _SFTPAccess.send_file(data['filename'], local_path=data['local_path'], remote_path=data['remote_path'])
                    else:
                        result = False
                    LOGGER.debug((p, host, data, result))
                    if result['success'] == True:
                        jobs_path_done = jobs_path_process.replace('.process_upload', '.done')
                        os.rename(jobs_path_process, jobs_path_done)
                        LOGGER.debug((jobs_path_process, jobs_path_done))
                    else:
                        jobs_path_reopen = jobs_path_process.replace('.process_upload', '.upload')
                        os.rename(jobs_path_process, jobs_path_reopen)
                    continue
            except Exception as e:
                LOGGER.warning(e)
        sleep(25.25)




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
            if _Helper.is_online(source='sync_topup_records') is True and IDLE_MODE is True:
                topup_records = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(topup_records) > 0:
                    print('pyt: sync_topup_records ' + _Helper.time_string() + ' Re-Sync Topup Records Data...')
                    for t in topup_records:
                        status, response = _NetworkAccess.post_to_url(url=url, param=t)
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
        sleep(44.5)


def start_sync_data_transaction():
    _Helper.get_thread().apply_async(sync_data_transaction)


def sync_data_transaction():
    url = _Common.BACKEND_URL + 'sync/transaction-topup'
    _table_ = 'Transactions'
    while True:
        try:
            if _Helper.is_online(source='sync_data_transaction') is True and IDLE_MODE is True:
                transactions = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(transactions) > 0:
                    print('pyt: sync_data_transaction ' + _Helper.time_string() + ' Re-Sync Transaction Data...')
                    for t in transactions:
                        status, response = _NetworkAccess.post_to_url(url=url, param=t)
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
        sleep(99.9)


def start_sync_data_transaction_failure():
    _Helper.get_thread().apply_async(sync_data_transaction_failure)


def sync_data_transaction_failure():
    url = _Common.BACKEND_URL + 'sync/transaction-failure'
    _table_ = 'TransactionFailure'
    while True:
        try:
            if _Helper.is_online(source='sync_data_transaction_failure') is True and IDLE_MODE is True:
                transaction_failures = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(transaction_failures) > 0:
                    print('pyt: sync_data_transaction_failure ' + _Helper.time_string() + ' Re-Sync Transaction Failure Data...')
                    for t in transaction_failures:
                        status, response = _NetworkAccess.post_to_url(url=url, param=t)
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
        sleep(99.9)


def start_sync_product_data():
    _Helper.get_thread().apply_async(sync_product_data)


def sync_product_data():
    url = _Common.BACKEND_URL + 'sync/product'
    _table_ = 'Product'
    while True:
        try:
            if _Helper.is_online(source='sync_product_data') is True and IDLE_MODE is True:
                products = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(products) > 0:
                    print('pyt: sync_product_data ' + _Helper.time_string() + ' Re-Sync Product Data...')
                    for p in products:
                        status, response = _NetworkAccess.post_to_url(url=url, param=p)
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
        sleep(55.5)


def start_sync_sam_audit():
    _Helper.get_thread().apply_async(sync_sam_audit)


def sync_sam_audit():
    url = _Common.BACKEND_URL + 'sync/sam-audit'
    _table_ = 'SAMAudit'
    while True:
        try:
            if _Helper.is_online(source='sync_sam_audit') is True and IDLE_MODE is True:
                audits = _DAO.not_synced_data(param={'syncFlag': 0}, _table=_table_)
                if len(audits) > 0:
                    print('pyt: sync_sam_audit ' + _Helper.time_string() + ' Re-Sync SAM Audit...')
                    for a in audits:
                        status, response = _NetworkAccess.post_to_url(url=url, param=a)
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
    _Helper.get_thread().apply_async(sync_settlement_data, (bank,))


def sync_settlement_data(bank):
    _url = _Common.SMT_CONFIG['full_url']
    # Do BNI Settlement Creation Every +- 15 Minutes
    _SettlementService.start_do_bni_topup_settlement()
    _table_ = 'Settlement'
    while True:
        try:
            if _Helper.is_online(source='sync_settlement_data') is True and IDLE_MODE is True:
                settlements = _DAO.custom_query(' SELECT * FROM ' + _table_ +
                                                ' WHERE status = "TOPUP_PREPAID|OPEN" AND createdAt > 1554783163354 ')
                if len(settlements) > 0:
                    print('pyt: sync_settlement_data ' + _Helper.time_string() + ' Re-Sync Settlement Data...')
                    for s in settlements:
                        _param = {
                            'mid': _Common.SMT_CONFIG['mid'],
                            'token': _Common.SMT_CONFIG['token'],
                            'tid': 'MDD-VM'+_Common.TID,
                            'path_file': os.path.join(sys.path[0], '_rRemoteFiles', s['filename']),
                            'filename': s['filename'],
                            'row': s['row'],
                            'amount': s['amount'],
                            'bank': bank,
                            'bid': _Common.BID[bank],
                            'settlement_created_at': datetime.fromtimestamp(s['createdAt']).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        status, response = _NetworkAccess.post_to_url(url=_url, param=_param)
                        if status == 200 and response['response']['code'] == 200:
                            _DAO.update_settlement({'sid': s['sid'], 'status': 'TOPUP_PREPAID|CLOSED'})
                            LOGGER.info(response)
                        else:
                            LOGGER.warning(response)
        except Exception as e:
            LOGGER.warning(e)
        finally:
            if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
                LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
                break
        sleep(888.8)


def start_sync_task():
    _Helper.get_thread().apply_async(sync_task)


def sync_task():
    _url = _Common.BACKEND_URL + 'task/check'
    while True:
        try:
            if _Helper.is_online(source='sync_task') is True and IDLE_MODE is True:
                status, response = _NetworkAccess.get_from_url(url=_url, log=False)
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
        sleep(33.3)


def start_sync_pending_refund():
    _Helper.get_thread().apply_async(sync_pending_refund)


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
                    s, r = _NetworkAccess.post_to_url(url=_url, param=_param)
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


def handle_tasks(tasks):
    if len(tasks) == 0:
        return
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
        if task['taskName'] == 'REBOOT':
            if IDLE_MODE is True:
                result = 'EXECUTED_INTO_MACHINE'
                _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('REBOOT')
                update_task(task, result)
                sleep(30)
                _KioskService.execute_command('shutdown -r -f -t 0')
            else:
                result = 'FAILED_EXECUTED_VM_ON_USED'
                update_task(task, result)
        if task['taskName'] == 'EDC_CLEAR_BATCH':
            result = _EDC.void_settlement_data()
            update_task(task, result)
        if task['taskName'] == 'EDC_SETTLEMENT':
            result = _EDC.backend_edc_settlement()
            update_task(task, result)
        if task['taskName'] in ['RESET_GRG', 'RESET_BILL']:
            if IDLE_MODE is True:
                _BILL.start_init_bill()
                result = 'EXECUTED_INTO_BILL'
            else:
                result = 'FAILED_EXECUTED_VM_ON_USED'
            update_task(task, result)
        if task['taskName'] == 'RESET_DB':
            result = _KioskService.reset_db_record()
            update_task(task, result)
        if 'DO_TOPUP_BNI_' in task['taskName']:
            _slot = int(task['taskName'][-1])
            result = _TopupService.do_topup_deposit_bni(slot=_slot, force=True)
            update_task(task, result)
        if task['taskName'] == 'DO_SETTLEMENT_MANDIRI':
            result = 'FAILED_EXECUTED_VM_ON_USED'
            if IDLE_MODE is True:
                _SettlementService.start_reset_mandiri_settlement()
                result = 'TRIGGERED_INTO_SYSTEM'
            update_task(task, result)
        if 'SAM_TO_SLOT_' in task['taskName']:
            _slot = task['taskName'][-1]
            result = _Common.sam_to_slot(_slot)
            update_task(task, result)
        if task['taskName'] == 'APP_UPDATE':
            result = _UpdateAppService.start_do_update()
            update_task(task, result)
            if result == 'APP_UPDATE|SUCCESS':
                _KioskService.execute_command('shutdown -r -f -t 0')
        if task['taskName'] == 'RESET_STOCK_PRODUCT':
            _DAO.clear_stock_product()
            update_task(task, 'RESET_STOCK_PRODUCT_SUCCESS')
        if task['taskName'] in ['UPDATE_STOCK_PRODUCT', 'REMOTE_UPDATE_STOCK']:
            result = sync_product_stock()
            update_task(task, result)
        if task['taskName'] == 'UPDATE_KIOSK':
            update_task(task)
            _url = _Common.BACKEND_URL + 'get/setting'
            LOGGER.info((_url, str(SETTING_PARAM)))
            s, r = _NetworkAccess.post_to_url(url=_url, param=SETTING_PARAM)
            # if s == 200 and r['result'] == 'OK':
            _KioskService.update_kiosk_status(s, r)
        if 'RESET_OFFLINE_USER|' in task['taskName']:
            __hash = task['taskName'].split('|')[1]
            result = _UserService.reset_offline_user(__hash)
            update_task(task, result)
        if 'HOUSE_KEEPING_' in task['taskName']:
            age_month = int(task['taskName'][-1])
            result = _KioskService.house_keeping(age_month)
            update_task(task, result)
        if task['taskName'] == 'REFRESH_PPOB_PRODUCT':
            result = 'TRIGGERED_INTO_SYSTEM'
            _Common.log_to_temp_config('last^get^ppob', '0')
            update_task(task, result)

    # Add Another TaskType


def update_task(task, result='TRIGGERED_TO_SYSTEM'):
    _url = _Common.BACKEND_URL + 'task/finish'
    task['result'] = result
    while True:
        status, response = _NetworkAccess.post_to_url(url=_url, param=task)
        if status == 200 and response['result'] == 'OK':
            break
        sleep(11.1)


def start_sync_product_stock():
    _Helper.get_thread().apply_async(sync_product_stock)


def sync_product_stock():
    _url = _Common.BACKEND_URL + 'get/product-stock'
    if _Helper.is_online(source='start_sync_product_stock') is True:
        s, r = _NetworkAccess.get_from_url(url=_url)
        if s == 200 and r['result'] == 'OK':
            products = r['data']
            products = sorted(products, key=itemgetter('status'))
            _DAO.flush_table('ProductStock')
            for product in products:
                if product['url_image'] is not None:
                    image_url = product['url_image']
                    download, image = _NetworkAccess.item_download(image_url, os.getcwd() + '/_qQml/source/card')
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
        if _Helper.is_online(source='sync_topup_amount') is True and IDLE_MODE is True:
            s, r = _NetworkAccess.get_from_url(url=_url)
            if s == 200 and r['result'] == 'OK':
                _Common.TOPUP_AMOUNT_SETTING = r['data']
                _Common.store_to_temp_data('topup-amount-setting', json.dumps(r['data']))
        if _Helper.whoami() not in _Common.ALLOWED_SYNC_TASK:
            LOGGER.debug(('[BREAKING-LOOP] ', _Helper.whoami()))
            break
        sleep(333.3)


# def parse_topup_data(topups):
#     topups = sorted(topups, key=itemgetter('name', 'sell_price'), reverse=True)
#     topup_provider = []
#     for topup in topups:
#         if topup['name'] not in topup_provider:
#             topup_provider.append(topup['name'])
#     list_amount = []
#     for topup in topups:
#         if topup['sell_price'] not in list_amount:
#             list_amount.append(topup['sell_price'])
#     topup_data = []
#     for provider in topup_provider:
#         _new_item = dict()
#         for x in range(len(topups)):
#             if provider == topups[x]['name']:
#                 _new_item['name'] = provider
#                 if topups[x]['sell_price'] == list_amount[0]:
#                     if _Common.TID == '110322':
#                         _new_item['bigDenom'] = 270
#                     else:
#                         _new_item['bigDenom'] = topups[x]['sell_price']
#                 if topups[x]['sell_price'] == list_amount[1]:
#                     if _Common.TID == '110322':
#                         _new_item['smallDenom'] = 170
#                     else:
#                         _new_item['smallDenom'] = topups[x]['sell_price']
#                 if topups[x]['sell_price'] == list_amount[2]:
#                     if _Common.TID == '110322':
#                         _new_item['tinyDenom'] = 17
#                     else:
#                         _new_item['tinyDenom'] = topups[x]['sell_price']
#         topup_data.append(_new_item)
#     return topup_data


def get_amount(idx, listx):
    output = 0
    try:
        output = listx[idx]
    except IndexError:
        output = 0
    finally:
        return output


# def start_automate_topup_bni():
#     _Tools.get_thread().apply_async(automate_topup_bni)
#
#
# def automate_topup_bni():
#     while True:
#         if IDLE_MODE is True and _Tools.is_online(source='automate_topup_bni') is True:
#             _QPROX.get_bni_wallet_status()
#             if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
#                 _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_1')
#                 _TopupService.do_topup_deposit_bni(slot=1)
#                 LOGGER.debug(('manual_topup_bni 1', str(_Common.BNI_SAM_1_WALLET), 'swap_to_slot 2'))
#                 _Common.BNI_ACTIVE = 2
#             if _Common.BNI_SAM_2_WALLET <= _Common.BNI_THRESHOLD:
#                 _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_2')
#                 _TopupService.do_topup_deposit_bni(slot=2)
#                 LOGGER.debug(('manual_topup_bni 2', str(_Common.BNI_SAM_2_WALLET), 'swap_to_slot 1'))
#                 _Common.BNI_ACTIVE = 1
#             _Common.save_sam_config()
#         sleep(900)


# def start_manual_trigger_topup_bni():
#     _Tools.get_thread().apply_async(manual_trigger_topup_bni)
#
#
# def manual_trigger_topup_bni():
#     while True:
#         if _Common.TRIGGER_MANUAL_TOPUP is True:
#             _Common.TRIGGER_MANUAL_TOPUP = False
#             if IDLE_MODE is True:
#                 _QPROX.get_bni_wallet_status()
#             if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
#                 _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_1')
#                 _TopupService.do_topup_deposit_bni(slot=1)
#                 LOGGER.debug(('manual_topup_bni 1', str(_Common.BNI_SAM_1_WALLET), 'swap_to_slot 2'))
#                 _Common.BNI_ACTIVE = 2
#             if _Common.BNI_SAM_2_WALLET <= _Common.BNI_THRESHOLD:
#                 _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_2')
#                 _TopupService.do_topup_deposit_bni(slot=2)
#                 LOGGER.debug(('manual_topup_bni 2', str(_Common.BNI_SAM_2_WALLET), 'swap_to_slot 1'))
#                 _Common.BNI_ACTIVE = 1
#             _Common.save_sam_config()
#         sleep(3.3)


def start_do_bni_topup_by_trx():
    _Helper.get_thread().apply_async(do_bni_topup_by_trx)


def do_bni_topup_by_trx():
    if _Common.BNI_SAM_1_WALLET <= _Common.BNI_THRESHOLD:
        _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_1')
        _TopupService.do_topup_deposit_bni(slot=1)
        if not _Common.BNI_SINGLE_SAM:
            LOGGER.debug(('topup_sam_bni 1', str(_Common.BNI_SAM_1_WALLET), str(_Common.BNI_THRESHOLD), '1 >>> 2'))
            _Common.BNI_ACTIVE = 2
        else:
            LOGGER.debug(('topup_sam_bni 1', str(_Common.BNI_SAM_1_WALLET), str(_Common.BNI_THRESHOLD)))
    elif _Common.BNI_SAM_2_WALLET <= _Common.BNI_THRESHOLD:
        _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.emit('INIT_TOPUP_BNI_2')
        _TopupService.do_topup_deposit_bni(slot=2)
        if not _Common.BNI_SINGLE_SAM:
            LOGGER.debug(('topup_sam_bni 2', str(_Common.BNI_SAM_2_WALLET), str(_Common.BNI_THRESHOLD), '2 >>> 1'))
            _Common.BNI_ACTIVE = 1
        else:
            LOGGER.debug(('topup_sam_bni 2', str(_Common.BNI_SAM_2_WALLET), str(_Common.BNI_THRESHOLD)))
    _Common.save_sam_config()

