#!/usr/bin/env python

''' INTRODUCTION AND INSTRUCTIONS '''

''' GET openni-python WRAPPER
Clone https://github.com/severin-lemaignan/openni-python
cd openni-python
python setup.py build
sudo python setup.py install
'''

''' USAGE INSTRUCTIONS '''
# --stream rgb,depth OR --stream ir,depth
# --display y OR n to display the frames
# --save y OR n to to save frames to file
# --depth_registered y OR n to use registered depth

import argparse
import numpy as np
from openni import openni2, utils
import cv2

''' INITIALIZE VARIABLES '''
# DEVICE
global dev
# STREAMS + FRAME DATA
global ir_stream, rgb_stream, depth_stream, ir_array, rgb_array, depth_array
# USER ARGUMENTS
global use_rgb, use_depth, use_ir, use_display, save_cap

''' START SEPARATE STREAMS FROM SENSOR '''
def start_ir():
	global ir_stream
	ir_stream = dev.create_ir_stream()
	ir_stream.set_video_mode(openni2.c_api.OniVideoMode(pixelFormat = openni2.c_api.OniPixelFormat.ONI_PIXEL_FORMAT_GRAY16, resolutionX = 640, resolutionY = 480, fps = 30))
	ir_stream.start()
	print 'IR Stream Started'
def start_depth():
	global depth_stream
	depth_stream = dev.create_depth_stream()
 	depth_stream.set_video_mode(openni2.c_api.OniVideoMode(pixelFormat = openni2.c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX = 640, resolutionY = 480, fps = 30))
	depth_stream.start()
	print 'Depth Stream Started'
def start_rgb():
	global rgb_stream
	rgb_stream = dev.create_color_stream()
	rgb_stream.set_video_mode(openni2.c_api.OniVideoMode(pixelFormat = openni2.c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX = 640, resolutionY = 480, fps = 30))
	rgb_stream.start()
	print 'RGB Stream Started'

''' STOP SEPARATE STREAMS FROM SENSOR '''
def stop_ir():
	global ir_stream
	ir_stream.stop()
	print 'IR Stream Stopped'
def stop_depth():
	global depth_stream
	depth_stream.stop()
	print 'Depth Stream Stopped'
def stop_rgb():
	global rgb_stream
	rgb_stream.stop()
	print 'RGB Stream Stopped'

''' FETCH FRAMES FOR EACH STREAM '''
def get_ir():
	global ir_array, use_display
	frame = ir_stream.read_frame()
	frame_data = frame.get_buffer_as_uint16()
	ir_array = np.ndarray((frame.height, frame.width),dtype=np.uint16,buffer=frame_data).astype(np.float32)
	if use_display:
		cv2.imshow('IR',ir_array)
def get_depth():
	global depth_array, use_display
	frame = depth_stream.read_frame()
	frame_data = frame.get_buffer_as_uint16()
	depth_array = np.ndarray((frame.height, frame.width),dtype=np.uint16,buffer=frame_data)/10000.
	depth_array_disp = (depth_array*255).astype(np.uint8)
	if use_display:
		cv2.imshow('DEPTH',np.uint8(depth_array_disp))
def get_rgb():
	global rgb_array, use_display
	frame = rgb_stream.read_frame()
	frame_data = frame
	frame_data = frame.get_buffer_as_uint8()
	rgb_array = np.ndarray((frame.height, frame.width, 3),dtype=np.uint8,buffer=frame_data)
	rgb_array = cv2.cvtColor(rgb_array,cv2.COLOR_BGR2RGB)
	if use_display:
		cv2.imshow('RGB',rgb_array)

''' SAVE FRAME '''
def save_frame(frame_type, frame_array, idx):
	fn = ('captures/capture_%s_%03d.png') % (frame_type,idx)

	if frame_type is 'rgb':
		cv2.imwrite(fn, (rgb_array).astype(np.uint8))
	if frame_type is 'ir':
		cv2.imwrite(fn, ir_array.astype(np.uint8))
	if frame_type is 'depth':
		cv2.imwrite(fn, depth_array.astype(np.uint16))

''' INITIALIZE SENSOR '''
def init_sensor():
	global dev
	openni2.initialize()
	dev = openni2.Device.open_any()

''' MAIN LOOP '''
def main():
	global use_rgb, use_depth, use_ir, use_display, save_cap
	global ir_array, rgb_array, depth_array
	global dev
	use_rgb, use_depth, use_ir, use_display, save_cap = False,False,False,False,False

	''' PARSE ARGUMENTS '''
	parser = argparse.ArgumentParser()
	parser.add_argument("-s","--stream",nargs='*',help="Type of streams to start as comma-separated parameters [rgb OR depth OR ir]",required=True)
	parser.add_argument("-d","--display",nargs='*',help="Show captured frame output [y OR n]",required=True)
	parser.add_argument("-sv","--save",nargs='*',help="Save frames to file [y OR n]",required=True)
	parser.add_argument("-r","--depth_registered",nargs='*',help="Use registered depth [y OR n]",required=True)
	get_args = parser.parse_args()

	''' Fetch and Use Arguments '''
	if 'rgb' in vars(get_args).get("stream")[0]:
		use_rgb = True
	if 'depth' in vars(get_args).get("stream")[0]:
		use_depth = True
	if 'ir' in vars(get_args).get("stream")[0]:
		use_ir = True
	if 'y' in vars(get_args).get("display")[0]:
		use_display = True
	elif 'n' in vars(get_args).get("display")[0]:
		use_display = False
	if 'y' in vars(get_args).get("save")[0]:
		save_cap = True
	elif 'n' in vars(get_args).get("save")[0]:
		save_cap = False
	if 'y' in vars(get_args).get("depth_registered")[0]:
		reg_dep = True
	elif 'n' in vars(get_args).get("depth_registered")[0]:
		reg_dep = False

	''' Start sensor '''
	init_sensor()

	''' Check and start streams '''
	if use_rgb:
		start_rgb()
	if use_depth:
		start_depth()
	if use_ir:
		start_ir()

	''' Set Registered Depth '''
	# Need to change registration mode only after streams have been started #
	if reg_dep:
		dev.set_image_registration_mode(openni2.c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_DEPTH_TO_COLOR)

	''' Initialize frame counter '''
	shot_idx = 0

	''' Capture loop '''
	while True:
		if use_rgb:
			get_rgb()
		if use_depth:
			get_depth()
		if use_ir:
			get_ir()

		if save_cap:
			if use_rgb:
				save_frame('rgb', rgb_array, shot_idx)
			if use_depth:
				save_frame('depth', depth_array, shot_idx)
			if use_ir:
				save_frame('ir', ir_array, shot_idx)
			shot_idx += 1

		ch = 0xFF & cv2.waitKey(1)
		if ch == 27:
			break

	''' Check and stop streams '''
	if use_rgb:
		stop_rgb()
	if use_depth:
		stop_depth()
	if use_ir:
		stop_ir()

	''' Stop and quit '''
	openni2.unload()
	cv2.destroyAllWindows()
	print "Saved %d files to disk"%(shot_idx)

if __name__ == '__main__':
	main()