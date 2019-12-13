from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

USER = 'root'
PASS = ''
HOST = '35.189.1.72'
DBNAME = 'mapsdb'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    USER, PASS, HOST, DBNAME)
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Appointment(db.Model):
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    start_datetime = db.Column(db.DATETIME, unique=False)
    doctor_id = db.Column(db.Integer, unique=False)
    patient_id = db.Column(db.Integer, unique=False)
    medical_note = db.Column(db.String(400), unique=False, nullable=True)

    def __init__(self, start_datetime, doctor_id, patient_id, medical_note):
        self.start_datetime = start_datetime
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.medical_note = medical_note


class AppointmentSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'start_datetime', 'doctor_id',
                  'patient_id', 'medical_note')


appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)


def add_appointment():
    """
    Adds an appointment to the database
    """
    app = request.form['app_slot']
    start_datetime = app.split(',')[1]
    doctor_id = app.split(',')[3]
    patient_id = app.split(',')[4]

    new_appointment = Appointment(start_datetime, doctor_id, patient_id, None)

    db.session.add(new_appointment)
    db.session.flush()
    db.session.commit()

def remove_appointment(app_id):
    """
    removes an appointment from the database
    """
    appointment = Appointment.query.get(app_id)
    db.session.delete(appointment)
    db.session.commit()


def add_medical_note(id):
    """
    updates the medical notes for provided appointment id
    """
    medical_note = request.form['medical_note']
    app = Appointment.query.get(id)
    app.medical_note = medical_note
    db.session.commit()
