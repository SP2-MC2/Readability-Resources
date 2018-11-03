# -*- coding: utf-8 -*-
"""
Created March 2018
@author: lisam

This program creates a cyberdictionary sorted on parts of speech 
(assuming one doesn't already exist saved as 'cyberDictionary.txt'. 
It looks at a folder called cyberDictionaryTexts to get all the words from the text
files inside that folder. In our case we just used the entire corpus in our
readability project.

Input: a flag that's 'True' if the pos tagger is spacy and 'None' for wordnet                      
Output: A list of tuples, first part is the pos abbreviation, i.e. 'NN' for noun, 
the second part is a list of the nouns found.

"""

import nltk
import json
import string
import os
from os.path import exists
from nltk.corpus import wordnet as wn
from nltk import pos_tag
from nltk import word_tokenize

spacyFlag = None # None for wordnet
folderName = 'dictionaryTexts'
cwd = os.getcwd()
cyberDictPath = os.path.join(cwd, folderName)

def getDict(flag):
    
    global spacyFlag
    spacyFlag = flag # set for spacy dictionary
    if (flag):
        import spacy

    cyberTermsPOSlib = [('CC',[]),('CD',[]),('DT',[]),('EX',[]),('FW',[]),('IN',[]),('JJ',[]),('JJR',[]),('JJS',[]),('LS',[]),('MD',[]),('NN',[]),('NNP',[]),('NNPS',[]),('NNS',[]),('PDT',[]),('POS',[]),('PRP',[]),('PRP$',[]),('RB',[]),('RBR',[]),('RBS',[]),('RP',[]),('TO',[]),('UH',[]),('VB',[]),('VBD',[]),('VBG',[]),('VBN',[]),('VBP',[]),('VBZ',[]),('WDT',[]),('WP',[]),('WP$',[]),('WRB',[])]
    
    # make this a load cyber dictionary instead of create each time
    fname = os.path.join(cwd, 'cyberDictionary.txt')
    if exists(fname):
        with open(fname,'r') as file:
            content = file.read().splitlines()
            #print (content)
            i = 0
            while (i < len(content)):
                for item in cyberTermsPOSlib:
                    if (item[0] == content[i]):
                        i += 1
                        poses = content[i].split(' ')
                        for pos in poses:
                            item[1].append(pos)
                i += 1

    else: # if no cyber dictionary I must read through all the cyber texts and pos tag them.
        for item in os.listdir(cyberDictPath): # open each file
            filename = os.path.join(cwd, folderName, item)
            with open(filename,"r") as fid:
                text = fid.read()
                
                tagged = []
                # this is where the pos tagging comes in:
                if (spacyFlag == True):
                    nlp = spacy.load('en')
                    #sentence = unicode(text, "utf-8")
                    charCount = 0
                    #doc = []
                    if (len(text) < 999999): # nlp(text) only works for files under 1 mil words
                        # while (charCount <= len(text)):
                            # doc.append(nlp(text[charCount:charCount+999999]))
                            # charCount += 999999
                    # else:
                        doc = nlp(text)
                    #for set in doc:
                        for token in doc:
                            tagged.append((token.text, token.tag_))
                else:
                    tokenized = word_tokenize(text)
                    
                    tagged = pos_tag(tokenized)   # get POS for every word
                
                #assign to a list
                for val in tagged: # each pos tagged word gets put into the final library list
                    for pos in cyberTermsPOSlib:
                        if (pos[0] == val[1]):  # the word is that pos
                            if (val[0].lower() not in pos[1]):
                                pos[1].append(val[0].lower())
                                
        cyberTermsPOSlib = weed_library(cyberTermsPOSlib)
        
        # once done, save to file
        with open(fname,'w') as file:
            for ele in cyberTermsPOSlib:
                file.write(ele[0]+'\n')
                for item in ele[1]:
                    file.write(item+' ')
                file.write('\n')
    return (cyberTermsPOSlib)
    
# This function attempts to remove punctuations from the library
def weed_library(posLib):
    punctuations = '''``'!!!!!()-[]{};;;:'"\,,<>....|||/?@#$%^&*_~'''
    tempLib = [('CC',[]),('CD',[]),('DT',[]),('EX',[]),('FW',[]),('IN',[]),('JJ',[]),('JJR',[]),('JJS',[]),('LS',[]),('MD',[]),('NN',[]),('NNP',[]),('NNPS',[]),('NNS',[]),('PDT',[]),('POS',[]),('PRP',[]),('PRP$',[]),('RB',[]),('RBR',[]),('RBS',[]),('RP',[]),('TO',[]),('UH',[]),('VB',[]),('VBD',[]),('VBG',[]),('VBN',[]),('VBP',[]),('VBZ',[]),('WDT',[]),('WP',[]),('WP$',[]),('WRB',[])]
    
    for pos in posLib:
        for temp in tempLib:
            if (pos[0] == temp[0]): # once both libraries are at the same pos
                count = 0
                for item in pos[1]:
                    if (item not in punctuations and item != 'n\'t' and item != ' ' and len(item) > 0): # not punctuation
                        for char in item:
                            if (char in punctuations):
                                count += 1
                        if (count < 2):
                            temp[1].append(item)
                    #else:
                       # print ('shouldn\'t be added to the dictionary')
                        
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
        
        
        
