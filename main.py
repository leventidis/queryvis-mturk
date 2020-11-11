from __future__ import division
import os
import boto3
import json
import datetime
from flask import Flask, render_template, url_for, request, make_response, jsonify, request, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
from post_hits import get_connection, qualification_id

#Start Configuration Variables
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
DEV_ENVIROMENT_BOOLEAN = False
DEBUG = True
LOCAL = False
#End Configuration Variables

#This allows us to specify whether we are pushing to the sandbox or live site.
if DEV_ENVIROMENT_BOOLEAN:
    AMAZON_HOST = "https://workersandbox.mturk.com/mturk/externalSubmit"
else:
    AMAZON_HOST = "https://www.mturk.com/mturk/externalSubmit"

app = Flask(__name__, static_url_path='')
app.secret_key="TODO:change-this-to-something-else"
app.config.from_object(os.environ['APP_SETTINGS'])

# Set up SQLAlchemy variables and settings
if (LOCAL):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'replace_with_database_url_on_local_computer'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'replace_with_database_url_on_heroku'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

# Configuration for returning workers
returning_workers_filename = 'data/worker_ids_taken_old_hit.csv'
returning_workers_sequence_num_amount = [0, 0, 0, 0, 0, 0]

# Creates the questions dictionary that includes the choices (a-d) for each of the 12 questions  
def create_questions_dict():
    questions = {}
    num_questions=12
    choices = ["a", "b", "c", "d"]

    # Loop through all questions
    for i in range(1,num_questions+1):
        question_key = "Q" + str(i)
        questions[question_key] = {}

        # Loop through all choices for each question
        for c in choices:
            question_str = ""
            # Read choices files
            with open('static/questions/' + str(i) + '/' + c + '.txt', 'r') as choice_file:
                question_str=choice_file.read().replace('\n', '')
            questions[question_key][c] = question_str

    return questions

# Creates the answers dictionary that includes the letter answer (a-d) for each of the 12 questions
def create_answers_dict():
    answers_json = open('static/questions/answers.json')
    answer_str = answers_json.read()
    answers = json.loads(answer_str)
    return answers

# Returns a sequence number for a given worker. The sequence number is assigned so that the sizes of the different sequence number groups are balanced
# It also tries to balance groups when assigning returning workers
def assign_sequence_num(worker_id):
    # Read the returning workers
    with open(returning_workers_filename) as f:
        returning_workers = f.readlines()
    returning_workers = [x.strip() for x in returning_workers]

    # check if current worker is a returning worker
    if worker_id in returning_workers:
        print(worker_id, "is a returning worker")
        lowest_sequence_num_amount = returning_workers_sequence_num_amount.index(min(returning_workers_sequence_num_amount))
    else:
        sequence_num_amount = []
        # sequence_num = "sequence_num"
        for i in range(6):
            amount = db.session.query(User.sequence_num).filter_by(sequence_num=i).count()
            sequence_num_amount.append(amount)
            print("There are " + str(amount) + " users with sequence_num = " + str(i))

        lowest_sequence_num_amount = sequence_num_amount.index(min(sequence_num_amount))
    
    print("The sequence_num with the lowest assigned workers is: " + str(lowest_sequence_num_amount))

    # Set sequence_num in the database
    user = db.session.query(User).filter_by(worker_id=worker_id).first()
    user.sequence_num = lowest_sequence_num_amount
    db.session.commit()

    return lowest_sequence_num_amount
    

#---------------------------------------------- ROUTES ----------------------------------------------#
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico')

@app.route('/', methods=['GET', 'POST'])
def main():
    preview = False

    # Check if the worker clicked on preview
    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        print("Worker has clicked to preview the task")
        preview = True
        resp = make_response(render_template("instructions.html", preview = preview))
        resp.headers['x-frame-options'] = '*'
        return resp

    worker_id = request.args.get("workerId")
    assignment_id = request.args.get("assignmentId")
    hit_id = request.args.get("hitId")
    print("worker_id:", worker_id, "assignment_id:", assignment_id, "hit_id:", hit_id)

    if (LOCAL):
        worker_id = "TEST"
        assignment_id = "TEST"
        hit_id = "TEST"

    # TODO: Check if user exists with the same worker_id in the database
    exists = db.session.query(User.worker_id).filter_by(worker_id=worker_id).scalar()

    if (exists):
        # TODO: Throw error, prevent the user from taking the study again
        print("Detected existing worker_id")
        pass
    else:
        # Add the new user into the database
        print("Creating new user")
        user = User(worker_id)
        db.session.add(user)
        db.session.commit()
    
    # Get the user and insert the amazon variables in the database
    user=db.session.query(User).filter_by(worker_id=worker_id).first()
    user.worker_id = worker_id
    user.assignment_id = assignment_id
    user.hit_id = hit_id

    # Record the datetime a new user is added
    start_datetime = datetime.datetime.utcnow()
    print("Recorded user's starting datetime as " + str(start_datetime))
    user.start_datetime = start_datetime

    # Grab the user's qualification score and place it in the database
    if (not LOCAL):
        conn = get_connection()
        response = conn.get_qualification_score(
            QualificationTypeId = qualification_id,
            WorkerId = worker_id
        )
        qualification_score = response['Qualification']['IntegerValue']
        user.qualification_score = qualification_score
        print("Worker: " + worker_id + " had a qualification score of " + str(qualification_score))

    db.session.commit()

    resp = make_response(render_template("instructions.html", preview = preview,
    worker_id = worker_id, assignment_id=assignment_id, hit_id=hit_id))
    
    #This is particularly nasty gotcha.
    #Without this header, your iFrame will not render in Amazon
    resp.headers['x-frame-options'] = '*'
    return resp

@app.route('/tutorial', methods=['GET','POST'])
def tutorial():
    resp = make_response(render_template("tutorial.html"))
    resp.headers['x-frame-options'] = '*'
    return resp

@app.route('/tutorial_record_time', methods=['GET','POST'])
def tutorialClick():
    print("Tutorial record time called")
    if request.method == 'POST':
        data = json.loads(request.form['data'])

        # Get the data
        tutorial_page_num = str(data['tutorial_page_num'])
        time_spent = data['time_spent']
        worker_id = data['worker_id']

        print("Worker: "+ worker_id + " moved away from tutorial page " + tutorial_page_num +
        ", elapsed time increased by " + str(time_spent))

        # Get the user
        user = db.session.query(User).filter_by(worker_id = worker_id).first()

        # Apply the changes to the database
        question_time = getattr(user, "tutorial_time")
        if (question_time == None):
            question_time = time_spent
        else:
            question_time += time_spent

        setattr(user, "tutorial_time", question_time)
        db.session.commit()

        print("Set tutorial_time to " + str(question_time))


    if request.method == 'GET':
        print("Wrong request, request should be POST not GET")

    return "OK"


@app.route('/test', methods=['GET','POST'])
def test():
    print("Test route called")

    # Create dictionary for the questions and answers data
    questions = create_questions_dict()
    resp = make_response(render_template("page.html", questions = questions))
    resp.headers['x-frame-options'] = '*'
    return resp

@app.route('/get_question_answer', methods=['POST'])
def get_question_answer():
    print("get_question_answer called with " + request.method + " request")
    if request.method == 'POST':
        question_num = request.json['question_num']
        print("Requesting answer for question_num", question_num)

        # Load the answers in a dictionary and extract the correct answer
        answers = json.loads(open("static/questions/answers.json").read())
        answer = answers[str(question_num)]
        print("Correct answer is choice:", answer)
        return answer

    if request.method == 'GET':
        print("Wrong request, request should be POST not GET")

    return "OK"

@app.route('/assign_sequence_num', methods=['GET','POST'])
def assign_sequence_num_route():
    '''
    Mode 1: Show SQL
    Mode 2: Show QV
    Mode 3: Show SQL + QV

    Sequence 0: 1, 2, 3, 1, 2, 3, ...
    Sequence 1: 1, 3, 2, 1, 3, 2, ...
    Sequence 2: 2, 1, 3, 2, 1, 3, ...
    Sequence 3: 2, 3, 1, 2, 3, 1, ...
    Sequence 4: 3, 1, 2, 3, 1, 2, ...
    Sequence 5: 3, 2, 1, 3, 2, 1, ...
    '''
    # TODO: use get_qualification_score (https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client.get_qualification_score)
    # if we want to set the mode based on user performance in the qualification test

    print("assign_sequence_num route called")
    worker_id = request.json['worker_id']
    print(worker_id)

    user = db.session.query(User).filter_by(worker_id=worker_id).first()
    sequence_num = user.sequence_num
    if (sequence_num == None):
        print("User doesn't have a sequence number assigned, assinging one to them now...")
        sequence_num = assign_sequence_num(worker_id)
        print("User assigned sequence number " + str(sequence_num))
    return str(sequence_num)

@app.route('/demographics', methods=['GET', 'POST'])
def demographics():
    print("Demographics route called")

    resp = make_response(render_template("demographics.html"))
    resp.headers['x-frame-options'] = '*'
    return resp

@app.route('/demographics_submit', methods=['POST'])
def demographics_submit():
    print("Demographics submit route called")
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        print(data)

        # Get the data
        likert_q1 = data['likert_q1']
        likert_q2 = data['likert_q2']
        likert_q3 = data['likert_q3']
        likert_q4 = data['likert_q4']
        likert_q5 = data['likert_q5']
        likert_q6 = data['likert_q6']

        feedback = data['feedback']
        country = data['country']
        gender = data['gender']
        age = custom_to_int(data['age'])
        occupation = data['occupation']
        income = custom_to_int(data['income'])
        sql_exp = data['sql_exp']
        frequency = custom_to_int(data['frequency'])
        usage = data['usage']

        # Get the user
        worker_id = data['worker_id']
        user=db.session.query(User).filter_by(worker_id=worker_id).first()

        # Apply the changes to the database
        user.feedback = feedback
        user.country = country
        user.gender = gender
        user.occupation = occupation
        user.sql_exp = sql_exp
        user.usage = usage

        # Make sure we don't insert empty strings for integer columns
        if (likert_q1 != ''):
            user.likert_q1 = likert_q1
        if (likert_q2 != ''):
            user.likert_q2 = likert_q2
        if (likert_q3 != ''):
            user.likert_q3 = likert_q3
        if (likert_q4 != ''):
            user.likert_q4 = likert_q4  
        if (likert_q5 != ''):
            user.likert_q5 = likert_q5
        if (likert_q6 != ''):
            user.likert_q6 = likert_q6

        if (age != ''):
            user.age = age
        if (income != ''):
            user.income = income
        if (frequency != ''):
            user.frequency = frequency

        db.session.commit()

    if request.method == 'GET':
        print("Wrong request, request should be POST not GET")

    return "OK"

# val is either an empty string or an integer string, custom_to_int converts the string to an integer if it wasn't empty
def custom_to_int(val):
    if (val==''):
        return val
    else:
        return int(val)

@app.route('/results', methods=['GET', 'POST'])
def results():
    # Calculate how many right or wrong, total time, average time
    worker_id = request.args.get('worker_id')
    print("worker_id: " + worker_id)

    # Load the answers in a dictionary
    answers = json.loads(open("static/questions/answers.json").read())

    min_num_correct_questions = 5
    min_allowed_accuracy = 0.5
    max_allowed_time = 50*60

    num_questions = 12
    num_correct = 0
    total_time = 0

    user = db.session.query(User).filter_by(worker_id=worker_id).first()

    # Record the datetime a new user is added
    end_datetime = datetime.datetime.utcnow()
    print("Recorded user's ending datetime as " + str(end_datetime))
    user.end_datetime = end_datetime
    db.session.commit()

    for i in range(1, num_questions + 1):
        q_col = "q" + str(i)
        q_time_col = "q" + str(i) + "_time"
        
        user_answer = getattr(user, q_col)
        user_time = getattr(user, q_time_col)

        if (user_answer == answers[str(i)]):
            num_correct += 1
            print("Correct answer for question " + str(i))

        total_time += user_time

    percentage_correct = num_correct / num_questions
    print("Number of correct answers is: " + str(num_correct))
    print("Percentage of correct answers is " + str(percentage_correct))
    print("Total time taken to complete the test is: " + str(total_time))

    accept = True
    failure_reason = ""

    # check if we will accept the hit
    if (num_correct < min_num_correct_questions):
        accept = False
        failure_reason = "you failed to answer 5 or more questions correctly."
    if (total_time > max_allowed_time*1000):
        accept = False
        failure_reason = "you failed to answer all questions within " + str(max_allowed_time/60) + " minutes."

    print("The hit acceptance is: " + str(accept))

    # TODO: Do not hard code variables
    # Calculate the bonus
    base_pay = 5.20
    bonus_time = 0
    bonus_correctness = 0
    total_bonus = 0
    correctness_per_question_bonus = 1.04

    # Calculate bonuses only if we accept the hit and submit the bonus
    if (accept):
        bonus_correctness = round(((num_correct - min_num_correct_questions) * correctness_per_question_bonus if (num_correct - min_num_correct_questions > 0) else 0), 2)
        
        if total_time < 14 * 60 * 1000:
            bonus_time = 0.32 * (base_pay + bonus_correctness)
        elif total_time < 15 * 60 * 1000:
            bonus_time = 0.28 * (base_pay + bonus_correctness)
        elif total_time < 16 * 60 * 1000:
            bonus_time = 0.24 * (base_pay + bonus_correctness)
        elif total_time < 17 * 60 * 1000:
            bonus_time = 0.20 * (base_pay + bonus_correctness)
        elif total_time < 18 * 60 * 1000:
            bonus_time = 0.16 * (base_pay + bonus_correctness)
        elif total_time < 18 * 60 * 1000:
            bonus_time = 0.12 * (base_pay + bonus_correctness)
        bonus_time = round(bonus_time, 2)

        print("Bonus from correctness: " + str(bonus_correctness) + " bonus from time: " + str(bonus_time))
        total_bonus = round(bonus_correctness + bonus_time, 2)

    total_pay = base_pay + total_bonus

    resp = make_response(render_template("results.html", AMAZON_HOST=AMAZON_HOST, percentage_correct=percentage_correct,
        num_correct=num_correct, total_time=int(round(total_time/1000)), accept=accept,
        failure_reason=failure_reason, bonus_time=str("{:.2f}".format(bonus_time)),
        bonus_correctness=str("{:.2f}".format(bonus_correctness)), total_bonus=str("{:.2f}".format(total_bonus)),
        total_pay=str("{:.2f}".format(total_pay)))
    )
    resp.headers['x-frame-options'] = '*'
    return resp


# Modifies the database in order to record a user's question choice and time spent on that question
@app.route('/record_question_and_time', methods=['POST'])
def record_question_and_time():
    print("record_question_and_time was called as a " + request.method + " request")
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        print(data)
        question = "q" + str(data['question_num'])
        question_time_col = question + "_time"
        user_choice = data['user_choice']
        question_time_val = str(data['time_spent'])

        worker_id = data['worker_id']   

        # Insert the user answer
        SQL_question = "UPDATE users SET " + question + "='" + user_choice + "' WHERE worker_id='" + worker_id + "';"
        print("Executing SQL", SQL_question)
        result = db.engine.execute(SQL_question)

        # Insert the time spent on the question
        SQL_question_time = "UPDATE users SET " + question_time_col  +"=" + question_time_val + " WHERE worker_id='" + worker_id + "';"
        print("Executing SQL", SQL_question_time)
        result = db.engine.execute(SQL_question_time)

    if request.method == 'GET':
        print("Wrong request, request should be POST not GET")

    return "OK"

if __name__ == "__main__":
    # app.debug = DEBUG
    app.run(threaded=True)