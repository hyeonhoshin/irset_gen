import numpy as np
import serial
import argparse

parser = argparse.ArgumentParser(description='Take IR photos')
parser.add_argument('--device',type=str, default='/dev/ttyACM0')
parser.add_argument('--baudrate',type=int, default=115200)
parser.add_argument('folder',type=str)
parser.add_argument('--count','-c', type=int, default=3)
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
ser.write(b'reg write 0xC1 0x08\n') # Turn off LED
# CDS elim.
# Turn off Coarse ALC.

# Get ir data
if(ser.is_open):
    # connected = True
    ser.reset_input_buffer()
    ser.reset_output_buffer()

def s16(val):
    return -(val & 0x8000)|(val&0x7fff)

try:
    for i in range(args.count):
        buffer = []
        ser.write(b'reg read 0x10 0x78\n')
        frame = ser.read_until()

        for j in range(0,360,6):
            prior = frame[j:j+2]
            post = frame[j+3:j+5]
            buffer.append(s16(int(prior+post)))

        tmp = np.array(buffer)
        f = open(args.folder+f'/{i:05}.npy', 'wb')
        np.save(f,tmp)
        f.close()
except:
    print('Read error!')
    exit(-1)



# output : /folder_name/"%05.npy" per frame.

