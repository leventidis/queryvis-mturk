from main import db

# Create our database model
class User(db.Model):
    __tablename__ = "users"
    # worker_id is also an Amazon variable
    worker_id = db.Column(db.String(), primary_key=True)

    # Amazon variables
    assignment_id = db.Column(db.String())
    hit_id = db.Column(db.String())
    qualification_score = db.Column(db.Integer)

    # Starting mode
    sequence_num = db.Column(db.Integer)

    # Starting datetime of the entry
    start_datetime = db.Column(db.DateTime())
    end_datetime = db.Column(db.DateTime())

    # Time spent on the tutorial
    tutorial_time = db.Column(db.Integer)

    # Main test
    q1 = db.Column(db.String(1))
    q1_time = db.Column(db.Integer)
    q2 = db.Column(db.String(1))
    q2_time = db.Column(db.Integer)
    q3 = db.Column(db.String(1))
    q3_time = db.Column(db.Integer)
    q4 = db.Column(db.String(1))
    q4_time = db.Column(db.Integer)
    q5 = db.Column(db.String(1))
    q5_time = db.Column(db.Integer)
    q6 = db.Column(db.String(1))
    q6_time = db.Column(db.Integer)
    q7 = db.Column(db.String(1))
    q7_time = db.Column(db.Integer)
    q8 = db.Column(db.String(1))
    q8_time = db.Column(db.Integer)
    q9 = db.Column(db.String(1))
    q9_time = db.Column(db.Integer)
    q10 = db.Column(db.String(1))
    q10_time = db.Column(db.Integer)
    q11 = db.Column(db.String(1))
    q11_time = db.Column(db.Integer)
    q12 = db.Column(db.String(1))
    q12_time = db.Column(db.Integer)

    # Demographics
    likert_q1 = db.Column(db.Integer)
    likert_q2 = db.Column(db.Integer)
    likert_q3 = db.Column(db.Integer)
    likert_q4 = db.Column(db.Integer)
    likert_q5 = db.Column(db.Integer)
    likert_q6 = db.Column(db.Integer)

    feedback = db.Column(db.String())
    country = db.Column(db.String())
    gender= db.Column(db.String())
    age = db.Column(db.Integer)
    occupation = db.Column(db.String())
    income = db.Column(db.Integer)
    sql_exp = db.Column(db.String())
    frequency = db.Column(db.Integer)
    usage = db.Column(db.String())

    def __init__(self, worker_id=None):
        self.worker_id = worker_id