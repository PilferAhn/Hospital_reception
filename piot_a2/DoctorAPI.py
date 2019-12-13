"""
This file implements classes for creating the Doctors table and functions for the data in the Doctors table.
"""

from flask import Flask, request
import MapsDB

app = Flask(__name__)
db, ma = MapsDB.connect_db(app)


class Doctor(db.Model):
    """
    This class will create a Doctor table with columns id, email, doctor_name, mobile_num, gener and calender_id.
    This table keeps track of information of doctors who are registered in the database.
    """
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    email = db.Column(db.String(120), unique=True)
    doctor_name = db.Column(db.String(80), unique=False)
    mobile_num = db.Column(db.Integer, unique=True)
    gender = db.Column(db.String(10), unique=False)
    calender_id = db.Column(db.String(100), unique=True)

    def __init__(self, email, doctor_name, mobile_num, gender, calender_id):
        """
        This function initialises the Doctors table.
        """
        self.email = email
        self.doctor_name = doctor_name
        self.mobile_num = mobile_num
        self.gender = gender
        self.calender_id = calender_id


class DoctorSchema(ma.Schema):
    """
    This class defines the schema for the Doctors table
    """
    class Meta:
        """
        This function defines the fields in the Doctors tabe schema
        """
        # Fields to expose
        fields = ('id', 'email', 'doctor_name', 'mobile_num', 'gender')


doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)


def add_doctor(calender_id):
    """
    This function accepts a calendar id as a parameter and will add a doctor to the Doctor table
    using parameters from a HTML form.
    """
    email = request.form['doctor_email']
    doctor_name = request.form['doctor_name']
    mobile_num = request.form['mobile_num']
    gender = request.form['gender']

    new_doctor = Doctor(email, doctor_name, mobile_num, gender, calender_id)

    db.session.add(new_doctor)
    db.session.flush()
    db.session.commit()


def get_all_doctors_name():
    """
    This function does not accepts any parameters and will return the name of all the doctors in
    the Doctors table.
    """
    doctor_list = Doctor.query.all()
    doctor_name_list = []
    for doctors in doctor_list:
        doctor_name_list.append(doctors.doctor_name)
    return doctor_name_list


def get_doctor_by_name(doctor_name):
    """
    This function accepts a string a name as its only parameter and will return the doctor that has
    the provided name in the Doctor table.
    """
    doctor = Doctor.query.filter(Doctor.doctor_name.like(doctor_name)).first()
    return doctor


def get_doctor_by_email(email):
    """
    This function accepts a string an email as its only parameter and will return the doctor that has
    the provided email in the Doctor table.
    """
    doctor = Doctor.query.filter(Doctor.email.like(email)).first()
    return doctor


def get_doctor_by_id(id):
    """
    This function accepts a string an id as its only parameter and will return the doctor that has
    the provided id in the Doctor table.
    """
    doctor = Doctor.query.get(id)
    return doctor
