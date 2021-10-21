__author__ = 'wahyudi@multidaya.id'

from serial import Serial
from _mModule import _GRGComProtocol
from _mModule import _CPrepaidLog as LOG


class GRGSerial():
    def __init__(self):
        self.ser = None
        # self.ser = Serial(port="port", baudrate=19200, timeout=500)
    
    def initConnect(self, port="COM7"):
        # if self.ser:
        #     if self.ser.isOpen():
        #         self.disconnect()

        if self.ser is None:
            self.ser = Serial(port=port, baudrate=19200, timeout=500)
            result = _GRGComProtocol.CM_Init(self.ser)
            LOG.grglog("[LIB] initConnect: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        else:
            if self.ser.isOpen():
                # self.ser.close()
                self.disconnect()
                self.ser = Serial(port=port, baudrate=19200, timeout=500)
            result = _GRGComProtocol.CM_Init(self.ser)
            LOG.grglog("[LIB] reInitConnect: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)

        return result
    
    def disconnect(self):
        self.ser.close()
    
    IS_START_DEPOSIT_ACTIVE = False
    def startDeposit(self):
        self.IS_START_DEPOSIT_ACTIVE = True
        try:
            isNormal, returnMessage, rawMessage = _GRGComProtocol.CM_StartDeposit(self.ser)
            LOG.grglog("[LIB] startDeposit: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, (isNormal, returnMessage, rawMessage))

            self.IS_START_DEPOSIT_ACTIVE = False
            if not isNormal:
                _GRGComProtocol.CM_CancelDeposit(self.ser, False)
        except Exception as ex:
            self.IS_START_DEPOSIT_ACTIVE = False
            _GRGComProtocol.CM_CancelDeposit(self.ser, False)
            raise ex

        return isNormal, returnMessage, rawMessage
    
    def cancelDeposit(self):
        result = _GRGComProtocol.CM_CancelDeposit(self.ser, self.IS_START_DEPOSIT_ACTIVE)
        LOG.grglog("[LIB] cancelDeposit: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        return result
    
    def confirmNote(self):
        result = _GRGComProtocol.CM_AcceptNote(self.ser)
        LOG.grglog("[LIB] confirmNote: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        return result
    
    def cancelNote(self):
        result = _GRGComProtocol.CM_CancelNote(self.ser)
        LOG.grglog("[LIB] cancelNote: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        return result
    
    def getStatus(self):
        result = _GRGComProtocol.CM_GetStatus(self.ser)
        LOG.grglog("[LIB] getStatus: ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_OUT, result)
        return result
    