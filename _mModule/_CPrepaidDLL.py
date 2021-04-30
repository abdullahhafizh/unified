__author__ = 'fitrah.wahyudi.imam@gmail.com'

import os.path
import datetime
import ctypes
import time
import sys
import traceback
import struct
from _mModule import _CPrepaidLog as LOG
from _mModule import _CPrepaidUtils as utils
from ctypes import *
from _mModule._CPrepaidDLLModel import *
from func_timeout import func_set_timeout
from _mModule import _CPrepaidLib as lib

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
def open_only(PORT):
    # global DLL_LOAD
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $open_only")
                
        LOG.fw("--> C_PORT = ",PORT)

        # C_PORT = utils.str_to_bytes(PORT)

        # LOG.fw("--> C_PORT = ", C_PORT)

        # func = DLL_LOAD.open_only

        # res = func(C_PORT)

        # res_str = utils.to_4digit(res)
        
        res_str, error_msg = lib.open_only(PORT.decode('utf-8'))

        if res_str != "0000":
            LOG.fw("CMD $open_only ERROR: ", error_msg)

    except Exception as ex:
        LOG.fw("CMD $open_only ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())


    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str

#001
@func_set_timeout(30)
def topup_init(PORT, SAMPIN, Institution, Terminal, _serial, _passd):
    # global DLL_LOAD
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $30")

        C_PORT = utils.str_to_bytes(PORT)
        C_SAMPIN = utils.str_to_bytes(SAMPIN)
        C_Institution = utils.str_to_bytes(Institution)
        C_Terminal = utils.str_to_bytes(Terminal)
        # serial = utils.str_to_bytes(_serial)
        # passd = utils.str_to_bytes(_passd)

        LOG.fw("--> C_PORT = ",C_PORT)
        LOG.fw("--> C_SAMPIN = ",C_SAMPIN)
        LOG.fw("--> C_Institution = ",C_Institution)
        LOG.fw("--> C_Terminal = ",C_Terminal)
        # LOG.fw("--> serial = ",serial)
        # LOG.fw("--> passd = ",passd)

        # func = DLL_LOAD.topup_init

        # res = func(C_PORT, C_SAMPIN, C_Institution, C_Terminal, serial, passd)

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

        C_PinKL = C_PinKL.hex()
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
    # global DLL_LOAD
    res_str = ""
    balance = ""
    card_number = ""
    sign = ""

    try:
        LOG.fw("--> CMD READER = $EF")

        # balanceValue = c_int64(0)
        # structSN = ResponSN()
        # signValue = c_int64()

        # p_balanceValue = pointer(balanceValue)
        # p_structSN = pointer(structSN)
        # p_signValue = pointer(signValue)

        # func = DLL_LOAD.topup_balance_with_sn
        # res = func(p_balanceValue, p_structSN, p_signValue)
        # res_str = utils.to_4digit(res)

        # balance = str(balanceValue.value)
        # card_number = structSN.repSN.decode("cp437")
        # sign = str(signValue.value)

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
    # global DLL_LOAD
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $67")
        timeout = utils.str_to_bytes(_timeout)
        LOG.fw("--> timeout = " , timeout)

        # func = DLL_LOAD.topupbni_validation
        # res = func(timeout)

        # res_str = utils.to_4digit(res)
        res_str = lib.topupbni_validation(timeout)
    except Exception as ex:
        LOG.fw("CMD $67 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str

#008
@func_set_timeout(30)
def topup_debit(Denom, _date_now, _timeout):
    # global DLL_LOAD
    res_str = ""
    debErrorStr  = ""
    balance = ""
    report  = ""
    typebank = "0"

    try:
        LOG.fw("--> CMD READER = $32")
        # LOG.tracing("DLL: ", "topup_debit")
        C_Denom = utils.str_to_bytes(Denom)
        date_now = utils.str_to_bytes(_date_now)
        timeout = utils.str_to_bytes(_timeout)
        
        LOG.fw("--> C_Denom = " , C_Denom)
        LOG.fw("--> date_now = " , date_now)
        LOG.fw("--> timeout = " , timeout)

        # structDebit = ResponDebit()
        # p_structDebit = pointer(structDebit)

        # func = DLL_LOAD.topup_debit
        # res = func(C_Denom, date_now, timeout, p_structDebit)
        # res_str = utils.to_4digit(res)

        # balance = str(structDebit.Balance)
        # report = structDebit.rep.decode("cp437")
        # debErrorStr = structDebit.c_error.decode("cp437")

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
    # global DLL_LOAD
    res_str = ""
    balance = "0"
    try:
        LOG.fw("--> CMD READER = $31")

        # balanceValue = c_int64()

        # p_balanceValue = pointer(balanceValue)

        # func = DLL_LOAD.topup_balance
        # res = func(p_balanceValue)
        # res_str = utils.to_4digit(res)
        # balance = str(balanceValue.value)

        res_str, balance = lib.topup_balance()

    except Exception as ex:
        LOG.fw("CMD $31 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    
    return res_str, str(balance)

#010
@func_set_timeout(30)
def topup_done():
    # global DLL_LOAD
    res_str = ""
    try:
        # LOG.tracing("DLL: ", "topup_done")
        LOG.fw("--> CMD READER = $topup_done")
        # func = DLL_LOAD.topup_done
        # res = func()
        # res_str = utils.to_4digit(res)
        res_str = lib.topup_done()
    except Exception as ex:
        LOG.fw("CMD $topup_done ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    
    LOG.fw("<-- CMD RESULT = ",res_str)
    
    return res_str

#011
@func_set_timeout(30)
def topup_bni_update(Terminal):
    # global DLL_LOAD
    res_str = ""
    try:
        # LOG.tracing("DLL: ", "topup_bni_update")
        LOG.fw("--> CMD READER = $17")
        C_Terminal = utils.str_to_bytes(Terminal)
        LOG.fw("--> C_Terminal = " , C_Terminal)

        # func = DLL_LOAD.topup_bni_update

        # res = func(C_Terminal)
        
        # res_str = utils.to_4digit(res)
        res_str = lib.topup_bni_update(C_Terminal)        
    except Exception as ex:
        LOG.fw("CMD $17 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    
    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str

#012-1
@func_set_timeout(30)
def topup_pursedata_multi_sam(_slot):
    # global DLL_LOAD
    # LOG.tracing("DLL: ", "topup_pursedata_multi_sam")
    res_str = ""
    response = ""
    try:
        LOG.fw("--> CMD READER = $76")
        slot = utils.str_to_bytes(_slot)
        LOG.fw("--> slot = " , slot)

        # structPurse = ResponPurseData()
        # p_structPurse = pointer(structPurse)

        # func = DLL_LOAD.topup_pursedata_multi_sam

        # res = func(slot, p_structPurse)
        # res_str = utils.to_4digit(res)

        # response = structPurse.rep.decode("cp437")

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
    # global DLL_LOAD
    res_str = ""
    rep_saldo = ""
    saldo = 0
    maxSaldo = 0
    try:
        # LOG.tracing("DLL: ", "topupbni_km_balance_multi_sam")
        LOG.fw("--> CMD READER = $74")
        slot = utils.str_to_bytes(_slot)
        LOG.fw("--> slot = " , slot)

        # structSaldo = ResponSamSaldo()
        # p_structSaldo = pointer(structSaldo)

        # func = DLL_LOAD.topupbni_km_balance_multi_sam

        # res = func(slot, p_structSaldo)
        # res_str = utils.to_4digit(res)
        # rep_saldo = structSaldo.repsaldo.decode("cp437")

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
    # global DLL_LOAD
    res_str = ""
    try:

        LOG.fw("--> CMD READER = $70")

        slot = utils.str_to_bytes(_slot)
        terminal = utils.str_to_bytes(_terminal)

        LOG.fw("--> slot = " , slot)
        LOG.fw("--> terminal = " , terminal)

        # func = DLL_LOAD.topupbni_init_multi

        # res = func(slot, terminal)
        
        # res_str = utils.to_4digit(res)
        res_str = lib.topupbni_init_multi(slot,terminal)
        
    except Exception as ex:
        LOG.fw("CMD $70 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#013-1
@func_set_timeout(30)
def topupbni_credit_multi_sam(_slot, _value, _timeOut):
    # global DLL_LOAD
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    card_number = ""
    try:

        # LOG.tracing("DLL: ", "topupbni_credit_multi_sam")
        LOG.fw("--> CMD READER = $71")

        slot = utils.str_to_bytes(_slot)
        value = utils.str_to_bytes(_value)
        timeOut = utils.str_to_bytes(_timeOut)

        LOG.fw("--> slot = " , slot)
        LOG.fw("--> value = " , value)
        LOG.fw("--> timeOut = " , timeOut)

        # structTopUp = ResponTopUpBNI()
        # p_structTopUp = pointer(structTopUp)

        # func = DLL_LOAD.topupbni_credit_multi_sam

        # res = func(slot, value, timeOut, p_structTopUp)

        # reportSAM = structTopUp.rep.decode("cp437")
        # debErrorStr = structTopUp.c_error.decode("cp437")

        res_str, reportSAM = lib.topupbni_credit_multi_sam(slot,value,timeOut)
        debErrorStr = res_str
        
        if res_str == "0000" :
            card_number = reportSAM[0:16]        

        # res_str = utils.to_4digit(res)
        
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
    # global DLL_LOAD
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        # LOG.tracing("DLL: ", "topupbni_sam_refill_multi")
        LOG.fw("--> CMD READER = $72")

        slot = utils.str_to_bytes(_slot)
        terminal = utils.str_to_bytes(_terminal)

        LOG.fw("--> slot = " , slot)
        LOG.fw("--> terminal = " , terminal)

        # structTopUp = ResponTopUpBNI()
        # p_structTopUp = pointer(structTopUp)

        # func = DLL_LOAD.topupbni_sam_refill_multi

        # res = func(slot, terminal, p_structTopUp)

        # res_str = utils.to_4digit(res)

        # reportSAM = structTopUp.rep.decode("cp437")
        # debErrorStr = structTopUp.c_error.decode("cp437")

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
    # global DLL_LOAD
    res_str = ""
    reportPurse=""
    debErrorStr= ""
    try:
        LOG.fw("--> CMD READER = $65")

        # structPurse = ResponPurseData()
        # p_structPurse = pointer(structPurse)

        # func = DLL_LOAD.topup_pursedata

        # res = func(p_structPurse)
        # res_str = utils.to_4digit(res)

        # reportPurse = structPurse.rep.decode("cp437")
        # debErrorStr = structPurse.c_error.decode("cp437")

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
    # global DLL_LOAD
    typebank = ""
    balance = 0
    report = ""
    debErrorStr = ""
    res_str = ""
    try:
        # LOG.tracing("DLL: ", "topup_debitnoinit_single")
        LOG.fw("--> CMD READER = $topup_debitnoinit_single")
        
        C_TID = utils.str_to_bytes(TID)
        C_Denom = utils.str_to_bytes(Denom)
        date_now = utils.str_to_bytes(_date_now)
        timeout = utils.str_to_bytes(_timeout)
        
        LOG.fw("--> C_TID = " , C_TID)
        LOG.fw("--> C_Denom = " , C_Denom)
        LOG.fw("--> date_now = " , date_now)
        LOG.fw("--> timeout = " , timeout)

        # structDebit = ResponDebitSingle()
        # p_structDebit = pointer(structDebit)

        # func = DLL_LOAD.topup_debitnoinit_single
        # res = func(C_TID, date_now, timeout, C_Denom, p_structDebit)
        # res_str = utils.to_4digit(res)

        # report = structDebit.rep.decode("cp437")
        # debErrorStr = structDebit.c_error.decode("cp437")

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

#026
@func_set_timeout(30)
def topup_C2C_refill(Value, Timestamp):
    # global DLL_LOAD
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:

        LOG.fw("--> CMD READER = $81")
        C_Value = utils.str_to_bytes(Value)
        LOG.fw("--> Value = " , C_Value)
        LOG.fw("--> Timestamp = " , Timestamp)

        # structTopUp = ResponTopUpC2C()
        # p_structTopUp = pointer(structTopUp)

        # func = DLL_LOAD.topup_C2C_refill

        # res = func(C_Value, p_structTopUp)

        # res_str = utils.to_4digit(res)

        # reportSAM = structTopUp.rep.decode("cp437")
        # debErrorStr = structTopUp.c_error.decode("cp437")

        res_str, reportSAM = lib.topup_C2C_refill(Value, Timestamp)
        debErrorStr = res_str
        
    except Exception as ex:
        LOG.fw("CMD $81 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)

    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str, reportSAM, debErrorStr

#027
@func_set_timeout(30)
def topup_C2C_init(Terminal, MAC, Slot):
    # global DLL_LOAD
    res_str = ""
    try:
        # LOG.tracing("DLL: ", "topup_C2C_init")
        LOG.fw("--> CMD READER = $80")

        C_Terminal = utils.str_to_bytes(Terminal)
        C_MAC = utils.str_to_bytes(MAC)
        C_Slot = utils.str_to_bytes(Slot)
        
        LOG.fw("--> C_Terminal = ", C_Terminal)
        LOG.fw("--> C_MAC = ", C_MAC)
        LOG.fw("--> C_Slot = ", C_Slot)

        # func = DLL_LOAD.topup_C2C_init

        # res = func(C_Terminal, C_MAC, C_Slot)

        # res_str = utils.to_4digit(res)

        res_str = lib.topup_C2C_init(C_Terminal, C_MAC, C_Slot)

    except Exception as ex:
        LOG.fw("CMD $80 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

#028
@func_set_timeout(30)
def topup_C2C_Correct():
    # global DLL_LOAD
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $82")

        # structReport = ResponTopUpC2C()
        # p_structReport = pointer(structReport)

        # func = DLL_LOAD.topup_C2C_Correct

        # res = func(p_structReport)
        # res_str = utils.to_4digit(res)

        # reportSAM = structReport.rep.decode("cp437")
        # debErrorStr = structReport.c_error.decode("cp437")

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
    # global DLL_LOAD
    # LOG.tracing("DLL: ", "topup_C2C_getfee")
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:

        LOG.fw("--> CMD READER = $85")

        C_Flag = utils.str_to_bytes(Flag)

        LOG.fw("--> C_Flag = ", C_Flag)

        # structReport = ResponTopUpC2C()
        # p_structReport = pointer(structReport)

        # func = DLL_LOAD.topup_C2C_getfee

        # res = func(C_Flag, p_structReport)

        # res_str = utils.to_4digit(res)

        # reportSAM = structReport.rep.decode("cp437")
        # debErrorStr = structReport.c_error.decode("cp437")

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
    # global DLL_LOAD
    
    res_str = ""
    
    try:
        LOG.fw("--> CMD READER = $86")
        C_Flag = utils.str_to_bytes(Flag)
        C_Response = utils.str_to_bytes(Response)

        LOG.fw("--> C_Flag = ", C_Flag)
        LOG.fw("--> C_Response = ", C_Response)

        # func = DLL_LOAD.topup_C2C_setfee

        # res = func(C_Flag, C_Response)

        # res_str = utils.to_4digit(res)
        res_str = lib.topup_C2C_setfee(C_Flag, C_Response)

    except Exception as ex:
        LOG.fw("CMD $86 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
    
    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str

#031
@func_set_timeout(30)
def topup_C2C_force(Flag):
    # global DLL_LOAD
    res_str = ""
    reportSAM = ""
    debErrorStr = ""
    try:
        LOG.fw("--> CMD READER = $84")
        C_Flag = utils.str_to_bytes(Flag)
        # C_Flag = c_char(C_Flag)
        LOG.fw("--> C_Flag = ", C_Flag)
        
        # structReport = ResponTopUpC2C()
        # p_structReport = pointer(structReport)

        # func = DLL_LOAD.topup_C2C_force

        # res = func(C_Flag, p_structReport)
        # res_str = utils.to_4digit(res)

        # reportSAM = structReport.rep.decode("cp437")
        # debErrorStr = structReport.c_error.decode("cp437")

        res_str, reportSAM = lib.topup_C2C_force(C_Flag)
        debErrorStr = res_str
        
    except Exception as ex:
        LOG.fw("CMD $84 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        
    LOG.fw("<-- reportSAM = ", reportSAM)
    LOG.fw("<-- debErrorStr = ", debErrorStr)

    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str, reportSAM, debErrorStr

#033
@func_set_timeout(30)
def topup_C2C_km_balance():
    # global DLL_LOAD
    # LOG.tracing("DLL: ", "topup_C2C_km_balance")\
    res_str = ""
    repsaldo = ""
    repUID = ""
    repData = ""
    repAttr = ""
    try:        
        LOG.fw("--> CMD READER = $83")

        # structSaldo = ResponSamSaldo()
        # structUID = ResponUID()
        # structData = ResponCardData()
        # structAttr = ResponCardAttr()

        # p_structSaldo = pointer(structSaldo)
        # p_structUID = pointer(structUID)
        # p_structData = pointer(structData)
        # p_structAttr = pointer(structAttr)

        # func = DLL_LOAD.topup_C2C_km_balance

        # res = func(p_structSaldo, p_structUID, p_structData, p_structAttr)
        # res_str = utils.to_4digit(res)

        # repsaldo = structSaldo.repsaldo
        # repUID = structUID.repUID
        # repData = structData.repData
        # repAttr = structAttr.repAttr

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
def topup_apdusend(Slot, APDU):
    # global DLL_LOAD
    RAPDU = ""
    res_str = ""
    # C_Slot = b"\xFF"
    # LOG.tracing("DLL: ", "topup_apdusend")
    try:

        LOG.fw("--> CMD READER = $B0")

        C_Slot = int(Slot)
        # C_Slot = utils.str_to_bytes(Slot)
        C_APDU = utils.str_to_bytes(APDU)

        LOG.fw("--> C_Slot = ", C_Slot)
        LOG.fw("--> C_APDU = ", C_APDU)

        # structAPDU = ResponAPDU()

        # p_structAPDU = pointer(structAPDU)

        # func = DLL_LOAD.topup_apdusend

        # res = func(C_Slot, C_APDU, p_structAPDU)
        
        # res_str = utils.to_4digit(res)

        # RAPDU = structAPDU.repcek.decode("cp437")
        res_str, RAPDU = lib.topup_apdusend(C_Slot, C_APDU)

        LOG.fw("<-- RAPDU = ", RAPDU)
        RAPDU = utils.only_alpanum(RAPDU)
        LOG.fw("RAPDU = ", RAPDU)

    except Exception as ex:
        LOG.fw("CMD $B0 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, RAPDU

#046
@func_set_timeout(30)
def topup_bca_update(TID, MID):
    # global DLL_LOAD
    res_str = ""
    # LOG.tracing("DLL: ", "topup_bca_update")
    try:

        LOG.fw("--> CMD READER = $19")

        C_TID = utils.str_to_bytes(TID)
        C_MID = utils.str_to_bytes(MID)

        LOG.fw("--> C_TID = ", C_TID)
        LOG.fw("--> C_MID = ", C_MID)

        # func = DLL_LOAD.topup_bca_update
        # res = func(C_TID, C_MID)
        
        # res_str = utils.to_4digit(res)
        res_str = lib.topup_bca_update(C_TID,C_MID)
        
    except Exception as ex:
        LOG.fw("CMD $19 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)        

    return res_str

#---
@func_set_timeout(30)
def topup_get_sn():
    # global DLL_LOAD
    UID = ""
    SN = ""
    res_str = ""
    try:

        # LOG.tracing("DLL: ", "topup_get_sn")
        LOG.fw("--> CMD READER = $F7")

        # structUID = ResponUID()

        # p_structUID = pointer(structUID)

        # structSN = ResponSN()

        # p_structSN = pointer(structSN)

        # func = DLL_LOAD.topup_get_sn

        # res = func(p_structUID, p_structSN)
        # res_str = utils.to_4digit(res)

        # UID = structUID.repUID.decode("cp437")
        # SN = structSN.repSN.decode("cp437")
        res_str, UID, SN = lib.topup_get_sn()
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
def topup_bca_cardinfo(ATD):
    # global DLL_LOAD
    report = ""
    res_str = ""

    try:        
        LOG.fw("--> CMD READER = $97")
        
        C_ATD = utils.str_to_bytes(ATD)
        LOG.fw("--> ATD = ", C_ATD)

        # structReport = ResponBCATopup1()

        # p_structReport = pointer(structReport)

        # func = DLL_LOAD.topup_bca_cardinfo

        # res = func(C_ATD, p_structReport)
        # res_str = utils.to_4digit(res)

        # report = structReport.repDATA.decode("cp437")

        res_str, report = lib.topup_bca_cardinfo(C_ATD)

    except Exception as ex:
        LOG.fw("CMD $97 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- report = ", report)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, report

#---
@func_set_timeout(30)
def topup_get_carddata():
    # global DLL_LOAD
    # LOG.tracing("DLL: ", "topup_get_carddata")
    repUID = ""
    repData = ""
    repAttr = ""
    res_str = ""

    try:
        LOG.fw("--> CMD READER = $F9")

        # structUID = ResponUID()
        # structData = ResponCardData()
        # structAttr = ResponCardAttr()

        # p_structUID = pointer(structUID)
        # p_structData = pointer(structData)
        # p_structAttr = pointer(structAttr)

        # func = DLL_LOAD.topup_get_carddata

        # res = func(p_structUID, p_structData, p_structAttr)
        # res_str = utils.to_4digit(res)

        # repUID = structUID.repUID.decode("cp437")
        # repData = structData.repData.decode("cp437")
        # repAttr = structAttr.repAttr.decode("cp437")

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
    # global DLL_LOAD
    res_str = ""
    try:
        LOG.fw("--> CMD READER = $FA")

        # func = DLL_LOAD.topup_card_disconnect

        # res = func()

        # res_str = utils.to_4digit(res)

        res_str = lib.topup_card_disconnect()

    except Exception as ex:
        LOG.fw("CMD $FA ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

@func_set_timeout(30)
def topup_bca_session1(ATD, datetimes):
    # global DLL_LOAD
    session = ""
    res_str = ""
    try:

        LOG.fw("--> CMD READER = $91")

        C_ATD = utils.str_to_bytes(ATD)
        C_datetimes = utils.str_to_bytes(datetimes)

        LOG.fw("--> ATD = ", C_ATD)
        LOG.fw("--> datetimes = ", C_datetimes)
        
        # structSession = ResponBCASession1()

        # p_structSession = pointer(structSession)
    
        # func = DLL_LOAD.topup_bca_session1

        # res = func(C_ATD, C_datetimes, p_structSession)

        # res_str = utils.to_4digit(res)

        # session = structSession.repDATA.decode("cp437")

        res_str, session = lib.topup_bca_session1(C_ATD, C_datetimes)

    except Exception as ex:
        LOG.fw("CMD $91 ERROR: ", "{0}".format(ex))        
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str, session

@func_set_timeout(30)
def topup_bca_session2(session):
    # global DLL_LOAD
    res_str = ""
    try:        
        LOG.fw("--> CMD READER = $92")

        C_session = utils.str_to_bytes(session)

        LOG.fw("--> session = ", C_session)
        
        # func = DLL_LOAD.topup_bca_session2

        # res = func(C_session)

        # res_str = utils.to_4digit(res)

        res_str = lib.topup_bca_session2(session)

    except Exception as ex:
        LOG.fw("CMD $92 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- CMD RESULT = ",res_str)
    return res_str

@func_set_timeout(30)
def topup_bca_topup1(ATD, accescard, accescode, datetimes, amounthex):
    # global DLL_LOAD
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
        
        # structTopUp = ResponBCATopup1()

        # p_structTopUp = pointer(structTopUp)
    
        # func = DLL_LOAD.topup_bca_topup1

        # res = func(C_ATD, C_accescard, C_accescode, C_datetimes, C_amounthex, p_structTopUp)
        # res_str = utils.to_4digit(res)
        # session = structTopUp.repDATA.decode("cp437")

        res_str, session = lib.topup_bca_topup1(C_ATD, C_accescard, C_accescode, C_datetimes, C_amounthex)

    except Exception as ex:
        LOG.fw("CMD $93 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str, session

@func_set_timeout(30)
def topup_bca_topup2(confirm1, confirm2):
    # global DLL_LOAD
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

        # structTopUp = ResponBCATopup2()

        # p_structTopUp = pointer(structTopUp)
    
        # func = DLL_LOAD.topup_bca_topup2

        # res = func(C_confirm1, C_confirm2, p_structTopUp)

        # respon = structTopUp.rep.decode("cp437")
        # balance = str(structTopUp.Balance)
        # debErrorStr = structTopUp.c_error.decode("cp437")

        # res_str = utils.to_4digit(res)

        res_str, respon = lib.topup_bca_topup2(C_confirm1, C_confirm2)

    except Exception as ex:
        LOG.fw("CMD $94 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- response = ", respon)
    LOG.fw("<-- balance = ", balance)
    LOG.fw("<-- debErrorStr = ", debErrorStr)

    LOG.fw("<-- CMD RESULT = ",res_str)

    return res_str, balance, respon, debErrorStr

@func_set_timeout(30)
def topup_bca_lastreport():
    # global DLL_LOAD
    res_str = ""
    session = ""
    try:
        LOG.fw("--> CMD READER = $96")
        
        # structTopUp = ResponBCATopup1()

        # p_structTopUp = pointer(structTopUp)
    
        # func = DLL_LOAD.topup_bca_lastreport

        # res = func(p_structTopUp)
        # res_str = utils.to_4digit(res)
        # session = structTopUp.repDATA.decode("cp437")
        res_str, session = lib.topup_bca_lastreport()

    except Exception as ex:
        LOG.fw("CMD $96 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ", res_str)
    
    return res_str, session

@func_set_timeout(30)
def topup_bca_reversal(ATD):
    # global DLL_LOAD
    session = ""
    res_str = ""
    try:           
        LOG.fw("--> CMD READER = $95")
        
        C_ATD = utils.str_to_bytes(ATD)

        LOG.fw("--> ATD = ", C_ATD)
        
        # structReversal = ResponBCAReversal()

        # p_structReversal = pointer(structReversal)    
        # func = DLL_LOAD.topup_bca_reversal

        # res = func(C_ATD, p_structReversal)
        # res_str = utils.to_4digit(res)
        # session = structReversal.repDATA.decode("cp437")

        res_str, session = lib.topup_bca_reversal(C_ATD)

    except Exception as ex:
        LOG.fw("CMD $95 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())

    LOG.fw("<-- session = ", session)
    LOG.fw("<-- CMD RESULT = ", res_str)

    return res_str, session

def topup_get_tokenbri():
    # global DLL_LOAD
    CardData = ""
    res_str = ""
    try:           
        LOG.fw("--> CMD READER = $A4")
        
        # structToken = ResponTokenBRI()

        # p_structToken = pointer(structToken)    
        # func = DLL_LOAD.topup_get_tokenbri

        # res = func(p_structToken)
        # res_str = utils.to_4digit(res)

        # CardData = structToken.repDATA.decode("cp437")

        res_str, CardData = lib.topup_get_tokenbri()

    except Exception as ex:
        LOG.fw("CMD $A4 ERROR: ", "{0}".format(ex))
        LOG.fw("Trace: ", traceback.format_exc())
        raise ex

    LOG.fw("<-- CardData = ", CardData)
    LOG.fw("<-- CMD RESULT = ", res_str)

    return res_str, CardData

