import json
from pymongo import MongoClient
import math
import pandas as pd
from bson import ObjectId

DB_URI = 'mongodb://dhruv:elissa@cloze.cs.umd.edu:27017/admin'
DB_NAME = 'interactive_cloze'

mongo_cursor = MongoClient(DB_URI, connect = False)
db = mongo_cursor[DB_NAME]

CSV_FILE = "wiki_story_survey"

COLLECTION_NAME = "survey"

def get_survey_key():
    survey_key = None
    with open('survey_key2.json') as f:
        survey_key = json.load(f)
    
    if survey_key:
        return survey_key

    return False

def populate_db():
    print ("populating db with " + CSV_FILE + ".csv")
    db[COLLECTION_NAME].remove({})
    df = pd.read_csv( CSV_FILE + ".csv")
    for i,row in df.iterrows():
        doc = dict()
        for column in df.columns:
            if (not (type(row[column]) is str)):
                if (not math.isnan(row[column])):
                    doc[column] = row[column]
            else:
                doc[column] = row[column]
        db[COLLECTION_NAME].update({'ResponseId':doc['ResponseId']}, doc, upsert = True)
        print ('[' + CSV_FILE + '][' + str(i) + "] inserted into db...")
    print ("COMPLETE: populated db with " + CSV_FILE + ".csv")

def clean_and_process():
    print ("cleaning and processing db...")
    survey_key = get_survey_key()
    
    if survey_key:
        cnt = 0
        total = db[COLLECTION_NAME].find().count()
        for doc in db[COLLECTION_NAME].find(no_cursor_timeout=True):
            for key in doc.keys():
                if key[0] == 'Q':
                    question_label = key[1:]
                    #iterate categories
                    for i in range(len(survey_key)):
                        category_label = survey_key[i]['category_label']
                        #iterate docs
                        for j in range(len(survey_key[i]['docnames'])):
                            docname = survey_key[i]['docnames'][j]['docname']
                            timing_qno = survey_key[i]['docnames'][j]['timing_qno']

                            if '_' in question_label:
                                if timing_qno == question_label.split('_')[0]:
                                    db[COLLECTION_NAME].update({'_id':doc['_id']}, {'$set':{category_label + '_docname': docname}}, upsert=True)
                                    db[COLLECTION_NAME].update({'_id':doc['_id']}, {'$set':{category_label + '_' + question_label.split('_')[1]: doc[key]}}, upsert=True)
                                    break
                                
                            else:
                                #iterate questions
                                # print (survey_key[i]['docnames'][j])
                                for k in range(len(survey_key[i]['docnames'][j]['questions'])):
                                    qno = survey_key[i]['docnames'][j]['questions'][k]['qno']
                                    answer = survey_key[i]['docnames'][j]['questions'][k]['answer']

                                    if qno == question_label:
                                        if doc[key] == answer:
                                            db[COLLECTION_NAME].update({'_id':doc['_id']}, {'$set':{category_label + '_docname': docname}}, upsert=True)
                                            db[COLLECTION_NAME].update({'_id':doc['_id']}, {'$set':{category_label + '_Q' + str(k+1): True}}, upsert=True)
                                        else:
                                            db[COLLECTION_NAME].update({'_id':doc['_id']}, {'$set':{category_label + '_docname': docname}}, upsert=True)
                                            db[COLLECTION_NAME].update({'_id':doc['_id']}, {'$set':{category_label + '_Q' + str(k+1): False}}, upsert=True)

            cnt += 1
            print (str(cnt) + '/' + str(total))
    print ("COMPLETE: db processed...")

def create_csv():
    print ("creating csv...")
    survey_key = get_survey_key()

    attrs = ['MID']
    
    for i in range(len(survey_key)):
        category_label = survey_key[i]['category_label']
        attrs.append(category_label + '_Q1')
        attrs.append(category_label + '_Q2')
        attrs.append(category_label + '_Q3')
        attrs.append(category_label + '_First Click')
        attrs.append(category_label + '_Last Click')
        attrs.append(category_label + '_Page Submit')
        attrs.append(category_label + '_Click Count')
        attrs.append(category_label + '_docname')

    
    file_name = "survey_results.csv"

    results = dict()
    for attr in attrs:
        results[attr] = list()

    for doc in db[COLLECTION_NAME].find({'MID':{'$exists':True}},no_cursor_timeout=True):
        if (doc['StartDate'] == 'Start Date') or (doc['StartDate'] == '{"ImportId":"startDate","timeZone":"America/New_York"}'):
            continue
        for attr in attrs:
            if attr in doc:
                results[attr].append(doc[attr])
            else:
                results[attr].append(None)

    # for attr in attrs:
    #     print (attr + ' ' +str(len(results[attr])))
    # print (results)
    df = pd.DataFrame(data=results)
    df.to_csv(file_name)
    print (file_name + " saved.")

populate_db()
clean_and_process()
create_csv()