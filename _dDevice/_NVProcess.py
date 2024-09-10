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

def send_command(param:str=None, config=[], restricted=[], hold_note=False):
    global PROCESS_NV
    global USER_REQUEST_NV
    global RESPONSE_NV
    global MUTEX_HOLDER
    global IS_RUNNING
    global IS_ENABLE

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
                if cmd == config["SET"]:
                    is_started = False
                    if PROCESS_NV:
                        is_started = PROCESS_NV.is_alive()

                    if is_started:
                        USER_REQUEST_NV.put("EXIT")
                        response = RESPONSE_NV.get()
                        if response == "EXIT_OK":
                            PROCESS_NV.join()

                    PROCESS_NV = Process(target=main_loop, args=(config["ENGINE_LIB"], param_split[1], USER_REQUEST_NV, RESPONSE_NV))
                    PROCESS_NV.start()
                    IS_RUNNING = True
                    code = 0
                    message = "SET OK"
                elif not IS_RUNNING:
                    return -1, "PROCESS NOT STARTED/SET"                
                elif cmd == config["ENABLE"]:
                    USER_REQUEST_NV.put("ENABLE")
                    code, message = get_response(RESPONSE_NV, "ENABLE_OK")
                elif cmd == config["RECEIVE"]:
                    response_list = []
                    response = "NONE"
                    while len(response) > 0:
                        try:
                            response = RESPONSE_NV.get(timeout=1)
                            response_list.append(response)
                        except:
                            response = ""
                            break
                        if len(response_list)> 10:
                            #MAX 10 message kemudian balikan agar tidak stay in the loop
                            break

                    code = 0
                    message = str(response_list)
                elif cmd == config["STOP"]:
                    USER_REQUEST_NV.put("DISABLE")
                    code, message = get_response(RESPONSE_NV, "DISABLE_OK")
                elif cmd == config["STORE"]:
                    USER_REQUEST_NV.put("ACCEPT")
                    code, message = get_response(RESPONSE_NV, "ACCEPT_OK")
                    if code == 0:
                        code, message = get_response(RESPONSE_NV, config["KEY_STORED"])
                elif cmd == config["REJECT"]:
                    USER_REQUEST_NV.put("REJECT")
                    code, message = get_response(RESPONSE_NV, "REJECT_OK")
                elif cmd == config["RESET"]:
                    USER_REQUEST_NV.put("RESET")
                    code, message = get_response(RESPONSE_NV, "RESET_OK")
            else:
                message = "PLEASE ADD | after cmd in param"

            MUTEX_HOLDER.clear()
            return code, message
        else:
            MUTEX_HOLDER.clear()
            return -1, "PARAM NOT SUPPORTED / PARAM KOSONG"
        
    except Exception as e:
        error_string = traceback.format_exc()
        _NVEngine.LOGGER.warning((e))
        _NVEngine.LOGGER.debug(error_string)
        MUTEX_HOLDER.clear()
        return -99, str(e)

def get_response(response_nv:Queue, expected_response):
    response = ""
    code = -1
    attempt = 10
    response_list = []
    while attempt > 0:
        try:
            response = response_nv.get(timeout=1)
        except:
            response = ""
            attempt -= 1
            continue

        if response.__contains__(expected_response):
            code = 0
            response_list.append(response)
            break
        else:
            code = -1
            response_list.append(response)
        attempt -= 1
    if attempt == 0:
        response_list.append("TIMEOUT")

    return code, str(response_list)