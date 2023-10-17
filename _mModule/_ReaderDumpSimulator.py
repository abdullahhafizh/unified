__author__ = 'wahyudi@multidaya.id'

import datetime
from serial import Serial, PARITY_NONE, STOPBITS_ONE
from time import sleep
import os, sys, json


STX = b'\x10\x02'
ETX = b'\x10\x03'
SUCCESS_CODE = '0000'
LINE_SEPARATOR = b'==EOL=='


def compose_request(len_data, data):
    out_data = b"\x10\x02\x08\x00\x00\x00\x00\x00\x00"
    len_str = format(len_data, 'x').upper().zfill(4)
    out_data = out_data + bytearray.fromhex(len_str)
    out_data = out_data + data
    c = 0
    for x in range(2,len(out_data)):
        c = c ^ out_data[x]
    # c = bytearray.fromhex(format(len_data, 'x').upper().zfill(2))
    out_data = out_data + c.to_bytes(1, byteorder='big') + b"\x10\x03"
    # print(out_data)
    
    return len(out_data), out_data


def READER_DUMP(Ser, console=False, min_row=10):
    sam = {}
    sam["cmd"] = b"\xB4"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)
    
    if console: print(p, p_len)

    Ser.flush()
    write = Ser.write(p)
    Ser.flush()
    
    sleep(1)
    
    dump_data = retrieve_rs232_dump_data(Ser, console)

    return SUCCESS_CODE, dump_data

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
    

def log_to_file(content='', filename='', default_ext='.dump'):
    path = sys.path[0]
    if '.' not in filename:
        filename = filename + default_ext
    path_file = os.path.join(path, filename)
    with open(path_file, 'w') as file_logging:
        print('Create Dump File : ' + path_file)
        for line in content.split('\n'):
            file_logging.write(line)
            file_logging.write('\n')
        file_logging.close()
    return path_file


# Not Used
def retrieve_rs232_dump_data(Ser=Serial(), console=False):
    response = b''
    while True:
        line = Ser.readline()
        if console: print(line)
        if line:
            print('Add Line')
            response += line
            if line.__contains__(b'Stop:B4'):
                if console: print('Stop')
                break
            else:
                continue
    return response.decode('ascii')

if __name__ == '__main__':
    _port = 'COM5'
    _baudrate = 38400
    _reff = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        COMPORT = Serial(_port, baudrate=_baudrate, bytesize=8, parity=PARITY_NONE, stopbits=STOPBITS_ONE)
        print(COMPORT.isOpen())
        result, data = READER_DUMP(COMPORT, True)
        print('Data Length', result, len(data))
        if result == SUCCESS_CODE:
            out_file = log_to_file(content=data, filename=('test'+_reff))
            print(out_file)
    except KeyboardInterrupt:
        if COMPORT.isOpen():
            COMPORT.close()
    except Exception as e:
        print(e)
    finally:
        print('Exit')
        sys.exit()
