__author__ = 'fitrah.wahyudi.imam@gmail.com'
import time
import serial.tools.list_ports
from _tTools import _Helper
from . import _eSSPLib
import json
import logging
from _cConfig import _Common
import traceback
import binascii

LOGGER = logging.getLogger()

ERROR_COUNT = 0
ERROR_FILE = "error_print_nv200_event_"


class NV200_BILL_ACCEPTOR(object):
    def __init__(self, serial_port='COM3', restricted_denom=["1000", "2000"]):
        self.nv200 = _eSSPLib.eSSP(serial_port, 0, 10)
        self.serial_port = serial_port
        self.default_channel = [0,0,1,1,1,1,1,1]
        if len(restricted_denom) == 3 and restricted_denom == ["1000", "2000", "5000"]:
            self.default_channel = [0,0,0,1,1,1,1,1]
        if len(restricted_denom) == 4 and restricted_denom == ["1000", "2000", "5000", "10000"]:
            self.default_channel = [0,0,0,0,1,1,1,1]
        self.open_status = False


    def open(self):
        self.open_status = False
        try:
            result = self.nv200.sync()
            result = self.nv200.enable_higher_protocol()
            inhibits = self.nv200.easy_inhibit(self.default_channel)
            print('pyt: [NV200] Channel Setting', str(inhibits))   
            result = self.nv200.set_inhibits(inhibits, '0xFF')
            self.open_status =  True
        except Exception as e:
            LOGGER.warning(('NV200_Module', e))
        finally:
            return self.open_status


    def enable(self):
        try:
            if not self.check_active():
                result = self.open()
            result = self.nv200.bulb_on()
            result = self.nv200.enable()
            return True
        except Exception as e:
            LOGGER.warning(('NV200_Module', e))
            return False


    def disable(self):
        try:
            result = self.nv200.bulb_off()
            result = self.nv200.disable()
            return True
        except Exception as e:
            LOGGER.warning(('NV200_Module', e))
            return False
        
    
    def disable_only(self):
        try:
            # result = self.nv200.bulb_off()
            result = self.nv200.disable()
            return True
        except Exception as e:
            LOGGER.warning(('NV200_Module', e))
            return False


    def reject(self):
        try:
            result = self.nv200.bulb_off()
            result = self.nv200.reject_note()
            return True
        except Exception as e:
            LOGGER.warning(('NV200_Module', e))
            return False
    
    # def store(self):
    #     try:
    #         result = self.nv200.bulb_off()
    #         result = self.nv200.reject_note()
    #         return True
    #     except Exception as e:
    #         return False

    # def resync(self):
    #     result = self.nv200.sync()
    #     result = self.nv200.enable_higher_protocol()
    #     inhibits = self.nv200.easy_inhibit(self.channelMapping.values())
    #     result = self.nv200.set_inhibits(inhibits, '0xFF')
    #     result = self.nv200.configure_bezel('0x00', '0xF0', '0x00', '0x00', '0x00')
    #     result = self.nv200.bulb_on()
    #     result = self.nv200.enable()
    #     return True


    def check_active(self):
        result = '0x00'
        try:
            result = self.nv200.sync()            
        except Exception as e:
            # LOGGER.warning(('NV200_Module', e))
            pass
            # print("Serial for Sync Cmd Timeout")
        finally:
            return result == '0xf0'
    
    
    def reset_bill(self):
        # print ("Device Reset")
        self.nv200.reset()
        # Waiting Time Bill After Reset
        time.sleep(7)
        attempt = 0
        while True:
            portlist = serial.tools.list_ports.comports()
            attempt += 1
            for port in portlist:
                if port.device == self.serial_port:
                    if self.check_active():
                        print('pyt: [NV200]', 'Bill Re/Activated')
                        return True
            if attempt >= 5:
                return False
            time.sleep(1)
        

    def parse_reject_code(self, rejectCode):
        if rejectCode == '0x0':
            return "NOTE ACCEPTED"
        elif  rejectCode == '0x1':
            return "LENGTH FAIL"
        elif  rejectCode == '0x2':
            return "AVERAGE FAIL"
        elif  rejectCode == '0x3':
            return "COASTLINE FAIL"
        elif  rejectCode == '0x4':
            return "GRAPH FAIL"
        elif  rejectCode == '0x5':
            return "BURIED FAIL"
        elif  rejectCode == '0x6':
            return "CHANNEL INHIBIT"
        elif  rejectCode == '0x7':
            return "SECOND NOTE DETECTED"
        elif  rejectCode == '0x8':
            return "REJECT BY HOST"
        elif  rejectCode == '0x9':
            return "CROSS CHANNEL DETECTED"
        elif  rejectCode == '0xa':
            return "REAR SENSOR ERROR"
        elif  rejectCode == '0xb':
            return "NOTE TO LONG"
        elif  rejectCode == '0xc':
            return "DISABLED BY HOST"
        elif  rejectCode == '0xd':
            return "SLOW MECH"
        elif  rejectCode == '0xe':
            return "STRIM ATTEMPT"
        elif  rejectCode == '0xf':
            return "FRAUD CHANNEL"
        elif  rejectCode == '0x10':
            return "NO NOTES DETECTED"
        elif  rejectCode == '0x11':
            return "PEAK DETECT FAIL"
        elif  rejectCode == '0x12':
            return "TWISTED NOTE REJECT"
        elif  rejectCode == '0x13':
            return "ESCROW TIME-OUT"
        elif  rejectCode == '0x14':
            return "BARCODE SCAN FAIL"
        elif  rejectCode == '0x15':
            return "NO CAM ACTIVATE"
        elif  rejectCode == '0x16':
            return "SLOT FAIL 1"
        elif  rejectCode == '0x17':
            return "SLOT FAIL 2"
        elif  rejectCode == '0x18':
            return "LENS OVERSAMPLE"
        elif  rejectCode == '0x19':
            return "WIDTH DETECTION FAIL"
        elif  rejectCode == '0x1a':
            return "SHORT NOTE DETECTED"
        elif  rejectCode == '0x1b':
            return "PAYOUT NOTE"
        elif  rejectCode == '0x1c':
            return "DOUBLE NOTE DETECTED"
        elif  rejectCode == '0x1d':
            return "UNABLE TO STACK"
        else:
            return "INVALID NOTE: " + rejectCode


    def parse_value(self, channel):
        if channel == 1:
            return 1000
        elif channel == 2:
            return 2000
        elif channel == 3:
            return 5000
        elif channel == 4:
            return 10000
        elif channel == 5:
            return 20000
        elif channel == 6:
            return 50000
        elif channel == 7:
            return 100000
        else:
            return 0


    def parse_event(self, poll_data):
        event = []
        event_data = []
        event_data.append(poll_data)
        if len(poll_data[1]) == 2:
            event.append('0xff')
            event.append(poll_data[1][0])
            event.append(poll_data[1][1])
        else:
            event = poll_data
            
        if event[1] == '0xf1':
            event_data.append("Slave reset")
        elif  event[1] == '0xef':
            event_data.append("Reading Note")
        elif  event[1] == '0xee':
            # Note in escrow, amount: 2000.00  IDR
            note_value = self.parse_value(event[2])
            event_data.append("Note in escrow, amount: " + str(note_value) + ".00  IDR")
            event_data.append(note_value)
            return event_data
        elif  event[1] == '0xed':
            event_data.append("Rejecting")
        elif  event[1] == '0xec':
            event_data.append("Rejected")
        elif  event[1] == '0xcc':
            event_data.append("Stacking")
        elif  event[1] == '0xeb':
            event_data.append("Note stacked")
        elif  event[1] == '0xe9':
            event_data.append("Unsafe Jam")
        elif  event[1] == '0xe8':
            event_data.append("Disabled")
        elif  event[1] == '0xe7':
            event_data.append("Stacker full")
        elif  event[1] == '0xe6':
            event_data.append("Fraud Attempt")
        elif  event[1] == '0xe1':
            event_data.append("Note Cleared From Front")
        elif  event[1] == '0xe2':
            event_data.append("Note Cleared Into Cashbox")
        elif  event[1] == '0xe3':
            event_data.append("Cashbox Removed")
        elif  event[1] == '0xe4':
            event_data.append("Cashbox Replaced")
        elif  event[1] == '0xe5':
            event_data.append("Barcode Ticket Validated")
        elif  event[1] == '0xd1':
            event_data.append("Barcode Ticket Ack")
        elif  event[1] == '0xe0':
            event_data.append("Note Path Open")
        elif  event[1] == '0xb5':
            event_data.append("Channel Disable")
        elif  event[1] == '0xb6':
            event_data.append("Initialising")
        elif  event[1] == '0xa5':
            event_data.append("Ticket Printing")
        elif  event[1] == '0xa6':
            event_data.append("Ticket Printed")
        elif  event[1] == '0xa8':
            event_data.append("Ticket Printing Error")
        elif  event[1] == '0xae':
            event_data.append("Print Halted")
        elif  event[1] == '0xad':
            event_data.append("Ticket In Bezel")
        elif  event[1] == '0xaf':
            event_data.append("Printed To Cashbox")
        else:
            # print('pyt: [NV200] Unknown Event: ')
            event_data.append("Unknown Event: " + str(event))
        event_data.append(0)
        return event_data

    def listen_poll(self):
        while True:
            poll = self.nv200.poll()      
            if len(poll) > 1:     
                event = self.parse_event(poll)
                if poll[1] == '0xed' or poll[1] == '0xec':
                    last_reject = self.nv200.last_reject()
                    event.append(self.parse_reject_code(last_reject))
                else:
                    event.append('')
                if _Common.BILL_LIBRARY_DEBUG is True:
                    try:
                        print('pyt: [NV200] Event :', str(event))
                    except Exception as e:
                        traceback.format_exc()
                        continue
                return event
            time.sleep(0.5)

NV200 = None

# NV = {
#     "SET": "601",
#     "RECEIVE": "602",
#     "STORE": "603",
#     "REJECT": "604",
#     "STOP": "605",
#     # "STATUS": "504",
#     "RESET": "606",
#     "KEY_RECEIVED": "Note in escrow, amount:",
#     "PORT": BILL_PORT,
#     # TODO Must Define Below Property
#     "CODE_JAM": None,
#     "TIMEOUT_BAD_NOTES": 'Invalid note',
#     "UNKNOWN_ITEM": None ,
#     "LOOP_DELAY": 2,
#     "KEY_STORED": 'Note stacked',
#     "MAX_STORE_ATTEMPT": 4,
#     "KEY_BOX_FULL": 'Stacker full',
#     "DIRECT_MODULE": _Common.BILL_NATIVE_MODULE
# }

# 601 = http://localhost:9000/Service/GET?type=json&cmd=601&param=COM16 <STAT>: 200 
# <RESP>: {'Response': '', 'Command': '601', 'ErrorDesc': 'Sukses', 'Parameter': 'COM16', 'Result': '0000'}

# 602 = http://localhost:9000/Service/GET?type=json&cmd=602&param=0 <STAT>: 200 
# <RESP>: {'Response': 'Note in escrow, amount: 50000.00  IDR\r\n', 'Command': '602', 'ErrorDesc': 'Sukses', 'Parameter': '0', 'Result': '0000'}

# 603 = http://localhost:9000/Service/GET?type=json&cmd=603&param=0 <STAT>: 200 
# <RESP>: {'Response': 'Note stacked\r\n', 'Command': '603', 'ErrorDesc': 'Sukses', 'Parameter': '0', 'Result': '0000'}

# 604 = http://localhost:9000/Service/GET?type=json&cmd=604&param=0 <STAT>: 200 
# <RESP>: {'Parameter': '0', 'Response': 'Host rejected note\r\n', 'ErrorDesc': 'Sukses', 'Result': '0000', 'Command': '604'}

# 605 = http://localhost:9000/Service/GET?type=json&cmd=605&param=0 <STAT>: 200 
# <RESP>: {'Parameter': '0', 'Response': '', 'ErrorDesc': 'Sukses', 'Result': '0000', 'Command': '605'}

LOOP_ATTEMPT = 0
# Set Max Waiting Event Listen From NV into 120 seconds
MAX_LOOP_ATTEMPT = 90


def send_command(param=None, config=[], restricted=[]):
    global NV200, LOOP_ATTEMPT
    try:
        # if _Helper.empty(param) or _Helper.empty(config):
        #     return -1, ""
        if NV200 is None:
            NV200 = NV200_BILL_ACCEPTOR(serial_port=config['PORT'], restricted_denom=restricted)
        args = param.split('|')
        command = args[0]
        param = "0"
        if len(args[1:]) > 0:
            param = "|".join(args[1:])
        # LOGGER.debug((command, param, config))
        # Define Command
        if command == config['SET']:
            result = NV200.open()
            if result is True:
                return 0, "0000"
            else:
                NV200 = None
                return -1, ""
        elif command == config['RECEIVE']:
            LOOP_ATTEMPT = 0
            action = NV200.check_active()
            if action is True:
                action = NV200.enable()
                while True:
                    pool = NV200.listen_poll()
                    LOOP_ATTEMPT += 1
                    if config['KEY_RECEIVED'] in pool[1]:
                        return 0, pool[1]
                    if config['KEY_BOX_FULL'] in pool[1]:
                        NV200.disable()
                        return -1, pool[1]
                        break
                    if config['CODE_JAM'] in pool[1]:
                        NV200.disable_only()
                        return -1, pool[1]
                        break
                    if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                        break
                    time.sleep(1)
                return -1, ""
            else:
                return -1, ""
        elif command == config['STORE']:
            LOOP_ATTEMPT = 0
            while True:
                pool = NV200.listen_poll()
                LOOP_ATTEMPT += 1
                if config['KEY_STORED'] in pool[1]:
                    return 0, pool[1]
                    break
                if config['KEY_BOX_FULL'] in pool[1]:
                    return -1, pool[1]
                    break
                if config['CODE_JAM'] in pool[1]:
                    NV200.disable_only()
                    return -1, pool[1]
                    break
                if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                    break
                time.sleep(1)
            return -1, ""
        elif command == config['REJECT']:
            action = NV200.reject()
            LOOP_ATTEMPT = 0
            while True:
                pool = NV200.listen_poll()
                LOOP_ATTEMPT += 1
                if "Rejected" in pool[1]:
                    return 0, pool[1]
                    break
                if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                    break
                time.sleep(1)
            return -1, ""
        elif command == config['RESET']:
            action = NV200.reset_bill()
            if action is True:
                # NV200.open()
                return 0, "Bill Reset"
            else:
                return -1, ""
        elif command == config['STOP']:
            LOOP_ATTEMPT = MAX_LOOP_ATTEMPT
            action = NV200.disable()
            if action is True:
                # while True:
                #     # pool = NV200.listen_poll()
                #     LOOP_ATTEMPT += 1
                #     # if config['KEY_RECEIVED'] in pool[1]:
                #     #     return 0, pool[1]
                #     # if config['KEY_BOX_FULL'] in pool[1]:
                #     #     return 0, pool[1]
                #     #     break
                #     if LOOP_ATTEMPT >= 3:
                #         break
                #     time.sleep(1)
                return 0, "Bill Stop"
            else:
                return -1, ""
        else:
            return -1, ""
    except Exception as e:
        error_string = traceback.format_exc()
        LOGGER.warning((e))
        LOGGER.debug(error_string)
        return -99, str(e)
    
    
