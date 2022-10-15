__author__ = "wahyudi@multidaya.id"

import sys, traceback
import os
os.system('pip install python-socketio[client]')

import socketio

SOCKET_IO = socketio.Client()

INTERRACTIVE_HOST = 'ws://192.168.7.8:3000'
TID = '18000101'

@SOCKET_IO.event
def connect():
    print(('Connected, ID', SOCKET_IO.sid))


@SOCKET_IO.event
def connect_error(data):
    print(('Connection Failed', str(data)))


@SOCKET_IO.event
def disconnect():
    print(('Disconnected'))
    
@SOCKET_IO.on('chat')
def on_chat(message):
    print(('Received', str(message)))
    print('Send Message : ')
    
    
def interraction(message='Halo Mas Ganteng'):
    try:
        SOCKET_IO.emit('chat', {
            'room': TID,
            'data': message
            })
    except Exception as e:
        print(str(e))

def main():
    global SOCKET_IO
    try:
        SOCKET_IO.connect(INTERRACTIVE_HOST)
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
    sys.exit(0)


if __name__ == "__main__":
    main()
