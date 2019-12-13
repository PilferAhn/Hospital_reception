from __future__ import print_function
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from flask import request
import dateutil.parser
import PatientAPI
import DoctorAPI

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'
MAX_RESULTS = 50
APPOINTMENT_DURATION = 30

def get_service():
    """
    get Google calender API service
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


def create_calender(doctor_name):
    """
    create a secondary calender for a newdoctor that is registered and 
    return the newly created calender id
    """
    calendar = {
        'summary': doctor_name,
        'timeZone': 'Australia/Melbourne'
    }
    service = get_service()
    new_calendar = service.calendars().insert(body=calendar).execute()
    return new_calendar['id']


def add_appointment(calender_id='primary'):
    """
    add an appointment to the calender 
    """
    service = get_service()

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
    add available time slot to doctor schedule
    """
    service = get_service()

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

# doctor = DoctorAPI.get_doctor_by_id(2)
# add_available_time(doctor, '2018-09-28T10:00:00')

def cancel_appointment(app_id, calenderId='primary'):
    """
    delete specified calender event
    """
    service = get_service()
    # when event is successfully deleted, empty response is returned
    service.events().delete(calendarId=calenderId,
                            eventId=app_id).execute()
    


def get_appointment_list(doctor_email=None, patient_email=None, calender_id='primary'):
    """
    get upcoming 20 calender events based on doctor email or patient email
    """
    service = get_service()
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = []
    # retrieve appointment details for all apointments
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
    # if not events:
    #     print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     end = event['end'].get('dateTime', event['end'].get('date'))
    #     start_time = dateutil.parser.parse(event['start']['dateTime']).strftime("%Y-%m-%dT%H:%M:%S")
    #     print(start_time, event['summary'])

def get_appointment_by_id(app_id):
    service = get_service()
    event = service.events().get(calendarId='primary', eventId=app_id).execute()
    return event

# add_appointment('liz@mail.com', 'mail@mail.com')

# app = get_appointment_list(patient_email='mail@mail')
# for appo in app:
#     print(appo['start']['dateTime'])
# cancel_appointment()
"""
events = get_appointment_list(patient_email='lucy@mail') get list of event patient is attending
delete_appointment(events[0]['id']) to delete single event returned
"""
