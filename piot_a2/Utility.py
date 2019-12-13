"""
This file includes functions for manipulating data from HTML forms
"""

from flask import request
import DoctorAPI
import PatientAPI
import GCalenderAPI
import AppointmentAPI


def get_id_from_form():
    """
    This function does not accept any parameters and will return a doctor and a patient based on the
    patient and doctor emails provided by a HTML form.
    """
    patient_email = request.form['patient_email']
    sel_doctor = request.form['doctor_name']
    doctor = DoctorAPI.get_doctor_by_name(sel_doctor)
    patient = PatientAPI.get_patient_by_email(patient_email)

    return doctor, patient


def get_doctor_id_from_form():
    """
    This function does not accept any parameters and will return a doctor based on the email provided
    by a HTML form.
    """
    sel_doctor_email = request.form['doctor_email']
    doctor = DoctorAPI.get_doctor_by_email(sel_doctor_email)
    return doctor


def get_doctor_name_from_form():
    """
    This function does not accept any parameters and will return a doctor based on the name entered into
    a HTML form..
    """
    sel_doctor_name = request.form['doctor_name']
    doctor = DoctorAPI.get_doctor_by_name(sel_doctor_name)
    return doctor


def add_medical_note():
    """
    This function does not accept any parameters and will add a medical note to the appointment table
    getting the appointment information form a HTML form.
    """
    sel_appointment = request.form['app_slot']
    app_dt = sel_appointment.split(',')[0]
    app_dt = app_dt.split('T')[0] + " " + app_dt.split('T')[1].split('+')[0]
    doctor_id = sel_appointment.split(',')[1]
    medical_note = request.form['medical_note']
    AppointmentAPI.add_medical_note(app_dt, doctor_id, medical_note)


def cancel_booking():
    """
    This function does not accept any parameters and will call the remove_appointment function in the
    AppointmentAPI to remove an remove an appointment based on an appointment id provided by a HTML form.
    """
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
    date = start_datetime.split('T')[0]
    time = start_datetime.split('T')[1]
    start_datetime = date + ' ' + time
    AppointmentAPI.remove_appointment(start_datetime, doctor.id)
