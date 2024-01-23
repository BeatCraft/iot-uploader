#! /usr/bin/python
# -*- coding: utf-8 -*-
#
import os
import sys
import time
import numpy as np
import csv
from PIL import Image, ImageDraw, ImageOps, ImageEnhance
#
# LDNN Modules
#
sys.path.append(os.path.join(os.path.dirname(__file__), '../ldnn/'))
import plat
import util
import core
#import train
import exam

sys.path.append(os.path.join(os.path.dirname(__file__), '../ptool/'))
import tool

CAM_WIDTH = 1280
CAM_HEIGHT = 960
DIGIT_WIDTH = 16
DIGIT_HEIGHT = 24
IMAGE_SIZE = DIGIT_WIDTH*DIGIT_HEIGHT
NUM_CLASS = 10

def setup_dnn(path):
    my_gpu = plat.getGpu()
    r = core.Roster()
    r.set_gpu(my_gpu)

    c = r.count_layers()
    input = core.InputLayer(c, IMAGE_SIZE, IMAGE_SIZE, None, r._gpu)
    r.layers.append(input)
    # 1 : hidden
    c = r.count_layers()
    hidden_1 = core.HiddenLayer(c, IMAGE_SIZE, 256, input, r._gpu)
    r.layers.append(hidden_1)
    # 2 : hidden
    c = r.count_layers()
    hidden_2 = core.HiddenLayer(c, 256, 256, hidden_1, r._gpu)
    r.layers.append(hidden_2)
    # 3 : output
    c = r.count_layers()
    output = core.OutputLayer(c, 256, 10, hidden_2, r._gpu)
    r.layers.append(output)
    
    r.set_path(path)
    r.set_scale_input(1)
    r.load()
    r.update_weight()
    return r

def get_brightness(pimg):
    gimg = pimg.convert('L')
    w = gimg.width
    h = gimg.height
    pmap = gimg.load()
    psum = 0
    for y in range(h):
        for x in range(w):
            psum = psum + pmap[x,y]
        #
    #
    b = float(psum) / float(w*h)
    b = b/255.0
    return b
    
def process_image(pimg, th, con=2.0):
    enhancer = ImageEnhance.Contrast(pimg)
    #enhancer = ImageEnhance.Sharpness(self.pimg_cropped)
    e_pimg = enhancer.enhance(con)
    pimg_inverted = ImageOps.invert(e_pimg)
    pimg_inverted = pimg_inverted.convert('L')
    pimg_processed = tool.pil_threshhold(pimg_inverted, th)
    pimg_processed = pimg_processed.resize((DIGIT_WIDTH, DIGIT_HEIGHT))
    return pimg_inverted, pimg_processed
    
def reader(pimg, path_rect, path_dnn, rotate=0):
    # rotate img
    if rotate!=0:
        pimg = pimg.rotate(rotate, expand=True)
    #
    
    #
    # load points and th from .csv
    #
    rect_list = tool.csv_to_list2d(path_rect, 1) # int
    
    nimg_list = []
    cnt = 0
    for line in rect_list:
        #
        # extract images of digits
        #
        rect = (line[0], line[1], line[0]+line[2], line[1]+line[3])
        #th = line[4]
        #con = line[5]
        pcrop = pimg.crop(rect)
        #
        # calc th
        #
        b = get_brightness(pcrop)
        th = 255 - int(b*0.9*255.0)
        #
        # prepare imgs to inference
        #
        pimg_inverted, pimg_processed = process_image(pcrop, th) # con
        w, h = pimg_processed.size
        nimg = np.array(pimg_processed)
        im_1d = nimg.reshape(h*w)
        nimg_list.append(im_1d)
        cnt = cnt + 1
    #
    
    #
    # inference
    #
    r = setup_dnn(path_dnn)
    if r:
        pass
    else:
        return 0
    #
    r.prepare(1, IMAGE_SIZE, NUM_CLASS)
    inf_list = []
    for data in nimg_list:
        ret = exam.inference(r, NUM_CLASS, data, IMAGE_SIZE)
        print("inf :", ret)
        inf_list.append(ret)
    #
    
    return inf_list

def main():
    argvs = sys.argv
    argc = len(argvs)
    #print(argvs)
    #print(argc)
    
    path_img = "./test/orig.jpeg"
    path_rotate = "./test/rect.csv"
    path_rect = "./test/rect.csv"
    path_dnn = "./test/wi-fc.csv"
    rotate = 0
        
    if os.path.isfile(path_img) is False:
        print("error : %s" % (path_img))
        return 0
    #
    
    dlist = tool.csv_to_list2d(path_rotate, 1)
    if len(dlist)!=1:
        print("error : no rotation setting")
    #
    rotate = dlist[0][0]
    print("rotate : %d" % (rotate), type(rotate))
    
    pimg = Image.open(path_img)
    list_inf = reader(pimg, path_rect, path_dnn, rotate)
    print(list_inf)

    return 0
#
#
#
if __name__=='__main__':
    print(">> start")
    sts = main()
    print(">> end")
    print("\007")
    sys.exit(sts)
#
#
#
