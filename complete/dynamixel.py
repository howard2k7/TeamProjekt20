import serial
import serialPorts
import copy


# Classdefinition to implement dynamixel protocol
# ===============================================================================
# Implements the dynamixel protocol 1.0
# ------------------------------------------------------------------------------
# Assigns the class object to a dedicated servo by the servo id
# Initializes the serial connection to the servo bus
# Handles the transfer of all required packet types with 1..n data bytes or -words


class Dynamixel:
    # Definition of protected class attributes
    # Accessible only within own and derived classes 
    # ---------------------------------------------------------------------------
    _ID_BROADCAST = 0xFE

    # Definition of private class attributes, accessible only within own class
    # ---------------------------------------------------------------------------
    # Define dynamixel constants
    __DYNAMIXEL_PORT_NR = 0  # Index of dynamixel line in list
    __BAUDRATE = 1000000  # Baudrate of dynamixel serial line
    __TIME_OUT_DEFAULT = 2  # Default time out
    __DIRECT_ACTION = 3  # Direct action command
    __TRIGGERT_ACTION = 4  # Triggered action command
    __STATUS_PACKET_BASE_LENGTH = 6  # Base length of status packet

    __lines = serialPorts.serialPortList()  # Contains all available serial lines

    print((__lines))  # Show all available Ports in output

    # __DYNAMIXEL_PORT_NR
    # 1000000
    __serial_port = serial.Serial(port=__lines[__DYNAMIXEL_PORT_NR], baudrate=__BAUDRATE)

    # Create templates of command packets
    # ToDo: use this insteed of hardcoded data
    __pktAction = [255, 255, 0, 2, 5, 0]  # Packet to invoke action
    __pktReadData = [255, 255, 0, 4, 2, 0, 0, 0]  # Packet to request date
    __pktWriteByte = [255, 255, 0, 4, 3, 0, 0, 0]  # Packet to write byte
    __pktWriteNByte = [255, 255, 0, 0, 3, 0]  # Base-packet to write n-bytes
    __pktWriteWord = [255, 255, 0, 5, 3, 0, 0, 0, 0]  # Packet to write word

    # Position of fields in Arrays:
    POS_ID = 2
    POS_LEN = 3
    POS_INS = 4
    POS_ERR = 4
    POS_PARAM = 5
    POS_CHKSUM = -1

    # Commandlist:
    COM_PING = 1
    COM_READ = 2
    COM_WRITE = 3
    COM_REGWR = 4
    COM_ACTION = 5
    COM_RESET = 6
    COM_SYNCWR = 7

    # value for error
    ERR_INPUT_VOLTAGE = 2 ** 0
    ERR_ANGLE_LIMIT = 2 ** 1
    ERR_OVERHEATING = 2 ** 2
    ERR_RANGE = 2 ** 3
    ERR_CHECKSUM = 2 ** 4
    ERR_OVERLOAD = 2 ** 5
    ERR_INSTRUCTION = 2 ** 6
    ERR_DEFAULT = 0

    # ---------------------------------------------------------------------------
    # Definition of private methods with implicit servo-id
    # Accessible only within own class
    # ---------------------------------------------------------------------------
    # Constructor, sets id and defines error variable
    # id -> id of attached servo
    def __init__(self, id):
        self.id = id
        self.error = self.ERR_DEFAULT

    # Start predefined action on servo
    # id -> id of servo to ping, without id -> broadcast action
    def __doAction(self, id: int = _ID_BROADCAST):
        action = [255, 255, 0, 0, 0, 0]
        action[self.POS_ID] = id
        action[self.POS_LEN] = 2
        action[self.POS_INS] = self.COM_ACTION
        action[self.POS_CHKSUM] = self.__checkSum(action)

        self._doAction(action)

    # Prepares and sends packet to servo in order to read data from servo memory
    # register -> register address of servo
    # nByte    -> number of bytes to read
    def __writeReadDataPkt(self, register, nByte):

        action = [255, 255, 0, 0, 0, 0, 0, 0]
        action[self.POS_ID] = self.id
        action[self.POS_LEN] = 4
        action[self.POS_INS] = Dynamixel.COM_READ
        action[self.POS_PARAM] = register
        action[self.POS_PARAM + 1] = nByte
        action[self.POS_CHKSUM] = self.__checkSum(action)

        self._doAction(action)

    # Read status packet, set error value and get return values from servo
    # nByte    -> number of bytes to read
    def __readStatusPkt(self, nByte):

        parameter, self.error = self.__doReadStatusPkt(nByte)

        return parameter

    # Read status packet, set error value and get return values from servo
    # nByte -> number of bytes to read
    def __doReadStatusPkt(self, nByte):

        statusPkt = list(self.__serial_port.read(Dynamixel.__STATUS_PACKET_BASE_LENGTH + nByte))

        if len(statusPkt) > 0 and statusPkt[self.POS_CHKSUM] == self.__checkSum(statusPkt):
            return statusPkt[self.POS_PARAM : self.POS_CHKSUM], self.ERR_DEFAULT
        else:
            return None, self.ERR_CHECKSUM

    # Calculates check sum of packet list
    def __checkSum(self, pkt):
        s = sum(pkt[2:-1])                              # add all values from servo-id to last parameter
        return (~s) & 0xFF                              # invert sum bit-wise and limit to byte range

    # Definition of protected methods
    # Accessible within own and derived classes
    # ---------------------------------------------------------------------------
    # Read data byte from servo memory
    # register -> register address of servo
    # dtLen    -> number of data bytes to read
    def _requestNByte(self, register, dtLen=1):
        self.__writeReadDataPkt(register, dtLen)
        return self.__readStatusPkt(dtLen)

    # Read data word from servo memory
    # register -> register address of servo
    # dtWLen   -> number of data words to read
    def _requestNWord(self, register, dtWlen=1):
        self.__writeReadDataPkt(register, dtWlen * 2)
        return self.__readStatusPkt(dtWlen * 2)

    # Sends packet to servo in order to write n data bytes into servo memory
    # register -> register address of servo
    # data     -> list of bytes to write
    # trigger  -> False -> command is directly executed, True -> command is delayed until action command
    def _writeNBytePkt(self, register, data, trigger):
        action = [255, 255, 0, 0, 0, 0]
        action[self.POS_ID] = self.id
        action[self.POS_LEN] = len(data) + 3
        if trigger:
            action[self.POS_INS] = self.COM_REGWR
        else:
            action[self.POS_INS] = self.COM_WRITE
        action[self.POS_PARAM] = register
        action.extend(data)
        action.append(0)
        action[-1] = self.__checkSum(action)

        self._doAction(action)

    # Sends packet to servo in order to write data dword into servo memory
    # register -> register address of servo
    # data     -> list of words to write
    # trigger  -> False -> command is directly executed, True -> command is delayed until action command
    def _writeNWordPkt(self, register, data, trigger):
        # ToDo: write function for byte-> int, int->byte
        byteData = []
        for word in data:
            byteData.append(word & 255)
            byteData.append(word >> 8 )

        self._writeNBytePkt(register, byteData, trigger)

    def _doAction(self, action):
        self.__serial_port.write(action)

    # Definition of public methods with implicit servo-id
    # Accessible from everywere
    # ---------------------------------------------------------------------------
    # Show available serial lines
    def showSerialLines(self):
        print(Dynamixel.__lines)

    # Start predefined action on servo with assigned id
    def action(self):
        return self.__doAction(self.id)

    # Get last error
    def getLastError(self):
        return self.error
