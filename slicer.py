import sys
import argparse
import cv2
import matplotlib.pyplot as plt
import os
import glob
print(cv2.__version__)


def extractImages(pathIn, pathOut , slice_time):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    success = True
    while success:
      vidcap.set(cv2.CAP_PROP_POS_MSEC ,(count*slice_time))    # added this line
      success,image = vidcap.read()
      print ('Read a new frame: ', success)
      cv2.imwrite( os.path.join(pathOut ,"frame%d.jpg" % count), image)     # save frame as JPEG file
      count = count + 1


def draw_rectangle(img , lefttop , right_bottom , RGB , line_thickness ):
    cv2.rectangle(img, lefttop, right_bottom , RGB , line_thickness )

# Convert  x1 ,y1 , w, h to x1,y1,x2,y2
def convert_xywh2ltrd(x1,y1 , width, height):
    x1, y1, width, height = map(int , [x1,y1, width,height])
    width ,height  = width , height
    x2 = x1 + width
    y2 = y1 + height
    return x1 ,y1 ,x2 ,y2

def read_gtfile(f_path):
    rects1 = []
    rects2 = []
    f=open(f_path,'r')
    lines=f.readlines()
    for line in lines:
        elements = line.split(',')
        rect1 = elements[2:2+4]
        rects1.append(rect1)
        rect2 = elements[-5:-1]
        rects2.append(rect2)

    return rects1 , rects2



if __name__=="__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--pathIn", help="path to video")
    a.add_argument("--pathOut", help="path to images")
    a.add_argument("--slice_time", help="slice time , msc")
    args = a.parse_args()
    extractImages(args.pathIn, args.pathOut)

