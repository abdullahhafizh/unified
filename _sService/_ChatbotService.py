__author__ = "wahyudi@multidaya.id"

import logging
from _cConfig import _Common
from _tTools import _Helper
from _sSync import _Sync
import sys

import os
# os.system('pip install python-socketio[client]')

import socketio

LOGGER = logging.getLogger()

SOCKET_IO = socketio.Client()

SCRIPT_PATH = sys.path[0] + '/_sService/'

HELLO_MESSAGE = open(os.path.join(SCRIPT_PATH, 'hello.script'), 'r').read().strip().split(',')


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
    if message.lower() in HELLO_MESSAGE:
        result = build_hello_message()
    else:
        result = _Sync.handle_tasks([
            {
                'taskName': message,
                'status': 'OPEN',
                'createdAt': _Helper.time_string(),
                'userId': SOCKET_IO.sid,
                'mode': 'CHATBOT'
            }
        ])
    response_message(result)
    
    
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
        print('pyt: Response Message\n', str(clean_message))
        SOCKET_IO.emit('chat', {
            'room': _Common.TID,
            'data': clean_message
            })
    except Exception as e:
        LOGGER.warning((e))
        print(str(e))
    
    
def build_hello_message():
    message = []
    message.append('Hi Team, Terminal '+_Common.TID+' ready for your command.')
    message.append('Application Version : '+_Common.VERSION)
    message.append('Below Available Commands :')
    for command in _Sync.available_commands():
        message.append(' - <strong>'+command.upper()+'</strong>')
    return '\n'.join(message)
