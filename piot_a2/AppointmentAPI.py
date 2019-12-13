"""
This file includes functions for manipulating and accessing the Appointment table in the MAPSDB database.
This table keeps track of the appointments that patients make with doctors 
"""

from flask import Flask, request
import MapsDB

app = Flask(__name__)
db, ma = MapsDB.connect_db(app)


class Appointment(db.Model):
    """
    This class defines the data inside the appointment table. Columns include:
    id as a primary key, start_datetime, doctor_id, patient_id and medical_note.
    """
    id = db.Column(db.Integer, db.Sequence(
        'seq_reg_id', start=1, increment=1), primary_key=True)
    start_datetime = db.Column(db.DATETIME, unique=False)
    doctor_id = db.Column(db.Integer, unique=False)
    patient_id = db.Column(db.Integer, unique=False)
    medical_note = db.Column(db.String(400), unique=False, nullable=True)

    def __init__(self, start_datetime, doctor_id, patient_id, medical_note):
        """
        This function initialises the Appointment table.
        """
        self.start_datetime = start_datetime
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.medical_note = medical_note


class AppointmentSchema(ma.Schema):
    """
    This function describes the schema for the Appointment table.
    """
    class Meta:
        # Fields to expose
        fields = ('id', 'start_datetime', 'doctor_id',
                  'patient_id', 'medical_note')


appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)


def add_appointment():
    """
    This function does not accept any parameters and will add an appointment to the Appoinments table
    getting the appointment information from a HTML form.
    """
    app = request.form['app_slot']
    start_datetime = app.split(',')[1]
    start_datetime = start_datetime.split('+')[0]
    doctor_id = app.split(',')[3]
    patient_id = app.split(',')[4]

    new_appointment = Appointment(start_datetime, doctor_id, patient_id, None)

    db.session.add(new_appointment)
    db.session.flush()
    db.session.commit()


def remove_appointment(start_datetime, doctor_id):
    """
    This function accepts an appointment id and will delete the appointment from the Appointment table.
    """
    appointment = Appointment.query.filter(Appointment.start_datetime.like(start_datetime),
                                            Appointment.doctor_id.like(doctor_id)
                                            ).first()
    db.session.delete(appointment)
    db.session.commit()


def add_medical_note(app_dt, doctor_id, medical_note):
    """
    This function accepts an appointment date, doctor id and a medical note and will add the supplied
    medical note the the Appointment table, using the appointment data and doctor id as keys to
    query the Appointment table.
    """

    app = Appointment.query.filter(Appointment.doctor_id.like(
        doctor_id), Appointment.start_datetime.like(app_dt)).first()
    app.medical_note = medical_note
    db.session.commit()
