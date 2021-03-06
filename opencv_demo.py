from __future__ import print_function
from __future__ import division

from threading import Thread
import time

import torch
import torch.nn as nn
from torch.autograd import Variable
import cv2

from util_detection import nms
from network_v_2_3 import FaceNet

class WebcamVideoStream:
    def __init__(self, src=0):
	# initialize the video camera stream and read the first frame
	# from the stream
        self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()
 
	# initialize the variable used to indicate if the thread should
	# be stopped
        self.stopped = False

    def start(self):
	# start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self
 
    def update(self):
        # keep looping infinitely until the libgtkglext-x11-1.0.so.0:thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            self.grabbed, self.frame = self.stream.read()
 
    def read(self):
        # return the frame most recently read
        return self.frame
 
    def stop(self):
	# indicate that the thread should be stopped
        self.stopped = True

def numpy_to_cuda(numpy_array):
    return Variable(torch.from_numpy(numpy_array).cuda().permute(2,0,1).float().unsqueeze(0), volatile=True)


model = FaceNet().cuda()
model.load_state_dict(torch.load("savedir/facenet_pref.pth"))
model.eval()
    
stream = WebcamVideoStream(src=0).start()
while True:
    now = time.time()
    frame = stream.read()
    frame = cv2.resize(frame, (640, 512))
    
    cuda_frame = numpy_to_cuda(frame)
    boxes, classes, anchors = model(cuda_frame)
    processed_boxes, processed_classes = nms(anchors, classes, 0.8, use_nms = True, softmax=False)

    for box in processed_boxes:
        box = box.int()
        xmin = box[0]
        ymin = box[1]
        xmax = box[2]
        ymax = box[3]
        cv2.rectangle(frame,(xmin,ymin),(xmax,ymax),(0,255,0),2)
       
    # check to see if the frame should be displayed to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    then = time.time()
    print(1/(then-now))
 
cv2.destroyAllWindows()
                























# cap = cv2.VideoCapture(0)
# cap.set(3, 1280)
# cap.set(4, 720)
    
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#     print(ret)

#     # Our operations on the frame come here
#     #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Display the resulting frame
#     cv2.imshow('frame',frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()
