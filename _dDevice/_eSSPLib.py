__author__ = 'wahyudi@multidaya.id'

import datetime
import serial
import time

class eSSPError(IOError):  # noqa
    """Generic error exception for eSSP problems."""
    pass

class eSSPTimeoutError(eSSPError):  # noqa
    """Indicates a timeout while communicating with the eSSP device."""
    pass

class eSSP(object):  # noqa
    """General class for talking to an eSSP device."""
    
    def __init__(self, serialport='/dev/ttyUSB0', eSSPId=0, timeout=None):  # noqa
        """
        Initialize a new eSSP object.

        The timeout parameter corresponds to the pySerial timeout parameter,
        but is used a bit different internally. When the parameter isn't set
        to None (blocking, no timeout) or 0, (non-blocking, return directly),
        we set a timeout of 0.1 seconds on the serial port, and perform reads
        until the specified timeout is expired. When the timeout is reached
        before the requested data is read, a eSSPTimeoutError will be raised.
        """
        if timeout is None or timeout == 0:
            serial_timeout = timeout
        else:
            serial_timeout = 0.1
        self.timeout = timeout
        self.__ser = serial.Serial(serialport, 9600, timeout=serial_timeout)
        self.__eSSPId = eSSPId
        self.__sequence = '0x80'
        self.__timeout_excp = ['0xETIMEDOUT']

        # self._logger = logging.getLogger(__name__)
        # self._logger.debug("Startup at " + str(datetime.datetime.now()))
        
    def release(self):
        try:
            self.__ser.close()
            del self.__ser
            self.__ser = None
        except Exception as e:
            print(e)
            self.__ser = None
        finally:
            return self.__ser is None

    def reset(self):
        """Reset the device completely."""
        result = self.send([self.getseq(), '0x1', '0x1'])
        return result

    def set_inhibits(self, lowchannels, highchannels):
        # lowchannels: Channel 1 to 8
        # highchannels: Channel 9 to 16
        # takes a bitmask
        # For more ease: use easy_inhibit() as helper
        result = self.send([self.getseq(), '0x3', '0x2', lowchannels, highchannels])
        return result

    def bulb_on(self):
        """Illuminate bezel."""
        result = self.send([self.getseq(), '0x1', '0x3'])
        return result

    def bulb_off(self):
        """Nox bezel."""
        result = self.send([self.getseq(), '0x1', '0x4'])
        return result

    def configure_bezel(self, red, green, blue, volatile, bezel_type):
        result = self.send([self.getseq(), '0x6', '0x54', red, green, blue, volatile, bezel_type])
        return result

    def setup_request(self):
        # Response consits of
        # Unit-Type (0 = BNV)
        # Firmware-Version
        # Country-Code
        # Value Multiplier
        # Number of channels
        # Channels Value array()
        # Security of Channels array()
        # Real value Multiplier
        # Protocol Version
        # 1 = Low Security
        # 2 = Std Security
        # 3 = High Security
        # 4 = Inhibited
        result = self.send([self.getseq(), '0x1', '0x5'], False)

        unittype = int(result[4], 16)

        fwversion = ''
        for i in range(5, 9):
            fwversion += chr(int(result[i], 16))

        country = ''
        for i in range(9, 12):
            country += chr(int(result[i], 16))

        valuemulti = int('00', 16)
        for i in range(12, 15):
            valuemulti += int(result[i], 16)

        channels = int(result[15], 16)

        values = []
        for i in range(0, channels):
            values.append(int(result[i + 16], 16))

        security = []
        for i in range(0, channels):
            security.append(int(result[i + 16 + channels], 16))

        multiplier = 0
        for i in range(16 + 2 * channels, 16 + 2 * channels + 3):
            multiplier += int(result[i], 16)

        protocol = int(result[16 + 2 * channels + 3], 16)

        unit_data = [unittype, fwversion, country, valuemulti, channels, values, security, multiplier, protocol]

        return unit_data

# Don't even know what this is doing...
#   def host_protocol(self, host_protocol):
#       result = self.send([self.getseq(), '0x2', '0x6', host_protocol])
#       return result

    def poll(self):
        """
        Poll the device.
        0xF1 = Slave Reset (right after booting up)
        0xEF = Read Note + Channel Number array()
        0xEE = Credit Note + Channel Number array()
        0xED = Rejecting
        0xEC = Rejected
        0xCC = Stacking
        0xEB = Stacked
        0xEA = Safe Jam
        0xE9 = Unsafe Jam
        0xE8 = Disabled
        0xE6 = Fraud attempt + Channel Number array()
        0xE7 = Stacker full
        0xE1 = Note cleared from front at reset (Protocol v3)
                + Channel Number array()
        0xE2 = Note cleared into cashbox at reset (Protocol v3)
                + Channel Number array()
        0xE3 = Cash Box Removed (Protocol v3)
        0xE4 = Cash Box Replaced (Protocol v3)
        """
        result = self.send([self.getseq(), '0x1', '0x7'], False)
        # result = self.send_only([self.getseq(), '0x1', '0x7'])

        poll_data = []
        try:
            for i in range(3, int(result[2], 16) + 3):
                if result[i] in ('0xef', '0xee', '0xe6', '0xe1', '0xe2'):
                    poll_data.append([result[i], int(result[i + 1], 16)])
                    i += 1
                else:
                    poll_data.append(result[i])
        except Exception as e:
            # print(e, str(result))
            if len(result) > 0:
                poll_data.append(result[0])
            pass

        return poll_data

    def reject_note(self):
        """Reject the current note."""
        result = self.send([self.getseq(), '0x1', '0x8'])
        return result

    def reject_note_no_response(self):
        """Reject the current note."""
        result = self.send_only([self.getseq(), '0x1', '0x8'])
        return result

    def disable(self):
        """
        Disable the device.

        Will resume to work only when beeing enable()'d again.
        """
        result = self.send([self.getseq(), '0x1', '0x9'])
        return result

    def enable(self):
        """Resume from disable()'d state."""
        result = self.send([self.getseq(), '0x1', '0xA'])
        return result

    # SSP_CMD_PROGRAM 0xB not implented

    def serial_number(self):
        """Return formatted serialnumber."""
        result = self.send([self.getseq(), '0x1', '0xC'], False)

        serial = 0
        for i in range(4, 8):
            serial += int(result[i], 16) << (8 * (7 - i))

        return serial

    def unit_data(self):
        # Response consits of
        # Unit-Type (0 = BNV)
        # Firmware-Version
        # Country-Code
        # Value-Multiplier
        # Protocol-Version
        result = self.send([self.getseq(), '0x1', '0xD'], False)

        unittype = int(result[4], 16)

        fwversion = ''
        for i in range(5, 9):
            fwversion += chr(int(result[i], 16))

        country = ''
        for i in range(9, 12):
            country += chr(int(result[i], 16))

        valuemulti = int('00', 16)
        for i in range(12, 15):
            valuemulti += int(result[i], 16)

        protocol = int(result[15], 16)

        unit_data = [unittype, fwversion, country, valuemulti, protocol]

        return unit_data

    def channel_values(self):
        """
        Return the real values of the channels.

        - Number of Channels
        - Values of Channels
        """
        result = self.send([self.getseq(), '0x1', '0xE'], False)

        channels = int(result[4], 16)

        unitdata = self.unit_data()

        values = []
        for i in range(0, channels):
            values.append(int(result[5 + i], 16) * unitdata[3])

        channel_data = [channels, values]
        return channel_data

    def channel_security(self):
        """
        Return the security settings of all channels.

        Number of Channels
        Security Data array()
        1 = Low Security
        2 = Std Security
        3 = High Security
        4 = Inhibited
        """
        result = self.send([self.getseq(), '0x1', '0xF'], False)

        channels = int(result[4], 16)

        security = []
        for i in range(0, channels):
            security.append(int(result[i + channels + 1], 16))

        security_data = [channels, security]
        return security_data

    def channel_reteach(self):
        """
        Return the (somewhat un-useful?) Re-Teach Data by Channel.

        Number of Channels
        Value of Reteach-Date array()
        """
        result = self.send([self.getseq(), '0x1', '0x10'], False)

        channels = int(result[4], 16)

        reteach = []
        for i in range(0, channels):
            reteach.append(int(result[i + channels + 1], 16))

        reteach_result = [channels, reteach]
        return reteach_result

    def sync(self):
        """
        Reset Sequence to be 0x00.

        Set ssp_sequence to 0x00, so next will be 0x80 by default
        """
        self.__sequence = '0x00'

        result = self.send([self.getseq(), '0x1', '0x11'])
        return result

    # SSP_CMD_DISPENSE 0x12 not implemented

    # SSP_CMD_PROGRAM_STATUS 0x16 not implemented

    def last_reject(self):
        """Get reason for latest rejected banknote.

        0x00 = Note Accepted
        0x01 = Note length incorrect
        0x02 = Reject reason 2
        0x03 = Reject reason 3
        0x04 = Reject reason 4
        0x05 = Reject reason 5
        0x06 = Channel Inhibited
        0x07 = Second Note Inserted
        0x08 = Reject reason 8
        0x09 = Note recognised in more than one channel
        0x0A = Reject reason 10
        0x0B = Note too long
        0x0C = Reject reason 12
        0x0D = Mechanism Slow / Stalled
        0x0E = Striming Attempt
        0x0F = Fraud Channel Reject
        0x10 = No Notes Inserted
        0x11 = Peak Detect Fail
        0x12 = Twisted note detected
        0x13 = Escrow time-out
        0x14 = Bar code scan fail
        0x15 = Rear sensor 2 Fail
        0x16 = Slot Fail 1
        0x17 = Slot Fail 2
        0x18 = Lens Over Sample
        0x19 = Width Detect Fail
        0x1A = Short Note Detected
        """
        result = self.send([self.getseq(), '0x1', '0x17'], False)
        return result[4]

    def hold(self):
        result = self.send([self.getseq(), '0x1', '0x18'])
        return result

    # SPP_CMD_MANUFACTURER 0x30 not implemented, collides with SSP_CMD_EXPANSION?

    # SSP_CMD_EXPANSION 0x30 not implemented, collides with SSP_CMD_MANUFACTURER?

    def enable_higher_protocol(self):
        """Enable functions from implemented with version >= 3."""
        result = self.send([self.getseq(), '0x1', '0x19'])
        return result

# End Of Definition Of SSP_CMD_* Commands

    def getseq(self):
        # toggle SEQ between 0x80 and 0x00
        if (self.__sequence == '0x80'):
            self.__sequence = '0x00'
        else:
            self.__sequence = '0x80'

        returnseq = hex(self.__eSSPId | int(self.__sequence, 16))
        return returnseq

    def crc(self, command):
        length = len(command)
        seed = int('0xFFFF', 16)
        poly = int('0x8005', 16)
        crc = seed
        # self._logger.debug( " 1 || " + hex(crc) )

        for i in range(0, length):
            # self._logger.debug( " 2 || " + str(i) )
            crc ^= (int(command[i], 16) << 8)
            # self._logger.debug( " 3 || " + command[i] )
            # self._logger.debug( " 4 || " + hex(crc) )

            for j in range(0, 8):
                # self._logger.debug( " 5 || " + str(j) )

                if (crc & int('0x8000', 16)):
                    # self._logger.debug( " 6 || " + hex(crc) )
                    crc = ((crc << 1) & int('0xffff', 16)) ^ poly
                    # self._logger.debug( " 7 || " + hex(crc) )
                else:
                    crc <<= 1
                    # self._logger.debug( " 8 || " + hex(crc) )

        crc = [hex((crc & 0xFF)), hex(((crc >> 8) & 0xFF))]
        return crc

    def send(self, command, process=True):
        crc = self.crc(command)
        prepedstring = '7F'
        command = command + crc
        
        for i in range(0, len(command)):
            if (len(command[i]) % 2 == 1):
                prepedstring += '0'
            prepedstring += command[i][2:]

        # self._logger.debug("OUT: 0x" + ' 0x'.join([prepedstring[x:x + 2]
        #                    for x in range(0, len(prepedstring), 2)]))

        prepedstring = bytes.fromhex(prepedstring)
        #prepedstring = prepedstring.decode('hex')

        self.__ser.write(prepedstring)
        # response = True
        time.sleep(.25)
        response = self.read(process)
        # Direct Raw Debug
        # print('pyt: NV200 Debug : ', str(prepedstring), str(response))
        return response
    
    def send_only(self, command):
        crc = self.crc(command)
        prepedstring = '7F'
        command = command + crc
        for i in range(0, len(command)):
            if (len(command[i]) % 2 == 1):
                prepedstring += '0'
            prepedstring += command[i][2:]

        prepedstring = bytes.fromhex(prepedstring)

        self.__ser.write(prepedstring)
        # response = True
        # if process:
        # response = self.read(process)
        return ['0xf0']

    def read(self, process=True, break_in_empty = False):
        """Read the requested data from the serial port."""
        bytes_read = []
        # initial response length is only the header.
        expected_bytes = 3
        timeout_expired = datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)
        while True:
            byte = self.__ser.read()
            if byte:
                bytes_read += byte
            else:
                # when the socket doesn't give us any data, evaluate the timeout
                if datetime.datetime.now() > timeout_expired:
                    # How to handle this, retrigger the same command ???
                    if not process:
                        return self.__timeout_excp
                    else:
                        raise eSSPTimeoutError('Unable to read the expected response of {} bytes within {} seconds'.format(
                                                expected_bytes, self.timeout))

            if expected_bytes == 3 and len(bytes_read) >= 3:
                # extract the actual message length
                expected_bytes += bytes_read[2] + 2

            if expected_bytes > 3 and len(bytes_read) == expected_bytes:
                # we've read the complete response
                break

            if break_in_empty:
                if byte == b"":
                    break

        response = self.arrayify_response(bytes_read)
        # self._logger.debug("IN:  " + ' '.join(response))

        if process:
            response = self.process_response(response)
        return response

    def arrayify_response(self, response):
        array = []
        for i in range(0, len(response)):
            array += [hex(response[i])]
        return array

    def process_response(self, response):
        # Answers seem to be always in lowercase

        # Error-Codes
        # 0xf0   OK
        # 0xf2   Command not known
        # 0xf3   Wrong number of parameters
        # 0xf4   Parameter out of range
        # 0xf5   Command cannot be processed
        # 0xf6   Software Error
        # 0xf8   FAIL
        # 0xFA   Key not set

        # Default: Something failed
        processed_response = '0xf8'

        if response[0] == '0x7f':
            crc_command = []
            for i in range(1, int(response[2], 16) + 3):
                crc_command.append(response[i])

            crc = self.crc(crc_command)

            if (response[len(response) - 2] != crc[0]) & (response[len(response) - 1] != crc[1]):
                pass
                # self._logger.debug("Failed to verify crc.")
            else:
                processed_response = response[3]
                if response[3] != '0xf0':
                    pass
                    # self._logger.debug("Error " + response[3])
        return processed_response

    def easy_inhibit(self, acceptmask):
        channelmask = []
        bitmask = int('00000000', 2)

        channelmask.append(int('00000001', 2))
        channelmask.append(int('00000010', 2))
        channelmask.append(int('00000100', 2))
        channelmask.append(int('00001000', 2))
        channelmask.append(int('00010000', 2))
        channelmask.append(int('00100000', 2))
        channelmask.append(int('01000000', 2))
        channelmask.append(int('10000000', 2))

        for i in range(0, len(acceptmask)):
            if acceptmask[i] == 1:
                bitmask = bitmask + channelmask[i]

        bitmask = hex(bitmask)
        return bitmask
    
    def accept_note(self):
        accept_res = self.send_and_flush([self.getseq(), '0x1', '0x7'])
        if accept_res == self.__timeout_excp:
            self.send_and_flush([self.getseq(), '0x1', '0x7'])
        # print("SYNC")
        # self.sync()
    
    def send_and_flush(self, command):
        crc = self.crc(command)

        prepedstring = '7F'
        command = command + crc

        for i in range(0, len(command)):
            if (len(command[i]) % 2 == 1):
                prepedstring += '0'
            prepedstring += command[i][2:]

        prepedstring = bytes.fromhex(prepedstring)
        self.__ser.write(prepedstring)

        response = self.read(False, True)
        return response
    