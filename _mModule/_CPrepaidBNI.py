__author__ = 'wahyudi@multidaya.id'

from email.contentmanager import raw_data_manager
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
        result_str, err_msg = send_update_balance(TOKEN, TID, MID, card_no, purse_data, reff_no, "0")
        if result_str == "1":
            raise SystemError(err_msg)
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
            raise SystemError("Error: "+result_str)
        
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
        result_str, err_msg = send_update_balance(TOKEN, TID, MID, card_no, purse_data, reff_no, "0")
        if result_str == "1":
            raise SystemError(err_msg)
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
            raise SystemError("Error: "+result_str)
    return __global_response__


def send_update_balance(TOKEN, TID, MID, card_no, purse_data, reff_no, last_balance):
    TIMEOUT_REQUESTS = 50
    
    try:
        sURL = UPDATE_BALANCE_URL + "topup-bni/update"

        payload = { 
            "token":TOKEN, 
            "tid": TID, 
            "mid": MID, 
            "card_no":card_no,
            "card_info": purse_data, 
            "reff_no":reff_no,
            "prev_balance": last_balance
            }

        LOG.fw(":UpdateBNI url = ", sURL)
        LOG.fw(":UpdateBNI json = ", payload)
        
        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)
        ValueText = r.text
        LOG.fw(":UpdateBNI = ", ValueText)

        return ValueText, "0000"
    except Exception as ex:
        errorcode = "UpdateBNI error: {0}".format(ex)
        return "1", errorcode

#003-2
def bni_validation(param, __global_response__):
        
    res_str = __global_response__["Result"]

    # Do validate BNI if only Tapcash
    if __global_response__["Result"] == '0000':
        card_balance_data =  __global_response__["Response"]
        if card_balance_data.split('|')[1][:4] == '7546':
            res_str = prepaid.topupbni_validation(b"5")
    
    __global_response__["Response"] = __global_response__["Response"] + "|" + res_str

    return res_str

#011
def bni_terminal_update(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 1:
        C_Terminal = Param[0].encode('utf-8')
    else:
        LOG.fw("011:Missing Parameter", param)
        raise SystemError("011:Missing Parameter: "+param)

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
        LOG.fw("012:Missing Parameter", param)
        raise SystemError("012:Missing Parameter: "+param)

    LOG.fw("012:Parameter = ", C_Slot)
    LOG.fw("012:Parameter = ", C_Terminal)
    
    # Purse Tapcash Data First
    # res_card_purse, report_card_purse, purse_error = prepaid.topup_pursedata()
    # if res_card_purse != '0000':
    #     __global_response__["ErrorDesc"] = "Gagal"
    #     LOG.fw("012:Result Purse Kartu= ", res_card_purse, True)
    #     LOG.fw("012:Gagal Purse Kartu", purse_error, True)
    #     return res_str
    
    # sleep(1)
    # BNI_CARD_NUMBER = report_card_purse[4:20] if res_card_purse == '0000' else ''

    # res_purse_sam, report_sam_purse = prepaid.topup_pursedata_multi_sam(C_Slot)
    # Change To RAW Purse SAM
    res_purse_sam, report_sam_purse = raw_purse_sam_priv(C_Slot)
    if len(report_sam_purse) >= 20:
        BNI_SAM_CARD_NUMBER = report_sam_purse[4:20]

    res_balance_sam, BNI_SAM_SALDO, BNI_SAM_MAX_SALDO = prepaid.topupbni_km_balance_multi_sam(C_Slot)
    sleep(1)
    # BNI_SAM_SALDO = str(_Common.BNI_ACTIVE_WALLET)
    # resB, BNI_CARD_SALDO, BNI_CARD_NUMBER, BT = prepaid.topup_balance_with_sn()
    # sleep(1)
    # Parse Card Amount From Purse
    # BNI_CARD_SALDO = ""

    res_str = prepaid.topupbni_init_multi(C_Slot, C_Terminal)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        __global_response__["Response"] = report_sam_purse
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
        LOG.fw("013:Missing Parameter", param)
        raise SystemError("013:Missing Parameter: "+param)

    LOG.fw("013:Parameter = ", C_Denom)
    LOG.fw("013:Parameter = ", C_Slot)

    res_str, card_number, reportSAM = prepaid.topupbni_credit_multi_sam(C_Slot, C_Denom, b"5")
    # str(int(__report_sam[58:64], 16))
    sam_last_saldo = str(_Common.BNI_ACTIVE_WALLET)
    # sleep(2)
    # resS, sam_last_saldo, BNI_SAM_MAX_SALDO = prepaid.topupbni_km_balance_multi_sam(C_Slot)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        # LOG.fw("013:reportSAM = ",reportSAM)

        amountBeforeStr = reportSAM[34:40]
        # LOG.fw("013:amountBeforeStr = ",amountBeforeStr)
        amountBefore = int(amountBeforeStr, 16)
        
        # Override Sam Last Saldo From Report
        sam_last_saldo = str(int(reportSAM[58:64], 16))

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
        raise SystemError("COM Open Fail: "+res_str)

    Param = param.split('|')

    if len(Param) == 1:
        C_Slot = Param[0]
    else:
        LOG.fw("014:Missing Parameter", param)
        raise SystemError("014:Missing Parameter: "+param)

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
    PurseMode = 'NORMAL'
    
    if len(Param) == 1:
        C_Slot = Param[0]
    elif len(Param) > 1:
        C_Slot = Param[0]
        PurseMode = Param[1]
        LOG.fw("015:SAM Purse Mode", PurseMode)
    else:
        LOG.fw("015:Missing Parameter", param)
        raise SystemError("015:Missing Parameter: "+param)

    LOG.fw("015:Parameter = ", C_Slot)

    if PurseMode == 'NORMAL':
        res_str, report = prepaid.topup_pursedata_multi_sam(C_Slot)
    else:
        res_str, report = raw_purse_sam_priv(C_Slot)

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
        LOG.fw("016:Missing Parameter", param)
        raise SystemError("016:Missing Parameter: "+param)

    LOG.fw("016:Parameter = ", C_Slot)
    LOG.fw("016:Parameter = ", C_PurseData)
    LOG.fw("016:Parameter = ", C_Cryptogram)

    dtpurse = C_PurseData[36:52]
    dtcrypto = C_Cryptogram[-32:]
    fixset = b"90361401250314021403"
    fixlastset = b"000000000000000018"

    C_APDU = fixset + dtpurse + dtcrypto + fixlastset

    res_str, RAPDU = prepaid.send_apdu_cmd(C_Slot, C_APDU)

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
        LOG.fw("017:Missing Parameter", param)
        raise SystemError("017:Missing Parameter: "+param)

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
        LOG.fw("018:Missing Parameter", param)
        raise SystemError("018:Missing Parameter: "+param)

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
        LOG.fw("021:Missing Parameter", param)
        raise SystemError("021:Missing Parameter: "+param)

    LOG.fw("021:Parameter = ", C_PurseData)
    LOG.fw("021:Parameter = ", C_Cryptogram)

    dtpurse = C_PurseData[36:52]
    dtcrypto = C_Cryptogram[-32:]
    fixset = b"90361401250314021403"
    fixlastset = b"000000000000000018"

    C_APDU = fixset + dtpurse + dtcrypto + fixlastset

    res_str, RAPDU = prepaid.send_apdu_cmd("255", C_APDU)

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
def bni_card_get_log(param, __global_response__):
    
    res_str, errmsg, desc = bni_card_get_log_priv()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        if type(desc) == list and len(desc) > 0:
            __global_response__["Description"] = ",".join(desc)
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

#077
def bni_card_get_log_custom(param, __global_response__):
    
    Param = param.split('|')
    row = 29
    if len(Param) > 0:
        row = Param[0].encode('utf-8') 
        row = int(row) - 1
    
    res_str, purseData, listRAPDU = bni_card_get_log_custom_priv(row)
    # resultStr, purseData, listRAPDU

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = purseData
        if type(listRAPDU) == list and len(listRAPDU) > 0:
            __global_response__["Response"] = purseData + "#" + (",".join(listRAPDU))
        LOG.fw("077:Response = ", purseData)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("077:Result = ", res_str)
        LOG.fw("077:Sukses", None)
    else:
        __global_response__["Response"] = purseData
        LOG.fw("077:Response = ", purseData, True)
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("077:Result = ",res_str, True)
        LOG.fw("077:Gagal", None, True)
    return res_str

#042
def bni_sam_get_log(param, __global_response__):
    
    Param = param.split('|')
    if len(Param) > 0:
        C_Slot = Param[0]
    else:
        LOG.fw("042:Missing Parameter", param)
        raise SystemError("042:Missing Parameter: "+param)
    
    res_str, errmsg, desc = bni_sam_get_log_priv(C_Slot)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        if type(desc) == list and len(desc) > 0:
            __global_response__["Response"] = ",".join(desc)
        LOG.fw("042:Response = ", errmsg)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("042:Result = ", res_str)
        LOG.fw("042:Sukses", None)
    else:
        __global_response__["Response"] = errmsg
        LOG.fw("042:Response = ", errmsg, True)
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("042:Result = ",res_str, True)
        LOG.fw("042:Gagal", None, True)

    return res_str

#080
def bni_topup_init_key(param, __global_response__):
    
    Param = param.split('|')
    if len(Param) > 0:
        C_MasterKey = Param[0]
        C_PIN = Param[1]
        C_TID = Param[2]
        LOG.fw("080:Parameter = ", C_MasterKey)
        LOG.fw("080:Parameter = ", C_PIN)
        LOG.fw("080:Parameter = ", C_TID)
    else:
        LOG.fw("080:Missing Parameter", param)
        raise SystemError("080:Missing Parameter: "+param)
    
    res_str, errmsg = bni_topup_init_key_priv(C_MasterKey, C_PIN, C_TID)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        LOG.fw("080:Response = ", errmsg)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("080:Result = ", res_str)
        LOG.fw("080:Sukses", None)
    else:
        __global_response__["Response"] = errmsg
        LOG.fw("080:Response = ", errmsg, True)
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("080:Result = ",res_str, True)
        LOG.fw("080:Gagal", None, True)

    return res_str
    
    
def bni_topup_init_key_priv(master_key, pin, tid):
    err_msg = 'FAILED'
    res_str = prepaid.topup_bni_init_key(master_key, pin, tid)
    if (res_str == '0000'):
        err_msg = 'OK'
    return res_str, err_msg


def bni_card_get_log_custom_priv(max_t=29):
    resultStr = ""
    resreport = ""
    msg = ""
    GetLogBNI = ""
    listRAPDU = []
    # Max History
    # max_t = 29

    try:
        prepaid.topup_card_disconnect()
        # resultStr, reportPurse, ErrMsg = prepaid.topup_pursedata()
        resultStr, cardUID, reportPurse, cardAttr = prepaid.topup_get_carddata()
        if len(reportPurse) >= len('0001754627000777669800000000A816814CA0C7CEA554CDB3918FAFA1F3C134FCB4000000000100D96988889999040027103629F5507020021701FFFFFF3632E99850555243000000000000255468A71F43D528061E4EC5F712B029'):
            resultStr, card_log = prepaid.get_card_history('BNI')
            if resultStr == '0000':
                i = 0
                for rapdu in card_log:
                    if i > max_t:
                        break
                    if rapdu in listRAPDU:
                        continue
                    listRAPDU.append(rapdu)
                    i = i + 1                        
                    types = rapdu[:2]
                    amount = get_amount_for_log(rapdu[2:8])
                    dates = get_date(rapdu[8:16])
                    resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates
                    msg = msg + resreport + "#"

        msg = msg + GetLogBNI
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, reportPurse, listRAPDU


def bni_card_get_log_priv(max_t=29):
    resultStr = ""
    resreport = ""
    msg = ""
    GetLogBNI = ""
    listRAPDU = []
    # Max History
    # max_t = 29

    try:
        prepaid.topup_card_disconnect()
        resultStr, card_log = prepaid.get_card_history('BNI')
        if resultStr == '0000':
            i = 0
            for rapdu in card_log:
                if i > max_t:
                    break
                if rapdu in listRAPDU:
                    continue
                listRAPDU.append(rapdu)
                i = i + 1                        
                types = rapdu[:2]
                amount = get_amount_for_log(rapdu[2:8])
                dates = get_date(rapdu[8:16])
                resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates
                msg = msg + resreport + "#"

        msg = msg + GetLogBNI
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg, listRAPDU


def bni_sam_get_log_priv(slot, max_t=29):
    resultStr = ""
    ErrorCode = ""
    resreport = ""
    ErrMsg = ""
    msg = ""
    GetLogBNI = ""
    listRAPDU = []
    # Max History
    # max_t = 29

    try:
        prepaid.topup_card_disconnect()
        resultStr, data, ErrMsg = prepaid.topup_pursedata_multi_sam(slot)
        if resultStr == "0000":
            i = 0
            while resultStr == "0000" and i <= max_t:
                if i > max_t:
                    break
                else:
                    idx = hex_padding(i)
                    apdu = "9032030001" + str(idx) + "10"
                    resultStr, rapdu = prepaid.send_apdu_cmd(slot, apdu)
                    # E/listApdu: 01FFF25433A26E4600000880234181029000
                    # E/listApdu: 01FFFFFF33620F180000162C788002449000
                    # E/listApdu: 01FFFFFF33620D6F0000162D788002449000
                    # E/listApdu: 01FFFFFF3361F00E0000162E410870039000
                    # E/listApdu: 01FFFFFF3361E9890000162F414001039000
                    # E/listApdu: 01FFFFFF3361D33E00001630414003179000
                    # E/listApdu: 01FFFFFF33379A2800001631333102019000
                    # E/listApdu: 01FFFFFF3183A25300001632012345679000
                    # E/listApdu: 01FF73603160303700001633140909019000
                    # E/listApdu: 040001F4315D35F00000A2D3888899999000
                    # E/listApdu: 040021343149BD600000A0DF888899999000
                    # E/listApdu: 01FF75543149BFF300007FAB140909019000
                    # E/listApdu: 040021343149B73500010A57888899999000
                    # E/listApdu: 040021343149A3E70000E923888899999000
                    # E/listApdu: 0400213431499D2A0000C7EF888899999000
                    if resultStr == "0000":
                        i = i + 1
                        if rapdu in listRAPDU:
                            continue
                        listRAPDU.append(rapdu)
                        types = rapdu[:2]
                        amount = get_amount_for_log(rapdu[2:8])
                        dates = get_date(rapdu[8:16])
                        resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates
                        msg = msg + resreport + "#"
                    else:
                        GetLogBNI= rapdu

        msg = msg + GetLogBNI
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg, listRAPDU


def get_amount_for_log(data):
    if data[:2] == "FF":
        return twos_complement(data, 24)
    else:        
        return int(data, 16)


def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value
    

def get_date(data):
    epoch = int(data, 16)
    date_1 = datetime.datetime(1995,1,1,0,0,0)
    date_2 = date_1 + datetime.timedelta(0,epoch)
    return date_2.strftime("%Y%m%d%H%M%S")


def hex_padding(i, pad=2):
    return format(int(i), 'x').zfill(pad).upper()


def raw_purse_sam_priv(slot):
    # apdu BNI buat secure raw purse
    # 1. 0x00, 0xA4, 0x04, 0x00, 0x08, 0xA0, 0x00, 0x42, 0x4E, 0x49, 0x10, 0x00, 0x01
    # 2. 0x00, 0x84, 0x00, 0x00, 0x08
    # 3. 0x90, 0x32, 0x03, 0x00, 0x0A, 0x12, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    resultStr, responseStr = prepaid.send_apdu_cmd(slot, '00A4040008A000424E49100001')
    if resultStr == '0000':
        resultStr, responseStr = prepaid.send_apdu_cmd(slot, '0084000008')
        if resultStr == '0000':
            resultStr, responseStr = prepaid.send_apdu_cmd(slot, '903203000A1201000000000000000000')
    return resultStr, responseStr