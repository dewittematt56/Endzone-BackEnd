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
        teams = []
        dbTeams = db.session.query(Team_Member).filter(Team_Member.User_ID == current_user.id).all()
        for team in dbTeams:
            team = db.session.query(Team).filter(Team.Team_Code == team.Team_Code).first()
            teams.append(team)
        teamsList = []
        for team in teams:
            teamsList.append({"text": team.Team_Name, "value": team.Team_Code})
        if current_user.Current_Team == None:
            current_user.Current_Team = teams[0].Team_Code
            db.session.query(User).filter(User.ID == current_user.id).update({"Current_Team": teams[0].Team_Code})
            db.session.commit()

        currentTeamObj = db.session.query(Team).filter(Team.Team_Code == User.Current_Team).all()
        currentTeam = currentTeamObj[0].Team_Name
        response = jsonify({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "email": current_user.Email, "phone": current_user.Phone, 
                            "curTeam": currentTeam, "teamsList": teamsList})
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
    elif 'curTeam' in data:
        try:
            db.session.query(User).filter(User.ID == current_user.id).update({"Current_Team": data['curTeam']})
            db.session.commit()
            return make_response("Success: user's current team has been updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'current team' in database.", 500)
    else:
        return make_response("Error: No user fields supplied.", 422)
