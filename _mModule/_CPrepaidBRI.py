__author__ = 'wahyudi@multidaya.id'

from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidUtils as utils
from _mModule import _CPrepaidLog as LOG
from _cConfig import _Common
import pprint
import requests
import json
from time import sleep

UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL_DEV
if _Common.LIVE_MODE is True:
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL

if _Common.PTR_MODE is True:
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL
    
TIMEOUT_REQUESTS = 50


def update_balance_bri(param, __global_response__):
    # LOG.fw("024:Mulai")
    Param = param.split('|')
    if len(Param) == 4:
        C_TID = Param[0]
        C_MID = Param[1]
        C_TOKEN = Param[2]
        C_SAMSLOT = Param[3]
    else:
        LOG.fw("024:Missing Parameter", param)
        raise SystemError("024:Missing Parameter: "+param)
    
    LOG.fw("024:Parameter = ", C_TID)
    LOG.fw("024:Parameter = ", C_MID)
    LOG.fw("024:Parameter = ", C_TOKEN)
    LOG.fw("024:Parameter = ", C_SAMSLOT)

    cardno = ""
    amount = "0"
    lastbalance = ""

    result_str, errmsg, cardno, amount, lastbalance, bri_token, reffnohost, CodeStatus = update_balance_bri_priv(C_TID, C_MID, C_TOKEN, C_SAMSLOT, cardno, amount)

    __global_response__["Result"] = result_str
    if result_str == "0000":
        __global_response__["Response"] = str(cardno) + "|" + str(amount) + "|" + str(lastbalance) + "|" + bri_token + "|" + reffnohost + "|" + CodeStatus
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("024:Response = ", cardno)
        LOG.fw("024:Response = ", amount)
        LOG.fw("024:Response = ", lastbalance)

        LOG.fw("024:Result = ", result_str)
        LOG.fw("024:Sukses")
    else:
        __global_response__["Response"] = errmsg + "|" + bri_token + "|" + reffnohost + "|" + CodeStatus
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("024:Response = ", errmsg, True)
        LOG.fw("024:Result = ", result_str, True)
        LOG.fw("024:Gagal", None, True)
    
    return __global_response__


def update_balance_bri_priv(TID, MID, TOKEN, SAMSLOT, cardno, amount):
    global UPDATE_BALANCE_URL
    msg = ""
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""
    Status = ""
    CodeStatus = ""
    CodeDesc = ""
    jsonD = []
    lastbalance = 0

    try:
        rapdu = ""
        sapdu = ""
        uid = ""
        data = ""
        attr = ""
        balance = 0
        SIGN = 0
        reffnohost = ""
        sam_auth = ""
        card_auth = ""
        card_topup = ""
        card_log_topup = ""
        card_write_trx = ""
        card_commit_trx = ""
        jsonD = None
        code = ""
        dataToCard = ""
        url = UPDATE_BALANCE_URL

        resultStr, balance, cardno, SIGN = prepaid.topup_balance_with_sn()        

        if resultStr == "0000":
            lastbalance = balance
            prepaid.topup_card_disconnect()
            resultStr, data = get_bri_card_token()
            if resultStr == "0000":
                resultStr, ErrMsg = do_send_update_balance_bri(url, TOKEN, TID, MID, cardno, data, balance)

                if resultStr == "1":
                    msg = ErrMsg
                else:                    
                    try:
                        jsonD = json.loads(resultStr)
                        if type(jsonD) is dict:
                            if "response" in jsonD.keys():
                                code = str(jsonD["response"]["code"])
                            else:
                                msg = "result don't have response: {0}".format(str(jsonD))
                                resultStr = "1"

                            resultStr = str(code)
                            if "data" in jsonD.keys():
                                reffnohost = jsonD["data"]["reff_no_host"]
                                dataToCard = jsonD["data"]["actions"]
                                
                                if type(dataToCard) is dict:
                                    sam_auth = dataToCard["sam_auth"]
                                    card_auth = dataToCard["card_auth"]
                                    card_topup = dataToCard["card_topup"]
                                    card_log_topup = dataToCard["card_log_topup"]
                                    card_write_trx = dataToCard["card_write_trx"]
                                    card_commit_trx = dataToCard["card_commit_trx"]
                                else:
                                    msg = "actions invalid type: {0}".format(str(dataToCard))
                                    resultStr = "1"                    
                            else:
                                msg = "result don't have data: {0}".format(str(jsonD))
                                resultStr = "1"
                    # except json.JSONDecodeError:
                    #     msg = "Invalid JSON: {0}".format(str(resultStr))
                    #     resultStr = "1"
                    except Exception as ex:
                        msg = "Error while parse: {0}".format(ex)                    
                        resultStr = "1"

                    if resultStr == "200":
                        resultStr, rapdu = prepaid.send_apdu_cmd(SAMSLOT, sam_auth)

                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                            sapdu = rapdu[-32:]
                            sapdu = b"90AF000010" + sapdu.encode("utf-8") + b"00"
                            resultStr, rapdu = prepaid.send_apdu_cmd("255", sapdu)
                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                resultStr, rapdu = prepaid.send_apdu_cmd("255", card_topup)
                                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                    resultStr, rapdu = prepaid.send_apdu_cmd("255", card_log_topup)
                                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                        resultStr, rapdu = prepaid.send_apdu_cmd("255", card_write_trx)
                                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                            resultStr, rapdu = prepaid.send_apdu_cmd("255", card_commit_trx)
                                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                                resultStr, ErrMsg = do_send_confirm_bri(url, TOKEN, TID, MID, cardno, data, reffnohost)
                                                if resultStr == "1":
                                                    resultStr = ErrMsg
                                                try:
                                                    jsonD = json.loads(resultStr)
                                                except:
                                                    jsonD = resultStr

                                                if type(jsonD) is dict:
                                                    if "response" in jsonD.keys():
                                                        code = str(jsonD["response"]["code"])
                                                    else:
                                                        raise SystemError("result don't have response: {0}".format(jsonD))
                                                    
                                                    if code == "200":
                                                        dataToCard = str(jsonD["data"])
                                                        amount = int(jsonD["data"]["amount"])
                                                        lastbalance = int(balance) + amount
                                                    
                                                    resultStr = code

                                                    if resultStr == "200":
                                                        resultStr = "0000"
                                                        msg = "SUCCESS TOPUP"
                                                    else:
                                                        msg = ErrMsg 
                    elif jsonD:
                        if "status" in jsonD["data"].keys():
                            if "code" in jsonD["data"]["status"].keys():
                                CodeStatus = jsonD["data"]["status"]["code"]
                                if "desc" in jsonD["data"]["status"].keys():
                                    msg = jsonD["data"]["status"]["desc"]
                        
            LOG.fw("CodeStatus = ",CodeStatus)
            LOG.fw("msg = ",msg)
            LOG.fw("ErrMsg = ",ErrMsg)
            LOG.fw("resultStr = ",resultStr)


    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg, cardno, amount, lastbalance, data, reffnohost, CodeStatus


def reversal_bri(param, __global_response__):
    # LOG.fw("024:Mulai")
    Param = param.split('|')
    if len(Param) == 6:
        C_TID = Param[0]
        C_MID = Param[1]
        C_TOKEN = Param[2]
        C_SAMSLOT = Param[3]
        C_BRI_TOKEN = Param[4]
        C_REFFNOHost = Param[5]
    else:
        LOG.fw("064:Missing Parameter", param)
        raise SystemError("064:Missing Parameter: "+param)
    
    LOG.fw("064:Parameter = ", C_TID)
    LOG.fw("064:Parameter = ", C_MID)
    LOG.fw("064:Parameter = ", C_TOKEN)
    LOG.fw("064:Parameter = ", C_SAMSLOT)
    LOG.fw("064:Parameter = ", C_BRI_TOKEN)
    LOG.fw("064:Parameter = ", C_REFFNOHost)

    cardno = ""
    amount = "0"
    lastbalance = ""

    result_str, errmsg, cardno, amount, lastbalance = reversal_bri_priv(C_TID, C_MID, C_TOKEN, C_SAMSLOT, cardno, amount, lastbalance, C_BRI_TOKEN, C_REFFNOHost)

    __global_response__["Result"] = result_str
    if result_str == "0000":
        __global_response__["Response"] = str(cardno) + "|" + str(amount) + "|" + str(lastbalance) 
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("064:Response = ", cardno)
        LOG.fw("064:Response = ", amount)
        LOG.fw("064:Response = ", lastbalance)

        LOG.fw("064:Result = ", result_str)
        LOG.fw("064:Sukses")
    else:
        __global_response__["Response"] = errmsg
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("064:Response = ", errmsg, True)
        LOG.fw("064:Result = ", result_str, True)
        LOG.fw("064:Gagal", None, True)


def reversal_bri_priv(TID,MID,TOKEN,SAMSLOT,cardno, amount, lastbalance, bri_token, reffnohost):
    global UPDATE_BALANCE_URL
    msg = ""
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""
    Status = ""
    CodeStatus = ""
    CodeDesc = ""
    jsonD = []
    

    try:
        rapdu = ""
        sapdu = ""
        uid = ""
        attr = ""
        balance = 0
        SIGN = 0
        sam_auth = ""
        card_auth = ""
        card_topup = ""
        card_log_topup = ""
        card_write_trx = ""
        card_commit_trx = ""
        jsonD = None
        code = ""
        dataToCard = ""
        url = UPDATE_BALANCE_URL

        resultStr, balance, cardno, SIGN = prepaid.topup_balance_with_sn()        
        sleep(1)

        #Start Reversal
        resultStr, ErrMsg = do_send_reversal_bri(url, TOKEN, TID, MID, cardno, bri_token, reffnohost)
        jsonT = resultStr

        if resultStr == "1":
            _Common.LAST_BRI_ERR_CODE = '32'
            msg = ErrMsg
        else:
            try:
                jsonD = json.loads(resultStr)
                if "response" in jsonD.keys():
                    code = str(jsonD["response"]["code"])
                else:
                    msg = "result don't have response: {0}".format(str(jsonD))
                    resultStr = "1"

                if "data" in jsonD.keys():
                    dataToCard = str(jsonD["data"])
                else:
                    msg = "result don't have data: {0}".format(str(jsonD))
                    resultStr = "1"

                resultStr = str(code)
            # except json.JSONDecodeError:
            #     msg = "Invalid JSON: {0}".format(str(resultStr))
            #     resultStr = "1"
            except Exception as ex:
                msg = "Error while parse: {0}".format(ex)                    
                resultStr = "1"
            
            if resultStr == "200":
                resultStr = '0000'
                msg = "SUCCESS REVERSAL\n" + jsonT
            else:
                msg = "FAILED REVERSAL\n" + jsonT 

    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg, cardno, amount, lastbalance


def get_bri_card_token():
    res_str, CardData = prepaid.topup_get_tokenbri()
    _CardData = utils.fix_report(CardData)
    LOG.fw("_CardData = ", _CardData)
    CardData = _CardData
    return res_str, CardData


def do_send_update_balance_bri(URL_Server, token, tid, mid, card_no, random_token, last_balance):
    global TIMEOUT_REQUESTS
    errorcode = ""
    try:
        sURL = URL_Server + "topup-bri/update"
        payload = {
            "token":token, 
            "tid":tid, 
            "mid":mid, 
            "card_no":card_no, 
            "random_token": random_token,
            "prev_balance": last_balance
            }
        LOG.fw(":updatebalancebri url = ", sURL)
        LOG.fw(":updatebalancebri json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":updatebalancebri = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = ":updatebalancebri error: {0}".format(ex)
        return "1", errorcode


def do_send_confirm_bri(URL_Server, token, tid, mid, card_no, random_token, reff_no_host):
    global TIMEOUT_REQUESTS
    errorcode = ""
    try:
        sURL = URL_Server + "topup-bri/confirm"
        payload = {
            "token":token, 
            "tid":tid, 
            "mid":mid, 
            "card_no":card_no, 
            "random_token": random_token, 
            "reff_no_host": reff_no_host
            }
        LOG.fw(":confirmbri url = ", sURL)
        LOG.fw(":confirmbri json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":confirmbri = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = ":confirmbri error: {0}".format(ex)
        return "1", errorcode


def do_send_reversal_bri(URL_Server, token, tid, mid, card_no, random_token, reff_no_host):
    global TIMEOUT_REQUESTS
    errorcode = ""
    try:
        sURL = URL_Server + "topup-bri/reversal"
        payload = {"token":token, "tid":tid, "mid":mid, "card_no":card_no, "random_token": random_token, "reff_no_host": reff_no_host}
        LOG.fw(":reversalbri url = ", sURL)
        LOG.fw(":reversalbri json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":reversalbri = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = ":reversalbri error: {0}".format(ex)
        return "1", errorcode


def do_send_refund_bri(URL_Server, token, tid, mid, card_no, reff_no_host):
    global TIMEOUT_REQUESTS
    errorcode = ""
    try:
        sURL = URL_Server + "topup-bri/refund"
        payload = {"token":token, "tid":tid, "mid":mid, "card_no":card_no, "reff_no_host": reff_no_host}
        LOG.fw(":refundbri url = ", sURL)
        LOG.fw(":refundbri json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text

        LOG.fw(":refundbri = ", ValueText)

        errorcode = "0000"
        return ValueText, errorcode
    except Exception as ex:
        errorcode = ":refundbri error: {0}".format(ex)
        return "1", errorcode


def bri_card_get_log(param, __global_response__):
    LOG.fw("025:Mulai")

    Param = param.split('|')
    if len(Param) > 0:
        C_SAMSLOT = Param[0]
    else:
        LOG.fw("025:Missing Parameter", param)
        raise SystemError("025:Missing Parameter: "+param)
    
    LOG.fw("025:Parameter = ", C_SAMSLOT)

    errmsg = ""

    if len(Param) > 1 and Param[1] == 'MODE_RAW':
        result_str, errmsg = get_raw_log_bri_priv(C_SAMSLOT, errmsg)
    else:
        result_str, errmsg = get_log_bri_priv(C_SAMSLOT, errmsg)
        
    __global_response__["Result"] = result_str
    if result_str == "0000":
        __global_response__["Response"] = errmsg
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("025:Response = ", errmsg)

        LOG.fw("025:Result = ", result_str)
        LOG.fw("025:Sukses")
    else:
        __global_response__["Response"] = errmsg
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("025:Response = ", errmsg, True)
        LOG.fw("025:Result = ", result_str, True)
        LOG.fw("025:Gagal", None, True)


def sort_data_by_datetime(h=[]):
    if len(h) == 0: return h
    sorted_key = []
    for row in h:
        datetime = row[32:44]
        sorted_key.append(datetime)
    sorted_key.sort(reverse=True)
    sorted_result = []
    for key in sorted_key:
        for row in h:
            if str(key) in row:
                sorted_result.append(row)
    return sorted_result
    

def get_log_bri_priv(slot, msg):
    resultStr = ""
    resreport = ""
    # slot => Not used in this new function
    try:
        prepaid.topup_card_disconnect()
        resultStr, history = prepaid.get_card_history('BRI')
        if resultStr == '0000' or resultStr.upper() == "911C":
            resultStr = "0000"
            history = sort_data_by_datetime(history)
            for item in history:
                mid = item[:16]
                tid = item[16:32]
                trx_date = item[32:38]
                trx_time = item[38:44]
                trx_type = item[44:46]
                amount = utils.getint(item[46:52])
                prev_balance = utils.getint(item[52:58])
                last_balance = utils.getint(item[58:64])            
                itemDec = str(mid) + "|" + str(tid) + "|" + str(trx_date) + "|" + str(trx_time) + "|" + str(trx_type) + "|" + str(amount) + "|" + str(prev_balance) + "|" + str(last_balance)
                resreport = resreport + itemDec + "#"
                msg = resreport

    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg


def get_raw_log_bri_priv(slot, msg=''):
    resultStr = ""
    resreport = ""
    # slot => Not used in this new function
    try:
        prepaid.topup_card_disconnect()
        resultStr, history = prepaid.get_card_history('BRI')
        if resultStr == '0000' or resultStr.upper() == "911C":
            resultStr = "0000"
            history = sort_data_by_datetime(history)
        msg = ",".join(history)            

    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg
