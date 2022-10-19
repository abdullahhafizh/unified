__author__ = "wahyudi@multidaya.id"

import logging
from _cConfig import _Common
from _tTools import _Helper
from _sSync import _Sync
from _nNetwork import _HTTPAccess
import sys
import os
from time import sleep

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
    if not is_response_message(message):
        process_message(message)
    

LOGGER = logging.getLogger()
SCRIPT_PATH = sys.path[0] + '/_sService/'

HELLO_WORDS = open(os.path.join(SCRIPT_PATH, 'hello.script'), 'r').read().strip().split(',')
BAD_WORDS_TEMPLATE = open(os.path.join(SCRIPT_PATH, 'bad-words.script'), 'r').read().strip().split(',')
BAD_WORDS = list(map(lambda x: x.lower(), BAD_WORDS_TEMPLATE))

RESPONSE_DECODER = '\t\t\t'
MULTI_RESPONSE_DECODER = '[[|MR|]]'
TODAYS_NEWS_MESSAGE = ['berita_hari_ini', 'todays_news', 'news_feed', 'tell_me_story', 'story_me']

def is_response_message(m):
    return  m[:3] == RESPONSE_DECODER
        
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
    response = []
    message = message.strip()
    if message.lower() in HELLO_WORDS:
        result = build_hello_message()
    elif message.lower() in BAD_WORDS:
        result = 'NOT_APPROPRIATE'
    elif message.lower() in TODAYS_NEWS_MESSAGE :
        result = get_news_message()
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
    if MULTI_RESPONSE_DECODER in result:
        for res in result.split(MULTI_RESPONSE_DECODER):
            response.append(res)
    else:
        response.append(result)
        
    while True:
        for res in response:
            result = human_message(res)
            response_message(result)
            sleep(1)
    

def find_arguments(message):
    for delimit in [' ', '\r\n', '\r', '\n', '|']:
        arguments = message.split(delimit)
        if len(arguments) > 1:
            break
    return arguments


def get_news_message():
    news = []
    status, response = _HTTPAccess.get_from_url('https://newsapi.org/v2/top-headlines?country=id&apiKey=eda20002dbc44b2ab46205e783ad4354')
    if status == 200:
        if response.get('status') == 'ok':
            if int(response.get('totalResults', '0')) > 0:
                if len(response.get('articles', [])) > 0:
                    for new in response.get('articles', []):
                        news.append(new['title'])
    return MULTI_RESPONSE_DECODER.join(news)


def human_message(m):
    if m is None:
        return 'Terjadi kesalahan dalam eksekusi instruksi'
    elif m == 'NOT_SUPPORTED':
        return 'Mohon Maaf, Instruksi tidak didukung saat ini'
    elif m == 'NOT_UNDERSTAND':
        return 'Mohon Maaf, Instruksi tidak dimengerti mesin'
    elif m == 'NOT_APPROPRIATE':
        return 'Mohon Maaf, Tolong berikan instruksi yang baik saja ya!'
    elif m == 'TRX_NOT_FOUND':
        return 'Mohon Maaf, Data Transaksi tersebut tidak ditemukan di mesin ini'  
    elif m == 'PARAMETER_MISMATCH':
        return 'Mohon Maaf, Parameter instruksi tidak sesuai!'  
    elif '_' in m and len(m) < 100:
        return 'Hasil eksekusi : <strong>' + m + '</strong>'
    elif '-' in m and len(m) < 100:
        return 'Hasil eksekusi : <strong>' + m + '</strong>'
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
            'data': RESPONSE_DECODER + clean_message
            })
    except Exception as e:
        LOGGER.warning((e))
        print(str(e))
    
    
def build_hello_message():
    message = []
    message.append('Halo Tim, Mesin '+_Common.TID+' sudah siap untuk instruksi Kamu.')
    message.append('Versi Aplikasi Mesin : <strong>'+_Common.VERSION+'</strong>')
    message.append('Instruksi yang dapat digunakan :')
    for command in _Sync.available_commands():
        message.append(' - <strong>'+command.upper()+'</strong>')
    return '\n'.join(message)
