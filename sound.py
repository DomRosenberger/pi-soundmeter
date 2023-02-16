'''Script to communicate with PeakTech8005.'''

import logging
import sys
import serial

logger = logging.getLogger('my-logger')


class PeakTech8005:
    '''PeakTeach8005 class with basic read and write functions.'''
    SYNC = b'\xa5'
    INDICATOR_DBA = b'\x1B'
    INDICATOR_DBC = b'\x1C'
    INDICATOR_DATA = b'\x0D'
    POWER_OFF = b'\x33'
    TRANSMIT = b'\x5A\xAC'
    TOGGLE_RECORD = b'\x55'
    TOGGLE_DISPLAY_MAX = b'\x11'
    TOGGLE_DISPLAY_FAST = b'\x77'
    TOGGLE_RANGE = b'\x88'
    TOGGLE_DBA_DBC = b'\x99'
    DATA_ERROR = -1

    def __init__(self, serial_port='/dev/ttyUSB0'):
        self.state_dba_dbc = "unkown"
        try:
            self.ser = serial.Serial(serial_port)
            self.ser.isOpen()
            self.ser.write(self.TRANSMIT)
        except IOError:
            logging.error(f'IO Error: Can not connect to {serial_port}')
            sys.exit()

    def read(self,num=1):
        ''' Read data from serial port '''
        data = self.ser.read(num)
        return data

    def _send_cmd(self, cmd):
        self.ser.write(cmd)

    def off(self):
        ''' Turn off device '''
        self._send_cmd(self.POWER_OFF)

    def rec(self):
        ''' Starts/stops recording in PT8005
            Not needed to read data via serial port.
        '''
        self._send_cmd(self.TOGGLE_RECORD)

    def display(self):
        ''' Switch display mode fast/slow '''
        self.ser.write(self.TOGGLE_DISPLAY_FAST)

    def range(self):
        ''' Switch range '''
        self.ser.write(self.TOGGLE_RANGE)

    def type(self):
        ''' Switch dBA/dBC '''
        self.ser.write(self.TOGGLE_DBA_DBC)

    def stream(self):
        '''Stream db levels.'''
        logger.info('Start streaming sound')
        while True:
            data = self.read(1)                     # ready byte from serial
            if data == self.SYNC:                   # sync found?
                data = self.read(1)                 # read next
                if data == self.INDICATOR_DBA:
                    self.state_dba_dbc = self.INDICATOR_DBA
                if data == self.INDICATOR_DBC:
                    self.state_dba_dbc = self.INDICATOR_DBC
                if data == self.INDICATOR_DATA:
                    try:
                        data1 = self.read(1)              # read next
                        data2 = self.read(1)              # read next
                        part1 = data1[0]                  # byte 1
                        part2 = bytes([data2[0] >> 4])    # byte 2 - extract bit 5-8
                        part3 = bytes([data2[0] & 15])    # byte 2 - extract bit 1-4
                        value = (part1*10)+int(part2.hex())+(int(part3.hex())/10)
                        return value
                    except ValueError:
                        logger.error(f'valueerror: {data}')
                        return self.DATA_ERROR
