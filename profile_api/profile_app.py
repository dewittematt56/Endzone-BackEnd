import json
from database.db import db, db_uri
from database.models import *

def handle(user, db): 
    try:
        db_user = db.session.query(User.ID == user.id)
        first_name = db_user.get_first_name()
        last_name = db_user.get_last_name()
        email = db_user.get_email()
        phone = db_user.get_phone()
        squads = db_user.get_squads() # squads isn't in db yet
        response = json.loads({'first_name': first_name, 'last_name': last_name, 'email': email, 'phone': phone, 'squads': squads})
        return response
    except Exception as e:
        print(e)