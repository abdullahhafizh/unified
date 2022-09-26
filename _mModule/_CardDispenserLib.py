from serial import Serial
from time import sleep
from datetime import datetime
from pytlv.TLV import *

LOG = ""

DEBUG_MODE = True

CARD_MOVE_TO_HOLD = b"\x30"
CARD_MOVE_TO_IC = b"\x31"
CARD_MOVE_TO_RF = b"\x32"
CARD_MOVE_TO_ERROR = b"\x33"
CARD_MOVE_TO_GATE = b"\x39"

CM_INITIALIZE = b"\x30"
CM_STATUS_REQUEST = b"\x31"
CM_CARD_MOVE = b"\x32"
CM_CARD_ENTRY = b"\x33"
CM_CARD_TYPE = b"\x50"
CM_CPUCARD_CONTROL = b"\x51"
CM_SAMCARD_CONTROL = b"\x52"
CM_SLECARD_CONTROL = b"\x53"
CM_ICMEMORYCARD_CONTROL = b"\x54"
CM_RFCARD_CONTROL = b"\x60"
CM_CRT_SERIALNUMBER = b"\xA2"
CM_CRT_CONFIG = b"\xA3"
CM_CRT_VERSION = b"\xA4"
CM_RECYLERBIN_COUNTER = b"\xA5"

CM_MESSAGE = {
    CM_INITIALIZE : b"CM_INITIALIZE",
    CM_STATUS_REQUEST : b"CM_STATUS_REQUEST",
    CM_CARD_MOVE : b"CM_CARD_MOVE",
    CM_CARD_ENTRY : b"CM_CARD_ENTRY",
    CM_CARD_TYPE : b"CM_CARD_TYPE",
    CM_CPUCARD_CONTROL : b"CM_CPUCARD_CONTROL",
    CM_SAMCARD_CONTROL : b"CM_SAMCARD_CONTROL",
    CM_SLECARD_CONTROL : b"CM_SLECARD_CONTROL",
    CM_ICMEMORYCARD_CONTROL : b"CM_ICMEMORYCARD_CONTROL",
    CM_RFCARD_CONTROL : b"CM_RFCARD_CONTROL",
    CM_CRT_SERIALNUMBER : b"CM_CRT_SERIALNUMBER",
    CM_CRT_CONFIG : b"CM_CRT_CONFIG",
    CM_CRT_VERSION : b"CM_CRT_VERSION",
    CM_RECYLERBIN_COUNTER : b"CM_RECYLERBIN_COUNTER"
}

CARD_POS_NOCARD = b"0"
CARD_POS_GATE = b"1"
CARD_POS_RFIC = b"2"

STACKER_EMPTY = b"0"
STACKER_NEAR_EMPTY = b"1"
STACKER_FULL = b"2"

ERRORBIN_NOT_FULL = b"0"
ERRORBIN_FULL = b"1"

ST0_MESSAGE = {
    CARD_POS_NOCARD : b"No Card in CRT-571",
    CARD_POS_GATE : b"One Card in gate",
    CARD_POS_RFIC : b"One Card on RF/IC Card Position",
}
ST1_MESSAGE = {
    STACKER_EMPTY: b"No Card in stacker",
    STACKER_NEAR_EMPTY: b"Few Card in stacker",
    STACKER_FULL: b"Enough Cards in card box",
}
ST2_MESSAGE = {
    ERRORBIN_NOT_FULL: b"ErrorCard bin not full",
    ERRORBIN_FULL: b"ErrorCard bin full",
}

ERROR_MESSAGE = {
    b"00": b"Reception of Undefined Command",
    b"01": b"Command Parameter Error",
    b"02": b"Command Sequence Error",
    b"03": b"Out of Hardware Support Command",
    b"04": b"Command Data Error",
    b"05": b"IC Card Contact Not Release",
    b"10": b"Card Jam",
    b"12": b"sensor error",
    b"13": b"Too Long-Card ",
    b"14": b"Too Short-Card",
    b"40": b"Disability of Recycling card",
    b"41": b"Magnet of IC Card Error",
    b"42": b"Disable To Move Card To IC Card Position",
    b"45": b"Manually Move Card",
    b"50": b"Received Card Counter Overflow",
    b"51": b"Motor error",
    b"60": b"Short Circuit of IC Card Supply Power",
    b"61": b"Activiation of Card False",
    b"62": b"Command Out Of IC Card Support",
    b"65": b"Disablity of IC Card",
    b"66": b"Command Out Of IC Current Card Support",
    b"67": b"IC Card Transmittion Error",
    b"68": b"IC Card Transmittion Overtime",
    b"69": b"CPU/SAM Non-Compliance To EMV Standard",
    b"A0": b"Empty-Stacker",
    b"A1": b"Full-Stacker",
    b"B0": b"Not Reset"
}

STATUS_HEAD_OK = b"P"
STATUS_ERROR = b"N"

IC_CARD_TYPE = {
    b"00": b"Unknown IC Card Type",
    b"10": b"T=0 CPU Card",
    b"11": b"T=1 CPU Card",
    b"20": b"SLE4442 Card",
    b"21": b"SLE4428 Card",
    b"30": b"AT24C01 Card",
    b"31": b"AT24C02 Card",
    b"32": b"AT24C04 Card",
    b"33": b"AT24C08 Card",
    b"34": b"AT24C16 Card",
    b"35": b"AT24C32 Card",
    b"36": b"AT24C64 Card",
    b"37": b"AT24C128 Card",
    b"38": b"AT24C256 Card"
}
CARD_TYPE_CPU = 0x31
CARD_TYPE_SLE = 0x32
CARD_TYPE_AT = 0x33

# ------------- Exception Class -----------------
class CardDispenserError(Exception):
    def __init__(self, response, message=""):
        head = response["head"]
        if head == STATUS_ERROR:
            error_code = response["e1"]+response["e0"]
            self.code = error_code.decode("utf-8")
        else:
            self.code = "FF"
        self.response = response
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        message = ERROR_MESSAGE.get(self.code, "Invalid ErrorCode ["+self.code+"]")
        return message


# ------------- Function Domain -----------------

def get_bcc(data):
    c = 0
    for x in range(0,len(data)):
        c = c ^ data[x]
    return c.to_bytes(1, byteorder='big')

def compose_message(ADDR, CM, PM, DATA):
    len_str = format((len(DATA) + 3), 'x' ).upper().zfill(4)
    len_str_byte = bytearray.fromhex(len_str)
    out_data = b"\xF2"+ADDR+len_str_byte+b"\x43"+CM+PM+DATA+b"\x03"
    out_data = out_data + get_bcc(out_data)

    LOG.cdlog("[FW]: CD DATA_OUT: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, out_data, show_log=DEBUG_MODE)

    return out_data

def decompose_message(data):
    response = {
        "head": "",
        "message": "Insufficent Return Data"
    }
    if len(data) <= 6:
        return response
    
    addr = data[1]
    data_size = int.from_bytes(data[2:4],'big')
    head = bytes([data[4]])
    response["head"] = head
    if head == STATUS_HEAD_OK:
        #Success
        response["CM"] = bytes([data[5]])
        response["PM"] = bytes([data[6]])
        response["st0"] = bytes([data[7]])
        response["st1"] = bytes([data[8]])
        response["st2"] = bytes([data[9]])
        response["data"] = data[10: (10 + (data_size-6))]
        response["message"] = "Success"

    elif head == STATUS_ERROR:
        #Failed
        response["CM"] = bytes([data[5]])
        response["PM"] = bytes([data[6]])
        response["e1"] = bytes([data[7]])
        response["e0"] = bytes([data[8]])
        response["data"] = data[9: (9 + (data_size-5))]
        response["message"] = "Failed"
    else:
        #Invalid
        response["message"] = "Invalid Head Message"
        response["data"] = data
    # if DEBUG_MODE:
    #     print("PARSED__:", response)
    return response

def read_data(ser=Serial()):
    data_in = ser.read_until(b"\xF2")
    # print("excess: ", data_in)
    data_in = read_data_rec(ser, b"\xF2")
    LOG.cdlog("[FW]: CD DATA__IN: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, data_in, show_log=DEBUG_MODE)
    return data_in

def read_data_rec(ser=Serial(), data_in=b""):
    data_in = data_in + ser.read_until(b"\x03")
    bcc = ser.read()
    c_bcc = get_bcc(data_in)
    data_in = data_in + bcc

    # print("bcc: ",bcc, ", c_bcc: ", c_bcc)
    # print("data_in: ", data_in)

    if bcc != c_bcc:
        data_in = read_data_rec(ser, data_in)
    
    return data_in

def send_and_receive(ser, ADDR, CM, PM, data):
    data_out = compose_message(ADDR, CM, PM, data)    
    ser.write(data_out)
    data_in = read_data(ser)
    result = decompose_message(data_in)
    ser.flushInput()
    ser.flushOutput()
    return result

def get_data_message(CM, PM, data):
    message = bytes(data.hex(),'utf-8') 
    if CM is CM_CARD_TYPE:
        if PM == b"\x30":
            message = IC_CARD_TYPE.get(data, b"Invalid DATA ["+ message +b"]")
        elif PM == b"\x31":
            message = b"Unimplemented Yet ["+ message +b"]"
        else:
            message = b"Invalid PM ["+ message +b"]"
    return message


def get_details_message(response):
    head = response["head"]
    message = ""
    if head == STATUS_HEAD_OK:
        #Success
        message = b"\r\n  [SUCCESS] " + CM_MESSAGE.get(response["CM"], b"Invalid CM ["+response["CM"]+b"]") + b"/ PM [" + response["PM"] + b"], RESULT: \r\n"
        message = message + b"    CardPosition[st0]: " + response["st0"] + b" - "+  ST0_MESSAGE.get(response["st0"], b"Invalid POS ["+response["st0"]+b"]") + b"\r\n"
        message = message + b"    StackerStatus[st1]: " + response["st1"] + b" - "+ ST1_MESSAGE.get(response["st1"], b"Invalid Status ["+response["st1"]+b"]") + b"\r\n"
        message = message + b"    RecylerBinStatus[st2]: " + response["st2"] + b" - "+ ST2_MESSAGE.get(response["st2"], b"Invalid Status ["+response["st2"]+b"]") + b"\r\n"
        message = message + b"    ResponseData: " + get_data_message(response["CM"], response["PM"], response["data"])

    elif head == STATUS_ERROR:
        #Failed
        error_code = response["e1"]+response["e0"]
        message = b"\r\n[ERROR] " + CM_MESSAGE.get(response["CM"], b"Invalid CM ["+response["CM"]+b"]") + b"/ PM [" + response["PM"] + b"], Message: "
        message = message + ERROR_MESSAGE.get( error_code, b"Invalid ErrorCode ["+error_code+b"]") + b"\r\n"
        message = message + b"ResponseData: " + response["data"] + b"\r\n"

    else:
        #Invalid
        message = b"\r\n[ERROR] " + CM_MESSAGE.get(response["CM"], b"Invalid CM ["+response["CM"]+b"]") + b"/" + response["PM"] + b", Message: Invalid Head Message \r\n"
    
    return message.decode("utf-8")

# ------------- COMMAND Domain -----------------

def do_check_error(response):
    head = response["head"]
    if head != STATUS_HEAD_OK:
        raise CardDispenserError(response, get_details_message(response))


def do_init(ser, ADDR, card_inside_move_card=False, move_to_errorbin=False, throw_error=True):
    #Initialize
    if card_inside_move_card:
        if move_to_errorbin:
            response = send_and_receive(ser, ADDR,CM_INITIALIZE,b"1",b"")
        else:
            response = send_and_receive(ser, ADDR,CM_INITIALIZE,b"0",b"")
    else:
        response = send_and_receive(ser, ADDR,CM_INITIALIZE,b"3",b"")

    if throw_error:
        do_check_error(response)

    return response


def do_check_status(ser, ADDR, sensor=False, throw_error=True):
    #Check Status
    if sensor is False:
        response = send_and_receive(ser, ADDR, CM_STATUS_REQUEST, b"0",b"")
    else:
        response = send_and_receive(ser, ADDR, CM_STATUS_REQUEST, b"1",b"")

    if throw_error:
        do_check_error(response)

    return response


def do_move_card(ser, ADDR, move_to, throw_error=True):
    #Move Card Out
    response = send_and_receive(ser, ADDR, CM_CARD_MOVE, move_to, b"")

    if throw_error:
        do_check_error(response)
        
    return response

def do_auto_check_card(ser, ADDR, rf_card=False, throw_error=True):
    if rf_card:
        response = send_and_receive(ser, ADDR, CM_CARD_TYPE, b"1", b"")
    else:
        response = send_and_receive(ser, ADDR, CM_CARD_TYPE, b"0", b"")

    if throw_error:
        do_check_error(response)

    return response

class CPUCard:
    def __init__(self):
        # self.tags = list(emv_tags.keys())
        # self.tlv = TLV(self.tags)
        self.tlv = TLV()

    def do_cold_reset(self, ser, ADDR, vcc=b"\x30", throw_error=True):
        response = send_and_receive(ser, ADDR, CM_CPUCARD_CONTROL, b"0", vcc)
        if throw_error:
            do_check_error(response)
        return response

    def do_deactivate(self, ser, ADDR, throw_error=True):
        response = send_and_receive(ser, ADDR, CM_CPUCARD_CONTROL, b"1", b"")
        if throw_error:
            do_check_error(response)
        return response

    def do_check_status(self, ser, ADDR, throw_error=True):
        response = send_and_receive(ser, ADDR, CM_CPUCARD_CONTROL, b"2", b"")
        if throw_error:
            do_check_error(response)
        return response

    def do_auto_send_apdu(self, ser, ADDR, APDU, throw_error=True):
        max_time = 10
        start_time = datetime.now()

        data_buffer = b""
        original_response = None

        while True:
            response = send_and_receive(ser, ADDR, CM_CPUCARD_CONTROL, b"9", APDU)
            if throw_error:
                do_check_error(response)

            if original_response is None:
                original_response = response

            data_in = response["data"]
            if len(data_in) >= 2:
                status = data_in[-2:]
                if status[0] != 0x61:
                    data_buffer = data_buffer + data_in
                    break
                else:
                    APDU = self.compose_get_response()
                    data_buffer = data_buffer + data_in[:-2]
                    sleep(2)

            cur_time = datetime.now()
            delta_time = cur_time - start_time
            if delta_time.seconds >= max_time:
                raise SystemError("99EE:Process Timeout")
        
        original_response["data"] = data_buffer
        
        return original_response
        
    def compose_select_apdu(self, AID):
        len_str = format(len(AID), 'x' ).upper().zfill(2)
        len_str_byte = bytearray.fromhex(len_str)
        data = b"\x00\xA4\x04\x00"+len_str_byte+AID+b"\x00"
        if DEBUG_MODE:
            print("compose_select_apdu: ", data.hex() )

        return data
    
    def compose_read_apdu(self, rec=0, sfi=0):
        data = b"\x00\xB2"+rec.to_bytes(1,"big") +((sfi<<3)|4).to_bytes(1,"big")+b"\x00"+b"\x00"
        if DEBUG_MODE:
            print("compose_read_apdu: ", data.hex() )

        return data

    def compose_get_response(self):
        data = b"\x00\xC0\x00\x00\x00\x00"
        return data
    
    def compose_get_data(self, tag="57"):
        tag = tag.zfill(4)
        tag_b = bytes.fromhex(tag)

        data = b"\x00\xCA"+tag_b+b"\x00"
        if DEBUG_MODE:
            print("compose_get_data: ", data.hex() )

        return data

    def do_select_AID(self, ser, ADDR, AID):
        is_success = False
        tlv = self.tlv
        try:
            while not is_success:
                data_out = self.compose_select_apdu(AID)
                response = self.do_auto_send_apdu(ser, ADDR, data_out)
                if DEBUG_MODE:
                    print(get_details_message(response))

                data_in = response["data"].hex().upper()
                if len(data_in) >= 4:
                    status = data_in[-4:]
                    if status == "9000":
                        if DEBUG_MODE:
                            print("AID_RESPONSE: ", data_in)
                        data_in = data_in[:-4]

                        parsed_data = tlv.parse(data_in)
                        dumper = tlv.dump(parsed_data)
                        if DEBUG_MODE:
                            print("AID_DUMP:\r\n", dumper)
                        tag6F = parsed_data.get('6F')

                        parsed_data = tlv.parse(tag6F)
                        dumper = tlv.dump(parsed_data)
                        if DEBUG_MODE:
                            print(dumper)
                        tagA5 = parsed_data.get('A5')
                        
                        parsed_data = tlv.parse(tagA5)
                        dumper = tlv.dump(parsed_data)
                        if DEBUG_MODE:
                            print(dumper)
                        tag9F38 = parsed_data.get("9F38")

                        if tag9F38:
                            #Do IAP
                            response = self.do_auto_send_apdu(ser, ADDR, bytes.fromhex("80A80000048302036000"))
                            data_in = response["data"].hex().upper()
                            if len(data_in) >= 4:
                                status = data_in[-4:]
                                if status == "9000":
                                    if DEBUG_MODE:
                                        print("IAP_RESPONSE: ", data_in)
                                    data_in = data_in[:-4]

                                    parsed_data = tlv.parse(data_in)
                                    dumper = tlv.dump(parsed_data)
                                    if DEBUG_MODE:
                                        print("IAP_DUMP:\r\n", dumper)
                                    tag77 = parsed_data.get('77')

                                    parsed_data = tlv.parse(tag77)
                                    dumper = tlv.dump(parsed_data)
                                    if DEBUG_MODE:
                                        print(dumper)

                        is_success = True
                    else:
                        if DEBUG_MODE:
                            print("AID_STATUS: ", status)
                        if status == "6A82":
                            break

        except Exception as ex:
            if DEBUG_MODE:
                print("do_select_AID",ex)

        return is_success
        
    def do_read_all_data(self, ser, ADDR):
        response_array = []
        for sfi in range(1, 31):
            for rec in range(1, 16):
                data_out = self.compose_read_apdu(rec, sfi)
                response = self.do_auto_send_apdu(ser, ADDR, data_out)
                response_array.append({ "index": str(rec)+"/"+str(sfi), "data":response["data"] })
        return response_array
    
    def do_find_tag_data(self, ser, ADDR, tag="57", attempt_to_read_records=False):
        found_tag = None
        try:

            data_out = self.compose_get_data(tag)
            response = self.do_auto_send_apdu(ser, ADDR, data_out)

            data_in = response["data"].hex()
            data_in = data_in.upper()
            status = data_in[-4:]
            # if DEBUG_MODE and status != "6985":
            if DEBUG_MODE:
                print(get_details_message(response))

            if status == "9000":
                found_tag = data_in[:-4]

            if attempt_to_read_records and found_tag is None:
                tlv = self.tlv
                for sfi in range(1, 31):
                    for rec in range(1, 16):
                        data_out = self.compose_read_apdu(rec, sfi)
                        response = self.do_auto_send_apdu(ser, ADDR, data_out)
                        

                        data_in = response["data"].hex()
                        data_in = data_in.upper()
                        status = data_in[-4:]
                        if DEBUG_MODE and status != "6985":
                            print(get_details_message(response))

                        if status != "6985":
                            if DEBUG_MODE:
                                print("find_tag: ", data_in)

                        if status == "9000":
                            try:
                                data_in = data_in[:-4]
                                parsed_data = tlv.parse(data_in)
                                tag70 = parsed_data.get('70')
                                # print(tag70)

                                parsed_data = tlv.parse(tag70)
                                # print(parsed_data)
                                found_tag = parsed_data.get(tag)
                                # print(tag57)
                                if found_tag:
                                    break

                            except Exception as ex:
                                if DEBUG_MODE:
                                    print(ex)
                    if found_tag:
                        break
        except Exception as ex:
            if DEBUG_MODE:
                print(ex)
        
        if DEBUG_MODE:
            print("Tag Found: ", found_tag)
        
        return found_tag

        # response_array.append({ "index": str(rec)+"/"+str(sfi), "data":response["data"] })
        # return response_array


# ----------- KYT DOMAIN -------------

def kyt_get_status(status):
    binar = bin(status)[2:].zfill(8)
    if DEBUG_MODE:
        print("KYT BIN_STATS:",binar)
    is_stack_empty = binar[7] == '1'
    is_card_on_sensor = binar[5] == '1'
    is_motor_failed = binar[3] == '1'
    is_cd_busy = binar[1] == '1'
    return is_stack_empty, is_card_on_sensor, is_motor_failed, is_cd_busy


