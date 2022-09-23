__author__ = 'wahyudi@multidaya.id'

# Boiler plate stuff to start the module
from _mModule import _CPrepaidLog as LOG
import time
import traceback
import logging

import jpype
import jpype.imports
from jpype.types import *

DEBUG_MODE = False
DEBUG_LOG_FOLDER = "mei_log/"
LOGGER = logging.getLogger()

jpype.startJVM(classpath=['_lLib/mei/*'])

from jpype import JImplements, JOverride

from cpi.banknotedevices.events import IRecyclerAsynchronousEventListener, CassetteStatusEvent, BoolResponseEvent, AsyncCompletedEvent, DeviceStateEvent
from cpi.banknotedevices.events import DocumentStatusEvent, DownloadProgressEvent, EscrowSessionSummaryEvent, MissingNotesEvent, TransportStatusEvent
from cpi.banknotedevices import Recycler, PowerUpPolicy, DeviceState, DocumentEvent, DocumentRoute


@JImplements(IRecyclerAsynchronousEventListener)
class MeiDevice:
    def __init__(self):
        self._scr = None
        self._settings = {
            "PREF_PORT":"",
            "PREF_POWER_UP_POLICY": PowerUpPolicy.R,
            "PREF_DEBUG_LOGGING_ENABLED":DEBUG_MODE,
            "PREF_DEBUG_PATH":DEBUG_LOG_FOLDER
        }
        self._APIVERSION = ""
        self._deviceState = ""
        self._documentStatus = ""
        self._currentValueInEscrowStack = 0
        self._currentStackedEscrow = []
        self._cheatDetected = 0
        self._transportOpenedWhilePoweredOff = 0
        self._transportStatus = ""
        self._cassetteStatus = ""
        self._serialNumber = ""
        self._enableRecycler = False
        self._isRecylerEnabled = None
        self._enabledRecyclerDenom = [0,0]
        self._recyclerError = ""
    
    def open(self, mei_port, enableRecycler=False, enabledRecyclerDenom=[2,3]):
        try:
            result = True, "", "OK"
            self._settings["PREF_PORT"] = mei_port
            if self._scr == None or not self._scr.isOpen():
                if enabledRecyclerDenom:
                    for i in enabledRecyclerDenom:
                        if i not in range(1,8):
                            raise Exception("Recyler Denom index start with 1 and end with 7, current invalid denom index: {}".format(i))                
                self._enableRecycler = enableRecycler
                self._enabledRecyclerDenom = enabledRecyclerDenom

                if self._settings["PREF_DEBUG_LOGGING_ENABLED"]:
                    self._scr = Recycler(self._settings["PREF_DEBUG_PATH"])
                    raise Exception("TODO: ADD CHECK FILE or FOLDER DEBUGLOG EXIST")
                else:
                    self._scr = Recycler()
                self._APIVERSION = self._scr.getApiVersion()
                self._scr.addRecyclerListener(self)
                self._scr.open(self._settings["PREF_PORT"], self._settings["PREF_POWER_UP_POLICY"])
                LOG.bvlog("[MEI]: OPENED ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "")
            else:
                self.close()
                self._recyclerError = ""
                self._isRecylerEnabled = None
                result=self.open(mei_port, enableRecycler, enabledRecyclerDenom)
            return result
        except Exception as ex:
            trace = traceback.format_exc()
            LOG.bvlog("[MEI]: open ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, trace)
            return False, "", str(ex)

    
    def close(self):
        self._scr.removeRecyclerListener(self)
        self._scr.close()
        LOG.bvlog("[MEI]: CLOSED ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "")
    
    
    def startAcceptBill(self):
        message_out = ""
        try:
            if not self._scr.isOpen():
                raise Exception("SCR Not Opened")
            self._scr.enableAcceptance()
            return True, message_out, "OK"
        except Exception as ex:
            trace = traceback.format_exc()
            LOG.bvlog("[MEI]: startAcceptBill ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, trace)
            return False, message_out, str(ex)
    
    
    def stopAcceptBill(self):
        message_out = ""
        try:
            if not self._scr.isOpen():
                raise Exception("SCR Not Opened")
            self._scr.disableAcceptance()
            return True, message_out, "OK"
        except Exception as ex:
            trace = traceback.format_exc()
            LOG.bvlog("[MEI]: stopAcceptBill ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, trace)
            return False, message_out, str(ex)


    def storeNotesBill(self):
        message_out = ""
        try:
            if not self._scr.isOpen():
                raise Exception("SCR Not Opened")
            message_out = self.createMessage()
            devState = self._scr.getDeviceState()
            if (devState == DeviceState.IDLE_IN_ESCROW_SESSION) or (devState == DeviceState.HOST_DISABLED_IN_ESCROW_SESSION) or (devState == DeviceState.ESCROW_STORAGE_FULL):
                self._scr.storeEscrowedDocuments()
            else:
                raise Exception("Unable To Store Note, Current DeviceState: {}".format(devState))
            return True, message_out, "OK"
        except Exception as ex:
            trace = traceback.format_exc()
            LOG.bvlog("[MEI]: storeNotesBill ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, trace)
            return False, message_out, str(ex)


    def rejectNotesBill(self):
        message_out = ""
        try:
            if not self._scr.isOpen():
                raise Exception("SCR Not Opened")
            message_out = self.createMessage()
            devState = self._scr.getDeviceState()
            if devState == DeviceState.ESCROWED:
                self._scr.returnDocument()
            elif (devState == DeviceState.IDLE_IN_ESCROW_SESSION) or (devState == DeviceState.HOST_DISABLED_IN_ESCROW_SESSION) or (devState == DeviceState.ESCROW_STORAGE_FULL):
                self._scr.returnEscrowedDocuments()
            else:
                raise Exception("Unable To Return Note, Current DeviceState: {}".format(devState))
            return True, message_out, "OK"
        except Exception as ex:
            trace = traceback.format_exc()
            LOG.bvlog("[MEI]: rejectNotesBill ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, trace)
            return False, message_out, str(ex)
    
    
    def getStatus(self):
        try:            
            return True, self.createMessage(), "OK"
        except Exception as ex:
            trace = traceback.format_exc()
            LOG.bvlog("[MEI]: getStatus ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, trace)
            return False, "", str(ex)
    
    
    def createMessage(self):
        if type(self._deviceState) == str:
            _deviceState = self._deviceState
        else:
            _deviceState = self._deviceState.toString()

        if type(self._cassetteStatus) == str:
            _cassetteStatus = self._cassetteStatus
        else:
            _cassetteStatus = self._cassetteStatus.toString()
        
        if type(self._transportStatus) == str:
            _transportStatus = self._transportStatus
        else:
            _transportStatus = self._transportStatus.toString()        

        count = "{}|_documentStatus={}|_disabledReason={}|_deviceState={}|_cassetteStatus={}|_transportStatus={}|_cheatDetected={}|_transportOpenedWhilePoweredOff={}|_currentStackedEscrow={}|_isRecylerEnabled={}|_recylerError={}".format(len(self._currentStackedEscrow),self._documentStatus,self._scr.getDisabledReason(),_deviceState,_cassetteStatus,_transportStatus,self._cheatDetected,self._transportOpenedWhilePoweredOff,self._currentStackedEscrow, self._isRecylerEnabled, self._recyclerError)
        message = "Received=IDR|Denomination={}|Version={}|SerialNumber={}|Go={}".format(self._currentValueInEscrowStack,self._APIVERSION,self._serialNumber,count)
        return message

    @JOverride
    def cassetteStatusChanged(self,event:CassetteStatusEvent):
        self._cassetteStatus = event.getStatus()
        disabledReason = self._scr.getDisabledReason()
        LOG.bvlog("[MEI]: cassetteStatusChanged ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "{}|{}".format(self._cassetteStatus,disabledReason))
        # displayEvent(event.toString());

        # txtCassetteStatus.setText(event.getStatus().toString());
        # txtDisabledReason.setText(_scr.getDisabledReason().toString());

    @JOverride
    def cheatDetected(self):
        LOG.bvlog("[MEI]: cheatDetected ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, "")
        self._cheatDetected = int(time.time())
        # displayEvent("Cheat Event Detected");

    @JOverride
    def clearAuditCompleted(self,event:BoolResponseEvent):
        LOG.bvlog("[MEI]: clearAuditCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayEvent(String.format("Clear Audit Completed : %s", (event.getValue() ? "Successful" : "FAILED")));

    @JOverride
    def clearRecyclerNoteTableEnablesCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: clearRecyclerNoteTableEnablesCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("ClearRecyclerNoteTableEnablesAsync", event);

    @JOverride
    def deviceStateChanged(self,event:DeviceStateEvent):
        deviceState = event.getState()
        disabledReason = self._scr.getDisabledReason()
        LOG.bvlog("[MEI]: deviceStateChanged ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "{}|{}".format(deviceState,disabledReason))
        self._deviceState = deviceState
        if deviceState == DeviceState.IDLE or deviceState == DeviceState.HOST_DISABLED:
            self._serialNumber = self._scr.getSerialNumber()
            if self._isRecylerEnabled == None:
                _isRecylerEnabled = False
                for entry in self._scr.getRecyclerNoteTable():
                    if entry.isRecyclingEnabled():
                        _isRecylerEnabled = True
                        if self._enableRecycler and entry.getCount()>0:
                            if not self._enabledRecyclerDenom.__contains__(entry.getIndex()):
                                self._recyclerError = "Cannot specify the recycler note table, try re-setup recyler failed. Other banknotes exist on the drum(s)."
                                LOG.bvlog("[MEI]: TryEnableRecyler ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, self._recyclerError)
                                self._isRecylerEnabled = True
                                return
                self._isRecylerEnabled = _isRecylerEnabled
                if self._enableRecycler:
                    devCaps = self._scr.getDeviceCapabilities()
                    len_enabledRecyclerDenom= len(self._enabledRecyclerDenom)
                    maxNumberDenom = devCaps.getMaxNumberOfRecyclableDenominations()
                    if len_enabledRecyclerDenom not in range(1,maxNumberDenom+1):
                        self._recyclerError = "Recyler Denom list count must be 1 to {} denoms, current len: {}".format(maxNumberDenom,len_enabledRecyclerDenom)
                        LOG.bvlog("[MEI]: TryEnableRecyler ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, self._recyclerError)
                        return
                    self._scr.setRecyclerNoteTableEnables(self._enabledRecyclerDenom)
                    self._isRecylerEnabled = True
                else:
                    self._scr.clearRecyclerNoteTableEnables()
                    self._isRecylerEnabled = False

        # displayEvent(event.toString());

        # // Update the status text box
        # txtDeviceState.setText(event.getState().toString());
        # txtDisabledReason.setText(_scr.getDisabledReason().toString());

    @JOverride
    def dispenseByCountCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: dispenseByCountCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("DispenseByCountAsync", event);

    @JOverride
    def dispenseByValueCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: dispenseByValueCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("DispenseByValueAsync", event);

    @JOverride
    def dispenseUnknownDocumentsCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: dispenseUnknownDocumentsCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("DispenseUnknownDocumentsAsync", event);

    @JOverride
    def documentStatusReported(self,event:DocumentStatusEvent):
        docEvent = event.getEvent()
        doc = event.getDocument()
        route = event.getRoute()
        LOG.bvlog("[MEI]: DocumentStatus EVENT ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "{}, DOC {}, ROUTE {}".format(docEvent, doc, route))

        self._documentStatus = docEvent

        if docEvent == DocumentEvent.ESCROWED: 
            iso = doc.getISO()
            if iso == "IDR" :
                note = doc.getValue()
                self._scr.stackDocumentToEscrow()
                LOG.bvlog("[MEI]: DocumentStatus ESCROWED ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, note)
            else:
                self._scr.returnDocument()
                LOG.bvlog("[MEI]: DocumentStatus ESCROWED ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, "INVALID CURRENCY {}".format(iso))
        elif docEvent == DocumentEvent.STACKED:
            iso = doc.getISO()
            if iso == "IDR" :
                if route == DocumentRoute.CUSTOMER_TO_ESCROW_STORAGE:
                    note = doc.getValue()
                    self._currentValueInEscrowStack += note
                    self._currentStackedEscrow.append(note)
                    LOG.bvlog("[MEI]: DocumentStatus STACKED ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, {"ADDED":note, "NOW":self._currentValueInEscrowStack})
                elif route == DocumentRoute.ESCROW_STORAGE_TO_INVENTORY:
                    self._currentValueInEscrowStack = 0
                    self._currentStackedEscrow.clear()
                    LOG.bvlog("[MEI]: DocumentStatus CLEARED TO CASSETE ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "")
            else:
                LOG.bvlog("[MEI]: DocumentStatus STACKED ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, "INVALID CURRENCY {}".format(iso))



        # // Save off this document so we can reference it later
        # _document = event.getDocument();

        # displayEvent(event.toString());

    @JOverride
    def downloadProgressReported(self,event:DownloadProgressEvent):
        LOG.bvlog("[MEI]: downloadProgressReported ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayEvent(event.toString());

    @JOverride
    def escrowSessionSummaryReported(self,event:EscrowSessionSummaryEvent):
        LOG.bvlog("[MEI]: escrowSessionSummaryReported ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        for doc in event.getDocumentEntries():
            iso = doc.getISO()
            if iso == "IDR":
                note = doc.getValue()
                ret = doc.getReturnedCount()
                esc = doc.getPendingStorage()
                cas = doc.getStackedToCassetteCount()
                rec = doc.getStackedToRecyclerCount()
                mis = doc.getMissingCount()
                if ret > 0:
                    for i in range(0, ret):
                        self._currentValueInEscrowStack -= note
                        self._currentStackedEscrow.remove(note)
                if esc > 0:
                    for i in range(0, esc):
                        self._currentValueInEscrowStack += note
                        self._currentStackedEscrow.append(note)
                if cas > 0:
                    for i in range(0, cas):
                        self._currentValueInEscrowStack -= note
                        self._currentStackedEscrow.remove(note)                
                if mis > 0:
                    for i in range(0, mis):
                        self._currentValueInEscrowStack -= note
                        self._currentStackedEscrow.remove(note)
                if rec > 0:
                    for i in range(0, rec):
                        self._currentValueInEscrowStack -= note
                        self._currentStackedEscrow.remove(note)

        # displayEvent(event.toString());

    @JOverride
    def flashDownloadCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: flashDownloadCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("FlashDownloadAsync", event);

    @JOverride
    def floatDownAllCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: floatDownAllCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("FloatDownAllAsync", event);

    @JOverride
    def floatDownByCountCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: floatDownByCountCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("FloatDownByCountAsync", event);

    @JOverride
    def floatDownUnknownDocumentsCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: floatDownUnknownDocumentsCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("FloatDownUnknownDocumentsAsync", event);

    @JOverride
    def setRecyclerNoteTableEnablesCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: setRecyclerNoteTableEnablesCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("SetRecyclerNoteTableEnablesAsync", event);

    @JOverride
    def missingNotesReported(self,event:MissingNotesEvent):
        LOG.bvlog("[MEI]: missingNotesReported ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, event.toString())
        # displayEvent(event.toString());

    @JOverride
    def openCompleted(self,event:AsyncCompletedEvent):
        LOG.bvlog("[MEI]: openCompleted ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, event.toString())
        # displayAsyncEvent("OpenAsync", event);

    @JOverride
    def transportOpenedWhilePoweredOff(self):
        LOG.bvlog("[MEI]: transportOpenedWhilePoweredOff ", LOG.INFO_TYPE_ERROR, LOG.FLOW_TYPE_PROC, "")
        self._transportOpenedWhilePoweredOff = int(time.time())
        # displayEvent("Transport Opened While Powered Off Event Detected");

    @JOverride
    def transportStatusChanged(self,event:TransportStatusEvent):
        self._transportStatus = event.getStatus()
        disabledReason = self._scr.getDisabledReason()
        LOG.bvlog("[MEI]: transportStatusChanged ", LOG.INFO_TYPE_INFO, LOG.FLOW_TYPE_PROC, "{}|{}".format(self._transportStatus,disabledReason))
        # displayEvent(event.toString());

        # // Update the status text box
        # txtTransportStatus.setText(event.getStatus().toString());
        # txtDisabledReason.setText(_scr.getDisabledReason().toString());    
    
    
MEI = None
LOOP_ATTEMPT = 0
MAX_LOOP_ATTEMPT = 90


def send_command(param=None, config=[], recycleNotes=[]):
    global MEI, LOOP_ATTEMPT
    try:
        # if _Helper.empty(param) or _Helper.empty(config):
        #     return -1, ""
        if MEI is None:
            MEI = MeiDevice()
        args = param.split('|')
        command = args[0]
        param = "0"
        if len(args[1:]) > 0:
            param = "|".join(args[1:])
        err = ''
        LOGGER.debug((command, param, config))
        # Define Command
        if command == config['SET']:
            res, msg, err = MEI.open(
                config['PORT'],
                len(recycleNotes) > 0,
                recycleNotes
            )
            if res is True:
                # Do Soft Reset
                return 0, "0000"
            else:
                MEI = None
                return -1, err
        elif command == config['RECEIVE']:
            LOOP_ATTEMPT = 0
            res, msg, err = MEI.startAcceptBill()
            if res is True:
                while True:
                    res, msg, err = MEI.getStatus()
                    LOOP_ATTEMPT += 1
                    # Need To Handle This False Denom Read
                    if 'Received=IDR|Denomination=0' in msg:
                        continue
                    if config['KEY_RECEIVED'] in msg:
                        return 0, msg
                    if config['KEY_BOX_FULL'] in msg:
                        # MEI.stopAcceptBill()
                        return -1, msg
                    if config['CODE_JAM'] in msg:
                        # MEI.stopAcceptBill()
                        return -1, msg
                    if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                        break
                    time.sleep(1)
                return -1, err
            else:
                return -1, err
        elif command == config['STORE']:
            LOOP_ATTEMPT = 0
            res, msg, err = MEI.storeNotesBill()
            if res is True:
                while True:
                    res, msg, err = MEI.getStatus()
                    LOOP_ATTEMPT += 1
                    if config['KEY_STORED'] in msg:
                        return 0, msg
                    if config['KEY_BOX_FULL'] in msg:
                        return -1, msg
                    if config['CODE_JAM'] in msg:
                        # MEI.stopAcceptBill()
                        return -1, msg
                    # if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                    # Set Harcoded only wait for 3 Seconds
                    if LOOP_ATTEMPT >= 3: 
                        break
                    time.sleep(1)
                return 0, msg
            else:
                return -1, err
        elif command == config['REJECT']:
            # Auto Reject
            LOOP_ATTEMPT = 0
            err = ''
            while True:
                res, msg, err = MEI.getStatus()
                LOOP_ATTEMPT += 1
                if "REJECTED" in msg or 'RETRIEVED' in msg:
                    return 0, msg
                if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                    break
                time.sleep(1)
            return -1, err
        elif command == config['RESET']:
            res, msg, err = MEI.open(
                config['PORT'],
                len(recycleNotes) > 0,
                recycleNotes
            )
            if res is True:
                # Do Soft Reset
                return 0, "Bill Reset"
            else:
                return -1, err
        elif command == config['STOP']:
            LOOP_ATTEMPT = MAX_LOOP_ATTEMPT
            res, msg, err = MEI.stopAcceptBill()
            if res is True:
                while True:
                    res, msg, err = MEI.getStatus()
                    LOOP_ATTEMPT += 1
                    if 'deviceState=HOST_DISABLED' in msg:
                        return 0, msg
                    if config['KEY_BOX_FULL'] in msg:
                        # MEI.stopAcceptBill()
                        return -1, msg
                    if config['CODE_JAM'] in msg:
                        # MEI.stopAcceptBill()
                        return -1, msg
                    if LOOP_ATTEMPT >= MAX_LOOP_ATTEMPT:
                        break
                    time.sleep(1)
                return -1, err
            else:
                return -1, err
        else:
            return -1, err
    except Exception as e:
        error_string = traceback.format_exc()
        LOGGER.warning((e))
        LOGGER.debug(error_string)
        return -99, str(e)
    
    
