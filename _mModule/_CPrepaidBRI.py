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
                        resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, sam_auth)

                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                            sapdu = rapdu[-32:]
                            sapdu = b"90AF000010" + sapdu.encode("utf-8") + b"00"
                            resultStr, rapdu = prepaid.topup_apdusend("255", sapdu)
                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                resultStr, rapdu = prepaid.topup_apdusend("255", card_topup)
                                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                    resultStr, rapdu = prepaid.topup_apdusend("255", card_log_topup)
                                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                        resultStr, rapdu = prepaid.topup_apdusend("255", card_write_trx)
                                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                            resultStr, rapdu = prepaid.topup_apdusend("255", card_commit_trx)
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
        payload = {"token":token, "tid":tid, "mid":mid, "card_no":card_no, "random_token": random_token, "reff_no_host": reff_no_host}
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


def get_log_bri_priv_bak(SAMSLOT, msg):
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""

    try:
        last_card_check = _Common.load_from_temp_data('last-card-check', 'json')
        cardno = last_card_check['card_no']
        LOG.fw("025:cardno = ",cardno)
        uid = ""
        value = ""
        rapdu = ""
        sapdu = ""
        Data = ""
        # resultStr, __value = prepaid.topup_balance()
        # sleep(1)
        # resultStr, __uid, __cardno = prepaid.topup_get_sn()
        # LOG.fw("025:extra_info = ", "-".join([__value, __uid, __cardno]))
        resultStr = prepaid.topup_card_disconnect()
        if resultStr == "0000":
            prepaid.topup_card_disconnect()
            # resultStr, CardData = prepaid.topup_get_tokenbri()
            resultStr = '0000'
            if resultStr == "0000":
                # resultStr, rapdu = prepaid.topup_apdusend("255", "91AF")
                resultStr = '0000'
                if resultStr in ["9000", "9100", "0000", "6700"]:
                    # Select AID
                    resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, "00A4040C09A00000000000000011")
                    if resultStr in ["9000", "9100", "0000"]:
                        # Card Select AID 1
                        resultStr, rapdu = prepaid.topup_apdusend("255", "905A00000301000000")
                        if resultStr in ["9000", "9100", "0000"]:
                            # CARD – Get Card Number, Perso Date & Issuer Code
                            resultStr, rapdu = prepaid.topup_apdusend("255", "90BD000007BD0000000017000000")
                            if resultStr in ["9000", "9100", "0000"]:
                                # CARD – Get Card Status
                                resultStr, rapdu = prepaid.topup_apdusend("255", "90BD0000070100000020000000")
                                resultStr = rapdu[6:10]
                                if resultStr in ["9000", "9100", "0000", "6161"]:
                                    # CARD – Select AID 3
                                    resultStr, rapdu = prepaid.topup_apdusend("255", "905A00000303000000")
                                    if resultStr in ["9000", "9100", "0000"]:
                                        # CARD – Request Key Card 00
                                        resultStr, rapdu = prepaid.topup_apdusend("255", "900A0000010000")
                                        if resultStr in ["9000", "9100", "0000", "91AF"]:
                                            resultStr = rapdu[-4:]
                                            card_key = rapdu[:16]
                                            LOG.fw("025:card_key = ",card_key)
                                            # CARD – Get UID
                                            resultStr, rapdu = prepaid.topup_apdusend("255", "FFCA000000")
                                            resultStr = rapdu[-4:]
                                            if resultStr in ["9000", "9100", "0000", "91AF"]:
                                                uid = rapdu[:14]
                                                LOG.fw("025:uid = ",uid)
                                                sapdu = "80B0000020" + cardno + uid + "FF0000030080000000" + card_key
                                                # SAM – Authenticate Key
                                                resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, sapdu)
                                                if resultStr in ["9000", "9100", "0000", "91AF"]:
                                                    random_key = rapdu[:32]
                                                    LOG.fw("025:random_key = ",random_key)
                                                    sapdu = "90AF000010" + random_key + "00"
                                                    # CARD – Authenticate Card
                                                    resultStr, rapdu = prepaid.topup_apdusend("255", sapdu)
                                                    if resultStr in ["9000", "9100", "0000", "91AF"]:
                                                        # CARD – GET LOG TRANSATION
                                                        resultStr, rapdu = prepaid.topup_apdusend("255", "90BB0000070100000000000000")
                                                        resreport = resreport + rapdu
                                                        if resultStr in ["9000", "9100", "0000", "91AF"]:
                                                            while resultStr in ["9000", "9100", "0000", "91AF"]:
                                                                # resultStr, rapdu = prepaid.topup_apdusend("255", "90AF000000")
                                                                if rapdu[:2] == 'BE': break
                                                                resreport = resreport + rapdu
                    
                n = 64
                result1 = [resreport[i:i+n] for i in range(0, len(resreport), n)]
                for item in result1:
                    MID = item[:16]
                    TID = item[16:32]
                    TRXDATE = item[32:38]
                    TRXTIME = item[38:44]
                    TRXTYPE = item[44:46]
                    AMOUNT = utils.getint(item[46:52])
                    BEFORE = utils.getint(item[52:58])
                    AFTER = utils.getint(item[58:64])            
                    itemDec = str(MID) + "|" + str(TID) + "|" + str(TRXDATE) + "|" + str(TRXTIME) + "|" + str(TRXTYPE) + "|" + str(AMOUNT) + "|" + str(BEFORE) + "|" + str(AFTER)
                    resreport = resreport + itemDec + "#"
                
                if resultStr.upper() == "911C":
                    resultStr = "0000"
                
                msg = resreport

    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg


def get_raw_log_bri_priv(SAMSLOT, msg):
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""

    try:
        cardno = ""
        uid = ""
        value = ""
        rapdu = ""
        sapdu = ""
        Data = ""
        resultStr, value = prepaid.topup_balance()
        sleep(1)
        resultStr, uid, cardno = prepaid.topup_get_sn()
        LOG.fw("025:cardno = ",cardno)
        LOG.fw("025:uid = ",uid)
        if resultStr == "0000":
            prepaid.topup_card_disconnect()
            resultStr, CardData = prepaid.topup_get_tokenbri()
            if resultStr == "0000":
                resultStr, rapdu = prepaid.topup_apdusend("255", "91AF")
                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "6700":
                    resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, "00A4040C09A00000000000000011")
                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                        resultStr, rapdu = prepaid.topup_apdusend("255", "905A00000301000000")
                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                            resultStr, rapdu = prepaid.topup_apdusend("255", "90BD0000070000000017000000")
                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                resultStr, rapdu = prepaid.topup_apdusend("255", "90BD0000070100000020000000")
                                resultStr = rapdu[6:10]
                                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "6161":
                                    resultStr, rapdu = prepaid.topup_apdusend("255", "905A00000303000000")
                                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                        resultStr, rapdu = prepaid.topup_apdusend("255", "900A0000010000")
                                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                            sapdu = "80B0000020" + cardno + uid + "FF0000030080000000" + rapdu
                                            resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, sapdu)
                                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                sapdu = rapdu[32:]
                                                sapdu = "90AF000010" + sapdu + "00"
                                                resultStr, rapdu = prepaid.topup_apdusend("255", sapdu)
                                                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                    resultStr, rapdu = prepaid.topup_apdusend("255", "90BB0000070100000000000000")
                                                    resreport = resreport + rapdu
                                                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                        while resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                            resultStr, rapdu = prepaid.topup_apdusend("255", "90AF000000")
                                                            resreport = resreport + rapdu
                
                n = 64
                result1 = [resreport[i:i+n] for i in range(0, len(resreport), n)]
                
                if resultStr.upper() == "911C":
                    resultStr = "0000"
                
                msg = ",".join(result1)
                
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg



def get_log_bri_priv(SAMSLOT, msg):
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""

    try:
        cardno = ""
        uid = ""
        value = ""
        rapdu = ""
        sapdu = ""
        card_token = ""
        # resultStr, value = prepaid.topup_balance()
        # sleep(1)
        resultStr, uid, cardno = prepaid.topup_get_sn()
        # LOG.fw("025:cardno = ",cardno)
        LOG.fw("025:uid = ",uid)
        # resultStr = prepaid.topup_card_disconnect()
        if resultStr == "0000":
            prepaid.topup_card_disconnect()
            resultStr, card_token = prepaid.topup_get_tokenbri()
            if resultStr == "0000":
                resultStr, rapdu = prepaid.topup_apdusend("255", "91AF")
                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "6700":
                    # Select AID
                    resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, "00A4040C09A00000000000000011")
                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                        # Card Select AID 1
                        resultStr, rapdu = prepaid.topup_apdusend("255", "905A00000301000000")
                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                            # CARD – Get Card Number, Perso Date & Issuer Code
                            resultStr, rapdu = prepaid.topup_apdusend("255", "90BD0000070000000017000000")
                            cardno = rapdu[6:22]
                            LOG.fw("025:cardno = ",cardno)
                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                # CARD – Get Card Status
                                resultStr, rapdu = prepaid.topup_apdusend("255", "90BD0000070100000020000000")
                                resultStr = rapdu[6:10]
                                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "6161":
                                    # CARD – Select AID 3
                                    resultStr, rapdu = prepaid.topup_apdusend("255", "905A00000303000000")
                                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000":
                                        # CARD – Request Key Card 00
                                        resultStr, rapdu = prepaid.topup_apdusend("255", "900A0000010000")
                                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                            # CARD – Get UID
                                            # resultStr, rapdu = prepaid.topup_apdusend("255", "FFCA000000")
                                            # uid = rapdu
                                            # LOG.fw("025:uid = ",uid)
                                            if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                # SAM – Authenticate Key
                                                sapdu = "80B0000020" + cardno + uid + "FF0000030080000000" + rapdu
                                                resultStr, rapdu = prepaid.topup_apdusend(SAMSLOT, sapdu)
                                                if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                    # CARD – Authenticate Card
                                                    sapdu = rapdu[32:]
                                                    sapdu = "90AF000010" + sapdu + "00"
                                                    resultStr, rapdu = prepaid.topup_apdusend("255", sapdu)
                                                    if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                        # CARD – GET LOG TRANSATION
                                                        resultStr, rapdu = prepaid.topup_apdusend("255", "90BB0000070100000000000000")
                                                        resreport = resreport + rapdu
                                                        if resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                            while resultStr == "9000" or resultStr == "9100" or resultStr == "0000" or resultStr == "91AF":
                                                                resultStr, rapdu = prepaid.topup_apdusend("255", "90AF000000")
                                                                resreport = resreport + rapdu
                
                n = 64
                result1 = [resreport[i:i+n] for i in range(0, len(resreport), n)]
                # history = []

                for item in result1:
                    item = item[-64:]
                    MID = item[:16]
                    TID = item[16:32]
                    TRXDATE = item[32:38]
                    TRXTIME = item[38:44]
                    TRXTYPE = item[44:46]
                    AMOUNT = item[46:52]
                    BEFORE = item[52:58]
                    AFTER = item[58:64]       
                    itemRow = str(MID) + "|" + str(TID) + "|" + str(TRXDATE) + "|" + str(TRXTIME) + "|" + str(TRXTYPE) + "|" + str(AMOUNT) + "|" + str(BEFORE) + "|" + str(AFTER)
                    resreport = resreport + itemRow + "\r\n"
                    # history.append({
                    #     'type': _Common.BRI_LOG_LEGEND.get(TRXTYPE, ''),
                    #     'trx_date': utils.serialize_str(str(TRXDATE), "/"),
                    #     'trx_time': utils.serialize_str(str(TRXTIME), ":"),
                    #     'amount': str(int("".join(reversed([AMOUNT[i:i+2] for i in range(0, 6, 2)])), 16)),
                    #     'prev_balance': str(int("".join(reversed([BEFORE[i:i+2] for i in range(0, 6, 2)])), 16)),
                    #     'last_balance': str(int("".join(reversed([AFTER[i:i+2] for i in range(0, 6, 2)])), 16)),
                    #     # 'raw': item
                    # })
                
                if resultStr.upper() == "911C":
                    resultStr = "0000"
                
                msg = resreport

    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg
