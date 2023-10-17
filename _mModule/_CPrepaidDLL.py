__author__ = 'wahyudi@multidaya.id'

import os.path
import sys
import traceback
import struct
from binascii import hexlify, unhexlify
from ctypes import *
from func_timeout import func_set_timeout
from _mModule import _CPrepaidLib as lib
from _mModule import _CPrepaidLog as LOG
from _mModule import _CPrepaidUtils as utils
from _mModule._CPrepaidDLLModel import *


DLL_LOAD = None

def load_dll():
    global DLL_LOAD
    if DLL_LOAD is None:
        # me = os.path.abspath(os.path.dirname(__file__))
        dll = "Prepaid_32.dll"
        os_arch = struct.calcsize("P") * 8
        if os_arch == 64:
            dll = "Prepaid_64.dll"
        DLL_PATH = os.path.join(sys.path[0], "_lLib", "C_LIB", dll)
        print("pyt: DLL Path", DLL_PATH)
        DLL_LOAD =  windll.LoadLibrary(DLL_PATH)
        LOG.fw("DLL LOADED: ", DLL_PATH)


def direct_load_dll():
    global DLL_LOAD
    if DLL_LOAD is None:
        me = os.path.abspath(os.path.dirname(__file__))
        DLL_PATH = os.path.join(me, "C_LIB", "Prepaid.dll")
        print("pyt: DLL Path", DLL_PATH)
        DLL_LOAD =  windll.LoadLibrary(DLL_PATH)
        LOG.fw("DLL LOADED DIRECT MODE: ", DLL_PATH)

#000
@func_set_timeout(30)
def open_only(PORT, BAUDRATE=None):
    res_str = ""
    error_msg = ""
    try:
        LOG.fw("--> C_PORT = ",PORT)
        LOG.fw("--> BAUDRATE = ",BAUDRATE)
        res_str, error_msg = lib.open_only(PORT.decode('utf-8'), BAUDRATE)

    except Exception as ex:
        LOG.fw("CMD $open_only ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    if res_str != "0000":
        LOG.fw("CMD ERROR = ", error_msg)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#001
@func_set_timeout(30)
def topup_init(PORT, SAMPIN, Institution, Terminal, _serial, _passd):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $30")

        C_PORT = utils.str_to_bytes(PORT)
        C_SAMPIN = utils.str_to_bytes(SAMPIN)
        C_Institution = utils.str_to_bytes(Institution)
        C_Terminal = utils.str_to_bytes(Terminal)

        LOG.fw("--> C_PORT = ",C_PORT)
        LOG.fw("--> C_SAMPIN = ",C_SAMPIN)
        LOG.fw("--> C_Institution = ",C_Institution)
        LOG.fw("--> C_Terminal = ",C_Terminal)

        res_str = lib.topup_init(C_PORT, C_SAMPIN, C_Institution, C_Terminal)
    except Exception as ex:
        LOG.fw("CMD $30 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#002
@func_set_timeout(30)
def topup_auth(PORT, Slot, PinSAM, Institution, Terminal, PinKA, PinKL):
    global DLL_LOAD
    res_str = ""
    NIKKL = ""
    try:
        LOG.fw("--> CMD READER = $34")

        C_PORT = utils.str_to_bytes(PORT)
        C_Slot = utils.str_to_bytes(Slot)
        C_PinSAM = utils.str_to_bytes(PinSAM)
        C_Institution = utils.str_to_bytes(Institution)
        C_Terminal = utils.str_to_bytes(Terminal)
        C_PinKA = utils.str_to_bytes(PinKA)
        C_PinKL = utils.str_to_bytes(PinKL)
        
        LOG.fw("--> C_PORT = ",C_PORT)
        LOG.fw("--> C_Slot = ",C_Slot)
        LOG.fw("--> C_PinSAM = ",C_PinSAM)
        LOG.fw("--> C_Institution = ",C_Institution)
        LOG.fw("--> C_Terminal = ",C_Terminal)
        LOG.fw("--> C_PinKA = ",C_PinKA)
        LOG.fw("--> C_PinKL = ",C_PinKL)

        C_PinKL = hexlify(C_PinKL)
        C_PinKL = C_PinKL.encode("utf-8")
        LOG.fw("C_PinKL = ",C_PinKL)

        structNIK = ResponNIKKL()
        p_structNIK = pointer(structNIK)
        func = DLL_LOAD.topup_auth
        res = func(C_PORT, C_Slot, C_PinSAM, C_Institution, C_Terminal, C_PinKA, C_PinKL, p_structNIK)
        res_str = utils.to_4digit(res)
        NIKKL = structNIK.repDATA.decode("cp437")
    except Exception as ex:
        LOG.fw("CMD $$34 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- NIKKL = " , NIKKL)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, NIKKL

#003-1 / 012-3
@func_set_timeout(30)
def topup_balance_with_sn():
    res_str = ""
    balance = ""
    card_number = ""
    sign = ""

    try:
        LOG.fw("--> CMD READER = $EF")
        res_str, balance, card_number, sign = lib.topup_balance_with_sn()
        int_balance = int(balance)
        balance = str(int_balance)
        
    except Exception as ex:
        LOG.fw("CMD $EF ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- balance = " , balance)
    LOG.fw("<-- card_number = " , card_number)
    LOG.fw("<-- sign = " , sign)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, balance, card_number, str(sign)

#003-2
@func_set_timeout(30)
def topupbni_validation(_timeout):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $67")
        timeout = utils.str_to_bytes(_timeout)
        LOG.fw("--> timeout = " , timeout)
        res_str = lib.topupbni_validation(timeout)
    except Exception as ex:
        LOG.fw("CMD $67 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#008
@func_set_timeout(30)
def topup_debit(Denom, _date_now, _timeout):
    res_str = ""
    debErrorStr  = ""
    balance = ""
    report  = ""
    typebank = "0"

    try:
        LOG.fw("--> CMD READER = $32")
        C_Denom = utils.str_to_bytes(Denom)
        date_now = utils.str_to_bytes(_date_now)
        timeout = utils.str_to_bytes(_timeout)
        
        LOG.fw("--> C_Denom = " , C_Denom)
        LOG.fw("--> date_now = " , date_now)
        LOG.fw("--> timeout = " , timeout)

        res_str, balance, report = lib.topup_debit(C_Denom, date_now, timeout)
        debErrorStr = res_str

        if res_str != "0000":
            typebank = "0"
        else :
            if len(report) <= 99 | len(report.split('q')) > 1:
                report = report.split('q')[0]
                typebank = "1"
            else:
                typebank = "2"
    except Exception as ex:
        LOG.fw("CMD $32 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- report = ", report)
    LOG.fw("<-- balance = ", balance)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<--  = ", )
    LOG.fw("typebank = ", typebank)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, debErrorStr, balance, report, typebank

#009
@func_set_timeout(30)
def topup_balance():
    res_str = ""
    balance = "0"
    try:
        LOG.fw("--> CMD READER = $31")
        res_str, balance = lib.topup_balance()
    except Exception as ex:
        LOG.fw("CMD $31 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, str(balance)

#010
@func_set_timeout(30)
def topup_done():
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $topup_done")
        res_str = lib.topup_done()
    except Exception as ex:
        LOG.fw("CMD $topup_done ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#011
@func_set_timeout(30)
def topup_bni_update(Terminal):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $17")
        C_Terminal = utils.str_to_bytes(Terminal)
        LOG.fw("--> C_Terminal = " , C_Terminal)
        res_str = lib.topup_bni_update(C_Terminal)        
    except Exception as ex:
        LOG.fw("CMD $17 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#012-1
@func_set_timeout(30)
def topup_pursedata_multi_sam(_slot):
    res_str = ""
    response = ""
    try:
        LOG.fw("--> CMD READER = $76")
        slot = utils.str_to_bytes(_slot)
        LOG.fw("--> slot = " , slot)

        res_str, response = lib.topup_pursedata_multi_sam(slot)
    except Exception as ex:
        LOG.fw("CMD $76 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- response = " , response)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, response

#012-2
@func_set_timeout(30)
def topupbni_km_balance_multi_sam(_slot):
    res_str = ""
    rep_saldo = ""
    saldo = 0
    maxSaldo = 0
    try:
        LOG.fw("--> CMD READER = $74")
        slot = utils.str_to_bytes(_slot)
        LOG.fw("--> slot = " , slot)
        res_str, rep_saldo = lib.topupbni_km_balance_multi_sam(slot)
        saldo = rep_saldo[0:10]
        maxSaldo = rep_saldo[-10:]
    except Exception as ex:
        LOG.fw("CMD $74 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- rep_saldo = " , rep_saldo)
    LOG.fw("saldo = " , saldo)
    LOG.fw("maxSaldo = " , maxSaldo)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, saldo, maxSaldo

#012-4
@func_set_timeout(30)
def topupbni_init_multi(_slot, _terminal):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $70")
        slot = utils.str_to_bytes(_slot)
        terminal = utils.str_to_bytes(_terminal)
        LOG.fw("--> slot = " , slot)
        LOG.fw("--> terminal = " , terminal)
        res_str = lib.topupbni_init_multi(slot,terminal)
    except Exception as ex:
        LOG.fw("CMD $70 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#013-1
@func_set_timeout(30)
def topupbni_credit_multi_sam(_slot, _value, _timeOut):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    card_number = ""
    try:
        LOG.fw("--> CMD READER = $71")
        slot = utils.str_to_bytes(_slot)
        value = utils.str_to_bytes(_value)
        timeOut = utils.str_to_bytes(_timeOut)
        LOG.fw("--> slot = " , slot)
        LOG.fw("--> value = " , value)
        LOG.fw("--> timeOut = " , timeOut)
        res_str, reportSAM = lib.topupbni_credit_multi_sam(slot,value,timeOut)
        debErrorStr = res_str
        
        if res_str == "0000" :
            card_number = reportSAM[0:16]        
        
    except Exception as ex:
        LOG.fw("CMD $71 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- card_number = ", card_number)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, card_number, reportSAM    

#018
@func_set_timeout(30)
def topupbni_sam_refill_multi(_slot, _terminal):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $72")
        slot = utils.str_to_bytes(_slot)
        terminal = utils.str_to_bytes(_terminal)
        LOG.fw("--> slot = " , slot)
        LOG.fw("--> terminal = " , terminal)
        res_str, reportSAM = lib.topupbni_sam_refill_multi(slot,terminal)
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $72 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr

#020
@func_set_timeout(30)
def topup_pursedata():
    res_str = ""
    reportPurse=""
    debErrorStr= ""
    try:
        LOG.fw("--> CMD READER = $65")
        res_str, reportPurse = lib.topup_pursedata()
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $65 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- reportPurse = " , reportPurse)
    LOG.fw("<-- debErrorStr = " , debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportPurse, debErrorStr

#022
@func_set_timeout(30)
def topup_debitnoinit_single(TID, Denom, _date_now, _timeout):
    typebank = ""
    balance = 0
    report = ""
    debErrorStr = ""
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $topup_debitnoinit_single")
        C_TID = utils.str_to_bytes(TID)
        C_Denom = utils.str_to_bytes(Denom)
        date_now = utils.str_to_bytes(_date_now)
        timeout = utils.str_to_bytes(_timeout)
        LOG.fw("--> C_TID = " , C_TID)
        LOG.fw("--> C_Denom = " , C_Denom)
        LOG.fw("--> date_now = " , date_now)
        LOG.fw("--> timeout = " , timeout)
        res_str, report = lib.topup_debitnoinit_single(C_TID, date_now, timeout, C_Denom)
        debErrorStr = res_str
        report = report.split('q')[0]

        if res_str != "0000":
            typebank = "0"
        else :
            typebank = report[0:1]
            if typebank == "0" :
                balance  = int(report[456:464], 16)
            elif typebank == "1" :
                balance  = int(report[456:464], 16)
            elif typebank == "2" :
                balance  = int(report[456:464], 16)
            elif typebank == "3" :
                balance  = int(report[456:464], 16)
            elif typebank == "4" :
                balance  = int(report[456:464], 16)
            elif typebank == "5" :
                balance  = int(report[456:464], 16)
            elif typebank == "c" | typebank == 'C':
                balance  = int(report[456:464], 16)
    except Exception as ex:
        LOG.fw("CMD $topup_debitnoinit_single ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("typebank = " , typebank)
    LOG.fw("balance = " , balance)
    LOG.fw("<-- report = " , report)
    LOG.fw("<-- debErrorStr = " , debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, debErrorStr, balance, report, typebank

#026 - OLD
@func_set_timeout(30)
def topup_C2C_refill(Value, Timestamp):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $81")
        C_Value = utils.str_to_bytes(Value)
        LOG.fw("--> Value = " , C_Value)
        LOG.fw("--> Timestamp = " , Timestamp)
        res_str, reportSAM = lib.topup_C2C_refill(Value, Timestamp)
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $81 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr


#026 - NEW
@func_set_timeout(15)
def new_topup_C2C_refill(Value, Timestamp):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $7F")
        C_Value = utils.str_to_bytes(Value)
        LOG.fw("--> Value = " , C_Value)
        LOG.fw("--> Timestamp = " , Timestamp)
        res_str, reportSAM = lib.new_topup_C2C_refill(Value, Timestamp)
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $7F ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr

#027
@func_set_timeout(30)
def topup_C2C_init(Terminal, MAC, Slot):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $80")
        C_Terminal = utils.str_to_bytes(Terminal)
        C_MAC = utils.str_to_bytes(MAC)
        C_Slot = utils.str_to_bytes(Slot)
        LOG.fw("--> C_Terminal = ", C_Terminal)
        LOG.fw("--> C_MAC = ", C_MAC)
        LOG.fw("--> C_Slot = ", C_Slot)
        res_str = lib.topup_C2C_init(C_Terminal, C_MAC, C_Slot)
    except Exception as ex:
        LOG.fw("CMD $80 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#028
@func_set_timeout(30)
def topup_C2C_Correct():
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $82")
        res_str, reportSAM = lib.topup_C2C_Correct()
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $82 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr

#029
@func_set_timeout(30)
def topup_C2C_getfee(Flag):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $85")
        C_Flag = utils.str_to_bytes(Flag)
        LOG.fw("--> C_Flag = ", C_Flag)
        res_str, reportSAM = lib.topup_C2C_getfee(C_Flag)
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $85 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr

#030
@func_set_timeout(30)
def topup_C2C_setfee(Flag, Response):    
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $86")
        C_Flag = utils.str_to_bytes(Flag)
        C_Response = utils.str_to_bytes(Response)
        LOG.fw("--> C_Flag = ", C_Flag)
        LOG.fw("--> C_Response = ", C_Response)
        res_str = lib.topup_C2C_setfee(C_Flag, C_Response)

    except Exception as ex:
        LOG.fw("CMD $86 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#031
# Force Settlement Timeout For 5 Seconds
@func_set_timeout(5)
def topup_C2C_force(Flag):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $84")
        C_Flag = utils.str_to_bytes(Flag)
        LOG.fw("--> C_Flag = ", C_Flag)
        res_str, reportSAM = lib.topup_C2C_force(C_Flag)
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $84 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr


#041
# Force Settlement Timeout For 5 Seconds
@func_set_timeout(5)
def topup_C2C_last_report(Flag):
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $7E")
        res_str, reportSAM = lib.topup_C2C_last_report()
        debErrorStr = res_str
    except Exception as ex:
        LOG.fw("CMD $7E ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, reportSAM, debErrorStr

#033
@func_set_timeout(30)
def topup_C2C_km_balance():
    res_str = ""
    repsaldo = ""
    repUID = ""
    repData = ""
    repAttr = ""
    try:        
        LOG.fw("--> CMD READER = $83")
        res_str, repsaldo, repUID, repData, repAttr = lib.topup_C2C_km_balance()
    except Exception as ex:
        LOG.fw("CMD $83 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- repsaldo = ", repsaldo)
    LOG.fw("<-- repUID = ", repUID)
    LOG.fw("<-- repData = ", repData)
    LOG.fw("<-- repAttr = ", repAttr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, repsaldo, repUID, repData, repAttr

#034, #016
@func_set_timeout(30)
def send_apdu_cmd(Slot, APDU):
    RAPDU = ""
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $B0")
        C_Slot = int(Slot)
        C_APDU = utils.str_to_bytes(APDU)
        LOG.fw("--> C_Slot = ", C_Slot)
        LOG.fw("--> C_APDU = ", C_APDU)
        res_str, RAPDU = lib.send_apdu_cmd(C_Slot, C_APDU)
        LOG.fw("<-- RAPDU = ", RAPDU)
        RAPDU = utils.only_alpanum(RAPDU)
    except Exception as ex:
        LOG.fw("CMD $B0 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, RAPDU

#046
@func_set_timeout(30)
def topup_bca_lib_config(TID, MID):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $19")
        C_TID = utils.str_to_bytes(TID)
        C_MID = utils.str_to_bytes(MID)
        LOG.fw("--> C_TID = ", C_TID)
        LOG.fw("--> C_MID = ", C_MID)
        res_str = lib.topup_bca_lib_config(C_TID,C_MID)
    except Exception as ex:
        LOG.fw("CMD $19 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    LOG.fw("<-- CMD RESULT = ",res_str)        
    return res_str

#---
@func_set_timeout(30)
def get_card_sn():
    UID = ""
    SN = ""
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $F7")
        res_str, UID, SN = lib.get_card_sn()
    except Exception as ex:
        LOG.fw("CMD $F7 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    
    LOG.fw("<-- UID = ", UID)
    LOG.fw("<-- SN = ", SN)
    SN = utils.only_alpanum(SN)
    LOG.fw("SN = ", SN)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, UID, SN

#---
@func_set_timeout(30)
def topup_bca_lib_cardinfo(ATD):
    report = ""
    res_str = ""

    try:        
        LOG.fw("--> CMD READER = $97")
        C_ATD = utils.str_to_bytes(ATD)
        LOG.fw("--> ATD = ", C_ATD)
        res_str, report = lib.topup_bca_lib_cardinfo(C_ATD)
    except Exception as ex:
        LOG.fw("CMD $97 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- report = ", report)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, report

#---
@func_set_timeout(30)
def topup_get_carddata():
    repUID = ""
    repData = ""
    repAttr = ""
    res_str = ""

    try:
        LOG.fw("--> CMD READER = $F9")
        res_str, repUID, repData, repAttr = lib.topup_get_carddata()
    except Exception as ex:
        LOG.fw("CMD $F9 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- repUID = ", repUID)
    LOG.fw("<-- repData = ", repData)
    LOG.fw("<-- repAttr = ", repAttr)
    LOG.fw("<-- CMD RESULT = ", res_str)
    return res_str, repUID, repData, repAttr

@func_set_timeout(30)
def topup_card_disconnect():
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $FA")
        res_str = lib.topup_card_disconnect()
    except Exception as ex:
        LOG.fw("CMD $FA ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

@func_set_timeout(30)
def topup_bca_lib_session1(ATD, datetimes):
    session = ""
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $91")
        C_ATD = utils.str_to_bytes(ATD)
        C_datetimes = utils.str_to_bytes(datetimes)
        LOG.fw("--> ATD = ", C_ATD)
        LOG.fw("--> datetimes = ", C_datetimes)
        res_str, session = lib.topup_bca_lib_session1(C_ATD, C_datetimes)
    except Exception as ex:
        LOG.fw("CMD $91 ERROR: ", "{0}".format(ex))        
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, session

@func_set_timeout(30)
def topup_bca_lib_session2(session):
    res_str = ""
    try:        
        LOG.fw("--> CMD READER = $92")
        C_session = utils.str_to_bytes(session)
        LOG.fw("--> session = ", C_session)
        res_str = lib.topup_bca_lib_session2(session)
    except Exception as ex:
        LOG.fw("CMD $92 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

@func_set_timeout(30)
def topup_bca_lib_topup1(ATD, accescard, accescode, datetimes, amounthex):
    res_str = ""
    session = ""
    try:
        LOG.fw("--> CMD READER = $93")
        C_ATD = utils.str_to_bytes(ATD)
        C_accescard = utils.str_to_bytes(accescard)
        C_accescode = utils.str_to_bytes(accescode)
        C_datetimes = utils.str_to_bytes(datetimes)
        C_amounthex = utils.str_to_bytes(amounthex)
        LOG.fw("--> ATD = ", C_ATD)
        LOG.fw("--> accescard = ", C_accescard)
        LOG.fw("--> accescode = ", C_accescode)
        LOG.fw("--> datetimes = ", C_datetimes)
        LOG.fw("--> amounthex = ", C_amounthex)
        res_str, session = lib.topup_bca_lib_topup1(C_ATD, C_accescard, C_accescode, C_datetimes, C_amounthex)
    except Exception as ex:
        LOG.fw("CMD $93 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, session

@func_set_timeout(30)
def topup_bca_lib_topup2(confirm1, confirm2):
    res_str = ""
    balance = "0"
    respon = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $94")
        C_confirm1 = utils.str_to_bytes(confirm1)
        C_confirm2 = utils.str_to_bytes(confirm2)
        LOG.fw("--> confirm1 = ", C_confirm1)
        LOG.fw("--> confirm2 = ", C_confirm2)
        res_str, respon = lib.topup_bca_lib_topup2(C_confirm1, C_confirm2)
    except Exception as ex:
        LOG.fw("CMD $94 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- response = ", respon)
    LOG.fw("<-- balance = ", balance)
    LOG.fw("<-- debErrorStr = ", debErrorStr)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, balance, respon, debErrorStr

@func_set_timeout(30)
def topup_bca_lib_lastreport():
    res_str = ""
    session = ""
    try:
        LOG.fw("--> CMD READER = $96")
        res_str, session = lib.topup_bca_lib_lastreport()
    except Exception as ex:
        LOG.fw("CMD $96 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ", res_str)
    return res_str, session

@func_set_timeout(30)
def topup_bca_lib_reversal(ATD):
    session = ""
    res_str = ""
    try:           
        LOG.fw("--> CMD READER = $95")
        C_ATD = utils.str_to_bytes(ATD)
        LOG.fw("--> ATD = ", C_ATD)
        res_str, session = lib.topup_bca_lib_reversal(C_ATD)
    except Exception as ex:
        LOG.fw("CMD $95 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ", res_str)
    return res_str, session

def topup_get_tokenbri():
    CardData = ""
    res_str = ""
    try:           
        LOG.fw("--> CMD READER = $A4")
        res_str, CardData = lib.topup_get_tokenbri()
    except Exception as ex:
        LOG.fw("CMD $A4 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        raise ex

    LOG.fw("<-- CardData = ", CardData)
    LOG.fw("<-- CMD RESULT = ", res_str)
    return res_str, CardData

@func_set_timeout(30)
def topup_bca_lib_cardhistory():
    report = ""
    res_str = ""

    try:        
        LOG.fw("--> CMD READER = $98")
        res_str, report = lib.topup_bca_lib_cardhistory()
    except Exception as ex:
        LOG.fw("CMD $98 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- report = ", report)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, report
#---

#080
@func_set_timeout(30)
def topup_bni_init_key(MASTER_KEY, PIN, TID):
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $63")
        STATIC_IV = '0' * 16

        C_MASTER_KEY = utils.str_to_bytes(MASTER_KEY)
        C_PIN = utils.str_to_bytes(PIN)
        C_TID = utils.str_to_bytes(TID)
        C_IV = utils.str_to_bytes(STATIC_IV)
        LOG.fw("--> C_MASTER_KEY = ",C_MASTER_KEY)
        LOG.fw("--> C_PIN = ",C_PIN)
        LOG.fw("--> C_TID = ",C_TID)
        LOG.fw("--> C_IV = ",C_IV)
        res_str = lib.topup_bni_init_key(C_MASTER_KEY, C_IV, C_PIN, C_TID)
    except Exception as ex:
        LOG.fw("CMD $30 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str


@func_set_timeout(25)
def reader_dump(card_no='', trxid=''):
    res_str = ""
    dump_data = ""
    try:
        LOG.fw("--> CMD READER = $B4")
        LOG.fw("--> CARD_NO = ", card_no)
        LOG.fw("--> TRXID = ", trxid)
        res_str, dump_data = lib.reader_dump()
    except Exception as ex:
        LOG.fw("CMD $B4 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- dump_data = ", dump_data)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, dump_data
