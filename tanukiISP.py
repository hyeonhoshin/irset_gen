# tanukiISP
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

parser.add_argument('--device',type=str, help='The port of connected max25405 evkit.', default='/dev/ttyACM0')
parser.add_argument('--baudrate',type=int, default=115200) # How about trying 128 000 or 256 000?
parser.add_argument('--bit',type=bool,help='Sweep the available bit depth from ADC',default=False)
args = parser.parse_args()

print("======= Setting ========")
print("Device name : {}".format(args.device))
print("Baud rate : {}".format(args.baudrate))

# Get images from different combinations of exposures
## Folder made to save.
try:
    os.makedirs('test_samples', exist_ok=True)
    os.makedirs('test_samples_normalized_imgs',exist_ok=True)
except:
    print("Cannot make directory!")
    exit(-1)

## Serial port open
ser = serial.Serial(port=args.device,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE, 
                baudrate=args.baudrate, 
                timeout=200,
                dsrdtr=True)

## Register setting is needed.
ser.write(b'reg write 0x01 0x04\n') # Turn on end of conversion interrupt. I think it is not needed also.
sleep(0.01)
ser.write(b'reg write 0x02 0x02\n') # Activate. One shot mode Disabled
sleep(0.01)
ser.write(b'reg write 0x03 0x0F\n') # End of converstion delay = 0, Integration time = 800us(max)
sleep(0.01)
ser.write(b'reg write 0x04 0x02\n') # No repeat.
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

## Get ir data
if(ser.is_open):
    # connected = True
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
def s16(val):
    return -(val & 0x8000)|(val&0x7fff)

adc_steps = [b'0',b'1',b'2',b'3']
amp_steps = [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9',b'A',b'B',b'C',b'D',b'E',b'F']
if args.bit:
    bit_steps = [b'02',b'06',b'0A',b'0E',b'12',b'16',b'1A',b'1E']
else:
    bit_steps = [b'02']

imgs = []

best_sharpness = -100000
loc_best_sharpness = {'adc':None,'amp':None, 'bit':None}

out=open("data_in_numbers.log","w")

for bit in bit_steps:
    for adc in adc_steps:
        imgs_same_amp = []
        for amp in amp_steps:
            out.write("\n===== bit"+str(bit,'utf-8')+",adc"+str(adc,'utf-8')+",amp"+str(amp,'utf-8')+" =====\n")
            # Change the gain and amp.
            ser.write(b'reg write 0x05 0x4'+adc+b'\n') ## amp updated.
            sleep(0.01)

            ## Gain updated
            ser.write(b'reg write 0xA5 0x'+amp+amp+b'\n')
            sleep(0.01)
            ser.write(b'reg write 0xA6 0x'+amp+amp+b'\n')
            sleep(0.01)
            ser.write(b'reg write 0xA7 0x'+amp+amp+b'\n')
            sleep(0.01)
            ser.write(b'reg write 0xA8 0x'+amp+amp+b'\n')
            sleep(0.01)
            ser.write(b'reg write 0xA9 0x'+amp+amp+b'\n')
            
            ## Bits updated
            ser.write(b'reg write 0x04 0x'+bit+b'\n')

            # Get value
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

            f = open(b'test_samples/'+b'adc_'+adc+b'_amp_'+amp+b'_bit_'+bit+b'.npy', 'wb')
            max = np.max(tmp)
            tmp_img = tmp.reshape(6,10)[::-1]
            np.save(f,tmp_img)
            f.close()
            print(tmp_img, file=out)

            np_img = (tmp_img/max)*255.0
            np_img = np_img.astype('uint8')

            cv_img = cv2.cvtColor(np_img,cv2.COLOR_GRAY2BGR)

            lap = cv2.Laplacian(cv_img,cv2.CV_16S)

            np_lap = np.array(lap)
            max_val = np.max(np_lap)

            if max_val > best_sharpness:
                best_sharpness = max_val
                loc_best_sharpness = {'adc':adc,'amp':amp,'bit':bit}
            img = cv2.resize(cv_img, dsize=(500,300), interpolation=cv2.INTER_NEAREST)
            cv2.imwrite('test_samples_normalized_imgs/'+'adc_'+str(adc,'utf-8')+'_amp_'+str(amp,'utf-8')+'_bit_'+str(bit,'utf-8')+'.png', img)
out.close()
    
print("The best sharpness:",best_sharpness)
print("At the image, adc : %s, amp : %s, bit : %s"%(str(loc_best_sharpness['adc'],'utf-8'),str(loc_best_sharpness['amp'],'utf-8'),str(loc_best_sharpness['bit'],'utf-8')))

