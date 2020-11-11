import sys
import boto3
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
DEV_ENVIRONMENT_BOOLEAN = False

def get_connection():
    if DEV_ENVIRONMENT_BOOLEAN:
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

def draw_submissions_over_time_graph(timestamps):
    num_workers_list = list(range(1, len(timestamps) + 1))

    # Draw figure of number of HIT submissions vs. Time
    fig, ax = plt.subplots(1)
    fig.autofmt_xdate()
    plt.plot(timestamps, num_workers_list)
    plt.xlabel('Time/Date', fontsize=18)
    plt.ylabel('Number of workers', fontsize=18)
    plt.title('Number of workers that completed HIT vs. Time', fontsize=20)

    xfmt = mdates.DateFormatter('%d-%m-%y %H:%M')
    ax.xaxis.set_major_formatter(xfmt)

    plt.show()


# Rejects all submitted assignments
def reject_all_assignments(hit_id):
    list_assignments_dict = conn.list_assignments_for_hit(HITId = hit_id, AssignmentStatuses=['Submitted'])

    for assignment in list_assignments_dict["Assignments"]:
        conn.reject_assignment(AssignmentId=assignment["AssignmentId"], RequesterFeedback="HIT rejected")

# Provides a summary of the last 100 hits
def summary():
    hit_list_dict = conn.list_hits(MaxResults=100)
    print("There are in total " + str(hit_list_dict['NumResults']) + " hits")

    for hit in hit_list_dict['HITs']:
        hit_id = hit["HITId"]
        hit_detail(hit_id, show_graph=False)

# Deletes all HITs except the ones in the except list
def clear():
    except_list = []
    hit_list_dict = conn.list_hits(MaxResults=100)

    for hit in hit_list_dict["HITs"]:
        hit_id = hit["HITId"]

        if hit_id not in except_list:
            if hit['HITStatus'] != 'Reviewable':
                print("Cannot delete HIT: " + hit_id + " because it is not reviewable")
            else:
                # This will auto-reject all assignments pending in the hit
                reject_all_assignments(hit_id)
                conn.delete_hit(HITId = hit_id)
                print("Deleting HIT: " + hit_id + " created on " + str(hit['CreationTime']))

# Extend HIT to have an additional num_additional_assignments assignments
def extend_hit(num_additional_assignments):
    hit_id = "306996CF6WKT6MUWN06276YLZXHB10"

    response = conn.create_additional_assignments_for_hit(
        HITId = hit_id,
        NumberOfAdditionalAssignments = num_additional_assignments
    )

    print("Added " + str(num_additional_assignments) + " for hit " + hit_id)

# More details on a specific HIT
def hit_detail(hit_id, show_graph = False):
    hit_obj = conn.get_hit(HITId = hit_id)
    hit = hit_obj['HIT']

    assignments = conn.list_assignments_for_hit(
        HITId=hit_id,
        MaxResults=100
    )

    num_submitted = 0
    num_approved = 0
    num_rejected = 0

    timestamps = []
    worker_ids = []

    for assignment in assignments["Assignments"]:
        status = assignment['AssignmentStatus']
        if (status == "Submitted"):
            num_submitted += 1
        elif (status == "Approved"):
            num_approved += 1
        elif (status == "Rejected"):
            num_rejected += 1
        timestamps.append(assignment['SubmitTime'])
        worker_ids.append(assignment['WorkerId'])
    
    print(hit_id + " created on " + str(hit['CreationTime']) + " with expiration on "
        + str(hit['Expiration']) + " has status " + hit['HITStatus'] + " and has " 
        + str(hit['NumberOfAssignmentsPending'])  + " pending "
        + str(hit['NumberOfAssignmentsAvailable'])  + " available and "
        + str(hit['NumberOfAssignmentsCompleted'])  + " completed. Out of those "
        + str(num_submitted) + " are submitted " + str(num_approved) + " are approved and "
        + str(num_rejected) + " are rejected")

    # check for returning workers
    worker_ids = set(worker_ids)
    with open('data/worker_ids_taken_old_hit.csv') as f:
        workers_taken_hit = set(f.read().splitlines())
    returning_workers = workers_taken_hit.intersection(worker_ids)
    print('There are', len(returning_workers), 'returning workers')

    if show_graph == True:
        draw_submissions_over_time_graph(timestamps)

# Details on a set of HITs
def hits_detail(hit_ids):
    num_submitted = 0
    num_approved = 0
    num_rejected = 0
    timestamps = []
    worker_ids = []

    for hit_id in hit_ids:
        assignments = conn.list_assignments_for_hit(
            HITId=hit_id,
            MaxResults=100
        )

        for assignment in assignments["Assignments"]:
            status = assignment['AssignmentStatus']
            if (status == "Submitted"):
                num_submitted += 1
            elif (status == "Approved"):
                num_approved += 1
            elif (status == "Rejected"):
                num_rejected += 1
            timestamps.append(assignment['SubmitTime'])
            worker_ids.append(assignment['WorkerId'])

    print(str(num_submitted) + " are submitted " +
        str(num_approved) + " are approved and " + str(num_rejected) + " are rejected")

    timestamps = sorted(timestamps)
    draw_submissions_over_time_graph(timestamps)
    

# List of submitted assignments for a hit
def get_assignments(hit_id, status, ids_only):
    assignments = conn.list_assignments_for_hit(
        HITId = hit_id,
        MaxResults=100,
        AssignmentStatuses=[status]
    )['Assignments']

    assignment_id_list = []
    worker_id_list = []
    for i in assignments:
        assignment_id_list.append(i['AssignmentId'])
        worker_id_list.append(i['WorkerId'])

    for i in range(len(assignment_id_list)):
        if (ids_only):
            print(worker_id_list[i])
        else:
            print("worker_id: " + worker_id_list[i] + " with assignment: " + assignment_id_list[i])
    print("There are " + str(len(assignment_id_list)) + " assignments that have status " + status)

# List of worker_ids that are Approved and Rejected for a hit
def get_worker_id_list(hit_id):
    assignments = conn.list_assignments_for_hit(
        HITId = hit_id,
        MaxResults=100,
        AssignmentStatuses=['Approved']
    )['Assignments']

    worker_id_list = []
    for i in assignments:
        print(i['WorkerId'])
        worker_id_list.append(i['WorkerId'])

    assignments = conn.list_assignments_for_hit(
        HITId = hit_id,
        MaxResults=100,
        AssignmentStatuses=['Rejected']
    )['Assignments']
    for i in assignments:
        print(i['WorkerId'])
        worker_id_list.append(i['WorkerId'])

    print(worker_id_list)
    print("There are in total: " + str(len(worker_id_list)) + " workers")


#------------------------- Qualification Functions -------------------------#

# Approves the qualifications of a custom list of worker_ids
def approve_qualifications(qual_id):
    qual_requests = conn.list_qualification_requests(
        QualificationTypeId = qual_id,
    )['QualificationRequests']

    accept_list = ['A1E64VF4LFO4GL']

    for request in qual_requests:
        worker_id = request['WorkerId']
        print("Worker " + worker_id + " requested")
        if worker_id in accept_list:
            print("Worker ID " + worker_id + "is in the list")
            conn.accept_qualification_request (
                QualificationRequestId = request['QualificationRequestId']
            )
            print("Granted " + worker_id + " the qualification " + qual_id)
    
    list_workers_with_qual = conn.list_workers_with_qualification_type(
        QualificationTypeId = qual_id,
        Status = "Granted"
    )['Qualifications']

    for worker in list_workers_with_qual:
        print("worker_id " + worker["WorkerId"] + " was granted the qualification on " 
        + str(worker['GrantTime']))

# Give a specific worker with a specific qualification
def give_worker_qualification(qual_id, worker_id):
    qual_score = 100

    time.sleep(2)
    response = conn.associate_qualification_with_worker (
        QualificationTypeId=qual_id,
        WorkerId=worker_id,
        IntegerValue=qual_score,
        SendNotification=True
    )
    print("Worker ID: " + worker_id + " has been given qualification " + qual_id + " with a score of " + str(qual_score))

# Gives the taken test qualification to everyone that has attempted to take the Visualizing Queries HIT
def set_taken_test_qualification(qual_id, workers_file):
    with open(workers_file) as f:
        worker_ids = f.readlines()

    worker_ids = [x.strip() for x in worker_ids]

    for i in range(len(worker_ids)):
        print("Worker " + str(i+1) + "/" + str(len(worker_ids)))
        time.sleep(2)
        response = conn.associate_qualification_with_worker (
            QualificationTypeId=qual_id,
            WorkerId=worker_ids[i],
            IntegerValue=1,
            SendNotification=True
        )
        print("Worker ID: " + worker_ids[i] + " has been given the taken_test_qualification")

# Removes qualification qual_id from a list of workers specified in workers_file
def remove_qualification(qual_id, workers_file):
    with open(workers_file) as f:
        worker_ids = f.readlines()

    worker_ids = [x.strip() for x in worker_ids]

    for i in range(len(worker_ids)):
        print("Worker " + str(i+1) + "/" + str(len(worker_ids)))
        time.sleep(2)
        response = conn.disassociate_qualification_from_worker (
            QualificationTypeId=qual_id,
            WorkerId=worker_ids[i],
            Reason='Revoked Qualification'
        )
        print("Worker ID: " + worker_ids[i] + " has been revoked from the taken_test_qualification")

def get_workers_with_qualification(qual_id):
    response = conn.list_workers_with_qualification_type(
        QualificationTypeId=qual_id,
        Status='Granted',
        MaxResults=100
    )
    token = response['NextToken']

    workers_ids_that_pass_qualification = []

    def print_qual_results(response, success_count, reject_count):
        min_qualification_score = 66
        for qual in response['Qualifications']:
            if qual["IntegerValue"] >= min_qualification_score:
                workers_ids_that_pass_qualification.append(qual['WorkerId'])
                success_count += 1
            else:
                reject_count += 1
            
            print("Worker ID: " + qual['WorkerId'] + " was " + qual['Status'] + " the qualification on "\
                + str(qual['GrantTime']) + " with IntegerValue of " + str(qual["IntegerValue"])) 
        return success_count, reject_count

    success_count = 0
    reject_count = 0

    success_count, reject_count = print_qual_results(response, success_count, reject_count)

    while token != None:
        response = conn.list_workers_with_qualification_type(
            QualificationTypeId=qual_id,
            NextToken=token,
            Status='Granted',
            MaxResults=100
        )
        if 'NextToken' in response:
            token = response['NextToken']
        else:
            token = None
        success_count, reject_count = print_qual_results(response, success_count, reject_count)

    print("Workers IDs that pass qualification:")
    for worker in workers_ids_that_pass_qualification:
        print(worker)

    print("There are in total " + str(success_count + reject_count) + " workers that have attempted the qualification " + qual_id)
    print(str(success_count), "successes and", str(reject_count), "rejections.")


def get_qualification_score(qual_id, worker_id):
    response = conn.get_qualification_score(
        QualificationTypeId=qual_id,
        WorkerId=worker_id
    )['Qualification']

    print("Worker ID: " + response['WorkerId'] + " was " + response['Status'] + " the qualification on "\
        + str(response['GrantTime']) + " with IntegerValue of " + str(response["IntegerValue"])) 

# Deactivates/hit_id an ongoing HIT
def update_expiration(qual_id):
    response = conn.update_expiration_for_hit(
        HITId=hit_id,
        ExpireAt=datetime(2019,5,15,18,0,0)
    )
    print(response)

def notify_workers(workers_file):
    '''
    Given a workers_file with a list of worker IDs, notify the workers to participate in our new study 
    '''
    
    with open(workers_file) as f:
        worker_ids = f.readlines()

    worker_ids = [x.strip() for x in worker_ids]

    print("Sending notification to", len(worker_ids), 'workers')

    for worker in worker_ids:
        time.sleep(2)
        response = conn.notify_workers(
            Subject="Invitation to participate in: Understanding SQL Queries -- $5.20 to $16.47 with bonuses HIT",
            MessageText=("You have previously participated in our HIT regarding the interpretation of SQL queries through "
                "visual diagrams. We are currently running a new HIT similar to the old one but with new questions, and we thought you might be "
                "interested in participating in this new study. "
                "The base pay for the new HIT is $5.20 if you answer at least 5/12 questions correctly and it can reach up to $16.47 with bonuses "
                "that are based on your performance and time metrics. You can find the HIT by searching for 'Understanding SQL Queries'. "
                "The HIT is provided by the requester: Northeastern U. DataVis Studies"),
            WorkerIds = [worker]
        )

        # Check for failures
        if not response['NotifyWorkersFailureStatuses']:
            print("Successfully notified worker", worker, '\n')
        else:
            print(response['NotifyWorkersFailureStatuses'])


def notify_workers_with_qualification(qualification_file, taken_hit_file):
    '''
    Given a qualification file that lists all workers that passed the qualification and a list of
    workers that have taken the hit, notify all the workers that have the qualification but have yet
    to take the hit.
    '''
    with open(qualification_file) as f:
        workers_with_qualification = set(f.read().splitlines())

    with open(taken_hit_file) as f:
        workers_taken_hit = set(f.read().splitlines())

    workers_to_notify = workers_with_qualification - workers_taken_hit

    for worker in workers_to_notify:
        time.sleep(2)
        response = conn.notify_workers(
            Subject="Invitation to participate in: Understanding SQL Queries -- $5.20 to $16.47 with bonuses HIT",
            MessageText=("We noticed that you have successfully completed your qualification test for our 'Understanding SQL Queries' HIT,"
                "but you haven't yet taken the HIT yet. Given the performance on your qualification test we believe that "
                "you can successfully complete the HIT. "
                "The base pay for the new HIT is $5.20 if you answer at least 5/12 questions correctly and it can reach up to $16.47 with bonuses "
                "that are based on your performance and time metrics. The expected completion time for the HIT is about 30 minutes."
                "You can find the HIT by searching for 'Understanding SQL Queries'. "
                "The HIT is provided by the requester: Northeastern U. DataVis Studies"),
            WorkerIds = [worker]
        )

        # Check for failures
        if not response['NotifyWorkersFailureStatuses']:
            print("Successfully notified worker", worker, '\n')
        else:
            print(response['NotifyWorkersFailureStatuses'])


conn = get_connection()

if __name__ == "__main__":
    print('DEV_ENVIRONMENT_BOOLEAN is set to', DEV_ENVIRONMENT_BOOLEAN, "\n")

    arg_arr = sys.argv[1:]
    arg1 = arg_arr[0]
    
    if (arg1 == "summary"):
        summary()
    elif (arg1 == "clear"):
        clear()
    elif (arg1 == "extend"):
        num_additional_assignments = int(arg_arr[1])
        extend_hit(num_additional_assignments)
    elif (arg1 == 'hit_detail'):
        hit_id = arg_arr[1]
        hit_detail(hit_id, show_graph=True)
    elif (arg1 == 'hits_detail'):
        hit_id1 = arg_arr[1]
        hit_id2 = arg_arr[2]
        hits = [hit_id1, hit_id2]
        hits_detail(hits)
    elif (arg1 == 'get_assignments'):
        hit_id = arg_arr[1]
        status = arg_arr[2]
        ids_only = False
        if (len(arg_arr) == 4):
            ids_only = bool(arg_arr[3])
        get_assignments(hit_id, status, ids_only)
    elif (arg1 == 'get_worker_id_list'):
        hit_id = arg_arr[1]
        get_worker_id_list(hit_id)
    elif (arg1 == 'approve_qualifications'):
        qual_id = arg_arr[1]
        approve_qualifications(qual_id)
    elif (arg1 == 'update_expiration'):
        hit_id = arg_arr[1]
    elif (arg1 == 'give_worker_qualification'):
        qual_id = arg_arr[1]
        worker_id = arg_arr[2]
        give_worker_qualification(qual_id, worker_id)
    elif (arg1 == 'set_taken_test_qualification'):
        qual_id = arg_arr[1]
        workers_file = arg_arr[2]
        set_taken_test_qualification(qual_id, workers_file)
    elif (arg1 == 'remove_qualification'):
        qual_id = arg_arr[1]
        workers_file = arg_arr[2]
        remove_qualification(qual_id, workers_file)
    elif (arg1 == 'get_workers_with_qualification'):
        qual_id = arg_arr[1]
        get_workers_with_qualification(qual_id)
    elif (arg1 == 'get_qualification_score'):
        qual_id = arg_arr[1]
        worker_id = arg_arr[2]
        get_qualification_score(qual_id, worker_id)
    elif (arg1 == 'notify_workers'):
        workers_file = arg_arr[1]
        notify_workers(workers_file)
    elif (arg1 == 'notify_workers_with_qualification'):
        qualification_file = arg_arr[1]
        taken_hit_file = arg_arr[2]
        notify_workers_with_qualification(qualification_file, taken_hit_file)
    else:
        print("Invalid command line argument")