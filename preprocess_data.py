"""
Updated 3/18/18
@author: lisa m

This program looks for appropriately placed blanks in an article, 
i.e. verbs and nouns. It was built for the purpose of creating fill in the 
blank questionnaires assessing the readability of security advice.

Input: A block of text.
Output: A json including: -the locations for blanks, the choices for the blanks, the answers.

"""

import nltk
import json
import string
import os
import re
import time
import copy
import random
from random import shuffle
import bigrams as bg
from nltk.corpus import wordnet as wn
from nltk import pos_tag
from nltk import word_tokenize
import createCyberDictionary as createCyberDict
import createNormalDictionary as createNormalDict
spacyFlag = True # None for wordnet
if (spacyFlag):
    import spacy

# Definitons for abbreviations avaiable in posDefintions.txt
currDocPOSlib = [('CC',[]),('CD',[]),('DT',[]),('EX',[]),('FW',[]),('IN',[]),('JJ',[]),('JJR',[]),('JJS',[]),('LS',[]),('MD',[]),('NN',[]),('NNP',[]),('NNPS',[]),('NNS',[]),('PDT',[]),('POS',[]),('PRP',[]),('PRP$',[]),('RB',[]),('RBR',[]),('RBS',[]),('RP',[]),('TO',[]),('UH',[]),('VB',[]),('VBD',[]),('VBG',[]),('VBN',[]),('VBP',[]),('VBZ',[]),('WDT',[]),('WP',[]),('WP$',[]),('WRB',[])]

blanks = []
choices = [] 
answers = []
smartCloze = False # changes various settings
cyberDict = True # None for normal distractors
cyberTermsPOSlib = createCyberDict.getDict(spacyFlag)
normalPOSlib = createNormalDict.getDict(spacyFlag)

# analysis booleans
stats = [0,0,0,0,0,0]  #numFilesProcessed, numTimesDistractorRejectedTotal, numTimesDistractorAcceptedTotal, numTimesDistractorRejectedCurr, numTimesDistractorAcceptedCurr = 0

def init(document):
    # first create libraries for this file
    text = document
    tagged = []
  
    if (spacyFlag):
        nlp = spacy.load('en')
        doc = nlp(text)
        charCount = 0
        if (len(text) > 999999): # spacy tagger limit
            text = text[0:999999]
        doc = nlp(text)
        for token in doc:
            tagged.append((token.text, token.tag_))
            
    else:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        
    #assign to a list
    currDocPOSlib = [('CC',[]),('CD',[]),('DT',[]),('EX',[]),('FW',[]),('IN',[]),('JJ',[]),('JJR',[]),('JJS',[]),('LS',[]),('MD',[]),('NN',[]),('NNP',[]),('NNPS',[]),('NNS',[]),('PDT',[]),('POS',[]),('PRP',[]),('PRP$',[]),('RB',[]),('RBR',[]),('RBS',[]),('RP',[]),('TO',[]),('UH',[]),('VB',[]),('VBD',[]),('VBG',[]),('VBN',[]),('VBP',[]),('VBZ',[]),('WDT',[]),('WP',[]),('WP$',[]),('WRB',[])]
    for val in tagged:
        for pos in currDocPOSlib:
            if (pos[0] == val[1]):  # the word is that pos
                if ((val[0]).lower() not in pos[1]):
                    pos[1].append(val[0].lower())
                    
    currDocPOSlib = createCyberDict.weed_library(currDocPOSlib)
    return currDocPOSlib

def process_document(document):
    currDocPOSlib = init(document)
    blanks = []
    choices = [] 
    answers = []
    text = document
    text = text.split('.')
    
    i = 0
    preamble = ""
    start = 0
    
    if (smartCloze): # skip first five sentences (put no blanks there)
        # we considered using this to give the reader a general idea of what
        # the article is about before adding blanks
        while (i<5):
            preamble += (text[i])
            preamble += '.'
            i = i+1
            
        start = len(word_tokenize(preamble))
    
    # rest of text to find the blanks for; start counting the number of blanks from here
    lines = ""
    preambleEnd = i
    while (i < len(text)):
        if (text[i] != " "):
            lines += (text[i])
            lines += "."
        i += 1
    
    # remove citations using regex
    p = re.compile('\[([0-9]*)\]')
    lines = p.sub('', lines)
    
    tagged = []
    tokenized = word_tokenize(lines)
  
    # pos tag the document
    if (spacyFlag):
        nlp = spacy.load('en')
        if (len(lines) > 999999): # spacy tagger limit
            lines = lines[0:999999]
        doc = nlp(lines)
        for token in doc:
            tagged.append((token.text, token.tag_))
            
    else:
        tagged = pos_tag(tokenized)
    
    tempOutput = ""
    choices = []
    posToIgnore = ['CC','CD','DT','EX','FW','IN','MD','NNP','NNPS','PDT','POS','PRP','PRP$','RBS','RP','TO','UH','WDT','WP','WP$''WRB']
    
    j = 0
    spacingVal = 5 # every nth word is a blank (in our case we used 5)
    count = 1
    numBlanks = 0
    trigger = False
    addLinesAsYouGo = ""
    pre = ''
    punctuations = '''``'-!!!!!()[]{};;;:'"\,,<>..../?@#$%^&*_~'''
    puncNoSpace = '''``'!!!!!;;;:'"\,,<>..../?@#$%^&*_~'''
    
    # This section is fairly complex and probably could be more simple.
    # It is trying to count every nth word to make a blank, until we have 35
    #blanks, skipping over punctuations, etc.
    while (j < len(tagged) and numBlanks <= 50): # while still in document text
        if (numBlanks > 34): # we wanted to have exactly 35 blanks, 0-based indexing ftw
            trigger = True # end after next period
        if (tagged[j][0][0] == '.' and trigger): # end sentence then end the while loop
            numBlanks = 100
             
        # this section preserves the text we want so far with appropriate spacing
        if (tagged[j][0][0] in puncNoSpace):
            addLinesAsYouGo += tagged[j][0]
        elif (len(tagged[j][0]) > 1 and tagged[j][0][1] in puncNoSpace): # for n't
            addLinesAsYouGo += tagged[j][0]
        else: # not punctuation that requires space
            addLinesAsYouGo += ' ' + tagged[j][0]

        if (j < len(tagged) and j < len(tokenized) and tagged[j][0][0].lower() in puncNoSpace): # for 's
            tempOutput += tokenized[j]
        elif (j < len(tagged) and j < len(tokenized) and len(tagged[j][0]) > 1 and tagged[j][0][1].lower() in puncNoSpace): # for n't
            tempOutput += tokenized[j]
            tempOutput += ' ' + tokenized[j]
        elif (count % spacingVal == 0 and j < len(tagged) and numBlanks <= 34): # word for blank
            count = 1
            # check if word is plural of something
            if (j+1 < len(tagged) and j < len(tokenized)-1 and (tokenized[j+1][0] == '\'' or (len(tokenized[j+1]) > 1 and tokenized[j+1][1] == '\''))):
                word = (tagged[j][0].lower() + tagged[j+1][0].lower())
                listVal = pos_tag([word])
                val = listVal[0][1]
            else:
                word = (tagged[j][0]).lower()
                val = tagged[j][1]
            
            # this word has been chosen for a blank
            blanks.append(j+start) # the location of the blank
            order = get_choices(word, val, currDocPOSlib, pre) # generate potential choices
            choices.append(order) # these are the 4 distrators and 1 correct answer
            answers.append(word) # hte ocrrect answer
            numBlanks += 1 # increase the number of blanks generated
            tempOutput += ('(' + str(order) + ')-[' + val + ']')
            pre = word # save the prior word
        elif (j < len(tagged) and j < len(tokenized) and tokenized[j][0] not in puncNoSpace):
            pre = tokenized[j]
            tempOutput += ' ' + pre
            count += 1
        j += 1
        
    document = preamble + addLinesAsYouGo # add preamble if you choose the
    # smartCloze option to keep the document correct.
    
    data = {}
    data['article'] = document
    data['blanks'] = blanks
    data['choices'] = choices 
    data['answers'] = answers
       
    return data
    
# Method that takes a list and a number of words, n, you want picked from it 
# and returns n randomly selected words as a list    
def get_choices(word, val, currDocPOSlib, pre):
   
    val = [val]
    
    # The following switches the POS according to our judgement when there aren't
    # enough options in some of the lesser populated POS. They're not perfect
    # and other users might see fit to change them.
    
    if val[0] == 'TO':  # to prevent 'to' from being the only answer.
        val.append('IN')
    
    if val[0] == 'EX':  # to prevent 'there' from being the only good answer.
        val.append('VBD')
        
    if val[0] == 'FW':  # to prevent from having only bad answers.
        val.append('IN')
        
    if val[0] == 'WP$':  # to prevent from having only bad answers.
        val.append('WP')
        
    if val[0] == 'WDT':  # to prevent from having only bad answers.
        val.append('WP')
        
    if val[0] == 'WP':  # to prevent from having only bad answers.
        val.append('WDT')
        
    if val[0] == 'PDT':  # to prevent from having only bad answers.
        val.append('IN')
        
    if val[0] == 'POS':  # to prevent from having only bad answers.
        val.append('IN')
        
    if val[0] == 'LS':  # to prevent from having only bad answers.
        val.append('IN')
        
    if val[0] == '$': # weird part of speech
        val.append('IN')
        
    choicesCurr = []
    choicesDict = []
    backupsCurr = [] 
    backupsDict = [] 
    temp = 0
    currDict = []
    distractorDict = []
    
    for pos in currDocPOSlib: # to avoid reference issues
        if '' in pos[1]: # if there are empty options remove them
            pos[1].remove('')
        if pos[0] in val: # same pos found in list
            currDict.append(copy.copy(pos[1]))

    if cyberDict: # if cyberDict is true use that for distractors
        for pos in cyberTermsPOSlib: # if there are empty options remove them
            if '' in pos[1]:
                pos[1].remove('')
            if pos[0] in val:
                distractorDict.append(copy.copy(pos[1]))
    else: # else use the normalDict for distractors
        for pos in normalPOSlib: # if there are empty options remove them
            if '' in pos[1]:
                pos[1].remove('')
            if pos[0] in val:
                distractorDict.append(copy.copy(pos[1]))
    
    if len(currDict) > 1:
        currDict = currDict[0] + currDict[1]
    elif len(currDict) == 0:
        currDict = []
    else:
        currDict = currDict[0]
            
    if len(distractorDict) > 1:
        distractorDict = distractorDict[0] + distractorDict[1]
    elif len(distractorDict) == 0:
        distractorDict = []
    else:
        distractorDict = distractorDict[0]

    # remove the answer from the list of choices
    if word in currDict:
        currDict.remove(word)
    if word in distractorDict:
        distractorDict.remove(word)
        
    # First randomly select n words (to eliminate going back to the
    # bigram corpus) from the current security document
    while (len(currDict) > 0  or len(distractorDict) > 0) and temp < 40:
        # get 40 potentials from this doc- ideally half from currDict half from distractorDict
        if len(currDict) > 0:
            choice = random.choice(currDict)
            if choice not in choicesCurr and choice not in choicesDict:
                choicesCurr.append(choice) # append choice to potentials list
                if choice in distractorDict:
                    distractorDict.remove(choice)
                temp += 1
            currDict.remove(choice)
        if len(distractorDict) > 0:
            choice = random.choice(distractorDict)
            if choice not in choicesCurr and choice not in choicesDict:
                choicesDict.append(choice) # append choice, set orig. prob to 0.
                if choice in currDict:
                    currDict.remove(choice)
                temp += 1
            distractorDict.remove(choice)
        if len(distractorDict) < 1 and len(currDict) < 1:
            temp += 1
    
    currDictProbs = []
    distractorDictProbs = []
    solution = []
    wordProb = 0
    
    # get the probabilities of each bigram from google ngrams corpus
    output = bg.testOption(pre, [word] + choicesCurr + choicesDict)
    
    # re sort words to their respective dictionaries
    for item in output:
        if item[0] in choicesCurr:
            currDictProbs.append(item)
            choicesCurr.remove(item[0])
        elif item[0] in choicesDict:
            distractorDictProbs.append(item)
            choicesDict.remove(item[0])
        elif item[0] == word:
            solution.append(item)
            wordProb = item[1]
    
    # add zero probs for words that weren't found
    for curr in choicesCurr:
        if curr not in currDictProbs: # doesn't do anything
            currDictProbs.append((curr,0))
    for curr in choicesDict:
        if curr not in distractorDictProbs:
            distractorDictProbs.append((curr,0))
    
    shuffle(currDictProbs)
    shuffle(distractorDictProbs)
    choices = []
    
    while len(choices) < 2 and len(currDictProbs) > 0:
        potential = currDictProbs.pop(0)
        if potential[1] != 0 and wordProb/potential[1] > 50:
            choices.append(potential[0])
            stats[3] += 1
        else:
            backupsCurr.append(potential)
            stats[1] += 1
    
    # get remaining possibilities into backups
    for poss in currDictProbs:
        backupsCurr.append(poss)
    
    # sort by prob
    backupsCurr = sorted(backupsCurr, key=lambda backupsCurr: backupsCurr[1], reverse = True) 
    
    # make sure choices are populated if there were any
    if len(choices) < 2 and len(backupsCurr) > 0:
        while len(choices) < 2 and len(backupsCurr) > 0:
            choices.append(backupsCurr.pop(0)[0])
            
    # now add the distractor dictionary options to choices
    while len(choices) < 4 and len(distractorDictProbs) > 0:
        potential = distractorDictProbs.pop(0)
        if potential[1] != 0 and wordProb/potential[1] > 50:
            choices.append(potential[0])
            stats[3] += 1
        else:
            backupsDict.append(potential)
            stats[1] += 1
            
    # get remaining possibilities into backups
    for poss in distractorDictProbs:
        backupsDict.append(poss)
        
    backupsDict = sorted(backupsDict, key=lambda backupsDict: backupsDict[1], reverse = True) 
    
    # make sure all choices are populated
    while len(choices) < 4 and (len(backupsCurr) > 0 or len(backupsDict) > 0):
        if len(choices) < 4 and len(backupsDict) > 0:
            choices.append(backupsDict.pop(0)[0])
        if len(choices) < 4 and len(backupsCurr) > 0:
            choices.append(backupsCurr.pop(0)[0])
    
    # if len(choices) < 4:
    #     print ('Not enough answer selections to provide choices for.')
        
    choices.append(word)

    for ch in choices:
        if (ch == 'i'): # just because lowercase I looks weird
            ch = 'I'
            
    # randomize choices
    order = []
    m = len(choices)
    while (m > 0):
        current = random.choice(choices)
        order.append(current)
        choices.remove(current)
        m -= 1
    
    return order

    
# # this runs process_doc with normal distractors being generated instead of cyber ones.
# def process_document_c(document):
#     global cyberDict
#     cyberDict = None # set for normal dictionary
#     dat = process_document(document)
#     return dat
    
# this function was used for analysis of the method
def process_document_analysis(document):
    global stats
    stats[0] += 1 #numFilesProcessed += 1
    stats[1] = 0  #numTimesDistractorRejectedCurr = 0
    stats[3] = 0  #numTimesDistractorAcceptedCurr = 0
    
    dat = process_document(document)
    
    # print out all the analysis stats
    print ('Num files: ', stats[0])
    
    stats[2] += stats[1] # add total rejects
    stats[4] += stats[3] # add total acceptancces
    stats[5] += stats[1] + stats[3] # keep count of total words
    
    print ('Rejects: ', str(stats[1]))
    print ('Accepts: ', str(stats[3]))
    
    # only print out at end
    if (stats[0] == 35):
        rejectionRate = stats[2]/stats[5]
        acceptanceRate = stats[4]/stats[5]
        print ('rejection rate: ', str(rejectionRate))
        print ('acceptance rate: ', str(acceptanceRate))
        
    return dat
    