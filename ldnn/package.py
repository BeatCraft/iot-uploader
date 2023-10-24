#! c:/Python26/python.exe
# -*- coding: utf-8 -*-

import os, sys, time, math
from stat import *
import random
import copy
import struct
import pickle
import numpy as np
import csv

from PIL import Image
from PIL import ImageFile
from PIL import JpegImagePlugin
from PIL import ImageFile
from PIL import PngImagePlugin
import zlib

# LDNN
import core
import util

TRAIN_IMAGE_PATH = ["../ldnn_package/MNIST/train-images-idx3-ubyte",
                    "../ldnn_package/cifar-10-batches-py/data_batch_1"]
TRAIN_LABEL_PATH = ["../ldnn_package/MNIST/train-labels-idx1-ubyte",
                    "../ldnn_config/cifar-10-batches-py/train_label_batch.pickle"]
TRAIN_IMAGE_BATCH_PATH = ["../ldnn_config/MNIST/train_image_batch.pickle",
                          "../ldnn_config/cifar-10-batches-py/train_image_batch.pickle"]
TRAIN_LABEL_BATCH_PATH = ["../ldnn_config/MNIST/train_label_batch.pickle",
                          "../ldnn_config/cifar-10-batches-py/train_label_batch.pickle"]
TRAIN_BATCH_SIZE = [60000, 50000]
TEST_BATCH_SIZE = [10000, 10000]
TEST_IMAGE_PATH = ["../ldnn_package/MNIST/t10k-images-idx3-ubyte",
                   "./"]
TEST_LABEL_PATH = ["../ldnn_package/MNIST/t10k-labels-idx1-ubyte",
                   "./"]
TEST_IMAGE_BATCH_PATH = ["../ldnn_config/MNIST/test_image_batch.pickle",
                         "../ldnn_config/cifar-10-batches-py/test_image_batch.pickle"]
TEST_LABEL_BATCH_PATH = ["../ldnn_config/MNIST/test_label_batch.pickle",
                         "../ldnn_config/cifar-10-batches-py/test_label_batch.pickle"]

PACKAGE_NAME = ["MNIST", "cifar-10-batches-py"]
PACKAGE_IMAGE_WIDTH = [28, 32]
PACKAGE_IMAGE_HEIGHT = [28, 32]
PACKAGE_IMAGE_SIZE = [784, 32*32*3]
PACKAGE_NUM_CLASS = [10, 10]

class Package:
    def __init__(self, package_id=0):
        self._package_id = package_id
        self._image_size = PACKAGE_IMAGE_SIZE[package_id]
        self._num_class = PACKAGE_NUM_CLASS[package_id]
        self._train_batch_size = TRAIN_BATCH_SIZE[package_id]
        self._test_batch_size = TEST_BATCH_SIZE[package_id]
        #
        self._name = PACKAGE_NAME[package_id]
        self._wi_csv_path = "../ldnn_config/%s/wi.csv" % (PACKAGE_NAME[package_id])
        self._w_float_path = "../ldnn_config/%s/wf.pickle" % (PACKAGE_NAME[package_id])
        self._w_save_path = None
        #
        self._train_image_path = TRAIN_IMAGE_PATH[package_id]
        self._train_label_path = TRAIN_LABEL_PATH[package_id]
        self._test_image_path = TEST_IMAGE_PATH[package_id]
        self._test_label_path = TEST_LABEL_PATH[package_id]
        #
        self._train_image_batch_path = TRAIN_IMAGE_BATCH_PATH[package_id]
        self._train_label_batch_path = TRAIN_LABEL_BATCH_PATH[package_id]
        self._test_image_batch_path = TEST_IMAGE_BATCH_PATH[package_id]
        self._test_label_batch_path = TEST_LABEL_BATCH_PATH[package_id]
        #
    def load_batch(self):
        if os.path.isfile(self._train_image_batch_path):
            self._train_image_batch = util.pickle_load(self._train_image_batch_path)
        else:
            print("error : no train image batch")
        #
        if os.path.isfile(self._train_label_batch_path):
            self._train_label_batch = util.pickle_load(self._train_label_batch_path)
        else:
            print("error : no train label batch")
        #
        if os.path.isfile(self._test_image_batch_path):
            self._test_image_batch = util.pickle_load(self._test_image_batch_path)
        else:
            print("error : no test image batch")
        #
        if os.path.isfile(self._test_label_batch_path) :
            self._test_label_batch = util.pickle_load(self._test_label_batch_path)
        else:
            print("error : no test label batch")
            print(self._test_label_batch_path)
        #
    
    def save_path_by_mode(self, mode=0):
        return self._wi_csv_path
#        if mode==0:
#            return self._wi_csv_path
#        elif mode==1:
#            return self._w_float_path
        #
#        return None
    
    def save_path(self):
        return self._w_save_path
    
    def setup_dnn(self, my_gpu, config=0, mode=0):
        r = core.Roster()
        r.set_gpu(my_gpu)
        #self._w_save_path = self._wi_csv_path

        if self._package_id==0: # MNIST
            if config==0:
                print("FC")
                #mode = r.mode()
                # 0 : input
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                r.input = input
                # 1 : hidden : 28 x 28 x 1 = 784
                c = r.count_layers()
                hidden_1 = core.HiddenLayer(c, 784, 64, input, my_gpu)
                r.layers.append(hidden_1)
                # 2 : hidden : 64
                c = r.count_layers()
                hidden_2 = core.HiddenLayer(c, 64, 64, hidden_1, my_gpu)
                r.layers.append(hidden_2)
                # 3 : hidden : 64
                c = r.count_layers()
                hidden_3 = core.HiddenLayer(c, 64, 64, hidden_2, my_gpu)
                r.layers.append(hidden_3)
                # 3 : output
                c = r.count_layers()
                output = core.OutputLayer(c, 64, 10, hidden_3, my_gpu)
                r.layers.append(output)
                r.output = output
            elif config==1:
                print("CNN")
                # 0 : input 28 x 28 x 1 = 784
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                # 1 : CNN 28 x 28 x 1 > 28 x 28 x 3
                c = r.count_layers()
                cnn_1 = core.Conv_4_Layer(c, 28, 28, 1, 3, input, my_gpu)
                r.layers.append(cnn_1)
                # 2 : max 28 x28 x 3 > 14 x 14 x 3
                c = r.count_layers()
                max_1 = core.MaxLayer(c, 3, 28, 28, cnn_1, my_gpu)
                r.layers.append(max_1)
                # 3 : CNN 14 x 14 x 3 > 14 x 14 x 6
                c = r.count_layers()
                cnn_2 = core.Conv_4_Layer(c, 14, 14, 3, 6, max_1, my_gpu)
                r.layers.append(cnn_2)
                # 4 : max 14 x 14 x 6 > 7 x 7 x 6
                c = r.count_layers()
                max_2 = core.MaxLayer(c, 6, 14, 14, cnn_2, my_gpu)
                r.layers.append(max_2)
                # 5 : hidden : (7 x 7 x 160 X 64 = 784 x 64
                c = r.count_layers()
                hidden_1 = core.HiddenLayer(c, 294, 64, max_2, my_gpu)
                r.layers.append(hidden_1)
                # 6 : hidden : 64 x 64
                c = r.count_layers()
                hidden_2 = core.HiddenLayer(c, 64, 64, hidden_1, my_gpu)
                r.layers.append(hidden_2)
                # 7 : output : 64 x 10
                c = r.count_layers()
                output = core.OutputLayer(c, 64, 10, hidden_2, my_gpu)
                r.layers.append(output)
            #
        elif self._package_id==1: # cifa-10
            if config==0:
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                r.input = input

                c = r.count_layers()
                hidden_1 = core.HiddenLayer(c, 3072, 256, input, my_gpu)
                r.layers.append(hidden_1)
                
                c = r.count_layers()
                hidden_2 = core.HiddenLayer(c, 256, 256, hidden_1, my_gpu)
                r.layers.append(hidden_2)

                c = r.count_layers()
                hidden_3 = core.HiddenLayer(c, 256, 256, hidden_2, my_gpu)
                r.layers.append(hidden_3)

                c = r.count_layers()
                output = core.OutputLayer(c, 256, 10, hidden_3, my_gpu)
                r.layers.append(output)
                r.output = output
            elif config==1:
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                
                c = r.count_layers()
                cnn_1 = core.Conv_4_Layer(c, 32, 32, 3, 16, input, my_gpu)
                r.layers.append(cnn_1)
                
                c = r.count_layers()
                cnn_2 = core.Conv_4_Layer(c, 32, 32, 16, 16, cnn_1, my_gpu)
                r.layers.append(cnn_2)
                
                c = r.count_layers()
                max_1 = core.MaxLayer(c, 16, 32, 32, cnn_2, my_gpu) # 8192
                r.layers.append(max_1)
                
                c = r.count_layers()
                fc_1 = core.HiddenLayer(c, 4096, 512, max_1, my_gpu)
                r.layers.append(fc_1)
                
                c = r.count_layers()
                fc_2 = core.HiddenLayer(c, 512, 512, fc_1, my_gpu)
                r.layers.append(fc_2)
                
                c = r.count_layers()
                output = core.OutputLayer(c, 512, 10, fc_2, my_gpu)
                r.layers.append(output)
            #
            elif config==2:
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                
                c = r.count_layers()
                cnn_1 = core.Conv_4_Layer(c, 32, 32, 3, 16, input, my_gpu)
                r.layers.append(cnn_1)
                
                c = r.count_layers()
                cnn_2 = core.Conv_4_Layer(c, 32, 32, 16, 16, cnn_1, my_gpu)
                r.layers.append(cnn_2)
                
                c = r.count_layers()
                max_1 = core.MaxLayer(c, 16, 32, 32, cnn_2, my_gpu) # 16 x 16 x 16 = 8192
                r.layers.append(max_1)
                
                c = r.count_layers()
                cnn_3 = core.Conv_4_Layer(c, 16, 16, 16, 32, max_1, my_gpu)
                r.layers.append(cnn_3)
                
                c = r.count_layers()
                cnn_4 = core.Conv_4_Layer(c, 16, 16, 32, 32, cnn_3, my_gpu)
                r.layers.append(cnn_4)
                
                c = r.count_layers()
                max_2 = core.MaxLayer(c, 32, 16, 16, cnn_4, my_gpu) # 8 x 8 x 32 = 2048
                r.layers.append(max_2)
                
                c = r.count_layers()
                fc_1 = core.HiddenLayer(c, 2048, 128, max_2, my_gpu)
                r.layers.append(fc_1)
                
                c = r.count_layers()
                fc_2 = core.HiddenLayer(c, 128, 128, fc_1, my_gpu)
                r.layers.append(fc_2)
                
                c = r.count_layers()
                output = core.OutputLayer(c, 128, 10, fc_2, my_gpu)
                r.layers.append(output)
            #
            elif config==3: # minicing LeNet
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                
                c = r.count_layers()
                cnn_1 = core.Conv_4_Layer(c, 32, 32, 3, 8, input, my_gpu)
                r.layers.append(cnn_1)
                
                c = r.count_layers()
                max_1 = core.MaxLayer(c, 8, 32, 32, cnn_1, my_gpu) # 8 x 16 x 16 = 2048
                r.layers.append(max_1)
                
                c = r.count_layers()
                cnn_2 = core.Conv_4_Layer(c, 16, 16, 8, 8, max_1, my_gpu)
                r.layers.append(cnn_2)
                
                c = r.count_layers()
                max_2 = core.MaxLayer(c, 8, 16, 16, cnn_2, my_gpu) # 8 x 8 x 8 = 512
                r.layers.append(max_2)
                
                c = r.count_layers()
                cnn_3 = core.Conv_4_Layer(c, 8, 8, 8, 8, max_2, my_gpu)
                r.layers.append(cnn_3)
                
                c = r.count_layers()
                max_3 = core.MaxLayer(c, 8, 8, 8, cnn_3, my_gpu) # 8 x 4 x 4 = 128
                r.layers.append(max_3)
                
                c = r.count_layers()
                fc_1 = core.HiddenLayer(c, 128, 128, max_3, my_gpu)
                r.layers.append(fc_1)
                
                c = r.count_layers()
                output = core.OutputLayer(c, 128, 10, fc_1, my_gpu)
                r.layers.append(output)
            #
            elif config==4: # minicing LeNet
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu)
                r.layers.append(input)
                
                c = r.count_layers()
                cnn_1 = core.Conv_4_Layer(c, 32, 32, 3, 6, input, my_gpu)
                r.layers.append(cnn_1)
                
                c = r.count_layers()
                max_1 = core.MaxLayer(c, 6, 32, 32, cnn_1, my_gpu) # 6 x 16 x 16 = 1536
                r.layers.append(max_1)
                
                c = r.count_layers()
                cnn_2 = core.Conv_4_Layer(c, 16, 16, 6, 12, max_1, my_gpu)
                r.layers.append(cnn_2)
                
                c = r.count_layers()
                max_2 = core.MaxLayer(c, 12, 16, 16, cnn_2, my_gpu) # 12 x 8 x 8 = 768
                r.layers.append(max_2)
                
                c = r.count_layers()
                fc_1 = core.HiddenLayer(c, 768, 128, max_2, my_gpu)
                r.layers.append(fc_1)
                
                c = r.count_layers()
                fc_2 = core.HiddenLayer(c, 128, 128, fc_1, my_gpu)
                r.layers.append(fc_2)
                
                c = r.count_layers()
                output = core.OutputLayer(c, 128, 10, fc_2, my_gpu)
                r.layers.append(output)
            #
        elif self._package_id==2: # codec test
            if config==0:
                print("FC")
                # 0 : input
                c = r.count_layers()
                input = core.InputLayer(c, self._image_size, self._image_size, None, my_gpu, mode)
                r.layers.append(input)
                # 1 : enc
                c = r.count_layers()
                enc_1 = core.HiddenLayer(c, 128, 32, input, my_gpu, mode)
                r.layers.append(enc_1)
                # 2 : enc
                c = r.count_layers()
                enc_2 = core.HiddenLayer(c, 32, 32, enc_1, my_gpu, mode)
                r.layers.append(enc_2)
                # 3 : intermediate
                c = r.count_layers()
                inter = core.HiddenLayer(c, 32, 4, enc_2, my_gpu, mode)
                r.layers.append(inter)
                # 4 : dec
                c = r.count_layers()
                dec_1 = core.HiddenLayer(c, 4, 32, inter, my_gpu, mode)
                r.layers.append(dec_1)
                # 5 : dec
                c = r.count_layers()
                dec_2 = core.HiddenLayer(c, 32, 32, dec_1, my_gpu, mode)
                r.layers.append(dec_2)
                # 3 : output
                c = r.count_layers()
                output = core.OutputLayer(c, 32, 128, dec_2, my_gpu, mode)
                r.layers.append(output)
            #
        else:
            print("package error")
            return None
        #
        #if os.path.isfile(self.save_path()):
        #    r.import_weight(self.save_path())
        #else:
        #    r.init_weight()
        #    r.export_weight(self.save_path())
        #
        #if my_gpu:
        #    r.update_weight()
        #
        return r

def echo(data):
    print(data)
