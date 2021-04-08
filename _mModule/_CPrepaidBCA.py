__author__ = 'fitrah.wahyudi.imam@gmail.com'

from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidUtils as utils
from _mModule import _CPrepaidLog as LOG
from _cConfig import _Common
import requests
import os
import json
import datetime

BCA_ATD = "01BTESTDEVAOZ5L0LDraBjL9d5JKVhFR0RJ4dlZu0aWBs"
UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL_DEV
BCA_ACCESS_CARD_NUMBER = "0145008000000025"
BCA_ACCESS_CODE = "111111"
if not _Common.DEV_MODE_TOPUP_BCA:
    BCA_ATD = "01SMUDAINACbIhPF92u0C38pOBKjQSFiZQHEQUZX0jWfA"
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL
    BCA_ACCESS_CARD_NUMBER = "NOT_SET"
    BCA_ACCESS_CODE = "NOT_SET"

TIMEOUT_REQUESTS = 50

#046
def update_bca(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 2:
        C_TID = Param[0].encode('utf-8')
        C_MID = Param[1].encode('utf-8')
    else:
        LOG.fw("045:Parameter tidak lengkap", param)
        raise Exception("045:Parameter tidak lengkap: "+param)

    LOG.fw("046:Parameter = ", C_TID)
    LOG.fw("046:Parameter = ", C_MID)

    res_str = prepaid.topup_bca_update(C_TID, C_MID)

    if res_str != "0000":
        prepaid.topup_done()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("046:Result = ", res_str)
        LOG.fw("046:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("046:Result = ", res_str, True)
        LOG.fw("046:Gagal", None, True)

    return res_str

#048
def get_card_info_bca(param, __global_response__):
    global BCA_ATD

    res_str, CardNo, CardUID = on_detect()

    LOG.fw("048:BCATopupCardInfo atd = ", BCA_ATD)
    res_str, report = topup_card_info(BCA_ATD)
    LOG.fw("048:BCATopupCardInfo = ", report)
    
    if report == "" :
        if res_str == "0000":
            res_str = "8888"
        __global_response__["Response"] = "BCATopupCardInfo_Failed"
        LOG.fw("048:Response = ", "BCATopupCardInfo_Failed", True)

    
    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] =  report

        LOG.fw("048:Response = ", report)
        LOG.fw("048:Result = ", res_str)
        LOG.fw("048:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("048:Result = ", res_str, True)
        LOG.fw("048:Gagal", None, True)

    return res_str

def on_detect():
    res_str, CardUID, CardNo = prepaid.topup_get_sn()

    LOG.fw("ONDetect CARDNO = ", CardNo)
    LOG.fw("ONDetect CARD_UID = ", CardUID)

    if CardUID[-6:] == "000000":
        CardUID = CardUID[0:8]
    else:
        CardUID = CardUID[0:14]

    return res_str, CardNo, CardUID

def topup_card_info(ATD):
    res_str, report = prepaid.topup_bca_cardinfo(ATD)
    return res_str, report

#044
def update_balance_bca(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 3:
        C_TID = Param[0].encode('utf-8')
        C_MID = Param[1].encode('utf-8')
        C_TOKEN = Param[2].encode('utf-8')
    else:
        LOG.fw("044:Parameter tidak lengkap", param)
        raise Exception("044:Parameter tidak lengkap: "+param)
        
    LOG.fw("044:Parameter = ", C_TID)
    LOG.fw("044:Parameter = ", C_MID)
    LOG.fw("044:Parameter = ", C_TOKEN)

    res_str, cardno, amount, lastbalance, report, ErrMsg = update_balance_bca_priv(C_TID, C_MID, C_TOKEN)

    __global_response__["Result"] = res_str
    if res_str == "0000" or res_str == "0":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] =  str(cardno) + "|" + str(amount) + "|" + str(lastbalance) + "|" + str(report)
        LOG.fw("044:Response = ", cardno)
        LOG.fw("044:Response = ", amount)
        LOG.fw("044:Response = ", lastbalance)
        LOG.fw("044:Response = ", report)

        LOG.fw("044:Result = ", res_str)
        LOG.fw("044:Sukses", None)

    else:
        __global_response__["Response"]  = ErrMsg
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("044:Response = ", ErrMsg)
        LOG.fw("044:Result = ", res_str, True)
        LOG.fw("044:Gagal", None, True)
    
    return res_str

#045
def reversal_bca(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 3:
        C_TID = Param[0].encode('utf-8')
        C_MID = Param[1].encode('utf-8')
        C_TOKEN = Param[2].encode('utf-8')
    else:
        LOG.fw("045:Parameter tidak lengkap", param)
        raise Exception("045:Parameter tidak lengkap: "+param)

    LOG.fw("045:Parameter = ", C_TID)
    LOG.fw("045:Parameter = ", C_MID)
    LOG.fw("045:Parameter = ", C_TOKEN)

    res_str, cardno, amount, lastbalance, report, ErrMsg = reversal_bca_priv(C_TID, C_MID, C_TOKEN)

    __global_response__["Result"] = res_str
    if res_str == "0000" or res_str == "0":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] =  str(cardno) + "|" + str(amount) + "|" + str(lastbalance) + "|" + str(report)
        LOG.fw("045:Response = ", cardno)
        LOG.fw("045:Response = ", amount)
        LOG.fw("045:Response = ", lastbalance)
        LOG.fw("045:Response = ", report)

        LOG.fw("045:Result = ", res_str)
        LOG.fw("045:Sukses", None)        
    else:
        __global_response__["Response"]  = ErrMsg
        __global_response__["ErrorDesc"] = "Gagal"
        
        LOG.fw("045:Response = ", ErrMsg)
        LOG.fw("045:Result = ", res_str, True)
        LOG.fw("045:Gagal", None, True)
    
    return res_str

def reversal_bca_priv(TID, MID, TOKEN):
    global BCA_ACCESS_CARD_NUMBER, BCA_ACCESS_CODE, BCA_ATD, UPDATE_BALANCE_URL
    bcaAccessCardNumber = BCA_ACCESS_CARD_NUMBER
    bcaAccessCode =  BCA_ACCESS_CODE
    bcaStaticATD = BCA_ATD

    resultStr = ""
    ErrorCode = ""
    resreport = ""
    valuetext = ""
    report = ""
    csn = ""
    uid = ""
    balance = 0
    SIGN = 0
    amount = 0
    cardno = ""
    lastbalance = ""

    resultStr = prepaid.topup_card_disconnect()
    value = 0
    url = UPDATE_BALANCE_URL

    resultStr, balance, cardno, SIGN = prepaid.topup_balance_with_sn()

    ErrorCode = resultStr
    topup_session = ""
    reference_id = ""
    topup_amount = ""
    confirm_data = ""
    datenow = ""
    ErrMsg = ""

    if resultStr == "0000":
        LOG.fw("045:cardno = ", cardno)
        LOG.fw("045:uid = ", uid)
        valuetext, ErrMsg = send_check_session_bca(url, TOKEN, TID, MID,cardno)
        if valuetext == "1":
            valuetext = ErrMsg
        
        code = ""
        updateStatus = ""
        dataToCard = ""
        dataJ = json.loads(valuetext)

        if "response" in dataJ.keys():
            temp_json = dataJ["response"]
            if "code" in temp_json:
                code = temp_json["code"]
                    
        if "data" in dataJ.keys():
            temp_json = dataJ["data"]
            if "topup_session" in temp_json.keys():
                topup_session = temp_json["topup_session"]
            if "reference_id" in temp_json.keys():
                reference_id = temp_json["reference_id"]
            if "topup_amount" in temp_json.keys():
                topup_amount = temp_json["topup_amount"]

            if "access_card" in temp_json.keys():
                bcaAccessCardNumber = temp_json["access_card"]
            if "topup_code" in temp_json.keys():
                bcaAccessCode = temp_json["topup_code"]

            amount = topup_amount
        
        LOG.fw("045:bcaAccessCardNumber respon = ", bcaAccessCardNumber)
        LOG.fw("045:bcaAccessCode respon = ", bcaAccessCode)

        if code == "200" or code == 200:
            resultStr = "0000"
        else:
            datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            resultStr, report = bca_topup_session(bcaStaticATD, datenow)
            ErrorCode = resultStr
            LOG.fw("044:BCATopupSession1 respon = ",  { "resultStr":resultStr, "report": report})
            valuetext,ErrMsg = send_session_bca(url, TOKEN, TID,MID, cardno, report)

            if valuetext == "1":
                valuetext = ErrMsg

            dataJ = json.loads(valuetext)

            if "response" in dataJ.keys():
                temp_json = dataJ["response"]
                if "code" in temp_json.keys():
                    code = temp_json["code"]
                    
            if "data" in dataJ.keys():
                temp_json = dataJ["data"]

                if "topup_session" in temp_json.keys():
                    topup_session = temp_json["topup_session"]
                if "reference_id" in temp_json.keys():
                    reference_id = temp_json["reference_id"]
                if "topup_amount" in temp_json.keys():
                    topup_amount = temp_json["topup_amount"]

                if "access_card" in temp_json.keys():
                    bcaAccessCardNumber = temp_json["access_card"]
                if "topup_code" in temp_json.keys():
                    bcaAccessCode = temp_json["topup_code"]

                amount = topup_amount

            LOG.fw("044:bcaAccessCardNumber respon = ", bcaAccessCardNumber)
            LOG.fw("044:bcaAccessCode respon = ", bcaAccessCode)

            ErrorCode = code
            resultStr = bca_topup_session2(topup_session)
            LOG.fw("044:BCATopupSession2 respon = ", resultStr)
            ErrorCode = resultStr

        resultStr, csn, uid = on_detect()

        if resultStr == "0000":
            datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            topup_amount_hex = format(int(topup_amount), "x")
            resultStr, report = bca_topup1(bcaStaticATD, bcaAccessCardNumber, bcaAccessCode, datenow, topup_amount_hex)
            LOG.fw("044:BCATopup1 respon = ", { "resultStr":resultStr, "report": report})
            ErrorCode = resultStr
            if resultStr == "0000":
                valuetext, ErrMsg = send_update_bca(url, TOKEN, TID, MID, cardno, report, balance, reference_id)
                if valuetext == "1":
                    valuetext = ErrMsg

                dataJ = json.loads(valuetext)

                if "response" in dataJ.keys():
                    temp_json = dataJ["response"]
                    if "code" in temp_json.keys():
                        code = temp_json["code"]

                if "data" in dataJ.keys():
                    temp_json = dataJ["data"]
                    if "confirm_data" in temp_json.keys():
                        confirm_data = temp_json["confirm_data"]

                ErrorCode = code
                if code == "200" or code == 200:
                    resultStr, report = bca_topup_reversal(bcaStaticATD)
                    LOG.fw("044:BCATopupReversal respon = ", { "resultStr":resultStr, "report": report})
                    ErrorCode = resultStr
                    if resultStr == "0000":
                        valuetext, ErrMsg = send_reversal_bca(url, TOKEN, TID, MID, cardno, report, balance, reference_id)
                        if valuetext == "1":
                            valuetext = ErrMsg
                        dataJ = json.loads(valuetext)
                        if "response" in dataJ.keys():
                            temp_json = dataJ["response"]
                            if "code" in temp_json.keys():
                                code = temp_json["code"]

                        
                        ErrorCode = code
                        if code == "200" or code == 200:
                            ErrorCode = "0000"

        ErrorCode = code

    return ErrorCode, cardno, amount, lastbalance, report, ErrMsg

def update_balance_bca_priv(TID, MID, TOKEN):
    global BCA_ACCESS_CARD_NUMBER, BCA_ACCESS_CODE, BCA_ATD, UPDATE_BALANCE_URL
    bcaAccessCardNumber = BCA_ACCESS_CARD_NUMBER
    bcaAccessCode =  BCA_ACCESS_CODE
    bcaStaticATD = BCA_ATD

    cardno = ""
    amount = ""
    lastbalance = ""
    reporttopup = ""
    ErrMsg = ""

    __global_response__ = 0
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    valuetext = ""
    report = ""
    csn = ""
    uid = ""
    balance = 0
    SIGN = 0

    resultStr = prepaid.topup_card_disconnect()
    value = 0
    url = UPDATE_BALANCE_URL
    
    resultStr, balance, cardno, SIGN = prepaid.topup_balance_with_sn()    

    ErrorCode = resultStr
    topup_session = ""
    reference_id = ""
    topup_amount = ""
    confirm_data = ""
    datenow = ""
    ErrMsg = ""

    if resultStr == "0000":
        LOG.fw("044:cardno = ", cardno)
        # LOG.fw("044:uid = ", uid)
        valuetext, ErrMsg = send_check_session_bca(url, TOKEN, TID, MID,cardno)
        if valuetext == "1":
            valuetext = ErrMsg
        
        dataJ = json.loads(valuetext)
        
        code = ""
        updateStatus = ""
        dataToCard = ""

        if "response" in dataJ.keys():
            temp_json = dataJ["response"]
            if "code" in temp_json:
                code = temp_json["code"]
        if "data" in dataJ.keys():
            temp_json = dataJ["data"]
            if "topup_session" in temp_json.keys():
                topup_session = temp_json["topup_session"]
            if "reference_id" in temp_json.keys():
                reference_id = temp_json["reference_id"]
            if "topup_amount" in temp_json.keys():
                topup_amount = temp_json["topup_amount"]
            if "access_card" in temp_json.keys():
                bcaAccessCardNumber = temp_json["access_card"]
            if "topup_code" in temp_json.keys():
                bcaAccessCode = temp_json["topup_code"]

        ErrorCode = code

        if code == "200" or code == 200:
            resultStr = "0000"
        else:
            datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            resultStr, report = bca_topup_session(bcaStaticATD, datenow)
            ErrorCode = resultStr
            LOG.fw("044:BCATopupSession1 respon = ",  { "resultStr":resultStr, "report": report})
            valuetext, ErrMsg = send_session_bca(url, TOKEN, TID,MID, cardno, report)

            if valuetext == "1":
                valuetext = ErrMsg

            dataJ = json.loads(valuetext)

            if "response" in dataJ.keys():
                temp_json = dataJ["response"]
                if "code" in temp_json.keys():
                    code = temp_json["code"]
            if "data" in dataJ.keys():
                temp_json = dataJ["data"]
                if "topup_session" in temp_json.keys():
                    topup_session = temp_json["topup_session"]
                if "reference_id" in temp_json.keys():
                    reference_id = temp_json["reference_id"]
                if "topup_amount" in temp_json.keys():
                    topup_amount = temp_json["topup_amount"]
                if "access_card" in temp_json.keys():
                    bcaAccessCardNumber = temp_json["access_card"]
                if "topup_code" in temp_json.keys():
                    bcaAccessCode = temp_json["topup_code"]
        
        if code == "200" or code == 200:
            amount = topup_amount
            LOG.fw("044:bcaAccessCardNumber respon = ", bcaAccessCardNumber)
            LOG.fw("044:bcaAccessCode respon = ", bcaAccessCode)
            
            resultStr = bca_topup_session2(topup_session)
            LOG.fw("044:BCATopupSession2 respon = ", resultStr)
            ErrorCode = resultStr
            
            if resultStr == "0000":
                resultStr, csn, uid = on_detect()
                if resultStr == "0000":
                    datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    topup_amount_hex = format(int(topup_amount), "x")
                    resultStr, report = bca_topup1(bcaStaticATD, bcaAccessCardNumber, bcaAccessCode, datenow, topup_amount_hex)
                    LOG.fw("044:BCATopup1 respon = ", { "resultStr":resultStr, "report": report})
                    ErrorCode = resultStr
                    if resultStr == "0000":
                        valuetext, ErrMsg = send_update_bca(url, TOKEN, TID, MID, cardno, report, balance, reference_id)
                        if valuetext == "1":
                            valuetext = ErrMsg

                        dataJ = json.loads(valuetext)

                        if "response" in dataJ.keys():
                            temp_json = dataJ["response"]
                            if "code" in temp_json.keys():
                                code = temp_json["code"]
                        if "data" in dataJ.keys():
                            temp_json = dataJ["data"]
                            if "confirm_data" in temp_json.keys():
                                confirm_data = temp_json["confirm_data"]

                        ErrorCode = code
                        if code == "200" or code == 200:
                            resultStr, balance_not_used, report = bca_topup2(confirm_data)
                            LOG.fw("044:BCATopup2 respon = ", { "resultStr":resultStr, "report": report})
                            ErrorCode = resultStr

                            lastreportfailed = False
                            if resultStr == "0000":
                                if report == "":
                                    LOG.fw("044:BCATopup2 report empty")
                                    report = bca_topup_lastreport()
                                    LOG.fw("044:BCATopup2 BCATopupLastReport = ", report)
                                    if report == "":
                                        lastreportfailed = True
                                        resultStr, report = topup_card_info(bcaStaticATD)
                                        LOG.fw("044:BCATopup2 BCATopupCardInfo = ", report)
                                        if report == "":
                                            ErrMsg = "BCATopup2_BCATopupLastReport_Failed"
                                lastbalance = int(balance) + int(amount)
                                reporttopup = report
                                valuetext, ErrMsg = send_confirm_bca(url, TOKEN, TID, MID, cardno, report, lastbalance, reference_id)
                                if valuetext == "1":
                                    valuetext = ErrMsg
                                
                                dataJ = json.loads(valuetext)
                                if "response" in dataJ.keys():
                                    tempJ = dataJ["response"]
                                    if "code" in tempJ.keys():
                                        code = tempJ["code"]
                                
                                ErrorCode = code
                                if code == "200" or code == 200:
                                    ErrorCode = "0000"

                                # valuetext = send_conde
                        else:
                            resultStr, report = bca_topup_reversal(bcaStaticATD)
                            LOG.fw("044:BCATopupReversal respon = ", { "resultStr":resultStr, "report": report})
                            ErrorCode = resultStr
                            if resultStr == "0000":
                                valuetext,ErrMsg = send_reversal_bca(url, TOKEN, TID, MID, cardno, report, balance, reference_id)
                                if valuetext == "1":
                                    valuetext = ErrMsg
                                dataJ = json.loads(valuetext)
                                if "response" in dataJ.keys():
                                    code = dataJ["response"]
                                
                                ErrorCode = code
                                if code == "200" or code == 200:
                                    ErrMsg = "UpdateAPI_Failed_Reversal_Success"
                                else:
                                    ErrMsg = "UpdateAPI_Failed_Reversal_Failed"
                            else:
                                ErrMsg = "UpdateAPI_Failed_Card_Reversal_Failed"
                    else:
                        resultStr, report = bca_topup_reversal(bcaStaticATD)
                        LOG.fw("044:BCATopupReversal respon = ", { "resultStr":resultStr, "report": report})
                        ErrorCode = resultStr
                        if resultStr == "0000":
                            valuetext, ErrMsg = send_reversal_bca(url, TOKEN, TID, MID, cardno, report, balance, reference_id)
                            if valuetext == "1":
                                valuetext = ErrMsg
                            dataJ = json.loads(valuetext)
                            if "response" in dataJ.keys():
                                code = dataJ["response"]
                            
                            ErrorCode = code
                            if code == "200" or code == 200:
                                ErrMsg = "BCATopup1_Failed_Reversal_Success"
                            else:
                                ErrMsg = "BCATopup1_Failed_Reversal_Failed"
                        else:
                            ErrMsg = "BCATopup1_Failed_Card_Reversal_Failed"
        else:
            resultStr = '8309'
            ErrMsg = 'BCA_TOPUP_SESSION_ERROR'
    
    ErrorCode = resultStr

    return ErrorCode, cardno, amount, lastbalance, reporttopup, ErrMsg

def send_check_session_bca(URL_Server, token, tid, mid, card_no):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/check-session"
        payload = {"token":token.decode('utf-8'), "tid":tid.decode('utf-8'), "mid":mid.decode('utf-8'), "card_no":card_no}
        LOG.fw(":CheckSessionBCA url = ", sURL)
        LOG.fw(":CheckSessionBCA json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":CheckSessionBCA respon = ", ValueText)

        errorcode = "0000"

        return ValueText, errorcode
    except Exception as ex:
        errorcode = "CheckSessionBCA error: {0}".format(ex)
        return "1", errorcode

def send_session_bca(URL_Server, token, tid, mid, card_no, session_data):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/get-session"
        payload = {"token":token.decode('utf-8'), "tid":tid.decode('utf-8'), "mid":mid.decode('utf-8'), "card_no":card_no, "session_data": session_data}
        LOG.fw(":SessionBCA url = ", sURL)
        LOG.fw(":SessionBCA json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":SessionBCA respon = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = "SessionBCA error: {0}".format(ex)
        return "1", errorcode

def send_confirm_bca(URL_Server, token, tid, mid, card_no, confirm_data, last_balance, reference_id):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/confirm"
        payload = {"token":token.decode('utf-8'), "tid":tid.decode('utf-8'), "mid":mid.decode('utf-8'), "card_no":card_no, "confirm_data": confirm_data, "last_balance":last_balance, "reference_id":reference_id}
        LOG.fw(":ConfirmBCA url = ", sURL)
        LOG.fw(":ConfirmBCA json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":ConfirmBCA respon = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = "ConfirmBCA error: {0}".format(ex)
        return "1", errorcode

def send_reversal_bca(URL_Server, token, tid, mid, card_no, reversal_data, last_balance, reference_id):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/reversal"
        payload = {"token":token.decode('utf-8'), "tid":tid.decode('utf-8'), "mid":mid.decode('utf-8'), "card_no":card_no, "reversal_data": reversal_data, "last_balance":last_balance, "reference_id":reference_id}
        LOG.fw(":ReversalBCA url = ", sURL)
        LOG.fw(":ReversalBCA json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":ReversalBCA respon = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = "ReversalBCA error: {0}".format(ex)
        return "1", errorcode

def send_update_bca(URL_Server, token, tid, mid, card_no, topup_data, prev_balance, reference_id):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/update"
        payload = {"token":token.decode('utf-8'), "tid":tid.decode('utf-8'), "mid":mid.decode('utf-8'), "card_no":card_no, "topup_data": topup_data, "prev_balance":prev_balance, "reference_id":reference_id}
        LOG.fw(":UpdateBCA url = ", sURL)
        LOG.fw(":UpdateBCA json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":UpdateBCA respon = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = "UpdateBCA error: {0}".format(ex)
        return "1", errorcode

def bca_topup_session(ATD, datetimes):
    return prepaid.topup_bca_session1(ATD.encode('utf-8'), datetimes.encode('utf-8'))

def bca_topup_session2(session):
    return prepaid.topup_bca_session2(session.encode('utf-8'))

def bca_topup1(ATD, accescard, accescode, datetimes, amounthex):
    amounthex = amounthex.zfill(8)
    return prepaid.topup_bca_topup1(ATD.encode('utf-8'), accescard.encode('utf-8'), accescode.encode('utf-8'), datetimes.encode('utf-8'), amounthex.encode('utf-8'))

def bca_topup2(strconfirm):
    confirm1 = strconfirm[0:200]
    confirm2 = strconfirm[200:]
    res_str, balance, respon, debErrorStr = prepaid.topup_bca_topup2(confirm1, confirm2)
    report = utils.remove_special_character(respon)
    LOG.fw("BCATopup2 Report Out SC = ", report)
    report = utils.fix_report_leave_space(report)
    report_length = len(report.split('\n'))
    LOG.fw("BCATopup2 Report Length= ", report_length)
    if len(report.split('\n')) > 1:
        report = report[1]
    report = report.split(' ')[0][-512:]
    LOG.fw("BCATopup2 Clean Report = ", report)
    lastbalance = balance
    return res_str, lastbalance, report

def bca_topup_lastreport():
    res_str, respon = prepaid.topup_bca_lastreport()
    report = utils.fix_report(respon)
    return res_str, report

def bca_topup_reversal(ATD):
    res_str, report = prepaid.topup_bca_reversal(ATD)
    report = utils.fix_report(report)
    return res_str, report
