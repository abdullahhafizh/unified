__author__ = 'wahyudi@multidaya.id'

import traceback
import _MainCPrepaidLog as LOG
import _CardDispenserLib as cdLib

from time import sleep
from serial import Serial
from func_timeout import func_timeout, func_set_timeout, FunctionTimedOut
import traceback


DEBUG_MODE = True
BAUD_RATE = 38400
BAUD_RATE_KYT = 9600
BAUD_RATE_SYN = 9600

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
    ser = None
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
        if ser:
            if ser.isOpen():
                ser.close()

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


@func_set_timeout(10)
def simply_eject_syn_priv(port="COM10"):
    message = ""
    status = None
    ser = None
    response = None

    STX = b"\x02"
    ETX = b"\x03"
    ADDR = b"\x31\x35" #Default Position 15
    
    C_MOVE = b'\x46\x43\x34'
    C_DISPENSE = b'\x44\x43'
    C_STATUS = b'\x41\x50'
    C_BASIC_STATUS = b'\x52\x46'
    
    ACK = 0x06
    NAK = 0x15
    ENQ = b'\x05'
    
    # Command Hex Descriptions
    # DC 44 43 Move card to front without holding card 
    # CP 43 50 Capture card
    # RF 52 46 Basic check status 
    # AP 41 50 Advanced check status
    # RS 52 53 Reset Machine
    # FC 46 43 Move Card To Specific Position

    try:
        #Init
        LOG.cdlog("[SYN]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "INIT", show_log=DEBUG_MODE)
        com = Serial(port, baudrate=BAUD_RATE_SYN, timeout=10)

        # cmd = C_DISPENSE #Move Card at front with holding card
        cmd = C_BASIC_STATUS
        data_out = STX + ADDR + cmd + ETX
        data_out = data_out + cdLib.get_bcc(data_out)
        com.write(data_out)
        
        LOG.cdlog("[SYN]: CD WRITE :", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)

        data_in = b""
        retry = 5
        while retry > 0:
            data_in = data_in + com.read_all()
            if len(data_in) > 0:
                if data_in.__contains__(ACK):
                    LOG.cdlog("[SYN]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    # cmd = C_STATUS
                    cmd = ENQ
                    data_in = b""
                elif data_in.__contains__(NAK):
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
            status = "C_DISPENSE"
            message = "Maksimum Retry Reached"
            raise SystemError('MAXR:'+message)

        # Send Enquiry
        data_out = STX + cmd + ADDR + ETX
        data_out = data_out + cdLib.get_bcc(data_out)
        com.write(data_out)
        LOG.cdlog("[SYN]: CD WRITE ENQ :", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)

        data_in = b""
        retry = 5
        while retry > 0:
            data_in = data_in + com.read_all()
            if len(data_in) > 0:
                LOG.cdlog("[SYN]: CD READ ENQ :", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                retry = retry - 1
            if retry <= 0 :
                status = "C_STATUS"
                message = "Maksimum Retry Reached"
                raise SystemError('MAXR:'+message)


        #Get Status
        LOG.cdlog("[SYN]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "C_STATUS", show_log=DEBUG_MODE)
        data_out = STX + ADDR + cmd + ETX
        data_out = data_out + cdLib.get_bcc(data_out)
        com.write(data_out)
        
        LOG.cdlog("[SYN]: CD WRITE :", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_out, show_log=DEBUG_MODE)

        data_in = b""
        retry = 5
        while cmd == C_STATUS and retry > 0:
            data_in = data_in + com.read_all()
            if len(data_in) > 0:
                if data_in.__contains__(ACK):
                    end = data_in.find(ETX)
                    if len(data_in) > 3 and end != -1:
                        LOG.cdlog("[SYN]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                        stat = data_in[end-1]
                        is_stack_empty, is_card_on_sensor, is_motor_failed, is_cd_busy = cdLib.syn_get_status(stat)
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
                    else:
                        continue
                elif data_in.__contains__(NAK):
                    LOG.cdlog("[SYN]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
                    com.write(data_out)        
                    data_in = b""
                    retry = retry - 1
                else:
                    LOG.cdlog("[SYN]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
                    data_in = b""
                    sleep(0.5)
                    continue
        
        if retry <= 0 :
            status = "C_STATUS"
            message = "Maksimum Retry Reached"
            raise SystemError('MAXR:'+message)

        if is_stack_empty:
            status = ES_CARDS_EMPTY
            message = "Stack Empty"
            LOG.cdlog("[SYN]: CD ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message, show_log=DEBUG_MODE)
        elif is_cd_busy:
            status = ES_INTERNAL_ERROR
            message = "CD Busy"
            LOG.cdlog("[SYN]: CD ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message, show_log=DEBUG_MODE)
        # elif is_motor_failed:
        #     data_out = STX + C_ERROR_CLEAR + ETX
        #     data_out = data_out + cdLib.get_bcc(data_out)
        #     com.write(data_out)
        #     status = ES_INTERNAL_ERROR
        #     message = "Motor Failed"
        #     LOG.cdlog("[SYN]: CD ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, message, show_log=DEBUG_MODE)
        else:
            #Issued Card
            LOG.cdlog("[SYN]: CD STEP ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "ELSE", show_log=DEBUG_MODE)
            # data_out = STX + ADDR + cmd + ETX
            # data_out = data_out + cdLib.get_bcc(data_out)
            # com.write(data_out)

            # data_in = b""
            # retry = 5
            # while retry > 0:
            #     data_in = data_in + com.read_all()
            #     if len(data_in) > 0:
            #         if data_in.__contains__(ACK):
            #             LOG.cdlog("[SYN]: CD RESPONSE ACK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
            #             cmd = C_STATUS
            #         elif data_in.__contains__(NAK):
            #             LOG.cdlog("[SYN]: CD RESPONSE NAK ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
            #             com.write(data_out)        
            #             data_in = b""
            #             retry = retry - 1
            #         elif data_in.__contains__(CAN):
            #             LOG.cdlog("[SYN]: CD RESPONSE CAN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "", show_log=DEBUG_MODE)
            #             com.write(data_out)
            #             data_in = b""
            #             retry = retry - 1
            #         elif data_in.__contains__(0x83) or data_in.__contains__(0x87):
            #             data_in = b""
            #             sleep(0.5)
            #             continue
            #         else:
            #             LOG.cdlog("[SYN]: CD RESPONSE UNKNOWN ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, data_in, show_log=DEBUG_MODE)
            #             data_in = b""
            #             sleep(0.5)
            #             continue
            
            # TODO: Fix State
            status = "UNKNOWN"
            message = "Unknown State"
            raise SystemError('STOP:'+message)
            
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
        if ser:
            if ser.isOpen():
                ser.close()

    return status, message, response