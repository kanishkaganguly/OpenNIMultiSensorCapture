#!/usr/bin/env python

__author__ = 'Kanishka Ganguly'
__version__ = '1.0.0'
__date__ = 'May 25 2017'

import numpy as np
from openni import openni2
import cv2


class capture_cam:
    ''' INITIALIZE SENSOR '''

    def init_sensor(self):
        openni2.initialize()
        dev = openni2.Device.open_all()
        return dev

    ''' SET REGISTERED DEPTH'''

    def set_registered_depth(self, dev):
        for each_dev in dev:
            each_dev.set_image_registration_mode(
                openni2.c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_DEPTH_TO_COLOR)
        return

    ''' START SEPARATE STREAMS FROM SENSOR '''

    def start_ir(self, dev):
        ir_stream = []
        for each_dev in dev:
            curr_stream = each_dev.create_ir_stream()
            ir_stream.append(curr_stream)
            curr_stream.set_video_mode(
                openni2.c_api.OniVideoMode(pixelFormat=openni2.c_api.OniPixelFormat.ONI_PIXEL_FORMAT_GRAY16,
                                           resolutionX=640,
                                           resolutionY=480, fps=30))
            curr_stream.set_mirroring_enabled(False)
            curr_stream.start()
        print 'IR Stream Started'
        return ir_stream

    def start_depth(self, dev):
        depth_stream = []
        for each_dev in dev:
            curr_stream = each_dev.create_depth_stream()
            depth_stream.append(curr_stream)
            curr_stream.set_video_mode(
                openni2.c_api.OniVideoMode(pixelFormat=openni2.c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM,
                                           resolutionX=640, resolutionY=480, fps=30))
            curr_stream.set_mirroring_enabled(False)
            curr_stream.start()
        print 'Depth Stream Started'
        return depth_stream

    def start_rgb(self, dev):
        rgb_stream = []
        for each_dev in dev:
            curr_stream = each_dev.create_color_stream()
            rgb_stream.append(curr_stream)
            curr_stream.set_video_mode(
                openni2.c_api.OniVideoMode(pixelFormat=openni2.c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888,
                                           resolutionX=640,
                                           resolutionY=480, fps=30))
            curr_stream.set_mirroring_enabled(False)
            curr_stream.start()
        print 'RGB Stream Started'
        return rgb_stream

    ''' STOP SEPARATE STREAMS FROM SENSOR '''

    def stop_ir(self, ir_stream):
        for each_stream in ir_stream:
            each_stream.stop()
        print 'IR Stream Stopped'

    def stop_depth(self, depth_stream):
        for each_stream in depth_stream:
            each_stream.stop()
        print 'Depth Stream Stopped'

    def stop_rgb(self, rgb_stream):
        for each_stream in rgb_stream:
            each_stream.stop()
        print 'RGB Stream Stopped'

    ''' FETCH FRAMES FOR EACH STREAM '''

    def get_ir(self, ir_stream):
        frame = ir_stream.read_frame()
        frame_data = frame.get_buffer_as_uint16()
        ir_array = np.ndarray((frame.height, frame.width), dtype=np.uint16, buffer=frame_data).astype(np.float32)
        return ir_array

    def get_depth(self, depth_stream):
        frame = depth_stream.read_frame()
        frame_data = frame.get_buffer_as_uint16()
        depth_array = np.ndarray((frame.height, frame.width), dtype=np.uint16, buffer=frame_data)
        return depth_array

    def get_rgb(self, rgb_stream):
        frame = rgb_stream.read_frame()
        frame_data = frame.get_buffer_as_uint8()
        rgb_array = np.ndarray((frame.height, frame.width, 3), dtype=np.uint8, buffer=frame_data)
        return rgb_array

    ''' SAVE FRAME '''

    def save_frame(self, frame_type, frame_array, idx, root_dir):
        fn = ('%s/capture_%s_%04d.png') % (root_dir, frame_type, idx)
        # print fn
        if frame_type is 'rgb':
            cv2.imwrite(fn, (frame_array).astype(np.uint8))
        if frame_type is 'ir':
            cv2.imwrite(fn, (frame_array / frame_array.max() * 255).astype(np.uint8))
        if frame_type is 'depth':
            cv2.imwrite(fn, frame_array.astype(np.uint16))
