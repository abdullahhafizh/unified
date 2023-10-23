__author__ = 'wahyudi@multidaya.id'

import datetime
from serial import Serial, PARITY_NONE, STOPBITS_ONE
from time import sleep
import os, sys, json
from func_timeout import func_set_timeout
import traceback


STX = b'\x10\x02'
ETX = b'\x10\x03'
SUCCESS_CODE = '0000'
LINE_SEPARATOR = b'==EOL=='
ETX_DUMP = b'EVENT:CMD:B4 Stop'
WAIT_AFTER_CMD = .2
MIN_REPLY_LENGTH = 5


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
    
    # print(len(out_data), out_data)
    return len(out_data), out_data


def parse_default_template(data):
    '''
    TBalResponsws  = packed record
    start   : array[0..1] of byte;
    header  : array[0..6] of byte;
    len     : array[0..1] of byte;
    data    : TBalanceresws;
    res     : array[0..2] of byte;
    end; 
    '''
    result = {}
    # Handle Anomaly Response From Reader Missing STX
    # if data[0] != b'\x10': 
    #     data = b'\x10' + data
    result["start"] = data[0:2]
    result["header"] = data[2:9]
    result["len"] = data[9:11]
    len_data = 11+int.from_bytes(result['len'],byteorder='big', signed=False)
    result["data"] = data[11:len_data]
    result["code"] = result["data"][1:5]
    result["res"] = data[len_data:len_data+3]

    return result


def parse_card_data_template(data):
    '''
    TBalanceresws = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    sign  : byte;
    bal   : array[0..9] of char;
    sn    : array[0..15] of char;
    end; 
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    try:
        result["sign"] = chr(int(data[5]))
        result["bal"] = data[6:16]
        if result['code'].decode('utf-8') == SUCCESS_CODE:
            amount = int(result["bal"])
    except:
        result["sign"] = ''
        result["code"] = b'ERR0'
    result["bal"] = data[6:16]
    result["sn"] = data[16:32]

    return result


def CLEAR_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB5"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)


def READER_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB4"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    result = dict()
    result['raw'] = b''
    result['etx'] = False
    
    try:
        res = retrieve_rs232_dump_data(Ser, result)
        print(res)
    except:
        err_message = traceback._cause_message
        print('EXCP: ', err_message)
    finally:
        CLEAR_DUMP(Ser)
        return SUCCESS_CODE, result['raw']
    

def GET_BALANCE_WITH_SN(Ser=Serial()):
    bal = {}
    bal["cmd"] = b"\xEF"
    st = datetime.datetime.now().strftime("%d%m%y%H%M00")
    bal["date"] = st
    st = "005"
    bal["tout"] = st

    bal_value = bal["cmd"] + bal["date"].encode("utf-8") + bal["tout"].encode("utf-8")
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)

    result = parse_card_data_template(response["data"])
    
    del data
    del response

    return result["code"].decode('utf-8'), result


def GET_CARD_HISTORY(Ser=Serial()):
    send = {}
    send["cmd"] = b"\xA5"
    
    bal_value = send["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    del data

    return response["code"].decode('utf-8'), response


def CARD_DISCONNECT(Ser):
    sam = {}
    sam["cmd"] = b"\xFA"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    del data
    
    return SUCCESS_CODE, response

'''
------------------------------------------------------------------------------------------------
'''

def send_command(Ser, p):
    print('Send', p)
    Ser.flush()
    Ser.write(p)
    sleep(WAIT_AFTER_CMD)
    Ser.flush()


def retrieve_rs232_data(Ser=Serial()):
    response = b''
    while True:
        response = Ser.read_until(ETX)
        # print('Read', response)

        if len(response) < MIN_REPLY_LENGTH:
            response = b''
            sleep(WAIT_AFTER_CMD)
            continue
        
        if response.__contains__(ETX):
            if response[:2] != STX: 
                print('Wrong STX', response[:2])
                response = STX[0].to_bytes(1, 'big') + response
                print('Fix STX', response[:2])
            i_start = response.index(STX)
            i_end = response.index(ETX)
            if i_start:
                print('Remove', len(response[:i_start]))
                response = response[i_start:(i_end+len(ETX))]
            else:
                response = response[:(i_end+len(ETX))]
            print('Receive', response)
            return response


def log_to_file(content='', filename='', default_ext='.dump'):
    path = sys.path[0]
    if '.' not in filename:
        filename = filename + default_ext
    path_file = os.path.join(path, 'Logs', filename)
    if type(content) == bytes:
        content = content.decode('cp1252')
    with open(path_file, 'w') as file_logging:
        print('Create Dump File : ' + path_file)
        for line in content.split('\n'):
            file_logging.write(line)
            file_logging.write('\n')
        file_logging.close()
    return path_file


DUMP_DURATION = 60

# Must Wait Within 60 Seconds
@func_set_timeout(DUMP_DURATION)
def retrieve_rs232_dump_data(Ser=Serial(), result={}):
    print('Dump Duration', DUMP_DURATION)
    while True:
        line = Ser.readline()
        if line:
            result['raw'] += line
            # If Do This Below, The Data Might be trimmed/not actual
            if line.__contains__(ETX_DUMP):
                print(ETX_DUMP.decode() + ' Detected')
                if result.get('etx') is True:
                    print('Break')
                    break
        continue
    return True


def do_exit(m):
    print(m)
    sys.exit()
    

AVAILABLE_COMMAND = {
    '1': 'Card Balance',
    '2': 'Card Disconnect',
    '3': 'Card Log',
    '9': 'Reader Dump',
    'X': 'Exit'
}

AVAILABLE_COMMAND = dict(sorted(AVAILABLE_COMMAND.items()))

avail_command_text = 'Pilih Mode Berikut : \n'

for c in AVAILABLE_COMMAND.keys():
    avail_command_text += (c + ' - ' + AVAILABLE_COMMAND.get(c) + '\n')

avail_command_text += 'Pilih Nomor : '


if __name__ == '__main__':
    COMPORT = None
    _port = 'COM5'
    _baudrate = 115200
    
    if len(sys.argv) > 1:
        print('Argument :', str(sys.argv))
        _port = sys.argv[1]
        _baudrate = int(sys.argv[2])
    
    print('Selected Port : ', str(_port))
    print('Selected Baudrate : ', str(_baudrate))
    
    try:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        COMPORT = Serial(_port, baudrate=_baudrate, bytesize=8, parity=PARITY_NONE, stopbits=STOPBITS_ONE)
        if COMPORT.isOpen():
            print('Reader OPEN', COMPORT.isOpen())
            while True:
                mode = input(avail_command_text)
                if mode in ['x', 'X']:
                    do_exit('Select X To Quit')
                    break
                elif mode in AVAILABLE_COMMAND.keys():
                    # print('Selected Mode : ', str(mode))
                    if mode == '1':
                        result, data = GET_BALANCE_WITH_SN(COMPORT)
                    elif mode == '3':
                        result, data = GET_CARD_HISTORY(COMPORT)
                    elif mode == '9':
                        _reff = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        result, data = READER_DUMP(COMPORT)
                        if result == SUCCESS_CODE:
                            out_file = log_to_file(content=data, filename=('simulator'+_reff))
                            print(out_file)
                    elif mode == '2':
                        result, data = CARD_DISCONNECT(COMPORT)
                    print('Data Length', result, data, len(data))
        else:
            print('Reader Cannot Be OPEN')
    except Exception as e:
        print('EXCP: ',e)
    finally:
        if COMPORT is not None and COMPORT.isOpen():
            COMPORT.close()
        do_exit('Finished')
