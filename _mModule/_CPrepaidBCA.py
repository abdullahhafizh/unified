__author__ = 'wahyudi@multidaya.id'

from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidUtils as utils
from _mModule import _CPrepaidLog as LOG
from _nNetwork import _HTTPAccess
from _cConfig import _Common
from time import sleep
import json
import requests
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

if _Common.PTR_MODE is True:
    BCA_ATD = "01SMUDAINACbIhPF92u0C38pOBKjQSFiZQHEQUZX0jWfA"
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL
    BCA_ACCESS_CARD_NUMBER = "NOT_SET"
    BCA_ACCESS_CODE = "NOT_SET"

# New Param
BCA_ACTIVE_TOPUP_SESSION = ''
BCA_LAST_REFF_ID = ''
BCA_LAST_TOPUP_AMOUNT = 0

TIMEOUT_REQUESTS = 50


#046
def update_bca(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 2:
        C_TID = Param[0].encode('utf-8')
        C_MID = Param[1].encode('utf-8')
    else:
        LOG.fw("045:Missing Parameter", param)
        raise SystemError("045:Missing Parameter: "+param)

    LOG.fw("046:Parameter = ", C_TID)
    LOG.fw("046:Parameter = ", C_MID)

    res_str = prepaid.topup_bca_lib_config(C_TID, C_MID)

    # if res_str != "0000":
    #     prepaid.topup_done()

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
    res_str, CardUID, CardNo = prepaid.get_card_sn()

    LOG.fw("ONDetect CARDNO = ", CardNo)
    LOG.fw("ONDetect CARD_UID = ", CardUID)

    if CardUID[-6:] == "000000":
        CardUID = CardUID[0:8]
    else:
        CardUID = CardUID[0:14]

    return res_str, CardNo, CardUID

def topup_card_info(ATD):
    res_str, report = prepaid.topup_bca_lib_cardinfo(ATD)
    return res_str, report

#044
def update_balance_bca(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 3:
        C_TID = Param[0].encode('utf-8')
        C_MID = Param[1].encode('utf-8')
        C_TOKEN = Param[2].encode('utf-8')
    else:
        LOG.fw("044:Missing Parameter", param)
        raise SystemError("044:Missing Parameter: "+param)
        
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
        LOG.fw("045:Missing Parameter", param)
        raise SystemError("045:Missing Parameter: "+param)

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
    global BCA_ACCESS_CARD_NUMBER, BCA_ACCESS_CODE, BCA_ATD, UPDATE_BALANCE_URL, BCA_ACTIVE_TOPUP_SESSION
    
    bcaStaticATD = BCA_ATD

    resultStr = ""
    ErrorCode = ""
    valuetext = ""
    amount = int(BCA_LAST_TOPUP_AMOUNT)

    resultStr = prepaid.topup_card_disconnect()
    url = UPDATE_BALANCE_URL

    resultStr, lastbalance, cardno, bid = prepaid.topup_balance_with_sn()

    ErrorCode = resultStr
    ErrMsg = ""

    if resultStr == "0000":
        resultStr, report = bca_topup_reversal(bcaStaticATD)
        LOG.fw("045:BCATopupReversal = ", { "resultStr": resultStr, "report": report})
        ErrorCode = resultStr
        
        if resultStr == "0000":
            valuetext, ErrMsg = send_post_reversal_bca(url, cardno, report, lastbalance, BCA_LAST_REFF_ID)
            if valuetext == -1:
                valuetext = ErrMsg

            dataJ = json.loads(valuetext)
            if "response" in dataJ.keys():
                temp_json = dataJ["response"]
            if "code" in temp_json.keys():
                code = temp_json["code"]
            if "message" in temp_json.keys():
                ErrMsg = temp_json["message"]
    
            ErrorCode = code
            if code == "200" or code == 200:
                ErrorCode = "0000"
                
    return ErrorCode, cardno, amount, lastbalance, report, ErrMsg


def update_balance_bca_priv(TID, MID, TOKEN):
    global BCA_ACCESS_CARD_NUMBER, BCA_ACCESS_CODE, BCA_ATD, UPDATE_BALANCE_URL, BCA_ACTIVE_TOPUP_SESSION, BCA_LAST_REFF_ID, BCA_LAST_TOPUP_AMOUNT
    
    bcaAccessCardNumber = BCA_ACCESS_CARD_NUMBER
    bcaAccessCode =  BCA_ACCESS_CODE
    bcaStaticATD = BCA_ATD

    cardno = ""
    amount = ""
    lastbalance = ""
    reporttopup = ""
    ErrMsg = ""

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
    success_topup = False

    if resultStr == "0000":
        LOG.fw("044:cardno = ", cardno)
        LOG.fw("044:uid = ", uid)
        # Failure Here
        valuetext, ErrMsg = do_check_session_bca(url, cardno)
        if valuetext == -1:
            valuetext = ErrMsg
            
        dataJ = json.loads(valuetext)
        
        code = ""
        message = ""
        updateStatus = ""
        dataToCard = ""

        if "response" in dataJ.keys():
            temp_json = dataJ["response"]
            if "code" in temp_json.keys():
                code = temp_json["code"]
            if "message" in temp_json.keys():
                message = temp_json["message"]
        
        if "No Pending Balance" in message:
            raise SystemError("044:No Pending Balance: "+valuetext)
        
        if "Configuration Not Found" in message:
            raise SystemError("044:Missing Host Configuration: "+valuetext)

                    
        if "data" in dataJ.keys():
            temp_json = dataJ["data"]
            if "topup_session" in temp_json.keys():
                topup_session = temp_json["topup_session"]
                BCA_ACTIVE_TOPUP_SESSION = topup_session
            if "reference_id" in temp_json.keys():
                reference_id = temp_json["reference_id"]
                BCA_LAST_REFF_ID = reference_id
                _Common.LAST_BCA_REFF_ID = BCA_LAST_REFF_ID
            if "topup_amount" in temp_json.keys():
                topup_amount = temp_json["topup_amount"]
                BCA_LAST_TOPUP_AMOUNT = topup_amount
            if "access_card" in temp_json.keys():
                bcaAccessCardNumber = temp_json["access_card"]
            if "topup_code" in temp_json.keys():
                bcaAccessCode = temp_json["topup_code"]

            amount = topup_amount
        
        LOG.fw("044:bcaAccessCardNumber = ", bcaAccessCardNumber)
        LOG.fw("044:bcaAccessCode = ", bcaAccessCode)

        ErrorCode = code

        if code == "200" or code == 200:
            resultStr = "0000"
        else:
            datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            resultStr, report = bca_lib_topup_session(bcaStaticATD, datenow)
            ErrorCode = resultStr
            LOG.fw("044:BCATopupSession1 = ", { "rc": resultStr, "report": report})
            valuetext, ErrMsg = do_get_session_bca(url, cardno, report)

            if valuetext == -1:
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
                    BCA_ACTIVE_TOPUP_SESSION = topup_session
                if "reference_id" in temp_json.keys():
                    reference_id = temp_json["reference_id"]
                    BCA_LAST_REFF_ID = reference_id
                    _Common.LAST_BCA_REFF_ID = BCA_LAST_REFF_ID
                if "topup_amount" in temp_json.keys():
                    topup_amount = temp_json["topup_amount"]
                    BCA_LAST_TOPUP_AMOUNT = topup_amount
                if "access_card" in temp_json.keys():
                    bcaAccessCardNumber = temp_json["access_card"]
                if "topup_code" in temp_json.keys():
                    bcaAccessCode = temp_json["topup_code"]

                amount = topup_amount

            LOG.fw("044:bcaAccessCardNumber = ", bcaAccessCardNumber)
            LOG.fw("044:bcaAccessCode = ", bcaAccessCode)

            ErrorCode = code
            resultStr = bca_lib_topup_session2(topup_session)
            LOG.fw("044:BCATopupSession2 = ", resultStr)
            ErrorCode = resultStr

        if code == "200" or code == 200:
            # Release Detect Card
            # if resultStr == "0000":
            resultStr, csn, uid = on_detect()

            if resultStr == "0000":
                datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                topup_amount_hex = format(int(topup_amount), "x")
                resultStr, report = bca_lib_topup1(bcaStaticATD, bcaAccessCardNumber, bcaAccessCode, datenow, topup_amount_hex)
                LOG.fw("044:BCATopup1 = ", { "rc": resultStr, "report": report})
                ErrorCode = resultStr
                if resultStr == "0000":
                    valuetext, ErrMsg = do_post_update_bca(url, cardno, report, balance, reference_id)
                    if valuetext == -1:
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
                        resultStr, last_balance, report = bca_lib_topup2(confirm_data)
                        # TODO: Must Send ACK Data Into BCA Host
                        # High Potential Not Receiving Return
                        LOG.fw("044:BCATopup2 = ", {"rc": resultStr, "report": report})
                        ErrorCode = resultStr
                            
                        # Normal Success
                        if resultStr == "0000" and len(report) == 512:
                            success_topup = True
                            lastbalance = (int(balance) + int(amount))
                                
                        # Not Success 0000 But Have Report
                        # elif cardno in report:
                        #     success_topup = False
                        #     lastbalance = int(balance)
                                
                        # Report 0000 But Have No Report
                        elif report == "" or len(report) != 512:
                            resultStr, report = bca_topup_lastreport()
                            LOG.fw("044:BCATopup2 BCATopupLastReport = ", report)
                                    
                            if len(report) == 512 and cardno in report:
                                resultStr = "0000" 
                                success_topup = True
                                lastbalance = (int(balance) + int(amount))
                            elif report == "" or len(report) != 512:
                                success_topup = False
                                resultStr, report = topup_card_info(bcaStaticATD)
                                LOG.fw("044:BCATopup2 BCATopupCardInfo = ", report)
                                # if report == "" or len(report) != 512:
                                #     report = "0" * 512
                                # Balance Not Changes
                                lastbalance = int(balance)
                            
                        if not success_topup:
                            _Common.LAST_BCA_ERR_CODE = '42'
                                    
                        # Must Call Confirm Whatever The Topup Result
                        reporttopup = report
                        valuetext, ErrMsg = send_post_confirm_bca(url, cardno, report, lastbalance, reference_id, success_topup)

                    else:
                        _Common.LAST_BCA_ERR_CODE = '41'
                        resultStr, report = bca_topup_reversal(bcaStaticATD)
                        LOG.fw("044:BCATopupReversal = ", {"rc": resultStr, "report": report})
                        ErrorCode = resultStr
                        if resultStr == "0000":
                            valuetext, ErrMsg = send_post_reversal_bca(url, cardno, report, balance, reference_id)
                            if valuetext == -1:
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
                            _Common.LAST_BCA_ERR_CODE = '43'
                            ErrMsg = "UpdateAPI_Failed_Card_Reversal_Failed"
                            
                        resultStr = "0442" 
                else:
                    ErrMsg = "BCATopup1_Failed_Card"

    ErrorCode = resultStr

    return ErrorCode, cardno, amount, lastbalance, reporttopup, ErrMsg


def do_check_session_bca(URL_Server, card_no):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/check-session"
        payload = {
            "token": _Common.CORE_TOKEN, 
            "tid": _Common.TID, 
            "mid": _Common.CORE_MID, 
            "card_no": card_no
            }
        
        LOG.fw(":CheckSessionBCA url = ", sURL)
        LOG.fw(":CheckSessionBCA json = ", payload)

        # errorcode, response = _HTTPAccess.direct_post(url=sURL, param=payload)
        # ValueText = response
        # if errorcode == 200:
        #     errorcode = "0000"
        errorcode = "0000"
        r = requests.post(url=sURL, timeout=TIMEOUT_REQUESTS, json=payload, headers=_HTTPAccess.get_header())

        ValueText = r.text
        LOG.fw(":CheckSessionBCA = ", ValueText)

        return ValueText, errorcode
    except Exception as ex:
        errorcode = "CheckSessionBCA error: {0}".format(ex)
        LOG.fw(":CheckSessionBCA error = ", ex)
        return -1, errorcode


def do_get_session_bca(URL_Server, card_no, session_data):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/get-session"
        payload = {
            "token": _Common.CORE_TOKEN, 
            "tid": _Common.TID, 
            "mid": _Common.CORE_MID, 
            "card_no": card_no, 
            "session_data": session_data
            }
        
        LOG.fw(":GetSessionBCA url = ", sURL)
        LOG.fw(":GetSessionBCA json = ", payload)

        # errorcode, response = _HTTPAccess.direct_post(url=sURL, param=payload)
        # ValueText = response
        # if errorcode == 200:
        #     errorcode = "0000"
        
        errorcode = "0000"
        r = requests.post(url=sURL, timeout=TIMEOUT_REQUESTS, json=payload, headers=_HTTPAccess.get_header())
        ValueText = r.text
        LOG.fw(":GetSessionBCA = ", ValueText)
            
        return ValueText, errorcode
    except Exception as ex:
        errorcode = "GetSessionBCA error: {0}".format(ex)
        LOG.fw(":GetSessionBCA error = ", ex)
        return -1, errorcode


def send_post_confirm_bca(URL_Server, card_no, confirm_data, last_balance, reference_id, success=True):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/confirm"
        payload = {
            "token": _Common.CORE_TOKEN, 
            "tid": _Common.TID, 
            "mid": _Common.CORE_MID, 
            "card_no": card_no, 
            "confirm_data":  confirm_data, 
            "last_balance": last_balance, 
            "reference_id": reference_id
            }
        
        if not success:
            disabled = True
            if disabled:
                LOG.fw(":ConfirmBCA Disabled = ", str(disabled))
                return -1, 'Disabled'
            if len(confirm_data) != 512 or confirm_data == BCA_ATD:
                sleep(.5)
                resultStr, cardInfo = topup_card_info(confirm_data)
                LOG.fw("BCATopupCardInfo = ", resultStr)
                LOG.fw("BCATopupCardInfo = ", cardInfo)
                confirm_data = cardInfo
            payload['card_data'] = confirm_data
            payload.pop('confirm_data')
        
        LOG.fw(":ConfirmBCA url = ", sURL)
        LOG.fw(":ConfirmBCA json = ", payload)

        # errorcode, response = _HTTPAccess.direct_post(url=sURL, param=payload)
        # ValueText = response
        
        errorcode = "0000"
        r = requests.post(url=sURL, timeout=TIMEOUT_REQUESTS, json=payload, headers=_HTTPAccess.get_header())
        ValueText = r.text
        
        # Store To Job If Push Failed
        if r.status_code != 200:
            _Common.LAST_BCA_ERR_CODE = '44'
            payload['endpoint'] = 'topup-bca/confirm'
            _Common.store_request_to_job(name='send_post_confirm_bca', url=sURL, payload=payload)

        LOG.fw(":ConfirmBCA = ", ValueText)

        return ValueText, errorcode
    except Exception as ex:
        errorcode = "ConfirmBCA error: {0}".format(ex)
        LOG.fw(":ConfirmBCA error = ", ex)
        return -1, errorcode


def send_post_reversal_bca(URL_Server, card_no, reversal_data, last_balance, reference_id):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/reversal"
        payload = {
            "token": _Common.CORE_TOKEN, 
            "tid": _Common.TID, 
            "mid": _Common.CORE_MID, 
            "card_no": card_no, 
            "reversal_data": reversal_data, 
            "last_balance": last_balance, 
            "reference_id": reference_id
            }
        LOG.fw(":ReversalBCA url = ", sURL)
        LOG.fw(":ReversalBCA json = ", payload)

        # errorcode, response = _HTTPAccess.direct_post(url=sURL, param=payload)
        # if errorcode == 200:
        #     errorcode = "0000"
        # ValueText = response
        errorcode = '0000'
        r = requests.post(url=sURL, timeout=TIMEOUT_REQUESTS, json=payload, headers=_HTTPAccess.get_header())
        ValueText = r.text
        _Common.LAST_BCA_REVERSAL_RESULT = r.text
        
        LOG.fw(":ReversalBCA = ", ValueText)

        return ValueText, errorcode
    except Exception as ex:
        errorcode = "ReversalBCA error: {0}".format(ex)
        LOG.fw(":ReversalBCA error = ", ex)
        return -1, errorcode


def do_post_update_bca(URL_Server, card_no, topup_data, prev_balance, reference_id):
    global TIMEOUT_REQUESTS

    try:
        sURL = URL_Server + "topup-bca/update"
        payload = {
            "token": _Common.CORE_TOKEN, 
            "tid": _Common.TID, 
            "mid": _Common.CORE_MID, 
            "card_no": card_no, 
            "topup_data": topup_data, 
            "prev_balance": prev_balance, 
            "reference_id": reference_id
            }
        LOG.fw(":UpdateBCA url = ", sURL)
        LOG.fw(":UpdateBCA json = ", payload)

        # errorcode, response = _HTTPAccess.direct_post(url=sURL, param=payload)
        # ValueText = response
        
        errorcode = '0000'
        r = requests.post(url=sURL, timeout=TIMEOUT_REQUESTS, json=payload, headers=_HTTPAccess.get_header())
        ValueText = r.text
        
        LOG.fw(":UpdateBCA = ", ValueText)

        return ValueText, errorcode
    except Exception as ex:
        errorcode = "UpdateBCA error: {0}".format(ex)
        LOG.fw(":UpdateBCA error = ", ex)
        return -1, errorcode


def bca_lib_topup_session(ATD, datetimes):
    return prepaid.topup_bca_lib_session1(ATD.encode('utf-8'), datetimes.encode('utf-8'))


def bca_lib_topup_session2(session):
    return prepaid.topup_bca_lib_session2(session.encode('utf-8'))


def bca_lib_topup1(ATD, accescard, accescode, datetimes, amounthex):
    amounthex = amounthex.zfill(8)
    return prepaid.topup_bca_lib_topup1(ATD.encode('utf-8'), accescard.encode('utf-8'), accescode.encode('utf-8'), datetimes.encode('utf-8'), amounthex.encode('utf-8'))


def bca_lib_topup2(strconfirm):
    confirm1 = strconfirm[0:200]
    confirm2 = strconfirm[200:]
    res_str, balance, response, debErrorStr = prepaid.topup_bca_lib_topup2(confirm1, confirm2)
    report = utils.remove_special_character(response)
    LOG.fw("BCATopup2 Initial Report= ", report)
    report = utils.fix_report_leave_space(report)
    report_split = report.split(' ')
    report_length = len(report_split)
    LOG.fw("BCATopup2 Report Length= ", report_length)
    for x in range(len(report_split)):
        if len(report_split[x]) >= 512:
            report = report_split[x]
            break    
    report = report[-512:]
    LOG.fw("BCATopup2 Clean Report = ", report)
    lastbalance = balance
    return res_str, lastbalance, report


def bca_topup_lastreport():
    res_str, response= prepaid.topup_bca_lib_lastreport()
    report = utils.fix_report(response)
    LOG.fw("BCALastReport Initial Report= ", report)
    report_split = report.split(' ')
    report_length = len(report_split)
    LOG.fw("BCALastReport Report Length= ", report_length)
    for x in range(len(report_split)):
        if len(report_split[x]) >= 512:
            report = report_split[x]
            break    
    report = report[-512:]
    LOG.fw("BCALastReport Clean Report = ", report)
    return res_str, report


def bca_topup_reversal(ATD):
    res_str, report = prepaid.topup_bca_lib_reversal(ATD)
    report = utils.fix_report(report)
    return res_str, report
