""" Untuk Python 3 keatas """
import logging
import binascii
import random
# from Cryptodome.Util.Padding import pad
# from Cryptodome.Cipher import DES3
# from Cryptodome.Random import get_random_bytes
import struct
from time import time
import time
import socket
from _sService import _BniActivationHTTPRequest
from _cCommand import _Command
from _dDevice import _QPROX
from _cConfig import _Common
# from BniActivationHTTPRequest import BniActivationHTTPRequest

LOGGER = logging.getLogger()

class bniSCardError(IOError):  # noqa
    pass

class bniSCard2(object):
    global SET_COM_SAM_1,SET_COM_SAM_2,SET_COM_NFC
    global GET_CURRENT_COM,SAM_ACT_RESET,NFC_ACT_RESET
    global BUFFER_SIZE      
    
    SET_COM_SAM_1 = b'\xFF\x71\x13\x01\x00'
    SET_COM_SAM_2 = b"\xFF\x71\x13\x02\x00"
    SET_COM_NFC = b"\xFF\x71\x13\x06\x00"
    GET_CURRENT_COM = b"\xFF\x71\x14\x00\x00"
    SAM_ACT_RESET = b"\xFF\x71\x10\x02\x00"
    NFC_ACT_RESET = b"\xFF\x71\x10\x00\x00"
    BUFFER_SIZE = 1024

    def __init__(self, mode=1, debug=False, card_no = "012345"):
        """ MODE:
                1. SAM
                2. TCP 
                3. HTTP\
                4. Service """
        
        self.tcp_ip = ''
        self.tcp_port = ''
        self.mode = mode
        self.debug = debug
        if mode == 1:
            raise bniSCardError("Mode ini dimatikan dikarenakan tidak disupport pada lib ini.")
            #self.modestr = "PHY"
            #self.context = pcsclite.Context()            
        elif mode == 2:
            self.modestr = "TCP"
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif mode == 3:
            self.modestr = "HTTP"
            self.reff_no = -1
            self.http = _BniActivationHTTPRequest.BniActivationHTTPRequest(url=_Common.URL_BNI_ACTIVATION)
            self.card_no = card_no
        elif mode == 4:
            self.modestr = "SERVICE"
            self.sam_no = str(4)
        else:
            raise bniSCardError("Mode not available:"+mode)
    
    def devTCPConnect(self, TCP_IP='192.168.9.42', TCP_PORT=444):
        self.socket.connect((TCP_IP, TCP_PORT))
        self.tcp_ip = TCP_IP
        self.tcp_port = TCP_PORT
        if self.debug : 
            # print("["+self.modestr+"] Connected To:" + TCP_IP + " Port: " + str(TCP_PORT))
            LOGGER.info("["+self.modestr+"] Connected To:" + TCP_IP + " Port: " + str(TCP_PORT))
            
        
    def devPCSCConnect(self, reader_name):
        readers = self.context.list_readers()
        reader = self.devPCSCIsReaderExist(reader_name)
        if not reader[0] : raise bniSCardError("SmartCard Reader tidak ditemukan: "+reader_name)       
        self.card = self.context.connect(reader[1])
        if self.debug : 
            # print("["+self.modestr+"] Connected To:" + self.tcp_ip + " Port: " + str(self.tcp_port))
            LOGGER.info("["+self.modestr+"] Connected To:" + self.tcp_ip + " Port: " + str(self.tcp_port))
        
    def devPCSCIsReaderExist(self, reader_name):
        readers = self.context.list_readers()
        readerdev = None
        reader_found = False
        for reader in readers:
            if reader == reader_name:
                reader_found = True
                readerdev = reader
                break
        return reader_found, readerdev 
    
    def devClose(self):
        if self.mode == 1 :
            self.card.disconnect()
            del self.card
            del self.context
        elif self.mode == 2:
            self.socket.close()
        elif self.mode == 3:
            self.http.close_session(self.card_no)
    
    def devTransmit(self, command):
        CMD_OK = b'\x90\x00'
        
        if self.debug :
            com_type = type(command) 
            #print("Command is " + str(type(command)))
            if com_type is str:
                # print("SEND["+ str(self.modestr) + "] : " + command)
                LOGGER.info("SEND["+ str(self.modestr) + "] : " + command)
            elif com_type is bytes:     
                # print("SEND["+ str(self.modestr) + "] : " + binascii.b2a_hex(command).decode("utf-8"))
                LOGGER.info("SEND["+ str(self.modestr) + "] : " + binascii.b2a_hex(command).decode("utf-8"))
            elif com_type is bytearray:     
                # print("SEND["+ str(self.modestr) + "] : " + binascii.b2a_hex(command).decode("utf-8"))
                LOGGER.info("SEND["+ str(self.modestr) + "] : " + binascii.b2a_hex(command).decode("utf-8"))
            else:
                # print("SEND["+ str(self.modestr) + "] : " + command)
                LOGGER.info("SEND["+ str(self.modestr) + "] : " + command)

        if self.mode == 1:
            data = self.card.transmit(command)
        elif self.mode == 2:
            self.socket.send(command)
            data = self.socket.recv(BUFFER_SIZE)
        elif self.mode == 3:
            data = self.http.send_data(self.card_no,command)
            data = bytearray.fromhex(data)
        elif self.mode == 4:
            command2 = binascii.b2a_hex(command).decode("utf-8")
            param = _QPROX.QPROX['RAW_APDU']+'|'+self.sam_no+"|" + command2
            response, result = _Command.send_request(param=param)
            if response == 0:
                data = result + "9000"
                data = bytearray.fromhex(data)
            else: data = b'\xFF'

        if self.debug : 
            dat_type = type(data) 
            if dat_type is str:
                # print("RECV["+ str(self.modestr) + "] : " + data)
                LOGGER.info("RECV["+ str(self.modestr) + "] : " + data)
            elif dat_type is bytes or dat_type is bytearray:
                # print("RECV["+ str(self.modestr) + "] : " + binascii.b2a_hex(data).decode("utf-8"))
                LOGGER.info("RECV["+ str(self.modestr) + "] : " + binascii.b2a_hex(data).decode("utf-8"))
            else:
                # print("RECV["+ str(self.modestr) + "] : " + data)     
                LOGGER.info("RECV["+ str(self.modestr) + "] : " + data)           
        return data
    
            
    def cmdSwitchToNFC(self):
        data = self.card.transmit(SET_COM_NFC)
        #print binascii.b2a_hex(data)

        data = self.card.transmit(GET_CURRENT_COM)
        #print binascii.b2a_hex(data)

        data = self.card.transmit(NFC_ACT_RESET)
        #print binascii.b2a_hex(data)
        if self.debug : 
            # print ("SWITCHED_TO_NFC")
            LOGGER.info("SWITCHED_TO_NFC")
        pass
    
    def cmdSwitchToSAM(self):
        data = self.card.transmit(SET_COM_SAM_1)
        #print binascii.b2a_hex(data)

        data = self.card.transmit(GET_CURRENT_COM)
        #print binascii.b2a_hex(data)

        data = self.card.transmit(SAM_ACT_RESET)
        #print binascii.b2a_hex(data)
        if self.debug : 
            # print ("SWITCHED_TO_SAM")
            LOGGER.info("SWITCHED_TO_SAM")
        pass
    
    def cmdGetSRN(self):
        if self.debug : 
            # print ("GET Challange or SAM RN:")
            LOGGER.info("GET Challange or SAM RN:")
        BNI_GC_SAM = b"\x80\x84\x00\x00\x08"
        self.devTransmit(BNI_GC_SAM)        
        return self.devTransmit(BNI_GC_SAM)
        
    def cmdGetCRN(self):
        if self.debug : 
            # print ("GET Challange or Card RN:")
            LOGGER.info("GET Challange or Card RN:")
        BNI_GC_CARD = b"\x00\x84\x00\x00\x08"
        return self.devTransmit(BNI_GC_CARD)
    
    # def cmdTerminalInit(self, TM_KEY, IV, BNI_PIN):        
    #     data = self.cmdGetCRN()
    #     R1 = data[:8]
    #     R2 = get_random_bytes(8)
    #     R1IIR2 = R1 + R2
    #     cipher = DES3.new(TM_KEY, DES3.MODE_CBC, IV)
    #     en_bytes = cipher.encrypt(R1IIR2)

    #     if self.debug : 
    #         print ("GET Session Key:")
    #     BNI_GET_SK = b"\x80\x82\x00\x00\x10" + en_bytes + b"\x08"
    #     data = self.devTransmit(BNI_GET_SK)
    #     SK = data[:8]

    #     DR1IIR2 = R1[:4] + R2[:4] + R1[-4:] + R2[-4:]
    #     cipher = DES3.new(TM_KEY, DES3.MODE_CBC, IV)
    #     SKT = cipher.encrypt(DR1IIR2)

    #     cipher = DES3.new(SKT, DES3.MODE_CBC, IV)
    #     R22 = cipher.decrypt(SK)
        
    #     BNI_PIN_VER = b"\x80\xA2\x00\x00\x08"
    #     if self.debug : 
    #         print ("GET PIN Verification")
    #     cipher = DES3.new(SKT, DES3.MODE_CBC, IV)
    #     EN_PIN = cipher.encrypt(BNI_PIN)

    #     BNI_GET_PIN_VER = BNI_PIN_VER + EN_PIN
    #     data = self.devTransmit(BNI_GET_PIN_VER)
        
    #     return R2 == R22, SK
    
    def cmdGetSAMRandomNumber(self, data):
        if self.debug : 
            print ("GET SAM Random Number")
            LOGGER.info("GET SAM Random Number")
        BNI_SAM_RND_NUMB_HEAD = b"\x80\x85\x00\x00\x1F\x20\x01\x02\x00\x00\x00\x00\x01"
        BNI_SAM_RND_NUMB_MID = b"\x00\x00\x00"
        BNI_SAM_RND_NUMB_TAIL = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        
        CARD_RND_NUMB = data[:8]    
        TIME_EPOCH = struct.pack(">i", int(time.time()))    
        BNI_GET_SAM_RND_NUMB = BNI_SAM_RND_NUMB_HEAD + TIME_EPOCH + BNI_SAM_RND_NUMB_MID + CARD_RND_NUMB + BNI_SAM_RND_NUMB_TAIL
        data = self.devTransmit(BNI_GET_SAM_RND_NUMB)
        return data
        
    def cmdSecureReadPurse(self):
        if self.debug : 
            print ("Secure Read Purse")
            LOGGER.info("Secure Read Purse")
        # RRN = get_random_bytes(8)
        RRN = b"\x90\x03\x00\x90\x80\x00\x00\x00"
        BNI_GET_PURSE_INFO = b"\x90\x32\x03\x00\x0A\x12\x01" + RRN + b"\x00"
        data = self.devTransmit(BNI_GET_PURSE_INFO)
        #if self.debug : 
            #self.parseSecureReadPurse(data)
    
    def parseSecureReadPurse(self, data):
        print ("Secure Read Purse Debug -> ")
        print ("Version : " + binascii.b2a_hex(data[0:1]))
        print ("Status  : " + binascii.b2a_hex(data[1:3]))
        print ("Balance : " + binascii.b2a_hex(data[3:7]))
        print ("Amount  : " + binascii.b2a_hex(data[7:9]))
        print ("CAN     : " + binascii.b2a_hex(data[9:16]))
        print ("CSN     : " + binascii.b2a_hex(data[16:23]))
        print ("EXP     : " + binascii.b2a_hex(data[23:24]))
        print ("CREATE  : " + binascii.b2a_hex(data[29:30]))
        print ("PURSE   : " + binascii.b2a_hex(data[31:31]))
        print ("ALM     : " + binascii.b2a_hex(data[32:34]))
        print ("CAN     : " + binascii.b2a_hex(data[35:42]))
        print ("CSN     : " + binascii.b2a_hex(data[43:50]))
        print ("EXP     : " + binascii.b2a_hex(data[51:52]))
        print ("CREATE  : " + binascii.b2a_hex(data[53:54]))
        print ("LCT     : " + binascii.b2a_hex(data[55:58]))
        print ("LCTH    : " + binascii.b2a_hex(data[59:62]))
        print ("NO RECT : " + binascii.b2a_hex(data[63:63]))
        print ("ISDNLen : " + binascii.b2a_hex(data[64:64]))
        print ("LAST TR : " + binascii.b2a_hex(data[65:68]))
        print ("LAST RC : " + binascii.b2a_hex(data[69:84]))
        print ("BDC     : " + binascii.b2a_hex(data[85:85]))
        print ("ATU EXP : " + binascii.b2a_hex(data[86:87]))
        print ("KEY IDX : " + binascii.b2a_hex(data[88:88]))
        print ("MAX BAL : " + binascii.b2a_hex(data[89:91]))
        print ("LTDO    : " + binascii.b2a_hex(data[92:92]))
