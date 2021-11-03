__author__ = 'wahyudi@multidaya.id'

from _dDB import _Database
from _tTools import _Helper
# sql = 'UPDATE express SET TakeTime=:takeTime,SyncFlag = :syncFlag,Version = :version,Status = :status,staffTakenUser_id=:staffTakenUser_id WHERE id=:id'
# sql = 'INSERT INTO Express (id, ExpressNumber, expressType, overdueTime, status, StoreTime, SyncFlag, TakeUserPhoneNumber, ValidateCode, Version, box_id, logisticsCompany_id, mouth_id, operator_id, storeUser_id,groupName) VALUES (:id,:expressNumber,:expressType,:overdueTime,:status,:storeTime,:syncFlag,:takeUserPhoneNumber,:validateCode,:version,:box_id,:logisticsCompany_id,:mouth_id,:operator_id,:storeUser_id,:groupName)'


def init_kiosk():
    # must bring {tid:xxx} in param
    sql = "SELECT * FROM Terminal WHERE tid is not NULL"
    return _Database.get_query(sql=sql, parameter={})


def get_airport():
    sql = "SELECT prefix, name FROM Airport"
    return _Database.get_query(sql=sql, parameter={})


def insert_airport(param):
    # must bring prefix, name, desription in param
    sql = "INSERT INTO Airport (prefix, name, description) VALUES (:prefix, :name, :description)"
    return _Database.insert_update(sql=sql, parameter=param)


def get_bank_id(param):
    # must bring name, and status
    sql = "SELECT bankMid, bankTid FROM Bank WHERE name=:name AND status=:status"
    return _Database.get_query(sql=sql, parameter=param)


def insert_bank(param):
    # insert new bank details, must bring bid, name, status, bankMid, bankTid
    param['createdAt'] = _Helper.now()
    param['serviceList'] = "[]"
    sql = "INSERT INTO Bank (bid, name, status, serviceList, createdAt, bankMid, bankTid) " \
          "VALUES (:bid, :name, :status, :serviceList, :createdAt, :bankMid, :bankTid)"
    return _Database.insert_update(sql=sql, parameter=param)


def insert_transaction(param):
    """
      trxid           VARCHAR(100) PRIMARY KEY NOT NULL,
      tid             VARCHAR(100)             NOT NULL,
      mid             VARCHAR(100),
      pid             VARCHAR(100),
      tpid            VARCHAR(100),
      amount          BIGINT,
      sale            BIGINT,
      cardNo          VARCHAR(100),
      paymentType     VARCHAR(150),
      paymentNotes    TEXT,
      bankTid         VARCHAR(100),
      bankMid         VARCHAR(100),
      isCollected     INT,
      pidStock        VARCHAR(100),
    """
    param["bankTid"] = ""
    param["bankMid"] = ""
    param["createdAt"] = _Helper.now()
    param["syncFlag"] = 0
    sql = "INSERT INTO Transactions ( trxid, tid, mid, pid, tpid, paymentType, amount, sale, createdAt, syncFlag, " \
          "bankMid, bankTid, paymentNotes, cardNo, isCollected, pidStock ) VALUES ( :trxid, :tid, :mid, :pid, :tpid, :paymentType, :amount, " \
          ":sale, :createdAt, :syncFlag, :bankMid, :bankTid, :paymentNotes, :cardNo, :isCollected, :pidStock )"
    return _Database.insert_update(sql=sql, parameter=param)


def insert_transaction_new(param):
    """
      trxId           VARCHAR(100) PRIMARY KEY NOT NULL,
      tid             VARCHAR(100)             NOT NULL,
      mid             VARCHAR(100),
      amount          BIGINT,
      baseAmount      BIGINT,
      adminFee        BIGINT,
      trxType         VARCHAR(100),
      cardNo          VARCHAR(100),
      paymentType     VARCHAR(150),
      paymentNotes    TEXT,
      productName     VARCHAR(100),
      productId       VARCHAR(100),
      traceNo         VARCHAR(100),
      targetCard      VARCHAR(100),
      bankId          VARCHAR(2)
      syncFlag        INT,
      trxNotes        TEXT,
      createdAt       BIGINT
    """
    param["syncFlag"] = 0
    sql = "INSERT INTO TransactionsNew ( trxId, tid, mid, amount, baseAmount, adminFee, trxType, cardNo, paymentType, " \
          "paymentNotes, productName, productId, traceNo, targetCard, bankId, syncFlag, trxNotes, createdAt ) VALUES ( :trxId, :tid, :mid, :amount, :baseAmount, :adminFee, :trxType, " \
          ":cardNo, :paymentType, :paymentNotes, :productName, :productId, :traceNo, :targetCard, :bankId, :syncFlag, :trxNotes, :createdAt )"
    return _Database.insert_update(sql=sql, parameter=param, log=False)


def insert_transaction_failure(param):
    """
      trxid           VARCHAR(100) PRIMARY KEY NOT NULL,
      tid             VARCHAR(100)             NOT NULL,
      mid             VARCHAR(100),
      pid             VARCHAR(100),
      amount          BIGINT,
      cardNo          VARCHAR(100),
      failureType     VARCHAR(255),
      paymentMethod   VARCHAR(255),
      createdAt       BIGINT,
      syncFlag        INT,
      remarks         TEXT
    """
    param["createdAt"] = _Helper.now()
    param["syncFlag"] = 0
    sql = "INSERT INTO TransactionFailure (trxid, tid, mid, pid, amount, cardNo, createdAt, syncFlag, " \
          "failureType, paymentMethod, remarks) VALUES (:trxid, :tid, :mid, :pid, :amount, :cardNo, " \
          ":createdAt, :syncFlag, :failureType, :paymentMethod, :remarks)"
    return _Database.insert_update(sql=sql, parameter=param)


def get_transaction_failure(param):
    """
      reff_no         VARCHAR(100) PRIMARY KEY NOT NULL,
      tid             VARCHAR(100)             NOT NULL,
    """
    sql = "SELECT * FROM TransactionFailure WHERE trxid LIKE '%{}' AND tid = '{}' ".format(param['reff_no'], param['tid'])
    return _Database.get_query(sql=sql, parameter={})


def delete_transaction_failure(param):
    """
      reff_no           VARCHAR(100) PRIMARY KEY NOT NULL,
      tid             VARCHAR(100)             NOT NULL,
    """
    condition = " trxid LIKE '%{}' AND tid = '{}' ".format(param['reff_no'], param['tid'])
    flush_table('TransactionFailure', condition)


def update_transaction(param):
    """
      trxid           VARCHAR(100) PRIMARY KEY NOT NULL,
      amount          BIGINT,
      paymentNotes    VARCHAR(255)
    """
    param["syncFlag"] = 0
    sql = "UPDATE Transactions SET amount=:amount, syncFlag=:syncFlag, paymentNotes=:paymentNotes WHERE trxid=:trxid "
    return _Database.insert_update(sql=sql, parameter=param)


def mark_sync(param, _table, _key, _syncFlag=1):
    """
    :param param: syncFlag, trxid
    :return: _Database.insert_update
    """
    sql = "UPDATE " + str(_table) + " SET syncFlag=" + str(_syncFlag) + "  WHERE " + str(_key) + "=:key"
    return _Database.insert_update(sql=sql, parameter=param)


def insert_cash(param):
    """
	`csid`	VARCHAR(100) NOT NULL,
	`tid`	VARCHAR(100) NOT NULL,
	`pid`   VARCHAR(100),
	`amount`	BIGINT NOT NULL,
    :param param: _Database.insert_update
    :return:
    """
    param["createdAt"] = _Helper.now()
    sql = "INSERT INTO Cash (csid, tid, amount, pid, createdAt) VALUES (:csid, :tid, :amount, :pid, :createdAt)"
    return _Database.insert_update(sql=sql, parameter=param)


def update_cash(param):
    """
    'csid'
    'amount'
    'updatedAt'
    :param param:
    :return:
    """
    param["updatedAt"] = _Helper.now()
    sql = "UPDATE Cash SET amount=:amount, updatedAt=:updatedAt WHERE csid=:csid"
    return _Database.insert_update(sql=sql, parameter=param)


def collect_cash(param):
    """
    :param param:
    'csid'
    'collectedAt'
    'collectedUser'
    :return: _Database.insert_update
    """
    param["updatedAt"] = _Helper.now()
    sql = "UPDATE Cash SET updatedAt=:updatedAt, collectedAt=:collectedAt, collectedUser=:collectedUser" \
          " WHERE csid=:csid"
    return _Database.insert_update(sql=sql, parameter=param)


def list_uncollected_cash():
    sql = "SELECT * FROM Cash Where collectedAt is Null"
    return _Database.get_query(sql=sql, parameter={})


def mark_uncollected_cash(param):
    """
    :param param:
    'collectedAt'
    'collectedUser'
    :return: _Database.insert_update
    """
    param["updatedAt"] = _Helper.now()
    sql = " UPDATE Cash SET updatedAt = :updatedAt, collectedAt = :collectedAt, collectedUser = :collectedUser Where collectedAt is Null "
    return _Database.insert_update(sql=sql, parameter=param)


def insert_product(param):
    '''
    :param param:
    pid             VARCHAR(100) PRIMARY KEY NOT NULL,
    name            VARCHAR(150)             NOT NULL,
    bid             INT             NOT NULL,
    price           BIGINT,
    details         TEXT,
    status          INT,
    :return:
    '''
    param["createdAt"] = _Helper.now()
    param["syncFlag"] = 0
    sql = "INSERT INTO Product (pid, bid, name, price, details, status, createdAt, syncFlag) VALUES " \
          "(:pid, :bid, :name, :price, :details, :status, :createdAt, :syncFlag)"
    return _Database.insert_update(sql=sql, parameter=param)


def update_product_status(param):
    '''
    :param param: pid, status
    :return:
    '''
    sql = "UPDATE Product SET status=:status WHERE pid=:pid"
    return _Database.insert_update(sql=sql, parameter=param)


def update_product_price(param):
    '''
    :param param: pid, price
    :return:
    '''
    sql = "UPDATE Product SET price=:price WHERE pid=:pid"
    return _Database.insert_update(sql=sql, parameter=param)


def insert_settlement(param):
    '''
    :param param:
    `sid`	VARCHAR(100) NOT NULL,
	`tid`	VARCHAR(100) NOT NULL,
	`bid`	VARCHAR(100),
	`filename`	VARCHAR(255),
	`status` VARCHAR,
	`amount`	BIGINT,
	`trx_type`	VARCHAR(100),
	`remarks`	TEXT,
	`row`	BIGINT,
    :return:
    '''
    param["createdAt"] = _Helper.now()
    if _Helper.empty(param["remarks"]):
        param["remarks"] = ""
    if _Helper.empty(param["trx_type"]):
        param["trx_type"] = ""
    sql = "INSERT INTO Settlement (sid, tid, bid, filename, status, amount, trx_type, remarks, row, createdAt) VALUES (:sid, :tid, :bid, " \
          ":filename, :status, :amount, :trx_type, :remarks, :row, :createdAt)"
    return _Database.insert_update(sql=sql, parameter=param)


def update_settlement(param):
    '''
    :param param:
    `sid`	VARCHAR(100) NOT NULL,
    `status` VARCHAR,
    `updatedAt`
    :return:
    '''
    param["updatedAt"] = _Helper.now()
    sql = "UPDATE Settlement SET status=:status, updatedAt=:updatedAt WHERE sid=:sid"
    return _Database.insert_update(sql=sql, parameter=param)


def insert_product_stock(param):
    '''
  stid            VARCHAR(100) PRIMARY KEY NOT NULL,
  pid             VARCHAR(100)             NOT NULL,
  bid             INT          DEFAULT 1,
  tid             VARCHAR(100),
  name            VARCHAR(255),
  init_price      INT,
  sell_price      INT,
  remarks         TEXT,
  stock           INT,
  status          INT,
  createdAt       BIGINT,
  updatedAt       BIGINT, -> This Field is removed in Main Server, replaced to lastUserUpdate
  syncFlag        INT
    '''
    param["createdAt"] = _Helper.now()
    param["syncFlag"] = 1
    sql = "INSERT INTO ProductStock (stid, pid, bid, tid, name, init_price, sell_price, remarks, stock, status, " \
          "createdAt, syncFlag) VALUES (:stid, :pid, :bid, :tid, :name, :init_price, :sell_price, :remarks, :stock, " \
          ":status, :createdAt, :syncFlag) "
    return _Database.insert_update(sql=sql, parameter=param, log=False)


def update_product_stock(param):
    '''
      pid             VARCHAR(100)             NOT NULL,
      stock           INT,
    :param param:
    :return:
    '''
    param["updatedAt"] = _Helper.now()
    sql = " UPDATE ProductStock SET stock = :stock WHERE pid = :pid "
    return _Database.insert_update(sql=sql, parameter=param, log=True)


def get_product_stock():
    sql = " SELECT * FROM ProductStock WHERE status > 1 "
    return _Database.get_query(sql=sql, parameter={})


def get_product_stock_by_slot_status(status):
    sql = " SELECT stock FROM ProductStock WHERE status = {} ".format(str(status))
    return _Database.get_query(sql=sql, parameter={})


def check_product_stock(param):
    sql = " SELECT count(*) as count FROM ProductStock WHERE stid = :stid AND pid = :pid LIMIT 0,1 "
    return _Database.get_query(sql=sql, parameter=param)


def check_product_status_by_pid(param):
    sql = " SELECT * FROM ProductStock WHERE pid = :pid LIMIT 0,1 "
    return _Database.get_query(sql=sql, parameter=param)


def clear_stock_product():
    flush_table('ProductStock')


def get_airport_name(param):
    '''
    :param param: prefix1 = CGK, prefix2=DPS
    :return: Soekarno-Hatta International Airport
    '''
    sql = "SELECT name FROM Airport where prefix=:prefix"
    return _Database.get_query(sql=sql, parameter=param)


def not_synced_data(param, _table):
    sql = "SELECT * FROM " + _table + " WHERE syncFlag = :syncFlag"
    return _Database.get_query(sql=sql, parameter=param)


def insert_transaction_type(param):
    '''
    :param param:
    tpid            VARCHAR(100) PRIMARY KEY NOT NULL,
    name            VARCHAR(150)             NOT NULL,
    status          INT,
    description     VARCHAR(255),
    createdAt       BIGINT,
    syncFlag        INT
    :return:
    '''
    param['syncFlag'] = 0
    param['createdAt'] = _Helper.now()
    sql = "INSERT INTO TransactionType(tpid, name, status, description, createdAt, syncFlag) " \
          "VALUES(:tpid, :name, :status, :description, :createdAt, :syncFlag)"
    return _Database.insert_update(sql=sql, parameter=param)


def get_tpid(param):
    sql = 'SELECT * FROM TransactionType WHERE name like "%{}%" ORDER BY name ASC LIMIT 0,1 '.format(param['string'])
    return _Database.get_query(sql=sql, parameter=param)


def get_airport_terminal(param):
    sql = 'SELECT terminal FROM AirportTerminal WHERE origin=:origin and destination=:destination and ' \
          'flight_name=:flight '
    return _Database.get_query(sql=sql, parameter=param)


def update_kiosk_data(param):
    # sql = ' INSERT INTO `Terminal`(`tid`,`name`,`locationId`,`status`,`token`,`defaultMargin`, `defaultAdmin`) ' \
    #     'VALUES (:tid, :name, :locationId, :status, :token, :defaultMargin, :defaultAdmin ) '
    delete = ' DELETE FROM `Terminal` WHERE tid <> "'+param['tid']+'"'
    _Database.delete_row(sql=delete)
    insert = ' INSERT OR IGNORE INTO `Terminal`(`tid`,`name`,`locationId`,`status`,`token`,`defaultMargin`, `defaultAdmin`) ' \
            ' VALUES (:tid, :name, :locationId, :status, :token, :defaultMargin, :defaultAdmin);'
    result_insert = _Database.insert_update(sql=insert, parameter=param)
    update = ' UPDATE `Terminal` SET name=:name, locationId=:locationId, status=:status, token=:token, defaultMargin=:defaultMargin, defaultAdmin=:defaultAdmin ' \
            ' WHERE tid=:tid '
    result_update = _Database.insert_update(sql=update, parameter=param)
    return {
        'insert': result_insert,
        'update': result_update
    }


def flush_table(_table, _where=None):
    if _where is None:
        sql = ' DELETE FROM {} '.format(_table)
    else:
        sql = ' DELETE FROM {} WHERE {} '.format(_table, _where)
    _Database.delete_row(sql=sql)


def adjust_table(_path):
    _Database.adjust_db(db=_path)


def direct_adjust_table(script):
    return _Database.adjust_db_direct(script)


def insert_receipt(param):
    param['syncFlag'] = 0
    '''
    rid,
    bookingCode,
    tid,
    receiptRaw,
    receiptData,
    createdAt,
    '''
    sql = "  INSERT INTO Receipts(rid, bookingCode, tid, receiptRaw, receiptData, syncFlag, createdAt) " \
          "VALUES(:rid, :bookingCode, :tid, :receiptRaw, :receiptData, :syncFlag, :createdAt)  "
    return _Database.insert_update(sql=sql, parameter=param)


def search_receipt(param):
    '''

    :param param:
    booking_code
    :return:
    1 full row
    '''

    sql = " SELECT * FROM Receipts WHERE bookingCode = :bookingCode ORDER BY createdAt ASC LIMIT 0,1 "
    return _Database.get_query(sql=sql, parameter=param)


def check_table(param):
    sql = " SELECT count(*) FROM {} ".format(param['table'])
    return _Database.get_query(sql=sql, parameter={})


def check_trx_new(trxid):
    sql = " SELECT * FROM TransactionsNew WHERE trxid = '{}' ".format(trxid)
    return _Database.get_query(sql=sql, parameter={})


def check_trx(trxid):
    sql = " SELECT * FROM Transactions WHERE trxid = '{}' ".format(trxid)
    return _Database.get_query(sql=sql, parameter={})


def check_trx_failure(trxid):
    sql = " SELECT * FROM TransactionFailure WHERE trxid = '{}' ".format(trxid)
    return _Database.get_query(sql=sql, parameter={})


def check_product(pid):
    sql = " SELECT * FROM Product WHERE pid = '{}' ".format(pid)
    return _Database.get_query(sql=sql, parameter={})


def check_settlement(status='EDC|OPEN'):
    sql = " SELECT * FROM Settlement WHERE status = '{}' ".format(status)
    return _Database.get_query(sql=sql, parameter={})


def insert_topup_record(param):
    '''

    :param param:
    :return:
    '''
    param['syncFlag'] = 0
    param['createdAt'] = _Helper.now()
    sql = " INSERT INTO TopUpRecords(rid, trxid, cardNo, balance, reportSAM, reportKA, status, remarks, " \
          "syncFlag, createdAt) VALUES (:rid, :trxid, :cardNo, :balance, :reportSAM, :reportKA, :status, :remarks, " \
          ":syncFlag, :createdAt) "
    return _Database.insert_update(sql=sql, parameter=param)


def insert_sam_record(param):
    '''
      smid            VARCHAR(100) PRIMARY KEY NOT NULL,
      fileName        TEXT,
      fileContent     TEXT,
      status          INT,
      remarks         TEXT,
    :param param:
    :return:
    '''
    param['createdAt'] = _Helper.now()
    sql = " INSERT INTO SAMRecords(smid, fileName, fileContent, status, remarks, createdAt) VALUES (:smid, :fileName, " \
          " :fileContent, :status, :remarks, :createdAt) "
    return _Database.insert_update(sql=sql, parameter=param)


def get_total_count(table, condition=None):
    sql = ' SELECT count(*) as total FROM ' + table
    if condition is not None:
        sql += ' WHERE ' + condition
    result = _Database.get_query(sql=sql, parameter={}, log=False)
    if len(result) > 0:
        return result[0].get('total', 0)
    else:
        return 0


def get_query_from(table, condition=None):
    sql = ' SELECT * FROM ' + table
    if condition is not None:
        sql += ' WHERE ' + condition
    return _Database.get_query(sql=sql, parameter={}, log=False)


def custom_query(sql):
    return _Database.get_query(sql=sql, parameter={}, log=False)


def custom_update(sql):
    return _Database.insert_update(sql=sql, parameter={}, log=False)


def insert_sam_audit(param):
    sql = ' INSERT INTO SAMAudit(lid, trxid, samCardNo, samCardSlot, samPrevBalance, samLastBalance, topupCardNo, ' \
          'topupPrevBalance, topupLastBalance, status, remarks, syncFlag, createdAt) VALUES (:lid, :trxid, :samCardNo,'\
          ':samCardSlot, :samPrevBalance, :samLastBalance, :topupCardNo, :topupPrevBalance, :topupLastBalance, :status,'\
          ':remarks, :syncFlag, :createdAt) '
    param['syncFlag'] = 0
    param['createdAt'] = _Helper.now()
    return _Database.insert_update(sql=sql, parameter=param)


def clean_old_data(tables, key='', age_month=0):
    if type(tables) != list or len(tables) == 0 or len(key) == 0 or age_month == 0:
        return False
    expired = _Helper.now()
    if age_month > 0:
        expired = _Helper.now() - (age_month * 30 * 24 * 60 * 60 * 1000)
    for t in tables:
        w = str(key) + ' < ' + str(expired)
        flush_table(_table=t, _where=w)
    return True

# CREATE TABLE PendingRefund
#   id              VARCHAR(100) PRIMARY KEY NOT NULL,
#   tid             VARCHAR(100)             NOT NULL,
#   trxid           VARCHAR(100),
#   amount          BIGINT,
#   customer        VARCHAR(100),
#   refundType      VARCHAR(100),
#   paymentType     VARCHAR(100),
#   isSuccess       INT,
#   remarks         TEXT,
#   createdAt       BIGINT

def get_pending_refund():
    return get_query_from('PendingRefund', condition='isSuccess = 0')

def insert_pending_refund(param):
    '''
    :param param:
    id
    tid             VARCHAR(100),
    trxid           VARCHAR(100),
    amount          BIGINT,
    customer        VARCHAR(100),
    channel         VARCHAR(100),
    refundType      VARCHAR(100),
    paymentType     VARCHAR(100),
    remarks         TEXT,
    :return:
    '''
    param['id'] = _Helper.uuid()
    param['isSuccess'] = 0
    param['createdAt'] = _Helper.now()
    sql = " INSERT INTO PendingRefund(id, tid, trxid, amount, customer, channel, refundType, paymentType, remarks, isSuccess, createdAt ) " \
          "VALUES(:id, :tid, :trxid, :amount, :customer, :channel, :refundType, :paymentType, :remarks, :isSuccess, :createdAt ) "
    return _Database.insert_update(sql=sql, parameter=param)

def update_pending_refund(param):
    '''
    trxid          VARCHAR(100),
    remarks        TEXT,
    :param param:
    :return:
    '''
    param["updatedAt"] = _Helper.now()
    sql = " UPDATE PendingRefund SET isSuccess=1, updatedAt=:updatedAt, remarks=:remarks  WHERE trxid=:trxid "
    return _Database.insert_update(sql=sql, parameter=param) 


def update_daily_summary(param):
    """
    param must contains :
    key
    value
    report_date
    """
    sql = " UPDATE DailySummary SET {key} = {key} + {value}  WHERE report_date = :report_date ".format(key = param['key'], value = param['value'])
    return _Database.insert_update(sql=sql, parameter=param) 


def update_today_summary(key, value):
    today = _Helper.time_string(f='%Y-%m-%d')
    return update_summary_by_date(key, value, today)


def update_summary_by_date(key, value, date):
    param = {
        'report_date': date,
        'key': key,
        'value': value
    }
    return update_daily_summary(param)


def create_today_report(tid):
    param = {
        'report_date': _Helper.time_string(f='%Y-%m-%d'),
        'tid': tid
    }
    sql = " INSERT INTO DailySummary (tid, report_date) SELECT :tid, :report_date WHERE NOT EXISTS ( SELECT * FROM DailySummary WHERE tid = :tid AND report_date = :report_date ) "
    return _Database.insert_update(sql=sql, parameter=param)


def update_today_summary_multikeys(keys=[], value=0):
    return update_summary_multikeys(keys=keys, value=value)


def update_summary_multikeys(keys=[], value=0, report_date=None):
    if report_date is None:
        report_date = _Helper.time_string(f='%Y-%m-%d')
    param = {
        'report_date': report_date
    }
    sql = " UPDATE DailySummary SET "
    for key in keys:
        if key in ['mandiri_deposit_last_balance', 'bni_deposit_last_balance']:
            sql += ' '.join([key, '=', str(value)])
            continue
        if key == keys[0]:
            sql += ' '.join([key, '=', key, '+', str(value)])
        else:
            sql += ' '.join([',', key, '=', key, '+', str(value)])
    sql += " WHERE report_date = :report_date "
    return _Database.insert_update(sql=sql, parameter=param, log=True)


def get_today_report(tid):
    param = {
        'tid': tid,
        'report_date': _Helper.time_string(f='%Y-%m-%d')
    }
    sql = " SELECT * FROM DailySummary WHERE tid = :tid AND report_date = :report_date AND synced_at IS NULL  "
    result = _Database.get_query(sql=sql, parameter=param)
    if len(result) > 0:
        result = result[0]
    return result


def mark_today_report(tid):
    param = {
        'tid': tid,
        'report_date': _Helper.time_string(f='%Y-%m-%d'),
        'synced_at': _Helper.time_string()        
    }
    sql = " UPDATE DailySummary SET synced_at = :synced_at WHERE tid =:tid AND report_date = :report_date "
    result = _Database.get_query(sql=sql, parameter=param)
    if len(result) > 0:
        result = result[0]
    return result


def truncate_cashbox():
    flush_table('Cashbox')


def insert_cashbox(amount='0'):
    param = {
        'amount': int(amount),
        'createdAt': _Helper.time_string()
    }
    sql = " INSERT INTO Cashbox (amount, createdAt) VALUES (:amount, :createdAt) "
    return _Database.insert_update(sql=sql, parameter=param, log=False)


def cashbox_status():
    return custom_query(' SELECT IFNULL(SUM(amount), 0) AS __  FROM Cashbox ')[0]['__']


def cashbox_history():
    return custom_query(' SELECT group_concat(cash_data, "\n") as __ FROM ( SELECT createdAt || "," || amount AS cash_data FROM CashBox) ' )