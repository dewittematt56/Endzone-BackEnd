import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, jsonify, make_response, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

tm_profile_api = Blueprint("tm_profile_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@tm_profile_api.route('/endzone/team/profile/info', methods = ['GET'])
def getTeamProfile(): 
    try:
        teamMember = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == current_user.id).first()
        if teamMember.Role == "Member":
            return make_response("You are not an admin of your current team", 400)
        
        team = db.session.query(Team).filter(Team.Team_Code == teamMember.Team_Code).first()

        org = db.session.query(Org).filter(Org.Org_Code == team.Org_Code).first()

        response = jsonify({"teamName": team.Team_Name, "orgName": org.Org_Name})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get team profile info", 500)

@login_required
@tm_profile_api.route('/endzone/team/profile/info/update', methods = ['PUT'])
def setTeamProfile():
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)
    data = json.loads(request.get_data())

    try:
        teamMember = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == current_user.id).first()
        if teamMember.Role != "Owner" and teamMember.Role != "Admin":
            return make_response("You are not an admin or owner of your current team", 400)
        
        if 'teamName' in data:
            db.session.query(Team).filter(Team.Team_Code == teamMember.Team_Code).update({"Team_Name": data['teamName']})
            db.session.commit()
            return make_response("Success: teams's name has been updated.", 200)
        else:
            return make_response("Error: No team fields supplied.", 422)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to update team profile info", 500)
