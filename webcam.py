# -*-coding: utf-8 -*-
# 이 코드는 두 카메라를 동시에 동시에 사용가능함을 확인함.
import cv2
import time
import numpy as np

# cap 이 정상적으로 open이 되었는지 확인하기 위해서 cap.isOpen() 으로 확인가능
cap = cv2.VideoCapture(0)

# cap.get(prodId)/cap.set(propId, value)을 통해서 속성 변경이 가능.
# 3은 width, 4는 heigh

print('width: {0}, height: {1}'.format(cap.get(3),cap.get(4)))
cap.set(3,360)
cap.set(4,640)


start_time = time.time()
monitor_time = 3

buffer = []

while(time.time()-start_time < monitor_time):
    # ret : frame capture결과(boolean)
    # frame : Capture한 frame
    ret, frame = cap.read() 

    if (ret):
        # image를 Grayscale로 Convert함.
        buffer.append(frame)

        # cv2.imshow('frame', frame)
        

        # if cv2.waitKey(1) & 0xFF == ord('q'):
            # break

# Post saving
for i, img in enumerate(buffer):
    cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    f = open(f"{i:05}.npy",'wb')
    np.save(f,np.array(cvt))
    f.close()

# cap.release()
# cv2.destroyAllWindows()
