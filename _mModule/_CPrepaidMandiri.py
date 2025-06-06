__author__ = 'wahyudi@multidaya.id'

from _mModule import _CPrepaidLog as LOG
from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidUtils as prepaid_utils
from _cConfig import _Common
import requests
import time
import json
import datetime

UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL_DEV
if _Common.LIVE_MODE is True:
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL
    
if _Common.PTR_MODE is True:
    UPDATE_BALANCE_URL = _Common.UPDATE_BALANCE_URL

TIMEOUT_REQUESTS = 50

#019
def update_balance_mandiri(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 3:
        C_TID = Param[0].encode('utf-8')
        C_MID = Param[1].encode('utf-8')
        C_Token = Param[2].encode('utf-8')
    else:
        LOG.fw("019:Missing Parameter", param)
        raise SystemError("019:Missing Parameter: "+param)

    LOG.fw("019:Parameter = ", C_TID)
    LOG.fw("019:Parameter = ", C_MID)
    LOG.fw("019:Parameter = ", C_Token)

    res_str, cardno, amount, lastbalance, errmsg = update_balance_mandiri_priv(C_TID, C_MID, C_Token)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = str(cardno) + "|" + str(amount) + "|" + str(lastbalance)
        LOG.fw("019:Response = ", cardno)
        LOG.fw("019:Response = ", amount)
        LOG.fw("019:Response = ", lastbalance)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("019:Result = ", res_str)
        LOG.fw("019:Sukses")
    else:
        if errmsg == "0000":
            __global_response__["Response"] = res_str
            LOG.fw("019:Response = ", res_str, True)
        else:
            __global_response__["Response"] = errmsg        
            LOG.fw("019:Response = ", errmsg, True)

        __global_response__["Result"] = "1"
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("019:Result = ", 1, True)
        LOG.fw("019:Gagal", None, True)

    return res_str


def update_balance_mandiri_priv(C_TID, C_MID, C_TOKEN):
    global UPDATE_BALANCE_URL

    approvalcode = int(time.time())
    url = UPDATE_BALANCE_URL
    cardno = ""
    amount = "0"
    lastbalance = ""
    ErrMsg = ""
    dataToCard = ""

    res_str, card_prev_balance = prepaid.topup_balance()
    card_prev_balance = int(card_prev_balance)
    
    LOG.fw("019:GetCardBalance, response:", res_str)

    if res_str == "0000":
        LOG.fw("019:GetCardBalance:", card_prev_balance)
        res_str, cardno, uid, data, attr = get_card_data()

        LOG.fw("019:GetCardData, response:", res_str)

        if attr == "":
            attr = "6A86"
        
        if res_str == "0000":
            LOG.fw("019:cardno:", cardno)
            LOG.fw("019:uid:", uid)
            LOG.fw("019:data:", data)
            LOG.fw("019:attr:", attr)

            ######################
            ####NEW APPLET SECTION
            ######################
            if attr == "6A86":
                LOG.fw("019:New Applet Found:")
                valuetext, ErrMsg = send_update_balance(url, C_TOKEN, C_TID, C_MID, cardno, approvalcode, attr, data, uid, card_prev_balance)

                if valuetext == "1": valuetext = ErrMsg

                code = ""
                dataToCard = ""
                session = ""
                pendingtopup = ""

                dataJ = json.loads(valuetext)

                if "response" in dataJ.keys():
                    temp_json = dataJ["response"]
                    if "code" in temp_json.keys():
                        code = str(temp_json["code"])
                    
                if "data" in dataJ.keys():
                    temp_json = dataJ["data"]
                    if code == "200" or code == 200:
                        # API Will Not Send dataToCard For New Applet
                        # dataToCard = temp_json["dataToCard"]
                        amount = temp_json["amount"]
                        lastbalance = int(card_prev_balance)
                        session = temp_json["session"]
                        pendingtopup = temp_json["pendingTopup"]
                    else:
                        if "code" in temp_json.keys():
                            code = temp_json["code"]
                            resp_json_temp = temp_json
                
                code = str(code)
                res_str = code

                if code == "200":
                    codeConfirm = ""
                    updateStatusConfirm = "PENDING"
                    dataToCardConfirm = ""
                    LOG.fw("019:session:", session)
                    strdate = datetime.datetime.now().strftime("%d%m%y%H%M%S")
                    LOG.fw("019:strdate:", strdate)
                    pendingtopup = format(int(pendingtopup),'x')
                    pendingtopup = pendingtopup.zfill(8).upper()
                    LOG.fw("019:pendingtopup:", pendingtopup)
                    combinedata = strdate + "0000000000000000000000000000" + session + '0123456789ABCDEF00112233445566778899' + pendingtopup + "0000000000000000000011111111111111111111"
                    # CMD 00E50000
                    # LEN 46 
                    # DATE (6) 020922150625 
                    # PADDING_LEFT (14) 0000000000000000000000000000 
                    # SESSION FROM API (8) 4A515F8316A11ECF 
                    # INSTITUTION_REFF (8) 0123456789ABCDEF 
                    # SOURCE OF ACCOUNT (10) 00112233445566778899 
                    # AMOUNT HEX (4) 0000000A 
                    # MERCHANT DATA (20) 0000000000000000000011111111111111111111
                    lendata = len(combinedata) / 2
                    lendata = format(int(lendata), 'x').upper()
                    dataToCard = "00E50000" + lendata + combinedata
                    LOG.fw("019:inputData:", dataToCard)
                    res_str, dataUpdate = prepaid.send_apdu_cmd(b"255", dataToCard)
                    LOG.fw("019:dataUpdate:", dataUpdate)
                    LOG.fw("019:dataUpdate(len):", len(dataUpdate)/2)
                    ErrorCode = res_str
                    
                    if res_str == "0000":
                        # Get Certificate
                        res_str, dataCertificate = prepaid.send_apdu_cmd(b"255", "00E0000000")
                        LOG.fw("019:dataCertificate:", dataCertificate)
                        LOG.fw("019:dataCertificate(len):", len(dataCertificate)/2)

                        if res_str == "0000":
                            dataToCardConfirm = dataUpdate + dataCertificate
                            LOG.fw("019:dataToCardConfirm:", dataToCardConfirm)
                            if updateStatusConfirm == "PENDING":
                                # Send dataToCardConfirm to Host
                                valuetext, errmsg = send_confirm_update(url,C_TOKEN, C_TID, C_MID, cardno, dataToCardConfirm, "", approvalcode)
                                data_to_confirm = json.loads(valuetext)
                                codeConfirm = None
                                if "response" in data_to_confirm.keys():
                                    temp_json = data_to_confirm["response"]
                                    if "code" in temp_json.keys():
                                        codeConfirm = temp_json["code"]
                                if "data" in data_to_confirm.keys():
                                    temp_json = data_to_confirm["data"]
                                    if "dataToCard" in temp_json.keys():
                                        # Reply From Server To Be Injected Into Card
                                        dataToCardConfirm = temp_json["dataToCard"]
                                    if "updateStatus" in temp_json.keys():
                                        updateStatusConfirm = temp_json["updateStatus"]
                                
                                codeConfirm = str(codeConfirm)
                                if codeConfirm == "200" and updateStatusConfirm == "SUCCESS":
                                    # No Need To Send Len On APDU Command
                                    res_str, cardUpdate = prepaid.send_apdu_cmd(b"255", dataToCardConfirm)
                                    LOG.fw("019:cardUpdate:", cardUpdate)
                                    LOG.fw("019:cardUpdate(len):", len(cardUpdate)/2)
                                    if res_str == '0000':
                                        valuetext, ErrMsg = send_confirm_update(url,C_TOKEN, C_TID, C_MID, cardno, dataToCardConfirm, "COMPLETED", approvalcode)
                                        data_to_confirm2 = json.loads(valuetext)
                                        codeConfirm = ""
                                        if "response" in data_to_confirm2.keys():
                                            temp_json = data_to_confirm2["response"]
                                            if "code" in temp_json.keys():
                                                codeConfirm = temp_json["code"]
                                        
                                        if codeConfirm == '200': ErrMsg = ''
                                        
                                        lastbalance = int(card_prev_balance) + int(amount)
                    # ################################
                    # Returning Success Here
                    # ################################
                                        lastbalance = str(lastbalance)
                                        return res_str, cardno, amount, lastbalance, ErrMsg
                    # ################################
                    # Do Reversal Of Any Failure Above
                    # ################################

                    # Get Reversal Data >> 00E70000 → expected response = dataReversal (149 byte) + 9000
                    # Get Certificate >> 00E00000 → expected response = dataCertificate (248 byte) + 9000
                    res_str, reversalData = prepaid.send_apdu_cmd(b"255", "00E70000")
                    LOG.fw("019:reversalData:", reversalData)
                    LOG.fw("019:reversalData(len):", len(reversalData)/2)
                    if res_str == "0000":
                        # Get Certificate
                        res_str, dataCertificate = prepaid.send_apdu_cmd(b"255", "00E0000000")
                        LOG.fw("019:dataCertificate:", dataCertificate)
                        LOG.fw("019:dataCertificate(len):", len(dataCertificate)/2)
                        if res_str == "0000":
                            reversalData = reversalData + dataCertificate
                            valuetext, ErrMsg = send_reversal_topup(url, C_TOKEN, C_TID, C_MID, cardno, card_prev_balance, approvalcode, amount, data, uid, "", reversalData, attr)
                            jsonReversal = json.loads(valuetext)
                            if "response" in jsonReversal.keys():
                                temp_json = jsonReversal["response"]
                                if "code" in temp_json.keys():
                                    codereversal = temp_json["code"]
                            if "data" in jsonReversal.keys():
                                temp_json = jsonReversal["data"]
                                if "reversalMessage" in temp_json.keys():
                                    StatusReversal = temp_json["reversalMessage"]

                            codereversal = str(codereversal)
                            if codereversal == "200" and StatusReversal == "REVERSAL_DONE":
                                res_str = codereversal
                                ErrMsg = "REVERSAL_DONE"
                            else:
                                res_str = "FAIL"
                                ErrMsg = "REVERSAL_FAILED"
                        else:
                            res_str = "FFEE"
                            ErrMsg = "REVERSAL_FAILED"
                    else:
                        res_str = "FFEE"
                        ErrMsg = "REVERSAL_FAILED"
                    
                elif code == "51003":
                    ErrorCode = code
                    ErrMsg = "NO PENDING BALANCE"
                else:
                    ErrorCode = code
            
            
            ######################
            ####OLD APPLET SECTION
            ######################
            else:
                LOG.fw("019:OLD Applet Found")
                valuetext, ErrMsg = send_update_balance(url, C_TOKEN, C_TID, C_MID, cardno, approvalcode, attr, data, uid, card_prev_balance)

                if valuetext == "1": valuetext = ErrMsg

                resp_json = json.loads(valuetext)
            
                resp_json_response = resp_json["response"]
                resp_json_data = resp_json["data"]

                code = resp_json_response["code"]
                if code == "200" or code == 200:
                    amount = resp_json_data["amount"]
                    dataToCard = resp_json_data["dataToCard"]
                    lastbalance = int(card_prev_balance) + int(amount)
                    
                elif "code" in resp_json_data.keys():
                    code = resp_json_data["code"]
                    resp_json_temp = resp_json_data
                # elif "data" in resp_json_data.keys():
                #     code, resp_json_temp = get_sub_code(resp_json_data)

                code = str(code)
                res_str = code

                if code == "200" or code == 200:
                    res = True
                    codeConfirm = ""
                    updateStatusConfirm = "PENDING"
                    dataToCardConfirm = ""

                    res_str, resreport = prepaid.send_apdu_cmd(b"255", dataToCard)
                    ErrorCode = res_str

                    LOG.fw("019:SendDataToCard update = ", ErrorCode)
                    if res_str == "0000":
                        dataToCardConfirm = resreport
                        while res and updateStatusConfirm == "PENDING":
                            dataToCardConfirm = dataToCardConfirm + "9000"
                            valuetext, ErrMsg = send_confirm_update(url, C_TOKEN, C_TID, C_MID, cardno, dataToCardConfirm, "COMPLETED", approvalcode)
                            data_to_confirm = json.loads(valuetext)
                            codeConfirm = None

                            if "response" in data_to_confirm.keys():
                                temp_json = data_to_confirm["response"]
                                if "code" in temp_json.keys():
                                    codeConfirm = temp_json["code"]
                            if "data" in data_to_confirm.keys():
                                temp_json = data_to_confirm["data"]
                                if "dataToCard" in temp_json.keys():
                                    dataToCardConfirm = temp_json["dataToCard"]
                                if "updateStatus" in temp_json.keys():
                                    updateStatusConfirm = temp_json["updateStatus"]
                            
                            codeConfirm = str(codeConfirm)

                            if codeConfirm == "200":
                                if updateStatusConfirm == "SUCCESS":
                                    ErrorCode = "0000"
                                    res = True
                                    break
                                else:
                                    res_str, resreport = prepaid.send_apdu_cmd("255", dataToCardConfirm)
                                    # res_str = prepaid_utils.to_4digit(res_w)
                                    LOG.fw("019:SendDataToCard confirm = ", ErrorCode)

                                    if res_str == "0000":
                                        dataToCardConfirm = resreport
                                        res = True
                                    else:
                                        res = False
                                        break 
                            else:
                                res_str = codeConfirm
                                res = False
                                break
                
                elif code == "51003":
                    ErrorCode = code
                    ErrMsg = "NO PENDING BALANCE"
                elif code == "51099":
                    amount = resp_json_temp["amount_reversal"]
                    approvalcode = resp_json_temp["approval_code"]
                    prepaid.topup_card_disconnect()
                    LOG.fw("019:Reversal OLD Start")
                    res_str, cardno, uid, data, attr = get_card_data()
                    ErrorCode = res_str
                    LOG.fw("019:GetCardData = ", ErrorCode)
                    if res_str == "0000":
                        ResReversal = True
                        codereversal = ""
                        StatusReversal = ""

                        while ResReversal:
                            if StatusReversal == "":
                                valuetext, ErrMsg = send_reversal_topup(url, C_TOKEN, C_TID, C_MID, cardno, card_prev_balance, approvalcode, amount, data, uid, "", dataToCard, attr)
                            else:
                                valuetext, ErrMsg = send_reversal_topup(url, C_TOKEN, C_TID, C_MID, cardno, card_prev_balance, approvalcode, amount, data, uid, "REVERSAL_LOOP", dataToCard, attr)

                            jsonReversal = json.loads(valuetext)

                            if "response" in jsonReversal.keys():
                                temp_json = jsonReversal["response"]
                                if "code" in temp_json.keys():
                                    codereversal = temp_json["code"]
                            if "data" in jsonReversal.keys():
                                temp_json = jsonReversal["data"]
                                if "reversalMessage" in temp_json.keys():
                                    StatusReversal = temp_json["reversalMessage"]
                            
                            codereversal = str(codereversal)

                            if codereversal == "200":
                                if StatusReversal == "REVERSAL_DONE" or StatusReversal == "":
                                    res_str = codereversal
                                    ResReversal = False
                                    ErrMsg = "REVERSAL_DONE"
                                else:
                                    res_str, resreport = prepaid.send_apdu_cmd(b"255", StatusReversal)

                                    if res_str == "0000":
                                        resreport= resreport+"9000"                                    
                                        dataToCard = resreport
                                        ResReversal = True
                                    else:
                                        ResReversal = False
                                        ErrMsg = "REVERSAL_FAILED"
                            else:
                                res_str = codereversal
                                ResReversal = False
                                ErrMsg = "REVERSAL_FAILED"
                else:
                    ErrorCode = code
    
    lastbalance = str(lastbalance)
    return res_str, cardno, amount, lastbalance, ErrMsg


def send_update_balance(url, TOKEN, TID, MID, card_no, approval_code, card_attribute, card_info, card_uid, last_balance):
    global TIMEOUT_REQUESTS
    try:
        sURL = url + "topup-mandiri/update"

        headers = {'Special-Case': 'TAPONBUSREADER'}
        payload = { 
            "token":TOKEN.decode("utf-8"), 
            "tid": TID.decode("utf-8"), 
            "mid": MID.decode("utf-8"), 
            "card_no":str(card_no),
            "approval_code": str(approval_code), 
            "card_attribute":str(card_attribute), 
            "card_info":str(card_info),
            "card_uid":str(card_uid), 
            "prev_balance":str(last_balance),
            "last_balance":str(last_balance)
        }

        LOG.fw(":UpdateMandiri url = ", sURL)
        LOG.fw(":UpdateMandiri json = ", payload)
        
        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload, headers=headers)
        ValueText = r.text
        LOG.fw(":UpdateMandiri = ", ValueText)
        
        if r.status_code != 200:
            return '1', ValueText
        else:
            return ValueText, "0000"
    except Exception as ex:
        errorcode = "UpdateMandiri error: {0}".format(ex)
        return "1", errorcode


def get_card_data():

    res_str, uid, data, attr = prepaid.topup_get_carddata()

    cardno = data[0:16]
    data = data + "9000"
    attr = attr[0:22]

    return res_str, cardno, uid, data, attr


def mandiri_get_log(param, __global_response__):
    Param = param.split('|')
    raw = True if len(Param) > 1 else False

    res_str, errmsg = mandiri_get_log_priv(raw)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        LOG.fw("039:Response = ", errmsg)

        __global_response__["ErrorDesc"] = "Sukses"

        LOG.fw("039:Result = ", res_str)
        LOG.fw("039:Sukses", None)
    else:
        __global_response__["Response"] = errmsg
        LOG.fw("039:Response = ", errmsg, True)
    
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("039:Result = ",res_str, True)
        LOG.fw("039:Gagal", None, True)

    return res_str


def sort_data_by_datetime(h=[]):
    if len(h) == 0: return h
    sorted_key = []
    for row in h:
        datetime = '1' + row[:21]
        sorted_key.append(datetime)
    sorted_key.sort(reverse=True)
    sorted_result = []
    for key in sorted_key:
        for row in h:
            if row in sorted_result:
                continue
            if str(key)[1:] in row:
                sorted_result.append(row)
    return sorted_result


def mandiri_get_log_priv(raw = False):
    resultStr = ""
    resreport = ""
    msg = ""
    GetLogMandiri = ""
    RawReport = []

    try:
        prepaid.topup_card_disconnect()
        resultStr, history = prepaid.get_card_history('MANDIRI')
        # 25102309042870201700D9100000012001000000AFD80000
        # 2510230645167520140000000000012001000000B8D80000
        # 25102308331870201600410E0000012001000000B3D80000
        # 1610231546377470300016000000012001000000B43B0000
        # 1810231146315109778800000000011048260000E2650000
        if resultStr == "0000" or len(history) > 0:
            history = sort_data_by_datetime(history)
            i = 0
            for rapdu in history:
                if rapdu == ('0'*240) or ('0'*100) in rapdu or rapdu in RawReport: 
                    continue
                dates = rapdu[:12]
                tid = rapdu[12:20]
                count = prepaid_utils.getint(rapdu[20:28])
                types = prepaid_utils.getint2(rapdu[27:31])
                amount = prepaid_utils.getint(rapdu[32:40])
                balance = prepaid_utils.getint(rapdu[40:48])
                resreport = str(i) + "|" + dates + "|" + tid + "|" + str(count) + "|" + str(types) + "|" + str(amount) + "|" + str(balance)
                msg = msg + resreport + "#"
                RawReport.append(rapdu)
                i = i + 1
        
        msg = msg + GetLogMandiri
        if len(RawReport) > 0:
            resultStr = '0000'
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    if raw:
        return resultStr, "#".join(RawReport)
    else:
        return resultStr, msg


def mandiri_update_sam_balance(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 4:
        C_Slot = Param[0].encode('utf-8')
        C_TID = Param[1].encode('utf-8')
        C_MID = Param[2].encode('utf-8')
        C_Token = Param[3].encode('utf-8')
    else:
        LOG.fw("035:Missing Parameter", param)
        raise SystemError("035:Missing Parameter: "+param)

    LOG.fw("035:Parameter = ", C_Slot)
    LOG.fw("035:Parameter = ", C_TID)
    LOG.fw("035:Parameter = ", C_MID)
    LOG.fw("035:Parameter = ", C_Token)

    res_str, cardno, amount, lastbalance, errmsg = mandiri_update_sam_balance_priv(C_Slot, C_TID, C_MID, C_Token)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = str(cardno) + "|" + str(amount) + "|" + str(lastbalance)
        LOG.fw("035:Response = ", cardno)
        LOG.fw("035:Response = ", amount)
        LOG.fw("035:Response = ", lastbalance)

        __global_response__["ErrorDesc"] = "Sukses"

        LOG.fw("035:Result = ", res_str)
        LOG.fw("035:Sukses", None)
    else:
        if errmsg == "0000":
            __global_response__["Response"] = res_str
            LOG.fw("035:Response = ", res_str, True)
        else:
            __global_response__["Response"] = errmsg
            LOG.fw("035:Response = ", errmsg, True)

        __global_response__["Result"] = "1"        
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("035:Result = ", 1, True)
        LOG.fw("035:Gagal", None, True)

    return res_str


def get_sub_code(resp_json_data):
    code = ""
    if type(resp_json_data) == 'str':
        resp_json_temp = json.loads(resp_json_data["data"])
    else:
        resp_json_temp = resp_json_data["data"]
    if "code" in resp_json_temp.keys():
        code = resp_json_temp["code"]
    elif "responseHeader" in resp_json_temp.keys():
        resp_json_temp = resp_json_temp["responseHeader"]
        if "error" in resp_json_temp.keys():
            resp_json_temp = resp_json_temp["error"]
            if "code" in resp_json_temp.keys():
                code = resp_json_temp["code"]
            elif "desc" in resp_json_temp.keys():
                code = resp_json_temp["desc"]
    return code, resp_json_temp


def mandiri_update_sam_balance_priv(C_Slot,C_TID, C_MID, C_Token):
    global UPDATE_BALANCE_URL

    approvalcode = int(time.time())
    url = UPDATE_BALANCE_URL
    errmsg = ""
    cardno = ""
    amount = "0"
    lastbalance = ""
    dataToCard = ""

    # res_str, uid = prepaid.send_apdu_cmd(C_Slot, b"00B4000007")
    # time.sleep(1)
    res_str, lastbalance, uidsam, data, attr  = prepaid.topup_C2C_km_balance()


    if res_str == "0000":
        attr = "0606170759424D79687875"

        if res_str == "0000":
            cardno = data[0:16]
            data = data + "9000"
            card_prev_balance = lastbalance
            response, status = send_update_balance(url, C_Token, C_TID, C_MID, cardno, approvalcode, attr, data, uidsam, card_prev_balance)

            if response == "1": response = status
            
            resp_json = json.loads(response)
            
            resp_json_response = resp_json["response"]
            resp_json_data = resp_json["data"]

            code = resp_json_response["code"]
            if code == "200" or code == 200:
                amount = resp_json_data["amount"]
                dataToCard = resp_json_data["dataToCard"]
                lastbalance = int(card_prev_balance) + int(amount)

            elif "code" in resp_json_data.keys():
                code = resp_json_data["code"]
                resp_json_temp = resp_json_data
            # # TODO: Recheck This
            # elif "data" in resp_json_data.keys():
            #     code, resp_json_temp = get_sub_code(resp_json_data)

# {\"response\":{\"code\":200,\"message\":\"OLD Applet, Ready For Confirmation\",\"latency\":1.4948790073395,\"host\":\"172.31.253.203\"},\"data\":{\"appletType\":\"OLD\",\"dataToCard\":\"00C7000030A20F0D46F73F30C9F37E787643CC9046B3D43CA3FDA2A2491DEAE2C8DCA1DF859FF47F97A6B82D2E80DE149877BF9B51\",\"amount\":\"2000000\"}

            code = str(code)

            if code == "51099":
                amount = resp_json_temp["amount_reversal"]
                approvalcode = resp_json_temp["approval_code"]
            
            if code == "200" or code == 200:
                updateStatusConfirm = "PENDING"
                res_str, resreport = prepaid.send_apdu_cmd(C_Slot, dataToCard)
                # res_str = prepaid_utils.to_4digit(res)
                #if 200
                if res_str == "0000":
                    res = True
                    dataToCardConfirm = resreport
                    while res and updateStatusConfirm == "PENDING":
                        dataToCardConfirm = dataToCardConfirm + "9000"
                        valuetext, errmsg = send_confirm_update(url,C_Token, C_TID, C_MID, cardno, dataToCardConfirm, "COMPLETED", approvalcode)
                        data_to_confirm = json.loads(valuetext)
                        codeConfirm = None

                        if "response" in data_to_confirm.keys():
                            temp_json = data_to_confirm["response"]
                            if "code" in temp_json.keys():
                                codeConfirm = temp_json["code"]
                        if "data" in data_to_confirm.keys():
                            temp_json = data_to_confirm["data"]
                            if "dataToCard" in temp_json.keys():
                                dataToCardConfirm = temp_json["dataToCard"]
                            if "updateStatus" in temp_json.keys():
                                updateStatusConfirm = temp_json["updateStatus"]
                        
                        codeConfirm = str(codeConfirm)

                        if codeConfirm == "200":
                            if updateStatusConfirm == "SUCCESS":
                                res_str = "0000"
                                res = True
                                break
                            else:
                                res_str, resreport = prepaid.send_apdu_cmd(C_Slot, dataToCardConfirm)
                                # res_str = prepaid_utils.to_4digit(res_w)

                                if res_str == "0000":
                                    dataToCardConfirm = resreport
                                    res = True
                                else:
                                    res = False
                                    break 
                        else:
                            res_str = codeConfirm
                            res = False
                            break
                    
            elif code == "51003":
                res_str = code
                errmsg = "NO PENDING BALANCE"
            elif code == "51099":
                #start reversal
                res_str, card_prev_balance, uidsam, data, attr  = prepaid.topup_C2C_km_balance()
                if res_str == "0000":
                    ResReversal = True
                    codereversal = ""
                    StatusReversal = ""

                    while ResReversal:
                        if StatusReversal == "":
                            valuetext,errmsg = send_reversal_topup(url, C_Token, C_TID, C_MID, cardno, card_prev_balance, approvalcode, amount, data, uidsam, "", dataToCard, attr)
                        else:
                            valuetext,errmsg = send_reversal_topup(url, C_Token, C_TID, C_MID, cardno, card_prev_balance, approvalcode, amount, data, uidsam, "REVERSAL_LOOP", dataToCard, attr)

                        jsonReversal = json.loads(valuetext)

                        if "response" in jsonReversal.keys():
                            temp_json = jsonReversal["response"]
                            if "code" in temp_json.keys():
                                codereversal = temp_json["code"]
                        if "data" in jsonReversal.keys():
                            temp_json = jsonReversal["data"]
                            if "reversalMessage" in temp_json.keys():
                                StatusReversal = temp_json["reversalMessage"]
                        
                        codereversal = str(codereversal)

                        if codereversal == "200":
                            if StatusReversal == "REVERSAL_DONE" or StatusReversal == "":
                                res_str = codereversal
                                ResReversal = False
                                errmsg = "REVERSAL_DONE"
                            else:
                                res_str, resreport = prepaid.send_apdu_cmd(C_Slot, StatusReversal)
                                # res_str = prepaid_utils.to_4digit(res_w)

                                if res_str == "0000":
                                    resreport= resreport+"9000"                                    
                                    dataToCard = resreport
                                    ResReversal = True
                                else:
                                    ResReversal = False
                                    errmsg = "REVERSAL_FAILED"
                        else:
                            res_str = codereversal
                            ResReversal = False
                            errmsg = "REVERSAL_FAILED"

            else:
                res_str = code

    lastbalance = str(lastbalance)
    return res_str, cardno, amount, lastbalance, errmsg


def send_confirm_update(URL_Server, TOKEN, TID, MID, card_no, sam_data, write_status, approval_code):
    global TIMEOUT_REQUESTS
    try:
        sURL = URL_Server + "topup-mandiri/confirm"

        # headers = {'Special-Case': 'TAPONBUSREADER'}
        payload = { 
            "token":TOKEN.decode("utf-8"), 
            "tid": TID.decode("utf-8"), 
            "mid": MID.decode("utf-8"), 
            "card_no":str(card_no),
            "approval_code": str(approval_code), 
            "sam_data":str(sam_data), 
            "write_status":str(write_status)
        }
        LOG.fw(":ConfirmMandiri url = ", sURL)
        LOG.fw(":ConfirmMandiri json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)
        ValueText = r.text
        LOG.fw(":ConfirmMandiri = ", ValueText)
        
        return ValueText, "0000"
    except Exception as ex:
        errorcode = "ConfirmMandiri error: {0}".format(ex)
        return "1", errorcode


def send_reversal_topup(URL_Server, token, tid, mid, card_no, last_balance, approval_code, amount, card_info, card_uid, mode, sam_data, card_attribute):
    global TIMEOUT_REQUESTS
    try:
        sURL = URL_Server + "topup-mandiri/reversal"

        # headers = {'Special-Case': 'TAPONBUSREADER'}
        payload = {
            "token":token.decode("utf-8"), 
            "tid": tid.decode("utf-8"), 
            "mid": mid.decode("utf-8"),
            "card_no":str(card_no),
            "card_uid":str(card_uid),
            "last_balance":str(last_balance),
            "approval_code":str(approval_code),
            "amount":str(amount),
            "card_attribute":str(card_attribute),
            "card_info":str(card_info),
            "mode": str(mode), 
            "sam_data":str(sam_data)
        }
        LOG.fw(":ReversalMandiri url = ", sURL)
        LOG.fw(":ReversalMandiri json = ", payload)

        r = requests.post(sURL, timeout=TIMEOUT_REQUESTS, json=payload)

        ValueText = r.text
        LOG.fw(":ReversalMandiri = ", ValueText)
        
        return ValueText, "0000"
    except Exception as ex:
        errorcode = "ReversalMandiri error: {0}".format(ex)
        return "1", errorcode


LAST_TIMESTAMP_MANDIRI = ''
#026
def mandiri_C2C_refill(param, __global_response__):
    global LAST_TIMESTAMP_MANDIRI
    # LOG.tracing("MANDIRI: ", "topup_C2C_refill")
    Param = param.split('|')
    if len(Param) == 1:
        C_Value = int(Param[0].encode('utf-8'),10)
        LOG.fw("026:Parameter Amount = ", C_Value)
    else:
        LOG.fw("026:Missing Parameter", param)
        raise SystemError("026:Missing Parameter: "+param)
    
    Timestamp = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    LOG.fw("026:Parameter Timestamp = ", Timestamp)
    LAST_TIMESTAMP_MANDIRI = Timestamp
    
    # res_str, reportSAM, debErrorStr = prepaid.topup_C2C_refill(C_Value, Timestamp)
    # Bind To New Topup Function
    res_str, reportSAM, debErrorStr = prepaid.new_topup_C2C_refill(C_Value, Timestamp)
    reportSAM = prepaid_utils.fix_report(reportSAM)

    __global_response__["Result"] = res_str

    balance = 0
    if res_str == "0000" :
        valueDeposit, valueEMoney, reportSAM = prepaid_utils.get_balance_from_report(reportSAM, "MANDIRI")

        balance = valueEMoney
        __global_response__["Response"] = str(balance) + "|" + reportSAM
        LOG.fw("026:Response = ", balance)
        LOG.fw("026:Response = ", reportSAM)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("026:Result = ", res_str)
        LOG.fw("026:Sukses", None)

    else:
        __global_response__["Response"] = reportSAM
        LOG.fw("026:Response = ", reportSAM, True)

        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("026:Result = ", res_str, True)
        LOG.fw("026:Gagal", None, True)

    return res_str

#027
def mandiri_C2C_init(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 3:
        C_Terminal = Param[0].encode('utf-8')
        C_MAC = Param[1].encode('utf-8')
        C_Slot =Param[2].encode('utf-8')
    else:
        LOG.fw("027:Missing Parameter", param)
        raise SystemError("027:Missing Parameter: "+param)

    LOG.fw("027:Parameter = ", C_Terminal)
    LOG.fw("027:Parameter = ", C_MAC)
    LOG.fw("027:Parameter = ", C_Slot)

    res_str = prepaid.topup_C2C_init(C_Terminal, C_MAC, C_Slot)
    
    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("027:Result = ", res_str)
        LOG.fw("027:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("027:Result = ", res_str, True)
        LOG.fw("027:Gagal", None, True)

    return res_str

#028
def mandiri_C2C_Correct(param, __global_response__):
    res_str, reportSAM, debErrorStr = prepaid.topup_C2C_Correct()

    __global_response__["Result"] = res_str

    balance = 0
    if res_str == "0000" :
        
        valueDeposit, valueEMoney, reportSAM = prepaid_utils.get_balance_from_report(reportSAM, "MANDIRI")

        balance = valueEMoney

        reportSAM = prepaid_utils.fix_report(reportSAM)

        __global_response__["Response"] = str(balance) + "|" + reportSAM
        LOG.fw("028:Response = ", balance)
        LOG.fw("028:Response = ", reportSAM)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("028:Result = ", res_str)
        LOG.fw("028:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("028:Result = ", res_str, True)
        LOG.fw("028:Gagal", None, True)

    return res_str

#029
def mandiri_C2C_getfee(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 1:
        C_Flag = Param[0].encode('utf-8')
    else:
        LOG.fw("029:Missing Parameter", param)
        raise SystemError("029:Missing Parameter: "+param)

    LOG.fw("029:Parameter = ", C_Flag)

    res_str, reportSAM, debErrorStr = prepaid.topup_C2C_getfee(C_Flag)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        reportSAM = prepaid_utils.fix_report(reportSAM)

        __global_response__["Response"] = reportSAM
        LOG.fw("029:Response = ", reportSAM)

        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("029:Result = ", res_str)
        LOG.fw("029:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("029:Result = ", res_str, True)
        LOG.fw("029:Gagal", None, True)

    return res_str

#030
def mandiri_C2C_setfee(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 2:
        C_Flag = Param[0].encode('utf-8')
        C_Response = Param[1].encode('utf-8')
    else:
        LOG.fw("030:Missing Parameter", param)
        raise SystemError("030:Missing Parameter: "+param)

    LOG.fw("030:Parameter = ", C_Flag)
    LOG.fw("030:Parameter = ", C_Response)

    res_str = prepaid.topup_C2C_setfee(C_Flag, C_Response)

    __global_response__["Result"] = res_str

    if res_str == "0000":
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("030:Result = ", res_str)
        LOG.fw("030:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("030:Result = ", res_str, True)
        LOG.fw("030:Gagal", None, True)

    return res_str

#031
def mandiri_C2C_force(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 1:
        C_Flag = Param[0]
    else:
        LOG.fw("031:Missing Parameter", param)
        raise SystemError("031:Missing Parameter: "+param)

    LOG.fw("031:Parameter = ", C_Flag)

    res_str,reportSAM,debErrorStr = prepaid.topup_C2C_force(C_Flag)

    __global_response__["Result"] = res_str

    balance = 0
    if res_str == "0000" :

        valueDeposit, valueEMoney, reportSAM = prepaid_utils.get_balance_from_report(reportSAM, "MANDIRI")

        balance = valueEMoney

        reportSAM = prepaid_utils.fix_report(reportSAM)
        __global_response__["Response"] = str(balance) + "|" + reportSAM
        LOG.fw("031:Response = ", balance)
        LOG.fw("031:Response = ", reportSAM)

        __global_response__["ErrorDesc"] = "Sukses"

        LOG.fw("031:Result = ", res_str)
        LOG.fw("031:Sukses", None)
    else:
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("031:Result = ", res_str, True)
        LOG.fw("031:Gagal", None, True)

    return res_str

# 041
def mandiri_get_last_report(param, __global_response__):
    Param = param.split('|')

    if len(Param) == 1:
        C_Slot = Param[0].encode('utf-8')
    else:
        LOG.fw("041:Missing Parameter", param)
        raise SystemError("041:Missing Parameter: "+param)

    LOG.fw("041:Parameter = ", C_Slot)

    res_str, errmsg = mandiri_get_last_report_priv(C_Slot)

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        LOG.fw("041:Response = ", errmsg)

        __global_response__["ErrorDesc"] = "Sukses"

        LOG.fw("041:Result = ", res_str)
        LOG.fw("041:Sukses", None)
    else:
        # __global_response__["Response"] = errmsg
        LOG.fw("041:ErrMsg = ", errmsg, True)
        
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("041:Result = ",res_str, True)
        LOG.fw("041:Gagal", None, True)

    return res_str


def old_mandiri_get_last_report_priv(C_Slot):

    resultStr = ""
    msg = ""
    report_1 = ""
    report_2 = ""

    try:
        resultStr, report_1 = prepaid.send_apdu_cmd(C_Slot, "00C2180000")

        if resultStr == "0000":
            resultStr, report_2 = prepaid.send_apdu_cmd(C_Slot, "00C2040000")
            msg = report_1 + report_2        
                
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg


# 100C = partial biasa
# 101C = partial dan sudah dilakukan force


def mandiri_get_last_report_priv(C_Slot):
    resultStr = ""
    msg = ""

    try:
        resultStr, report = prepaid.topup_C2C_last_report(C_Slot)
        if resultStr == "0000": msg = report        
                
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    return resultStr, msg
