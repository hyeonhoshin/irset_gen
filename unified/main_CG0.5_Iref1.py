import numpy as np
import serial
import argparse
import FPS
from time import sleep
import cv2
import time
import os

from hir import hir_process
from multiprocessing import Process, current_process, Barrier, Pipe

parser = argparse.ArgumentParser(description='Take IR photos')
parser.add_argument('folder', type=str)
parser.add_argument('subject', type=int)
parser.add_argument('distance', type=int)
parser.add_argument('orientation', type=int)

parser.add_argument('--device',type=str, help='The port of connected max25405 evkit.', default='/dev/ttyACM0')
parser.add_argument('--baudrate',type=int, default=115200) # How about trying 128 000 or 256 000?
parser.add_argument('--count','-c', type=int,help='How many frames do you want.', default=1)
parser.add_argument('--mode','-m',type=str,help='If mode is \'conti\', it does not save output and just draw plot in real time', default='save')
parser.add_argument('--bias','-b',type=str,help='Do bias compensation. Not implemented yet.', default='False')
parser.add_argument('--normalize','-n',type=str,help='Do simple normalizing by cv2.normalize', default='False')
parser.add_argument('--flip','-f',type=str,help='If true, it plots from bottom right.', default='True')

args = parser.parse_args()

print("======= Setting ========")
print("Device name : {}".format(args.device))
print("Baud rate : {}".format(args.baudrate))
print("foler : {}".format(args.folder))
print("count taking photo : {}\n".format(args.count))


### Start Hir grabbing by multi-processing.
sync_barrier = Barrier(2)
[hir_connection, connection] = Pipe(duplex=True)
proc = Process(target=hir_process,args=(os.path.join(args.folder, f"s{args.subject:02d}-d{args.distance}-t{args.orientation:03d}"), args.count,args.flip,args.mode,sync_barrier, hir_connection))
proc.start()

### input : name of usb. baud rate. folder name.
# lr_path = args.folder + '/ir_lr'
lr_path = os.path.join(args.folder, f"s{args.subject:02d}-d{args.distance}-t{args.orientation:03d}", "ir_lr")

# Generate folder
try:
    os.makedirs(lr_path, exist_ok=True)
except:
    print("Cannot make directory!")
    exit(-1)
print("Low resolution IR Directory is made.")

print(f"Main program pid : {os.getpid()}")

## Commnication with IR sensor.
# Serial port open
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
ser.write(b'reg write 0x04 0x42\n') # Number of repeats = 4, Number of coherent double samples = 1, Turn off fine-grained compensation; 0100001X = 0x43
sleep(0.01)
ser.write(b'reg write 0x05 0x40\n') # Full PGA amplifying.
sleep(0.01)
ser.write(b'reg write 0x06 0x0A\n') # LED PWM Setting. No need to cocern.
sleep(0.01)
ser.write(b'reg write 0xC1 0x00\n') # Turn off LED, Turn on amplifiers.
sleep(0.01)

# Make the amplifier sensitive
ser.write(b'reg write 0xA5 0x33\n')
sleep(0.01)
ser.write(b'reg write 0xA6 0x33\n')
sleep(0.01)
ser.write(b'reg write 0xA7 0x33\n')
sleep(0.01)
ser.write(b'reg write 0xA8 0x33\n')
sleep(0.01)
ser.write(b'reg write 0xA9 0x33\n')

# Get ir data
if(ser.is_open):
    # connected = True
    ser.reset_input_buffer()
    ser.reset_output_buffer()

def s16(val):
    return -(val & 0x8000)|(val&0x7fff)

fps = FPS.FPS()

cv2.imshow('stream', cv2.resize(np.zeros([6, 10], dtype=float), dsize=(500, 300), interpolation=cv2.INTER_NEAREST))
cv2.waitKey(1)
sync_barrier.wait()
start_time = time.time()

fps.start()
if args.mode == 'save':

    for i in range(args.count):
        fps.update()
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

        tmp_img = tmp_img - np.min(tmp_img)
        tmp_img = tmp_img / 1023.
        img = cv2.resize(tmp_img, dsize=(500,300), interpolation=cv2.INTER_NEAREST)

        cv2.imshow('stream', img)
        cv2.waitKey(1)

    connection.send("End")
    end_time = time.time()
    
    print("Low Resolution image captured! Duration %s, from %s to %s" % (end_time-start_time, start_time, end_time))

elif args.mode == 'conti':
    while(True):
        fps.update()
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
print(f"Total fps : {fps.fps():.2f}")
print(f"Total time : {fps.elapsed():.2f}")

proc.join()

cv2.waitKey(10)
cv2.destroyAllWindows()

# output : /folder_name/"%05.npy" per frame.

