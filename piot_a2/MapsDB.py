"""
This file implements basic connection and service functions for the MAPSDB database.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def connect_db(app):
    """
    This function will retrieve cloud database details from another folder and 
    connect to the database
    """
    with open('secretKey/config.json', 'r') as f:
        config = json.load(f)

    USER = config['MAPSDB']['USER']
    PASS = config['MAPSDB']['PASS']
    HOST = config['MAPSDB']['HOST']
    DBNAME = config['MAPSDB']['DBNAME']

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
    USER, PASS, HOST, DBNAME)
    db = SQLAlchemy(app)
    ma = Marshmallow(app)
    return db, ma


def get_service(SCOPES):
    """
    This function does not accept any parameters and will return 
    the service using the token.json and credentials.json files.
    """
    store = file.Storage('secretKey/token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service
