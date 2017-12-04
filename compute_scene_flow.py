#!/usr/bin/env python

import os
import glob
import threading
import Queue
import subprocess
import time

max_processes = 2
process_queue = Queue.Queue(maxsize=max_processes)


def get_folders_to_process():
    root_dir = "compute_scene_flow"
    level1_dirs = os.walk(root_dir).next()[1]
    glove_type = "IMU"
    process_list = []
    for each_dir in level1_dirs:
        curr_dir = os.path.join(root_dir, each_dir)
        get_cam_dirs = glob.glob('%s/Glove%sCam[0-9]' % (curr_dir, glove_type))
        cam_dir_count = len(get_cam_dirs)
        for i in range(cam_dir_count):
            rgb_path = get_cam_dirs[i] + "/capture_rgb_%04d.png"
            depth_path = get_cam_dirs[i] + "/capture_depth_%04d.png"
            output_path = get_cam_dirs[i] + "Flow/flow_%04d"
            scene_flow_process = ["scene_flow/PD-Flow/build/flow_batch", rgb_path, depth_path, output_path]
            process_list.append(scene_flow_process)
    glove_type = "Force"
    for each_dir in level1_dirs:
        curr_dir = os.path.join(root_dir, each_dir)
        get_cam_dirs = glob.glob('%s/Glove%sCam[0-9]' % (curr_dir, glove_type))
        cam_dir_count = len(get_cam_dirs)
        for i in range(cam_dir_count):
            rgb_path = get_cam_dirs[i] + "/capture_rgb_%04d.png"
            depth_path = get_cam_dirs[i] + "/capture_depth_%04d.png"
            output_path = get_cam_dirs[i] + "Flow/flow_%04d"
            scene_flow_process = ["scene_flow/PD-Flow/build/flow_batch", rgb_path, depth_path, output_path]
            process_list.append(scene_flow_process)
    return process_list


def do_scene_flow(process_queue):
    while True:
        to_do = process_queue.get()
        proc = subprocess.Popen(to_do)
        while proc.poll() is None:
            print "Working on Process %d...\r\n" % proc.pid
        process_queue.task_done()


def main():
    process_list = get_folders_to_process()
    print "Computing scene flow for %d folders" % len(process_list)
    st = time.time()
    for i in range(max_processes):
        worker = threading.Thread(target=do_scene_flow, args=(process_queue,))
        worker.setDaemon(True)
        worker.start()

    for process in process_list:
        print "Adding process to queue..."
        process_queue.put(process)

    print 'Main thread waiting...'
    process_queue.join()
    print "Finished SceneFlow in %f seconds!" % (time.time() - st)
    return


if __name__ == '__main__':
    main()
