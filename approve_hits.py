import sys
import boto3
import psycopg2
import json
import time
import datetime
import logging
import pandas as pd
from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Heroku Database URL
DATABASE_URL = "replace_with_database_url_on_heroku"

AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
DEV_ENVIROMENT_BOOLEAN = False

def get_connection():
    if DEV_ENVIROMENT_BOOLEAN:
        return  boto3.client('mturk',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name = 'us-east-1',
            endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com'
        )
    else:
        return  boto3.client('mturk',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name = 'us-east-1',
            endpoint_url='https://mturk-requester.us-east-1.amazonaws.com'
        )

# Set up the AMT connection
connection = get_connection()

# The answers to the questions
answers = json.loads(open("static/questions/answers.json").read())

# Database setup
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

# Setup logging
log_filename = "logs/approve_hits_full_study_january_2020.log"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m-%d-%y %H:%M:%S',
                    filename=log_filename,
                    filemode='a')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Returns the list of assignments with certain status for a given HITId
def get_assignment_hits(connection, hit_id, status):
    return connection.list_assignments_for_hit(
        HITId = hit_id,
        MaxResults=100,
        AssignmentStatuses=[status]
    )

# Returns the score and time (in milliseconds) given a worker_id
def get_score_and_time(worker_id):
    user = session.query(User).filter_by(worker_id=worker_id).first()
    num_questions = 12
    num_correct = 0
    total_time = 0
    for i in range(1, num_questions + 1):
        q_col = "q" + str(i)
        q_time_col = "q" + str(i) + "_time"
        
        user_answer = getattr(user, q_col)
        user_time = getattr(user, q_time_col)

        if (user_answer == answers[str(i)]):
            num_correct += 1
            logging.info("Correct answer for question " + str(i))

        total_time += user_time
    return num_correct, total_time


def approve_hits(connection, assignment_id_list, worker_id_list, check_completion_times = True):
    '''
    If check_completion_times is set to true only print out the times and do not accept or reject any time
    '''
    min_allowed_correct = 5
    max_allowed_time = 50*60 #In seconds

    for i in range(len(assignment_id_list)):
        accept = True
        time.sleep(2)

        assignment_id = assignment_id_list[i]
        worker_id = worker_id_list[i]

        logging.info("Worker " + str(i+1) + "/" + str(len(assignment_id_list))) 
        logging.info("--------------------- Evaluating " + assignment_id + " of worker " + worker_id + " ---------------------")

        num_correct, total_time = get_score_and_time(worker_id)
        logging.info("Assignment " + assignment_id + " had " + str(num_correct)
        + " correct and was completed in " + str(total_time/1000) + " seconds")

        if check_completion_times == False:
            # Check if the user failed
            failure_reason = ""
            if (num_correct < min_allowed_correct):
                accept = False
                failure_reason = "low correctness"
                logging.info("User failed the assignment with ID: " + assignment_id + " due to " + failure_reason)
            if (total_time > max_allowed_time*1000):
                accept = False
                failure_reason = "high completion time"
                logging.info("User failed the assignment with ID: " + assignment_id + " due to " + failure_reason)

            # Approve or reject assignment accordingly
            if (accept):
                logging.info("Assignment " + assignment_id + " approved")
                connection.approve_assignment(
                    AssignmentId = assignment_id,
                    RequesterFeedback = "Congratulations! Your HIT has been approved. Thank you for your time! :)",
                    OverrideRejection = True
                )
            elif (not accept):
                logging.info("Assignment " + assignment_id + " rejected")
                connection.reject_assignment(
                    AssignmentId = assignment_id,
                    RequesterFeedback = "We are sorry to inform you that your HIT has been rejected due to" + failure_reason
                )

            # Send appropriate bonus if the assignment is accepted
            time.sleep(2)
            if accept:
                logging.info("Calculating bonus for WorkerId: " + worker_id)
                send_bonus(assignment_id, num_correct, total_time)


def send_bonus(assignment_id, num_correct, total_time):
    base_pay = 5.20
    min_allowed_correct = 5
    correctness_per_question_bonus = 1.04

    bonus_correctness = round(((num_correct - min_allowed_correct) * correctness_per_question_bonus if (num_correct - min_allowed_correct > 0) else 0), 2)
    
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
    else:
        bonus_time = 0
    bonus_time = round(bonus_time, 2)

    total_bonus = round(bonus_correctness + bonus_time, 2)

    if (total_bonus > 0):
        reason_str = "You received a total bonus of $" + str(total_bonus) + ". $" + str(bonus_correctness) + " due to your correctness and $" + str(bonus_time) + " due to your completion time."
        worker_id = session.query(User).filter_by(assignment_id=assignment_id).first().worker_id
        logging.info("In addition Worker ID: " + worker_id + " received a total bonus of $" + str(total_bonus) + ". $" + str(bonus_correctness) +\
             " due to your correctness and $" + str(bonus_time) + " due to your completion time.")
        connection.send_bonus(
            WorkerId = worker_id,
            BonusAmount = str(total_bonus),
            AssignmentId = assignment_id,
            Reason = reason_str
        ) 
    else:
        worker_id = session.query(User).filter_by(assignment_id=assignment_id).first().worker_id
        logging.info("In addition Worker ID: " + worker_id + "did not receive any bonus.")

def send_bonus_error(worker_id, assignment_id):
    total_bonus = "4.5"
    reason_str = "Due to our issues with your HIT submission you have been compensated with the base pay. Your HIT is neither accepted nor rejected."
    connection.send_bonus(
            WorkerId = worker_id,
            BonusAmount = str(total_bonus),
            AssignmentId = assignment_id,
            Reason = reason_str
    )
    logging.info("Worker ID: " + worker_id + " with Assignment ID: " + assignment_id + " is payed as bonus the base pay due to issues with their HIT submission.")

# Evaluate the workers that failed the HIT initially and accept their hit if they had at least 1 right answer
def re_evaluate_workers(connection, filename):
    data = pd.read_csv(filename)
    worker_id_list = data['worker_id'].values
    assignment_id_list = data['assignment_id'].values

    current_date = datetime.datetime.now().date()

    min_allowed_correct = 1

    for i in range(len(assignment_id_list)):
        accept = True

        assignment_id = assignment_id_list[i]
        worker_id = worker_id_list[i]

        # Check if the assignment was submitted less than a month ago
        submit_date = connection.get_assignment(AssignmentId = assignment_id)['Assignment']['SubmitTime'].date()
        days_diff = (current_date - submit_date).days
        print("Days Difference:", days_diff)

        if days_diff < 30:
            time.sleep(2)
            logging.info("--------------------- Evaluating " + assignment_id + " of worker " + worker_id + " ---------------------")
            num_correct, total_time = get_score_and_time(assignment_id)
            logging.info("Assignment " + assignment_id + " had " + str(num_correct)
            + " correct and was completed in " + str(total_time/1000) + " seconds")

            # Check if the user answered 0 questions correctly
            if (num_correct < min_allowed_correct):
                accept = False
                logging.info("worker's " + worker_id + "HIT is REJECTED")
            else:
                accept = True

            # Approve or reject assignment accordingly
            if (accept):
                connection.approve_assignment(
                    AssignmentId = assignment_id,
                    RequesterFeedback = "Congratulations! We have decided to accept your HIT after re-evaluating our acceptance criteria for the HIT. Thank you for your time! :)",
                    OverrideRejection = True
                )
                logging.info("worker's " + worker_id + "HIT is ACCEPTED")


def approve_specific_assignment(assignment_id):
    connection.approve_assignment(
        AssignmentId = assignment_id,
        RequesterFeedback = "Congratulations! Your HIT has been approved. Thank you for your time! :)",
        OverrideRejection = True
    )

def reject_specific_assignment(assignment_id):
    connection.approve_assignment(
        AssignmentId = assignment_id,
        RequesterFeedback = "Rejected! Speeding detecting. The HIT cannot be completed in less than 5 minutes!",
    )

def grade_specific_assignment(assignment_id, worker_id):
    approve_hits(connection, [assignment_id], [worker_id], check_completion_times=False)


if __name__ == "__main__":
    arg_arr = sys.argv[1:]
    arg1 = arg_arr[0]

    if (arg1 == 'batch_grade'):
        hit_id = arg_arr[1]
        assignments = get_assignment_hits(connection, hit_id, "Submitted")['Assignments']
        assignment_id_list = []
        worker_id_list = []
        for i in assignments:
            assignment_id_list.append(i['AssignmentId'])
            worker_id_list.append(i['WorkerId'])

        logging.info("\n\
        ---------------------------------------------------------------\n\
        --------------------- Running approve_hits.py -----------------\n\
        ---------------------------------------------------------------\n"
        )

        for i in range(len(assignment_id_list)):
            logging.info("worker_id: " + worker_id_list[i] + " with assignment: " + assignment_id_list[i])
        logging.info("There are " + str(len(assignment_id_list)) + " assignments submitted waiting approval")

        approve_hits(connection, assignment_id_list, worker_id_list, check_completion_times=True)
    elif (arg1 == 'reject'):
        assignment_id = arg_arr[1]
        reject_specific_assignment(assignment_id)
    elif (arg1 == 'approve'):
        assignment_id = arg_arr[1]
        approve_specific_assignment(assignment_id)
    elif (arg1 == 'grade'):
        assignment_id = arg_arr[1]
        worker_id = arg_arr[2]
        grade_specific_assignment(assignment_id, worker_id)
