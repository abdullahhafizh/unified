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


def parse_card_history_template(data):
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
    result["response"] = data[5:]
    result["len_response"] = len(result["response"])
    return result


def parse_default_report(data):
    '''
    Tdebitres = packed record
    cmd   : byte;
    code  : array[0..3] of byte;
    //sign  : byte;                      //MULTIBANK
    rep   : array[0..218] of byte;
    end;   
    '''
    result = {}
    result["cmd"] = data[0]
    result["code"] = data[1:5]
    result["rep"] = data[5:len(data)]
    result["len"] = len(data)
    return result


def CLEAR_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB5"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    del data
    return response['code'].decode(), response
    
    
def ENABLE_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB6"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    del data
    return response['code'].decode(), response


def DISABLE_DUMP(Ser):
    sam = {}
    sam["cmd"] = b"\xB7"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    del data
    return response['code'].decode(), response


def READER_DUMP(Ser, etx_stop=False):
    sam = {}
    sam["cmd"] = b"\xB4"

    bal_value = sam["cmd"]
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    result = dict()
    result['raw'] = b''
    result['etx'] = etx_stop
    
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


def SYNC_TIME(Ser=Serial()):
    bal = {}
    bal["cmd"] = b"\xF0"
    st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    bal["time"] = st

    bal_value = bal["cmd"] + bal["time"].encode("utf-8")
    p_len, p = compose_request(len(bal_value), bal_value)

    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    result = parse_default_report(response["data"])
    
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
    result = parse_card_history_template(response['data'])
    
    del data
    del response
    return result["code"].decode('utf-8'), result


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



def GET_FEE_C2C(Ser, Flag=b"1"):
    sam = {}
    sam["cmd"] = b"\x85"
    st = datetime.datetime.now().strftime("%d%m%y%H%M%S")
    sam["date"] = st
        
    # SYNC TIME
    SYNC_TIME(Ser)

    bal_value = sam["cmd"] + sam["date"].encode("utf-8") + Flag
    p_len, p = compose_request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    result = parse_default_report(response["data"])
    
    del data
    del response
    return result["code"], result["rep"]



def SEND_APDU(Ser, slot, apdu):
    sam = {}
    sam["cmd"] = b"\xB0"
    sam["slot"] = format(slot, "X")[0:2].zfill(2)
    sam["len"] = format(len(apdu), "X")[0:2].zfill(2)
    # Define Max APDU Len on 255 / FF
    if len(apdu) > 255: sam["len"] = "FF"
    sam["apdu"] = apdu

    bal_value = sam["cmd"] + sam["slot"].encode("utf-8") + sam["len"].encode("utf-8") + sam["apdu"].encode('utf-8')
    p_len, p = compose_request(len(bal_value), bal_value)
    send_command(Ser, p)
    
    data = retrieve_rs232_data(Ser)
    response = parse_default_template(data)
    
    result = parse_default_report(response["data"])

    Len = ((response["len"][0] << 8)+response["len"][1])-5
    rep = ''
    for i in range(0, Len):
        rep = rep + chr(result["rep"][i])

    del data
    del response
    return result["code"], rep

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
            print('Receive', response)
            if response[:2] != STX: 
                print('Wrong STX', response[:2])
                response = STX + response
                print('Fix STX', response[:2])
            i_start = response.index(STX)
            i_end = response.index(ETX)
            if i_start:
                print('Remove', len(response[:i_start]))
                response = response[i_start:(i_end+len(ETX))]
            else:
                response = response[:(i_end+len(ETX))]
            print('Final Response', response)
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


DUMP_DURATION = 15

# Must Wait Within 60 Seconds
@func_set_timeout(DUMP_DURATION)
def retrieve_rs232_dump_data(Ser=Serial(), result={}):
    print('Dump Duration', DUMP_DURATION)
    while True:
        line = Ser.read_until(ETX)
        if line:
            result['raw'] += line
            # If Do This Below, The Data Might be trimmed/not actual
            if line.__contains__(ETX) or line.__contains__(ETX_DUMP):
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
    '4': 'Enable Dump',
    '5': 'Disable Dump',
    '6': 'Sync Time',    
    '7': 'Send APDU Command',    
    '8': 'Get Mandiri C2C Fee',    
    '9': 'Get Reader Dump',
    'X': 'Exit'
}

avail_command_text = (32*'+')+'\n'
avail_command_text += 'Pilih Mode Berikut : \n'
avail_command_text += (32*'+')+'\n'
avail_command_text += ( '1 : Card Balance\n')
avail_command_text += ( '2 : Card Disconnect\n')
avail_command_text += ( '3 : Card Log\n')
avail_command_text += ( '4 : Enable Dump\n')
avail_command_text += ( '5 : Disable Dump\n')
avail_command_text += ( '6 : Sync Time\n')
avail_command_text += ( '7 : Send APDU\n')
avail_command_text += ( '8 : Get Mandiri C2C Fee\n')
avail_command_text += ( '9 : Get Reader Dump\n')
avail_command_text += ( 'X : Exit\n')
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
                    elif mode == '4':
                        result, data = ENABLE_DUMP(COMPORT)
                    elif mode == '5':
                        result, data = DISABLE_DUMP(COMPORT)
                    elif mode == '6':
                        result, data = SYNC_TIME(COMPORT)
                    elif mode == '7':
                        while True:
                            target = input('Select Target Slot (1,2,3,4) Or 255 For Contactless) : \n')
                            if target in ['1', '2', '3', '4', '255']:
                                break
                        while True:
                            command = input('Insert Command To Be Executed : \n')
                            if len(command) >= 8:
                                break
                        result, data = SEND_APDU(COMPORT, int(target), command)
                    elif mode == '8':
                        while True:
                            target = input('Select Applet Type 0-Old, 1-New : \n')
                            if target in ['0', '1']:
                                break
                        result, data = GET_FEE_C2C(COMPORT, target.encode('utf-8'))
                    elif mode == '9':
                        while True:
                            target = input('0-Timer Stop or 1-ETX Stop : \n')
                            if target in ['0', '1']:
                                break
                        _reff = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        etx_stop = (target == '1')
                        result, data = READER_DUMP(COMPORT, etx_stop)
                        if result == SUCCESS_CODE:
                            out_file = log_to_file(content=data, filename=('simulator'+_reff))
                            print(out_file)
                    elif mode == '2':
                        result, data = CARD_DISCONNECT(COMPORT)
                    print('Result', data)
        else:
            print('Reader Cannot Be OPEN')
    except Exception as e:
        print('EXCP: ',e)
    finally:
        if COMPORT is not None and COMPORT.isOpen():
            COMPORT.close()
        do_exit('Finished')
