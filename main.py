from datetime import MAXYEAR
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import random
import hashlib
import os

db = SQLAlchemy()
DB_NAME = "database.db"

app = Flask(__name__)

app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

db.init_app(app)
subject_id = 1
max_questions = 3
question_counter = 0

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    chosen = db.Column(db.String(255))
    options = db.Column(db.String(255))

class Subject(db.Model):
    id = db.Column(db.String(255), primary_key=True)

db.create_all(app=app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

@app.route('/new-subject', methods=['GET', 'POST'])
def new_subject():

    if request.method == 'POST':
        email = request.form["email"]
        hash = hashlib.md5(email.encode('utf-8')).digest()
        hash_str = str(int.from_bytes(hash,"big"))
        print(hash_str,"hash str")
        subject = Subject(id = hash_str)
        db.session.add(subject) #############
        db.session.commit()
        
        global subject_id,max_questions,question_counter
        subject_id = 1
        max_questions = 3
        question_counter = 0

        return redirect(url_for('interview'))
        
    return render_template('new-subject.html')

@app.route('/interview', methods=['GET', 'POST'])
def interview():

    global question_counter, max_questions

    def get_video_paths():
        ours_path = "static/videos/ours/"
        baseline_path = "static/videos/baseline/"
        
        ours = os.listdir(ours_path)
        baseline = os.listdir(baseline_path)

        print("ours",ours)#random.shuffle(videos)
        print("baseline",baseline)#random.shuffle(videos)
        print("ours_path",ours_path)#random.shuffle(videos)
        print("baseline_path",baseline_path)#random.shuffle(videos)

        for i in range(len(baseline)):
            baseline[i] = baseline_path + baseline[i]
        for i in range(len(ours)):
            ours[i] = ours_path + ours[i]
        
        baseline_1, baseline_2 = random.sample(baseline,2)
        videos = [random.choice(ours),baseline_1,baseline_2]
        
        global question_counter, max_questions, subject_id
        question_counter = question_counter + 1
        
        return videos

    if request.method == 'POST':
        print("CHOICES",request.form["choice"])
        post = request.form["choice"]
        chosen = post.split(',')[0][1:]
        options = post.replace(chosen,"")[3:-1]

        print("CHOSen",chosen)
        print("Options",options)
        if question_counter >= max_questions:
            return redirect(url_for('thank_you'))
        answer = Answer(subject_id = subject_id, chosen = chosen, options = options) 
        db.session.add(answer) #############
        db.session.commit()
        #         
    return render_template('interview.html', video=get_video_paths(), question_counter=str(question_counter), max_questions=str(max_questions))
    
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]
