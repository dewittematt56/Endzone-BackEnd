import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, jsonify, make_response, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

tm_members_api = Blueprint("tm_members_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@tm_members_api.route('/endzone/team/members/info', methods = ['GET'])
def getMembers(): 
    try:
        userTeamMember = db.session.query(Team_Member).filter((Team_Member.Team_Code == current_user.Current_Team) and (Team_Member.Role == "Admin") and (Team_Member.User_ID == current_user.id)).first()
        if userTeamMember == None:
            return make_response("You are not an admin of your current team", 400)
        
        teamMembers = db.session.query(Team_Member).filter(Team_Member.Team_Code == userTeamMember.Team_Code).all()
        membersList = []
        for x in teamMembers:
            member = db.session.query(User).filter(User.ID == x.User_ID).first()
            membersList.append({"id": member.ID, "First_Name": member.First_Name, "Last_Name": member.Last_Name, "Email": member.Email, "Phone_Number": member.Phone_Number, "Role": x.Role, "Creation_Date": member.Creation_Date})

        response = jsonify({"members": membersList})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get team members", 500)
    

@login_required
@tm_members_api.route('/endzone/team/members/update/role', methods = ['PUT'])
def updateRole():
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)
    
    try:
        userTeamMember = db.session.query(Team_Member).filter((Team_Member.Team_Code == current_user.Current_Team) and (Team_Member.Role == "Admin") and (Team_Member.User_ID == current_user.id)).first()
        if userTeamMember == None:
            return make_response("You are not an admin of your current team", 400)
        
        data = json.loads(request.get_data())
        if data['role'] == "null":
            return make_response("Error: Please select a valid 'Role' option", 299)
        
        target = db.session.query(Team_Member).filter(Team_Member.User_ID == data['id']).first()
        oldRole = target.Role

        db.session.query(Team_Member).filter(Team_Member.User_ID == data['id']).update({"Role": data['role']})
        db.session.commit()

        if oldRole == "Admin":
            members = db.session.query(Team_Member).filter(Team_Member.Team_Code == userTeamMember.Team_Code).all()
            status = False
            for x in members:
                if x.Role == "Admin":
                    status = True
                    break

            if status == False:
                db.session.query(Team_Member).filter(Team_Member.User_ID == data['id']).update({"Role": "Admin"})
                db.session.commit()
                return make_response("Error: The team needs at least 1 admin", 299)

        return make_response("Success: user's team role has been updated.", 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to update user's team role", 500)
