__author__ = 'wahyudi@multidaya.id'

from serial import Serial
from enum import Enum
import time
from binascii import hexlify, unhexlify
import datetime
from threading import Event
from _mModule import _CPrepaidLog as LOG


STATUS_CODE = {
    "0000": "Normal status",                                                                                    # N/A
    "0001": "Notes at input slot (applicable to bundle acceptance module)",                                     # Warning: Take away the notes from the input slot.
    "0002": "The configuration parameters read for the NV are inconsistent with the specified parameters.",     # Warning: Reconfigure the parameters.
    "0003": "There is no note in the transport",                                                                # Warning: Insert notes.
    "0004": "The banknote acceptance module is in wrong status when getting note information",                  # Warning: Insert notes and get note information when the BA-08 banknote acceptance module is in waiting status after recovering notes.
    "0005": "Notes at exit slot",                                                                               # Warning: take away the notes from the exit slot.
    "0006": "All notes are rejected (applicable to bundle acceptance module)",                                  # Warning: Check the validation part for fault, or check to see whether the notes are the currencies supported by algorithm.
    "0007": "Failed to get note information from the upper layer",                                              # Warning: Failed to get note information from the upper layer after completion of recovering notes.
    "0008": "Notes are rejected from the exit slot when jams are cleared",                                      # Pay attention to the account of such note at upper layer.
    "0009": "Notes enter the cassette when jams are cleared",                                                   # Pay attention to the account of such note at upper layer.
    "02xx": "Unidentified notes",                                                                               # Warning: xx is the reason for rejecting notes.
    "3000": "The main motor fails to rotate clockwise",                                                         # Error: Check the main motor or sensor.
    "3001": "The main motor fails to rotate counterclockwise",                                                  # Error: Check the main motor or sensor.
    "3002": "The pressure motor fails to rotate clockwise",                                                     # Error: Check the pressure motor or sensor.
    "3003": "The pressure motor fails to rotate counterclockwise",                                              # Error: Check the pressure motor or sensor.
    "3004": "The alignment motor fails to rotate clockwise",                                                    # Error: Check the alignment motor or sensor.
    "3005": "The alignment motor fails to rotate counterclockwise",                                             # Error: Check the alignment motor or sensor.
    "3006": "Failed to open the clamping tension cushion",                                                      # Error: Check the tension cushion or the sensor of the entrance connecting rod.
    "3007": "Failed to release the clamping tension cushion",                                                   # Error: Check the tension cushion or the sensor of the entrance connecting rod.
    "3100": "Cassette full",                                                                                    # Error: Change the cassette.
    "3101": "No cassette is tested",                                                                            # Error: Insert and lock the cassette.
    "3102": "The NV is not calibrated",                                                                         # Error: Calibrate the NV.
    "3103": "The NV is not configured",                                                                         # Error: Configure the NV.
    "3104": "Validation times out",                                                                             # Error: Check the NV.
    "3200": "The system is in wrong status when preparing for inserting notes",                                 # Error: Check the BA-08.
    "3201": "There is note in the transport when preparing for inserting notes",                                # Error: Check the transport sensor and clear the transport.
    "3202": "The cassette is full when preparing for inserting notes",                                          # Error: Check the BA-08 and change the cassette.
    "3203": "The clamping solenoid valve is abnormal when preparing for inserting notes",                       # Check the clamping solenoid valve or U-shaped sensor.
    "3204": "The alignment motor fails to return to the initial position",                                      # Check the alignment motor or detect the in-place U-shaped sensor.
    "4000": "The cassette does not exist when initialization",                                                  # Error: Check the cassette or its in-place sensor.
    "4001": "There is not note in the transport when initialization",                                           # Error: Clear the transport and check the transport sensor.
    "4002": "The cassette has detection error when initialization",                                             # Error: Sensor error or pressure motor error.
    "4003": "The pressure solenoid valve has attracting error when initialization",                             # Error: Check the solenoid valve.
    "4004": "The pressure solenoid valve has release error when initialization",                                # Error: Check the solenoid valve.
    "4005": "The alignment motor or alignment right sensor has error when initialization.",                     # Error: Check the alignment motor or alignment sensor.
    "4006": "The alignment motor or alignment left sensor has error when initialization.",                      # Error: Check the alignment motor or alignment sensor.
    "4007": "The sensor at feeding port is blocked when initialization",                                        # Error: The sensor at feeding port is blocked.
    "8000": "The alignment is not in original position when inserting notes",                                   # Error: Check to see whether the alignment motor is in place.
    "8001": "The alignment is not in original position when inserting notes",                                   # Error: Check the alignment stopper.
    "8002": "Scanning times out",                                                                               # Error: Check the main motor or dial.
    "8003": "Failed to retract the pressure bar of the cassette",                                               # Error: Check the pressure bar or pressure motor motion system.
    "8004": "Pushing out the pressure bar of the cassette fails.",                                              # Error: Check the pressure bar or cassette motion component.
    "8005": "Failed to insert notes into the cassette transport.",                                              # Error: Check the cassette transport and anti-phishing component.
    "8006": "Notes are rejected from the cassette transport when pressing notes.",                              # Error: Check the transport sensor or check to see whether there is suspicious transaction.
    "8007": "Cassette full",                                                                                    # Error: Cassette full.
    "8008": "Feeding timeout",                                                                                  # Error: Check to see whether the feeding part is jammed.
    "8009": "Note jams in transport",                                                                           # Error: Clear notes in the transport and check the sensor.
    "8010": "Main transport sensor abnormal",                                                                   # Error: Check the main transport sensor and fasten the upper cover.
    "8011": "The cassette has error, and the returning notes fails.",                                           # Error: After the pressing failure, rejecting notes in the upper transport fails.
    "8012": "After the feeding error, the cassette is full",                                                    # Error: After the feeding failure, the pressure bar detects that the cassette is full.
    "8013": "After the feeding failure, pushing the pressure plate fails.",                                     # Error: After the feeding failure, pushing the pressure plate fails.
    "8014": "After the feeding failure, notes are rejected from the cassette transport when pressing notes.",   # Error: After the feeding failure, the sensor is abnormal when pressing notes.
    "8015": "After the feeding failure, retracting the pressure bar of the cassette fails.",                    # Error: After the feeding failure, retracting the pressure plate fails.
    "8016": "After the pressing failure, notes are rejected.",                                                  # Error: After the pressing failure, notes are normally rejected.
    "9000": "Command frame error",                                                                              # Error: Confirm the operating state of the hardware, command format and command check information.
    "9001": "Parameter error",                                                                                  # Error: change to correct command parameter. See Chapter 6 for details.
    "9002": "Checking error",                                                                                   # Error: change to correct command parameter. See Chapter 6 for details.
    "9003": "Unsupported command",                                                                              # ...
}

DENOM_LIST={
    "2A": "1000",
    "2B": "2000",
    "2C": "5000",
    "A1": "10000",
    "A2": "20000",
    "A3": "50000",
    "A4": "100000",
    "92": "20000",

}

class PROTO_FUNC(Enum):
    STX = b"\x10\x02" # Start of a data packet
    EXT = b"\x10\x03" # End of a data packet
    EOT = b"\x10\x04" # Cancellation of a command
    ENQ = b"\x10\x05" # Confirmation response
    ACK = b"\x10\x06" # Receiving response
    DLE = b"\x10\x10" # Start of a control word
    NAK = b"\x10\x15" # Error response
    BOT = b"\x10\x13" # Busy response
    FOT = b"\x10\x11" # Idle response, actively idle response only when feeding notes.


class CMD(Enum):
    QUERY_STATUS = b"A"
    INITIALIZE = b"T"
    CLEAR_NOTES = b"B"
    NOTE_INFO = b"Q"
    DEPOSIT_PREP = b"V"
    STOP_RECEIVE = b"E"
    DEPOSIT_CONFIRM = b"M"
    DEPOSIT_CANCEL = b"C"
    R_DENOM = b"P"
    W_DENOM = b"W"
    R_AFTER_W_DENOM = b"K"
    QUERY_VERSION = b"r"


class GRGReponseData():
    def __init__(self, data=b""):
        if len(data) < 4:
            raise Exception("Insufficent length")            
        self.rawData = data
        self.length = data[2] + (data[3] * 255)
        data = data[4:]

        if len(data) < self.length:
            raise Exception("Insufficent data length")            

        self.cmdCode = data[0]
        self.statusWord = data[1]
        self.statusCode = bytearray(data[2:4])
        self.statusCode.reverse()
        self.sensorStatus = data[4:6]
        self.statusModule = data[6:8]

        self.state = self.statusModule[0] & 15
        self.isNormal = self.state == 0
        self.isBusy = self.state == 1
        self.isError = self.state == 2
        self.isReceiving = self.state == 3
        self.isReceived = self.state == 8

        if self.statusWord != b'e':
            self.responseData = data[8:self.length]
        else:
            self.responseData = b""


    def toString(self):
        code = hexlify(self.statusCode).decode("utf-8")
        codeMessage = self.getStatusMessage(code)
        try:   
            cmdDat = str(CMD(self.cmdCode.to_bytes(1, byteorder="big")))
        except Exception:
            cmdDat = str(self.cmdCode)

        strData = "Len["+str(self.length)+"], "+cmdDat+", STATUS["+str(self.statusWord)+"], STATE["+str(self.state)+"], "
        # strData = strData + "CODE["+code+"]: "+codeMessage+", SENSOR["+hexlify(self.sensorStatus)+"], MODULE["+hexlify(self.statusModule)+"]\r\n"
        strData = strData + "CODE["+code+"]: "+codeMessage+", SENSOR["+self.sensorStatus.decode("utf-8")+"], MODULE["+self.statusModule.decode("utf-8")+"]\r\n"
        strData = strData + "DATA:" + str(self.responseData) + "\r\n"
        return strData
    
    
    def getCashInfo(self):
        dataCash = hexlify(self.responseData).upper()
        iD = dataCash.find("44")
        if(iD == -1):
            return self.getResponse()
        
        iCur = dataCash[iD+2] + dataCash[iD+3]
        LOG.grglog("[LIB] iCur: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, iCur)

        if iCur == "4F":
            iCur = "IDR"
        else:
            iCur = "UNK"
        
        iDen = dataCash[iD+4] + dataCash[iD+5]
        LOG.grglog("[LIB] iDen: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, iDen)

        denom = DENOM_LIST.get(iDen, "0")
        return True, "Received="+iCur+"|Denomination="+denom+"|Version=1|SerialNumber=1|Go=0", "OK"
    
    
    def getResponse(self):
        isNormal = True
        iHandle = "0"
        # code = hexlify(self.statusCode)
        code = hexlify(self.statusCode).decode("utf-8")
        if code != "0000":
            iHandle = "1"
            isNormal = False
        
        if self.statusWord == 101:
            iHandle = "1"
            isNormal = False
        
        if code == "0004" or code == "0003":
            iHandle = "0"
            isNormal = True
        
        print('iHandle', type(iHandle), str(iHandle))
        print('code', type(code), str(code))
        statusMessage = self.getStatusMessage(code)
        print('statusMessage', type(statusMessage), str(statusMessage))
        return isNormal, "acDevReturn:|acReserve:|iHandle:"+iHandle+"|iLogicCode:"+code+"|iPhyCode:"+code+"|iType:"+iHandle, statusMessage


    def getStatusMessage(self, code=""):
        if code.startswith("02"):
            return "Unidentified notes"
        return STATUS_CODE.get(code, "Error Code["+code+"] not found")


def getByteTimestamp():
    today = datetime.datetime.now()
    todayStr = today.strftime("%y%m%d%H%M%S")
    return bytes.fromhex(todayStr)


def createMessage(command=CMD.QUERY_STATUS, param=[]):
    # result = bytes.fromhex( command.value )
    result = command.value
    if command == CMD.QUERY_VERSION:
        #param -> 
        # '0' (mainboard version), 
        # '1' (algo version)
        result = result + getByteTimestamp() + param[0]        
    elif command == CMD.CLEAR_NOTES:
        #param -> 
        # '0' (withdraw the note in the transport), 
        # '1' (push the note in the transport into the cassette)
        result = result + getByteTimestamp() + param[0]
    elif command == CMD.QUERY_STATUS:
        #param -> None
        result = result + getByteTimestamp()
    elif command == CMD.DEPOSIT_PREP:
        #param -> None
        result = result + getByteTimestamp()
    elif command == CMD.NOTE_INFO:
        #param -> None
        result = result + getByteTimestamp()
    elif command == CMD.DEPOSIT_CONFIRM:
        #param -> None
        result = result + getByteTimestamp()
    elif command == CMD.DEPOSIT_CANCEL:
        #param -> None
        result = result + getByteTimestamp()
    elif command == CMD.R_DENOM:
        #param -> None
        result = result + getByteTimestamp()
    elif command == CMD.STOP_RECEIVE:
        #param -> None
        result = result + getByteTimestamp()
    else:
        result = result + getByteTimestamp()
    
    result = len(result).to_bytes(2, byteorder='little') + result

    return result


def calculateCRC(data=b""):
    crc = 0
    for x in data :
        crc = x ^ crc
    return crc.to_bytes(1, byteorder='big')


def writeAndRead(ser=Serial(), wByte=b""):    
    wByte = PROTO_FUNC.STX.value + wByte + PROTO_FUNC.EXT.value
    wByte = wByte + calculateCRC(wByte)
    ser.write(wByte)
    LOG.grglog("[LIB] write: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, wByte)

    #GET ACK
    counter = 0
    while True:
        rByte = ser.read_until(size=2)
        LOG.grglog("[LIB] read: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, rByte)

        proto = PROTO_FUNC(rByte[0:2])   
        if proto == PROTO_FUNC.ACK:
            #OK Next Sequence
            wByte = PROTO_FUNC.ENQ.value
            ser.write(wByte)
            LOG.grglog("[LIB] write: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, wByte)


            rByte = ser.read_until(PROTO_FUNC.EXT.value)
            crc = ser.read(1)
            LOG.grglog("[LIB] read: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, rByte)
            LOG.grglog("[LIB] crc: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_IN, crc)
            break

        elif proto == PROTO_FUNC.BOT:
            #Busy
            time.sleep(1)
            rByte = b""
            ser.write(wByte)
            LOG.grglog("[LIB] busy response: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, wByte)

        elif proto == PROTO_FUNC.FOT:
            rByte = b""
            ser.write(wByte)
            LOG.grglog("[LIB] resume: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, wByte)

        else:
            continue
                    
        counter = counter + 1
        if counter > 20:
            raise Exception("Timeout")

    return rByte


def CM_Init(ser=Serial()):
    getVersionMessage = createMessage(CMD.QUERY_VERSION, [b'0'])
    responseData = writeAndRead(ser, getVersionMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())

    if not isNormal:
        return isNormal, returnMessage, rawMessage

    clearNotesMessage = createMessage(CMD.CLEAR_NOTES, [b'1'])
    responseData = writeAndRead(ser, clearNotesMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())

    if not isNormal:
        return isNormal, returnMessage, rawMessage

    getStatusMessage = createMessage(CMD.QUERY_STATUS)
    responseData = writeAndRead(ser, getStatusMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())

    if not isNormal:
        return isNormal, returnMessage, rawMessage

    return isNormal, returnMessage, rawMessage


CANCEL_EVENT = Event()


def CM_StartDeposit(ser=Serial()):
    global CANCEL_EVENT
    CANCEL_EVENT = Event()

    prepareDepositMessage = createMessage(CMD.DEPOSIT_PREP)
    responseData = writeAndRead(ser, prepareDepositMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    getNotesInfo = createMessage(CMD.NOTE_INFO)
    responseData = writeAndRead(ser, getNotesInfo)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    getStatusMessage = createMessage(CMD.QUERY_STATUS)
    responseData = writeAndRead(ser, getStatusMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    LOG.grglog("[LIB] state: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.state)

    startTime = time.time()
    while responseMessage.state == 3:
        getNotesInfo = createMessage(CMD.NOTE_INFO)
        responseData = writeAndRead(ser, getNotesInfo)
        responseMessage = GRGReponseData(responseData)
        isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
        LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
        if not isNormal:
            cancelNotesMessage = createMessage(CMD.DEPOSIT_CANCEL)
            responseData = writeAndRead(ser, cancelNotesMessage)
            responseMessage = GRGReponseData(responseData)
            isxNormal, returnxMessage, xrawMessage = responseMessage.getResponse()
            LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())

            if not isxNormal:
                return isxNormal, returnxMessage, xrawMessage

            return isNormal, returnMessage, rawMessage

        getStatusMessage = createMessage(CMD.QUERY_STATUS)
        responseData = writeAndRead(ser, getStatusMessage)
        responseMessage = GRGReponseData(responseData)
        isNormal, returnMessage, rawMessage = responseMessage.getResponse()
        LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())

        if not isNormal:
            return isNormal, returnMessage, rawMessage

        LOG.grglog("[LIB] state: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.state)
        if responseMessage.state == 3:
            currentTime = time.time()
            if (currentTime - startTime) >= 30:
                isNormal = False        
                rawMessage = "TimeOut Receive Bill Note 30S Achieved"            
                return isNormal, returnMessage, rawMessage
            if CANCEL_EVENT.isSet():
                CANCEL_EVENT.clear()
                return isNormal, returnMessage, rawMessage

            time.sleep(1)
    
    getNotesInfo = createMessage(CMD.NOTE_INFO)
    responseData = writeAndRead(ser, getNotesInfo)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    getStatusMessage = createMessage(CMD.QUERY_STATUS)
    responseData = writeAndRead(ser, getStatusMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnxMessage, xrawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnxMessage, xrawMessage
    
    return isNormal, returnMessage, rawMessage
    

def CM_CancelDeposit(ser=Serial(), needCancelStart=False):
    if needCancelStart:
        global CANCEL_EVENT
        CANCEL_EVENT.set()
        counter = 0
        while CANCEL_EVENT.isSet():
            LOG.grglog("[LIB] WAIT: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, "ACK Cancel EVENT")
            counter = counter + 1
            time.sleep(1)
            if counter >= 30:
                break

    stopDepositMessage = createMessage(CMD.STOP_RECEIVE)
    responseData = writeAndRead(ser, stopDepositMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())


    return isNormal, returnMessage, rawMessage


def CM_AcceptNote(ser=Serial()):  
    getNotesInfo = createMessage(CMD.NOTE_INFO)
    responseData = writeAndRead(ser, getNotesInfo)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    getStatusMessage = createMessage(CMD.QUERY_STATUS)
    responseData = writeAndRead(ser, getStatusMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnxMessage, xrawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnxMessage, xrawMessage

    confirmNotesMessage = createMessage(CMD.DEPOSIT_CONFIRM)
    responseData = writeAndRead(ser, confirmNotesMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnxMessage, xrawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnxMessage, xrawMessage

    return isNormal, returnMessage, rawMessage


def CM_CancelNote(ser=Serial()):  
    getNotesInfo = createMessage(CMD.NOTE_INFO)
    responseData = writeAndRead(ser, getNotesInfo)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    getStatusMessage = createMessage(CMD.QUERY_STATUS)
    responseData = writeAndRead(ser, getStatusMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnxMessage, xrawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnxMessage, xrawMessage

    cancelNotesMessage = createMessage(CMD.DEPOSIT_CANCEL)
    responseData = writeAndRead(ser, cancelNotesMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnxMessage, xrawMessage = responseMessage.getResponse()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnxMessage, xrawMessage

    return isNormal, returnMessage, rawMessage


def CM_GetStatus(ser=Serial()):  
    getStatusMessage = createMessage(CMD.QUERY_STATUS)
    responseData = writeAndRead(ser, getStatusMessage)
    responseMessage = GRGReponseData(responseData)
    isNormal, returnMessage, rawMessage = responseMessage.getCashInfo()
    LOG.grglog("[LIB] responseMessage: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, responseMessage.toString())
    if not isNormal:
        return isNormal, returnMessage, rawMessage

    return isNormal, returnMessage, rawMessage