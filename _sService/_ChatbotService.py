__author__ = "wahyudi@multidaya.id"

import logging
from _cConfig import _Common
from _tTools import _Helper
from _sSync import _Sync
import sys
import os
from time import sleep
from newsapi import NewsApiClient

# Init
NEWSAPI = None

import socketio
SOCKET_IO = socketio.Client(reconnection=True, logger=False, engineio_logger=False)
    
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
NEWS_DECODER = ':::'
MULTI_RESPONSE_DECODER = '[[|MR|]]'
TODAYS_NEWS_MESSAGE = ['berita_hari_ini', 'todays_news', 'news_feed', 'tell_me_story', 'story_me', 'tell_me_about', 'ceritakan', 'tell_me', 'what_about', 'how_is', 'berita', 'berita_tentang']

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


def init(attempt=1):
    global SOCKET_IO
    try:
        LOGGER.debug((attempt))
        SOCKET_IO.connect(_Common.INTERRACTIVE_HOST)
        SOCKET_IO.emit('create', {
            'room': _Common.TID,
            'name': 'VM ' + _Common.TID,
        })
        SOCKET_IO.wait()
        SOCKET_IO.sleep(1)
    except Exception as e:
        LOGGER.warning((e))
    finally:
        while True:
            attempt += 1
            sleep(60*60)
            init(attempt)
        
    
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
        if len(arguments) >= 2:
            result = 'PARAMETER_MISMATCH'
            for arg in arguments:
                if arg.lower() in HELLO_WORDS:
                    result = build_hello_message()
                    break
                elif arg.lower() in BAD_WORDS:
                    result = 'NOT_APPROPRIATE'
                    break
                elif arg.lower() in TODAYS_NEWS_MESSAGE :
                    result = get_news_message(message)
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
    # print('pyt: Raw Message -> '+str(result))
    if MULTI_RESPONSE_DECODER in result:
        for res in result.split(MULTI_RESPONSE_DECODER):
            # print('pyt: Append Result -> '+str(res))
            response.append(NEWS_DECODER+res)
    else:
        response.append(result)
        
    while True:
        for res in response:
            result = human_message(res)
            response_message(result)
            sleep(1)
        break
    

def find_arguments(message):
    for delimit in [' ', '\r\n', '\r', '\n', '|']:
        arguments = message.split(delimit)
        if len(arguments) > 1:
            break
    print('pyt: Args Length '+str(len(arguments)))
    return arguments


def get_news_message(keyword='transjakarta'):
    global NEWSAPI
    news = []
    selected_keyword = keyword.split(' ')[-1:]
    print('pyt: Found Keyword '+str(selected_keyword))
    try:
        if NEWSAPI is None:
            NEWSAPI = NewsApiClient(api_key='eda20002dbc44b2ab46205e783ad4354')
        response = NEWSAPI.get_everything(
            q=selected_keyword[0]
            )
        if response.get('status') == 'ok':
            if int(response.get('totalResults', '0')) > 0:
                if len(response.get('articles', [])) > 0:
                    for new in response.get('articles', []):
                        if len(news) >= 10: break
                        news.append(new['title'])      
                        # news.append(new['description'] + '<br />Link : <span><a href="'+news['url']+'" target="_blank">Here</a></span>')      
    except Exception as e:
        print('pyt: '+str(e))
    finally:
        if len(news) == 0: return 'NOT_UNDERSTAND'
        else : return MULTI_RESPONSE_DECODER.join(news)


def human_message(m):
    if m is None:
        return 'Terjadi kesalahan dalam eksekusi instruksi'
    elif NEWS_DECODER in m:
        return '<strong>FYI : ' + m.replace(NEWS_DECODER, '') + '</strong>'
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
    elif ('_' in m or '-' in m) and len(m) < 100:
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
