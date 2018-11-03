# -*- coding: utf-8 -*-
"""
Created March 2018
@author: lisam

This program uses google 2grams to determine the relative probability of two words occurring
in a row.

Input: pre is the first word in the bigram, choices are a list of potential second words to get prob for.                                                                  
Output: Tuples that have the word with it's probability of occurring.
"""

import nltk
from nltk import bigrams
import re
import os
from os.path import exists
import datetime

cwd = os.getcwd()
(thing_I_want, thing_I_dont_want) = os.path.split(os.getcwd())
(thing_I_want_most, thing_I_dont_want) = os.path.split(thing_I_want)
ngramsPath = os.path.join(thing_I_want_most, 'googleLDC2gms',  'trimmed100')

def testOption(pre, choices):
    now = datetime.datetime.now()
    #print ("Current date and time : ", now.strftime("%Y-%m-%d %H:%M:%S"))
    countSize = 910884463583 #total number of bigrams in all files
    choicesProbs = []
    
    # first find the file that the bigram should be in
    if (pre < ','):
        fname = os.path.join(ngramsPath, '2gm-0000.txt')
    elif (pre < '04530'):
        fname = os.path.join(ngramsPath, '2gm-0001.txt')
    elif (pre < '17'):
        fname = os.path.join(ngramsPath, '2gm-0002.txt')
    elif (pre < '29425'):
        fname = os.path.join(ngramsPath, '2gm-0003.txt')
    elif (pre < '6th'):
        fname = os.path.join(ngramsPath, '2gm-0004.txt')
    elif (pre < '<S>'):
        fname = os.path.join(ngramsPath, '2gm-0005.txt')
    elif (pre < 'ABCbodybuilding'):
        fname = os.path.join(ngramsPath, '2gm-0006.txt')
    elif (pre < 'BRIDGEPORT'):
        fname = os.path.join(ngramsPath, '2gm-0007.txt')
    elif (pre < 'Captain'):
        fname = os.path.join(ngramsPath, '2gm-0008.txt')
    elif (pre < 'David'):
        fname = os.path.join(ngramsPath, '2gm-0009.txt')
    elif (pre < 'FRAME'):
        fname = os.path.join(ngramsPath, '2gm-0010.txt')
    elif (pre < 'HUSH'):
        fname = os.path.join(ngramsPath, '2gm-0011.txt')
    elif (pre < 'Johann'):
        fname = os.path.join(ngramsPath, '2gm-0012.txt')
    elif (pre < 'MISIÓN'):
        fname = os.path.join(ngramsPath, '2gm-0013.txt')
    elif (pre < 'Network'):
        fname = os.path.join(ngramsPath, '2gm-0014.txt')
    elif (pre < 'Pixel'):
        fname = os.path.join(ngramsPath, '2gm-0015.txt')
    elif (pre < 'Russian'):
        fname = os.path.join(ngramsPath, '2gm-0016.txt')
    elif (pre < 'Star'):
        fname = os.path.join(ngramsPath, '2gm-0017.txt')
    elif (pre < 'U'):
        fname = os.path.join(ngramsPath, '2gm-0018.txt')
    elif (pre < 'Zebra'):
        fname = os.path.join(ngramsPath, '2gm-0019.txt')
    elif (pre < 'at'):
        fname = os.path.join(ngramsPath, '2gm-0020.txt')
    elif (pre < 'civIV'):
        fname = os.path.join(ngramsPath, '2gm-0021.txt')
    elif (pre < 'doubt'):
        fname = os.path.join(ngramsPath, '2gm-0022.txt')
    elif (pre < 'frist'):
        fname = os.path.join(ngramsPath, '2gm-0023.txt')
    elif (pre < 'influx'):
        fname = os.path.join(ngramsPath, '2gm-0024.txt')
    elif (pre < 'measuring'):
        fname = os.path.join(ngramsPath, '2gm-0025.txt')
    elif (pre < 'ordinate'):
        fname = os.path.join(ngramsPath, '2gm-0026.txt')
    elif (pre < 'readiness'):
        fname = os.path.join(ngramsPath, '2gm-0027.txt')
    elif (pre < 'somehow'):
        fname = os.path.join(ngramsPath, '2gm-0028.txt')
    elif (pre < 'to'):
        fname = os.path.join(ngramsPath, '2gm-0029.txt')
    elif (pre < 'woman'):
        fname = os.path.join(ngramsPath, '2gm-0030.txt')
    else:  
        fname = os.path.join(ngramsPath, '2gm-0031.txt')
    
    try:
        with open(fname, 'r', encoding="utf-8") as file: # open the file once it's found
            try:
                text = file.readlines()
            except UnicodeEncodeError:
                pass
            
            for line in text: # for each bigram in the file
                try:
                    length = len(pre)
                    if (line[:length] == pre):
                        curr = line.split('\t')
                        words = curr[0].split(' ')
                        if (words[0] <= pre):
                            for ch in choices: # Here check if it is any of the words I'm looking for.
                                if (words[0] == pre and words[1] == ch and len(curr) > 1):
                                    choicesProbs.append((ch, int(curr[1])/countSize)) # if it is add to return list
                except UnicodeEncodeError:
                    pass
    except FileNotFoundError:
        ('Google LDC grams corpus not found...will continue without bigrams language modeling.')
                                
    now = datetime.datetime.now()
    #print ("Current date and time : ", now.strftime("%Y-%m-%d %H:%M:%S"))
    return choicesProbs
  
