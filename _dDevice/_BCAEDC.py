__author__ = 'wahyudi@multidaya.id'

from serial import Serial
from enum import Enum
from time import sleep
from binascii import hexlify, unhexlify
from _mModule import _CPrepaidLog as LOG
from _cConfig import _Common
import json


class PROTO_FUNC(Enum):
    STX     = b"\x02" # Start of a data packet
    EXT     = b"\x03" # End of a data packet
    EOT     = b"\x04" # Cancellation of a command
    ENQ     = b"\x05" # Confirmation response
    ACK     = b"\x06" # Receiving response
    DLE     = b"\x10" # Start of a control word
    NAK     = b"\x15" # Error response
    BOT     = b"\x13" # Busy response
    FOT     = b"\x11" # Idle response, actively idle response only when feeding notes.
    REQ_LEN = b'\x01\x50'
    ECR_TYPE= b'\x01' #b'\x02'


ZERO = '0'
SPACE = ' '
YES = 'Y'
NO = 'N'
RESPONSE_LENGTH = 200
REQUEST_LENGTH = 150

RESPONSE_CODE = {
    '00' : 'Approve',
    '54' : 'Decline Expired Card',
    '55' : 'Decline Incorrect PIN',
    'P2' : 'Read Card Error',
    'P3' : 'User press Cancel on EDC',
    'Z3' : 'EMV Card Decline',
    'CE' : 'Connection Error/Line Busy TO Connection Timeout',
    'PT' : 'EDC Problem',
    'S3' : 'TXN BLM DIPROSES MINTA SCAN QR',
    'S4' : 'TXN EXPIRED ULANGI TRANSAKSI',
    'S2' : 'TRANSAKSI GAGAL ULANGI TRANSAKSI DI EDC',
    'TN' : 'Topup Tunai Not Ready',
}

TRANS_TYPE = {
    '01' :  'Purchase',
    '02' :  'Sale & Cash',
    '03' :  'Refund',
    '04' :  'Release Cardver',
    '05' :  'Authorization',
    '07' :  'Offline',
    '08' :  'Void',
    '10' :  'Settlement',
    '12' :  'Adjustment',
    '13' :  'Sale Contactless',
    '17' :  'Echo-test',
    '19' :  'Print Receipt and EDC sends the details (OriginalRRN will be sent from ECR)',
    '20' :  'Inquiry All Transaction',
    '21' :  'TOP UP Flazz using Debit Card (Source) and Flazz Card (Destination)',
    '22' :  'Cash TOP UP using Chasier Card (Source) and Flazz Card (Destination)',
    '23' :  'Get Card Information',
    '24' :  'Cash Top Up from ECR Flazz using Chasier Card (Source) and Flazz Card (Destination)',
    '25' :  'Get Card Information – Kompas',
    '26' :  'Payment Transaction Sakuku',
    '27' :  'Continue Transaction Sakuku',
    '28' :  'Inquiry Transaction Sakuku',
    '31' :  'Payment QRIS',
    '32' :  'Inquiry QRIS',
    '36' :  'Balance Inquiry Flazz (prepaid) Card',
}

TRANS_TYPE_CMD = {v.lower(): k for k, v in TRANS_TYPE.items()}

CANCEL_REASON = {
    '01' : 'Time-out Reversal',
    '02' : 'Transaction Void',
    '03' : 'Signature Declined Void',
    '04' : 'User Cancelled',
    '05' : 'EMV Declined',
    '06' : 'Others',
    '07' : 'Power Failure',
}

CARD_ISSUER = {
    '00' : 'Debit BCA',
    '01' : 'Visa',
    '02' : 'Mastercard',
    '03' : 'AMEX',
    '04' : 'Diners Club',
    '05' : 'JCB',
    '06' : 'UP ( Union pay)',
    '07' : 'BCA Card',
    '08' : 'Others',
    '09' : 'AMEX BCA',
    '10' : 'BCA Syariah',
    '11' : 'Cash BCA',
    '12' : 'Smartcash',
    '13' : 'Debit MC BCA',
    '14' : 'Flazz BCA',
    '15' : 'JCB BCA',
    '16' : 'Maestro',
    '17' : 'Master BCA',
    '18' : 'Unionpay BCA',
    '19' : 'Visa BCA',
    '20' : 'Visa SQ',
}

def get_card_type(issuer):
    card_issuer = CARD_ISSUER.get(issuer, 'CREDIT')
    return 'DEBIT' if 'debit' in card_issuer.lower() else 'CREDIT'


LENGTH = {
    'Version' : 1,
    'TransType' : 2,
    'TransAmount' : 12,
    'OtherAmount' : 12,
    'PAN' : 19,
    'ExpiryDate' : 4,
    'CancelReason' : 2,
    'InvoiceNumber' : 6,
    'AuthorizationIDResponse' : 6,
    'InstallmentFlag' : 1,
    'RedeemFlag' : 1,
    'DCCFlag' : 1,
    'InstallmentPlan' : 3,
    'InstallmentTenor' : 2,
    'GenericData' : 12,
    'ReffNumber' : 12,
    'OriginalDate' : 4,
    'Filler' : 50,
}


def calculate_crc(data=b""):
    crc = 0
    for x in data :
        crc = crc ^ x
    output = [
        crc.to_bytes(1, byteorder='big'),
        hex(crc)
        ]
    if not _Common.LIVE_MODE:
        print('LRC Input', data, len(data))
        print('LRC Output', output)
    return output[0]


def build_command(wByte=b''):
    # return decimal_to_bcd(wByte) + wByte + PROTO_FUNC.EXT.value
    return PROTO_FUNC.REQ_LEN.value + wByte + PROTO_FUNC.EXT.value


def send_wait_response(ser=Serial(), wByte=b""):   
    debug = not _Common.LIVE_MODE
    cmd =  build_command(wByte)
    wByte = PROTO_FUNC.STX.value + cmd + calculate_crc(cmd)
    ser.write(wByte)
    LOG.ecrlog("[ECR] WRITE: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, wByte)

    counter = 0
    proto = None
    retrigger = False
    while True:
        rByte = ser.read_until(size=1)
        LOG.ecrlog("[ECR] READING: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, rByte)
        if debug: print("[ECR] READING: ", rByte)
        # Grab ACK
        if rByte == PROTO_FUNC.ACK.value:
            proto = PROTO_FUNC.ACK
            LOG.ecrlog("[ECR] FOUND ACK: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, rByte)
            if debug: print("[ECR] FOUND ACK: ", rByte)
            break
        # Grab NAK
        if rByte == PROTO_FUNC.NAK.value:
            proto = PROTO_FUNC.NAK
            LOG.ecrlog("[ECR] FOUND NAK: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, rByte)
            if debug: print("[ECR] FOUND NAK: ", rByte)
            return False
        # Resend Command If No ACK Found After 2s
        if counter == 2 and not retrigger:
            ser.write(wByte)
            LOG.ecrlog("[ECR] RE-WRITE: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, wByte)
            if debug: print("[ECR] RE-WRITE: ", wByte)
            retrigger = True
            counter = 0
            continue
        # No Response at-all After re-trigger
        if counter > (_Common.EDC_PAYMENT_DURATION-3):
            LOG.ecrlog("[ECR] TIMEOUT CMD: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, counter)
            if debug: print("[ECR] TIMEOUT CMD: ", counter)
            rByte = False
            break
        counter = counter + 1
        sleep(1)
        
    while proto == PROTO_FUNC.ACK:
        # Do Need Reset Counter ?
        # counter = 0
        rByte = ser.read_until(PROTO_FUNC.EXT.value)
        LOG.ecrlog("[ECR] RESULT: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, rByte)
        if debug: print("[ECR] RESULT: ", rByte)
        # Read and Looking For The End TRX
        if PROTO_FUNC.EXT.value in rByte:
            # Flag ACK
            # Resend ACK to EDC
            ser.write(PROTO_FUNC.ACK.value)
            LOG.ecrlog("[ECR] RESEND ACK: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, (PROTO_FUNC.ACK.value))
            if debug: print("[ECR] RESEND ACK: ", PROTO_FUNC.ACK.value)
            break
        if counter > _Common.EDC_PAYMENT_DURATION:
            LOG.ecrlog("[ECR] TIMEOUT RESULT: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, counter)
            if debug: print("[ECR] TIMEOUT RESULT: ", counter)
            rByte = False
            break
        counter = counter + 1
        sleep(1)
        
    return rByte

ECR_BAUDRATE = 115200
ECR_TIMEOUT = 60
ECR_STOPBITS = 1
ECR_DATABITS = 8


class BCAEDC():
    def __init__(self) -> None:
        self.ser = None
    
    def connect(self, port="COM7"):
        LOG.ecrlog("[ECR] configuration: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, json.dumps(_Common.EDC))
        if self.ser is None:
            self.ser = Serial(
                port=port, 
                bytesize=ECR_DATABITS,
                stopbits=ECR_STOPBITS,
                baudrate=ECR_BAUDRATE, 
                timeout=ECR_TIMEOUT
                )
            result = self.ser.isOpen()
            LOG.ecrlog("[ECR] connect: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        else:
            if self.ser.isOpen():
                # self.ser.close()
                self.disconnect()
                self.ser = Serial(port=port, baudrate=ECR_BAUDRATE, timeout=ECR_TIMEOUT)
            result = self.ser.isOpen()
            LOG.ecrlog("[ECR] re-connect: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        return result
    
    def disconnect(self):
        LOG.ecrlog("[ECR] disconnect: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW, '')
        self.ser.close()
    
    def do_payment(self, trxid, amount):
        self.trxid = trxid
        self.amount = amount
        ecr_message = ECRMessage('Purchase', self.amount)
        tle_message = ecr_message.build('encoded')
        LOG.ecrlog("[ECR] do_payment[D]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, ecr_message.parse())
        LOG.ecrlog("[ECR] do_payment[S]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, tle_message)
        result = send_wait_response(self.ser, tle_message)
        if not result:
            del ecr_message
            return False, []
        # Slice 4 (STX (2 bytes), Message Length (2 bytes))
        response = ecr_message.parse_response(result[4:].decode('utf-8'))
        LOG.ecrlog("[ECR] do_payment[R]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, json.dumps(response))
        del ecr_message
        # Refill TRXID in struck_id
        if response.get('struck_id') == '': response['struck_id'] = self.trxid
        return True, response
    
    def card_info(self):
        ecr_message = ECRMessage('Get Card Information', '0')
        tle_message = ecr_message.build('encoded')
        LOG.ecrlog("[ECR] card_info[D]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, ecr_message.parse())
        LOG.ecrlog("[ECR] card_info[S]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, tle_message)
        result = send_wait_response(self.ser, tle_message)
        if not result:
            del ecr_message
            return False, []
        # Slice 4 (STX (2 bytes), Message Length (2 bytes))
        response = ecr_message.parse_response(result[4:].decode('utf-8'), True)
        LOG.ecrlog("[ECR] card_info[R]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, json.dumps(response))
        del ecr_message
        return True, response
    
    def echo_test(self):
        ecr_message = ECRMessage('Echo-test', '0')
        tle_message = ecr_message.build('encoded')
        LOG.ecrlog("[ECR] echo_test[D]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, ecr_message.parse())
        LOG.ecrlog("[ECR] echo_test[S]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, tle_message)
        result = send_wait_response(self.ser, tle_message)
        if not result:
            del ecr_message
            return False, []
        # Slice 4 (STX (2 bytes), Message Length (2 bytes))
        response = ecr_message.parse_response(result[4:].decode('utf-8'), True)
        LOG.ecrlog("[ECR] echo_test[R]: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, json.dumps(response))
        del ecr_message
        return True, response
    
    def get_trxid(self):
        LOG.ecrlog("[ECR] get_trxid: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW, self.trxid)
        return self.trxid
    
    def get_amount(self):
        LOG.ecrlog("[ECR] get_amount: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW, self.amount)
        return self.amount
    

class ECRMessage():
    def __init__(self, type, amount) -> None:
        self.Version = b'\x01' #Version of ECR Message (in Hex), always “02h” Transaction type
        self.TransType = '' #Transaction type
        if type.lower() in [x for x in TRANS_TYPE_CMD.keys()]:
            self.TransType = TRANS_TYPE_CMD[type.lower()]
        self.TransAmount = ZERO * LENGTH.get('TransAmount') #Transaction total amount, 0 left padding
        if int(amount) > 0:
            self.TransAmount = (str(amount) + '00').zfill(LENGTH.get('TransAmount'))
        self.OtherAmount = ZERO * LENGTH.get('OtherAmount') #Present for Sale & Cash (Debit), Sale & Tip (Credit) , 0 left padding
        self.PAN = SPACE * LENGTH.get('PAN') #For manual entry transaction, space character right padding, default to spaces
        self.ExpiryDate = ZERO * LENGTH.get('ExpiryDate') #For manual entry transaction, default to zeros
        self.CancelReason = ZERO * LENGTH.get('CancelReason') #Void/Cancel Reason, default to zeros
        self.InvoiceNumber = SPACE * LENGTH.get('InvoiceNumber') #Invoice Number from original transaction, default to zeros
        self.AuthorizationIDResponse = SPACE * LENGTH.get('AuthorizationIDResponse') #Approval Code from Card Verification transaction,default to spaces
        self.InstallmentFlag = NO * LENGTH.get('InstallmentFlag') #Installment indicator, default value Y or N
        self.RedeemFlag = NO * LENGTH.get('RedeemFlag')#Redeem indicator for Loyalti Transaction, default value Y or N
        self.DCCFlag = NO * LENGTH.get('DCCFlag')#DCC ( Dynamic Currency Converter ) indicator for Adjusment Transaction, default value Y or N
        self.InstallmentPlan = SPACE * LENGTH.get('InstallmentPlan') #Plan of Installment Transaction, default to spaces
        self.InstallmentTenor = SPACE * LENGTH.get('InstallmentTenor') #Month of Installment Transaction, default to spaces
        self.GenericData = SPACE * LENGTH.get('GenericData') #Free Text for Merchant Information, can be printed in transaction receipt,default to spaces
        self.ReffNumber = SPACE * LENGTH.get('ReffNumber') #Reff number input from payment Sakuku Transaction
        self.OriginalDate = SPACE * LENGTH.get('OriginalDate') #For release cardver original date mandatory MMDD
        self.Filler = SPACE * LENGTH.get('Filler') #default to spaces
        
    def build(self, output='plain'):
        data = [
            self.Version.decode(),
            self.TransType,
            self.TransAmount,
            self.OtherAmount, 
            self.PAN, 
            self.ExpiryDate, 
            self.CancelReason, 
            self.InvoiceNumber, 
            self.AuthorizationIDResponse, 
            self.InstallmentFlag, 
            self.RedeemFlag, 
            self.DCCFlag, 
            self.InstallmentPlan, 
            self.InstallmentTenor, 
            self.GenericData, 
            self.ReffNumber, 
            self.OriginalDate, 
            self.Filler, 
        ]
        message = ''.join(data)
        if output.lower() != 'plain': 
            # if not _Common.LIVE_MODE:
            #     for l in LENGTH: print(l, LENGTH.get(l))
            #     print('---')
            #     for d in data: print(d, len(d))
            print('EDC Build Message', message, len(message))
        return message if output.lower() == 'plain' else message.encode('utf-8')
    
    def parse(self, message=None):
        if message is not None: message = str(message)
        else: message = self.build('plain')
        return {
            'Version' : message[0:1],
            'TransType' : message[1:(1+LENGTH.get('TransType'))],
            'TransAmount' : message[3:(3+LENGTH.get('TransAmount'))],
            'OtherAmount' : message[15:(15+LENGTH.get('OtherAmount'))],
            'PAN' : message[27:(27+LENGTH.get('PAN'))],
            'ExpiryDate' : message[46:(46+LENGTH.get('ExpiryDate'))],
            'CancelReason' : message[50:(50+LENGTH.get('CancelReason'))],
            'InvoiceNumber' : message[52:(52+LENGTH.get('InvoiceNumber'))],
            'AuthorizationIDResponse' : message[58:(58+LENGTH.get('AuthorizationIDResponse'))],
            'InstallmentFlag' : message[64:(64+LENGTH.get('InstallmentFlag'))],
            'RedeemFlag' : message[65:(65+LENGTH.get('RedeemFlag'))],
            'DCCFlag' : message[66:(66+LENGTH.get('DCCFlag'))],
            'InstallmentPlan' : message[69:(69+LENGTH.get('InstallmentPlan'))],
            'InstallmentTenor' : message[71:(71+LENGTH.get('InstallmentTenor'))],
            'GenericData' : message[73:(73+LENGTH.get('GenericData'))],
            'ReffNumber' : message[85:(85+LENGTH.get('ReffNumber'))],
            'OriginalDate' : message[97:(97+LENGTH.get('OriginalDate'))],
            'Filler' : message[101:(101+LENGTH.get('Filler'))],
        }
        
    def parse_response(self, message, original=False):
        if not _Common.LIVE_MODE: print('parse_response [INPUT]', message, len(message))
        message = str(message)
        # \x02\x02\x00\x01 -> Sliced STX & Version
        # 01000000000000000000000000                       P3                                                                                                                                                    
        # \x03 -> ETX
        res_code = message[49:51]
        trx_amount = str(int(message[2:14])/100)
        original_data = {
            'TransType'         : message[0:2],
            'TransAmount'       : trx_amount,
            'OtherAmount'       : message[14:26],
            'PAN'               : message[26:45],
            'ExpiryDate'        : message[45:49],
            'ResponseCode'      : res_code,
            'RRN'               : message[51:63],
            'ApprovalCode'      : message[63:69],
            'TransDate'         : message[69:77],
            'TransTime'         : message[77:83],
            'MerchantID'        : message[83:98],
            'TerminalID'        : message[98:106],
            'OfflineFlag'       : message[106:107],
            'CardholderName'    : message[107:133],
            'PANCashierCard'    : message[133:149],
            'InvoiceNumber'     : message[149:155],
            'BatchNumber'       : message[155:161],
            'IssuerID'          : message[161:163],
            'InstallmentFlag'   : message[163:164],
            'DCCFlag'           : message[164:165],
            'RewardsLoyaltyFlag': message[165:166], #RedeemFlag
            'InfoAmount'        : message[166:178],
            'DCCDecimalPlace'   : message[178:179],
            'DCCCurrencyName'   : message[179:182],
            'DCCExchangeRate'   : message[182:190],
            'CouponFlag'        : message[190:191],
            'Filler'            : message[191:200],       
        }
        if not _Common.LIVE_MODE: print('[ECR] parse_response -> original', json.dumps(original_data))
        map_data = {
            'raw'           : message,
            'card_type'     : get_card_type(original_data.get('IssuerID')),
            'struck_id'     : '',
            'status'        : 'SUCCESS' if res_code == '00' else RESPONSE_CODE.get(res_code, 'UNKNOWN').upper(),
            'amount'        : original_data.get('TransAmount'),
            'res_code'      : res_code,
            'trace_no'      : original_data.get('RRN').strip(),
            'inv_no'        : original_data.get('InvoiceNumber'),
            'card_no'       : original_data.get('PAN')[:16],
            'card_pan'      : original_data.get('PAN')[:16],
            'exp_date'      : original_data.get('ExpiryDate'),
            'trans_date'    : ''.join([original_data.get('TransDate'), original_data.get('TransTime')]),
            'app_code'      : original_data.get('ApprovalCode'),
            'tid'           : original_data.get('TerminalID'),
            'mid'           : original_data.get('MerchantID'),
            'ref_no'        : original_data.get('RRN').strip(),
            'bank_reff_no'  : original_data.get('RRN').strip(),
            'batch_no'      : original_data.get('BatchNumber'),
        }
        if not _Common.LIVE_MODE: print('[ECR] parse_response -> mapped', json.dumps(map_data))
        result = map_data if not original else original_data
        return result

# SIMULATOR LOG

# ECR --> EDC : [ SALE ] 8/24/2023 12:45:43 PM
# Start of Text       : 02 ( HEX )
# Message Length      : 0150 ( HEX )
# ECR Version         : 01 ( HEX )
# Transaction Type    : 01 ( 3031 ) ( ASCII )
# Transaction Amount  : 000000001000 ( 303030303030303031303030 ) ( ASCII )
# Other Amount        : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# PAN                 :                     ( 20202020202020202020202020202020202020 ) ( ASCII )
# Expire Date         :      ( 20202020 ) ( ASCII )
# Cancel Reason       : 00 ( 3030 ) ( ASCII )
# Invoice Number      : 000000 ( 303030303030 ) ( ASCII )
# Auth Code           : 000000 ( 303030303030 ) ( ASCII )
# Installment Flag    :   ( 20 ) ( ASCII )
# Reedem Flag         :   ( 20 ) ( ASCII )
# DCC Flag            : N ( 4E ) ( ASCII )
# Installment Plan    : 000 ( 303030 ) ( ASCII )
# Installment Tenor   : 00 ( 3030 ) ( ASCII )
# Generic Data        :              ( 202020202020202020202020 ) ( ASCII )
# Reff. Number        :              ( 202020202020202020202020 ) ( ASCII )
# Merchant Filler     :                                                        ( 202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020 ) ( ASCII )
# End of Text         : 03 ( HEX )
# CRC                 : 0D ( HEX )

# EDC --> ECR : [ SALE ] 8/24/2023 12:45:44 PM
# ACK                 : 06 ( HEX )

# NORMAL

# EDC --> ECR : [ SALE ] 8/24/2023 1:55:14 PM
# Start of Text       : 02 ( HEX )
# Message Length      : 0200 ( HEX )
# ECR Version         : 01 ( HEX )
# Transaction Type    : 01 ( 3031 ) ( ASCII )
# Transaction Amount  : 000000001000 ( 303030303030303031303030 ) ( ASCII )
# Other Amount        : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# PAN                 : ************3367    ( 2A2A2A2A2A2A2A2A2A2A2A2A33333637202020 ) ( ASCII )
# Expire Date         : **** ( 2A2A2A2A ) ( ASCII )
# Response Code       : 00 ( 3030 ) ( ASCII )
# RRN                 :       000136 ( 202020202020303030313336 ) ( ASCII )
# Approval Code       : 135537 ( 313335353337 ) ( ASCII )
# Transaction Date    : 20230824 ( 3230323330383234 ) ( ASCII )
# Transaction Time    : 135537 ( 313335353337 ) ( ASCII )
# Merchant ID         : 000885000224162 ( 303030383835303030323234313632 ) ( ASCII )
# Terminal ID         : DVMMDD01 ( 44564D4D44443031 ) ( ASCII )
# Offline Flag        : N ( 4E ) ( ASCII )
# Cardholder Name     :                         /  ( 2020202020202020202020202020202020202020202020202F20 ) ( ASCII )
# PAN Cashier Card    :                  ( 20202020202020202020202020202020 ) ( ASCII )
# Invoice Number      : 000018 ( 303030303138 ) ( ASCII )
# Batch Number        : 000002 ( 303030303032 ) ( ASCII )
# Issuer ID           : 00 ( 3030 ) ( ASCII )
# Installment Flag    : N ( 4E ) ( ASCII )
# DCC Flag            : N ( 4E ) ( ASCII )
# Rewards/Loyalty Flag: N ( 4E ) ( ASCII )
# Info Amount         : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# DCC Decimal Place   :   ( 20 ) ( ASCII )
# DCC Currency Name   :     ( 202020 ) ( ASCII )
# DCC Exchange Rate   :          ( 2020202020202020 ) ( ASCII )
# Coupon Flag         : N ( 4E ) ( ASCII )
# Filler              :          ( 2020202020202020 ) ( ASCII )
# End of Text         : 03 ( HEX )
# CRC                 : 45 ( HEX )

# ECR --> EDC : [ SALE ] 8/24/2023 1:55:48 PM
# ACK                 : 06 ( HEX )

# DECLINED

# EDC --> ECR : [ SALE ] 8/24/2023 12:45:44 PM
# Start of Text       : 02 ( HEX )
# Message Length      : 0200 ( HEX )
# ECR Version         : 01 ( HEX )
# Transaction Type    : 01 ( 3031 ) ( ASCII )
# Transaction Amount  : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# Other Amount        : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# PAN                 :                     ( 20202020202020202020202020202020202020 ) ( ASCII )
# Expire Date         :      ( 20202020 ) ( ASCII )
# Response Code       : PT ( 5054 ) ( ASCII )
# RRN                 :              ( 202020202020202020202020 ) ( ASCII )
# Approval Code       :        ( 202020202020 ) ( ASCII )
# Transaction Date    :          ( 2020202020202020 ) ( ASCII )
# Transaction Time    :        ( 202020202020 ) ( ASCII )
# Merchant ID         :                 ( 202020202020202020202020202020 ) ( ASCII )
# Terminal ID         :          ( 2020202020202020 ) ( ASCII )
# Offline Flag        :   ( 20 ) ( ASCII )
# Cardholder Name     :                            ( 2020202020202020202020202020202020202020202020202020 ) ( ASCII )
# PAN Cashier Card    :                  ( 20202020202020202020202020202020 ) ( ASCII )
# Invoice Number      :        ( 202020202020 ) ( ASCII )
# Batch Number        :        ( 202020202020 ) ( ASCII )
# Issuer ID           :    ( 2020 ) ( ASCII )
# Installment Flag    :   ( 20 ) ( ASCII )
# DCC Flag            :   ( 20 ) ( ASCII )
# Rewards/Loyalty Flag:   ( 20 ) ( ASCII )
# Info Amount         :              ( 202020202020202020202020 ) ( ASCII )
# DCC Decimal Place   :   ( 20 ) ( ASCII )
# DCC Currency Name   :     ( 202020 ) ( ASCII )
# DCC Exchange Rate   :          ( 2020202020202020 ) ( ASCII )
# Coupon Flag         :   ( 20 ) ( ASCII )
# Filler              :          ( 2020202020202020 ) ( ASCII )
# End of Text         : 03 ( HEX )
# CRC                 : 25 ( HEX )

# ECR --> EDC : [ SALE ] 8/24/2023 12:46:34 PM
# ACK                 : 06 ( HEX )

# ERROR CARD

# EDC --> ECR : [ SALE ] 8/24/2023 1:48:52 PM
# Start of Text       : 02 ( HEX )
# Message Length      : 0200 ( HEX )
# ECR Version         : 01 ( HEX )
# Transaction Type    : 01 ( 3031 ) ( ASCII )
# Transaction Amount  : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# Other Amount        : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# PAN                 :                     ( 20202020202020202020202020202020202020 ) ( ASCII )
# Expire Date         : 0000 ( 30303030 ) ( ASCII )
# Response Code       : P2 ( 5032 ) ( ASCII )
# RRN                 :              ( 202020202020202020202020 ) ( ASCII )
# Approval Code       :        ( 202020202020 ) ( ASCII )
# Transaction Date    :          ( 2020202020202020 ) ( ASCII )
# Transaction Time    :        ( 202020202020 ) ( ASCII )
# Merchant ID         :                 ( 202020202020202020202020202020 ) ( ASCII )
# Terminal ID         :          ( 2020202020202020 ) ( ASCII )
# Offline Flag        : N ( 4E ) ( ASCII )
# Cardholder Name     :                            ( 2020202020202020202020202020202020202020202020202020 ) ( ASCII )
# PAN Cashier Card    :                  ( 20202020202020202020202020202020 ) ( ASCII )
# Invoice Number      : 000000 ( 303030303030 ) ( ASCII )
# Batch Number        :        ( 202020202020 ) ( ASCII )
# Issuer ID           : 00 ( 3030 ) ( ASCII )
# Installment Flag    : N ( 4E ) ( ASCII )
# DCC Flag            : N ( 4E ) ( ASCII )
# Rewards/Loyalty Flag: N ( 4E ) ( ASCII )
# Info Amount         : 000000000000 ( 303030303030303030303030 ) ( ASCII )
# DCC Decimal Place   :   ( 20 ) ( ASCII )
# DCC Currency Name   :     ( 202020 ) ( ASCII )
# DCC Exchange Rate   :          ( 2020202020202020 ) ( ASCII )
# Coupon Flag         : N ( 4E ) ( ASCII )
# Filler              :          ( 2020202020202020 ) ( ASCII )
# End of Text         : 03 ( HEX )
# CRC                 : 2D ( HEX )

# ECR --> EDC : [ SALE ] 8/24/2023 1:49:01 PM
# ACK                 : 06 ( HEX )


