__author__ = 'wahyudi@multidaya.id'

from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidLog as LOG

import datetime
import json
import os
import sys

SLOT_KA = ""
COM_PORT = None
LOAD_DLL = False

COM_PORT = None
COM_BAUDRATE = None

DUMP_FOLDER = sys.path[0] + '/_dDump/'
if not os.path.exists(DUMP_FOLDER):
    os.makedirs(DUMP_FOLDER)

# Log File Dump
def log_to_file(content='', filename='', default_ext='.dump'):
    path = DUMP_FOLDER
    if '.' not in filename:
        filename = filename + default_ext
    path_file = os.path.join(path, filename)
    if type(content) == bytes:
        content = content.decode('cp1252')
    with open(path_file, 'w') as file_logging:
        print('pyt: Create Dump File : ' + path_file)
        for line in content.split('\n'):
            file_logging.write(line)
            file_logging.write('\n')
        file_logging.close()
    return path_file

# ST0
def reset_contactless(__global_response__=None):
    res_str = prepaid.topup_card_disconnect()
    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("ST0:Result = ", res_str)
        LOG.fw("ST0:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("ST0:Result = ", res_str, True)
        LOG.fw("ST0:Gagal", None, True)
    return res_str

# RD0
def reader_dump(param, __global_response__=None):
    Param = param.split('|')
    if len(Param) > 1:
        card_no = Param[0]
        trxid = Param[1]
    res_str, dump_data = prepaid.reader_dump(card_no, trxid)
    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        if len(dump_data) > 0:
            # Write To File Here
            reff = '_'.join([card_no, trxid])
            dump_file = log_to_file(dump_data, reff)
            __global_response__["Response"]= dump_file
        LOG.fw("RD0:Result = ", res_str)
        LOG.fw("RD0:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("RD0:Result = ", res_str, True)
        LOG.fw("RD0:Gagal", None, True)
    return res_str



# RD1
def enable_reader_dump(__global_response__=None):
    res_str = prepaid.enable_reader_dump()
    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("RD1:Result = ", res_str)
        LOG.fw("RD1:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("RD1:Result = ", res_str, True)
        LOG.fw("RD1:Gagal", None, True)
    return res_str


# RD2
def disable_reader_dump(__global_response__=None):
    res_str = prepaid.disable_reader_dump()
    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("RD2:Result = ", res_str)
        LOG.fw("RD2:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("RD2:Result = ", res_str, True)
        LOG.fw("RD2:Gagal", None, True)
    return res_str



#000
def open_only(param=None, __global_response__=None):
    global COM_PORT, COM_BAUDRATE
    
    if LOAD_DLL is True:
        prepaid.load_dll()
        
    if param is not None:
        Param = param.split('|')
        if len(Param) > 1:
            C_PORT = Param[0].encode('utf-8')
            LOG.fw("000:Parameter Port = ", C_PORT)
            COM_BAUDRATE = int(Param[1])
            COM_PORT = C_PORT
    else:
        C_PORT = ""

    if C_PORT == "":
        if COM_PORT is None:
            raise SystemError("No Global Configuration For COM_PORT")
        else:
            C_PORT = COM_PORT

    res_str = prepaid.open_only(C_PORT, COM_BAUDRATE)

    if __global_response__ != None and type(__global_response__) == dict:
        __global_response__["Result"] = res_str
        if res_str == "0000":
            __global_response__["ErrorDesc"] = "Sukses"
            LOG.fw("000:Result = ", res_str)
            LOG.fw("000:Sukses")
        else:
            __global_response__["ErrorDesc"] = "Gagal"
            LOG.fw("000:Result = ", res_str, True)
            LOG.fw("000:Gagal", None, True)
    return res_str

#001
def init_topup(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 4:
        C_PORT = Param[0].encode('utf-8')
        C_SAMPIN = Param[1].encode('utf-8')
        C_Institution =Param[2].encode('utf-8')
        C_Terminal = Param[3].encode('utf-8')
    else:
        LOG.fw("001:Missing Parameter", param)
        raise SystemError("001:Missing Parameter: "+param)

    LOG.fw("001:Parameter = ", C_PORT)
    LOG.fw("001:Parameter = ", C_SAMPIN)
    LOG.fw("001:Parameter = ", C_Institution)
    LOG.fw("001:Parameter = ", C_Terminal)

    serial = b"0123456789abcdef"
    passd = b"01234567"

    res_str = prepaid.topup_init(C_PORT, C_SAMPIN, C_Institution, C_Terminal, serial, passd)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("001:Result = ", res_str)
        LOG.fw("001:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("001:Result = ", res_str, True)
        LOG.fw("001:Gagal", None, True)
    return res_str

#002
def auth_ka(param, __global_response__):
    global SLOT_KA
    Param = param.split('|')
    C_PORT = Param[0].encode('utf-8')
    C_SLOT = Param[1].encode('utf-8')
    C_PinSAM = Param[2].encode('utf-8')
    C_Institution =Param[3].encode('utf-8')
    C_Terminal = Param[4].encode('utf-8')
    C_PinKA = Param[5].encode('utf-8')
    C_PinKL = Param[6].encode('utf-8')

    LOG.fw("002:Parameter = ", C_PORT)
    LOG.fw("002:Parameter = ", C_SLOT)
    LOG.fw("002:Parameter = ", C_PinSAM)
    LOG.fw("002:Parameter = ", C_Institution)
    LOG.fw("002:Parameter = ", C_Terminal)
    LOG.fw("002:Parameter = ", C_PinKA)
    LOG.fw("002:Parameter = ", C_PinKL)


    serial = b"0123456789abcdef"
    passd = b"01234567"

    res_str, NIKKL = prepaid.topup_auth(C_PORT, C_SLOT, C_PinSAM, C_Institution, C_Terminal, C_PinKA, C_PinKL)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        SLOT_KA = C_SLOT
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"]= NIKKL
        LOG.fw("002:Response = ", NIKKL)

        LOG.fw("002:Result = ", res_str)
        LOG.fw("002:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("002:Result = ", res_str, True)
        LOG.fw("002:Gagal", None, True)
    return res_str

#003-1 / 012-3
def balance_with_sn(param, __global_response__):
    res_str = open_only()
    if res_str != "0000":
        raise SystemError("COM Open Fail: "+res_str)

    Param = param.split('|')
    if len(Param) == 1:
        C_Denom = Param[0].encode('utf-8')
    else:
        LOG.fw("003:Missing Parameter", param)
        raise SystemError("003:Missing Parameter: "+param)

    LOG.fw("003:Parameter = ", C_Denom)

    res_str, balance_value, card_number, sign = prepaid.topup_balance_with_sn()

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = balance_value + "|" + card_number + "|" + sign
        LOG.fw("003:Response = ", balance_value)
        LOG.fw("003:Response = ", card_number)
        LOG.fw("003:Response = ", sign)

        LOG.fw("003:Result = ", res_str)
        LOG.fw("003:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("003:Result = ", res_str, True)
        LOG.fw("003:Gagal", None, True)
    return res_str

#004
def topup(param, __global_response__):
    raise SystemError("KA Type, deprecated")

    # res, balance_value, card_number, sign = prepaid.topup_balance_with_sn()

    # res_str = format(res, 'x')
    # if len(res_str) < 4 :
    #     res_str = res_str.zfill(4)
    # __global_response__["Result"] = res_str

    # if res == 0:
    #     __global_response__["ErrorDesc"] = "Sukses"
    #     __global_response__["Response"] = balance_value + "|" + card_number + "|" + sign
    # else:
    #     __global_response__["ErrorDesc"] = "Gagal"

    # return res_str

#008
def debit(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 1:
        C_Denom = Param[0].encode('utf-8')
    else:
        LOG.fw("008:Missing Parameter", param)
        raise SystemError("008:Missing Parameter: "+param)

    LOG.fw("008:Parameter = ", C_Denom)

    date_now = datetime.datetime.now().strftime("%d%m%y%H%M%S").encode("utf-8")
    timeout = b"5"

    res_str, error_str, C_Balance,C_ReportSAM, C_TypeBank = prepaid.topup_debit(C_Denom, date_now, timeout)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = C_Balance + "|" + C_ReportSAM + "|" + C_TypeBank

        LOG.fw("008:Response = ", C_Balance)
        LOG.fw("008:Response = ", C_ReportSAM)
        LOG.fw("008:Response = ", C_TypeBank)

        LOG.fw("008:Result = ", res_str)
        LOG.fw("008:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("008:Response = ", error_str, True)
        LOG.fw("008:Result = ", res_str, True)
        LOG.fw("008:Gagal", None, True)
    return res_str

#009
def balance(param, __global_response__):
    # LOG.tracing("Enter Common: ", "balance")
    res_str = open_only()
    if res_str != "0000":
        raise SystemError("COM Open Fail: "+res_str)

    res_str, C_Balance = prepaid.topup_balance()

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = C_Balance 
        
        LOG.fw("009:Response = ", C_Balance)

        LOG.fw("009:Result = ", res_str)
        LOG.fw("009:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("009:Result = ", res_str, True)
        LOG.fw("009:Gagal", None, True)
    return res_str

#000
def done(param, __global_response__):
    res_str = prepaid.topup_done()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("done:Result = ", res_str)
        LOG.fw("done:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("done:Result = ", res_str, True)
        LOG.fw("done:Gagal", None, True)
    return res_str

#020
def get_purse_data(param, __global_response__):
    Param = param.split('|')
    # Empty String Will Have Less Than 2 Param
    if len(Param) < 2:
        # Set Back to Old Command $65
        LOG.fw("020:Mode = ", '$65')
        res_str, reportPurse, purseError = prepaid.topup_pursedata()
    else:
        prepaid.topup_card_disconnect()
        purseMode = Param[0]
        LOG.fw("020:Mode = ", purseMode)
        res_str, cardUID, reportPurse, cardAttr = prepaid.topup_get_carddata()

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = reportPurse

        LOG.fw("020:Response = ", reportPurse)

        LOG.fw("020:Result = ", res_str)
        LOG.fw("020:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("020:Result = ", res_str, True)
        LOG.fw("020:Gagal", None, True)
    return res_str

#022
def debit_no_init_single_report(param, __global_response__):
    Param = param.split('|')
    
    if len(Param) == 2:
        C_Denom = Param[0].encode('utf-8')
        C_TID = Param[1].encode('utf-8')
    else:
        LOG.fw("022:Missing Parameter", param)
        raise SystemError("022:Missing Parameter: "+param)

    LOG.fw("022:Parameter = ", C_Denom)
    LOG.fw("022:Parameter = ", C_TID)


    date_now = datetime.datetime.now().strftime("%d%m%y%H%M%S").encode("utf-8")
    timeout = b"5"

    res_str, error_str, C_Balance,C_ReportSAM, C_TypeBank = prepaid.topup_debitnoinit_single(C_TID, C_Denom, date_now, timeout)
    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = C_Balance + "|" + C_ReportSAM + "|" + C_TypeBank

        LOG.fw("022:Response = ", C_Balance)
        LOG.fw("022:Response = ", C_ReportSAM)
        LOG.fw("022:Response = ", C_TypeBank)

        LOG.fw("022:Result = ", res_str)
        LOG.fw("022:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("022:Response = ", error_str, True)
        LOG.fw("022:Result = ", res_str, True)
        LOG.fw("022:Gagal", None, True)
    return res_str

#034
def send_apdu(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 2:
        C_Slot = Param[0].encode('utf-8')
        C_APDU = Param[1].encode('utf-8')
    else:
        LOG.fw("034:Missing Parameter", param)
        raise SystemError("034:Missing Parameter: "+param)

    LOG.fw("034:Parameter = ", C_Slot)
    LOG.fw("034:Parameter = ", C_APDU)

    res_str, RAPDU = prepaid.send_apdu_cmd(C_Slot, C_APDU)

    # res_str = format(res, 'x')
    # if len(res_str) < 4 :
    #     res_str = res_str.zfill(4)
    __global_response__["Result"] = res_str
    
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = RAPDU
        LOG.fw("034:Response = ", RAPDU)

        LOG.fw("034:Result = ", res_str)
        LOG.fw("034:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("034:Result = ", res_str, True)
        LOG.fw("034:Gagal", None, True)
    return res_str

#033
def check_balance_C2C(param, __global_response__):
    # LOG.tracing("COMMON: ", "check_balance_C2C")
    res_str = open_only()
    if res_str != "0000":
        raise SystemError("COM Open Fail: "+res_str)

    res_str, res_saldo, res_uid, res_data, res_attr  = prepaid.topup_C2C_km_balance()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        res_saldo = res_saldo
        res_uid = res_uid
        res_data = res_data
        res_attr = res_attr
        
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = res_saldo + "|" + res_uid + "|" + res_data + "|" + res_attr

        LOG.fw("033:Response = ", res_saldo)
        LOG.fw("033:Response = ", res_uid)
        LOG.fw("033:Response = ", res_data)
        LOG.fw("033:Response = ", res_attr)

        LOG.fw("033:Result = ", res_str)
        LOG.fw("033:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("033:Result = ", res_str, True)
        LOG.fw("033:Gagal", None, True)
    return res_str
