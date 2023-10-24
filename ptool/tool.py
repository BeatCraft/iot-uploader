#! /usr/bin/python
# -*- coding: utf-8 -*-
#
import os, sys, time, math
from stat import *
import pickle
import numpy as np
import csv

def list2d_to_csv(l2d, fpath):
    pass

def csv_to_list2d(fpath, type=0):
    l2d = []
    with open(fpath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            line = []
            for cell in row:
                if type==0: # through
                    line.append(cell)
                elif type==1: # int
                    line.append(int(cell))
                #
            #
            l2d.append(line)
        #
        return l2d
    #
    return None
    
def pil_threshhold(pimg, th):
    w, h = pimg.size
    for y in range(h):
        for x in range(w):
            pv = pimg.getpixel((x, y))
            if pv>th:
                pimg.putpixel((x,y),(255))
            else:
                pimg.putpixel((x,y),(0))
            #
        #
    #
    return pimg

def pickle_save(path, data):
    with open(path, mode='wb') as f:
        pickle.dump(data, f)
    #

def pickle_load(path):
    try:
        with open(path, mode='rb') as f:
            data = pickle.load(f)
            return data
        #
    except:
        return None
    #

def scan_dir_for_image(path):
    files = os.listdir(path)
    plist = []
    for f in files:
        fpath = os.path.join(path, f)
        if os.path.isfile(fpath):
            fname, ext = os.path.splitext(fpath)
            if ext==".png" or ext==".PNG" or ext==".jpg" or ext==".JPG" or ext==".jpeg" or ext==".JPEG":
                plist.append(fpath)
            #
        #
    #
    return plist

def scan_dir_dir(path):
    files = os.listdir(path)
    plist = []
    for f in files:
        fpath = os.path.join(path, f)
        if os.path.isdir(fpath):
            plist.append(fpath)
        #
    #
    return plist

def scan_dir_with(path, extension):
    files = os.listdir(path)
    plist = []
    for f in files:
        fpath = os.path.join(path, f)
        if os.path.isfile(fpath):
            fname, ext = os.path.splitext(fpath)
            if ext.upper()==extension.upper():
                plist.append(fpath)
            #
        #
    #
    return plist

def list_to_csv(path, data_list):
    with open(path, 'wb') as file:
        wr = csv.writer(file, quoting=csv.QUOTE_ALL)
        wr.writerow(data_list)
    #
    
def csv_to_list(path, skip=False):
    #print("csv_to_list(%s)" % (path))
    data_list = []
    try:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            if skip==True:
                header = next(reader)
            #
            #print(reader)
            for row in reader:
                line = []
                for cell in row:
                    line.append(cell)
                #
                data_list.append(line)
            #
        #
        return data_list
    except Exception as e:
        print("error: %s" % e)
        return data_list
    #
    return data_list

def main():
    argvs = sys.argv
    argc = len(argvs)
    print(argc)
    return 0

if __name__=='__main__':
    print(">> start")
    sts = main()
    print(">> end")
    print("\007")
    sys.exit(sts)
#
#
#
