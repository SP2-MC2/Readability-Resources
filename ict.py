"""
Created March 2018
@author: dhruvk

This script runs the Interactive Cloze Tester (ICT) web interface.

Input: Accepts no input.                     
Output: Provides no ouput. Launches the web interface of the application.

"""

#import libraries
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from nltk import word_tokenize
from bson import ObjectId
import os, time, random, string

#user-defined libraries
import preprocess_data, constants

#connect to mongoDB
mongo_cursor = MongoClient(constants.DB_URI, connect = False)
interactive_clozeDB = mongo_cursor[constants.DB_NAME]

#method used to print with timestamp
def cout(string_to_print):
    print ("[" + time.ctime() + "] " + string_to_print)

#method used to check if all documents have been processed to the database. Runs only once when the interface is started.
def initialize():
    cout("Initializing...")

    cout("Checking if all files in the documents folder have been processed...")
    
    dir = constants.DOCUMENTS_DIR
    os.chdir(dir)

    #explore categories of documents in constants.DOCUMENTS_DIR
    for category in next(os.walk('.'))[1]:

        #explore category folder if category is in constants.CATEGORIES
        if category not in constants.CATEGORIES:
            continue
        os.chdir(category)

        for file_name in next(os.walk('.'))[2]:
            #name category's documents collection in db
            category_docs_db = category + '_' + 'docs'

            if not interactive_clozeDB[category_docs_db].find_one({'file_name':file_name}):
                cout("Processing the new file found - " + file_name + " ...")
                file_path = constants.DOCUMENTS_DIR + '/' + category + '/' + file_name

                #call methods from preprocess_data to process data
                processed_document = None
                processed_document = preprocess_data.process_document(open(file_path, 'r').read())
                 
                #update record in db
                if processed_document:
                    processed_document['file_name'] = file_name
                    interactive_clozeDB[category_docs_db].update({'file_name':file_name}, processed_document, upsert=True)
                    cout(file_name +  " processed...")
                else:
                    cout("ERROR - couldn't process " + file_name + "...!")    
        os.chdir('..')
    os.chdir('..')
               
    cout("All files in the documents folder have been processed.")

#method used to fetch next document from the database
def getDocumentFromDB(mturk_id, cloze_variant):

    q_no = 1
    for doc in interactive_clozeDB['mturk_users'].find_one({'mturk_id':mturk_id})['selected_docs']:
        
        #skip questions for which responses have already been received in previous sessions
        if interactive_clozeDB['responses'].find_one({'cloze_variant':cloze_variant, 'mturk_id':mturk_id, 'question_id':doc['_id']}):
            q_no += 1
            continue

        #contains all information about the document
        doc_info = dict()

        #insert blanks into the article by breaking it into article segments
        doc_info['article_segments'] = list()
        article_words = word_tokenize(doc['article'])
        prev_blank = 0
        blank_i = 0
        
        for blank_index in doc['blanks']:
            sentence = ' '.join(article_words[prev_blank:blank_index])

            #handle new line in text
            sentence = sentence.replace('\n','<br>')
            
            #handle punctuation cases in text
            for punctuation in constants.PUNCTUATIONS:
                sentence = sentence.replace(' ' + punctuation, punctuation)
            sentence = sentence.replace(" n't", "n't")
            
            #in cases of modified cloze, include distractors into doc_info
            if (cloze_variant == 'modified_cloze' or cloze_variant == 'modified_cloze2'):
                choices = doc['choices'][blank_i]
                
                #add last choice of don't know
                choices.append('I do not know the answer')

                doc_info['article_segments'].append({'sentence':sentence, 'choices':choices, 'blank_id':str(doc['_id']) + "_" + str(blank_i)})
            else:
                doc_info['article_segments'].append({'sentence':sentence, 'blank_id':str(doc['_id']) + "_" + str(blank_i)})
            blank_i += 1
            prev_blank = blank_index + 1

        #handle last sentence
        sentence = ' '.join(article_words[prev_blank:]).replace('\n','<br>')
        for punctuation in constants.PUNCTUATIONS:
            sentence = sentence.replace(' ' + punctuation, punctuation)
        
        doc_info['article_segments'].append({'sentence':sentence})
        return q_no, doc_info
    return False, False

#method returns the documents to be processed on priority (ones having less than five attempts)
def get_priority_docs(cloze_variant):

    #flag_label marks documents which have atleast 5 attempts
    flag_label = cloze_variant + '_five_done_flag'
    priority_docs = dict()

    for category in constants.CATEGORIES:
        priority_docs[category] = list()

        category_docs_db = category + '_' + 'docs'

        #check for five_done_flag
        for doc in interactive_clozeDB[category_docs_db].find(no_cursor_timeout=True):
            if (flag_label in doc) and (doc[flag_label]):
                continue
            if (interactive_clozeDB['responses'].find({'cloze_variant':cloze_variant, 'question_id':doc['_id']}).count()/constants.TOTAL_BLANKS) >= 5:
                interactive_clozeDB[category_docs_db].update({'_id':doc['_id']}, {'$set':{flag_label:True}}, upsert=True)
            else:
                priority_docs[category].append(doc['_id']) 
    return priority_docs

#method called when a user logs into the interface for the first time - selects documents for the user to attempt and creates an entry in mturk_users
def create_mturk_user(mturk_id, cloze_variant):

    #return False if the user is already present in the database associated with a different cloze variant
    if interactive_clozeDB['mturk_users'].find_one({'cloze_variant':{'$ne':cloze_variant}, 'mturk_id':mturk_id}):
        return False

    #return True if the user is already present in database associated with the same cloze variant
    if interactive_clozeDB['mturk_users'].find_one({'cloze_variant':cloze_variant, 'mturk_id':mturk_id}):
        return True
    
    #selects documents based on priority and categories
    i_pass_categories = 0
    random_docs = list()
    priority_docs_ids = get_priority_docs(cloze_variant)
    while(len(random_docs) < constants.N_DOCS_TO_DISPLAY) and (i_pass_categories < len(constants.CATEGORIES)):
        for category in constants.CATEGORIES:
            try:
                random_doc_id = random.choice(priority_docs_ids[category])
            except:
                print (category + " finished.")
                continue
            while((category,random_doc_id) in random_docs):
                priority_docs_ids[category].remove(random_doc_id)
                try:
                    random_doc_id = random.choice(priority_docs_ids[category])
                except:
                    print (category + " finished.")
                    break
            random_docs.append((category, random_doc_id))
        i_pass_categories += 1
    
    #saves selected documents to database
    selected_docs = list()
    for category, random_doc_id in random_docs:
        category_docs_db = category + '_' + 'docs'
        selected_docs.append(interactive_clozeDB[category_docs_db].find_one({'_id':random_doc_id}))
    interactive_clozeDB['mturk_users'].update({'cloze_variant':cloze_variant, 'mturk_id':mturk_id}, {'$set':{'selected_docs':list(selected_docs)}}, upsert=True)

#method returns a success code once the cloze test is complete
def get_success_code(mturk_id, cloze_variant):
    mturk_user_doc = interactive_clozeDB['mturk_users'].find_one({'cloze_variant':cloze_variant, 'mturk_id':mturk_id, 'success_code':{'$exists':True}})
    if mturk_user_doc:
        return mturk_user_doc['success_code']
    else:
        success_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=constants.SUCCESS_CODE_LEN))
        interactive_clozeDB['mturk_users'].update({'cloze_variant':cloze_variant, 'mturk_id':mturk_id}, {'$set':{'success_code':success_code}}, upsert=True)
        return success_code

#initializating web app
initialize()
application = Flask(__name__)

#index page is a sample page from modified cloze test
@application.route("/", methods=['GET', 'POST'])
def index():
    mturk_id = 'test_presentation'
    cloze_variant_code = 'a'
    cloze_variant = 'modified_cloze'
    q_no, doc = getDocumentFromDB(mturk_id, cloze_variant)
    return render_template('survey_index.html', mturk_id = mturk_id, doc = doc, cloze_variant_code = cloze_variant_code, q_no = q_no, total_q = constants.N_DOCS_TO_DISPLAY)


@application.route("/<cloze_variant_code>/<mturk_id>/", methods=['GET', 'POST'])
def cloze(cloze_variant_code, mturk_id):

    #check for cloze_variant_code in page params
    if cloze_variant_code == 'a':
        cloze_variant = 'modified_cloze'
    elif cloze_variant_code == 'b':
        cloze_variant = 'traditional_cloze'
    else:
        return render_template('survey_error.html', error = "404. Page Not Found.")

    #handle GET requests
    if request.method == 'GET':

        #check for mturk_id in page params
        if not mturk_id:
            return render_template('survey_error.html', error = "No MTurk ID specified")
        
        #check if user already in database associated with a different cloze test
        if not create_mturk_user(mturk_id, cloze_variant):
            return render_template('survey_error.html', error = "You previously entered a similar survey, so you are not eligible for this survey.")
        
        #get documents for cloze test
        q_no, doc = getDocumentFromDB(mturk_id, cloze_variant)
        if doc:
            return render_template('survey.html', mturk_id = mturk_id, doc = doc, cloze_variant_code = cloze_variant_code, q_no = q_no, total_q = constants.N_DOCS_TO_DISPLAY)
        
        #if no documents returned, create and display success code
        else:
            success_code = get_success_code(mturk_id, cloze_variant)
            return render_template('survey_success.html', success_code = success_code)

    #handle POST requests from the cloze test - save responses into the database
    if request.method == 'POST':
        mturk_id = None
        tab_focus_time = None
        responses = dict()
        for fieldname in request.form:
            if fieldname == 'mturk_id':
                mturk_id = request.form[fieldname]
            elif fieldname == "tab_focus_time":
                tab_focus_time = request.form[fieldname]
            else:
                responses[fieldname] = request.form[fieldname]
        for fieldname in responses:
            question_id, blank_i = fieldname.split('_')
            blank_answer = responses[fieldname]
            interactive_clozeDB['responses'].update({'cloze_variant':cloze_variant, 'mturk_id':mturk_id, 'question_id':ObjectId(question_id), 'blank_i':blank_i}, {'$set':{'blank_answer':blank_answer, 'tab_focus_time':tab_focus_time}}, upsert=True)
        return redirect(url_for('cloze', cloze_variant_code = cloze_variant_code, mturk_id = mturk_id))

if __name__ == "__main__":
    application.run(host = '0.0.0.0', threaded=True)
