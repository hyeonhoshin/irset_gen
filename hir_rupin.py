import time
import picamera
import numpy as np

width = 720
height = 1280

frames = 60
import argparse

parser = argparse.ArgumentParser(description='Take HR IR photos')
parser.add_argument('folder',type=str)
args = parser.parse_args()

path = args.folder+'/ir_hr'
print(f'Writing in {path}')

# Generate folder
import os
try:
    os.makedirs(path, exist_ok=True)
except:
    print("Cannot make directory!")
    exit(-1)
print("Directory is made.")

with picamera.PiCamera() as camera:
    camera.resolution = (height, width)
    camera.framerate = 24 # Full speed at 720p
    time.sleep(2)
    #output = np.empty((height, width, 3), dtype=np.uint8)

    start = time.time()
    camera.capture_sequence([
       path +'/%05d.png' % i        # capture_continuous --> can used with multi-process.
        for i in range(frames)
        ], use_video_port=True)
    finish = time.time()

print('Captured %d frames at %.2ffps' % ( # 23.48fps offered. Up to 26fps.
    frames,
    frames / (finish - start)))

print('Written Ended.')