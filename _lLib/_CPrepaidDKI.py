from _lLib import _CPrepaidDLL as prepaid
from _lLib import _CPrepaidUtils as utils
from _lLib import _CPrepaidLog as LOG
import datetime

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

DKI_REK_SUMBER = "43216000114"
DKI_REK_TUJUAN = "91192406095"

def DKI_RequestTopup(param, __global_response__):
    Param = param.split('|')
    if len(Param) == 1:
        C_Denom = Param[0]
    else:
        LOG.fw("051:Parameter tidak lengkap", param)
        raise Exception("051:Parameter tidak lengkap: "+param)
    
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
    global DKI_REK_SUMBER, DKI_REK_TUJUAN
    ResultStr = ""
    DepositCard=""
    ExpireCardDate=""
    report=""

    prepaid.topup_card_disconnect()

    ResultStr, BalValue, CardNo, SIGN = prepaid.topup_balance_with_sn()

    ResultStr, reportPurse, debErrorStr = prepaid.topup_pursedata()

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

