

def hir_process(folder, frames, flip, mode, barrier, connection):
    # folder : The path of where hir folder will be generated
    # frames : count in main loop. In other words, how many frames are grabbed.

    import picamera
    import time
    import os
    from time import sleep

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

            start = time.time()
            for frame in range(frames):
                camera.capture_sequence([path + '/%05d.png' % frame], use_video_port=True)
                if(connection.poll()):
                    break
            finish = time.time()

            print('High resolution IR images : Captured %d frames at %.2ffps, duration %.2fs' % ( # 23.48fps offered. Up to 26fps.
                frame+1,
                (frame+1) / (finish - start),
                finish-start))

            print('Written Ended.')
            camera.stop_preview()
        else:
            print("Now streaming?")
            sleep(100000000)
