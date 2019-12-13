from flask import request
import DoctorAPI
import PatientAPI
import GCalenderAPI
import AppointmentAPI

def get_id_from_form():
    patient_email = request.form['patient_email']
    sel_doctor = request.form['doctor_name']
    doctor = DoctorAPI.get_doctor_by_name(sel_doctor)
    patient = PatientAPI.get_patient_by_email(patient_email)

    return doctor, patient

def  get_doctor_id_from_form():
    sel_doctor_email = request.form['doctor_email']
    doctor = DoctorAPI.get_doctor_by_email(sel_doctor_email)
    return doctor


def cancel_booking():
    # cancel selected appointment
    app_id = request.form['sel_appoint']
    GCalenderAPI.cancel_appointment(app_id)
    # add appointent slot back to doctor
    app = GCalenderAPI.get_appointment_by_id(app_id)
    doctor_email = app['extendedProperties']['private']['doctor_email']
    doctor = DoctorAPI.get_doctor_by_email(doctor_email)
    start_datetime = app['start']['dateTime']
    start_datetime = start_datetime.split('+')[0]
    GCalenderAPI.add_available_time(doctor, start_datetime)
    # remove appointment from the cloud database
    AppointmentAPI.remove_appointment(app_id)

