import os

from flask import Flask, request, jsonify
from flask import render_template
#from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# define cloud database details
USER = 'root'
PASS = ''
HOST = '35.189.1.72'
DBNAME = 'mapsdb'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    USER, PASS, HOST, DBNAME)
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Doctor(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1), primary_key=True)
    email = db.Column(db.String(120),unique=True)
    doctor_name = db.Column(db.String(80), unique=False)
    mobile_num = db.Column(db.Integer, unique=True)
    gender = db.Column(db.String(10), unique=False)
    calender_id = db.Column(db.String(100), unique=True)

    def __init__(self, email, doctor_name, mobile_num, gender, calender_id):
        self.email = email
        self.doctor_name = doctor_name
        self.mobile_num = mobile_num
        self.gender = gender
        self.calender_id = calender_id


class DoctorSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'email', 'doctor_name', 'mobile_num', 'gender')


doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)


def add_doctor(calender_id):
    """
    add patient details to the cloud database
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
    get list of available doctors
    """
    doctor_list = Doctor.query.all()
    doctor_name_list = []
    for doctors in doctor_list:
        doctor_name_list.append(doctors.doctor_name)
    return doctor_name_list


def get_doctor_by_name(doctor_name):
    """
    find a doctor by name
    """
    doctor = Doctor.query.filter(Doctor.doctor_name.like(doctor_name)).first()
    return doctor

def get_doctor_by_email(email):
    """
    find a doctor by email
    """
    doctor = Doctor.query.filter(Doctor.email.like(email)).first()
    return doctor

def get_doctor_by_id(id):
    """
    find a doctor by email
    """
    doctor = Doctor.query.get(id)
    return doctor
