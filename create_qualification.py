import boto3
import sys
from post_hits import get_connection

# Make sure to check the value of DEV_ENVIROMENT_BOOLEAN from post_hits.py before running to make sure it is in Sandbox or Live mode

questions = open(name='qualification_questions.xml', mode='r').read()
answers = open(name='qualification_answers.xml', mode='r').read()

connection = get_connection()

def create_qualification():
    qual_response = connection.create_qualification_type(
        Name='SQL qualification test',
        Keywords='test, qualification, SQL',
        Description='A basic SQL qualification test required in order to qualify for the HIT',
        QualificationTypeStatus='Active',
        Test=questions,
        AnswerKey=answers,
        TestDurationInSeconds=60*15
    )
                            
    print("QualificationId: " + qual_response['QualificationType']['QualificationTypeId'])

# Custom qualification designed to grant qualifications for people that were faced with errors when taking the test
def create_custom_qualification():
    qual_response = connection.create_qualification_type(
        Name='Custom qualification test (for invited workers only)',
        Keywords='Custom',
        Description='Only workers who have been specifically emailed will be able to have this qualification approved. \
        If you have not been specifically emailed please do not send a request to have this qualification approved.',
        QualificationTypeStatus='Active',
        RetryDelayInSeconds = 1,
        TestDurationInSeconds=60*60
    )
                            
    print("Custom QualificationId: " + qual_response['QualificationType']['QualificationTypeId'])

# Qualification assigned to everyone that has taken the test previously
def create_taken_test_qualification():
    qual_response = connection.create_qualification_type(
        Name='Worker attempted/completed Understanding SQL Queries -- $5.20 to $16.47 with bonuses HIT previously',
        Keywords='Custom, Attempted HIT, Prevent Repetition, Prevent Retake',
        Description='Having this qualification signifies that you have attempted/completed the Visualizing Database Queries HIT posted in October/November of 2019.\
        This qualification is given so that the same workers cannot take the same HIT twice. ONLY WORKERS WITHOUT THIS QUALIFICATION CAN ACCEPT THE NEW POSTED HIT.',
        QualificationTypeStatus='Active',
        TestDurationInSeconds=60*60
    )
                            
    print("Taken Test QualificationId: " + qual_response['QualificationType']['QualificationTypeId'])


if __name__ == "__main__":
    arg_arr = sys.argv[1:]
    arg1 = arg_arr[0]

    if arg1 == "test":
        create_qualification()
    elif arg1 == "custom":
        create_custom_qualification()
    elif arg1 == "test_taken":
        create_taken_test_qualification()