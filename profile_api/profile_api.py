import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, jsonify, make_response, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

profile_api = Blueprint("profile_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@profile_api.route('/endzone/account/user/profile', methods = ['GET'])
def getProfile(): 
    try:
        squads = []
        dbSquads = db.session.query(Squad_Member).filter(Squad_Member.User_ID == current_user.id).all()
        print(dbSquads[0])
        for squad in dbSquads:
            squadName = db.session.query(Squad).filter(Squad.Squad_Code == squad.Squad_Code).first().Squad_Name
            squads.append(squadName)
            
        squadsList = []
        for squad in squads:
            squadsList.append({"text": squad, "value": squad})

        if current_user.Current_Squad == None:
            current_user.Current_Squad = squads[0]
            db.session.query(User).filter(User.ID == current_user.id).update({"Current_Squad": squads[0]})
            db.session.commit()


        response = jsonify({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "email": current_user.Email, "phone": current_user.Phone, 
                            "squads": squads, "curSquad": current_user.Current_Squad, "squadsList": squadsList})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get user profile info", 500)

@login_required
@profile_api.route('/endzone/account/user/profile/update', methods = ['PUT'])
def setProfile():
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)
    data = json.loads(request.get_data())
    print(data)
    user_db = db.session.query(User.ID == current_user.id)

    if 'first_name' in data and 'last_name' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"First_Name": data['first_name'], "Last_Name": data['last_name']})
            db.session.commit()
            return make_response("Success: user's name updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'first name' and/or 'last name' in database.", 500)
    elif 'email' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Email": data['email']})
            db.session.commit()
            return make_response("Success: user's email updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'email' in database.", 500)
    elif 'phone' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Phone_Number": data['phone']})
            db.session.commit()
            return make_response("Success: user's phone updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'phone' in database.", 500)
    elif 'curSquad' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Current_Squad": data['curSquad']})
            db.session.commit()
            return make_response("Success: user updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'current squad' in database.", 500)
    else:
        return make_response("Error: No user fields supplied.", 422)
