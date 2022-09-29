__author__ = 'wahyudi@multidaya.id'

import traceback
from _mModule import _CPrepaidLog as LOG
from _dDevice import _MeiSCR as _MeiJava

MEI = None

def send_command(cmd, param):
    LOG.bvlog("LIB [{0}]: Param = ".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW, param)

    __output_response__ = {
        "cmd": cmd,
        "param": param,
        "data": {},
        "message": "",
        "code": ""
    }
    
    try:
        LOG.bvlog("LIB [{0}]: Mulai".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW)

        if cmd == "INIT_BILL":
            doInit(param, __output_response__)
        elif cmd == "START_RECEIVE_BILL":
            doStartDeposit(param, __output_response__)
        elif cmd == "STOP_RECEIVE_BILL":
            doCancelDeposit(param, __output_response__)
        elif cmd == "GET_STATUS_BILL":
            doGetStatus(param, __output_response__)
        elif cmd == "STORE_NOTES_BILL":
            doAcceptNote(param, __output_response__)
        elif cmd == "REJECT_NOTES_BILL":
            doCancelNote(param, __output_response__)
        else:
            raise SystemError("99FF:Command ["+cmd+"] not Supported")

    except:
        trace = traceback.format_exc()
        formatted_lines = trace.splitlines()
        err_message = formatted_lines[-1]
        LOG.bvlog("LIB [{0}]: ERROR ".format(cmd), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_NO_FLOW, formatted_lines[-1])
        LOG.bvlog("LIB [{0}]: TRACE ".format(cmd), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_NO_FLOW, trace)

        __output_response__["code"] = err_message.split(':')[0] if ':' in err_message else 'EXCP'
        __output_response__["message"] = "General Error"
    finally:
        LOG.bvlog("LIB [{0}]: DONE\r\n".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW)

    return __output_response__

#501
def doInit(param, __output_response__):
    global MEI

    Param = param.split('|')

    if len(Param) == 1:
        MEI_PORT = Param[0]
        enableRecyler = False
        enableRecylerDenom = []
    elif len(Param) == 2:
        MEI_PORT = Param[0]
        denomList = Param[1].split(",")
        enableRecyler = len(denomList) > 1
        enableRecylerDenom = []
        for i in denomList:
            enableRecylerDenom.append(int(i))
    else:
        LOG.bvlog("[501]: Missing/Improper Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        LOG.bvlog("[501]: Example Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, "MEI_PORTS_PATH|RECYLER_DENOM -> /dev/ttyS1|1,2 or /dev/ttyS1| or just /dev/ttyS1")
        LOG.bvlog("[501]: Example Parameters: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, "IF RECYLER_DENOM not exist or not valid, it will use default with Recyler Disabled")
        raise SystemError("9900:Missing/Improper Parameters")

    LOG.bvlog("[501]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, MEI_PORT)

    if MEI is None:
        MEI = _MeiJava.MeiDevice()

    isNormal, returnMessage, messsage = MEI.open(MEI_PORT, enableRecyler, enableRecylerDenom)

    if isNormal:
        __output_response__["code"] = "0000"
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = "Success"

        LOG.bvlog("[501]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[501]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.bvlog("[501]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = "9501" 
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = messsage

        LOG.bvlog("[501]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[501]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.bvlog("[501]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, messsage)
    
    return isNormal

#502
def doStartDeposit(param, __output_response__):
    global MEI

    if MEI is None:
        LOG.bvlog("[502]: Please Init Device", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("9951:Please Init Device")

    isNormal, returnMessage, messsage = MEI.startAcceptBill()

    if isNormal:
        __output_response__["code"] = "0000"
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = "Success"

        LOG.bvlog("[502]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[502]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.bvlog("[502]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = "9502" 
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = messsage

        LOG.bvlog("[502]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[502]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.bvlog("[502]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, messsage)
    
    return isNormal

#503
def doCancelDeposit(param, __output_response__):
    global MEI

    if MEI is None:
        LOG.bvlog("[503]: Please Init Device", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("9953:Please Init Device")

    isNormal, returnMessage, messsage = MEI.stopAcceptBill()

    if isNormal:
        __output_response__["code"] = "0000"
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = "Success"

        LOG.bvlog("[503]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[503]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.bvlog("[503]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = "9503" 
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = messsage

        LOG.bvlog("[503]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[503]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.bvlog("[503]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, messsage)
    
    return isNormal

#504
def doGetStatus(param, __output_response__):
    global MEI

    if MEI is None:
        LOG.bvlog("[504]: Please Init Device", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("9954:Please Init Device")

    isNormal, returnMessage, messsage = MEI.getStatus()

    if isNormal:
        __output_response__["code"] = "0000"
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = "Success"

        LOG.bvlog("[504]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[504]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.bvlog("[504]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = "9504" 
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = messsage

        LOG.bvlog("[504]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[504]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.bvlog("[504]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, messsage)
    
    return isNormal

#505
def doAcceptNote(param, __output_response__):
    global MEI

    if MEI is None:
        LOG.bvlog("[505]: Please Init Device", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("9955:Please Init Device")

    isNormal, returnMessage, messsage = MEI.storeNotesBill()

    if isNormal:
        __output_response__["code"] = "0000"
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = "Success"

        LOG.bvlog("[505]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[505]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.bvlog("[505]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = "9505" 
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = messsage

        LOG.bvlog("[505]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[505]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.bvlog("[505]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, messsage)
    
    return isNormal

#506
def doCancelNote(param, __output_response__):
    global MEI

    if MEI is None:
        LOG.bvlog("[506]: Please Init Device", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("9956:Please Init Device")

    isNormal, returnMessage, messsage = MEI.rejectNotesBill()

    if isNormal:
        __output_response__["code"] = "0000"
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = "Success"

        LOG.bvlog("[506]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[506]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.bvlog("[506]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __output_response__["code"] = "9506" 
        __output_response__["data"] = {
            "bill_response": returnMessage
            }
        __output_response__["message"] = messsage

        LOG.bvlog("[506]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.bvlog("[506]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.bvlog("[506]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, messsage)
    
    return isNormal