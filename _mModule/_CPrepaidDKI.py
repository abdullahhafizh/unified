__author__ = 'wahyudi@multidaya.id'

from _mModule import _CPrepaidDLL as prepaid
from _mModule import _CPrepaidUtils as utils
from _mModule import _CPrepaidLog as LOG
from _cConfig import _Common
import datetime
from time import sleep

"""
1. SIGN-ON
2. DebitRequest
3. GetCardData (Native)    
4. TopUpRequest
5. SendTopUpDataToCard (Native)
6. TopUpConfirm

IF 2 -> 6 FAILED:
R1. ReversalRequest

ISO SIGN-ON:
    DE2(7) = DateTime.Now.ToString("MMddhhmmss")
    DE2(11) = STAN
    DE2(41) = TID
    DE2(70) = "001"
    Dim iso8583_2 As New BIM_ISO8583.NET.ISO8583()
    Dim NewISOmsg As String = iso8583_2.Build(DE2, "0800")

ISO DebitRequest:
    DE_debit(2) = "0000000000000000"
    DE_debit(3) = "050000"
    DE_debit(4) = amount
    BIT7 = DateTime.Now.ToString("MMddHHmmss")
    DE_debit(7) = BIT7
    DE_debit(11) = STAN
    BIT12 = DateTime.Now.ToString("HHmmss")
    DE_debit(12) = BIT12
    DE_debit(13) = DateTime.Now.ToString("MMdd")
    'DE_debit(15) = DateTime.Now.ToString("MMdd")
    DE_debit(18) = "6010"
    DE_debit(32) = "100700"
    DE_debit(33) = "100700"
    BIT37 = ReffNo
    DE_debit(37) = BIT37
    DE_debit(41) = "GTL00" & Strings.Left(RekTujuan, 3) '"900"
    'DE_debit(42) = "VM" & TID & "00900"
    DE_debit(42) = "USERVM"
    DE_debit(43) = TID & "00900"
    DE_debit(49) = "360"
    DE_debit(62) = DateTime.Now.ToString("yyyy")
    DE_debit(102) = RekSumber
    DE_debit(103) = RekTujuan

    KeteranganTopup = "Pay TopupJakcard " & CardNo
    KeteranganTopup = KeteranganTopup.PadRight(50, " ")

    TermID = "GTL00" & Strings.Left(RekTujuan, 3) '"900"

    TermID = TermID.PadRight(16, " ")
    DE_debit(120) = KeteranganTopup

    'DE_debit(120) = "123456" & "123456" & TermID & "050000" & "200505191908" & KeteranganTopup
    'DE_debit(121) = "02" & "0404" & RekSumber & amount & "0304" & RekTujuan & amount

    DE_debit(121) = "02" & "0201" & RekSumber & amount & "0101" & RekTujuan & amount


    Dim iso8583_debit As New BIM_ISO8583.NET.ISO8583()
    Dim NewISOmsg_debit As String = iso8583_debit.Build(DE_debit, "0200")



ISO TopUpRequest:
ISOMessageBuilder
    .Packer(imohsenb.iso8583.enums.VERSION.V1987)
    .Financial.MTI(MESSAGE_FUNCTION.Request, MESSAGE_ORIGIN.Acquirer)
    .SetField(FIELDS.F2_PAN, "16" & CardNo)
    .SetField(FIELDS.F3_ProcessCode, "705000")
    .SetField(FIELDS.F4_AmountTransaction, Denom & "00")
    .SetField(FIELDS.F11_STAN, STAN)
    .SetField(FIELDS.F24_NII_FunctionCode, "100")
    .SetField(FIELDS.F41_CA_TerminalID, TID)
    .SetField(FIELDS.F42_CA_ID, CAID)
    .SetField(FIELDS.F46_AddData_ISO, "00")
    .SetField(FIELDS.F48_AddData_Private, report & DepositCard & ExpireCardDate)
    .SetField(FIELDS.F62_Reserved_Private, InvoiceNo)
    .SetHeader("6001003000")
    .Build()

ISO TopUpConfirm:
ISOMessageBuilder
    .Packer(imohsenb.iso8583.enums.VERSION.V1987)
    .Financial.MTI(MESSAGE_FUNCTION.Advice, MESSAGE_ORIGIN.Acquirer)
    .SetField(FIELDS.F2_PAN, "16" & CardNo)
    .SetField(FIELDS.F3_ProcessCode, "705000")
    .SetField(FIELDS.F4_AmountTransaction, Denom & "00")
    .SetField(FIELDS.F11_STAN, STAN)
    .SetField(FIELDS.F12_LocalTime, DateTime.Now.ToString("HHmmss"))
    .SetField(FIELDS.F13_LocalDate, DateTime.Now.ToString("MMdd"))
    .SetField(FIELDS.F24_NII_FunctionCode, "100")
    .SetField(FIELDS.F41_CA_TerminalID, TID)
    .SetField(FIELDS.F42_CA_ID, CAID)
    .SetField(FIELDS.F48_AddData_Private, reportdatatoconfirm)
    .SetField(FIELDS.F62_Reserved_Private, InvoiceNo)
    .SetHeader("6001003000")
    .Build()

"""

# DKI_REK_SUMBER = "43216000114"
# DKI_REK_TUJUAN = "91192406095"

def DKI_RequestTopup(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 1:
        C_Denom = Param[0]
    else:
        LOG.fw("051:Missing Parameter", param)
        raise SystemError("051:Missing Parameter: "+param)
    
    LOG.fw("051:Parameter = ", C_Denom)

    result_str, BalValue, CardNo, reportPurse, DepositCard, ExpireCardDate, report = DKI_RequestTopup_priv(C_Denom)

    __global_response__["Result"] = result_str
    if result_str == "0000":
        __global_response__["Response"] = CardNo + "|" + BalValue + "|" + reportPurse + "|" + DepositCard + "|" + ExpireCardDate + "|" + report
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("051:Response = ", __global_response__["Response"])

        LOG.fw("051:Result = ", result_str)
        LOG.fw("051:Sukses")
    else:
        __global_response__["Response"] = CardNo + "|" + BalValue + "|" + reportPurse + "|" + DepositCard + "|" + ExpireCardDate + "|" + report
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("051:Response = ", __global_response__["Response"], True)
        LOG.fw("051:Result = ", result_str, True)
        LOG.fw("051:Gagal", None, True)


def DKI_RequestTopup_priv(Denom):
    ResultStr = ""
    DepositCard=""
    ExpireCardDate=""
    report=""

    prepaid.topup_card_disconnect()

    ResultStr, BalValue, CardNo, SIGN = prepaid.topup_balance_with_sn()
    sleep(1)
    ResultStr, reportPurse, debErrorStr = prepaid.topup_pursedata()
    sleep(1)
    ResultStr, reportAPDU = prepaid.topup_apdusend("255", "00A4040008A0000005714E4A43")

    if ResultStr == "0000":
        CardNo = reportAPDU[16:32]
        LOG.fw("051:CardNo = ", CardNo)
        ExpireCardDate = reportAPDU[50:58]
        LOG.fw("051:ExpireCardDate = ", ExpireCardDate)
        DepositCard = reportAPDU[74:82]
        LOG.fw("051:DepositCard = ", DepositCard)

        amounthex = format(int(Denom), "x").upper().zfill(8)
        padding = "11111111111111111111111111"
        dtm_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        DATACARD = "9040000118" + amounthex + dtm_now + padding
        
        LOG.fw("051:DATACARD Send = ", DATACARD)
        ResultStr, report = prepaid.topup_apdusend("255", DATACARD)            
        LOG.fw("051:DATACARD Receive = ", report)

    return ResultStr, BalValue, CardNo, reportPurse, DepositCard, ExpireCardDate, report


def DKI_Topup(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 1:
        C_DataToCard = Param[0]
    else:
        LOG.fw("052:Missing Parameter", param)
        raise SystemError("052:Missing Parameter: "+param)
    
    LOG.fw("052:Parameter = ", C_DataToCard)

    result_str, report = DKI_Topup_priv(C_DataToCard)

    __global_response__["Result"] = result_str
    if result_str == "0000":
        __global_response__["Response"] = report
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("052:Response = ", __global_response__["Response"])

        LOG.fw("052:Result = ", result_str)
        LOG.fw("052:Sukses")
    else:
        __global_response__["Response"] = report
        __global_response__["ErrorDesc"] = "Gagal"

        LOG.fw("052:Response = ", __global_response__["Response"], True)
        LOG.fw("052:Result = ", result_str, True)
        LOG.fw("052:Gagal", None, True)


def DKI_Topup_priv(DataToCard):
    LOG.fw("052:DATACARD SEND 2 = ", DataToCard)
    DataToCard = "9042000010" + DataToCard
    ResultStr, reportRAPDU = prepaid.topup_apdusend("255", DataToCard)
    LOG.fw("052:DATACARD RECEIVE 2 = ", reportRAPDU)

    return ResultStr, reportRAPDU



#053
def dki_card_get_log(param, __global_response__):
    
    res_str, errmsg, desc = dki_card_get_log_priv()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        if type(desc) == list and len(desc) > 0:
            __global_response__["Response"] = errmsg + "#" + (",".join(desc))
        LOG.fw("053:Response = ", errmsg)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("053:Result = ", res_str)
        LOG.fw("053:Sukses", None)
    else:
        __global_response__["Response"] = errmsg
        LOG.fw("053:Response = ", errmsg, True)
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("053:Result = ",res_str, True)
        LOG.fw("053:Gagal", None, True)

    return res_str

#054
def dki_card_get_log_raw(param, __global_response__):
    
    res_str, errmsg, desc = dki_card_get_log_raw_priv()

    __global_response__["Result"] = res_str
    if res_str == "0000":
        __global_response__["Response"] = errmsg
        if type(desc) == list and len(desc) > 0:
            __global_response__["Response"] = ",".join(desc)
        LOG.fw("054:Response = ", errmsg)
        __global_response__["ErrorDesc"] = "Sukses"
        LOG.fw("054:Result = ", res_str)
        LOG.fw("054:Sukses", None)
    else:
        __global_response__["Response"] = errmsg
        LOG.fw("054:Response = ", errmsg, True)
        __global_response__["ErrorDesc"] = "Gagal"
        LOG.fw("054:Result = ",res_str, True)
        LOG.fw("054:Gagal", None, True)

    return res_str


def dki_card_get_log_priv():
    resultStr = ""
    resreport = ""
    msg = ""
    GetLogDKI = ""
    purseData = ""
    listRAPDU = []
    # Max History
    max_t = 10

    try:
        # resultStr = prepaid.topup_card_disconnect()
        resultStr, uid, cardno = prepaid.get_card_sn()
        # resultStr, purseData, errMessage = prepaid.topup_pursedata()
        if resultStr == "0000":
            i = 0
            while resultStr == "0000" and i <= max_t:
                if i > max_t:
                    break
                else:
                    i = i + 1                        

                    idx = hex_padding(i)
                    apdu = "00B2" + str(idx) + "242E"
                    resultStr, rapdu = prepaid.topup_apdusend("255", apdu)
                    if resultStr in ["9000", "0000"]:
                        # Type Fix Balance  Seq Num  TRX Amt  SAM              SAM Seq  Time (BCD)     AL Amt AL AccTl AL AcM AL AcD
                        # 01   2C  0000ABE0 00000004 00001770 D360010100000060 00000022 00000000000000 000000 00000000 000000 000000
                        if rapdu in listRAPDU:
                            continue
                        listRAPDU.append(rapdu)
                        types = rapdu[:2]
                        amount = int(rapdu[20:28], 16)
                        balance = int(rapdu[4:12], 16)
                        dates = rapdu[52:66]
                        resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates + "|" + str(balance)
                        msg = msg + resreport + "#"
                    else:
                        GetLogDKI= rapdu

        msg = msg + GetLogDKI
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    if len(listRAPDU) > 0: resultStr = '0000'
    
    return resultStr, msg, listRAPDU


def dki_card_get_log_raw_priv():
    resultStr = ""
    resreport = ""
    msg = ""
    GetLogDKI = ""
    purseData = ""
    listRAPDU = []
    # Max History
    max_t = 10

    try:
        # resultStr = prepaid.topup_card_disconnect()
        resultStr, uid, cardno = prepaid.get_card_sn()
        # resultStr, purseData, errMessage = prepaid.topup_pursedata()
        if resultStr == "0000":
            i = 0
            while resultStr == "0000" and i <= max_t:
                if i > max_t:
                    break
                else:
                    i = i + 1                        
                    idx = hex_padding(i)
                    apdu = "00B2" + str(idx) + "242E"
                    resultStr, rapdu = prepaid.topup_apdusend("255", apdu)
                    if resultStr in ["9000", "0000"]:
                        # Type Fix Balance  Seq Num  TRX Amt  SAM              SAM Seq  Time (BCD)     AL Amt AL AccTl AL AcM AL AcD
                        # 01   2C  0000ABE0 00000004 00001770 D360010100000060 00000022 00000000000000 000000 00000000 000000 000000
                        if rapdu in listRAPDU:
                            continue
                        listRAPDU.append(rapdu)
                        types = rapdu[:2]
                        amount = int(rapdu[20:28], 16)
                        balance = int(rapdu[4:12], 16)
                        dates = rapdu[52:66]
                        resreport = str(i) + "|" + types + "|" + str(amount) + "|" + dates + "|" + str(balance)
                        msg = msg + resreport + "#"
                    else:
                        GetLogDKI= rapdu

        msg = msg + GetLogDKI
        
    except Exception as ex:
        resultStr = "1"
        msg = "{0}".format(ex)
    
    if len(listRAPDU) > 0: resultStr = '0000'
    
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
