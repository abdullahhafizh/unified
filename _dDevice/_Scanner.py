__author__ = "wahyudi@multidaya.id"

from PyQt5.QtCore import QObject, pyqtSignal
from _dDevice import _HID
from _cConfig import _Common
import sys
from _tTools import _Helper
import logging
import time
import keyboard


LOGGER = logging.getLogger()


class ScannerSignalHandler(QObject):
    __qualname__ = 'ScannerSignalHandler'
    SIGNAL_READ_SCANNER = pyqtSignal(str)

SCANNER_SIGNDLER = ScannerSignalHandler()
#from hid import AccessDeniedError, PathNotFoundError

# The scanner VID/PID change if neessary
VENDORID = _Common.SCANNER_VID
PRODUCTID = _Common.SCANNER_PID

class Scanner(object):
    """ this library is platform-independent but depends on the backend HID.py"""
    def __init__(self, handle):
        """handle is an HIDDevice object """
        self.handle = handle
        #self.overlapped = overlapped

    def read(self):
        return self.handle.read(80)

    def getBarcode(self):
        readresult = self.read()
        #print readresult
        length = readresult[0]
        if (length == 0):
            return
        reportdata = readresult[1]
        reporttype = reportdata[0]
        #print "Number of bytes read: ", length
        #print "Buffer: "
        #for x in range(length):
        #    print(reportdata[x]),
        #print('\n')

        barcode = ""
        for x in range(5, length):
            if (reportdata[x] == 0):
                break
            barcode += chr(reportdata[x])
        return barcode
        #self.printStatus()

    def simply_read(self):
        while 1:
            barcode = sys.stdin.readline().rstrip().replace(' ', '')
            # f = urllib.urlopen("http://www.google.com/search?%s" % urllib.urlencode( {'q':line} ))
            return barcode 
        
def get_scanners():
    """Returns a collection of barcode scanner objects."""
    targets = _HID.OpenDevices(VENDORID, PRODUCTID)
    return [Scanner(scanner) for scanner in targets]


BREAK_EVENT = ['enter']
SKIP_EVENT = ['tab', 'alt', 'menu', 'shift', 'ctrl', 'delete', 'backspace', 'right ctrl', 'left ctrl', 'esc']
MIN_READ_LEN = 15
EVENT_RESULT = ''
SCANNER_ACTIVE = False

    
def reset_state():
    global EVENT_RESULT, SCANNER_ACTIVE
    EVENT_RESULT = ''
    SCANNER_ACTIVE = False
    
    
def on_key_event(event):
    global EVENT_RESULT
    if event.name in BREAK_EVENT and SCANNER_ACTIVE is True:
        SCANNER_SIGNDLER.SIGNAL_READ_SCANNER.emit('SCANNER|'+EVENT_RESULT)
        reset_state()
        return
    if len(event.name) == 1:
        EVENT_RESULT += event.name
        

def start_simple_read_scanner():
    _Helper.get_thread().apply_async(simple_read_scanner)


def simple_read_scanner():
    global SCANNER_ACTIVE
    SCANNER_ACTIVE = True
    keyboard.on_press(on_key_event)
