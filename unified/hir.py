def hir_process(folder, frames, flip):
    # folder : The path of where hir folder will be generated
    # frames : count in main loop. In other words, how many frames are grabbed.

    import picamera
    import time
    import os
    
    proc = os.getpid()
    print(f"HIR process pid : {proc}")

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
    print("High resolution IR Directory is made.")

    with picamera.PiCamera() as camera:
        camera.resolution = (height, width)
        camera.framerate = 24 # Full speed at 720p
        if flip == 'True':
            camera.vflip = True
            camera.hflip = True
        time.sleep(2)
        #output = np.empty((height, width, 3), dtype=np.uint8)

        start = time.time()
        camera.capture_sequence([
        path +'/%05d.png' % i        # capture_continuous --> can used with multi-process.
            for i in range(frames)
            ], use_video_port=True)
        finish = time.time()

    print('High resolution IR images : Captured %d frames at %.2ffps' % ( # 23.48fps offered. Up to 26fps.
        frames,
        frames / (finish - start)))

    print('Written Ended.')
