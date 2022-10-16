__author__ = "wahyudi@multidaya.id"

import logging
from _cConfig import _Common
from _tTools import _Helper
from _sSync import _Sync
import sys
import os

import socketio
SOCKET_IO = socketio.Client()
    
@SOCKET_IO.event
def connect():
    LOGGER.info(('Connected, ID', SOCKET_IO.sid))

@SOCKET_IO.event
def connect_error(data):
    LOGGER.info(('Connection Failed', str(data)))

@SOCKET_IO.event
def disconnect():
    # LOGGER.info(('Disconnected'))
    print(('Disconnected'))
        
@SOCKET_IO.on('chat')
def on_chat(message):
    print('pyt: Receive Message\n', str(message))
    process_message(message)
    

LOGGER = logging.getLogger()
SCRIPT_PATH = sys.path[0] + '/_sService/'

HELLO_WORDS = open(os.path.join(SCRIPT_PATH, 'hello.script'), 'r').read().strip().split(',')
BAD_WORDS_TEMPLATE = open(os.path.join(SCRIPT_PATH, 'bad-words.script'), 'r').read().strip().split(',')
BAD_WORDS = list(map(lambda x: x.lower(), BAD_WORDS_TEMPLATE))


# class WindowsNamespace(BaseNamespace):
    
#     def on_connect(self):
#         print(('Connected, ID', SOCKET_IO.sid))

#     def on_connect_error(self, data):
#         print(('Connection Failed', str(data)))

#     def on_disconnect(self):
#         print(('Disconnected'))
        
#     def on_chat(self, message):
#         print(('Received', str(message)))
#         process_message(message)


def start_initiation():
    _Helper.get_thread().apply_async(init)


def init():
    global SOCKET_IO
    try:
        SOCKET_IO.connect(_Common.INTERRACTIVE_HOST)
        SOCKET_IO.emit('create', {
            'room': _Common.TID,
            'name': 'VM ' + _Common.TID,
        })
        SOCKET_IO.wait()
        SOCKET_IO.sleep(1)
    except Exception as e:
        LOGGER.warning((e))
        
    
def process_message(message):
    if message.lower() in HELLO_WORDS:
        result = build_hello_message()
    elif message.lower() in BAD_WORDS:
        result = 'NOT_APPROPRIATE'
    else:
        arguments = find_arguments(message)
        if len(arguments) > 2:
            result = 'PARAMETER_MISMATCH'
            for arg in arguments:
                if arg.lower() in HELLO_WORDS:
                    result = build_hello_message()
                    break
                if arg.lower() in BAD_WORDS:
                    result = 'NOT_APPROPRIATE'
                    break
        else:
            result = _Sync.handle_tasks([
                {
                    'taskName': message.replace(' ', '|'),
                    'status': 'OPEN',
                    'createdAt': _Helper.time_string(),
                    'userId': SOCKET_IO.sid,
                    'mode': 'CHATBOT'
                }
            ])
    # Serialise to Readable Response
    result = human_message(result)
    response_message(result)
    

def find_arguments(message):
    for delimit in [' ', '\r\n', '\r', '\n', '|']:
        arguments = message.split(delimit)
        if len(arguments) > 1:
            break
    return arguments


def human_message(m):
    if m == 'NOT_SUPPORTED':
        return 'Mohon Maaf, Instruksi tidak didukung saat ini'
    elif m == 'NOT_UNDERSTAND':
        return 'Mohon Maaf, Instruksi tidak dimengerti mesin'
    elif m == 'NOT_APPROPRIATE':
        return 'Mohon Maaf, Tolong berikan instruksi yang baik saja ya!'
    elif m == 'PARAMETER_MISMATCH':
        return 'Mohon Maaf, Parameter instruksi tidak sesuai!'    
    else:
        return m
    
    
def serialise_chatbot_response(res):
    try:
        # print(('Initial Message', type(res), str(res)))
        if type(res) is None: return ''
        elif type(res) == tuple: return str(res)
        elif type(res) == str: return res
        elif type(res) == list: 
            lresult = []
            delimit = ','
            for l in res:
                if type(l) == dict:
                    delimit = '\n'
                    dl = []
                    for lkey in l.keys():
                        dl.append(lkey.upper() + '-' + serialise_chatbot_response(l.get(lkey)))
                    lresult.append('|'.join(dl))
                else:
                    lresult.append(str(l))
            return delimit.join(lresult)
        elif type(res) == int: return str(res)
        elif type(res) == dict:
            result = []
            for key in res.keys():
                result.append(key.upper() + ' : ' + serialise_chatbot_response(res.get(key)))
            return '\n'.join(result)
        else:
            return 'ERROR_TYPE'
    except Exception as e:
        LOGGER.warning((e))
        return 'ERROR_EXCEPTION'
    

def response_message(message='Halo Mas Ganteng'):
    try:
        clean_message = serialise_chatbot_response(message)
        # print('pyt: Response Message\n', str(clean_message))
        SOCKET_IO.emit('chat', {
            'room': _Common.TID,
            'data': clean_message
            })
    except Exception as e:
        LOGGER.warning((e))
        print(str(e))
    
    
def build_hello_message():
    message = []
    message.append('Halo Tim, Mesin '+_Common.TID+' sudah siap untuk instruksi Kamu.')
    message.append('Versi Aplikasi Mesin : '+_Common.VERSION)
    message.append('Instruksi yang dapat digunakan :')
    for command in _Sync.available_commands():
        message.append(' - <strong>'+command.upper()+'</strong>')
    return '\n'.join(message)
