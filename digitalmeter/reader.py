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
sys.path.append(os.path.join(os.path.dirname(__file__), '../ldnn'))
import plat
import util
import core
import train
import exam

sys.path.append(os.path.join(os.path.dirname(__file__), '../ptool/'))
import tool

IMAGE_SIZE = 16*24
NUM_CLASS = 10
W_VGA = 640
H_VGA = 480

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

def reader(pimg, path_rect, path_dnn):
    #
    # extract VGA at the center
    #
    
    #
    # finding center of image is ommitted, for now
    #
    ## pimg = Image.open(path_img)
    w_in, h_in = pimg.size
    if w_in<W_VGA or h_in<H_VGA:
        print("image should be VGA and larger")
        return 0
    #

    if w_in==W_VGA and h_in==H_VGA:
        pass
    else:
        crop_x = 0
        crop_y = 0
        dif_w = w_in - W_VGA
        dif_h = h_in - H_VGA
        crop_x = int(dif_w/2)
        crop_y = int(dif_h/2)
        #
        pimg = pimg.crop((crop_x, crop_y, crop_x+W_VGA, crop_y+H_VGA))
    #
    
    #
    # load points and th from .csv
    #
    rect_list = tool.csv_to_list2d(path_rect, 1) # int
    print(rect_list)
    
    #
    # extract images of digits
    #
    nimg_list = []
    for line in rect_list:
        rect = (line[0], line[1], line[0]+line[2], line[1]+line[3])
        th = line[4]
        print(rect, th)
        pcrop = pimg.crop(rect)
        pcrop = pcrop.convert("L")
        pcrop = ImageOps.invert(pcrop)
        pcrop = tool.pil_threshhold(pcrop, th)
        #
        pcrop = pcrop.resize((16, 24))
        print(pcrop.size)
        w, h = pcrop.size
        nimg = np.array(pcrop)
        im_1d = nimg.reshape(h*w)
        nimg_list.append(im_1d)
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
    
    temp = "%d%d.%d" % (inf_list[0], inf_list[1], inf_list[2])
    humd = "%d%d" % (inf_list[3], inf_list[4])
    return temp, humd

def main():
    argvs = sys.argv
    argc = len(argvs)
    print(argvs)
    print(argc)
    if argc!=2:
        print("need a file path")
        return 0
    #
    
    # check file path
    path_img = argvs[1]
    print(path_img)
    
    path_rect = "./rect.csv"
    path_dnn = "./wi-fc.csv"
        
    if os.path.isfile(path_img) is False:
        print("error : %s" % (path_img))
        return 0
    #
    temp, humd = reader(path_img, path_rect, path_dnn)

    # output
    print("temp :", temp)
    print("humd :", humd)
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
