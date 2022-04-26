import io

class SplitFrames(object):
    def __init__(self,path):
        self.frame_num = 0
        self.output = None
        self.path = path

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; close the old one (if any) and
            # open a new output
            if self.output:
                self.output.close()
            self.frame_num += 1
            self.output = io.open(self.path + '%05d.jpg' % self.frame_num, 'wb')
        self.output.write(buf)

def hir_process(folder, frames, flip, mode, barrier, connection):
    # folder : The path of where hir folder will be generated
    # frames : count in main loop. In other words, how many frames are grabbed.
    import picamera
    import time
    import os
    from time import sleep
    import io

    proc = os.getpid()
    #print(f"HIR process pid : {proc}")

    width = 360
    height = 480

    path = folder+'/ir_hr'
    print(f'Writing highresolution ir images in {path}')

    # Generate folder
    import os
    try:
        os.makedirs(path, exist_ok=True)
    except:
        print("Cannot make directory!")
        exit(-1)
    #print("High resolution IR Directory is made.")

    with picamera.PiCamera() as camera:
        camera.resolution = (height, width)
        camera.framerate = 24 # Full speed at 720p
        if flip == 'True':
            camera.vflip = True
            camera.hflip = True
        #time.sleep(2)
        #output = np.empty((height, width, 3), dtype=np.uint8)

        camera.start_preview()
        camera.preview_fullscreen = False
        camera.preview_window = (0,0,360,480)

        barrier.wait()
        if mode == 'save':

            output = SplitFrames(path)
            start = time.time()
            camera.start_recording(output, format='mjpeg')
            camera.wait_recording(2)
            camera.stop_recording()
            finish = time.time()
            camera.stop_preview()
            print('Captured %d frames at %.2ffps' % (
                output.frame_num,
                output.frame_num / (finish - start)))
        else:
            print("Now streaming?")
            sleep(100000000)
