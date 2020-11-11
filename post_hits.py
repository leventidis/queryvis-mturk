import os
import sys
import boto3

#Start Configuration Variables
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
DEV_ENVIROMENT_BOOLEAN = False
#End Configuration Variables

#This allows us to specify whether we are pushing to the sandbox or live site.
if DEV_ENVIROMENT_BOOLEAN:
    AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"            # For Sandbox only
    qualification_id = "qualification_id"                           # For Sandbox only
    custom_qualification_id = "custom_qualification_id"             # For Sandbox only
    taken_test_qualification_id = "taken_test_qualification_id"     # For Sandbox only
else:
    AMAZON_HOST = "mechanicalturk.amazonaws.com"                    # For Non-Sandbox only
    qualification_id = "qualification_id"             # For Non-Sandbox only
    custom_qualification_id = "custom_qualification_id"             # For Non-Sandbox only
    taken_test_qualification_id = "taken_test_qualification_id"     # For Non-Sandbox only

# HIT specific variables
base_pay = "5.2"
approval_percentage = 95
minimum_qualification_score = 66    # This is equivalent to 4/6 correct for Amazon

title_str = "Understanding SQL Queries -- $5.20 to $16.47 with bonuses"

description_str = "You will receive $5.20-$16.47 (estimated time 30 minutes) for participating in this research. \
Workers must be experienced with SQL as measured by the qualification test (included in the 30 minutes estimate). \
The HIT is composed of 12 multiple choices questions that ask the user to find the correct description \
of a SQL query based on a text and/or visual representation. To successfully complete the HIT you need \
to answer at least 5 questions correctly within 50 minutes. You receive bonuses for more correct answers \
and in a shorter time. For more details click on Preview to view the full instructions of the HIT. \
Please contact us with any questions or issues, especially if you get a 'Your HIT submission \
was not successful' error message."

usa = [{'Country': "US"}]

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

def post_hit(approval_percentage):
    connection = get_connection()

    questionform = open("external_question.xml", 'r').read()

    # Boto3 version
    create_hit_result = connection.create_hit(
        Question = questionform,
        MaxAssignments = 30,
        LifetimeInSeconds = 60*60*24*10,
        AssignmentDurationInSeconds = 60*60*2,
        Reward = base_pay,
        Title = title_str,
        Description = description_str,
        QualificationRequirements = [{'QualificationTypeId': qualification_id,
                                    'Comparator': 'GreaterThanOrEqualTo',
                                    'IntegerValues':[minimum_qualification_score],
                                    },
                                    {'QualificationTypeId': "00000000000000000071",
                                    'Comparator': 'EqualTo',
                                    'LocaleValues': usa
                                    },
                                    {'QualificationTypeId': "000000000000000000L0",
                                    'Comparator': 'GreaterThanOrEqualTo',
                                    'IntegerValues':[approval_percentage]
                                    },
                                    {'QualificationTypeId': taken_test_qualification_id,
                                    'Comparator': 'DoesNotExist',
                                    }]
    )

    print("Created a new HIT with HITId: " + create_hit_result['HIT']['HITId'])

def pilot_post_hit(approval_percentage):
    connection = get_connection()

    questionform = open("external_question.xml", 'r').read()

    # Boto3 version
    create_hit_result = connection.create_hit(
        Question = questionform,
        MaxAssignments=12,
        LifetimeInSeconds=60*60*24*7,
        AssignmentDurationInSeconds=60*60*2,
        Reward = base_pay,
        Title = title_str,
        Description = description_str,
        QualificationRequirements=[{'QualificationTypeId': qualification_id,
                                    'Comparator': 'GreaterThanOrEqualTo',
                                    'IntegerValues':[minimum_qualification_score]
                                    },
                                    {'QualificationTypeId': "00000000000000000071",
                                    'Comparator': 'EqualTo',
                                    'LocaleValues': usa
                                    },
                                    {'QualificationTypeId': "000000000000000000L0",
                                    'Comparator': 'GreaterThanOrEqualTo',
                                    'IntegerValues':[approval_percentage]
                                    }]
    )

    print("Created a new HIT with HITId: " + create_hit_result['HIT']['HITId'])

def test_post_hit():
    connection = get_connection()

    questionform = open("external_question.xml", 'r').read()

    # Boto3 version
    create_hit_result = connection.create_hit(
        Question = questionform,
        MaxAssignments=12,
        LifetimeInSeconds=60*60*1,
        AssignmentDurationInSeconds=60*60*2,
        Reward = base_pay,
        Title = title_str,
        Description = description_str,
        QualificationRequirements=[{'QualificationTypeId': qualification_id,
                            'Comparator': 'GreaterThanOrEqualTo',
                            'IntegerValues':[minimum_qualification_score]
                            },
                            {'QualificationTypeId': "00000000000000000071",
                            'Comparator': 'In',
                            'LocaleValues': usa
                            },
                            {'QualificationTypeId': "000000000000000000L0",
                            'Comparator': 'GreaterThanOrEqualTo',
                            'IntegerValues':[approval_percentage]
                            },
                            {'QualificationTypeId': taken_test_qualification_id,
                            'Comparator': 'DoesNotExist',
                            }]
    )

    print("Created a test HIT with HITId: " + create_hit_result['HIT']['HITId'])

def custom_post_hit(approval_percentage):
    connection = get_connection()

    questionform = open("external_question.xml", 'r').read()

    # Boto3 version
    create_hit_result = connection.create_hit(
        Question = questionform,
        MaxAssignments=1,
        LifetimeInSeconds=60*60*24*10,
        AssignmentDurationInSeconds=60*60*2,
        Reward = base_pay,
        Title = "CUSTOM HIT for A2OATZCX1YXE77, " + title_str,
        Description = description_str + "THIS HIT IS ONLY FOR THAT SPECIFIC WORKER!",
        QualificationRequirements = [{'QualificationTypeId': qualification_id,
                                    'Comparator': 'GreaterThanOrEqualTo',
                                    'IntegerValues':[minimum_qualification_score],
                                    },
                                    {'QualificationTypeId': "00000000000000000071",
                                    'Comparator': 'EqualTo',
                                    'LocaleValues': usa
                                    },
                                    {'QualificationTypeId': "000000000000000000L0",
                                    'Comparator': 'GreaterThanOrEqualTo',
                                    'IntegerValues':[approval_percentage]
                                    },
                                    {'QualificationTypeId': custom_qualification_id,
                                    'Comparator': 'Exists',
                                    }]
    )

    print("Created a custom new HIT with HITId: " + create_hit_result['HIT']['HITId'])

def create_multiple_hits():
    for i in range(5):
        title = "SQL Query Visualization " + str(i)
        post_hit(title)

if __name__ == "__main__":
    arg_arr = sys.argv[1:]
    arg1 = arg_arr[0]

    if arg1 not in ['full', 'pilot', 'custom', 'test']:
        print("Invalid argument! Argument must be one of 'full', 'pilot', 'custom' or 'test'")
        sys.exit()

    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}

    setting = "on SANDBOX" if DEV_ENVIROMENT_BOOLEAN else "LIVE"
    print("Are you sure you want to deploy a " + arg1 + " HIT " + setting + "? [Y/N]")
    choice = input().lower()
    if choice in yes:
        if arg1 == 'full':
            post_hit(approval_percentage)
        elif arg1 == 'pilot':
            pilot_post_hit(approval_percentage)
        elif arg1 == 'custom':
            custom_post_hit(approval_percentage)
        elif arg1 == 'test':
            test_post_hit()
    elif choice in no:
        print("Execution cancelled")
    else:
        sys.stdout.write("Please respond with 'y' (yes) or 'n' (no)\n")