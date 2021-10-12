# -*-coding: utf-8 -*-
# 이 코드는 두 카메라를 동시에 동시에 사용가능함을 확인함.
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
import time
import numpy as np

from FPS import FPS
from WebcamVideoStream import WebcamVideoStream

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
    help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
    help="Whether or not frames should be displayed")
# ap.add_argument('--folder', type=str, default='test', help="Where to save?")
args = vars(ap.parse_args())

# Generate folder
# import os
# try:
#     os.makedirs(args.folder, exist_ok=True)
# except:
#     print("Cannot make directory!")
#     exit(-1)
# print("Directory is made.")

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()

buffer = []
# loop over some frames...this time using the threaded stream
while fps._numFrames < args["num_frames"]:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    buffer.append(frame)
    # check to see if the frame should be displayed to our screen
    if args["display"] > 0:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
    # update the FPS counter
    fps.update()
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

for i, img in enumerate(buffer):
    cv2.imwrite(f'test/{i:05}.png', img)

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()