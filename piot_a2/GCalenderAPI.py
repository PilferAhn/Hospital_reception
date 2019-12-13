"""
This file includes functionality for using google calendars in the application.
"""

from __future__ import print_function
from datetime import datetime, timedelta
from flask import request
import PatientAPI
import DoctorAPI
import MapsDB

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'
MAX_RESULTS = 50
APPOINTMENT_DURATION = 30

def create_calender(doctor_name):
    """
    Create a secondary calender for a newdoctor that is registered and 
    return the newly created calender id.
    """
    calendar = {
        'summary': doctor_name,
        'timeZone': 'Australia/Melbourne'
    }
    service = MapsDB.get_service(SCOPES)
    new_calendar = service.calendars().insert(body=calendar).execute()
    return new_calendar['id']


def add_appointment(calender_id='primary'):
    """
    This function accepts a calender id in and creates an event 
    to that calendar using a HTML form to get the event information.
    """
    service = MapsDB.get_service(SCOPES)

    summary = request.form['summary']
    app = request.form['app_slot']
    app_id = app.split(',')[0]
    start_datetime = app.split(',')[1]
    end_datetime = app.split(',')[2]
    doctor_id = app.split(',')[3]
    patient_id = app.split(',')[4]
    doctor = DoctorAPI.get_doctor_by_id(doctor_id)
    patient = PatientAPI.get_patient_by_id(patient_id)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Australia/Melbourne',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Australia/Melbourne',
        },
        'attendees': [
            {'displayName': doctor.doctor_name,
             'email': doctor.email
             },
            {'displayName': patient.first_name,
             'email': patient.email
             }
        ],
        'extendedProperties': {
            'private': {
                'doctor_email': doctor.email,
                'patient_email': patient.email
            }
        }}

    event = service.events().insert(calendarId=calender_id, body=event).execute()
    # remove available slot from doctor calendar
    cancel_appointment(app_id, calenderId=doctor.calender_id)


def add_available_time(doctor, start_datetime):
    """
    This function accepts a doctor and start time for an available time slot 
    and adds the time slot to the doctors google calendar.
    """
    service = MapsDB.get_service(SCOPES)

    start = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
    end_datetime = start + timedelta(minutes=APPOINTMENT_DURATION)
    end_datetime = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    event = {
        'summary': 'Open Time Slot',
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Australia/Melbourne',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Australia/Melbourne',
        },
        'attendees': [
            {'displayName': doctor.doctor_name,
             'email': doctor.email
             }
        ],
        'extendedProperties': {
            'private': {
                'doctor_email': doctor.email,
            }
        }}

    event = service.events().insert(calendarId=doctor.calender_id, body=event).execute()


def cancel_appointment(app_id, calenderId='primary'):
    """
    This function accepts an appointment id and a calendar id and 
    will delete the event in the calendar relating to the id provided.
    """
    service = MapsDB.get_service(SCOPES)
    service.events().delete(calendarId=calenderId,
                            eventId=app_id).execute()


def get_appointment_list(doctor_email=None, patient_email=None, calender_id='primary'):
    """
    This function accepts a doctor email, patient email and 
    calendar id an will return the next 20 upcoming calendar events that 
    contain both the doctor and patient email.
    """
    service = MapsDB.get_service(SCOPES)
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = []
    # retrieve appointment details for all appointments
    if doctor_email is None and patient_email is None:
        events_result = service.events().list(calendarId=calender_id, timeMin=now,
                                              maxResults=MAX_RESULTS, singleEvents=True,
                                              orderBy='startTime').execute()
    # retrieve appointment details for specified doctor or patient
    else:
        search_property = 'doctor_email' if doctor_email is not None else 'patient_email'
        search_email = doctor_email if doctor_email is not None else patient_email
        events_result = service.events().list(calendarId=calender_id, timeMin=now,
                                              maxResults=MAX_RESULTS, singleEvents=True,
                                              orderBy='startTime',
                                              privateExtendedProperty=search_property +
                                              ' = ' + search_email).execute()

    events = events_result.get('items', [])
    return events


def get_past_appointments(doctor_email=None, calender_id='primary'):
    """
    get appointments for specified doctor in the primary calendar for the past week
    """
    service = MapsDB.get_service(SCOPES)
    now = datetime.utcnow().isoformat() + 'Z'
    time_now = now.split('.')[0]
    time_now = datetime.strptime(time_now, '%Y-%m-%dT%H:%M:%S')
    last_week = time_now - timedelta(weeks=1)
    last_week = last_week.isoformat() + 'Z'
    events_result = []
    events_result = service.events().list(calendarId=calender_id, timeMin=last_week,
                                          timeMax=now, maxResults=MAX_RESULTS,
                                          singleEvents=True, orderBy='startTime',
                                          privateExtendedProperty='doctor_email = ' 
                                          + doctor_email).execute()

    events = events_result.get('items', [])
    return events


def get_appointment_by_id(app_id):
    """
    This function accepts an appointment id and will 
    delete the appointment that related to the provided id.
    """
    service = MapsDB.get_service(SCOPES)
    event = service.events().get(calendarId='primary', eventId=app_id).execute()
    return event


events = get_past_appointments(doctor_email='liz@mail.com')
for event in events:
    cancel_appointment(event['id'])
