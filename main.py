from datetime import MAXYEAR
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.sql import func
from flask import session

import hashlib
import os
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'

def send_data():
        upload_file = "answers/" + str(session['subject_id'])+".txt"

        file = open(upload_file, "w")

        file.write('\n'.join(session['answers'])) 
        file.close()

@app.route('/begin')
def index():
    return render_template('index.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/new_subject', methods=['GET', 'POST'])
def new_subject():

    if request.method == 'POST':
        email = request.form["email"]
        hash = hashlib.md5(email.encode('utf-8')).digest()
        hash_str = str(int.from_bytes(hash,"big"))
        print(hash_str,"hash str")

        session['subject_id'] = hash_str
        session['question_counter'] = 0
        session['answers'] = []
	
        return redirect(url_for('interview'))

    return render_template('new_subject.html')

@app.route('/interview', methods=['GET', 'POST'])
def interview():

    def get_question_list():

        question_root = "static/videos/"
        question_names = os.listdir(question_root)
        question_folders = []
        
        for name in question_names:
            question_folders.append(question_root + name)
			
        question_list = []
                
        for folder in question_folders:
            video_names = os.listdir(folder)
            video_paths = []
            for name in video_names:
            	video_paths.append(folder+"/"+name)
            question_list.append(video_paths)
		
        print("INIT QUESTION LIST DEBUG:",question_list)
        
        return question_list
        
    def get_video_paths():  
    
        questions = get_question_list()
        video_paths = questions[session['question_counter']-1]
        random.shuffle(video_paths)
        session['question_counter'] = session['question_counter'] + 1
        return video_paths

    def get_question_amount():
        return len(get_question_list())
		
    if request.method == 'POST':
        print("CHOICES",request.form["choice"])
        post = request.form["choice"]
        chosen = post.split(',')[0][1:]
        options = post.replace(chosen,"")[3:-1]

        global answers
        answer = "chosen index " + str(chosen) + " of " + str(options) 
        session['answers'].append(answer)

        if session['question_counter'] >= get_question_amount():
            send_data()
            return redirect(url_for('thank_you'))
    
    return render_template('interview.html', video=get_video_paths(), question_counter=str(session['question_counter']), max_questions=str(get_question_amount()))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8875, debug=False, threaded=True)


