#!/usr/bin/env python

__author__ = 'Kanishka Ganguly'
__version__ = '1.0.0'
__date__ = 'May 25 2017'

import argparse
import os
import threading
from capture_glove import *
from capture_force import *
from capture_cam import *
from file_io import *


def capture_and_save(cam_handle, cam_id, dir_to_write, log_writer, rgb_stream,
                     depth_stream, io, cam_disp):
    t = threading.currentThread()
    shot_idx = 0

    while getattr(t, "do_run", True):
        if rgb_stream is not None:
            # print "Capture %s camera %d frame..." % ("rgb", cam_id + 1)
            rgb_array = cam_handle.get_rgb(rgb_stream)
            rgb_array = cv2.cvtColor(rgb_array, cv2.COLOR_BGR2RGB)
            cam_disp['RGB' + str(cam_id)] = rgb_array
            cam_handle.save_frame('rgb', rgb_array, shot_idx, dir_to_write + str(cam_id + 1))
            io.write_log(log_writer[cam_id], shot_idx, None)

        if depth_stream is not None:
            # print "Capture %s camera %d frame..." % ("depth", cam_id + 1)
            depth_array = cam_handle.get_depth(depth_stream)
            cam_disp['DEPTH' + str(cam_id)] = ((depth_array / 10000.) * 255).astype(np.uint8)
            cam_handle.save_frame('depth', depth_array, shot_idx, dir_to_write + str(cam_id + 1))
        shot_idx = shot_idx + 1

    print "Stopping camera %d thread..." % (cam_id + 1)
    return


class capture_tool:
    def __init__(self, io, force_cap=None):
        self.io = io
        if force_cap is not None:
            self.force_cap = force_cap

    ''' GLOVE THREAD WORKER'''

    def parse_quat_accel_data(self, quat_accel_data):
        val_count = len(quat_accel_data.split(","))
        if (val_count) == 49:
            quat_accel_data = quat_accel_data.replace("\r\n", "")
            return quat_accel_data

    def imu_glove_capture(self, e, ser, log_file):
        while not e.isSet():
            raw_quat_accel_data = fetch_data(ser, data_fetch_type('DATA_SNAPSHOT'))
            get_quat_accel_data = self.parse_quat_accel_data(raw_quat_accel_data)
            print "Capture IMU data %s " % (raw_quat_accel_data)
            #if get_quat_accel_data is None:
            #    exit(0)
            self.io.write_log(log_file, None, get_quat_accel_data)

        print 'Glove data collection stopped...'
        return

    def utf8len(self, s):
        return len(s.encode('utf-8'))

    ''' FORCE GLOVE FUNCTIONS '''

    def force_glove_capture(self, e):
        while not e.isSet():
            self.force_cap.setSensorRates()
        self.force_cap.closeForceGlove()
        print "Glove data collection stopped..."
        return


''' MAIN LOOP '''


def main():
    ''' Init some variables'''
    use_force, save_path, time_delay = False, "", 0

    ''' PARSE ARGUMENTS '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", help="Use force gloves", action="store_true", default=False,
                        required=False)
    parser.add_argument("-p", "--save_path", nargs='*', help="Save captures to folder name",
                        required=False)
    parser.add_argument("-t", "--time_delay", nargs='*', help="Add time delay for user to get ready",
                        required=True)
    get_args = parser.parse_args()

    ''' COUNT CAMERAS '''

    ''' Start sensor '''
    # Camera Class
    cam_cap = capture_cam()
    dev = cam_cap.init_sensor()

    cam_count = len(dev)
    if cam_count > 1:
        print "TWO cameras found."
    elif cam_count == 1:
        print "ONE camera found."
    else:
        print "No cameras connected. Exiting..."
        exit(0)

    ''' SET GLOVE TYPE BEING RECORDED '''

    ''' Set glove type '''
    if vars(get_args).get("force") is False:
        glove_type = "IMU"
        print "Using IMU glove..."
    elif vars(get_args).get("force") is True:
        glove_type = "Force"
        print "Using force glove..."

    ''' Add time delay for user '''
    if vars(get_args).get("time_delay") is not None:
        print "Waiting for %f seconds" % float(vars(get_args).get("time_delay")[0])
        time.sleep(float(vars(get_args).get("time_delay")[0]))

    ''' SAVE FILES HERE '''
    log_writer = []
    # File IO Class
    io = file_io()

    if vars(get_args).get("save_path") is not None:
        save_path = vars(get_args).get("save_path")[0]

    for i in range(cam_count):
        make_dir = str("captures/" + save_path + "/Glove" + glove_type + "Cam" + str(i + 1))
        make_flow_dir = str("captures/" + save_path + "/Glove" + glove_type + "Cam" + str(i + 1) + "Flow")
        if os.path.isdir(make_dir) is False:
            os.makedirs(make_dir)
            log_writer.append(io.open_file(make_dir, glove_type, i + 1))
        if os.path.isdir(make_flow_dir) is False:
            os.makedirs(make_flow_dir)

    make_dir_glove = str("captures/" + save_path + "/Glove" + glove_type)
    if (os.path.isdir(make_dir_glove)) is False:
        os.makedirs(make_dir_glove)
        glove_writer = io.open_file(make_dir_glove, glove_type, None)

    ''' Check and start streams '''
    rgb_stream = cam_cap.start_rgb(dev)
    depth_stream = cam_cap.start_depth(dev)

    ''' Set Registered Depth '''
    # Need to change registration mode only after streams have been started #
    cam_cap.set_registered_depth(dev)

    ''' Capture loop '''

    if vars(get_args).get("force") is False:
        ''' Set up IMU glove'''
        cap_tool = capture_tool(io, None)
        ser = open_port()
        fetch_data(ser, data_fetch_type('SET_ASCII'))
        e = threading.Event()
        threads = []
        imu_glove_thread = threading.Thread(name="imu_glove_thread", target=cap_tool.imu_glove_capture,
                                            args=(e, ser, glove_writer,))
        threads.append(imu_glove_thread)
        imu_glove_thread.start()
    elif vars(get_args).get("force") is True:
        # Helper Class
        ''' Set up force glove '''
        force_cap = force_glove(glove_writer)
        cap_tool = capture_tool(io, force_cap)
        e = threading.Event()
        threads = []
        force_glove_thread = threading.Thread(name="force_glove_thread", target=cap_tool.force_glove_capture,
                                              args=(e,))
        threads.append(force_glove_thread)
        force_glove_thread.start()

    ''' Setup camera threads '''
    cam_threads = []
    dir_to_write = str("captures/" + save_path + "/Glove" + glove_type + "Cam")
    cam_disp = {}
    for cam in range(cam_count):
        cam = (cam + 1) % cam_count
        cv2.namedWindow('RGB' + str(cam))
        cv2.namedWindow('DEPTH' + str(cam))
        cam_disp['RGB' + str(cam)] = None
        cam_disp['DEPTH' + str(cam)] = None
        one_thread = threading.Thread(target=capture_and_save,
                                      name="CamThread" + str(cam + 1),
                                      args=(cam_cap, cam, dir_to_write,
                                            log_writer,
                                            rgb_stream[cam], depth_stream[cam], io, cam_disp))
        cam_threads.append(one_thread)
        one_thread.daemon = True
        one_thread.start()

    try:
        while True:
            for cam in range(cam_count):
                if cam_disp['RGB' + str(cam)] is not None and cam_disp['DEPTH' + str(cam)] is not None:
                    cv2.imshow('RGB' + str(cam), cam_disp['RGB' + str(cam)])
                    cv2.imshow('DEPTH' + str(cam), cam_disp['DEPTH' + str(cam)])
                    k = cv2.waitKey(1)
                    if k == 27:
                        break
    except KeyboardInterrupt:
        ''' Stop everything '''
        for each_thread in cam_threads:
            each_thread.do_run = False
            each_thread.join(1)
        cam_cap.stop_rgb(rgb_stream)
        cam_cap.stop_depth(depth_stream)
        for each_writer in log_writer:
            io.close_file(each_writer)
        e.set()
        if vars(get_args).get("force") is False:
            imu_glove_thread.join(0.5)
        else:
            force_glove_thread.join(0.5)
        io.close_file(glove_writer)
        if vars(get_args).get("force") is False:
            close_port(ser)

        ''' Stop and quit '''
        openni2.unload()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
