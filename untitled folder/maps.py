#!/usr/bin/env python3

import os
from flask import Flask, request, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
import GCalenderAPI
import PatientAPI
import DoctorAPI
import datetime as dt
import Utilities as util

# Get prepared for flask (a web framework) and bootstrap
app = Flask(__name__, static_url_path='/static')
bootstrap = Bootstrap(app)

# define cloud database details
USER = 'root'
PASS = ''
HOST = '35.189.1.72'
DBNAME = 'mapsdb'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    USER, PASS, HOST, DBNAME)
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Route pages based on purposes
user_not_exist = "The user does not exist in the database. Please try again."
doctor_not_available = "The doctor you have selected currently does not have available sessions."
no_booking_found = "You have not made any bookings yet."

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/patients', methods=['GET', 'POST'])
def patients():
    return render_template('patients.html')


@app.route('/patients/register', methods=['GET', 'POST'])
def patient_reg():
    """
    patient registration page
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
    patient enters their email and select a doctor to book appointment with
    """
    patient_valid = True
    doctor_valid = True
    msg = ""
    if request.method == 'POST':
        if request.form['patient_book_email_action'] == "search":
            doctor, patient = util.get_id_from_form()
            doctor_availability = GCalenderAPI.get_appointment_list(doctor_email = doctor.email, calender_id = doctor.calender_id)
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
    return render_template('patient_book.html', **template_data, patient_valid = patient_valid, doctor_valid = doctor_valid, msg = msg)


@app.route('/patients/book/appointment', methods=['GET', 'POST'])
def patient_book_app():
    """
    patient selects from list of appointment slots available for selected doctor
    and make appointment booking
    """
    if request.method == 'POST':
        if request.form['patient_book_app_action'] == "submit":
            # add appointment to primary calender
            GCalenderAPI.add_appointment()
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
    Patient cancel appointment page
    gets the patient's email from input box to know which patient 
    is cancelling appointment and redirect to appointment cancel page
    """

    booking_exist = "True"
    msg = ""

    if request.method == 'POST':
        if request.form['patient_cancel_email_action'] == "search":
            # get the selected patient's email
            patient_email = request.form['patient_email']
            # doctor, patient = util.get_id_from_form()
            patient_booking_exist = GCalenderAPI.get_appointment_list(patient_email = patient_email)
            print(patient_booking_exist)
            # if there's no booking made, indicate, error message
            if not patient_booking_exist:
                booking_exist = "False"
                msg = "You have not made any bookings yet."
            else:
                return redirect(url_for('patient_cancel_app', patient_email = patient_email))
        elif request.form['patient_cancel_email_action'] == "back":
            return redirect(url_for('patients'))
    return render_template('patient_cancel.html', booking_exist = booking_exist, msg = msg)


@app.route('/patients/cancel/select_appointment', methods=['GET', 'POST'])
def patient_cancel_app():
    """
    using the previously obtained patient email, 
    check for all upcoming appointments for the patient and display them
    selected appointment will be removed from primary calender
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
    return render_template('doctors.html')


@app.route('/doctors/register', methods=['POST', 'GET'])
def doctor_reg():
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
    if request.method == 'POST':
        if request.form['doctor_book_email_action'] == "search":

            #doctor_email = request.form['doctor_email']
            # if DoctorAPI.get_doctor(doctor_email):
            return redirect(url_for('doctor_book'))

        elif request.form['doctor_book_email_action'] == "back":

            return redirect(url_for('doctors'))

    return render_template('doctor_book_auth.html')


@app.route('/doctors/book/appointment', methods=['POST', 'GET'])
def doctor_book():
    if request.method == 'POST':
        if request.form['doctor_book_app_action'] == "submit":

            email = request.form['doctor_email']
            date = request.form['avail_date']
            time = request.form['avail_time']

            doctor = DoctorAPI.get_doctor_by_email(email)

            # check for AM or PM slot
            # if slot = AM, program allocate time between 09 - 12 
            # if slot = PM, program allocate time between 13 - 17 
            # by every 30 min
            if time == 'AM':
                ini_time = date + 'T09:00:00'
                
                for x in range(1,7):
                    GCalenderAPI.add_available_time(doctor, ini_time)
                    ini_time = datetime.strptime(ini_time, '%Y-%m-%dT%H:%M:%S')
                    ini_time = ini_time + timedelta(minutes=30)
                    ini_time = ini_time.strftime('%Y-%m-%dT%H:%M:%S')

            if time == 'PM':
                #PM start at 01:00 PM
                ini_time = date + 'T13:00:00'

                for x in range(1,9):
                    GCalenderAPI.add_available_time(doctor, ini_time)
                    ini_time = datetime.strptime(ini_time, '%Y-%m-%dT%H:%M:%S')
                    ini_time = ini_time + timedelta(minutes=30)
                    ini_time = ini_time.strftime('%Y-%m-%dT%H:%M:%S')

            return redirect(url_for('doctors'))

        elif request.form['doctor_book_app_action'] == "back":

            return redirect(url_for('doctor_book_auth'))

    days = []
    today = dt.date.today()
    for x in range(1, 8):

        next_week = today + dt.timedelta(days=x)
        days.append(next_week)

    template_data = {
        'days': days,
    }

    return render_template('doctor_book.html', **template_data)


@app.route('/doctors/search_patient', methods=['POST', 'GET'])
def doctor_search():
    if request.method == 'POST':
        if request.form['doctor_search_action'] == "search":
            PatientAPI.get_patient_data()
            return redirect(url_for('doctor_search_note'))
        elif request.form['doctor_search_action'] == "back":
            return redirect(url_for('doctors'))
    return render_template('doctor_search.html')


@app.route('/doctors/search_patient/note', methods=['POST', 'GET'])
def doctor_search_note():
    if request.method == 'POST':
        if request.form['doctor_add_note_action'] == "submit":
            patient_info = PatientAPI.display_patient_data()
            email = patient_info[0]
            first_name = patient_info[1]
            last_name = patient_info[2]
            mobile_num = patient_info[3]
            gender = patient_info[4]
            dob = patient_info[5]
            medical_history = patient_info[6]

            return redirect(url_for('doctors'))
        elif request.form['doctor_add_note_action'] == "back":
            return redirect(url_for('doctor_search'))
    return render_template('doctor_search_note.html', email=email)

@app.route('/clerks', methods=['GET'])
def clerks():
    return render_template('clerks.html')


@app.route('/clerks/book', methods=['GET', 'POST'])
def clerk_book():
    """
    clerk enters their email and select a doctor to book appointment with
    """
    patient_valid = True
    doctor_valid = True
    msg = ""

    if request.method == 'POST':
        if request.form['clerk_book_email_action'] == "search":

            #get doctor and patient -- Name
            doctor, patient = util.get_id_from_form()
            
            doctor_availability = GCalenderAPI.get_appointment_list(doctor_email = doctor.email, calender_id = doctor.calender_id)
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
    return render_template('clerk_book.html', **template_data, patient_valid = patient_valid, doctor_valid = doctor_valid, msg = msg)

@app.route('/clerks/book/appointment', methods=['GET', 'POST'])
def clerk_book_app():
    """
    clerk selects from list of appointment slots available for selected doctor
    and make appointment booking
    """
    if request.method == 'POST':
        if request.form['clerk_book_app_action'] == "submit":
            # add appointment to primary calender
            GCalenderAPI.add_appointment()
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

    booking_exist = "True"
    msg = ""

    if request.method == 'POST':
        if request.form['clerk_cancel_email_action'] == "search":
            # get the selected patient's email
            patient_email = request.form['patient_email']
            patient_booking_exist = GCalenderAPI.get_appointment_list(patient_email = patient_email)
            if not patient_booking_exist:
                booking_exist = "False"
                msg = "The patient has not made any bookings yet."
            else:
                return redirect(url_for('clerk_cancel_app', patient_email = patient_email))
            # return redirect(url_for('clerk_cancel_app', patient_email=patient_email))
        elif request.form['clerk_cancel_email_action'] == "back":
            return redirect(url_for('clerks'))
    return render_template('clerk_cancel.html', booking_exist = booking_exist, msg = msg)

@app.route('/clerks/cancel/select_appointment', methods=['POST', 'GET'])
def clerk_cancel_app():
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
    if request.method == 'POST':
        return redirect(url_for('clerks'))
    return render_template('clerk_list.html')



# This module is only run when it is executed by the interpreter itself
if __name__ == "__main__":
    # At home
    app.run(debug=True, host='0.0.0.0')
    # At university
    app.run(debug=True, host=os.popen('hostname -I').read())
