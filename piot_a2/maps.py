#!/usr/bin/env python3

"""
This file implements the functionality of the website and controls the flow of user interaction.
"""

import os
from flask import Flask, request, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import GCalenderAPI
import PatientAPI
import DoctorAPI
import AppointmentAPI
import Utility as util
import MapsDB
import AssistantPi as assistant

# Get prepared for flask (a web framework) and bootstrap
app = Flask(__name__, static_url_path='/static')
bootstrap = Bootstrap(app)
db, ma = MapsDB.connect_db(app)

user_not_exist = "The user does not exist in the database. Please try again."
doctor_not_available = "The doctor you have selected currently does not have available sessions."
no_booking_found = "You have not made any bookings yet."

# Route pages based on purposes
@app.route('/', methods=['GET'])
def index():
    """
    This function directs the user on the index page of the site.
    """
    return render_template('index.html')


@app.route('/patients', methods=['GET', 'POST'])
def patients():
    """
    This function directs the user to the patients page of the site.
    """
    return render_template('patients.html')


@app.route('/patients/register', methods=['GET', 'POST'])
def patient_reg():
    """
    This function directs the user to the register page of the site.
    """
    if request.method == 'POST':
        if request.form['patient_action'] == "submission":
            PatientAPI.add_patient()
            return redirect(url_for('patients'))
        elif request.form['patient_action'] == "back":
            return redirect(url_for('patients'))
    return render_template('patient_reg.html')


@app.route('/patients/book', methods=['GET', 'POST'])
def patient_book():
    """
    This function handles the patient booking, it has a POST method that requires the user to enter a patient email.
    The user is then prompted to enter the doctor they with to book their appointment with.
    """
    patient_valid = True
    doctor_valid = True
    msg = ""
    if request.method == 'POST':
        if request.form['patient_book_email_action'] == "search":
            doctor, patient = util.get_id_from_form()
            doctor_availability = GCalenderAPI.get_appointment_list(
                doctor_email=doctor.email, calender_id=doctor.calender_id)
            # check for valid patient email
            if patient is None:
                patient_valid = "False"
                msg = "You have not been registered in the Database."
                # return redirect(url_for('patient_book', error_msg = "The user does not exist.", patient_valid = "False"))
            elif not doctor_availability:
                doctor_valid = "False"
                msg = "The doctor currently does not have any available time slot."
                # return redirect(url_for('patient_book', error_msg = "The doctor does not have available sessions.", doctor_valid = "False"))
            else:
                return redirect(url_for('patient_book_app', patient_id=patient.id, doctor_id=doctor.id))
        elif request.form['patient_book_email_action'] == "back":
            return redirect(url_for('patients'))

    doctors = DoctorAPI.get_all_doctors_name()
    template_data = {
        'doctors': doctors
    }
    return render_template('patient_book.html', **template_data, patient_valid=patient_valid, doctor_valid=doctor_valid, msg=msg)


@app.route('/patients/book/appointment', methods=['GET', 'POST'])
def patient_book_app():
    """
    This function directs the user to the appointment booking page where the patients booking is finalised and placed
    in the primary calendar and the cloud database. It checks the doctors available time slots from the doctors calendar.
    and make appointment booking
    """
    if request.method == 'POST':
        if request.form['patient_book_app_action'] == "submit":
            # add appointment to primary calender and cloud database
            GCalenderAPI.add_appointment()
            AppointmentAPI.add_appointment()
            return redirect(url_for('patients'))
        elif request.form['patient_book_app_action'] == "back":
            return redirect(url_for('patient_book'))
    # get selected doctor's available time slots
    doctor_id = request.args.get('doctor_id')
    patient_id = request.args.get('patient_id')
    doctor = DoctorAPI.get_doctor_by_id(doctor_id)
    appointments = GCalenderAPI.get_appointment_list(
        doctor_email=doctor.email, calender_id=doctor.calender_id)
    template_data = {
        'appointments': appointments,
        'doctor_id': doctor.id,
        'patient_id': patient_id
    }

    return render_template('patient_book_app.html', **template_data)


@app.route('/patients/cancel', methods=['GET', 'POST'])
def patient_cancel():
    """
    This function directs the user to the patient cancel appointment page where the patient can enter their email and then
    redirects them to the cancel/select_appointment page.
    """

    booking_exist = "True"
    msg = ""

    if request.method == 'POST':
        if request.form['patient_cancel_email_action'] == "search":
            # get the selected patient's email
            patient_email = request.form['patient_email']
            patient_booking_exist = GCalenderAPI.get_appointment_list(
                patient_email=patient_email)
            # if there's no booking made, indicate, error message
            if not patient_booking_exist:
                booking_exist = "False"
                msg = "You have not made any bookings yet."
            else:
                return redirect(url_for('patient_cancel_app', patient_email=patient_email))
        elif request.form['patient_cancel_email_action'] == "back":
            return redirect(url_for('patients'))
    return render_template('patient_cancel.html', booking_exist=booking_exist, msg=msg)


@app.route('/patients/cancel/select_appointment', methods=['GET', 'POST'])
def patient_cancel_app():
    """
    This function uses the previously input email from the patients/cancel page to check for all upcoming appointments for the patient and display them
    The selected appointment will be removed from the primary calender.
    """
    if request.method == 'POST':
        if request.form['patient_cancel_app_action'] == "submit":

            util.cancel_booking()
            return redirect(url_for('patients'))

        elif request.form['patient_cancel_app_action'] == "back":
            return redirect(url_for('patient_cancel'))
    # using the input patient email, get all upcoming appointments for that patient
    patient_email = request.args.get('patient_email')
    appointments = GCalenderAPI.get_appointment_list(
        patient_email=patient_email)
    template_data = {
        'appointments': appointments
    }
    return render_template('patient_cancel_app.html', **template_data)


@app.route('/doctors', methods=['POST', 'GET'])
def doctors():
    """
    This function directs the user to the doctors main page.
    """
    return render_template('doctors.html')


@app.route('/doctors/register', methods=['POST', 'GET'])
def doctor_reg():
    """
    This function places the user on the doctor registation page where a doctor and fill out a form in order to submit
    their data to the Doctors table and then create a calendar.
    """
    if request.method == 'POST':
        if request.form['doctor_reg_action'] == "submit":
            calender_id = GCalenderAPI.create_calender(
                request.form['doctor_name'])
            DoctorAPI.add_doctor(calender_id)
            return redirect(url_for('doctors'))
        elif request.form['doctor_reg_action'] == "back":
            return redirect(url_for('doctors'))
    return render_template('doctor_reg.html')


@app.route('/doctors/book', methods=['GET', 'POST'])
def doctor_book_auth():
    """
    This function directs the user to the doctors/book page which allows the doctor to enter their email and then POST's
    the entered email to the book/appointment page.
    """
    if request.method == 'POST':
        if request.form['doctor_book_email_action'] == "search":
            doctor_email = request.form['doctor_email']
            # if DoctorAPI.get_doctor(doctor_email):
            return redirect(url_for('doctor_book', doctor_email=doctor_email))

        elif request.form['doctor_book_email_action'] == "back":

            return redirect(url_for('doctors'))

    return render_template('doctor_book_auth.html')


@app.route('/doctors/book/appointment', methods=['POST', 'GET'])
def doctor_book():
    """
    This function places the user on the doctors/book/appointment page and will get the doctor's email from the POST method in
    the doctors/book page to allow a doctor to add time slots in which they are available to see a patient.
    """
    if request.method == 'POST':
        if request.form['doctor_book_app_action'] == "submit":
            doctor_email = request.form['doctor_email']
            doctor = DoctorAPI.get_doctor_by_email(doctor_email)
            appointments = GCalenderAPI.get_appointment_list(
                doctor_email=doctor.email, calender_id=doctor.calender_id)

            date = request.form['avail_date']
            time = request.form['avail_time']

            # check for AM or PM slot // by every 30 min
            # if slot = AM, program allocate time between 09 - 12
            if time == 'AM':
                ini_time = date + 'T09:00:00'
                for appointment in appointments:
                    appointment_time = appointment['start']['dateTime'].split(
                        '+')[0]
                    # .strftime('%Y-%m-%dT%H:%M:%S')
                    if ini_time == appointment_time:
                        return redirect(url_for('doctor_book'))

                for x in range(1, 7):
                    GCalenderAPI.add_available_time(doctor, ini_time)
                    ini_time = datetime.strptime(ini_time, '%Y-%m-%dT%H:%M:%S')
                    ini_time = ini_time + timedelta(minutes=30)
                    ini_time = ini_time.strftime('%Y-%m-%dT%H:%M:%S')
                return redirect(url_for('index'))

            # if slot = PM, program allocate time between 13 - 17
            if time == 'PM':
                # PM start at 01:00 PM
                ini_time = date + 'T13:00:00'

                for appointment in appointments:
                    appointment_time = appointment['start']['dateTime'].split(
                        '+')[0]
                    # .strftime('%Y-%m-%dT%H:%M:%S')
                    if ini_time == appointment_time:
                        return redirect(url_for('doctor_book'))

                for appointment in appointments:
                    appointment_time = appointment['start']['dateTime'].split(
                        '+')[0]
                    # .strftime('%Y-%m-%dT%H:%M:%S')
                    if ini_time == appointment_time:
                        return redirect(url_for('doctor_book'))

                for x in range(1, 9):
                    GCalenderAPI.add_available_time(doctor, ini_time)
                    ini_time = datetime.strptime(ini_time, '%Y-%m-%dT%H:%M:%S')
                    ini_time = ini_time + timedelta(minutes=30)
                    ini_time = ini_time.strftime('%Y-%m-%dT%H:%M:%S')

                return redirect(url_for('doctors'))

        elif request.form['doctor_book_app_action'] == "back":
            return redirect(url_for('doctor_book_auth'))

    doctor_email = request.args.get('doctor_email')
    # get next 7 days
    days = []
    today = datetime.now().date()
    for x in range(1, 8):
        next_week = today + timedelta(days=x)
        days.append(next_week)

    template_data = {
        'days': days,
        'doctor_email': doctor_email
    }

    return render_template('doctor_book.html', **template_data)


@app.route('/doctors/search', methods=['POST', 'GET'])
def doctor_search():
    """
    This function will place the user on the doctors/search page and will ask the user to enter a patients email which will
    then be posted to the doctors/search/note page.
    """

    if request.method == 'POST':
        if request.form['doctor_search_action'] == "search":
            doctor = util.get_doctor_name_from_form()
            return redirect(url_for('doctor_search_note', doctor_id=doctor.id))
        elif request.form['doctor_search_action'] == "back":
            return redirect(url_for('doctors'))

    doctors = DoctorAPI.get_all_doctors_name()
    template_data = {
        'doctors': doctors
    }
    return render_template('doctor_search.html', **template_data)


@app.route('/doctors/search/note', methods=['POST', 'GET'])
def doctor_search_note():
    """
    This function will place the user on the doctor/search/note page. This page will get the email POSTed by the previous 
    page and then diplay that user's information from the Patient table in the MAPSDB database
    """
    if request.method == 'POST':
        submit_value = request.form['doctor_add_note_action'].split(',')[0]
        if submit_value == "submit":
            # add medical notes to appointment database
            util.add_medical_note()
            return redirect(url_for('doctors'))
        elif submit_value == "back":
            return redirect(url_for('doctor_search'))
        elif submit_value == "record":
            doctor_id = request.form['doctor_add_note_action'].split(',')[1]
            return redirect(url_for('doctor_record', doctor_id=doctor_id))
    # get selected doctor's available time slots
    doctor_id = request.args.get('doctor_id')
    doctor = DoctorAPI.get_doctor_by_id(doctor_id)
    appointments = GCalenderAPI.get_appointment_list(doctor_email=doctor.email)
    medical_note = request.args.get('medical_note')
    if medical_note is None:
        medical_note = ''
    template_data = {
        'appointments': appointments,
        'doctor_id': doctor.id,
        'medical_note': medical_note
    }
    return render_template('doctor_search_note.html', **template_data)

@app.route('/doctors/record', methods=['POST', 'GET'])
def doctor_record():
    """
    This function will place the user on the doctors/record page and will place the user on the doctor_search_note and POSTing the input medical
    note and the doctor_id to the next page.
    """
    if request.method == 'POST':
        submit_value = request.form['doctor_record'].split(',')[0]
        if submit_value == "record":
            # get dictated medical notes using Google assistant 
            medical_note = assistant.main()
            doctor_id = request.form['doctor_record'].split(',')[1]
        return redirect(url_for('doctor_search_note', medical_note=medical_note, doctor_id=doctor_id))
    doctor_id = request.args.get('doctor_id')
    template_data = {
        'doctor_id': doctor_id
    }
    return render_template('doctor_record.html', **template_data)


@app.route('/clerks', methods=['GET'])
def clerks():
    """
    This function places the user on the clerks main page.
    """
    return render_template('clerks.html')


@app.route('/clerks/book', methods=['GET', 'POST'])
def clerk_book():
    """
    This function puts the user on the clerks/book page which allows a clerk to enter their email and 
    select a doctor to book an appointment with.
    """
    patient_valid = True
    doctor_valid = True
    msg = ""

    if request.method == 'POST':
        if request.form['clerk_book_email_action'] == "search":
            doctor, patient = util.get_id_from_form()
            doctor_availability = GCalenderAPI.get_appointment_list(
                doctor_email=doctor.email, calender_id=doctor.calender_id)
            if patient is None:
                patient_valid = "False"
                msg = "The patient has not been registered in the Database."
                # return redirect(url_for('patient_book', error_msg = "The user does not exist.", patient_valid = "False"))
            elif not doctor_availability:
                doctor_valid = "False"
                msg = "The doctor currently does not have any available time slot."
                # return redirect(url_for('patient_book', error_msg = "The doctor does not have available sessions.", doctor_valid = "False"))
            else:
                return redirect(url_for('clerk_book_app', patient_id=patient.id, doctor_id=doctor.id))
            # check for valid patient email
            # return redirect(url_for('clerk_book_app', patient_id=patient.id, doctor_id=doctor.id))
        elif request.form['clerk_book_email_action'] == "back":
            return redirect(url_for('clerks'))

    doctors = DoctorAPI.get_all_doctors_name()
    template_data = {
        'doctors': doctors
    }
    return render_template('clerk_book.html', **template_data, patient_valid=patient_valid, doctor_valid=doctor_valid, msg=msg)


@app.route('/clerks/book/appointment', methods=['GET', 'POST'])
def clerk_book_app():
    """
    This function places the user on the clerks/book/appointment page and allows a clerk to selects from a
    list of appointment slots available for the selected doctor and then make appointment booking with that doctor
    """
    if request.method == 'POST':
        if request.form['clerk_book_app_action'] == "submit":
            # add appointment to primary calender and cloud database
            GCalenderAPI.add_appointment()
            AppointmentAPI.add_appointment()
            return redirect(url_for('clerks'))
        elif request.form['clerk_book_app_action'] == "back":
            return redirect(url_for('clerk_book'))
    # get selected doctor's available time slots
    doctor_id = request.args.get('doctor_id')
    patient_id = request.args.get('patient_id')
    doctor = DoctorAPI.get_doctor_by_id(doctor_id)
    appointments = GCalenderAPI.get_appointment_list(
        doctor_email=doctor.email, calender_id=doctor.calender_id)
    template_data = {
        'appointments': appointments,
        'doctor_id': doctor.id,
        'patient_id': patient_id
    }

    return render_template('clerk_book_app.html', **template_data)


@app.route('/clerks/cancel', methods=['POST', 'GET'])
def clerk_cancel():
    """
    This function places the user on the clerks/cancel page which will check if the booking exists and then cancel it.
    """

    booking_exist = "True"
    msg = ""

    if request.method == 'POST':
        if request.form['clerk_cancel_email_action'] == "search":
            # get the selected patient's email
            patient_email = request.form['patient_email']
            patient_booking_exist = GCalenderAPI.get_appointment_list(
                patient_email=patient_email)
            if not patient_booking_exist:
                booking_exist = "False"
                msg = "The patient has not made any bookings yet."
            else:
                return redirect(url_for('clerk_cancel_app', patient_email=patient_email))
            # return redirect(url_for('clerk_cancel_app', patient_email=patient_email))
        elif request.form['clerk_cancel_email_action'] == "back":
            return redirect(url_for('clerks'))
    return render_template('clerk_cancel.html', booking_exist=booking_exist, msg=msg)


@app.route('/clerks/cancel/select_appointment', methods=['POST', 'GET'])
def clerk_cancel_app():
    """
    This function places the user on the clerks/cancel/select_appointment which allows the clerk to select an appointment
    and cancel it if necessary.
    """
    if request.method == 'POST':
        if request.form['clerk_cancel_app_action'] == "submit":
            util.cancel_booking()
            return redirect(url_for('clerks'))
        elif request.form['clerk_cancel_app_action'] == "back":
            return redirect(url_for('clerks_book'))
    # using the input patient email, get all upcoming appointments for that patient
    patient_email = request.args.get('patient_email')
    appointments = GCalenderAPI.get_appointment_list(
        patient_email=patient_email)
    template_data = {
        'appointments': appointments
    }
    return render_template('clerk_cancel_app.html', **template_data)


@app.route('/clerks/list', methods=['POST', 'GET'])
def clerk_list():
    """
    This function places the user on the clerks/list page which allows a clerk to display a list of doctors.
    """
    if request.method == 'POST':
        if request.form['clerk_doctor_search_action'] == "search":
            doctor_name = request.form['doctor_name']
            return redirect(url_for('clerk_list_app', doctor_name=doctor_name))
        elif request.form['clerk_doctor_search_action'] == "back":
            return redirect(url_for('clerks'))
    doctors = DoctorAPI.get_all_doctors_name()
    template_data = {
        'doctors': doctors
    }
    return render_template('clerk_list.html', **template_data)


@app.route('/clerks/list/appointment', methods=['POST', 'GET'])
def clerk_list_app():
    """
    This function places the user on the clerks/list/appointment page which will display a list of appointments based on
    the doctors name entered in the previous page.
    """
    if request.method == "POST":
        if request.form['clerk_list_app_action'] == "back":
            return redirect(url_for('clerks'))
    doctor_name = request.args.get('doctor_name')
    doctor = DoctorAPI.get_doctor_by_name(doctor_name)
    appointments = GCalenderAPI.get_appointment_list(doctor_email=doctor.email)
    template_data = {
        'appointments': appointments
    }
    return render_template('clerk_list_app.html', **template_data)


@app.route('/clerks/view', methods=['POST', 'GET'])
def clerk_view():
    """
    This function places the user on the clerks/view page which allows a clerk to view a doctor's appointments.
    """
    if request.method == "POST":
        if request.form['clerk_search_action'] == "search":
            doctor = util.get_doctor_name_from_form()
            return redirect(url_for('clerk_view_data', doctor_id=doctor.id))
        elif request.form['clerk_search_action'] == "back":
            return redirect(url_for('clerks'))

    doctors = DoctorAPI.get_all_doctors_name()
    past_app_data = []
    # get number of appointments for each doctor
    for doctor_name in doctors:
        doctor = DoctorAPI.get_doctor_by_name(doctor_name)
        apps = GCalenderAPI.get_past_appointments(doctor_email=doctor.email)
        past_app_data.append(len(apps))
    template_data = {
        'doctors': doctors,
        'pastAppData': past_app_data
    }
    return render_template('clerk_view.html', **template_data)



# This module is only run when it is executed by the interpreter itself
if __name__ == "__main__":
    # At home
    app.run(debug=True, host='0.0.0.0')
    # At university
    app.run(debug=True, host=os.popen('hostname -I').read())
