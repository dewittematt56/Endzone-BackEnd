import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

profile_api = Blueprint("profile_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@profile_api.route('/account/user/profile', methods = ['GET'])
def getProfile(): 
    try:
        db_user = db.session.query(User.ID == current_user.id)
        response = json.dumps({'first_name': current_user.First_Name, 'last_name': current_user.Last_Name, 'email': current_user.Email, 'phone': current_user.Phone})
        return Response(response, 200)
    except Exception as e:
        print(e)
        return Response("Error: Failed to get user profile info", 500)

@login_required
@profile_api.route('/account/user/profile', methods = ['PUT'])
def setProfile():
    if request.method != 'PUT':
        return Response("Error: Incorrect request method", 405)
    data = json.loads(request.get_data())
    user_db = db.session.query(User.ID == current_user.id)

    if 'first_name' in data and 'last_name' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"First_Name": data['first_name'], "Last_Name": data['last_name']})
            db.session.commit()
            return Response("Success: user's name updated", 200)
        except Exception as e:
            print(e)
            return Response("Error: database update failure", 500)
    elif 'email' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Email": data['email']})
            db.session.commit()
            return Response("Success: user's email updated", 200)
        except Exception as e:
            print(e)
            return Response("Error: database update failure", 500)
    elif 'phone' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Phone_Number": data['phone']})
            db.session.commit()
            return Response("Success: user's phone updated", 200)
        except Exception as e:
            print(e)
            return Response("Error: database update failure", 500)
    elif 'squad' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"squad": data['Current_Squad']})
            db.session.commit()
            return Response("Success: user updated", 200)
        except Exception as e:
            print(e)
            return Response("Error: database update failure", 500)
    else:
        return Response("Error: No user fields supplied", 422)
