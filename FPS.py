# import the necessary packages
import datetime
import time
class FPS:
    def __init__(self, count):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._start2 = None
        self._end = None
        self._end2 = None
        self._numFrames = count

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        self._start2 = time.time()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()
        self._end2 = time.time()

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()
    def elapsed2(self):
        return (self._end2 - self._start2)

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()

    def fps2(self):
        return self._numFrames / self.elapsed2()
