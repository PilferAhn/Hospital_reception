"""
This file implements functions for accessing and editing the Patient table in the MAPSDB database
"""

from flask import Flask, request
import MapsDB

app = Flask(__name__)
db, ma = MapsDB.connect_db(app)


class Patient(db.Model):
    """
    This class describes the columns in the Patient table. Patient columns include:
    id as the primary key, email, first_name, last_name, mobile_num, gender, dob and medical_history.
    This table is used to hold patient information.
    """
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(80), unique=False)
    last_name = db.Column(db.String(80), unique=False)
    mobile_num = db.Column(db.Integer, unique=True)
    gender = db.Column(db.String(10), unique=False)
    dob = db.Column(db.DATE, unique=False)
    medical_history = db.Column(db.String(400), unique=False)

    def __init__(self, email, first_name, last_name, mobile_num, gender, dob, medical_history):
        """
        This function initialises the Patient table
        """
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.mobile_num = mobile_num
        self.gender = gender
        self.dob = dob
        self.medical_history = medical_history


class PatientSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'email', 'first_name', 'last_name',
                  'mobile_num', 'gender', 'dob', 'medical_history')


patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)


def add_patient():
    """
    This function does not accept any parameters and will add a patient to the Patient table, getting
    patient data form a HTML form.
    """
    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    mobile_num = request.form['mobile_num']
    gender = request.form['gender']
    dob = request.form['dob']
    medical_history = request.form['medical_history']

    new_patient = Patient(email, first_name, last_name,
                          mobile_num, gender, dob, medical_history)

    db.session.add(new_patient)
    db.session.flush()
    db.session.commit()


def get_patient_by_id(id):
    """
    This function accepts a patient id as a parameter and will return the patient from the Patient table
    that has the provided id.
    """
    patient = Patient.query.get(id)
    return patient


def get_patient_by_email(email):
    """
    This function accepts a patient email and will return the patient from the Patient table that has
    the provided email
    """
    patient = Patient.query.filter(Patient.email.like(email)).first()
    return patient


def get_patient_data():
    """
    This function does not accept any parameters and returns the patients information form the Patient table
    that has the email provide by a HTML form.
    """
    email = request.form["doctor_search_action"]
    patient_list = Patient.query(Patient).filter(Patient.email.like(email))
    patient_info = []

    for patient_data in patient_list:
        patient_info[0](patient_data.id)
        patient_info[1](patient_data.email)
        patient_info[2](patient_data.first_name)
        patient_info[3](patient_data.last_name)
        patient_info[4](patient_data.mobile_num)
        patient_info[5](patient_data.email)
        patient_info[6](patient_data.gender)
        patient_info[7](patient_data.dob)
        patient_info[8](patient_data.medical_history)
        return(patient_info)
