__author__ = 'wahyudi@multidaya.id'

import traceback
from _mModule import _CPrepaidLog as LOG
from _mModule import _CardDispenserLib as cdLib

from time import sleep, time
from serial import Serial
from func_timeout import func_timeout, func_set_timeout, FunctionTimedOut
import sys


DEBUG_MODE = True
BAUD_RATE = 38400
BAUD_RATE_KYT = 9600
BAUD_RATE_SYN = 9600
BAUD_RATE_MTK = 9600

#ERROR STATUS
ES_NO_ERROR = "0000"
ES_UNKNOWN_ERROR = "ER01"
ES_TRACK2_NOT_FOUND = "ER02"
ES_CARDS_EMPTY = "ER03"
ES_ERRORBIN_FULL = "ER04"
ES_INTERNAL_ERROR = "FF"


def send_command(cmd, param):
    cdLib.LOG = LOG
    LOG.cdlog("LIB [{0}]: Param = ".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW, param)
    if DEBUG_MODE:
        cdLib.DEBUG_MODE = DEBUG_MODE

    __output_response__ = {
        "cmd": cmd,
        "param": param,
        "data": {},
        "message": "",
        "code": ""
    }
    
    try:
        LOG.cdlog("LIB [{0}]: Mulai".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW)

        if cmd == "SIMPLY_EJECT":
            simply_eject(param, __output_response__)
        elif cmd == "SIMPLY_EJECT_KYT":
            simply_eject_kyt(param, __output_response__)
        elif cmd == "SIMPLY_EJECT_SYN":
            simply_eject_syn(param, __output_response__)
        elif cmd == "SIMPLY_EJECT_MTK":
            simply_eject_mtk(param, __output_response__)
        elif cmd == "EJECT_READ_CARD":
            read_track2data_then_move_card(param, __output_response__)
        elif cmd == "FAST_EJECT":
            fast_eject(param, __output_response__)
        else:
            raise SystemError("99FF:Command ["+cmd+"] not Supported")

    except:
        trace = traceback.format_exc()
        formatted_lines = trace.splitlines()
        err_message = formatted_lines[-1]
        LOG.cdlog("LIB [{0}]: ERROR ".format(cmd), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_NO_FLOW, formatted_lines[-1])
        LOG.cdlog("LIB [{0}]: TRACE ".format(cmd), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_NO_FLOW, trace)

        __output_response__["code"] = err_message.split(':')[0] if ':' in err_message else 'EXCP'
        __output_response__["message"] = err_message
    finally:
        LOG.cdlog("LIB [{0}]: DONE\r\n".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW)

    return __output_response__

#111
def simply_eject(param, __output_response__):
    Param = param.split('|')

    if len(Param) == 2:
        CD_PORT = Param[0]
        CD_ADDR = Param[1]
    else:
        LOG.cdlog("[111]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("9900:Missing/Improper Parameters")

    LOG.cdlog("[111]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_PORT)
    LOG.cdlog("[111]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_ADDR)

    status, message, response = simply_eject_priv(CD_PORT, CD_ADDR)

    if status == ES_NO_ERROR:
        __output_response__["code"] = status
        __output_response__["data"] = {
            "st0": response["st0"].decode("utf-8"),
            "st1": response["st1"].decode("utf-8"),
            "st2": response["st2"].decode("utf-8")
        }

        desc = cdLib.get_details_message(response)

        LOG.cdlog("[111]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, desc)

        __output_response__["message"] = "Success"
        __output_response__["description"]  = desc
        LOG.cdlog("[111]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[111]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = status 
        __output_response__["message"] = message

        if response:
            desc = cdLib.get_details_message(response)
        else:
            desc = ""
        __output_response__["description"]  = desc

        LOG.cdlog("[111]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[111]: Gagal", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    return status

def simply_eject_priv(port="COM10", ADDR="00"):
    ADDR = bytes.fromhex(ADDR)

    message = ""
    status = None
    ser = None
    response = None

    try:
        #Init
        ser = Serial(port, baudrate=BAUD_RATE, timeout=10)
        response = func_timeout(3, func=cdLib.do_init, args=(ser, ADDR))
        LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

        #Check First Status
        response = cdLib.do_check_status(ser, ADDR)
        LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

        if response["st0"] == cdLib.CARD_POS_GATE:
            response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_GATE)
            LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
        
        if response["st1"] == cdLib.STACKER_EMPTY:
            if response["st0"] == cdLib.CARD_POS_NOCARD:
                status = ES_CARDS_EMPTY
                raise SystemError("991A:No Card in Card Dispenser")
            elif response["st0"] == cdLib.CARD_POS_GATE:
                raise SystemError("991B:Panic! Card in Gate but no Card in stacker. Help!")
        
        if response["st2"] == cdLib.ERRORBIN_FULL:
            status = ES_ERRORBIN_FULL
            raise SystemError("991C:ErrorBin Full please empty first before continue.")
        
        #Move To IC for smooth Transition
        if response["st0"] == cdLib.CARD_POS_NOCARD or response["st0"] == cdLib.CARD_POS_GATE:
            response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_IC)
            LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
        
        #Move Out / Eject with out release it from GATE
        if response["st0"] == cdLib.CARD_POS_RFIC:
            response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_HOLD)
            LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
            status = ES_NO_ERROR
        
        #Get Last Status
        response = cdLib.do_check_status(ser, ADDR)
        LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

    except cdLib.CardDispenserError as ex:        
        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format(ex, status, message, ex.message)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_INTERNAL_ERROR + ex.code
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    except Exception as ex:
        last_response = None
        if response:
            last_response = cdLib.get_details_message(response)

        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format(ex, status, message, last_response)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    except FunctionTimedOut as ex:
        last_response = None
        if response:
            last_response = cdLib.get_details_message(response)

        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format("INIT_GAGAL, CD Tidak Ada Response", status, message, last_response)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    finally:
        if ser:
            if ser.isOpen():
                ser.close()

    return status, message, response

#112
def read_track2data_then_move_card(param, __output_response__):
    Param = param.split('|')

    if len(Param) == 4:
        CD_PORT = Param[0]
        CD_ADDR = Param[1]
        CD_AID = Param[2]
        CD_RETRY_IF_TRACK2_NOT_FOUND = int(Param[3])
        if CD_RETRY_IF_TRACK2_NOT_FOUND == 0:
            CD_RETRY_IF_TRACK2_NOT_FOUND = 1
    else:
        LOG.cdlog("[112]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("9900:Missing/Improper Parameters")

    LOG.cdlog("[112]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_PORT)
    LOG.cdlog("[112]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_ADDR)
    LOG.cdlog("[112]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_AID)
    LOG.cdlog("[112]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_RETRY_IF_TRACK2_NOT_FOUND)

    ERRORBIN_COUNTER = 0
    while CD_RETRY_IF_TRACK2_NOT_FOUND > 0:
        status, message, track2data, response = read_track2data_then_move_card_priv(CD_PORT, CD_ADDR, CD_AID)
        CD_RETRY_IF_TRACK2_NOT_FOUND = CD_RETRY_IF_TRACK2_NOT_FOUND - 1
        if status == ES_NO_ERROR and track2data is not None:
            break
        elif status == ES_TRACK2_NOT_FOUND:
            #Counter Up if Track2NotFound or CardType Unimplemented
            ERRORBIN_COUNTER = ERRORBIN_COUNTER + 1
            LOG.cdlog("[112]: Message = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message)
            continue
        else:
            break

    ERRORBIN_COUNTER = str(ERRORBIN_COUNTER)
    if status == ES_NO_ERROR:
        cardnumber, expiry = split_track2_data(track2data)

        __output_response__["code"] = status
        __output_response__["data"] = {
            "card_no": cardnumber,
            "expirity": expiry,
            "error_bin": ERRORBIN_COUNTER,
            "st0": response["st0"].decode("utf-8"),
            "st1": response["st1"].decode("utf-8"),
            "st2": response["st2"].decode("utf-8")
        }

        LOG.cdlog("[112]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, cardnumber)
        LOG.cdlog("[112]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, expiry)
        LOG.cdlog("[112]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, ERRORBIN_COUNTER)
        LOG.cdlog("[112]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, cdLib.get_details_message(response))

        __output_response__["message"] = "Success"
        LOG.cdlog("[112]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[112]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["data"] = {
            "error_bin": ERRORBIN_COUNTER
        }
        __output_response__["code"] = status 
        __output_response__["message"] = message

        LOG.cdlog("[112]: Response = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, ERRORBIN_COUNTER)
        LOG.cdlog("[112]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[112]: Gagal", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    return status

def split_track2_data(track2=""):
    cardnumber = ""
    expiry = ""
    try:
        track2 = track2.upper()
        split_track = track2.split("D")

        if len(split_track) >= 2:
            cardnumber = split_track[0]
            expiry = split_track[1][:4]

    except Exception as ex:
        LOG.cdlog("split_track2_data: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, ex)

    return cardnumber, expiry

def read_track2data_then_move_card_priv(port="COM10", ADDR="00", AID="A0000006021010"):
    ADDR = bytes.fromhex(ADDR)
    AID = bytes.fromhex(AID)
    track2tag = "57"
    track2data = None
    message = ""
    status = None
    ser = None
    response = None

    try:
        #Init
        ser = Serial(port, baudrate=BAUD_RATE, timeout=10)
        response = cdLib.do_init(ser, ADDR)
        LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

        #Check First Status
        response = cdLib.do_check_status(ser, ADDR)
        LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
        
        if response["st1"] == cdLib.STACKER_EMPTY:
            if response["st0"] == cdLib.CARD_POS_NOCARD:
                status = ES_CARDS_EMPTY
                raise SystemError("992A:No Card in Card Dispenser")
            elif response["st0"] == cdLib.CARD_POS_GATE:
                raise SystemError("992B:Panic! Card in Gate but no Card in stacker. Help!")
        
        if response["st2"] == cdLib.ERRORBIN_FULL:
            status = ES_ERRORBIN_FULL
            raise SystemError("992C:ErrorBin Full please empty first before continue.")
        
        #Sequence to Read ICCard and Eject It
        if response["st0"] == cdLib.CARD_POS_NOCARD or response["st0"] == cdLib.CARD_POS_GATE:
            response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_IC)
            LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
        
        if response["st0"] == cdLib.CARD_POS_RFIC:
            response = cdLib.do_auto_check_card(ser, ADDR)
            LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

            if response["data"][0] == cdLib.CARD_TYPE_CPU:
                cpuCard = cdLib.CPUCard()
                response = cpuCard.do_check_status(ser, ADDR)
                LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

                if response["data"] == b"0":
                    response = cpuCard.do_cold_reset(ser, ADDR)
                    LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

                    try:
                        if cpuCard.do_select_AID(ser, ADDR, AID):
                            track2data = cpuCard.do_find_tag_data(ser, ADDR, track2tag, True)

                    except Exception as ex:
                        message =  "Failed GetTrack2: {0}".format(ex)
                                            
                response = cpuCard.do_deactivate(ser, ADDR)
                LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

            else:
                message = "Card Type Unimplemented Yet, "
            
            LOG.cdlog('Track2Data: ', LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, track2data, show_log=cdLib.DEBUG_MODE)

            if track2data:
                #Move Card to Hold if Track2 Exist
                response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_HOLD)
                LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
                message = "Success"
                status = ES_NO_ERROR
            else:
                #Move Card to Error if Track2 Not Exist
                response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_ERROR)
                LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
                message = message + "Track2 Data Not Found"
                status = ES_TRACK2_NOT_FOUND

        else:
            raise SystemError("992D:Invalid Card Position after CMD Move to IC")
        
        #Check Last Status
        response = cdLib.do_check_status(ser, ADDR)
        LOG.cdlog("[112]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
    
    except Exception as ex:
        last_response = None
        if response:
            last_response = cdLib.get_details_message(response)

        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format(ex, status, message, last_response)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    finally:
        if ser:
            if ser.isOpen():
                ser.close()

    return status, message, track2data, response

#113
def fast_eject(param, __output_response__):
    Param = param.split('|')

    if len(Param) == 2:
        CD_PORT = Param[0]
        CD_ADDR = Param[1]
    else:
        LOG.cdlog("[113]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("9900:Missing/Improper Parameters")

    LOG.cdlog("[113]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_PORT)
    LOG.cdlog("[113]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_ADDR)

    status, message, response = fast_eject_priv(CD_PORT, CD_ADDR)

    if status == ES_NO_ERROR:
        __output_response__["code"] = status
        __output_response__["data"] = {
            "st0": response["st0"].decode("utf-8"),
            "st1": response["st1"].decode("utf-8"),
            "st2": response["st2"].decode("utf-8")
        }
        LOG.cdlog("[113]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, cdLib.get_details_message(response))

        __output_response__["message"] = "Success"
        LOG.cdlog("[113]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[113]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = status 
        __output_response__["message"] = message

        LOG.cdlog("[113]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[113]: Gagal", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    return status

def fast_eject_priv(port="COM10", ADDR="00"):
    ADDR = bytes.fromhex(ADDR)

    message = ""
    status = None
    ser = None
    response = None

    try:
        #Init
        ser = Serial(port, baudrate=BAUD_RATE, timeout=10)
        response = cdLib.do_init(ser, ADDR)
        LOG.cdlog("[113]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

        #Check First Status
        response = cdLib.do_check_status(ser, ADDR)
        LOG.cdlog("[113]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)
        
        if response["st1"] == cdLib.STACKER_EMPTY:
            if response["st0"] == cdLib.CARD_POS_NOCARD:
                status = ES_CARDS_EMPTY
                raise SystemError("993B:No Card in Card Dispenser")
            elif response["st0"] == cdLib.CARD_POS_GATE:
                raise SystemError("993C:Panic! Card in Gate but no Card in stacker. Help!")
        
        if response["st2"] == cdLib.ERRORBIN_FULL:
            status = ES_ERRORBIN_FULL
            raise SystemError("993D:ErrorBin Full please empty first before continue.")

        # #Move Card To Hold
        # response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_HOLD)
        # LOG.cdlog("[113]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)        
    

        #Eject Card To Gate
        response = cdLib.do_move_card(ser, ADDR, cdLib.CARD_MOVE_TO_GATE)
        LOG.cdlog("[113]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

        status = ES_NO_ERROR
                
        #Get Last Status
        response = cdLib.do_check_status(ser, ADDR)
        LOG.cdlog("[111]: CD Response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cdLib.get_details_message(response), show_log=DEBUG_MODE)

    except cdLib.CardDispenserError as ex:        
        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format(ex, status, message, ex.message)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_INTERNAL_ERROR + ex.code
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    except Exception as ex:
        last_response = None
        if response:
            last_response = cdLib.get_details_message(response)

        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format(ex, status, message, last_response)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    finally:
        if ser:
            if ser.isOpen():
                ser.close()

    return status, message, response

def simply_eject_kyt(param, __output_response__):
    Param = param.split('|')

    if len(Param) >= 1:
        CD_PORT = Param[0]
    else:
        LOG.cdlog("[KYT]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("ERRO:Missing/Improper Parameters")

    LOG.cdlog("[KYT]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_PORT)

    status, message, response = simply_eject_kyt_priv(CD_PORT)

    if status == ES_NO_ERROR:
        __output_response__["code"] = status
        __output_response__["message"] = "Success"
        __output_response__["description"] = {
            "is_stack_empty": response["is_stack_empty"],
            "is_card_on_sensor": response["is_card_on_sensor"],
            "is_motor_failed": response["is_motor_failed"],
            "is_cd_busy": response["is_cd_busy"]
        }

        LOG.cdlog("[KYT]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, __output_response__)
        LOG.cdlog("[KYT]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[KYT]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = status 
        __output_response__["message"] = message
        __output_response__["description"] = ""
        
        if response:
            __output_response__["description"] = {
                "is_stack_empty": response["is_stack_empty"],
                "is_card_on_sensor": response["is_card_on_sensor"],
                "is_motor_failed": response["is_motor_failed"],
                "is_cd_busy": response["is_cd_busy"]
            }

        LOG.cdlog("[KYT]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[KYT]: Gagal", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    return status

@func_set_timeout(10)
def simply_eject_kyt_priv(port="COM10"):
    message = ""
    status = None
    com = None
    response = None

    STX = b"\x02"
    ETX = b"\x03"
    EOT = b"\x04"
    ENQ = b"\x05"
    ACK = 0x06
    NAK = 0x15
    CAN = 0x18

    C_ERROR_CLEAR = b'\x30'
    C_STATUS_REQUEST = b'\x31'
    C_ISSUE_CARD = b"\x40"
    C_ISSUE_LENGTH = b"\xF0"

    try:
        #Init
        LOG.cdlog("[KYT]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "INIT", show_log=DEBUG_MODE)
        com = Serial(port, baudrate=BAUD_RATE_KYT, timeout=10)

        cmd = C_ISSUE_LENGTH
        data_out = STX + cmd + ETX
        data_out = data_out + cdLib.get_bcc(data_out)
        com.write(data_out)

        data_in = b""
        retry = 5
        while cmd == C_ISSUE_LENGTH and retry > 0:
            data_in = data_in + com.read_all()
            if len(data_in) > 0:
                if data_in.__contains__(ACK):
                    LOG.cdlog("[KYT]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                    cmd = C_STATUS_REQUEST
                    data_in = b""
                elif data_in.__contains__(NAK):
                    LOG.cdlog("[KYT]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                    com.write(data_out)        
                    data_in = b""
                    retry = retry - 1
                elif data_in.__contains__(CAN):
                    LOG.cdlog("[KYT]: CD RESPONSE CAN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                    com.write(data_out)
                    data_in = b""
                    retry = retry - 1
                else:
                    LOG.cdlog("[KYT]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    data_in = b""
                    sleep(0.5)
                    continue
        if retry <= 0 :
            status = "C_ISSUE_LENGTH"
            message = "Maksimum Retry Reached"
            raise SystemError('MAXR:'+message)


        #Get Status
        LOG.cdlog("[KYT]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "C_STATUS_REQUEST", show_log=DEBUG_MODE)
        data_out = STX + cmd + ETX
        data_out = data_out + cdLib.get_bcc(data_out)
        com.write(data_out)

        data_in = b""
        retry = 5
        while cmd == C_STATUS_REQUEST and retry > 0:
            data_in = data_in + com.read_all()
            if len(data_in) > 0:
                if data_in.__contains__(ACK):
                    end = data_in.find(ETX)
                    if len(data_in) > 3 and end != -1:
                        LOG.cdlog("[KYT]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        stat = data_in[end-1]
                        is_stack_empty, is_card_on_sensor, is_motor_failed, is_cd_busy = cdLib.kyt_get_status(stat)
                        response = {
                            "is_stack_empty": is_stack_empty,
                            "is_card_on_sensor": is_card_on_sensor,
                            "is_motor_failed": is_motor_failed,
                            "is_cd_busy": is_cd_busy
                        }
                        com.write(b"\x06")
                        sleep(0.5)
                        if is_cd_busy:
                            data_in = b""
                            data_out = STX + cmd + ETX
                            data_out = data_out + cdLib.get_bcc(data_out)
                            com.write(data_out)
                        else:
                            data_in = b""
                            cmd = C_ISSUE_CARD
                    else:
                        continue
                elif data_in.__contains__(NAK):
                    LOG.cdlog("[KYT]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                    com.write(data_out)        
                    data_in = b""
                    retry = retry - 1
                elif data_in.__contains__(CAN):
                    LOG.cdlog("[KYT]: CD RESPONSE CAN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                    com.write(data_out)
                    data_in = b""
                    retry = retry - 1
                else:
                    LOG.cdlog("[KYT]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    data_in = b""
                    sleep(0.5)
                    continue
        
        if retry <= 0 :
            status = "C_STATUS_REQUEST"
            message = "Maksimum Retry Reached"
            raise SystemError('MAXR:'+message)

        if is_stack_empty:
            status = ES_CARDS_EMPTY
            message = "Stack Empty"
            LOG.cdlog("[KYT]: CD ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message, show_log=DEBUG_MODE)
        elif is_cd_busy:
            status = ES_INTERNAL_ERROR
            message = "CD Busy"
            LOG.cdlog("[KYT]: CD ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message, show_log=DEBUG_MODE)
        elif is_motor_failed:
            data_out = STX + C_ERROR_CLEAR + ETX
            data_out = data_out + cdLib.get_bcc(data_out)
            com.write(data_out)
            status = ES_INTERNAL_ERROR
            message = "Motor Failed"
            LOG.cdlog("[KYT]: CD ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message, show_log=DEBUG_MODE)
        else:
            #Issued Card
            LOG.cdlog("[KYT]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "C_ISSUE_CARD", show_log=DEBUG_MODE)
            data_out = STX + cmd + ETX
            data_out = data_out + cdLib.get_bcc(data_out)
            com.write(data_out)

            data_in = b""
            retry = 5
            while cmd == C_ISSUE_CARD and retry > 0:
                data_in = data_in + com.read_all()
                if len(data_in) > 0:
                    if data_in.__contains__(ACK):
                        LOG.cdlog("[KYT]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        cmd = C_STATUS_REQUEST
                    elif data_in.__contains__(NAK):
                        LOG.cdlog("[KYT]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        com.write(data_out)        
                        data_in = b""
                        retry = retry - 1
                    elif data_in.__contains__(CAN):
                        LOG.cdlog("[KYT]: CD RESPONSE CAN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        com.write(data_out)
                        data_in = b""
                        retry = retry - 1
                    elif data_in.__contains__(0x83) or data_in.__contains__(0x87):
                        data_in = b""
                        sleep(0.5)
                        continue
                    else:
                        LOG.cdlog("[KYT]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                        data_in = b""
                        sleep(0.5)
                        continue
            if retry <= 0 :
                status = "C_ISSUE_CARD"
                message = "Maksimum Retry Reached"
                raise SystemError('MAXR:'+message)
            
            #Get Last Status
            LOG.cdlog("[KYT]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "C_STATUS_REQUEST", show_log=DEBUG_MODE)
            data_out = STX + cmd + ETX
            data_out = data_out + cdLib.get_bcc(data_out)
            com.write(data_out)

            data_in = b""
            retry = 5
            while cmd == C_STATUS_REQUEST and retry > 0:
                data_in = data_in + com.read_all()
                
                if len(data_in) > 0:
                    if data_in.__contains__(ACK):
                        end = data_in.find(ETX)
                        if len(data_in) > 3 and end != -1:
                            LOG.cdlog("[KYT]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                            stat = data_in[end-1]
                            is_stack_empty, is_card_on_sensor, is_motor_failed, is_cd_busy = cdLib.kyt_get_status(stat)
                            response = {
                                "is_stack_empty": is_stack_empty,
                                "is_card_on_sensor": is_card_on_sensor,
                                "is_motor_failed": is_motor_failed,
                                "is_cd_busy": is_cd_busy
                            }
                            com.write(b"\x06")
                            sleep(0.5)
                            if is_cd_busy:
                                data_in = b""
                                data_out = STX + cmd + ETX
                                data_out = data_out + cdLib.get_bcc(data_out)
                                com.write(data_out)
                            else:
                                data_in = b""
                                cmd = C_ISSUE_CARD
                        else:
                            continue
                    elif data_in.__contains__(NAK):
                        LOG.cdlog("[KYT]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        com.write(data_out)        
                        data_in = b""
                        retry = retry - 1
                    elif data_in.__contains__(CAN):
                        LOG.cdlog("[KYT]: CD RESPONSE CAN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        com.write(data_out)
                        data_in = b""
                        retry = retry - 1
                    else:
                        LOG.cdlog("[KYT]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                        data_in = b""
                        sleep(0.5)
                        continue
            if retry <= 0 :
                status = "C_STATUS_REQUEST"
                message = "Maksimum Retry Reached For Last Status"
                raise SystemError('MAXR:'+message)

            status = ES_NO_ERROR
        
    except FunctionTimedOut as ex:
        last_response = None

        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format("INIT_GAGAL, CD Tidak Ada Response", status, message, last_response)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    except Exception as ex:
        last_response = None

        message = "Exception: {0}.\r\n  LastStatus: {1}, LastMessage: {2}, LastResponse: {3}".format(ex, status, message, last_response)
        if status != ES_CARDS_EMPTY or status != ES_ERRORBIN_FULL:
            status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    finally:
        if com:
            if com.isOpen():
                com.close()

    return status, message, response

def simply_eject_syn(param, __output_response__):
    Param = param.split('|')

    if len(Param) >= 1:
        CD_PORT = Param[0]
    else:
        LOG.cdlog("[SYN]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("ERRO:Missing/Improper Parameters")

    LOG.cdlog("[SYN]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_PORT)

    status, message, response = simply_eject_syn_priv(CD_PORT)

    if status == ES_NO_ERROR:
        __output_response__["code"] = status
        __output_response__["message"] = "Success"
        __output_response__["description"] = {
            "is_stack_empty": response["is_stack_empty"],
            "is_card_on_sensor": response["is_card_on_sensor"],
            "is_motor_failed": response["is_motor_failed"],
            "is_cd_busy": response["is_cd_busy"]
        }

        LOG.cdlog("[SYN]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, __output_response__)
        LOG.cdlog("[SYN]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[SYN]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = status 
        __output_response__["message"] = message
        __output_response__["description"] = ""
        
        if response:
            __output_response__["description"] = {
                "is_stack_empty": response["is_stack_empty"],
                "is_card_on_sensor": response["is_card_on_sensor"],
                "is_motor_failed": response["is_motor_failed"],
                "is_cd_busy": response["is_cd_busy"]
            }

        LOG.cdlog("[SYN]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[SYN]: Gagal", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    return status

def send_enq_syn(com, cmd):
    try:
        com.write(cmd)
        LOG.cdlog("[SYN]: CD SEND ENQ ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, cmd, show_log=DEBUG_MODE)
    except:
        pass


class SyncotekCD():
    SYN_STX = b"\x02"
    SYN_ETX = b"\x03"
    SYN_ADDR = b"\x31\x35" #Default Position 15
    SYN_DISABLE_CAPTURE = "IN".encode('ascii') + b'\x30'
        
    SYN_C_MOVE = 'FC'.encode('ascii') + b'\x30'
    SYN_C_DISPENSE = 'DC'.encode('ascii')
    SYN_C_STATUS = 'AP'.encode('ascii')
    SYN_C_BASIC_STATUS = 'RF'.encode('ascii')
    SYN_C_RESET = 'RS'.encode('ascii')
        
    SYN_ACK = 0x06
    SYN_NAK = 0x15
    SYN_ENQ = b'\x05' + SYN_ADDR
        
    # STAT CD
    SYN_DISPENSED = b"804" #Card Successfully Dispensed
    SYN_CARD_STILL_STACKED = b"003" #Card Successfully Dispensed
    SYN_CARD_DISPENSE_ERROR = b"120" #Card Successfully Dispensed
    
    SYN_DISPENSING = b"800" #Dispensing card 
    SYN_CAPTURING = b"400" #Capturing card 
    SYN_DISPENSE_ERROR = b"200" #Dispense error
    SYN_CAPTURE_ERROR = b"100" #Capture error

    SYN_GENERAL_ERROR = b"080"
    SYN_CARD_OVERLAP = b"040"
    SYN_CARD_JAMMED = b"020"
    SYN_CARD_STACK_WILL_EMPTY = b"010"
    SYN_CARD_NORMAL = b"000"

    SYN_STACK_EMPTY = b"008"
    SYN_SENSOR_3 = b"004"
    SYN_SENSOR_2 = b"002"
    SYN_SENSOR_1 = b"001"    
        
    # Command Hex Descriptions
    # DC 44 43 Move card to front without holding card 
    # CP 43 50 Capture card
    # RF 52 46 Basic check status 
    # AP 41 50 Advanced check status
    # RS 52 53 Reset Machine
    # FC 46 43 Move Card To Specific Position
    def __init__(self, com:Serial,) -> None:
        self.com = com

    def basic_status_syn(self, com):
        cmd = self.SYN_C_BASIC_STATUS
        data_out = self.SYN_STX + self.SYN_ADDR + cmd + self.SYN_ETX
        data_out = data_out + cdLib.get_bcc(data_out)
        self.com.write(data_out)
                
        LOG.cdlog("[SYN]: CD SEND RF ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)

        data_in = b""
        retry = 5
        while True:
            if retry == 0: break
            data_in = data_in + self.com.read_all()
            if len(data_in) > 0:
                if data_in.__contains__(self.SYN_ACK):
                    LOG.cdlog("[SYN]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    # Send Enquiry
                    self.com.write(self.SYN_ENQ)
                    LOG.cdlog("[SYN]: CD SEND ENQ ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, self.SYN_ENQ, show_log=DEBUG_MODE)
                    break
                elif data_in.__contains__(self.SYN_NAK):
                    LOG.cdlog("[SYN]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    self.com.write(data_out)        
                    data_in = b""
                    retry = retry - 1
                else:
                    LOG.cdlog("[SYN]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    data_in = b""
                    retry = retry - 1
                    sleep(0.5)
                    continue
                    
        if retry <= 0 :
            message = "Maksimum Retry Reached [C_BASIC_STATUS]"
            raise SystemError('MAXR:'+message)
        
        data_in = b""
        retry = 5
        stat = None
        
        while True:
            if retry == 0: break
            data_in = data_in + self.com.read_all()
            if len(data_in) > 0:
                if data_in.__contains__(self.SYN_ETX):
                    LOG.cdlog("[SYN]: CD RESPONSE ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    message = "Normal State"
                    stat = data_in.split(b'SF')[1][:3]
                    LOG.cdlog("[SYN]: CD STAT ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, stat.decode('utf-8'), show_log=DEBUG_MODE)
                    break
                else:
                    retry = retry - 1
                    sleep(0.5)
                    continue
        
        if retry <= 0 :
            message = "Maksimum Retry Reached"
            raise SystemError('MAXR:'+message)
        
        return stat

    def set_disable_capture(self, com):
        try:
            cmd = self.SYN_DISABLE_CAPTURE
            data_out = self.SYN_STX + self.SYN_ADDR + cmd + self.SYN_ETX
            data_out = data_out + cdLib.get_bcc(data_out)
            self.com.write(data_out)
            LOG.cdlog("[SYN]: CD SEND DISABLE CAPTURE ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)
            sleep(.5)
            self.com.write(self.SYN_ENQ)
            LOG.cdlog("[SYN]: CD SEND ENQ ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, self.SYN_ENQ, show_log=DEBUG_MODE)
        except:
            pass


@func_set_timeout(30)
def simply_eject_syn_priv(port="COM10"):
    message = "General Error"
    status = ES_UNKNOWN_ERROR
    com = None
    response = {
        "is_stack_empty": True,
        "is_card_on_sensor": True,
        "is_motor_failed": True,
        "is_cd_busy": True
    }
    
    stat = None

    try:

        LOG.cdlog("[SYN]: CD INIT ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, port, show_log=DEBUG_MODE)
        com = Serial(port, baudrate=BAUD_RATE_SYN, timeout=10)
        selectedCD = SyncotekCD(com)
        stat = selectedCD.basic_status_syn(com)
        
        # Add New Handle If Card Is Empty
        if stat == selectedCD.SYN_STACK_EMPTY:
            status = ES_CARDS_EMPTY
            message = "Empty Card"
            if com:
                if com.isOpen(): com.close()
            return status, message, response 
        
        # Experimental Below (Detected Capture Error)
        # while stat in [SYN_SENSOR_1, SYN_SENSOR_2, SYN_SENSOR_3]:
        #     # set_disable_capture(com)
        #     sleep(.5)
        #     stat = basic_status_syn(com)
            
        # if stat == SYN_CARD_DISPENSE_ERROR or stat[1] == b'1':
        #     # set_disable_capture(com)
        #     # cmd = SYN_C_RESET
        #     # data_out = SYN_STX + SYN_ADDR + cmd + SYN_ETX
        #     # data_out = data_out + cdLib.get_bcc(data_out)
        #     # com.write(data_out)
        #     # LOG.cdlog("[SYN]: CD SEND RS ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)        
        #     sleep(.5)
        #     stat = basic_status_syn(com)
        
        # if stat == SYN_CARD_STILL_STACKED:
        #     cmd = SYN_C_MOVE
        #     data_out = SYN_STX + SYN_ADDR + cmd + SYN_ETX
        #     data_out = data_out + cdLib.get_bcc(data_out)
        #     com.write(data_out)
        #     LOG.cdlog("[SYN]: CD SEND FC ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)
        #     sleep(.5)
        #     com.write(SYN_ENQ)
        #     LOG.cdlog("[SYN]: CD SEND ENQ ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, SYN_ENQ, show_log=DEBUG_MODE)
        #     sleep(.5)
        #     stat = basic_status_syn(com)
    
        # if stat in [SYN_CARD_NORMAL, SYN_CARD_STACK_WILL_EMPTY]:
        if stat is not None:
            # Do Dispense/Move
            # cmd = SYN_C_DISPENSE
            cmd = selectedCD.SYN_C_MOVE
            data_out = selectedCD.SYN_STX + selectedCD.SYN_ADDR + cmd + selectedCD.SYN_ETX
            data_out = data_out + cdLib.get_bcc(data_out)
            com.write(data_out)
            
            LOG.cdlog("[SYN]: CD SEND FC ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)
            data_in = b""
            retry = 5
            while True:
                if retry == 0: break
                data_in = data_in + com.read_all()
                if len(data_in) > 0:
                    if data_in.__contains__(selectedCD.SYN_ACK):
                        LOG.cdlog("[SYN]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                        # Send Enquiry
                        com.write(selectedCD.SYN_ENQ)
                        LOG.cdlog("[SYN]: CD SEND ENQ ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, selectedCD.SYN_ENQ, show_log=DEBUG_MODE)
                        break
                    elif data_in.__contains__(selectedCD.SYN_NAK):
                        LOG.cdlog("[SYN]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                        com.write(data_out)        
                        data_in = b""
                        retry = retry - 1
                    else:
                        LOG.cdlog("[SYN]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                        data_in = b""
                        sleep(0.5)
                        continue
                    
            if retry <= 0 :
                status = "SYN_C_MOVE"
                message = "Maksimum Retry Reached [SYN_C_MOVE]"
                raise SystemError('MAXR:'+message)
            
            retry = 5
            while True:
                sleep(1) 
                stat = selectedCD.basic_status_syn(com)
                retry = retry - 1
                response = {
                    "is_stack_empty": stat == selectedCD.SYN_STACK_EMPTY,
                    "is_card_on_sensor": stat in [selectedCD.SYN_SENSOR_1, selectedCD.SYN_SENSOR_2, selectedCD.SYN_SENSOR_3, selectedCD.SYN_CARD_STILL_STACKED],
                    "is_motor_failed": stat in [selectedCD.SYN_DISPENSE_ERROR, selectedCD.SYN_CAPTURE_ERROR, selectedCD.SYN_CARD_JAMMED, selectedCD.SYN_CARD_OVERLAP, selectedCD.SYN_GENERAL_ERROR],
                    "is_cd_busy": stat in [selectedCD.SYN_DISPENSING, selectedCD.SYN_CAPTURING]
                }
                if stat in [selectedCD.SYN_CARD_NORMAL, selectedCD.SYN_CARD_STACK_WILL_EMPTY]:
                    status = ES_NO_ERROR
                    message = 'Success'
                    break
                elif stat in [selectedCD.SYN_DISPENSE_ERROR, selectedCD.SYN_CAPTURE_ERROR, selectedCD.SYN_CARD_JAMMED, selectedCD.SYN_CARD_OVERLAP, selectedCD.SYN_GENERAL_ERROR]:
                    status = ES_INTERNAL_ERROR
                elif stat in [selectedCD.SYN_SENSOR_1, selectedCD.SYN_SENSOR_2, selectedCD.SYN_SENSOR_3]:
                #     set_disable_capture(com)
                # Force OK Status By Timer If Card Detected on Sensor
                    if retry == 1:
                        status = ES_NO_ERROR
                        message = 'Success'
                        break
                    else:
                        continue
                # Disable This Stack Empty
                # elif stat == SYN_STACK_EMPTY:
                #     status = ES_CARDS_EMPTY
                else:
                    if retry == 1:
                    # if retry == 1 and stat in [SYN_CARD_STILL_STACKED, SYN_CARD_STACK_WILL_EMPTY]:
                        # cmd = SYN_C_MOVE
                        # data_out = SYN_STX + SYN_ADDR + cmd + SYN_ETX
                        # data_out = data_out + cdLib.get_bcc(data_out)
                        # com.write(data_out)
                        # LOG.cdlog("[SYN]: CD SEND FC ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)
                        # sleep(.5)
                        # com.write(SYN_ENQ)
                        # LOG.cdlog("[SYN]: CD SEND ENQ ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, SYN_ENQ, show_log=DEBUG_MODE)
                        status = ES_NO_ERROR
                        message = 'Success'
                        break
                    else:
                        continue
                    # Experimental Below (Detected Capture Error)
                    # elif stat[1] == b'1':
                    #     set_disable_capture(com)
                    #     status = ES_INTERNAL_ERROR
                    # else:
                    #     # Add Reset At Error
                    #     status = ES_UNKNOWN_ERROR
            
            # if retry <= 0 :
            #     status = "SYN_C_MOVE"
            #     message = "Maksimum Retry Reached [SYN_C_MOVE]"
            #     raise SystemError('MAXR:'+message)
        
    except FunctionTimedOut as ex:
        message = "Exception: FunctionTimedOut"
        status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    except Exception as ex:
        message = "Exception: General"
        status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(str(ex), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    finally:
        if com:
            if com.isOpen():
                com.close()

    return status, message, response


def simply_eject_mtk(param, __output_response__):
    Param = param.split('|')

    if len(Param) >= 1:
        CD_PORT = Param[0]
    else:
        LOG.cdlog("[MTK]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("ERRO:Missing/Improper Parameters")

    LOG.cdlog("[MTK]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, CD_PORT)

    status, message, response = __simply_eject_mtk(CD_PORT)

    if status == ES_NO_ERROR:
        __output_response__["code"] = status
        __output_response__["message"] = "Success"
        __output_response__["description"] = {
            "is_stack_empty": response["is_stack_empty"],
            "is_card_on_sensor": response["is_card_on_sensor"],
            "is_motor_failed": response["is_motor_failed"],
            "is_cd_busy": response["is_cd_busy"]
        }

        LOG.cdlog("[MTK]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, __output_response__)
        LOG.cdlog("[MTK]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[MTK]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = status 
        __output_response__["message"] = message
        __output_response__["description"] = ""
        
        if response:
            __output_response__["description"] = {
                "is_stack_empty": response["is_stack_empty"],
                "is_card_on_sensor": response["is_card_on_sensor"],
                "is_motor_failed": response["is_motor_failed"],
                "is_cd_busy": response["is_cd_busy"]
            }

        LOG.cdlog("[MTK]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, status)
        LOG.cdlog("[MTK]: Gagal", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
    
    return status


class MutekCD():
    MTK_STX = b"\xF2"
    MTX_ETX = b"\x03"
    MTK_ADDR = b"\x00"
    MTK_CMT = b"\x43"
    ST0 = { b'0': 'No Card in Card Channel', b'1': 'Card Held at Gate', b'2': 'Card on RF/IC Position' }
    ST1 = { b'0': 'No Card in Hopper', b'1': 'Not Enough Card in Hopper', b'2': 'Enough Cards in Hopper' }
    ST2 = { b'0': 'Error card bin not full', b'1': 'Error card bin full' }

    def __init__(self, com:Serial,) -> None:
        self.com = com

    def encaps_request(self, cm:bytes, pm:bytes, data:bytes):
        if len(data)>512:
            raise Exception("LENGTH TO LONG")
        
        r_data = self.MTK_STX + self.MTK_ADDR
        i_data = self.MTK_CMT + cm + pm + data
        len_data = len(i_data).to_bytes(2, 'big')

        f_data = r_data + len_data + i_data + self.MTX_ETX

        return f_data+self.xor(f_data)
    
    def xor(self, data:bytes):
        bcc = data[0]
        # print(bcc.to_bytes(1,'big').hex(),data[0].to_bytes(1,'big').hex())
        for x in data[1:]:
            bcc ^= x
            # print(bcc.to_bytes(1,'big').hex(),x.to_bytes(1,'big').hex())
        return bcc.to_bytes(1, "big")
        
    def send_command(self, data:bytes, timeout_ms:int):
        LOG.cdlog("[MTK]: CD SEND ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data.hex().upper(), show_log=DEBUG_MODE)
        self.com.write(data)
        r_data = b""
        st_time = round(time() * 1000)
        nt_time = st_time
        while True:
            d = self.com.read(1)
            if d == b"\x06":
                LOG.cdlog("[MTK]: CD RECV ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                # ACK, next wait for response
                head = self.com.read_until(self.MTK_STX)
                head += self.com.read(3)
                len_data = int.from_bytes(head[2:4], 'big') + 2
                in_data = self.com.read(len_data)
                LOG.cdlog("[MTK]: CD RECV "+str(len_data)+" ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, (head+in_data).hex().upper(), show_log=DEBUG_MODE)
                while len(in_data) < len_data:
                    in_data += self.read()

                LOG.cdlog("[MTK]: CD SEND ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                self.com.write(b'\x06')
                r_data = head+in_data
                break
            elif d == b"\x15":
                # NAK, resend command
                LOG.cdlog("[MTK]: CD RECV NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                self.com.write(data)
            elif ((time()*1000) - nt_time) > 300:
                # timeout no response > 300ms
                LOG.cdlog("[MTK]: CD RECV TIMEOUT, RESEND ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                nt_time = time()*1000
                self.com.write(data)
            elif ((time()*1000) - st_time ) > timeout_ms:
                LOG.cdlog("[MTK]: CD TIMEOUT ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                raise Exception("CD TIMEOUT")
        
        return r_data
    
    def parse_error(self, e1:bytes, e0:bytes):
        ec = e1+e0
        if ec == b"00":
            return "Undefined Command"
        elif ec == b"01":
            return "Command Parameter Error"
        elif ec == b"02":
            return "Command Sequence Error"
        elif ec == b"03":
            return "Unsupported Command"
        elif ec == b"04":
            return "Command Data Error"
        elif ec == b"05":
            return "ICC Card Contact Not Released"
        elif ec == b"10":
            return "Card Jam"
        elif ec == b"12":
            return "Sensor Error"
        elif ec == b"13":
            return "Too Long Card"
        elif ec == b"14":
            return "Too Short Card"
        elif ec == b"40":
            return "Card Removed accidentally when recycling"
        elif ec == b"41":
            return "Electro-Magnet Error of ICC Module"
        elif ec == b"43":
            return "Unable to Move Card to IC Card Position"
        elif ec == b"45":
            return "Card Moved Manually (to a non-standard position)"
        elif ec == b"50":
            return "Overflow of Error Card Counter"
        elif ec == b"51":
            return "Motor error"
        elif ec == b"60":
            return "Short Circuit of IC Card Supply Power"
        elif ec == b"61":
            return "Fail to Activate IC Card"
        elif ec == b"62":
            return "Command Not Supported by the IC Card"
        elif ec == b"65":
            return "IC Card not activated"
        elif ec == b"66":
            return "IC Card don’t support command"
        elif ec == b"67":
            return "IC Card Data transmission Error"
        elif ec == b"68":
            return "IC Card Data transmission Overtime"
        elif ec == b"69":
            return "CPU/SAM APDU not complying to EMV"
        elif ec == b"A0":
            return "No Card Inside hopper"
        elif ec == b"A1":
            return "Error Card Bin is full"
        elif ec == b"B0":
            return "Fail to Reset/Initialize"
        else:
            return "ERROR {} - UNKNOWN".format(ec.decode(errors='ignore'))
        
    def parse_error_to_response(self, e1:bytes, e0:bytes):
        response = {
            "is_stack_empty": False,
            "is_card_on_sensor": False,
            "is_motor_failed": False,
            "is_cd_busy": False
        }

        ec = e1+e0

        if ec == b'A0':
            response["is_stack_empty"] = True
        elif ec in [ b'A1', b'43', b'45', b'50', b'51', b'41', b'40', b'10']:
            response["is_motor_failed"] = True

        return response

    def parse_status(self, response:dict, old_response:dict):
        old_response['is_stack_empty'] = response['st1'] == b'0'
        old_response['is_card_on_sensor'] = response['st0'] != b'0'
        return old_response

    def decaps_response(self, data:bytes):
        len_data = int.from_bytes(data[2:4], 'big')
        if len(data) != len_data+6:
            raise Exception("INVALID LENGTH; Real {} vs Expected {}".format(len(data), len_data+6))
        etx = data[4+len_data]
        if etx != 0x03:
            raise Exception("INVALID ETX Expected 3 vs {}".format(etx))
        bcc = data[5+len_data].to_bytes(1, 'big')
        c_bcc = self.xor(data[:(5+len_data)])
        if bcc != c_bcc:
            raise Exception("BCC NOT MATCH {} vs CALCULATED {}".format(bcc, c_bcc))
        
        mt = data[4].to_bytes(1, 'big')
        cm = data[5].to_bytes(1, 'big')
        pm = data[6].to_bytes(1, 'big')
        
        if mt == b'P':
            st0 = data[7].to_bytes(1, 'big')
            st1 = data[8].to_bytes(1, 'big')
            st2 = data[9].to_bytes(1, 'big')
            r_data = data[10:10+len_data-6]
            result = {
                "mt": mt,
                "cm": cm,
                "pm": pm,
                "st0": st0,
                "st0_message": self.ST0.get(st0, "UNKNOWN"),
                "st1": st1,
                "st1_message": self.ST1.get(st1, "UNKNOWN"),
                "st2": st2,
                "st2_message": self.ST2.get(st2, "UNKNOWN"),
                "data": r_data
            }
            LOG.cdlog("[MTK]: CD RESPONSE ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, result, show_log=DEBUG_MODE)
            return result
        elif mt == b'N' :
            e1 = data[7].to_bytes(1, 'big')
            e0 = data[8].to_bytes(1, 'big')
            r_data = data[9:9+len_data-5]
            result =  {
                "mt": mt,
                "cm": cm,
                "pm": pm,
                "e1": e1,
                "e0": e0,
                "error_message": self.parse_error(e1, e0),
                "error_response": self.parse_error_to_response(e1, e0),
                "data": r_data
            }
            LOG.cdlog("[MTK]: CD RESPONSE ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, result, show_log=DEBUG_MODE)
            return result
        else:
            raise Exception("INVALID MESSAGE HEADER (MT)")
        
    def init_device(self):
        # CM -> 30H

        # PM
        # 30H: Move and Hold the card at gate;
        # 31H: Capture Card to Error Card Bin;
        # 33H: No Movement, Retain the Card Inside; 
        # 34H: As 30H, and Error Card Counter increment; 
        # 35H: As 31H, and Error Card Counter increment; 
        # 37H: As 33H, and Error Card Counter increment;

        # Init and do nothing if card in channel
        LOG.cdlog("[MTK]: CD REQUEST INIT_DEVICE ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
        cmd = self.encaps_request(b'\x30', b'\x33', b'')
        byte_response = self.send_command(cmd, 10000)
        return self.decaps_response(byte_response)

    def inquire_status(self):
        # CM -> 31H

        # PM
        # Pm=30H: Report current card status with st0, st1, st2.
        # Pm=31H: Report Sensor Status with 10 bytes of data. (Usually used for Debugging and Maintenance)

        # Inquiry status of standard sensor
        LOG.cdlog("[MTK]: CD REQUEST INQUIRY_STATUS ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
        cmd = self.encaps_request(b'\x31', b'\x30', b'')
        byte_response = self.send_command(cmd, 10000)
        return self.decaps_response(byte_response)

    MOVE_TO_GATE = b'0'
    MOVE_TO_IC = b'1'
    MOVE_TO_RF = b'2'
    MOVE_TO_ERROR = b'3'
    MOVE_TO_OUT = b'9'

    def move_card(self, pm:bytes):
        # CM -> 32H

        # PM
        # Pm=30H: Move and hold card at gate position; 
        # Pm=31H: Move card to contact IC position; 
        # Pm=32H: Move card to RF Antenna Position; 
        # Pm=33H: Capture Card to Error Card Bin (Recycle Box); 
        # Pm=39H: Eject Card out of Machine;

        # Inquiry status of standard sensor
        LOG.cdlog("[MTK]: CD REQUEST MOVE_CARD ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, pm, show_log=DEBUG_MODE)
        cmd = self.encaps_request(b'\x32', pm, b'')
        byte_response = self.send_command(cmd, 10000)
        return self.decaps_response(byte_response)


@func_set_timeout(30)
def __simply_eject_mtk(port="COM10"):
##    global INIT_MTK
    message = "General Error"
    status = ES_UNKNOWN_ERROR
    com = None
    response = {
        "is_stack_empty": False,
        "is_card_on_sensor": False,
        "is_motor_failed": False,
        "is_cd_busy": False
    }
    
    try:

        LOG.cdlog("[MTK]: CD INIT ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, port, show_log=DEBUG_MODE)
        com = Serial(port, baudrate=BAUD_RATE_MTK, timeout=10)
        selectedCD = MutekCD(com)

##        if not INIT_MTK:
##            result = mtk.init_device()
##            if result["mt"] == b'N':
##                com.close()
##                return ES_INTERNAL_ERROR, result['error_message'], result['error_response']
##            else:
##                response = mtk.parse_status(result, response)
##                INIT_MTK = True
##        else:
##            result = mtk.inquire_status()
##            if result["mt"] == b'N':
##                com.close()
##                return ES_INTERNAL_ERROR, result['error_message'], result['error_response']
##            else:
##                response = mtk.parse_status(result, response)

        result = selectedCD.init_device()
        if result["mt"] == b'N':
            com.close()
            return ES_INTERNAL_ERROR, result['error_message'], result['error_response']
        else:
            response = selectedCD.parse_status(result, response)

        if result['st1'] == b'0':
            com.close()
            return ES_CARDS_EMPTY, "No Card Inside hopper", response
        elif result['st0'] == b'0':
            #No card in channel MOVE to bezel(IC/RF) first, if not will error 'Command Sequence Error'
            result = selectedCD.move_card(selectedCD.MOVE_TO_RF)
            if result["mt"] == b"N":
                com.close()
                return ES_INTERNAL_ERROR, result['error_message'], result['error_response']
            else:
                #print("SLEEP")
                #sleep(4)
                result = selectedCD.move_card(selectedCD.MOVE_TO_GATE)            
                if result["mt"] == b"N":
                    com.close()
                    return ES_INTERNAL_ERROR, result['error_message'], result['error_response']
                else:
                    status = ES_NO_ERROR
                    message = "SUCCESS"
                    response = selectedCD.parse_status(result, response)
        elif result['st0'] == b'1':
            #Card already out and held at gate, customer can get it.
            status = ES_INTERNAL_ERROR
            message = "Card on Sensor Gate"
            response = selectedCD.parse_status(result, response)
        elif result['st0'] == b'2':
            #Card already out or held at sensor RF, customer can get it or cannot.
            status = ES_INTERNAL_ERROR
            message = "Card on Sensor RF/IC"
            response = selectedCD.parse_status(result, response) 
            

## USE THIS IF EJECT is drop card out of machine
##        result = mtk.move_card(mtk.MOVE_TO_OUT)            
##        if result["mt"] == b"N":
##            com.close()
##            return ES_INTERNAL_ERROR, mtk.parse_error(result['e1'], result['e0']), mtk.parse_error_to_response(result['e1'], result['e0'])
##        else:
##            status = ES_NO_ERROR
##            message = "SUCCESS"
##            response = mtk.parse_status(result, response)
        
        
    except FunctionTimedOut as ex:
        message = "Exception: FunctionTimedOut"
        status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    except Exception as ex:
        message = "Exception: General"
        status = ES_UNKNOWN_ERROR
    
        LOG.cdlog(str(ex), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        LOG.cdlog(message, LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)

    finally:
        if com:
            if com.isOpen():
                com.close()

    return status, message, response
