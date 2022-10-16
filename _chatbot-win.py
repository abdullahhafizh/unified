__author__ = "wahyudi@multidaya.id"

from datetime import datetime
import sys, traceback
from termcolor import colored

import os
# os.system('pip install socketIO-client==0.5.7.2')
# os.system('pip install termcolor')

from socketIO_client import SocketIO, BaseNamespace

class Namespace(BaseNamespace):

    def on_connect(self):
        print(('Connected, ID', SOCKET_IO.sid))

    def on_connect_error(self, data):
        print(('Connection Failed', str(data)))

    def on_disconnect(self):
        print(('Disconnected'))
        
    def on_chat(self, message):
        print(('Received', str(message)))
        print('Send Message : ')


INTERRACTIVE_HOST = 'ws://192.168.7.8:3000'
TID = '18000101'


def now_time():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')


def welcome_text():
    print("""                                                  
            CONSOLE CHAT TOOLS
        Copyright PT. Multidaya Dinamika
                    -2022-
        Started At : {}
        """.format(now_time())
    )
    

def empty(s):
    if s is None:
        return True
    elif type(s) == bool and s is False:
        return True
    elif type(s) == int and s == 0:
        return True
    elif type(s) != int and len(s) == 0:
        return True
    else:
        return False
    
    
def interraction(message='Halo Mas Ganteng'):
    try:
        SOCKET_IO.emit('chat', {
            'room': TID,
            'data': message
            })
    except Exception as e:
        print(str(e))
        
        
def raise_exit(msg='General Error', code=1):
    if code == 0:
        print(colored(msg, 'green'))
    else:
        print(colored(msg, 'red'))
    sys.exit(code)
    
        
def initiate():
    global TID
    if len(sys.argv) > 1:
        print('Argument :', str(sys.argv))
        tid = sys.argv[1]
        if empty(tid):
            raise_exit('Wrong Argument Terminal ID')
        TID = tid
        print('Terminal ID', TID)
    else:
        raise_exit('Empty Argument')


def main():
    global SOCKET_IO
    try:
        # print('Chat Host', INTERRACTIVE_HOST+'\n')
        host = INTERRACTIVE_HOST.replace('ws', 'http')
        port = INTERRACTIVE_HOST.split(':')[2]
        SOCKET_IO = SocketIO(host, int(port), BaseNamespace)
        SOCKET_IO.emit('create', {
            'room': TID,
            'name': 'CONSOLE ' + TID,
        })
        while True:
            message = input('Send Message : \n')
            if len(message) > 0:
                interraction(message)
        # SOCKET_IO.wait()    
        # SOCKET_IO.sleep(1)
    except KeyboardInterrupt:
        print("Shutdown Requested... Exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    raise_exit('Finished', 0)


if __name__ == "__main__":
    welcome_text()
    initiate()
    main()
