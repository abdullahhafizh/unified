__author__ = 'wahyudi@multidaya.id'

import datetime
from . import _CPrepaidProtocol as proto
from serial import Serial, PARITY_NONE, STOPBITS_ONE
from time import sleep
import os


STX = b'\x10\x02'
ETX = b'\x10\x03'


def READER_DUMP(Ser, console=False, min_row=10):
    sam = {}
    sam["cmd"] = b"\xB4"

    bal_value = sam["cmd"]
    p_len, p = proto.Compose_Request(len(bal_value), bal_value)
    
    if console: print(p, p_len)

    Ser.flush()
    write = Ser.write(p)
    Ser.flush()
    
    sleep(2)
    
    dump_data = retrieve_rs232_dump_data(Ser, console, min_row)

    return '0000', dump_data

'''
------------------------------------------------------------------------------------------------
'''

def retrieve_rs232_data(Ser=Serial()):
    response = b''
    while True:
        response = response + Ser.read()
        # LOG.fw("DEBUG_READ:", response)
        if response.__contains__(ETX):
            i_end = response.index(ETX)
            response = response[:(i_end+len(ETX))]
            if response[0] == STX[1]: 
                response = STX[0].to_bytes(1, 'big') + response
            return response
    # start =  Ser.read_until(b'\x10\x02')
    # LOG.fw("READ_START:", start)
    # end = Ser.read_until(ETX)
    # LOG.fw("READ_END:", end)
    # result = start + end
    # return result
    

# Not Used
def retrieve_rs232_dump_data(Ser=Serial(), console=False, min_row=3):
    response = []
    while True:
        line = Ser.readline()
        if console: print(line)
        if len(line):
            response.append(line)
            continue
        if len(response) < min_row:
            continue
        else:
            break
    response = os.linesep.join(response)
    return 


if __name__ == '__main__':
    _port = 'COM5'
    _baudrate = 38400
    _min_row = 10
    
    try:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        COMPORT = Serial(_port, baudrate=_baudrate, bytesize=8, parity=PARITY_NONE, stopbits=STOPBITS_ONE)
        print(COMPORT.isOpen())
        READER_DUMP(COMPORT, True, _min_row)
    except KeyboardInterrupt:
        if COMPORT.isOpen():
            COMPORT.close()
    except Exception as e:
        print(e)
