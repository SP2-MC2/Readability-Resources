# -*- coding: utf-8 -*-
"""
Created March 2018
@author: lisam

This program creates a normal dictionary sorted on parts of speech 
(assuming one doesn't already exist saved as 'normalDictionary.txt'. 
It uses the brown corpus from nltk to load the words. In our case we just used 
the entire corpus in our readability project.

Input: a flag that's 'True' if the pos tagger is spacy and 'None' for wordnet                      
Output: A list of tuples, first part is the pos abbreviation, i.e. 'NN' for noun, 
the second part is a list of the nouns found.

(there are more detailed comments throughout the procedure in 'createCyberDictionary.txt')

"""

import nltk
import json
import string
import os
from os.path import exists
from nltk.corpus import wordnet as wn
from nltk import pos_tag
from nltk import word_tokenize
from nltk.corpus import brown

spacyFlag = None # None for wordnet
folderName = 'dictionaryTexts'
cwd = os.getcwd()
distractorDictPath = os.path.join(cwd, folderName)

def getDict(flag):
    global spacyFlag
    spacyFlag = flag # set for spacy dictionary
    if (flag):
        import spacy
    
    normalPOSlib = [('CC',[]),('CD',[]),('DT',[]),('EX',[]),('FW',[]),('IN',[]),('JJ',[]),('JJR',[]),('JJS',[]),('LS',[]),('MD',[]),('NN',[]),('NNP',[]),('NNPS',[]),('NNS',[]),('PDT',[]),('POS',[]),('PRP',[]),('PRP$',[]),('RB',[]),('RBR',[]),('RBS',[]),('RP',[]),('TO',[]),('UH',[]),('VB',[]),('VBD',[]),('VBG',[]),('VBN',[]),('VBP',[]),('VBZ',[]),('WDT',[]),('WP',[]),('WP$',[]),('WRB',[])]
    
    # make this a load normal dictionary instead of create each time
    fname = os.path.join(cwd, 'normalDictionary.txt')
    if exists(fname):
        with open(fname,'r') as file:
            content = file.read().splitlines()
            i = 0
            while (i < len(content)):
                for item in normalPOSlib:
                    if (item[0] == content[i]):
                        i += 1
                        poses = content[i].split(' ')
                        for pos in poses:
                            item[1].append(pos)
                i += 1

    else:
        tagged = []
        if (spacyFlag == True):
            nlp = spacy.load('en')
            #sentence = unicode(text, "utf-8")
            charCount = 0
            
            for curr in brown.words():
                doc = nlp(curr)
                for token in doc:
                    tagged.append((token.text, token.tag_))
        else:
            for curr in brown.words():
                tokenized = word_tokenize(curr)
                # get POS for every word
                tag = pos_tag(tokenized)
                tagged.append(tag)
                               
        #assign to a list
        for val in tagged:
            for pos in normalPOSlib:
                if (pos[0] == val[1]):  # the word is that pos
                    if (val[0].lower() not in pos[1]):
                        pos[1].append(val[0].lower())
                               
        normalPOSlib = weed_library(normalPOSlib)
        # once done, save to file
        with open(fname,'w') as file:
            for ele in normalPOSlib:
                file.write(ele[0]+'\n')
                for item in ele[1]:
                    file.write(item+' ')
                file.write('\n')
    #print (normalPOSlib) 
    return (normalPOSlib)
    
def weed_library(posLib):
    punctuations = '''``'!!!!!()-[]{};;;:'"\,,<>....|||/?@#$%^&*_~'''
    tempLib = [('CC',[]),('CD',[]),('DT',[]),('EX',[]),('FW',[]),('IN',[]),('JJ',[]),('JJR',[]),('JJS',[]),('LS',[]),('MD',[]),('NN',[]),('NNP',[]),('NNPS',[]),('NNS',[]),('PDT',[]),('POS',[]),('PRP',[]),('PRP$',[]),('RB',[]),('RBR',[]),('RBS',[]),('RP',[]),('TO',[]),('UH',[]),('VB',[]),('VBD',[]),('VBG',[]),('VBN',[]),('VBP',[]),('VBZ',[]),('WDT',[]),('WP',[]),('WP$',[]),('WRB',[])]
    
    for pos in posLib:
        for temp in tempLib:
            if (pos[0] == temp[0]): # once they're at the same pos
                count = 0
                for item in pos[1]:
                    if (item not in punctuations and item != 'n\'t' and item != ' ' and len(item) > 0): # not punctuation
                        for char in item:
                            if (char in punctuations):
                                count += 1
                        if (count < 2):
                            temp[1].append(item)
                    #else:
                       # print ('shouldn\'t be added')
                        
    return tempLib

# what each POS means
# CC- conjunction, coordinating
# CD- numeral, cardinal
# DT- determiner
# EX- existential there
# FW- idk what this is ********************************
# IN- preposition or conjunction, subordinating
# JJ- adjective or numeral, ordinal
# JJR - adjective, comparative
# JJS- adjective, superlative
# LS- list item marker
# MD - modal auxiliary
# NN - noun, common, singular or mass
# NNP- noun, proper, singular
# NNPS- noun, proper, not singular
# NNS- noun, common, plural
# PDT- pre determiner
# POS- genitive marker
# PRP- pronoun, personal
# PRP$- pronoun, possessive
# RB- adverb
# RBR- adverb, comparative
# RBS- adverb, superlative
# RP- particle
# TO- "to" as a preposition or infinite marker
# UH- interjection
# VB- verb, base format
# VBD- verb, past tense
# VBG- verb, present participle or gerund
# VBN- verb, past participle
# VBP- verb, present tense, not 3rd person singular
# VBZ- verb, present tense, 3rd person singular
# WDT- WH-determiner
# WP- WH-pronoun
# WP$- WH-pronoun, possessive
# WRB- WH-adverb
        
        
        
