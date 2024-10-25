import logging.handlers
import sys
import logging
from enum import Enum

LOGGER = logging.getLogger("NV200")

try:
    import clr
    clr.AddReference("System")
    from System import Byte, Array, BitConverter
except:
    pass

def FormatToCurrency(unformattedNumber, valueMultiplier):
    f = unformattedNumber / valueMultiplier
    return "{:.2f}".format(f)

class ChannelData():
    def __init__(self):
        self.Value = 0
        self.Channel = 0
        self.Currency = ""
        self.Level = 0
        self.Recycling = False

class CCommands(Enum):
    SSP_CMD_RESET = 0x01
    SSP_CMD_SET_CHANNEL_INHIBITS = 0x02
    SSP_CMD_DISPLAY_ON = 0x03
    SSP_CMD_DISPLAY_OFF = 0x04
    SSP_CMD_SETUP_REQUEST = 0x05
    SSP_CMD_HOST_PROTOCOL_VERSION = 0x06
    SSP_CMD_POLL = 0x07
    SSP_CMD_REJECT_BANKNOTE = 0x08
    SSP_CMD_DISABLE = 0x09
    SSP_CMD_ENABLE = 0x0A
    SSP_CMD_GET_SERIAL_NUMBER = 0x0C
    SSP_CMD_UNIT_DATA = 0x0D
    SSP_CMD_CHANNEL_VALUE_REQUEST = 0x0E
    SSP_CMD_CHANNEL_SECURITY_DATA = 0x0F
    SSP_CMD_CHANNEL_RE_TEACH_DATA = 0x10
    SSP_CMD_SYNC = 0x11
    SSP_CMD_LAST_REJECT_CODE = 0x17
    SSP_CMD_HOLD = 0x18
    SSP_CMD_GET_FIRMWARE_VERSION = 0x20
    SSP_CMD_GET_DATASET_VERSION = 0x21
    SSP_CMD_GET_ALL_LEVELS = 0x22
    SSP_CMD_GET_BAR_CODE_READER_CONFIGURATION = 0x23
    SSP_CMD_SET_BAR_CODE_CONFIGURATION = 0x24
    SSP_CMD_GET_BAR_CODE_INHIBIT_STATUS = 0x25
    SSP_CMD_SET_BAR_CODE_INHIBIT_STATUS = 0x26
    SSP_CMD_GET_BAR_CODE_DATA = 0x27
    SSP_CMD_SET_REFILL_MODE = 0x30
    SSP_CMD_PAYOUT_AMOUNT = 0x33
    SSP_CMD_SET_DENOMINATION_LEVEL = 0x34
    SSP_CMD_GET_DENOMINATION_LEVEL = 0x35
    SSP_CMD_COMMUNICATION_PASS_THROUGH = 0x37
    SSP_CMD_HALT_PAYOUT = 0x38
    SSP_CMD_SET_DENOMINATION_ROUTE = 0x3B
    SSP_CMD_GET_DENOMINATION_ROUTE = 0x3C
    SSP_CMD_FLOAT_AMOUNT = 0x3D
    SSP_CMD_GET_MINIMUM_PAYOUT = 0x3E
    SSP_CMD_EMPTY_ALL = 0x3F
    SSP_CMD_SET_COIN_MECH_INHIBITS = 0x40
    SSP_CMD_GET_NOTE_POSITIONS = 0x41
    SSP_CMD_PAYOUT_NOTE = 0x42
    SSP_CMD_STACK_NOTE = 0x43
    SSP_CMD_FLOAT_BY_DENOMINATION = 0x44
    SSP_CMD_SET_VALUE_REPORTING_TYPE = 0x45
    SSP_CMD_PAYOUT_BY_DENOMINATION = 0x46
    SSP_CMD_SET_COIN_MECH_GLOBAL_INHIBIT = 0x49
    SSP_CMD_SET_GENERATOR = 0x4A
    SSP_CMD_SET_MODULUS = 0x4B
    SSP_CMD_REQUEST_KEY_EXCHANGE = 0x4C
    SSP_CMD_SET_BAUD_RATE = 0x4D
    SSP_CMD_GET_BUILD_REVISION = 0x4F
    SSP_CMD_SET_HOPPER_OPTIONS = 0x50
    SSP_CMD_GET_HOPPER_OPTIONS = 0x51
    SSP_CMD_SMART_EMPTY = 0x52
    SSP_CMD_CASHBOX_PAYOUT_OPERATION_DATA = 0x53
    SSP_CMD_CONFIGURE_BEZEL = 0x54
    SSP_CMD_POLL_WITH_ACK = 0x56
    SSP_CMD_EVENT_ACK = 0x57
    SSP_CMD_GET_COUNTERS = 0x58
    SSP_CMD_RESET_COUNTERS = 0x59
    SSP_CMD_COIN_MECH_OPTIONS = 0x5A
    SSP_CMD_DISABLE_PAYOUT_DEVICE = 0x5B
    SSP_CMD_ENABLE_PAYOUT_DEVICE = 0x5C
    SSP_CMD_SET_FIXED_ENCRYPTION_KEY = 0x60
    SSP_CMD_RESET_FIXED_ENCRYPTION_KEY = 0x61
    SSP_CMD_REQUEST_TEBS_BARCODE = 0x65
    SSP_CMD_REQUEST_TEBS_LOG = 0x66
    SSP_CMD_TEBS_UNLOCK_ENABLE = 0x67
    SSP_CMD_TEBS_UNLOCK_DISABLE = 0x68
    SSP_POLL_TEBS_CASHBOX_OUT_OF_SERVICE = 0x90
    SSP_POLL_TEBS_CASHBOX_TAMPER = 0x91
    SSP_POLL_TEBS_CASHBOX_IN_SERVICE = 0x92
    SSP_POLL_TEBS_CASHBOX_UNLOCK_ENABLED = 0x93
    SSP_POLL_JAM_RECOVERY = 0xB0
    SSP_POLL_ERROR_DURING_PAYOUT = 0xB1
    SSP_POLL_SMART_EMPTYING = 0xB3
    SSP_POLL_SMART_EMPTIED = 0xB4
    SSP_POLL_CHANNEL_DISABLE = 0xB5
    SSP_POLL_INITIALISING = 0xB6
    SSP_POLL_COIN_MECH_ERROR = 0xB7
    SSP_POLL_EMPTYING = 0xC2
    SSP_POLL_EMPTIED = 0xC3
    SSP_POLL_COIN_MECH_JAMMED = 0xC4
    SSP_POLL_COIN_MECH_RETURN_PRESSED = 0xC5
    SSP_POLL_PAYOUT_OUT_OF_SERVICE = 0xC6
    SSP_POLL_NOTE_FLOAT_REMOVED = 0xC7
    SSP_POLL_NOTE_FLOAT_ATTACHED = 0xC8
    SSP_POLL_NOTE_TRANSFERED_TO_STACKER = 0xC9
    SSP_POLL_NOTE_PAID_INTO_STACKER_AT_POWER_UP = 0xCA
    SSP_POLL_NOTE_PAID_INTO_STORE_AT_POWER_UP = 0xCB
    SSP_POLL_NOTE_STACKING = 0xCC
    SSP_POLL_NOTE_DISPENSED_AT_POWER_UP = 0xCD
    SSP_POLL_NOTE_HELD_IN_BEZEL = 0xCE
    SSP_POLL_BAR_CODE_TICKET_ACKNOWLEDGE = 0xD1
    SSP_POLL_DISPENSED = 0xD2
    SSP_POLL_JAMMED = 0xD5
    SSP_POLL_HALTED = 0xD6
    SSP_POLL_FLOATING = 0xD7
    SSP_POLL_FLOATED = 0xD8
    SSP_POLL_TIME_OUT = 0xD9
    SSP_POLL_DISPENSING = 0xDA
    SSP_POLL_NOTE_STORED_IN_PAYOUT = 0xDB
    SSP_POLL_INCOMPLETE_PAYOUT = 0xDC
    SSP_POLL_INCOMPLETE_FLOAT = 0xDD
    SSP_POLL_CASHBOX_PAID = 0xDE
    SSP_POLL_COIN_CREDIT = 0xDF
    SSP_POLL_NOTE_PATH_OPEN = 0xE0
    SSP_POLL_NOTE_CLEARED_FROM_FRONT = 0xE1
    SSP_POLL_NOTE_CLEARED_TO_CASHBOX = 0xE2
    SSP_POLL_CASHBOX_REMOVED = 0xE3
    SSP_POLL_CASHBOX_REPLACED = 0xE4
    SSP_POLL_BAR_CODE_TICKET_VALIDATED = 0xE5
    SSP_POLL_FRAUD_ATTEMPT = 0xE6
    SSP_POLL_STACKER_FULL = 0xE7
    SSP_POLL_DISABLED = 0xE8
    SSP_POLL_UNSAFE_NOTE_JAM = 0xE9
    SSP_POLL_SAFE_NOTE_JAM = 0xEA
    SSP_POLL_NOTE_STACKED = 0xEB
    SSP_POLL_NOTE_REJECTED = 0xEC
    SSP_POLL_NOTE_REJECTING = 0xED
    SSP_POLL_CREDIT_NOTE = 0xEE
    SSP_POLL_READ_NOTE = 0xEF
    SSP_POLL_SLAVE_RESET = 0xF1
    SSP_RESPONSE_OK = 0xF0
    SSP_RESPONSE_COMMAND_NOT_KNOWN = 0xF2
    SSP_RESPONSE_WRONG_NO_PARAMETERS = 0xF3
    SSP_RESPONSE_PARAMETER_OUT_OF_RANGE = 0xF4
    SSP_RESPONSE_COMMAND_CANNOT_BE_PROCESSED = 0xF5
    SSP_RESPONSE_SOFTWARE_ERROR = 0xF6
    SSP_RESPONSE_FAIL = 0xF8
    SSP_RESPONSE_KEY_NOT_SET = 0xFA

class NVEngine():

    def __init__(self, path_to_library:str, is_log_active:bool):
        sys.path.append(path_to_library)
        try:
            clr.AddReference("ITLlib")
            import ITLlib
        except:
            pass

        self.m_eSSP = ITLlib.SSPComms()
        self.m_cmd = ITLlib.SSP_COMMAND()
        self.keys = ITLlib.SSP_KEYS()
        self.sspKey = ITLlib.SSP_FULL_KEY()
        self.info = ITLlib.SSP_COMMAND_INFO()

        self.m_ProtocolVersion = 0
        self.m_FirmwareVersion = ""
        self.m_UnitType = '\xFF'
        self.m_UnitName = ""
        self.m_NumStackedNotes = 0
        self.m_NumberOfChannels = 0
        self.m_ValueMultiplier = 1
        self.m_HoldNumber = 0
        self.m_HoldCount = 0
        self.m_NoteValue = 0
        self.m_NoteHeld = False
        self.m_HeldNoteByCount = False
        self.m_UnitDataList = []
        self.m_SerialNumber = 0
        self.log_active = is_log_active

        if is_log_active:            
            flog = logging.handlers.TimedRotatingFileHandler("nv200.log", when='d')
            slog = logging.StreamHandler()
            flog.namer = lambda name: name.replace(".log", "") + ".log"
            formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(funcName)s : %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

            flog.setFormatter(formatter)
            slog.setFormatter(formatter)

            flog.setLevel(logging.DEBUG)
            slog.setLevel(logging.DEBUG)
            LOGGER.setLevel(logging.DEBUG)

            LOGGER.addHandler(flog)
            LOGGER.addHandler(slog)
            
            LOGGER.info("INIT LIBRARY BERHASIL")
    
    def GetChannelValue(self,channelNum:int):
        if channelNum>=1 and channelNum<=self.m_NumberOfChannels:
            for d in self.m_UnitDataList:
                # if d is ChannelData:
                if d.Channel == channelNum:
                    return d.Value
        return -1
    
    def GetChannelCurrency(self,channelNum:int):
        if channelNum>=1 and channelNum<=self.m_NumberOfChannels:
            for d in self.m_UnitDataList:
                # if d is ChannelData:
                if d.Channel == channelNum:
                    return d.Currency
        return ""
    
    def SendCommand(self):
        p_backup = bytearray(255)
        backup = Array[Byte](p_backup)
        self.m_cmd.CommandData.CopyTo(backup, 0)
        length = self.m_cmd.CommandDataLength

        if self.m_eSSP.SSPSendCommand(self.m_cmd, self.info) == False:
            self.m_eSSP.CloseComPort()
            # m_Comms.UpdateLog(info,true);
            LOGGER.error("Kirim CMD gagal -> PORT Status {}".format(self.m_cmd.ResponseStatus))
            return False
        
        return True
    
    def CheckGenericResponses(self):
        message = ""
        if self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_OK.value:
            return True, "OK"
        else:
            if self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_COMMAND_CANNOT_BE_PROCESSED.value:
                if self.m_cmd.ResponseData[1] == 0x03:
                    message = "Validator memberi response Busy, cmd tidak dapat di proses pada saat ini"
                else:
                    message = "CMD response adalah CANNOT PROCESS COMMAND, error code - 0x{}".format(BitConverter.ToString(self.m_cmd.ResponseData, 1, 1))
            elif self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_FAIL.value:
                message = "CMD response adalah FAIL"
            elif self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_KEY_NOT_SET.value:
                message = "CMD response adalah KEY NOT SET, validator membutuhkan enkripsi pada perintah ini atau terdapat masalah enkripsi pada permintaan ini"
            elif self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_PARAMETER_OUT_OF_RANGE.value:
                message = "CMD response adalah PARAMATER OUT OF RANGE"
            elif self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_SOFTWARE_ERROR.value:
                message = "CMD response adalah SOFTWARE ERROR"
            elif self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_COMMAND_NOT_KNOWN.value:
                message = "CMD response adalah UNKNOWN"
            elif self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_WRONG_NO_PARAMETERS.value:
                message = "CMD response adalah WRONG PARAMETERS"
            else:
                message = "OTHER ERROR"
            if self.log_active: LOGGER.error(message)
            return False, message

    def EnableValidator(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_ENABLE.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            return False, "ERROR SEND COMMAND ENABLE"
        
        isOk, message = self.CheckGenericResponses()        
        
        if isOk and self.log_active:
            LOGGER.info("Unit enabled")
            return True, message
        
        return isOk, message
    
    def DisableValidator(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_DISABLE.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            return False
        
        isOk, message = self.CheckGenericResponses()        

        if isOk and self.log_active:
            LOGGER.info("Unit disabled")
            return True
        
        return True
    
    def AcceptNote(self):
        LOGGER.info("Accepting Note")
        self.m_HoldCount = 0
        return True
        #Todo DoPoll again?

    def ReturnNote(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_REJECT_BANKNOTE.value
        self.m_cmd.CommandDataLength = 1
        message = "ERROR"

        if not self.SendCommand():
            return False, "ERROR SEND COMMAND RETURN"
        
        isOk, message = self.CheckGenericResponses()

        if isOk:
            if self.log_active:
                LOGGER.info("Returning Note")
                pass
            self.m_HoldCount = 0            
        
            return True, message
        
        return False, message
    
    def Reset(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_RESET.value
        self.m_cmd.CommandDataLength = 1
        message = "ERROR"

        if not self.SendCommand():
            return False, "ERROR SEND COMMAND RESET"
        
        isOk, message = self.CheckGenericResponses()        

        if isOk and self.log_active:
            LOGGER.info("Resetting unit")
            return True, message
        
        return isOk, message
    
    def SendSync(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_SYNC.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            return False
        
        isOk, message = self.CheckGenericResponses()        

        if isOk and self.log_active:
            LOGGER.info("Send Sync Success")
            return True
        
        return True
    
    def OpenComPort(self):
        # Todo Logging OpeningPort
        if self.log_active:
            LOGGER.info("Opening COM PORT {}".format(self.m_cmd.ComPort))

        return self.m_eSSP.OpenSSPComPort(self.m_cmd)
    
    def NegotiateKeys(self):
        #Encrypt OFF
        self.m_cmd.EncryptionStatus = False
        if self.log_active:
            LOGGER.info("Syncing... ")

        #Send Sync
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_SYNC.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            return False
        if self.log_active: LOGGER.info("Success")

        
        self.m_eSSP.InitiateSSPHostKeys(self.keys, self.m_cmd)

        #Send Generator
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_SET_GENERATOR.value
        self.m_cmd.CommandDataLength = 9
        if self.log_active:
            LOGGER.info("Setting generator... ")

        # Generate from ULONG to Bytes then copy it pos 1 not 0
        # key_gen = int(self.keys.Generator).to_bytes(8, 'big')
        # self.m_cmd.CommandData[1:1+len(key_gen)] = Array[Byte](key_gen)
        BitConverter.GetBytes(self.keys.Generator).CopyTo(self.m_cmd.CommandData, 1)
        
        if not self.SendCommand():
            return False
        if self.log_active: LOGGER.info("Success")
        
        #Send Modulus
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_SET_MODULUS.value
        self.m_cmd.CommandDataLength = 9
        if self.log_active:
            LOGGER.info("Setting modulus... ")

        # Generate from ULONG to Bytes then copy it pos 1 not 0
        # key_gen = int(self.keys.Modulus).to_bytes(8, 'big')
        # self.m_cmd.CommandData[1:1+len(key_gen)] = Array[Byte](key_gen)
        BitConverter.GetBytes(self.keys.Modulus).CopyTo(self.m_cmd.CommandData, 1)
        
        if not self.SendCommand():
            return False
        if self.log_active: LOGGER.info("Success")

        #Send Key Exchange
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_REQUEST_KEY_EXCHANGE.value
        self.m_cmd.CommandDataLength = 9
        if self.log_active:
            LOGGER.info("Exchanging keys... ")

        # Generate from ULONG to Bytes then copy it pos 1 not 0
        # key_gen = int(self.keys.HostInter).to_bytes(8, 'big')
        # self.m_cmd.CommandData[1:1+len(key_gen)] = Array[Byte](key_gen)
        BitConverter.GetBytes(self.keys.HostInter).CopyTo(self.m_cmd.CommandData, 1)
                
        if not self.SendCommand():
            return False
        if self.log_active: LOGGER.info("Success")
        
        # Read Slave Intermediate Key
        # self.keys.SlaveInterKey = int.from_bytes(self.m_cmd.ResponseData, 'big')
        self.keys.SlaveInterKey = BitConverter.ToUInt64(self.m_cmd.ResponseData, 1)

        self.m_eSSP.CreateSSPHostEncryptionKey(self.keys)

        # Get Full Encryption Key
        self.m_cmd.Key.FixedKey = 0x0123456701234567
        self.m_cmd.Key.VariableKey = self.keys.KeyHost

        if self.log_active:
            LOGGER.info("Keys successfully negotiated")

        return True
    
    def SetProtocolVersion(self, pVersion):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_HOST_PROTOCOL_VERSION.value
        self.m_cmd.CommandData[1] = pVersion
        self.m_cmd.CommandDataLength = 2
        return self.SendCommand()
    
    def FindMaxProtocolVersion(self):
        b = 0x06
        while True:
            self.SetProtocolVersion(b)
            if self.m_cmd.ResponseData[0] == CCommands.SSP_RESPONSE_FAIL.value:
                return b-1
            b+=1
            if b > 20:
                return 0x06
    
    def ValidatorSetupRequest(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_SETUP_REQUEST.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            if self.log_active:
                LOGGER.error("SETUP FAILED")
            return False
        
        index = 1
        self.m_UnitType = self.m_cmd.ResponseData[index]
        index += 1
        unitName = ""
        if self.m_UnitType == 0x00: unitName = "Validator"
        elif self.m_UnitType == 0x03: unitName = "SMART Hopper"
        elif self.m_UnitType == 0x06: unitName = "SMART Payout"
        elif self.m_UnitType == 0x07: unitName = "NV11"
        elif self.m_UnitType == 0x0D: unitName = "TEBS"
        else: unitName = "Unknown Type"
        self.m_UnitName = unitName
        LOGGER.info("Unit Type: {}".format(self.m_UnitName))

        self.m_FirmwareVersion = ""

        self.m_FirmwareVersion += str(self.m_cmd.ResponseData[index].to_bytes(1, 'big'), encoding="utf-8")
        index += 1
        self.m_FirmwareVersion += str(self.m_cmd.ResponseData[index].to_bytes(1, 'big'), encoding="utf-8")
        index += 1

        self.m_FirmwareVersion += "."

        self.m_FirmwareVersion += str(self.m_cmd.ResponseData[index].to_bytes(1, 'big'), encoding="utf-8")
        index += 1
        self.m_FirmwareVersion += str(self.m_cmd.ResponseData[index].to_bytes(1, 'big'), encoding="utf-8")
        index += 1

        LOGGER.info("Firmware: {}".format(self.m_FirmwareVersion))

        # Country Code for Legacy Skiped
        index += 3
        # Value Multiplier Code for Legacy Skiped
        index += 3

        self.m_NumberOfChannels = self.m_cmd.ResponseData[index]
        LOGGER.info("Number of Channels: {}".format(self.m_NumberOfChannels))
        index += 1

        # Channel Value for Legacy Skiped
        index += self.m_NumberOfChannels

        # Channel Security for Legacy Skiped
        index += self.m_NumberOfChannels

        self.m_ValueMultiplier = self.m_cmd.ResponseData[index + 2]        
        self.m_ValueMultiplier += self.m_cmd.ResponseData[index + 1] << 8
        self.m_ValueMultiplier += self.m_cmd.ResponseData[index] << 16
        LOGGER.info("Real Value Multiplier: {}".format(self.m_ValueMultiplier))
        index += 3

        self.m_ProtocolVersion = self.m_cmd.ResponseData[index]
        index += 1
        LOGGER.info("ProtocolVersion: {}".format(self.m_ProtocolVersion))

        self.m_UnitDataList.clear()

        for i in range(0, self.m_NumberOfChannels, 1):
            loopChannelData = ChannelData()

            # Channel Number
            loopChannelData.Channel = i + 1
            channelIndex = index + (self.m_NumberOfChannels * 3) + (i * 4)

            # Channel Value
            loopChannelData.Value = BitConverter.ToInt32(self.m_cmd.ResponseData, channelIndex) * self.m_ValueMultiplier

            # Channel Currency
            loopChannelData.Currency = ""
            loopChannelData.Currency += str(self.m_cmd.ResponseData[index+(i*3)].to_bytes(1, 'big'), encoding="utf-8")
            loopChannelData.Currency += str(self.m_cmd.ResponseData[(index+1)+(i*3)].to_bytes(1, 'big'), encoding="utf-8")
            loopChannelData.Currency += str(self.m_cmd.ResponseData[(index+2)+(i*3)].to_bytes(1, 'big'), encoding="utf-8")

            # Channel Level
            loopChannelData.Level = 0

            # Channel Recycling
            loopChannelData.Recycling = False
    
            self.m_UnitDataList.append(loopChannelData)

            LOGGER.info("Channel {}: {} {}".format(loopChannelData.Channel, loopChannelData.Value/self.m_ValueMultiplier, loopChannelData.Currency))
        self.m_UnitDataList.sort(key=lambda d : d.Value)

    def GetSerialNumber(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_GET_SERIAL_NUMBER.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            return False
        isOk, message = self.CheckGenericResponses()        
        
        if isOk:
            Array.Reverse(self.m_cmd.ResponseData, 1, 4)
            self.m_SerialNumber = BitConverter.ToUInt32(self.m_cmd.ResponseData, 1)

            if self.log_active:
                LOGGER.info("Serial Number : {}".format(self.m_SerialNumber))
            self.m_HoldCount = 0            
            return True
        return False
    
    def SetInhibits(self):
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_SET_CHANNEL_INHIBITS.value
        self.m_cmd.CommandData[1] = 0xFF
        self.m_cmd.CommandData[2] = 0xFF
        self.m_cmd.CommandDataLength = 3

        if not self.SendCommand():
            return False
        isOk, message = self.CheckGenericResponses()        

        if isOk:
            if self.log_active:
                LOGGER.info("Inhibits set")
            self.m_HoldCount = 0            
            return True
        return False

    def ConnectToValidator(self):
        self.m_eSSP.CloseComPort()
        self.m_cmd.EncryptionStatus = False
        if self.OpenComPort() and self.NegotiateKeys():
            self.m_cmd.EncryptionStatus = True
            maxVersion = self.FindMaxProtocolVersion()
            if maxVersion > 6:
                self.SetProtocolVersion(maxVersion)
            else:
                if self.log_active: LOGGER.error("Program ini tidak support untuk unit dibawah protokol versi 6, update firmware")
                return False
            self.ValidatorSetupRequest()
            self.GetSerialNumber()
            self.SetInhibits()
            isOK, message = self.EnableValidator()
            return isOK
        return False

    def QueryRejection(self):
        message = ""
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_LAST_REJECT_CODE.value
        self.m_cmd.CommandDataLength = 1

        if not self.SendCommand():
            return False, "ERROR SEND COMMAND QUERY"

        isOk, message = self.CheckGenericResponses()

        if isOk:
            if 0x00 == self.m_cmd.ResponseData[1]: message = "Note accepted"
            elif 0x01 == self.m_cmd.ResponseData[1]: message = "Note length incorrect"
            elif 0x02 == self.m_cmd.ResponseData[1]: message = "Invalid note 1"
            elif 0x03 == self.m_cmd.ResponseData[1]: message = "Invalid note 2"
            elif 0x04 == self.m_cmd.ResponseData[1]: message = "Invalid note 3"
            elif 0x05 == self.m_cmd.ResponseData[1]: message = "Invalid note 4"
            elif 0x06 == self.m_cmd.ResponseData[1]: message = "Channel inhibited"
            elif 0x07 == self.m_cmd.ResponseData[1]: message = "Second note inserted during read"
            elif 0x08 == self.m_cmd.ResponseData[1]: message = "Host rejected note"
            elif 0x09 == self.m_cmd.ResponseData[1]: message = "Invalid note 5"
            elif 0x0A == self.m_cmd.ResponseData[1]: message = "Invalid note read 1"
            elif 0x0B == self.m_cmd.ResponseData[1]: message = "Note too long"
            elif 0x0C == self.m_cmd.ResponseData[1]: message = "Validator disabled"
            elif 0x0D == self.m_cmd.ResponseData[1]: message = "Mechanism slow/stalled"
            elif 0x0E == self.m_cmd.ResponseData[1]: message = "Strim attempt"
            elif 0x0F == self.m_cmd.ResponseData[1]: message = "Fraud channel reject"
            elif 0x10 == self.m_cmd.ResponseData[1]: message = "No notes inserted"
            elif 0x11 == self.m_cmd.ResponseData[1]: message = "Invalid note read 2"
            elif 0x12 == self.m_cmd.ResponseData[1]: message = "Twisted note detected"
            elif 0x13 == self.m_cmd.ResponseData[1]: message = "Escrow time-out"
            elif 0x14 == self.m_cmd.ResponseData[1]: message = "Bar code scan fail"
            elif 0x15 == self.m_cmd.ResponseData[1]: message = "Invalid note read 3"
            elif 0x16 == self.m_cmd.ResponseData[1]: message = "Invalid note read 4"
            elif 0x17 == self.m_cmd.ResponseData[1]: message = "Invalid note read 5"
            elif 0x18 == self.m_cmd.ResponseData[1]: message = "Invalid note read 6"
            elif 0x19 == self.m_cmd.ResponseData[1]: message = "Incorrect note width"
            elif 0x1A == self.m_cmd.ResponseData[1]: message = "Note too short"
            else: message = "Unknown rejection code: {}".format(self.m_cmd.ResponseData[1])

            if self.log_active: LOGGER.info(message)

            return True, message
        
        return False, message
    
    def DoPoll(self):
        # i = 0xFF

        message = ""

        if self.m_HoldCount > 0:
            self.m_NoteHeld = True
            if self.m_HeldNoteByCount:
                self.m_HoldCount -= 1
            self.m_cmd.CommandData[0] = CCommands.SSP_CMD_HOLD.value
            self.m_cmd.CommandDataLength = 1
            message = "Note held in escrow, amount: {}".format(FormatToCurrency(self.m_NoteValue, self.m_ValueMultiplier))
            if self.log_active: LOGGER.info(message)

            if not self.SendCommand():
                message += "ERROR SEND COMMAND HOLD"
                if self.log_active: LOGGER.info(message)
                return False, message
            else: return True, message
        
        self.m_cmd.CommandData[0] = CCommands.SSP_CMD_POLL.value
        self.m_cmd.CommandDataLength = 1
        self.m_NoteHeld = False

        if not self.SendCommand(): return False, "ERROR: SEND COMMAND POLL"
        
        i = 1
        while i < self.m_cmd.ResponseDataLength:
            if self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_SLAVE_RESET.value:
                message += "Unit Reset"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_READ_NOTE.value:
                if self.m_cmd.ResponseData[i+1] > 0 :
                    self.m_NoteValue = self.GetChannelValue(self.m_cmd.ResponseData[i+1])
                    self.m_HoldCount = self.m_HoldNumber
                    message += "Note in escrow, amount: {} {}".format(FormatToCurrency(self.m_NoteValue, self.m_ValueMultiplier), self.GetChannelCurrency(self.m_cmd.ResponseData[i+1]))
                else:
                    message += "Reading note... "
                i+=1
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_CREDIT_NOTE.value:
                self.m_NoteValue = self.GetChannelValue(self.m_cmd.ResponseData[i+1])
                message += "Credit {} {}".format(FormatToCurrency(self.m_NoteValue, self.m_ValueMultiplier), self.GetChannelCurrency(self.m_cmd.ResponseData[i+1]))
                self.m_NumStackedNotes += 1
                i+=1
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_REJECTING.value:
                message += "Rejecting note... "
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_REJECTED.value:
                message += "Note rejected"
                isOk, rejectionReason = self.QueryRejection()
                message += " -> Reason {}".format(rejectionReason)
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_STACKING.value:
                message += "Stacking note... "
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_STACKED.value:
                message += "Note stacked"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_SAFE_NOTE_JAM.value:
                message += "Safe jam"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_UNSAFE_NOTE_JAM.value:
                message += "Unsafe jam"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_DISABLED.value:
                message += "Disabled"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_FRAUD_ATTEMPT.value:
                message += "Fraud attempt, note type: {}".format(self.GetChannelValue(self.m_cmd.ResponseData[i+1]))
                i+=1
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_STACKER_FULL.value:
                message += "Stacker full"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_CLEARED_FROM_FRONT.value:
                message += "{} note cleared from front at reset".format(self.GetChannelValue(self.m_cmd.ResponseData[i+1]))
                i+=1
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_CLEARED_TO_CASHBOX.value:
                message += "{} note cleared to stacker at reset".format(self.GetChannelValue(self.m_cmd.ResponseData[i+1]))
                i+=1
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_CASHBOX_REMOVED.value:
                message += "Cashbox removed..."
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_CASHBOX_REPLACED.value:
                message += "Cashbox replaced"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_NOTE_PATH_OPEN.value:
                message += "Note path open"
            elif self.m_cmd.ResponseData[i] == CCommands.SSP_POLL_CHANNEL_DISABLE.value:
                message += "All channel inhibited, unit disabled"
            else:
                message += "Unrecognised poll response detected {}".format(self.m_cmd.ResponseData[i])

            if self.log_active: LOGGER.info(message)

            i+=1    

        return True, message
