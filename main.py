from datetime import MAXYEAR
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.sql import func

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import hashlib
import os
import string
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'

subject_id = 1
max_questions = 3
question_counter = 0
answers = []

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def send_data():
	gauth = GoogleAuth()
	gauth.LoadCredentialsFile("mycreds.txt")

	drive = GoogleDrive(gauth)
	#gauth.LocalWebserverAuth()
	#gauth.SaveCredentialsFile("mycreds.txt")

	fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	for file in fileList:
		if(file['title'] == "survey-database"):
			fileID = file['id']
			print("fileID : ", fileID)
		
	global subject_id
	upload_file = subject_id+".txt"

	file = open(upload_file, "w")
	global answers 
	
	file.write('\n'.join(answers)) 
	file.close() 

	gfile = drive.CreateFile({'parents': [{'id':fileID}]})
	gfile.SetContentFile(upload_file)
	gfile.Upload() 
	
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
        
        global subject_id,max_questions,question_counter
        subject_id = hash_str
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
            send_data()
            return redirect(url_for('thank_you'))
            
        global answers
        answer = "chosen index " + str(chosen) + " of " + str(options) 
        answers.append(answer)

    return render_template('interview.html', video=get_video_paths(), question_counter=str(question_counter), max_questions=str(max_questions))
    
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8075, debug=True)
# [END gae_flex_quickstart]
