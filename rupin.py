import numpy as np
import serial
import argparse
import FPS
from time import sleep
import cv2
import time

parser = argparse.ArgumentParser(description='Take IR photos')
parser.add_argument('--device',type=str, default='/dev/ttyACM0')
parser.add_argument('--baudrate',type=int, default=115200)
parser.add_argument('folder',type=str)
parser.add_argument('--count','-c', type=int, default=1)
args = parser.parse_args()

print("======= Setting ========")
print("Device name : {}".format(args.device))
print("Baud rate : {}".format(args.baudrate))
print("foler : {}".format(args.folder))
print("count taking photo : {}\n".format(args.count))

### input : name of usb. baud rate. folder name.

# Generate folder
import os
try:
    os.makedirs(args.folder, exist_ok=True)
except:
    print("Cannot make directory!")
    exit(-1)
print("Directory is made.")

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
ser.write(b'reg write 0xC1 0x08\n') # Turn off LED
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

# Get ir data
if(ser.is_open):
    # connected = True
    ser.reset_input_buffer()
    ser.reset_output_buffer()

def s16(val):
    return -(val & 0x8000)|(val&0x7fff)

fps = FPS.FPS()

fps.start()
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
    f = open(args.folder+f'/{i:05}.npy', 'wb')
    np.save(f,tmp)
    f.close()

    tmp_img = tmp.reshape(6,10)
    tmp_img = tmp_img - np.min(tmp_img)
    tmp_img = tmp_img / 1023.
    img = cv2.resize(tmp_img, dsize=(1000,600), interpolation=cv2.INTER_NEAREST)

    cv2.imshow('stream', img)
    cv2.waitKey(1)
fps.stop()
print(f"Total fps : {fps.fps():.2f}")

cv2.waitKey(10)
cv2.destroyAllWindows()

# output : /folder_name/"%05.npy" per frame.

