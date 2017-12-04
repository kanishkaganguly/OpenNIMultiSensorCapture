#!/usr/bin/env python

__author__ = 'Kanishka Ganguly'
__version__ = '1.0.0'
__date__ = 'May 25 2017'

import serial

''' SERIAL IO FUNCTIONS'''


def data_fetch_type(val):
    if val is 'QUATERNIONS_START':
        return b'1\r\n'
    elif val is 'QUATERNIONS_STOP':
        return b'0\r\n'
    elif val is 'DATA_SNAPSHOT':
        # Get quaternion + accel data together
        return b'z\r\n'
    elif val is 'RAW_START':
        return b'F\r\n'
    elif val is 'RAW_STOP':
        return b'H\r\n'
    elif val is 'SET_ASCII':
        return b'W\r\n'
    elif val is 'VERSION':
        return b'V\r\n'


def open_port():
    ser = serial.Serial('/dev/ttyACM0', baudrate='115200', timeout=0.01)
    print 'Opened serial device %s' % ser.name
    return ser


def close_port(ser):
    ser.close()
    print 'Serial port closed...'
    return


def fetch_data(ser, data_type):
    ser.write(data_type)
    got_data = ser.readline()
    ser.flushInput()
    ser.flushOutput()
    return got_data
