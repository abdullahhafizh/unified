from . import _NVEngine
import time
from multiprocessing import Queue, Process
from threading import Event
import traceback

def main_loop(lib_path:str, com_port:str, user_request:Queue, response:Queue):

    is_connected = False
    is_exit = False
    nv = init(lib_path, com_port)

    while True:
        request = user_request.get()
        if request == "ENABLE":
            is_connected = nv.ConnectToValidator()
            if is_connected:
                response.put("ENABLE_OK")
            else:
                response.put("ENABLE_FAIL")
        elif request == "EXIT":
            is_exit = True
            if is_exit:
                response.put("EXIT_OK")
            else:
                response.put("EXIT_FAIL")
        elif len(request) > 0:
            #GIVE FALSE POSITIF
            response.put(request+"_OK")

        while is_connected:
            isOk, message = nv.DoPoll()
            if not isOk:
                response.put("POLL_FAIL|{}".format(message))
                is_connected = False
                # Try Reconnect
                while not is_connected:
                    is_connected = nv.ConnectToValidator()
                    if not is_connected:
                        time.sleep(0.001)
                continue
            
            if len(message)>0:
                response.put("POLL_OK|{}".format(message))

            time.sleep(0.25)

            try:
                request = user_request.get_nowait()
                if request == "ENABLE":
                    is_connected = nv.ConnectToValidator()
                    if is_connected:
                        response.put("ENABLE_OK")
                    else:
                        response.put("ENABLE_FAIL")
                elif request == "DISABLE":
                    isOk = nv.DisableValidator()
                    if isOk:
                        is_connected = False

                    if isOk:
                        response.put("DISABLE_OK")
                    else:
                        response.put("DISABLE_FAIL")
                elif request == "REJECT":
                    isOk = nv.ReturnNote()
                    if isOk:
                        response.put("REJECT_OK")
                    else:
                        response.put("REJECT_FAIL")
                elif request == "ACCEPT":
                    isOk = nv.AcceptNote()
                    if isOk:
                        response.put("ACCEPT_OK")
                    else:
                        response.put("ACCEPT_FAIL")
                elif request == "RESET":
                    isOk = nv.Reset()
                    if isOk:
                        response.put("RESET_OK")
                    else:
                        response.put("RESET_FAIL")
                elif request == "EXIT":
                    if nv.DisableValidator():
                        is_connected = False
                        is_exit = True
                        response.put("EXIT_OK")

            except:
                pass

        if is_exit:
            break

        time.sleep(0.25)

    print("MAIN_LOOP EXIT")

def init(lib_path:str, com_port:str):
    nv = _NVEngine.NVEngine(lib_path, True)
    nv.m_cmd.ComPort = com_port
    nv.m_cmd.SSPAddress = 0
    nv.m_cmd.Timeout = 3000

    #Setting tahan note tanpa batas
    nv.m_HoldNumber = 1
    nv.m_HeldNoteByCount = False

    #Setting tahan note dengan batas counter
    # nv.m_HoldNumber = 10
    # nv.m_HeldNoteByCount = True
    return nv

PROCESS_NV = None
USER_REQUEST_NV = Queue()
RESPONSE_NV = Queue()
MUTEX_HOLDER = Event()
IS_RUNNING = False
IS_ENABLE = False
NV_OBJECT = None

def send_command(param:str=None, config=[], restricted=[], hold_note=False):
    global MUTEX_HOLDER
    global NV_OBJECT

    if MUTEX_HOLDER.is_set():
        # Change to false positif
        return 0, "OTHER INSTANCE RUNNING"
    
    MUTEX_HOLDER.set()

    try:
        if param:
            code = -1
            message = "UNKNOWN ERROR"

            param_split = param.split("|")
            cmd = param_split[0]
            if len(param_split) > 1:
                if NV_OBJECT is None:
                    NV_OBJECT = init(config["ENGINE_LIB"], param_split[1])
    
                if cmd == config["SET"]:
                    isOK = NV_OBJECT.ConnectToValidator()
                    if isOK:
                        #check for 10 error/last_message:
                        attempt = 10
                        while attempt > 0:
                            isOK, message = NV_OBJECT.DoPoll()
                            attempt -= 1

                        # check last message kalau ada potensi ada error / Lakukan manual reset
                        if len(message) > 0: code = -1
                        else: code = 0
                        message = "SET OK"
                    else:
                        message = "SET FAIL"                    
                elif cmd == config["ENABLE"]:
                    if NV_OBJECT.EnableValidator(): 
                        code = 0
                        message = "ENABLE OK"
                    else: message = "ENABLE FAIL"
                elif cmd == config["RECEIVE"]:
                    isOK, message = NV_OBJECT.DoPoll()
                    if isOK: 
                        code = 0
                    else: message = "RECEIVE FAIL"
                elif cmd == config["STOP"]:
                    if NV_OBJECT.DisableValidator(): 
                        code = 0
                        message = "STOP OK"
                    else: message = "STOP FAIL"
                elif cmd == config["STORE"]:
                    if NV_OBJECT.AcceptNote():
                        code = 0
                        message = "STORE OK"
                    else: message = "STORE FAIL"
                elif cmd == config["REJECT"]:
                    if NV_OBJECT.ReturnNote():
                        code = 0
                        message = "REJECT OK"
                    else: message = "REJECT FAIL"
                elif cmd == config["RESET"]:
                    if NV_OBJECT.Reset(): 
                        code = 0
                        message = "RESET OK"
                    else: message = "RESET FAIL"
            else:
                message = "PLEASE ADD | after cmd in param"
        else:
            message = "PARAM NOT SUPPORTED / PARAM KOSONG"        
    except Exception as e:
        error_string = traceback.format_exc()
        _NVEngine.LOGGER.warning((e))
        _NVEngine.LOGGER.debug(error_string)
        MUTEX_HOLDER.clear()
        code = -99
        message = str(e)
    finally:
        MUTEX_HOLDER.clear()
        return code, message

def get_response(response_nv:Queue, expected_response):
    response = ""
    code = -1
    attempt = 100
    response_list = []
    is_empty = False
    while not is_empty:
        try:
            response = response_nv.get(timeout=1)
        except:
            response = ""
            continue

        if response.__contains__(expected_response):
            code = 0
            response_list.append(response)
            break
        else:
            code = -1
            response_list.append(response)
        
        is_empty = response_nv.empty()

    return code, str(response_list)