__author__ = 'wahyudi@multidaya.id'

import traceback
from _mModule import _CPrepaidLog as LOG
from _mModule import _GRGSerialCom

GRG = None

def send_command(cmd, param):
    LOG.grglog("LIB [{0}]: Param = ".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW, param)

    __global_response__ = {
        "Command": cmd,
        "Parameter": param,
        "Response": "",
        "ErrorDesc": "",
        "Result": ""
    }
    
    try:
        LOG.grglog("LIB [{0}]: Mulai".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW)

        if cmd == "501":
            doInit(param, __global_response__)
        elif cmd == "502":
            doStartDeposit(param, __global_response__)
        elif cmd == "503":
            doCancelDeposit(param, __global_response__)
        elif cmd == "504":
            doGetStatus(param, __global_response__)
        elif cmd == "505":
            doAcceptNote(param, __global_response__)
        elif cmd == "506":
            doCancelNote(param, __global_response__)
        else:
            raise SystemError("Command ["+cmd+"] not Supported")

    except:
        trace = traceback.format_exc()
        formatted_lines = trace.splitlines()
        err_message = traceback._cause_message
        LOG.grglog("LIB [{0}]: ERROR ".format(cmd), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_NO_FLOW, formatted_lines[-1])
        LOG.grglog("LIB [{0}]: TRACE ".format(cmd), LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_NO_FLOW, trace)

        __global_response__["Result"] = "EXCP"
        __global_response__["ErrorDesc"] = trace
    finally:
        LOG.grglog("LIB [{0}]: DONE\r\n".format(cmd), LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_NO_FLOW)

    return __global_response__

#501
def doInit(param, __global_response__):
    global GRG

    Param = param.split('|')

    if len(Param) == 1:
        GRG_PORT = "COM"+Param[0]
    else:
        LOG.grglog("[501]: Parameter tidak lengkap: ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, param)
        raise SystemError("Parameter tidak lengkap: "+param)

    LOG.grglog("[501]: Parameter = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, GRG_PORT)

    if GRG is None:
        GRG = _GRGSerialCom.GRGSerial()

    isNormal, returnMessage, rawMessage = GRG.initConnect(GRG_PORT)

    if isNormal:
        __global_response__["Result"] = "0000"
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = "Sukses"

        LOG.grglog("[501]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[501]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.grglog("[501]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __global_response__["Result"] = "1" 
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = rawMessage

        LOG.grglog("[501]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[501]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.grglog("[501]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, rawMessage)
    
    return isNormal

#502
def doStartDeposit(param, __global_response__):
    global GRG

    if GRG is None:
        LOG.grglog("[502]: Lakukan init terlebih dulu", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("Lakukan init terlebih dulu")

    isNormal, returnMessage, rawMessage = GRG.startDeposit()

    if isNormal:
        __global_response__["Result"] = "0000"
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = "Sukses"

        LOG.grglog("[502]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[502]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.grglog("[502]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __global_response__["Result"] = "1" 
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = rawMessage

        LOG.grglog("[502]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[502]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.grglog("[502]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, rawMessage)
    
    return isNormal

#503
def doCancelDeposit(param, __global_response__):
    global GRG

    if GRG is None:
        LOG.grglog("[503]: Lakukan init terlebih dulu", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("Lakukan init terlebih dulu")

    isNormal, returnMessage, rawMessage = GRG.cancelDeposit()

    if isNormal:
        __global_response__["Result"] = "0000"
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = "Sukses"

        LOG.grglog("[503]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[503]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.grglog("[503]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __global_response__["Result"] = "1" 
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = rawMessage

        LOG.grglog("[503]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[503]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.grglog("[503]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, rawMessage)
    
    return isNormal

#504
def doGetStatus(param, __global_response__):
    global GRG

    if GRG is None:
        LOG.grglog("[504]: Lakukan init terlebih dulu", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("Lakukan init terlebih dulu")

    isNormal, returnMessage, rawMessage = GRG.getStatus()

    if isNormal:
        __global_response__["Result"] = "0000"
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = "Sukses"

        LOG.grglog("[504]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[504]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.grglog("[504]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __global_response__["Result"] = "1" 
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = rawMessage

        LOG.grglog("[504]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[504]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.grglog("[504]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, rawMessage)
    
    return isNormal

#505
def doAcceptNote(param, __global_response__):
    global GRG

    if GRG is None:
        LOG.grglog("[505]: Lakukan init terlebih dulu", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("Lakukan init terlebih dulu")

    isNormal, returnMessage, rawMessage = GRG.confirmNote()

    if isNormal:
        __global_response__["Result"] = "0000"
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = "Sukses"

        LOG.grglog("[505]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[505]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.grglog("[505]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __global_response__["Result"] = "1" 
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = rawMessage

        LOG.grglog("[505]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[505]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.grglog("[505]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, rawMessage)
    
    return isNormal

#506
def doCancelNote(param, __global_response__):
    global GRG

    if GRG is None:
        LOG.grglog("[506]: Lakukan init terlebih dulu", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC)
        raise SystemError("Lakukan init terlebih dulu")

    isNormal, returnMessage, rawMessage = GRG.cancelNote()

    if isNormal:
        __global_response__["Result"] = "0000"
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = "Sukses"

        LOG.grglog("[506]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[506]: Result = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "0000")
        LOG.grglog("[506]: Sukses", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC)
    else:
        __global_response__["Result"] = "1" 
        __global_response__["Response"] = returnMessage
        __global_response__["ErrorDesc"] = rawMessage

        LOG.grglog("[506]: Response = ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, returnMessage)
        LOG.grglog("[506]: Result = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_OUT, "1")
        LOG.grglog("[506]: Gagal = ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, rawMessage)
    
    return isNormal