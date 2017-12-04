#!/usr/bin/env python

__author__ = 'Kanishka Ganguly'
__version__ = '1.0.0'
__date__ = 'May 25 2017'

import time


class file_io:
    ''' FILE IO '''

    def open_file(self, root_dir, glove_type=None, cam=None):
        if cam is not None:
            text_file = ('%s/Cam%dTimestamp.txt') % (root_dir, cam)
            save_log = open(text_file, 'w')
            print 'Opened camera %d log...' % (cam)
            return save_log
        else:
            text_file = ('%s/%sTimestamp.txt') % (root_dir, glove_type)
            save_log = open(text_file, 'w')
            print 'Opened glove log...'
            return save_log

    def close_file(self, save_log):
        save_log.close()
        print 'Closed log file...'
        return

    ''' Writes images or log for IMU
        Force glove is async, log writer in that class
    '''

    def write_log(self, save_log, idx=None, glove_data=None):
        if idx is not None:
            to_log = ('%f,capture_rgb_%04d.png\r\n') % (time.time(), idx)
            if not save_log.closed:
                save_log.write(to_log)
        else:
            if glove_data is not None:
                to_log = ('%f,%s\r\n') % (time.time(), glove_data)
                if not save_log.closed:
                    save_log.write(to_log)
