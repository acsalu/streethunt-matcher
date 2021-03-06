#!/usr/local/bin/python
#!/usr/bin/python

import cv2
import time
import numpy as np
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join
from numpy import *
from scipy.cluster.vq import kmeans,vq
from descriptor import test_feature_detector
from operator import itemgetter

def buildVocabulary(path,k,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    total_desc = []
    dict_vocab = []
    database_keypoints = []
    database_file_desc = []
    for f in files:
        print f
        keypoints,file_desc = test_feature_detector(path+f, grid_n)
        database_keypoints.append(keypoints)
        database_file_desc.append(file_desc)
        for i in range(0,grid_m):
            for j in range(0,grid_n):
                if len(total_desc) < 1:
                   total_desc.append(file_desc[j])
                else:
                   temp = total_desc[0]
                   total_desc[0] = np.vstack((temp,file_desc[j]))
    t1 = time.time()
    vocab,dist = kmeans(total_desc[0],k) # k is the seed number
    t2 = time.time()
    print 'Kmeans in grid[',j,'] takes',t2-t1
    dict_vocab.append(vocab)
    
    word_hist = []
    for fidx in range(0,len(files)):
        keypoints = database_keypoints[fidx]
        file_desc = database_file_desc[fidx]
        line_hist = []
        for i in range(0,grid_m):
            for j in range(0,grid_n):
                desc = array(file_desc[j])
                hist = buildWordHist(desc,dict_vocab[0])
                #if len(line_hist) == 0:
                #   line_hist = hist
                #else:
                #   line_hist = np.hstack((line_hist,hist))
                line_hist.append(hist)
        word_hist.append(line_hist)

    return dict_vocab,word_hist

def findWord(dict_vocab,path,grid_m,grid_n):
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    word_hist = []
    for f in files:
        keypoints,file_desc = test_feature_detector(path+f, grid_n)
        line_hist = []
        for i in range(0,grid_m):
            for j in range(0,grid_n):
                desc = array(file_desc[j])
                hist = buildWordHist(desc,dict_vocab[0])
                # if len(line_hist) == 0:
                #   line_hist = hist
                #else:
                #   line_hist = np.hstack((line_hist,hist))
                line_hist.append(hist)
        word_hist.append(line_hist)
    return word_hist

def buildWordHist(desc,dict_part):
    r = 2
    index,temp = vq(desc,dict_part)
    k = dict_part.shape[0]
    hist,bucket = np.histogram(index,bins = range(k+1))
    norm_hist = hist/double(sum(absolute(hist**r))**(1/r))
    return norm_hist

def calcDistance(t_hist,d_hist,grid_n):
    dist_table = []
    for i in range(0,len(t_hist)):
        total_dist = []
        for j in range(0,len(d_hist)):
              dist = []
              for k in range(0,grid_n):
                  for l in range(0,grid_n):
            	      dist.append(sum(absolute(t_hist[i][k]-d_hist[j][l])))
              total_dist.append(min(dist))
        dist_table.append(total_dist)
    return dist_table
 
def main():
    path = './images/'
    d_path = path+'test_find/database/'
    t_path = path+'test_find/testcase/'
    k = 30
    grid_m = 1
    grid_n = 4
    dict_vocab,d_hist = buildVocabulary(d_path,k,grid_m,grid_n)
    t_hist = findWord(dict_vocab,t_path,grid_m,grid_n)
    dist_table = calcDistance(t_hist,d_hist,grid_n)
    indices, sorted_dist = zip(*sorted(enumerate(dist_table[0]), key=itemgetter(1)))
    print 'indices'
    files = [ f for f in listdir(d_path) if isfile(join(d_path,f)) ]
    for i in range(0,len(indices)):
        print files[indices[i]]    

if __name__ == '__main__':
    main()
