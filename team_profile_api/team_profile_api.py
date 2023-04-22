import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, jsonify, make_response, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

team_profile_api = Blueprint("team_profile_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@team_profile_api.route('/endzone/team/profile/info', methods = ['GET'])
def getTeamProfile(): 
    try:
        dbSquads = db.session.query(Team_Member).filter((Team_Member.User_ID == current_user.id) and (Team_Member.Role == "Admin" or Team_Member.Role == "Owner")).all()
        if len(dbSquads) == 0:
            return make_response("You are not an admin or owner of any team", 400)
            
        team_member = dbSquads[0]
        team = db.session.query(Team).filter(Team.Team_Code == team_member.Team_Code).all()


        squads = db.session.query(Squad).filter(Squad.Team_Code == team.Team_Code).all()
        squadsList = []
        for squad in squads:
            squadsList.append({"text": squad, "value": squad})

        response = jsonify({"teamName": team.Team_Name, "address": team.Address, "city": team.City, "zip": team.Zip, 
                            "state": team.State, "compLevel": team.Competition_Level, "squadsList": squadsList})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get user profile info", 500)

@login_required
@team_profile_api.route('/endzone/team/profile/info/update', methods = ['PUT'])
def setTeamProfile():
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)
    data = json.loads(request.get_data())

    if 'first_name' in data and 'last_name' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"First_Name": data['first_name'], "Last_Name": data['last_name']})
            db.session.commit()
            return make_response("Success: user's name has been updated.", 200)
        except Exception as e:
            return make_response("Error: failed to update 'first name' and/or 'last name' in database.", 500)
    elif 'email' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Email": data['email']})
            db.session.commit()
            return make_response("Success: user's email has been updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'email' in database.", 500)
    elif 'phone' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Phone_Number": data['phone']})
            db.session.commit()
            return make_response("Success: user's phone number has been updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'phone' in database.", 500)
    elif 'curSquad' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Current_Squad": data['curSquad']})
            db.session.commit()
            return make_response("Success: user's current squad has been updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'current squad' in database.", 500)
    else:
        return make_response("Error: No user fields supplied.", 422)
