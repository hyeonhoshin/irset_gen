import numpy as np
import serial
import argparse
import FPS
from time import sleep
import cv2
import time
import os

#from hir import hir_process
from multiprocessing import Process, current_process, Barrier, Pipe

def sub(args, barrier, connection):

    ### Start Hir grabbing by multi-processing.
    sync_barrier = Barrier(2)

    lr_path = os.path.join(args.folder, f"s{args.subject:02d}-d{args.distance}-t{args.orientation:03d}", "ir_lr2")

    # Generate folder
    try:
        os.makedirs(lr_path, exist_ok=True)
    except:
        print("Cannot make directory!")
        exit(-1)

    ## Commnication with IR sensor.
    ser = serial.Serial(port=args.device,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, 
                    baudrate=args.baudrate, 
                    timeout=200,
                    dsrdtr=True)

    # Register setting is needed.
    ser.write(b'reg write 0x01 0x04\n') # Turn on end of conversion interrupt. I think it is not needed also.
    sleep(0.01)
    ser.write(b'reg write 0x02 0x02\n') # Activate. One shot mode Disabled
    sleep(0.01)
    ser.write(b'reg write 0x03 0x0F\n') # End of converstion delay = 0, Integration time = 800us(max)
    sleep(0.01)
    ser.write(b'reg write 0x04 0x02\n') # Number of repeats = 4, Number of coherent double samples = 1, Turn off fine-grained compensation; 0100001X = 0x43
    sleep(0.01)
    ser.write(b'reg write 0x05 0x40\n') # Full PGA amplifying.
    sleep(0.01)
    ser.write(b'reg write 0x06 0x0A\n') # LED PWM Setting. No need to cocern.
    sleep(0.01)
    ser.write(b'reg write 0xC1 0x00\n') # Turn off LED
    sleep(0.01)

    # Make the amplifier sensitive
    ser.write(b'reg write 0xA5 0xFF\n')
    sleep(0.01)
    ser.write(b'reg write 0xA6 0xFF\n')
    sleep(0.01)
    ser.write(b'reg write 0xA7 0xFF\n')
    sleep(0.01)
    ser.write(b'reg write 0xA8 0xFF\n')
    sleep(0.01)
    ser.write(b'reg write 0xA9 0xFF\n')

    print("======= Setting2 ========")
    print("Device name : {}".format(args.device))
    print("Baud rate : {}".format(args.baudrate))
    print("folder : {}".format(args.folder))
    print("count taking photo : {}\n".format(args.count))

    # Get ir data
    if(ser.is_open):
        # connected = True
        ser.reset_input_buffer()
        ser.reset_output_buffer()

    def s16(val):
        return -(val & 0x8000)|(val&0x7fff)

    fps = FPS.FPS(args.count)

    cv2.imshow('stream', cv2.resize(np.zeros([6, 10], dtype=float), dsize=(500, 300), interpolation=cv2.INTER_NEAREST))
    cv2.waitKey(1)
    barrier.wait()
    fps.start()
    if args.mode == 'save':

        for i in range(args.count):
            buffer = []
            ser.write(b'reg read 0x10 0x78\n')
            frame = ser.read_until()
            
            for j in range(0,360,6):
                prior = frame[j:j+2]
                post = frame[j+3:j+5]
                try:
                    buffer.append(s16(int(prior+post, base = 16)))
                except:
                    print(prior+post)
                    # print(frame)

            tmp = np.array(buffer)
            
            f = open(lr_path+f'/{i:05}.npy', 'wb')
            tmp_img = tmp.reshape(6,10)[::-1]
            np.save(f,tmp_img)
            f.close()
            
            #if(connection.poll()):
            #        break

            tmp_img = tmp_img - np.min(tmp_img)
            tmp_img = tmp_img / 1023.
            #img = cv2.resize(tmp_img, dsize=(500,300), interpolation=cv2.INTER_NEAREST)

            #cv2.imshow('stream', img)
            #cv2.waitKey(1)

        connection.send("End")

    elif args.mode == 'conti':
        while(True):
            buffer = []
            ser.write(b'reg read 0x10 0x78\n')
            frame = ser.read_until()

            for j in range(0,360,6):
                prior = frame[j:j+2]
                post = frame[j+3:j+5]
                try:
                    buffer.append(s16(int(prior+post, base = 16)))
                except:
                    print(prior+post)
                    # print(frame)

            #if args.flip == 'True':
            #    buffer.reverse()

            tmp = np.array(buffer)
            tmp_img = tmp.reshape(6,10)
            
            if args.flip == 'True':
                tmp_img = tmp_img[::-1]

            if args.normalize == 'False':
                tmp_img = tmp_img - np.min(tmp_img)
                tmp_img = tmp_img / 1023.
            else:
                tmp_img = tmp_img - np.min(tmp_img)
                tmp_img = tmp_img / 1023.
                tmp_img = cv2.normalize(tmp_img, None, 0, 1, cv2.NORM_MINMAX)
            
                # print(type(tmp_img))

            img = cv2.resize(tmp_img, dsize=(500,300), interpolation=cv2.INTER_NEAREST)

            cv2.imshow('stream', img)
            cv2.waitKey(1)

            
    fps.stop()
    #print(f"Total fps : {fps.fps():.4f}")
    #print(f"Total time : {fps.elapsed():.4f}")
    #print(f"Total fps : {fps.fps2():.4f}")
    #print(f"Total time : {fps.elapsed2():.4f}")

    #proc.join()

    cv2.waitKey(10)
    cv2.destroyAllWindows()

    # output : /folder_name/"%05.npy" per frame.

