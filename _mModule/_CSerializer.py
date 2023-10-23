__author__ = 'wahyudi@multidaya.id'

import datetime
from _mModule import _CPrepaidLog as LOG
from _mModule import _CPrepaidProtocol as proto
from serial import Serial
from time import sleep
from func_timeout import func_set_timeout
import traceback


STX = b'\x10\x02'
ETX = b'\x10\x03'
ETX_DUMP = b'EVENT:CMD:B4 Stop'
WAIT_AFTER_CMD = .2


def SAM_INITIATION(Ser, PIN, INSTITUTION, TERMINAL
# , PIN_Len, INSTITUTION_Len, TERMINAL_Len
):
    tsam = {}
    tsam["cmd"] = b"\x30"
    tsam["ser"] = PIN
    tsam["inst"] = INSTITUTION
    tsam["term"] = TERMINAL
    tsam_value = tsam["cmd"] + tsam["ser"] + tsam["inst"] + tsam["term"]
    p_len, p = proto.Compose_Request(len(tsam_value), tsam_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"]

    
def GET_BALANCE_WITH_SN(Ser=Serial()):
    bal = {}
    bal["cmd"] = b"\xEF"
    st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    bal["date"] = st
    st = "005"
    bal["tout"] = st

    bal_value = bal["cmd"] + bal["date"].encode("utf-8") + bal["tout"].encode("utf-8")
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_balance_response(response["data"])
    # print(result)
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"], result["bal"], result["sn"], result["sign"]


def GET_BALANCE(Ser):
    bal = {}
    bal["cmd"] = b"\x31"
    st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    bal["date"] = st
    st = "005"
    bal["tout"] = st

    bal_value = bal["cmd"] + bal["date"].encode("utf-8") + bal["tout"].encode("utf-8")
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    # If STX Missing 1 byte, trim data to be converted into integer
    if response['start'] != STX or response['start'][0] == STX[1]:
        response['data'] = b'0' + response['data']
        # response['data'] = response['data'][:-1]
        
    result = parse_balance_template(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"], result["bal"]


def DEBIT(Ser, datetime, time_out, value):
    deb = {}
    deb["cmd"] = b"\x32"
    # st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    deb["date"] = datetime
    deb["amt"] = value
    deb["tout"] = time_out.zfill(3)

    deb_value = deb["cmd"] + deb["date"] + deb["amt"] + deb["tout"]
    p_len, p = proto.Compose_Request(len(deb_value), deb_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    if len(rep) > 95:
        balance = parse_balance_from_report_bni(result["rep"])
    else:
        balance = parse_balance_from_report(result["rep"])

    del data
    del response
    
    return result["code"], balance, rep


def parse_balance_from_report_bni(report):
    balance = report[53:59]
    return int.from_bytes(balance, byteorder='big', signed=False)


def parse_balance_from_report(report):
    balance = report[56:64]
    return int.from_bytes(balance, byteorder='big', signed=False)


def BNI_TOPUP_VALIDATION(Ser, timeout):
    sam = {}
    sam["cmd"] = b"\x67"
    st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    sam["date"] = st
    st = timeout.zfill(3)
    sam["tout"] = st

    bal_value = sam["cmd"] + sam["date"].encode("utf-8") + sam["tout"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"]


def BNI_TERMINAL_UPDATE(Ser, terminal):
    sam = {}
    sam["cmd"] = b"\x17"
    st = terminal
    sam["tid"] = terminal

    bal_value = sam["cmd"] + sam["tid"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"]


def BNI_TOPUP_INIT_KEY(Ser, C_MASTER_KEY, C_IV, C_PIN, C_TID):
    sam = {}
    sam["cmd"] = b"\x63"
    sam["mk"] = C_MASTER_KEY
    sam["iv"] = C_IV
    sam["pin"] = C_PIN
    sam["tid"] = C_TID

    bal_value = sam["cmd"] + sam["mk"] + sam["iv"] + sam["pin"] + sam["tid"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    LOG.fw("RAW_RECV:", response)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"]


def PURSE_DATA_MULTI_SAM(Ser, slot):
    sam = {}
    sam["cmd"] = b"\x76"
    sam["slot"] = slot

    bal_value = sam["cmd"] + sam["slot"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    Len = ((response["len"][0] << 8)+response["len"][1])-5
    
    if result['len'] >= 189:
        rep = ''
        for i in range(0, Len):
            rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def BNI_KM_BALANCE_MULTI_SAM(Ser, slot):
    sam = {}
    sam["cmd"] = b"\x74"
    sam["slot"] = slot

    bal_value = sam["cmd"] + sam["slot"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_km_balance_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"], result["bal"]


def BNI_TOPUP_INIT_MULTI(Ser, slot, TIDs):
    sam = {}
    sam["cmd"] = b"\x70"
    sam["slot"] = slot
    sam["tids"] = TIDs

    bal_value = sam["cmd"] + sam["tids"] +  sam["slot"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)

    del data
    del response
    
    return result["code"]


def BNI_TOPUP_CREDIT_MULTI_SAM(Ser, slot, value, time_out):
    sam = {}
    sam["cmd"] = b"\x71"
    st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    sam["date"] = st
    sam["AMOUNT"] = str(value).zfill(10)
    sam["TIMEOUT"] = time_out.zfill(3)
    sam["slot"] = slot

    bal_value = sam["cmd"] + sam["date"].encode("utf-8") + sam["AMOUNT"].encode("utf-8") + sam["slot"] + sam["TIMEOUT"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def BNI_REFILL_SAM_MULTI(Ser, slot, TIDs):
    sam = {}
    sam["cmd"] = b"\x72"
    sam["TID"] = TIDs
    sam["slot"] = slot

    bal_value = sam["cmd"] + sam["TID"] + sam["slot"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response
    
    return result["code"], rep


def PURSE_DATA(Ser):
    sam = {}
    sam["cmd"] = b"\x65"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response
    
    return result["code"], rep


def DEBIT_NOINIT_SINGLE(Ser, tid, datetime, time_out, value):
    sam = {}
    sam["cmd"] = b"\x65"
    st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    sam["date"] = st
    sam["amt"] = value
    sam["tout"] = time_out.zfill(3)
    sam["term"] = tid

    bal_value = sam["cmd"] + sam["date"].encode("utf-8") + sam["amt"] + sam["term"] + sam["tout"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def TOP_UP_C2C(Ser, amount, timestamp):
    sam = {}
    sam["cmd"] = b"\x81"
    # st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    sam["date"] = timestamp
    sam["amt"] = str(amount).zfill(10)
    sam["tout"] = "005".zfill(3)

    c2c_refill = sam["cmd"] + sam["date"].encode("utf-8") + sam["amt"].encode("utf-8") + sam["tout"].encode("utf-8")
    p_len, p = proto.Compose_Request(len(c2c_refill), c2c_refill)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    # Len = ((response["len"][0] << 8)+response["len"][1])-5
    # rep = ''
    # for i in range(0, Len-1):
    #     rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], result["rep"]


def INIT_TOPUP_C2C(Ser, tidnew, tidold, C_Slot):
    sam = {}
    sam["cmd"] = b"\x80"
    st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    sam["tid_new"] = tidnew
    sam["tid_old"] = tidold

    bal_value = sam["cmd"] + sam["tid_new"] + sam["tid_old"] + b"\x00"
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)

    # Len = ((response["len"][0] << 8)+response["len"][1])-5
    # rep = ''
    # for i in range(0, Len-1):
    #     rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"]


def TOPUP_C2C_CORRECTION(Ser):
    sam = {}
    sam["cmd"] = b"\x82"
    sam["tout"] = "005"

    bal_value = sam["cmd"] + sam["tout"].encode("utf-8")
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def GET_FEE_C2C(Ser, Flag):
    sam = {}
    sam["cmd"] = b"\x85"
    st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    sam["date"] = st
    if Flag == b"1":
        sam["isNew"] = b"1"
    else:
        sam["isNew"] = b"0"

    bal_value = sam["cmd"] + sam["date"].encode("utf-8") + sam["isNew"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    # Len = ((response["len"][0] << 8)+response["len"][1])-5
    # rep = ''
    # for i in range(0, Len-1):
    #     rep = rep + chr(result["rep"][i])
    
    del data
    del response

    return result["code"], result["rep"]


def SET_FEE_C2C(Ser, Flag, respon):
    sam = {}
    sam["cmd"] = b"\x86"
    # st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    # sam["date"] = st
    if Flag == b"1":
        sam["isNew"] = b"1"
    else:
        sam["isNew"] = b"0"
    
    sam["len"] = bytearray.fromhex(format(len(respon), 'x').upper().zfill(3))
    sam["data"] = respon

    bal_value = sam["cmd"] + sam["isNew"] + sam["len"] + sam["data"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)

    # Len = ((response["len"][0] << 8)+response["len"][1])-5
    # rep = ''
    # for i in range(0, Len-1):
    #     rep = rep + chr(result["rep"][i])
    
    del data
    del response

    return result["code"]


def TOPUP_FORCE_C2C(Ser, Flag):
    sam = {}
    sam["cmd"] = b"\x84"
    st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    sam["date"] = st
    if Flag == b"1":
        sam["isNew"] = b"1"
    else:
        sam["isNew"] = b"0"

    bal_value = sam["cmd"] + sam["date"].encode("utf-8") + sam["isNew"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    # Len = ((response["len"][0] << 8)+response["len"][1])-5
    # rep = ''
    # for i in range(0, Len-1):
    #     rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], result["rep"]


def MDR_C2C_LAST_REPORT(Ser):
    sam = {}
    sam["cmd"] = b"\x7E"
    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    del data
    del response

    return result["code"], result["rep"]


def NEW_TOP_UP_C2C(Ser, amount, timestamp):
    sam = {}
    sam["cmd"] = b"\x7F"
    # st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    sam["date"] = timestamp
    sam["amt"] = str(amount).zfill(10)
    sam["tout"] = "005".zfill(3)

    c2c_refill = sam["cmd"] + sam["date"].encode("utf-8") + sam["amt"].encode("utf-8") + sam["tout"].encode("utf-8")
    p_len, p = proto.Compose_Request(len(c2c_refill), c2c_refill)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    del data
    del response

    return result["code"], result["rep"]


def KM_BALANCE_TOPUP_C2C(Ser):
    sam = {}
    sam["cmd"] = b"\x83"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    if result["code"] == b"0000" or result["code"] == b"9000":
        idx_last_saldo = 10
        # EXTRAS: Handling Missing STX Report in Deposit Check
        if result["len"] < 173: idx_last_saldo = 9
        saldo = result["rep"][0:idx_last_saldo]
        uid = result["rep"][10:24]
        carddata = result["rep"][24:150]        
        cardatr = result["rep"][150:len(result["rep"])]
        return b"0000", saldo, uid, carddata, cardatr
    else:
        return result["code"], b"", b"", b"", b""


def APDU_SEND(Ser, slot, apdu):
    sam = {}
    sam["cmd"] = b"\xB0"
    sam["slot"] = format(slot, "X")[0:2].zfill(2)
    sam["len"] = format(len(apdu), "X")[0:2].zfill(2)
    sam["apdu"] = apdu

    bal_value = sam["cmd"] + sam["slot"].encode("utf-8") + sam["len"].encode("utf-8") + sam["apdu"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def BCA_TERMINAL_UPDATE(Ser, TID, MID):
    sam = {}
    sam["cmd"] = b"\x19"

    sam["TID"] = TID
    i = len(sam["TID"])
    while i < 8:
        sam['TID'] = sam['TID'] + b"0" 
        i = len(sam["TID"])

    # sam["TID"] = "00000000"
    # for i in range(0, len(TID)):
    #     sam["TID"][i] = TID[i+1]

    sam["MID"] = MID
    i = len(sam["MID"])
    while i < 9:
        sam['MID'] = sam['MID'] + b"0" 
        i = len(sam["MID"])
    # sam["MID"] = "000000000"
    # for i in range(0, len(MID)):
    #     sam["MID"][i] = MID[i+1]

    sam["MINBAL"] = b"00001"

    bal_value = sam["cmd"] + sam["TID"] + sam["MID"] + sam["MINBAL"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)
    
    del data
    del response

    return result["code"]


def GET_SN(Ser):
    sam = {}
    sam["cmd"] = b"\xF7"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5

    #f70000 044580C21B5D80006013500433185031
    uid = ''
    for i in range(0, 14):
        uid = uid + chr(result["rep"][i])

    sn = ''
    if Len > 16:
        for i in range(16, 32):
            sn = sn + chr(result["rep"][i])
            
    del data
    del response
    
    return result["code"], uid.encode('utf-8'), sn.encode('utf-8')


def BCA_CARD_INFO(Ser, ATD):
    sam = {}
    sam["cmd"] = b"\x97"

    # sam["ATD"] = '0'
    # for i in range(0, 44):
    #     sam["ATD"] = '0' + sam["ATD"]
    # for i in range(0, len(ATD)):
    #     sam["ATD"][i] = ATD[i+1]

    sam["ATD"] = ATD
    i = len(sam["ATD"])
    while i < 45:
        sam['ATD'] = sam['ATD'] + b"0" 
        i = len(sam["ATD"])

    bal_value = sam["cmd"] + sam["ATD"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def GET_CARDDATA(Ser):
    sam = {}
    sam["cmd"] = b"\xF9"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    # Len = ((response["len"][0] << 8)+response["len"][1])-5
    # rep = ''
    # for i in range(0, Len-1):
    #     rep = rep + chr(response["rep"][i])

    del data
    del response

    if result["code"] == b"0000" or result["code"] == b"9000":
        UID = ""
        for i in range(0,8):
            UID = UID + chr(result["rep"][i])
        CARDDATA = ""
        for i in range(8,8+126):
            CARDDATA = CARDDATA + chr(result["rep"][i])
        CARDATTR = ""
        for i in range(8+126,len(result["rep"])):
            CARDATTR = CARDATTR + chr(result["rep"][i])            
        return b"0000", UID, CARDDATA, CARDATTR
    else:
        return result["code"], "", "", ""


def CARD_DISCONNECT(Ser):
    sam = {}
    sam["cmd"] = b"\xFA"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    # send_command(Ser, p)
    Ser.write(p)
    Ser.flush()
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    del data
    del response
    
    return True


def BCA_SESSION_1(Ser, ATD, datetimes):
    sam = {}
    sam["cmd"] = b"\x91"

    # sam["ATD"] = '0'
    # for i in range(0, 44):
    #     sam["ATD"] = '0' + sam["ATD"]
    # for i in range(0, len(ATD)):
    #     sam["ATD"][i] = ATD[i+1]

    sam["ATD"] = ATD
    i = len(sam["ATD"])
    while i < 45:
        sam['ATD'] = sam['ATD'] + b"0" 
        i = len(sam["ATD"])

    sam["date"] = datetimes

    bal_value = sam["cmd"] + sam["ATD"] + sam["date"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def BCA_SESSION_2(Ser, session):
    sam = {}
    sam["cmd"] = b"\x92"

    # sam["session"] = '0'
    # for i in range(0, 499):
    #     sam["session"] = '0' + sam["session"]
    # for i in range(0, len(session)):
    #     sam["session"][i] = session[i+1]

    sam["session"] = session
    i = len(sam["session"])
    while i < 500:
        sam['session'] = sam['session'] + b"0" 
        i = len(sam["session"])

    bal_value = sam["cmd"] + sam["session"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_response(response["data"])
    LOG.fw("RESPONSE:", result)

    del data
    del response

    return result["code"]


def BCA_TOPUP_1(Ser, ATD, AccessCard, AccessCode, datetimes, AmountHex):
    sam = {}
    sam["cmd"] = b"\x93"

    # sam["ATD"] = '0'
    # for i in range(0, 44):
    #     sam["ATD"] = '0' + sam["ATD"]
    # for i in range(0, len(ATD)):
    #     sam["ATD"][i] = ATD[i+1]

    sam["ATD"] = ATD
    i = len(sam["ATD"])
    while i < 45:
        sam['ATD'] = sam['ATD'] + b"0" 
        i = len(sam["ATD"])    
    
    # sam["AccessCard"] = '0'
    # for i in range(0, 15):
    #     sam["AccessCard"] = '0' + sam["AccessCard"]
    # for i in range(0, len(AccessCard)):
    #     sam["AccessCard"][i] = AccessCard[i+1]

    sam["AccessCard"] = AccessCard
    i = len(sam["AccessCard"])
    while i < 16:
        sam['AccessCard'] = sam['AccessCard'] + b"0" 
        i = len(sam["AccessCard"]) 
    
    # sam["AccessCode"] = '0'
    # for i in range(0, 5):
    #     sam["AccessCode"] = '0' + sam["AccessCode"]
    # for i in range(0, len(AccessCode)):
    #     sam["AccessCode"][i] = AccessCode[i+1]

    sam["AccessCode"] = AccessCode
    i = len(sam["AccessCode"])
    while i < 6:
        sam['AccessCode'] = sam['AccessCode'] + b"0" 
        i = len(sam["AccessCode"])

    sam["datetimes"]=datetimes
    
    # sam["AmountHex"] = '0'
    # for i in range(0, 15):
    #     sam["AmountHex"] = '0' + sam["AmountHex"]
    # for i in range(0, len(AmountHex)):
    #     sam["AmountHex"][i] = AmountHex[i+1]

    sam["AmountHex"] = AmountHex
    i = len(sam["AmountHex"])
    while i < 16:
        sam['AmountHex'] = sam['AmountHex'] + b"0" 
        i = len(sam["AmountHex"])

    bal_value = sam["cmd"] + sam["ATD"] + sam["AccessCard"] + sam["AccessCode"] + sam["datetimes"] + sam["AmountHex"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def BCA_TOPUP_2(Ser, strConfirm):
    sam = {}
    sam["cmd"] = b"\x94"

    # sam["strConfirm"] = '0'
    # for i in range(0, 1023):
    #     sam["strConfirm"] = '0' + sam["strConfirm"]
    # for i in range(0, len(strConfirm)):
    #     sam["strConfirm"][i] = strConfirm[i+1]
    
    sam["strConfirm"] =strConfirm
    i = len(sam["strConfirm"])
    while i < 1024:
        sam['strConfirm'] = sam['strConfirm'] + b"0" 
        i = len(sam["strConfirm"])
    
    bal_value = sam["cmd"] + sam["strConfirm"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def BCA_LAST_REPORT(Ser):
    sam = {}
    sam["cmd"] = b"\x96"
    
    bal_value = sam["cmd"] 
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response
    
    return result["code"], rep


def BCA_REVERSAL(Ser, ATD):
    sam = {}
    sam["cmd"] = b"\x95"
    
    # sam["ATD"] = '0'
    # for i in range(0, 44):
    #     sam["ATD"] = '0' + sam["ATD"]
    # for i in range(0, len(ATD)):
    #     sam["ATD"][i] = ATD[i+1]

    sam["ATD"] = ATD
    i = len(sam["ATD"])
    while i < 45:
        sam['ATD'] = sam['ATD'] + b"0" 
        i = len(sam["ATD"])

    bal_value = sam["cmd"] + sam["ATD"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response
    
    return result["code"], rep


def BCA_CARD_HISTORY(Ser):
    sam = {}
    sam["cmd"] = b"\x98"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response

    return result["code"], rep


def GET_TOKEN_BRI(Ser):
    sam = {}
    sam["cmd"] = b"\xA4"

    bal_value = sam["cmd"] 
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    Len = ((response["len"][0] << 8)+response["len"][1])-5
    CARDDATA = ''
    for i in range(0, Len):
        CARDDATA = CARDDATA + chr(result["rep"][i])

    del data
    del response

    return result["code"], CARDDATA


def GET_CARD_HISTORY(Ser):
    send = {}
    send["cmd"] = b"\xA5"
    
    bal_value = send["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_default_report(response["data"])
    LOG.fw("RESPONSE:", result)
    
    data_len = ((response["len"][0] << 8)+response["len"][1])-5
    history_data = ''
    for i in range(0, data_len):
        history_data = history_data + chr(result["rep"][i])

    del data
    del response

    return result["code"], history_data


def CLEAR_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB5"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    Ser.write(p)
    Ser.flush()


def READER_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB4"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    result = dict()
    result['raw'] = b''
    
    try:
        res = retrieve_rs232_dump_data(Ser, result)
        print(res)
    except:
        err_message = traceback._cause_message
        print(err_message)
    finally:
        CLEAR_DUMP(Ser)
        return '0000', result['raw'].decode('cp1252')
    
'''
------------------------------------------------------------------------------------------------
'''

def send_command(Ser, p):
    Ser.flush()
    Ser.write(p)
    sleep(WAIT_AFTER_CMD)
    Ser.flush()


MIN_REPLY_LENGTH = 5


def retrieve_rs232_data(Ser=Serial()):
    response = b''
    while True:
        response = Ser.read_until(ETX)
        
        if len(response) < MIN_REPLY_LENGTH:
            response = b''
            sleep(WAIT_AFTER_CMD)
            continue
        
        # OLD HANDLING
        # if response.__contains__(ETX):
        #     i_end = response.index(ETX)
        #     response = response[:(i_end+len(ETX))]
        #     if response[0] == STX[1]: 
        #         response = STX[0].to_bytes(1, 'big') + response
        #     LOG.fw("RAW_REPLY:", response)
        #     return response
        
        # NEW HANDLING
        if response.__contains__(ETX):
            LOG.fw("RAW_REPLY:", response)
            if response[:2] != STX: 
                response = STX[0].to_bytes(1, 'big') + response
                LOG.fw("FIX_STX:", response)
            i_start = response.index(STX)
            i_end = response.index(ETX)
            if i_start:
                LOG.fw("TRIM_REPLY:", len(response[:i_start]))
                response = response[i_start:(i_end+len(ETX))]
            else:
                response = response[:(i_end+len(ETX))]
            LOG.fw("FINAL_REPLY:", response)
            return response

# Must Wait Within 15 Seconds
@func_set_timeout(15)
def retrieve_rs232_dump_data(Ser=Serial(), result={}):
    # Waiting Response until Function Timeout Reach
    while True:
        line = Ser.readline()
        if line:
            result['raw'] += line
            if line.__contains__(ETX_DUMP):
                print(ETX_DUMP.decode() + ' Detected: Break')
                break
            continue
        break
    return True


def parse_default_template(data):
    '''
    TBalResponsws  = packed record
    start   : array[0..1] of byte;
    header  : array[0..6] of byte;
    len     : array[0..1] of byte;
    data    : TBalanceresws;
    res     : array[0..2] of byte;
    end; 
    '''
    result = {}
    # Handle Anomaly Response From Reader Missing STX
    # if data[0] != b'\x10': 
    #     data = b'\x10' + data
    result["start"] = data[0:2]
    result["header"] = data[2:9]
    result["len"] = data[9:11]
    len_data = 11+int.from_bytes(result['len'],byteorder='big', signed=False)
    result["data"] = data[11:len_data]
    result["res"] = data[len_data:len_data+3]

    return result


def parse_balance_response(data):
    '''
    TBalanceresws = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    sign  : byte;
    bal   : array[0..9] of char;
    sn    : array[0..15] of char;
    end; 
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    try:
        result["sign"] = chr(int(data[5]))
        result["bal"] = data[6:16]
        amount = int(result["bal"])
    except:
        result["sign"] = ''
        result["code"] = b'ERR0'
    result["bal"] = data[6:16]
    result["sn"] = data[16:32]

    return result


def parse_balance_template(data):
    '''
    TBalanceres = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    bal   : array[0..9] of char;
    end; 
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    result["bal"] = data[5:15]

    return result


def parse_default_km_balance_report(data):
    '''
    TBNIKMMULTIBalanceres = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    bal  : array[0..19] of byte;
    end; 
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    result["bal"] = data[5:25]

    return result


def parse_default_response(data):
    '''
    TSamInitres = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    end;
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]

    return result


def parse_default_report(data):
    '''
    Tdebitres = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    //sign  : byte;                      //MULTIBANK
    rep   : array[0..218] of byte;
    end;   
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    result["rep"] = data[5:len(data)]
    result["len"] = len(data)

    return result


def parse_default_sn_report(data):
    '''
    TSerialNumberres = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    uid   : array[0..7] of byte;
    SN    : array[0..15] of byte;
    end;
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    result["uid"] = data[5:13]
    result["sn"] = data[13:29]
    
    return result
