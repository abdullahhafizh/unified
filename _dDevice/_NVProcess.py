from . import _NVEngine
import time
from multiprocessing import Queue, Process
from threading import Event, Thread
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
    try:
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
    except:
        return None

PROCESS_NV = None
USER_REQUEST_NV = Queue()
RESPONSE_NV = Queue()
MUTEX_HOLDER = Event()
HELD_EVENT = Event()
IS_RUNNING = False
IS_ENABLE = False
NV_OBJECT = None
NV_HELD = Event()
NV_HELD_TH = None

def held(nv:_NVEngine.NVEngine, held:Event, loop_delay):
    message = ""
    held.set()
    _NVEngine.LOGGER.info("HELD Thread started -> DELAY {}".format(loop_delay))
    nv.log_active = False
    while held.is_set():
        isOk, new_message = nv.DoPoll()
        if isOk:
            if message != new_message:
                message = new_message
                _NVEngine.LOGGER.info((message))
        time.sleep(loop_delay)
    nv.log_active = True
    _NVEngine.LOGGER.info("HELD Thread stoped")


def send_command(param:str=None, config=[], restricted=[], hold_note=False):
    global MUTEX_HOLDER
    global NV_OBJECT
    global NV_HELD
    global NV_HELD_TH

    if MUTEX_HOLDER.is_set():
        # Change to false positif
        return 0, "OTHER_INSTANCE_RUNNING"
    
    MUTEX_HOLDER.set()

    try:
        if param:
            code = -1
            message = "UNKNOWN_ERROR"

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
                        else: 
                            NV_OBJECT.DisableValidator()
                            code = 0
                        message = "SET_OK"
                    else:
                        message = "SET_FAIL"                    
                elif cmd == config["ENABLE"]:
                    isOK, message = NV_OBJECT.EnableValidator()
                    if isOK: 
                        code = 0
                        message = "ENABLE_OK"
                elif cmd == config["RECEIVE"]:
                    isOK, message = NV_OBJECT.DoPoll()
                    if isOK: 
                        code = 0
                        if config['KEY_RECEIVED'] in message:
                            is_active = not (NV_HELD_TH is None)
                            if is_active:
                                NV_HELD.clear()
                                NV_HELD_TH.join()
                            NV_HELD_TH = Thread(target=held, args=(NV_OBJECT, NV_HELD, config['LOOP_DELAY']))
                            NV_HELD_TH.start()
                    else: message = "RECEIVE_FAIL"
                elif cmd == config["STOP"]:
                    if NV_OBJECT.DisableValidator(): 
                        code = 0
                        message = "STOP_OK"
                    else: message = "STOP_FAIL"
                elif cmd == config["STORE"]:
                    is_active = not (NV_HELD_TH is None)
                    if is_active:
                        NV_HELD.clear()
                        NV_HELD_TH.join()        

                    if NV_OBJECT.AcceptNote():
                        while True:
                            isOK, message = NV_OBJECT.DoPoll()
                            if config['KEY_STORED'] in message:
                                code = 0
                                message = "STORE_OK"
                                break
                            time.sleep(config['LOOP_DELAY'])
                    else: message = "STORE_FAIL"
                elif cmd == config["REJECT"]:
                    is_active = not (NV_HELD_TH is None)
                    if is_active:
                        NV_HELD.clear()
                        NV_HELD_TH.join()
                    isOK, message = NV_OBJECT.ReturnNote()
                    if isOK:
                        code = 0
                        message = "REJECT_OK"
                elif cmd == config["RESET"]:
                    isOK, message = NV_OBJECT.Reset()
                    if isOK: 
                        isOK = NV_OBJECT.ConnectToValidator()
                        if isOK:
                            isOK = NV_OBJECT.DisableValidator()
                            if isOK:
                                code = 0
                                message = "RESET_OK"
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