# This Repository: 300 human-written document comprehension questions and tools for generating Cloze tests
This repository contains: 
- 300 human-written, expert validated comprehension questions for 100 documents (25 security advice documents, 25 health advice documents, 25 Wikipedia articles, and 25 stories from the MCTest dataset). You can use these questions as a baseline to compare with other measures of text readability you might apply to our sample documents (in the documents folder). 
- Code that can be used to generate both Smart and Traditional Cloze tests (see more detail below). 

These resources were used to evaluate the validity of different measures of adult readability for online (and domain-specific) texts. You can learn more by reading the paper ["Comparing and Developing Tools to Measure the Readability of Domain-Specific Texts" published in EMNLP 2019] (http://www.cs.umd.edu/~eredmiles/emnlp2019).

## Generating Cloze Tests

Smart Cloze is a tool for creating multiple choice Cloze tests with intelligently selected distractors (answer choice options).

The Cloze test is a method for assessing text difficulty or reading level and/or for assessing the reading skill of the test taker. Traditionally, the Cloze test involves filling in every nth blank of a text. In the Interactive Cloze Tester tool, these blanks are multiple choice options with 5 choices (4 distractors + the correct answer). 

We created this tool to identify where the blanks are and what the choices should be. You can clone the tool and update with your own corpus in order to generate Cloze tests with distractors drawn from your corpus. See below for more detail on installation instructions and distractor generation.

You can use the code provided here to create both Smart Cloze and traditional (no distractors) Cloze tests.


### Requirements

* [Python 3.6](https://www.python.org/downloads/)
* [VirtualEnv](https://virtualenv.pypa.io/en/stable/installation/)
* [MongoDB 3.2.20](https://docs.mongodb.com/manual/installation/)
* [nltk](https://www.nltk.org/install.html)- Text processing
* [spaCy](https://spacy.io/usage/) - Part of speech tagging

### Installation

We used python 3.6 for development, no testing was done with python 2.
Fresh boot on a linux os with python3 and pip3:

```
virtualenv env3 --python=python3
```
```
source env3/bin/activate
```

```
pip install -r requirements.txt
```
```
nltk.download('punkt')
```
```
nltk.download('averaged_perceptron_tagger')
```
```
python -m spacy download en
```
See spaCy's documentation for any issues: https://spacy.io/

Now that your virtual environment is set up, it's time to get to the actual program. As we said earlier this tool will choose every 5th word and generate multiple choice options for it. In order to find these 'distractor' words you need a dictionary to find them by. You can pick a generic dictionary (from here on I'll refer to this as a 'normal dictionary'), or one that is specific to a certain field, such as cybersecurity (we'll call ours the 'cyber dictionary').

## Distractor Selection Process
In order to choose distractors for your multiple choice, we used the dictionary to choose words of the same part of speech. A certain n words are taken from that pos in cyber or normal dictionary. Then, we used bigram language modeling to make sure our distractors had a reasonable chance of occurring in the sentence. i.e., the sentence makes sense (the analyst 'danced' his results, doesn't make sense if the word is 'analyzed'). Our function: bigram.testOption() will calculate the probability of the bigram 'analyst danced' occurring. To calculate these probabilities we used Google's ngram corpus, which is not publicly available. You can substite your own bigram corpus in bigram.py, OR, not use the bigrams at all. If you choose not to use the bigrams it will look for the folder and an exception will be caught. You shouldn't need to provide any extra code, it will just not use probabilities to eliminate possible distractors. Once the probabilities are calculated by the distractors we eliminated them if they were 2 orders or more away from the probability of the correct answer occurring. We made this choice by reasoning that one order away is reasonable, but 2 is fairly unlikely to occur (100x less likely to be the word).

**Note: Our implementation of using bigrams to eliminate poor choices is a proof of concept. You can tune the selection of viable bigrams for your program. Not using the bigram language modeling will not affect the success of the program. The program will still generate distractors, the bigram modeling is supposed to make those potential answers more realistic.

### Dictionary generation:
We've included the 'cyber' and 'normal' dictionaries that we used. The normal dictionary is created using spacy pos (part-of-speech) tagging (it will use wordnet if you set spacyFlag = None) on the Brown word corpus to create normalDictionary.txt. The cyber dictionary also uses spacy pos tagging, but the distractor (cyber) dictionary is generated from the folder ict/dictionaryTexts. You can set this folder location in createCyberDictionary.py.

**Note: If you decide to re-generate your own dictionaries, this will take a few hours depending on your computer speed.

### Instructions for execution:

The code begins processing in ict.py. Please define some constants required in constants.py before executing.

## Authors

[Dhruv Kuchhal](https://github.com/dhruvkuchhal), [Lisa Maszkiewicz](https://github.com/lmasz), [Elissa Redmiles](http://cs.umd.edu/~eredmiles).

## Cite
If you use this tool in an academic setting, please cite Comparing and Developing Tools to Measure the Readability of Domain-Specific Texts. Redmiles, E.M., Maszkiewicz, L., Hwang, E., Kuchhal, D., Liu, E., Morales, M., Peskov, D., Rao, S., Stevens, R., Gligoric, K., Kross, S., Mazurek, M.L. and Daume III, H. In Proceedings of EMNLP 2019. Available at: [http://www.cs.umd.edu/~eredmiles/emnlp2019](http://www.cs.umd.edu/~eredmiles/emnlp2019).

## Contact Information
This work is part of an ongoing research project at the University of Maryland. Please contact Elissa Redmiles (eredmiles@cs.umd.edu) or Michelle Mazurek (mmazurek@cs.umd.edu) with questions / concerns.

## Acknowledgements
This material is based upon work supported by a UMIACS contract under the partnership between the University of Maryland and DoD. Elissa M. Redmiles additionally wishes to acknowledge support from the National Science Foundation Graduate Research Fellowship Program under Grant No. DGE 1322106 and a Facebook Fellowship. 
