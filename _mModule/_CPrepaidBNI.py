__author__ = 'fitrah.wahyudi.imam@gmail.com'

from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidCommon as pr_common
from _mModule import _CPrepaidUtils as utils
from _mModule import _CPrepaidLog as LOG
from _cConfig import _Common
import requests
import json
import datetime
from time import sleep

BNI_SAM_CARD_NUMBER = ""
BNI_SAM_SALDO = ""
BNI_SAM_MAX_SALDO = ""

BNI_CARD_NUMBER = ""
BNI_CARD_SALDO = ""

UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL_DEV
if _Common.LIVE_MODE is True:
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL
    
if _Common.PTR_MODE is True:
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL


def test_update_balance_card(reff_no, TOKEN, TID, MID, card_no):
    
    __global_response__ = {
        "Command": "020",
        "Parameter": "",
        "Response": "",
        "ErrorDesc": "",
        "Result": ""
    }

    pr_common.get_purse_data("", __global_response__)

    if __global_response__["Result"] == "0000":
        purse_data = __global_response__["Response"]
        print("purse_data:"+purse_data)
        result_str, err_msg = send_update_balance(TOKEN, TID, MID, card_no, purse_data, reff_no)
        if result_str == "1":
            raise Exception(err_msg)
        dataJ = json.loads(result_str)
        if "response" in dataJ.keys():
            tempJ = dataJ["response"]
            if "code" in tempJ.keys():
                code = str(tempJ["code"])
                if code == "200":
                    if "data" in dataJ.keys():
                        tempJ = dataJ["data"]
                        if "dataToCard" in tempJ.keys():
                            crypto = tempJ["dataToCard"]
                            __global_response__ = {
                                "Command": "021",
                                "Parameter": purse_data + "|" + crypto,
                                "Response": "",
                                "ErrorDesc": "",
                                "Result": ""
                            }
                            bni_update_card_crypto(__global_response__["Parameter"], __global_response__)

        if result_str != "0000":
            raise Exception("Error: "+result_str)
        
    return __global_response__


def test_update_balance_sam(reff_no, TOKEN, TID, MID, card_no, sam_slot):
    
    __global_response__ = {
        "Command": "015",
        "Parameter": "",
        "Response": "",
        "ErrorDesc": "",
        "Result": ""
    }

    bni_get_purse_data_sam_multi(sam_slot, __global_response__)

    if __global_response__["Result"] == "0000":
        purse_data = __global_response__["Response"]
        print("purse_data:"+purse_data)
        result_str, err_msg = send_update_balance(TOKEN, TID, MID, card_no, purse_data, reff_no)
        if result_str == "1":
            raise Exception(err_msg)
        dataJ = json.loads(result_str)
        if "response" in dataJ.keys():
            tempJ = dataJ["response"]
            if "code" in tempJ.keys():
                code = str(tempJ["code"])
                if code == "200":
                    if "data" in dataJ.keys():
                        tempJ = dataJ["data"]
                        if "dataToCard" in tempJ.keys():
                            crypto = tempJ["dataToCard"]
                            __global_response__ = {
                                "Command": "016",
                                "Parameter": sam_slot + "|" + purse_data + "|" + crypto,
                                "Response": "",
                                "ErrorDesc": "",
                                "Result": ""
                            }
                            bni_update_sam_crypto(__global_response__["Parameter"], __global_response__)

        if result_str != "0000":
            raise Exception("Error: "+result_str)
    return __global_response__


def send_update_balance(TOKEN, TID, MID, card_no, purse_data, reff_no):
    TIMEOUT_REQUESTS = 50
    
    try:
        sURL = UPDATE_BALANCE_URL + "topup-bni/update"

        payload = { 
            "token":TOKEN, "tid": TID, "mid": MID, "card_no":card_no,"card_info": purse_data, 
            "reff_no":reff_no
            }

        LOG.fw(":UpdateBNI url = ", sURL)
        LOG.fw(":UpdateBNI json = ", payload)
        
        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)
        ValueText = r.text
        LOG.fw(":UpdateBNI = ", ValueText)

        return r.text, "0000"
    except Exception as ex:
        errorcode = "UpdateBNI error: {0}".format(ex)
        return "1", errorcode

#003-2
def bni_validation(param, __global_response__):
    res_str = prepaid.topupbni_validation(b"5")
        
    __global_response__["Response"] = __global_response__["Response"] + "|" + res_str

    return res_str

#011
def bni_terminal_update(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 1:
        C_Terminal = Param[0].encode('utf-8')
    else:
        LOG.fw("011:Parameter tidak lengkap", param)
        raise Exception("011:Parameter tidak lengkap: "+param)

    LOG.fw("011:Parameter = ", C_Terminal)

    res_str = prepaid.topup_bni_update(C_Terminal)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("011:Result = ", res_str)
        LOG.fw("011:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("011:Result = ", res_str, True)
        LOG.fw("011:Gagal", None, True)

    return res_str

#012
def bni_init_topup(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO

    Param = param.split('|')
    if len(Param) == 2:
        C_Slot = Param[0].encode('utf-8')
        C_Terminal = Param[1].encode('utf-8')
    else:
        LOG.fw("012:Parameter tidak lengkap", param)
        raise Exception("012:Parameter tidak lengkap: "+param)

    LOG.fw("012:Parameter = ", C_Slot)
    LOG.fw("012:Parameter = ", C_Terminal)

    resP, report = prepaid.topup_pursedata_multi_sam(C_Slot)
    if len(report) >= 20:
        BNI_SAM_CARD_NUMBER = report[4:20]

    resS, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO = prepaid.topupbni_km_balance_multi_sam(C_Slot)
    sleep(1)
    resB, BNI_CARD_SALDO, BNI_CARD_NUMBER, BT = prepaid.topup_balance_with_sn()
    sleep(1)
    res_str = prepaid.topupbni_init_multi(C_Slot, C_Terminal)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("012:Result = ", res_str)
        LOG.fw("012:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("012:Result = ", res_str, True)
        LOG.fw("012:Gagal", None, True)

    return res_str

#013
def bni_topup(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO

    Param = param.split('|')

    if len(Param) == 2:
        C_Denom = int(Param[0].encode('utf-8'),10)
        C_Slot = Param[1].encode('utf-8')
    else:
        LOG.fw("013:Parameter tidak lengkap", param)
        raise Exception("013:Parameter tidak lengkap: "+param)

    LOG.fw("013:Parameter = ", C_Denom)
    LOG.fw("013:Parameter = ", C_Slot)

    res_str, card_number, reportSAM = prepaid.topupbni_credit_multi_sam(C_Slot, C_Denom, b"5")
    sleep(2)
    resS, sam_last_saldo, BNI_SAM_MAX_SALDO = prepaid.topupbni_km_balance_multi_sam(C_Slot)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        # LOG.fw("013:reportSAM = ",reportSAM)

        amountBeforeStr = reportSAM[34:40]
        # LOG.fw("013:amountBeforeStr = ",amountBeforeStr)
        amountBefore = int(amountBeforeStr, 16)

        amountAfterStr = reportSAM[40:46]
        # LOG.fw("013:amountAfterStr = ",amountAfterStr)
        amountAfter = int(amountAfterStr, 16)

        amountTrxStr = reportSAM[46:52]
        # LOG.fw("013:amountTrxStr = ",amountTrxStr)
        amountTrx = int(amountTrxStr, 16)

        LOG.fw("013:Response = ", BNI_SAM_CARD_NUMBER)
        LOG.fw("013:Response = ", BNI_SAM_SALDO)
        LOG.fw("013:Response = ", sam_last_saldo)
        LOG.fw("013:Response = ", amountTrx)
        LOG.fw("013:Response = ", reportSAM)
        LOG.fw("013:Response = ", card_number)
        LOG.fw("013:Response = ", amountBefore)
        LOG.fw("013:Response = ", amountAfter)

        __global_response__["Response"] = res_str + "|" + BNI_SAM_CARD_NUMBER + "|" + BNI_SAM_SALDO + "|" + str(sam_last_saldo) + "|" + str(amountTrx) + "|" + reportSAM + "|" + card_number + "|" + str(amountBefore) + "|" + str(amountAfter)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("013:Result = ", res_str)
        LOG.fw("013:Sukses")
    else:
        __global_response__["Response"] = res_str + "|" + BNI_SAM_CARD_NUMBER + "|" + BNI_SAM_SALDO + "|" + str(sam_last_saldo) + "|" + str(C_Denom) + "|" + reportSAM + "|" + card_number + "|" + BNI_CARD_SALDO + "|"  + BNI_CARD_SALDO
        LOG.fw("013:Response = ", BNI_SAM_CARD_NUMBER, True)
        LOG.fw("013:Response = ", BNI_SAM_SALDO, True)
        LOG.fw("013:Response = ", sam_last_saldo, True)
        LOG.fw("013:Response = ", C_Denom, True)
        LOG.fw("013:Response = ", reportSAM, True)
        LOG.fw("013:Response = ", card_number, True)
        LOG.fw("013:Response = ", BNI_CARD_SALDO, True)
        LOG.fw("013:Response = ", BNI_CARD_SALDO, True)

        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("013:Result = ", res_str, True)
        LOG.fw("013:Gagal", None, True)

    return res_str

#014
def bni_sam_balance_multi(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO
    # LOG.tracing("BNI: ", "bni_sam_balance_multi")
    res_str = pr_common.open_only()
    if res_str != "0000":
        raise Exception("COM Open Fail: "+res_str)

    Param = param.split('|')

    if len(Param) == 1:
        C_Slot = Param[0]
    else:
        LOG.fw("014:Parameter tidak lengkap", param)
        raise Exception("014:Parameter tidak lengkap: "+param)

    LOG.fw("014:Parameter = ", C_Slot)

    res_str, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO = prepaid.topupbni_km_balance_multi_sam(C_Slot)
    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["Response"] = BNI_SAM_SALDO + "|" + BNI_SAM_MAX_SALDO
        LOG.fw("014:Response = ", BNI_SAM_SALDO)
        LOG.fw("014:Response = ", BNI_SAM_MAX_SALDO)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("014:Result = ", res_str)
        LOG.fw("014:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("014:Result = ", res_str, True)
        LOG.fw("014:Gagal", None, True)
    
    return res_str

#015
def bni_get_purse_data_sam_multi(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO
    # LOG.tracing("BNI: ", "bni_get_purse_data_sam_multi")

    Param = param.split('|')
    
    if len(Param) == 1:
        C_Slot = Param[0]
    else:
        LOG.fw("015:Parameter tidak lengkap", param)
        raise Exception("015:Parameter tidak lengkap: "+param)

    LOG.fw("015:Parameter = ", C_Slot)

    res_str, report = prepaid.topup_pursedata_multi_sam(C_Slot)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["Response"] = report
        LOG.fw("015:Response = ", report)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("015:Result = ", res_str)
        LOG.fw("015:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("015:Result = ", res_str, True)
        LOG.fw("015:Gagal", None, True)
    
    return res_str

#016
def bni_update_sam_crypto(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO

    Param = param.split('|')
    
    if len(Param) == 3:
        C_Slot = Param[0]
        C_PurseData = Param[1].encode('utf-8')
        C_Cryptogram = Param[2].encode('utf-8')
    else:
        LOG.fw("016:Parameter tidak lengkap", param)
        raise Exception("016:Parameter tidak lengkap: "+param)

    LOG.fw("016:Parameter = ", C_Slot)
    LOG.fw("016:Parameter = ", C_PurseData)
    LOG.fw("016:Parameter = ", C_Cryptogram)


    dtpurse = C_PurseData[36:52]
    dtcrypto = C_Cryptogram[-32:]
    fixset = b"90361401250314021403"
    fixlastset = b"000000000000000018"

    C_APDU = fixset + dtpurse + dtcrypto + fixlastset

    res_str, RAPDU = prepaid.topup_apdusend(C_Slot, C_APDU)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["Response"] = RAPDU
        LOG.fw("016:Response = ", RAPDU)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("016:Result = ", res_str)
        LOG.fw("016:Sukses")

    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("016:Result = ", res_str, True)
        LOG.fw("016:Gagal", None, True)

    return res_str

#017
def bni_get_card_no_sam_multi(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO
    Param = param.split('|')
    
    if len(Param) == 1:
        C_Slot = Param[0]
    else:
        LOG.fw("017:Parameter tidak lengkap", param)
        raise Exception("017:Parameter tidak lengkap: "+param)

    LOG.fw("017:Parameter = ", C_Slot)

    res_str, report = prepaid.topup_pursedata_multi_sam(C_Slot)
    C_CARD_NUMBER = ""
    if len(report) >= 20:
        C_CARD_NUMBER = report[4:20]
    
    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["Response"] = C_CARD_NUMBER
        LOG.fw("017:Response = ", C_CARD_NUMBER)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("017:Result = ", res_str)
        LOG.fw("017:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("017:Result = ", res_str, True)
        LOG.fw("017:Gagal", None, True)
    
    return res_str

#018
def bni_reset_count_sam_multi(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO

    Param = param.split('|')

    if len(Param) == 2:
        C_Slot = Param[0]
        C_TerminalID = Param[1]
    else:
        LOG.fw("018:Parameter tidak lengkap", param)
        raise Exception("018:Parameter tidak lengkap: "+param)

    LOG.fw("018:Parameter = ", C_Slot)
    LOG.fw("018:Parameter = ", C_TerminalID)

    res_str, report, deb_error = prepaid.topupbni_sam_refill_multi(C_Slot, C_TerminalID)
    
    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("018:Result = ", res_str)
        LOG.fw("018:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("018:Result = ", res_str, True)
        LOG.fw("018:Gagal", None, True)
    
    return res_str

#021
def bni_update_card_crypto(param, __global_response__):
    global BNI_SAM_CARD_NUMBER, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO, BNI_CARD_NUMBER, BNI_CARD_SALDO
    Param = param.split('|')

    if len(Param) == 2:
        C_PurseData = Param[0].encode('utf-8')
        C_Cryptogram = Param[1].encode('utf-8')
    else:
        LOG.fw("021:Parameter tidak lengkap", param)
        raise Exception("021:Parameter tidak lengkap: "+param)

    LOG.fw("021:Parameter = ", C_PurseData)
    LOG.fw("021:Parameter = ", C_Cryptogram)

    dtpurse = C_PurseData[36:52]
    dtcrypto = C_Cryptogram[-32:]
    fixset = b"90361401250314021403"
    fixlastset = b"000000000000000018"

    C_APDU = fixset + dtpurse + dtcrypto + fixlastset

    res_str, RAPDU = prepaid.topup_apdusend("255", C_APDU)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["Response"] = RAPDU
        LOG.fw("021:Response = ", RAPDU)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("021:Result = ", res_str)
        LOG.fw("021:Sukses")
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("021:Result = ", res_str, True)
        LOG.fw("021:Gagal", None, True)
    
    return res_str

#040
def bni_get_log(param, __global_response__):
    res_str, errmsg = bni_get_log_priv()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        LOG.fw("040:Response = ", errmsg)

        __global_response__["ErrorDesc"] = "Sukses"

        LOG.fw("040:Result = ", res_str)
        LOG.fw("040:Sukses", None)
    else:
        __global_response__["Response"] = errmsg
        LOG.fw("040:Response = ", errmsg, True)
     
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("040:Result = ",res_str, True)
        LOG.fw("040:Gagal", None, True)

    return res_str

def bni_get_log_priv():
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""
    msg = ""
    GetLogBNI = ""

    try:
        prepaid.topup_card_disconnect()
        resultStr, data, ErrMsg = prepaid.topup_pursedata()
        if resultStr == "0000":
            max_t = 4
            i = 0
            while resultStr == "0000" and i <= max_t:
                if i == 4:
                    resultStr, rapdu = prepaid.topup_apdusend("255","90320300010410")
                    if resultStr == "0000":
                        types = rapdu[:2]
                        amount = get_amount_for_log(rapdu[2:8])
                        dates = get_date(rapdu[8:16])

                        resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates

                        msg = msg + resreport

                        i = i + 1
                    else:
                        GetLogBNI= rapdu
                else:
                    apdu = "90320300010" + str(i) + "10"
                    resultStr, rapdu = prepaid.topup_apdusend("255",apdu)
                    if resultStr == "0000":
                        types = rapdu[:2]
                        amount = get_amount_for_log(rapdu[2:8])
                        dates = get_date(rapdu[8:16])

                        resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates

                        msg = msg + resreport + "#"

                        i = i + 1
                    else:
                        GetLogBNI= rapdu

        msg = msg + GetLogBNI
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg


def get_amount_for_log(data):
    if data[2:] == "FF":
        return 1
    else:        
        return int(data, 16)


def get_date(data):
    epoch = int(data, 16)
    date_1 = datetime.datetime(1995,1,1,0,0,0)
    date_2 = date_1 + datetime.timedelta(0,epoch)
    return date_2.strftime("%Y%m%d%H%M%S")
