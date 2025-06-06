__author__ = 'wahyudi@multidaya.id'

import time
import serial.tools.list_ports
from _tTools import _Helper
from . import _eSSPLib
import logging
from _cConfig import _Common
import traceback

LOGGER = logging.getLogger()

ERROR_COUNT = 0
ERROR_FILE = "error_print_nv200_event_"
SOCKET_TIMEOUT = _Common.BILL_SOCKET_TIMEOUT


# COMMAND_MODE as state for async hold trigger
COMMAND_MODE = ''


class NV200_BILL_ACCEPTOR(object):
    global COMMAND_MODE
    
    def __init__(self, serial_port='COM3', restricted_denom=["1000", "2000"]):
        self.nv200 = _eSSPLib.eSSP(
            serialport=serial_port, 
            eSSPId=0, 
            timeout=SOCKET_TIMEOUT,
            )
        self.serial_port = serial_port
        self.default_channel = [0,0,1,1,1,1,1,1]
        if len(restricted_denom) == 3 and restricted_denom == ["1000", "2000", "5000"]:
            self.default_channel = [0,0,0,1,1,1,1,1]
        if len(restricted_denom) == 4 and restricted_denom == ["1000", "2000", "5000", "10000"]:
            self.default_channel = [0,0,0,0,1,1,1,1]
        self.open_status = False
        self.known_notes = [0, 1000, 2000, 5000, 10000, 20000, 50000, 100000]

    def open(self):
        self.open_status = False
        try:
            result = self.nv200.sync()
            result = self.nv200.enable_higher_protocol()
            inhibits = self.nv200.easy_inhibit(self.default_channel)
            result = self.nv200.set_inhibits(inhibits, '0xFF')
            if _Common.BILL_LIBRARY_DEBUG is True:
                # print('pyt: [NV200] Channel Setting', str(inhibits), str(result))   
                LOGGER.debug(('[NV200] Channel Setting', str(inhibits), str(result)))
            self.open_status =  True
        except Exception as e:
            LOGGER.warning(('[NV200]', e))
        finally:
            return self.open_status

    def enable(self):
        try:
            if not self.check_active():
                result = self.open()
            result = self.nv200.enable()
            result = self.nv200.bulb_on()
            if _Common.BILL_LIBRARY_DEBUG is True:
                # print('pyt: [NV200] Enabling', str(result), str(COMMAND_MODE))   
                LOGGER.debug(('[NV200] Enabling', str(result), str(COMMAND_MODE)))
            return True
        except Exception as e:
            LOGGER.warning(('[NV200]', e))
            return False

    def disable(self):
        try:
            result = self.nv200.disable()
            result = self.nv200.bulb_off()
            if _Common.BILL_LIBRARY_DEBUG is True:
                # print('pyt: [NV200] Disabling', str(result))   
                LOGGER.debug(('[NV200] Disabling', str(result)))
            return True
        except Exception as e:
            LOGGER.warning(('[NV200]', e))
            return False
        
    def disable_only(self):
        try:
            # result = self.nv200.bulb_off()
            result = self.nv200.disable()
            if _Common.BILL_LIBRARY_DEBUG is True:
                # print('pyt: [NV200] Disabling', str(result))   
                LOGGER.debug(('[NV200] Disabling', str(result)))
            return True
        except Exception as e:
            LOGGER.warning(('[NV200]', e))
            return False

    def reject(self):
        try:
            # Switch REJECT without response required
            result = self.nv200.reject_note_no_response()
            result = self.nv200.bulb_off()
            if _Common.BILL_LIBRARY_DEBUG is True:
                # print('pyt: [NV200] Rejecting', str(result))   
                LOGGER.debug(('[NV200] Rejecting', str(result)))
            return True
        except Exception as e:
            LOGGER.warning(('[NV200', e))
            return False
    
    def disconnect(self):
        result = self.nv200.release()
        del self.nv200
        self.nv200 = None
        if _Common.BILL_LIBRARY_DEBUG is True:
            # print('pyt: [NV200] Releasing', str(result))   
            LOGGER.debug(('[NV200] Releasing', str(result)))
        return result
    
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
            if _Common.BILL_LIBRARY_DEBUG is True: 
                # print('pyt: [NV200] Active Check', str(result))
                LOGGER.debug(('[NV200] Active Check', str(result)))
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
                        if _Common.BILL_LIBRARY_DEBUG is True:
                            # print('pyt: [NV200] Resetting', 'Bill Re/Activated')
                            LOGGER.debug(('[NV200] Resetting', 'Bill Re/Activated'))
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
        try: 
            return self.known_notes[channel] 
        except:
            return 0
        
    def async_hold(self):
        _Helper.get_thread().apply_async(self.hold)

    def parse_event(self, poll_data):

        event = []
        event_data = []
        event_data.append(poll_data)

        # Serializing Poll Event
        if len(poll_data[1]) == 2 and type(poll_data[1]) == list and len(poll_data) == 3:
            # ['0xf0', ['0xef', 4], '0x4']
            # Length 3 For Normal Notes Detection
            event.append('0xff')
            event.append(poll_data[1][0])
            event.append(poll_data[1][1])
        else:
            #Sample Anomaly
            # ['0xf0', ['0xef', 4], '0x4', '0xed', '0xec', '0xe8']"
            # ['0xf0', '0xed', '0xec', ['0xef', 0], '0x0', '0xed', '0xec', '0xe8'] 
            # ['0xf0', '0xed', '0xec', ['0xef', 0], '0x0', ['0xef', 4], '0x4', '0xed']
            # ['0xf0', '0xeb', '0xe8']" -> Event When Notes Automatically Stack After Received
            # ReCheck Pattern Loop Response
            # if len(event) == 0:
            #     for p in poll_data:
            #         if type(p) != list:
            #             # Why must less than 4, just remove all the things
            #             poll_data.remove(p)
            #             continue
            #         else:
            #             if len(p) == 2:
            #                 event.append('0xff')
            #                 event.append(p[0])
            #                 event.append(p[1])
            #                 break     

            # If Receive Notes, But Its Rejected and Disabled
            if COMMAND_MODE == 'receive':
                if poll_data[-2] in ['0xed', '0xec']:
                    event.append(poll_data[0])
                    event.append(poll_data[-2])

            # Last Parsing, Get Last Poll as Status Event
            if len(event) == 0:
                event.append(poll_data[0])
                event.append(poll_data[-1])

        # Do Parse Event
        if event[1] == '0xf1':
            event_data.append("Slave reset")
        elif  event[1] == '0xef':
            if event[2] == '0x0':
                event_data.append("Reading Note")
            else:
                # Do Return The Bite Value And Trigger Hold in Other Thread
                note_value = self.parse_value(event[2])
                event_data.append("Note in escrow, amount: " + str(note_value) + ".00  IDR")
                event_data.append(note_value)
                # Remove Trigger Async Hold Here
                # if COMMAND_MODE == 'hold': self.async_hold()
                return event_data
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

    def get_event(self, caller):
        
        poll = []
        while len(poll) == 0:
            poll = self.nv200.poll()

        # ('[NV200] Poll Event', '', '603', "['0xf0', '0xeb', '0xe8']", "[['0xf0', '0xeb', '0xe8'], 'Disabled', 0, '']")
        # ('[NV200] Poll Event', '', '602', "['0xf0', ['0xef', 4], '0x4']", "[['0xf0', ['0xef', 4], '0x4'], 'Reading Note', 0, '']")
        event = []
        
        if len(poll) > 1:
            if len(poll[1]) == 2 and type(poll[1]) == list:
                # On Reading Notes
                if poll[1][0] == '0xef':
                    # This Cause Notes On Reject Will be treated as Normal Reading Notes
                    # Must be validated with caller/COMMAND MODE
                    # Extra Handling NV For Reject Activity
                    if COMMAND_MODE == 'reject' or caller == '604':
                        if _Common.BILL_LIBRARY_DEBUG is True:
                            # print('pyt: [NV200] Anomaly Response Reading Note After Reject Activity', str(poll))
                            LOGGER.debug(('[NV200] Anomaly Response Reading Note After Reject Activity', str(poll)))
                        return event
                    elif 0 < poll[1][1] < len(self.known_notes):
                        event = self.parse_event(poll)
                        # if COMMAND_MODE == 'hold':
                        #     self.async_hold()
                # On Stacking Notes
                elif poll[1][0] == '0xee':
                    event = self.parse_event(poll)
                    # return event
            else:
                event = self.parse_event(poll)
                if len(poll) > 1:
                    if poll[1] in ['0xed', '0xec']:
                        last_reject = self.nv200.last_reject()
                        event.append(self.parse_reject_code(last_reject))

        event.append(COMMAND_MODE)
        # 602 Will assumpt empty event so it will be retriggered
            
        if _Common.BILL_LIBRARY_DEBUG is True:
            try:
                LOGGER.debug(('[NV200] Poll Event', str(COMMAND_MODE), str(caller), str(poll), str(event)))
            except Exception as e:
                traceback.format_exc()
            # Ensure This Will Break Here
        return event
            
    def hold(self):
        while True:
            if COMMAND_MODE == 'hold':
                if _Common.BILL_LIBRARY_DEBUG is True:
                    # print('pyt: [NV200] Trigger Hold Notes')
                    LOGGER.debug(('[NV200] Trigger Hold Notes'))
                self.nv200.hold()
            else:
                break
            time.sleep(LOOP_INTERVAL)    
    
    def accept(self):
        self.nv200.accept_note()
    
    def poll(self):
        self.nv200.poll()

    def poll_once(self):
        poll = self.nv200.poll()
        event = self.parse_event(poll)
        event.append("")
        return event

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
MAX_LOOP_ATTEMPT = 30

# Set Loop Interval For The Event Polling
# Must use If Converter + Wire Grounding To Have Stable Connection
LOOP_INTERVAL = .25

MAX_STORE_ATTEMPT = 5 * (1/LOOP_INTERVAL)


def send_command(param=None, config=[], restricted=[], hold_note=False):
    global NV200, LOOP_ATTEMPT, COMMAND_MODE, MAX_LOOP_ATTEMPT
    try:
        if NV200 is None:
            NV200 = NV200_BILL_ACCEPTOR(
                serial_port=config['PORT'], 
                restricted_denom=restricted
                )
        args = param.split('|')
        command = args[0]
        param = "0"
        if len(args[1:]) > 0:
            param = "|".join(args[1:])
        # LOGGER.debug((command, param, config))
        MAX_LOOP_ATTEMPT = config['MAX_EXECUTION_TIME'] * (1/LOOP_INTERVAL)
        # Define Command
        if command == config['SET']:
            result = NV200.open()
            if result is True:
                return 0, "0000"
            NV200 = None
        #===
        elif command == config['RECEIVE']:
            LOOP_ATTEMPT = 0
            action = NV200.check_active()
            if action is True:
                COMMAND_MODE = 'receive'
                if hold_note: COMMAND_MODE = 'hold'
                NV200.enable()
                while True:
                    event = NV200.get_event(command)
                    if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                        return -1, 'Bill Receive Max Attempt Reached'
                    LOOP_ATTEMPT += 1
                    if len(event) == 1:
                        time.sleep(LOOP_INTERVAL)
                        continue
                    if 'reject' in str(event[1]).lower():
                        # return -1, event[1]
                        # Pass the Reject Event, Just Continue
                        continue
                    if config['KEY_RECEIVED'] in event[1]:
                        time.sleep(LOOP_INTERVAL)
                        if COMMAND_MODE == 'hold':
                            # Trigger Async Hold Here
                            NV200.async_hold()
                        elif COMMAND_MODE == 'receive':
                            NV200.accept()
                            # NV200.poll()
                        return 0, event[1]
                    if config['KEY_BOX_FULL'] in event[1]:
                        NV200.disable()
                        return -1, event[1]
                    if config['CODE_JAM'] in event[1]:
                        NV200.disable_only()
                        return -1, event[1]
                    time.sleep(LOOP_INTERVAL)
        #===
        elif command == config['STORE']:
            # Enhanced on 20250113
            # Stop The Trigger By change the state
            COMMAND_MODE = 'store'
            # Anomaly Handled Here
            if NV200 is None:
                return -1, "Bill already stoped"
            
            LOOP_ATTEMPT = 0
            while True:
                event = NV200.get_event(command)
                if LOOP_ATTEMPT >= MAX_STORE_ATTEMPT: 
                    return -1, "Noted cannot stacked on Max Attempt"
                LOOP_ATTEMPT += 1
                if len(event) == 1:
                    time.sleep(LOOP_INTERVAL)
                    continue
                if config['KEY_RECEIVED'] in event[1] or config['KEY_STORED'] in event[1]:
                    return 0, event[1]
                if config['KEY_BOX_FULL'] in event[1]:
                    return -1, event[1]
                if config['CODE_JAM'] in event[1]:
                    NV200.disable_only()
                    return -1, event[1]
                time.sleep(LOOP_INTERVAL)
            return 0, "Noted stacked"
        #===
        elif command == config['REJECT']:
            LOOP_ATTEMPT = 0
            COMMAND_MODE = 'reject'
            NV200.reject()
            while True:
                event = NV200.get_event(command)
                LOOP_ATTEMPT += 1
                if LOOP_ATTEMPT >= 3:
                    break
                if len(event) > 1 and  "Rejected" in event[1]:
                    break
                time.sleep(.25)
            NV200.disable()
            return 0, "Note Rejected"
        #===
        elif command == config['RESET']:
            COMMAND_MODE = 'reset'
            action = NV200.reset_bill()
            if action is True:
                # Add Open to Re-enable Bill
                NV200.open()
                return 0, "Bill Reset"
        #===
        elif command == config['STOP']:
            COMMAND_MODE = 'stop'
            action = NV200.disable()
            if action is True:
                # Must Do Get Poll To Reset Cashbox Status
                attempt = 0
                while True:
                    attempt += 1
                    event = NV200.get_event(command)
                    # Wait 5 Seconds
                    if attempt >= (5*(1/LOOP_INTERVAL)): 
                        break
                    time.sleep(LOOP_INTERVAL)
                
                # Release & Flush the NV200 Object
                NV200.disconnect()
                del NV200
                NV200 = None
                return 0, "Bill Stop"
        # Default Response
        return -1, ""
    except Exception as e:
        error_string = traceback.format_exc()
        LOGGER.warning((e))
        LOGGER.debug(error_string)
        return -99, str(e)
    
    
