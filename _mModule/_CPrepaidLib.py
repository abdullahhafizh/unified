__author__ = 'wahyudi@multidaya.id'

import serial
import traceback
from _mModule import _CSerializer as serializer

COMPORT = None

def open_only(port):
    global COMPORT
    resultStr = "0000"
    msg = ""

    if COMPORT is None:
        COMPORT = serial.Serial(port, baudrate=38400, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    elif COMPORT.isOpen() and COMPORT.name != port:
        COMPORT.close
        COMPORT = serial.Serial(port, baudrate=38400, bytesize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    elif not COMPORT.isOpen():
        COMPORT = serial.Serial(port, baudrget_TDefaultResressize=8, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    else:
        print('pyt: COM Status', COMPORT.isOpen())
    
    return resultStr, msg


def is_serial_valid():
    global COMPORT
    if COMPORT is None:
        # print('is_serial_valid: COMPORT is None')
        return False
    elif not COMPORT.isOpen():
        # print('is_serial_valid: COMPORT is not OPEN')
        return False
    elif COMPORT.isOpen():
        # print('is_serial_valid: COMPORT is OPEN')
        return True
    else:
        print('pyt: COM Status Invalid')
        return False


def topup_auth(C_PORT, C_Slot, C_PinSAM, C_Institution, C_Terminal, C_PinKA, C_PinKL, p_structNIK):
    #Deprecated
    return "FFFF"


def topup_init(PORT, SAMPIN, Institution, Terminal):
    global COMPORT
    # res_str, msg = open_only(PORT)
    # if res_str != "0000":
    #     return "FFFE"
    if not is_serial_valid():
        return "FFFE"

    res_str = serializer.SAM_INITIATION(COMPORT, SAMPIN, Institution, Terminal)
    
    return res_str.decode("utf-8")
    
    
def topup_balance_with_sn():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", "", "", ""
    
    res_str, balance, card_number, sign = serializer.GET_BALANCE_WITH_SN(COMPORT)

    return res_str.decode("utf-8"), balance.decode("utf-8"), card_number.decode("utf-8"), sign


def topup_debit(C_Denom, date_now, timeout):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", "", ""
    
    res_str, balance, report = serializer.DEBIT(COMPORT,date_now,timeout,C_Denom)

    return res_str.decode("utf-8"), balance, report


def topupbni_validation(timeout):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.BNI_TOPUP_VALIDATION(COMPORT, timeout)

    return res_str.decode("utf-8")


def topup_balance():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, balance = serializer.GET_BALANCE(COMPORT)

    return res_str.decode("utf-8"), balance.decode("utf-8")


def topup_bni_update(Terminal):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.BNI_TERMINAL_UPDATE(COMPORT, Terminal)

    return res_str.decode("utf-8")


def topup_pursedata_multi_sam(slot):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, response = serializer.PURSE_DATA_MULTI_SAM(COMPORT, slot)

    return res_str.decode("utf-8"), response


def topupbni_km_balance_multi_sam(slot):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, balance = serializer.BNI_KM_BALANCE_MULTI_SAM(COMPORT, slot)

    return res_str.decode("utf-8"), balance.decode("cp437")


def topupbni_init_multi(slot, terminal):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.BNI_TOPUP_INIT_MULTI(COMPORT, slot, terminal)

    return res_str.decode("utf-8")


def topupbni_credit_multi_sam(slot, value, timeOut):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.BNI_TOPUP_CREDIT_MULTI_SAM(COMPORT, slot, value, timeOut)

    return res_str.decode("utf-8"), report


def topupbni_sam_refill_multi(slot, tid):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.BNI_REFILL_SAM_MULTI(COMPORT, slot, tid)

    return res_str.decode("utf-8"), report


def topup_pursedata():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.PURSE_DATA(COMPORT)

    return res_str.decode("utf-8"), report


def topup_debitnoinit_single(tid, datetime, time_out, value):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.DEBIT_NOINIT_SINGLE(COMPORT, tid, datetime, time_out, value)

    return res_str.decode("utf-8"), report


def topup_C2C_refill(Value, Timestamp):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.TOP_UP_C2C(COMPORT, Value, Timestamp)

    return res_str.decode("utf-8"), report.decode("utf-8")


def topup_C2C_init(tidnew, tidold, C_Slot):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.INIT_TOPUP_C2C(COMPORT, tidnew, tidold, C_Slot)

    return res_str.decode("utf-8")


def topup_C2C_Correct():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.TOPUP_C2C_CORRECTION(COMPORT)

    return res_str.decode("utf-8"), report


def topup_C2C_getfee(C_Flag):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.GET_FEE_C2C(COMPORT, C_Flag)

    return res_str.decode("utf-8"), report.decode("utf-8")


def topup_C2C_setfee(C_Flag, C_Response):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.SET_FEE_C2C(COMPORT, C_Flag, C_Response)

    return res_str.decode("utf-8")


def topup_C2C_force(C_Flag):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.TOPUP_FORCE_C2C(COMPORT, C_Flag)

    return res_str.decode("utf-8"), report.decode("utf-8")


def topup_C2C_km_balance():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", "", "", "", ""
    
    res_str, saldo, uid, carddata, cardattr = serializer.KM_BALANCE_TOPUP_C2C(COMPORT)

    return res_str.decode("utf-8"), saldo.decode("utf-8"), uid.decode("utf-8"), carddata.decode("utf-8"), cardattr.decode("utf-8")


def send_apdu_cmd(C_Slot, C_APDU):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.APDU_SEND(COMPORT, C_Slot, C_APDU)

    return res_str.decode("utf-8"), report


def topup_bca_lib_config(C_TID, C_MID):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.BCA_TERMINAL_UPDATE(COMPORT, C_TID, C_MID)

    return res_str.decode("utf-8")


def get_card_sn():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", "", ""
    
    res_str, uid, sn = serializer.GET_SN(COMPORT)

    return res_str.decode("utf-8"), uid.decode("utf-8"), sn.decode("utf-8")


def topup_bca_lib_cardinfo(C_ATD):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.BCA_CARD_INFO(COMPORT, C_ATD)

    return res_str.decode("utf-8"), report


def topup_get_carddata():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", "", "", ""
    
    res_str, uid, carddata, cardattr = serializer.GET_CARDDATA(COMPORT)

    return res_str.decode("utf-8"), uid, carddata, cardattr


def topup_card_disconnect():
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.CARD_DISCONNECT(COMPORT)

    if res_str:
        return "0000"
    else:
        return "FFFF"


def topup_bca_lib_session1(atd, datetimes):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, session = serializer.BCA_SESSION_1(COMPORT, atd, datetimes)

    return res_str.decode("utf-8"), session


def topup_bca_lib_session2(session):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    
    res_str = serializer.BCA_SESSION_2(COMPORT, session)

    return res_str.decode("utf-8")


def topup_bca_lib_topup1(C_ATD, C_accescard, C_accescode, C_datetimes, C_amounthex):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, rep = serializer.BCA_TOPUP_1(COMPORT, C_ATD, C_accescard, C_accescode, C_datetimes, C_amounthex)

    return res_str.decode("utf-8"), rep


def topup_bca_lib_topup2(C_confirm1, C_confirm2):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, rep = serializer.BCA_TOPUP_2(COMPORT, C_confirm1 + C_confirm2 )

    return res_str.decode("utf-8"), rep    


def topup_bca_lib_lastreport():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, rep = serializer.BCA_LAST_REPORT(COMPORT)

    return res_str.decode("utf-8"), rep    


def topup_bca_lib_reversal(ATD):
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, rep = serializer.BCA_REVERSAL(COMPORT, ATD)

    return res_str.decode("utf-8"), rep


def topup_get_tokenbri():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, rep = serializer.GET_TOKEN_BRI(COMPORT)

    return res_str.decode("utf-8"), rep

def topup_done():
    global COMPORT
    if not COMPORT.isOpen()():
        COMPORT.close()
    
    COMPORT = None

    return "0000"


def topup_bca_lib_cardhistory():
    global COMPORT
    if not is_serial_valid():
        return "FFFE", ""
    
    res_str, report = serializer.BCA_CARD_HISTORY(COMPORT)

    return res_str.decode("utf-8"), report


def topup_bni_init_key(C_MASTER_KEY, C_IV, C_PIN, C_TID):
    global COMPORT
    if not is_serial_valid():
        return "FFFE"
    res_str = serializer.BNI_TOPUP_INIT_KEY(COMPORT, C_MASTER_KEY, C_IV, C_PIN, C_TID)
    return res_str.decode("utf-8")
