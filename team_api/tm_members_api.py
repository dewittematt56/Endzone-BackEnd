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
        userTeamMember = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == current_user.id).first()
        if userTeamMember.Role == "Member":
            return make_response("You are not an admin/owner of your current team", 400)
        
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
        userTeamMember = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == current_user.id).first()
        if userTeamMember.Role == "Member" or userTeamMember.Role == "Coach":
            return make_response("You are not an admin/owner of your current team", 400)
        
        data = json.loads(request.get_data())
        print(data)
        if data['role'] == "null":
            return make_response("Error: Please select a valid 'Role' option", 299)
        
        target = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == data['id']).first()
        match userTeamMember.Role:
            case "Admin":
                if target.Role == "Admin" or target.Role == "Owner":
                    return make_response("You cannot make changes to admins or owners", 299)
                else:
                    db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == data['id']).update({"Role": data['role']})
                    db.session.commit()
            case "Owner":
                if target.Role == "Owner":
                    return make_response("You cannot make changes to admins or owners", 299)
                else:
                    db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == data['id']).update({"Role": data['role']})
                    db.session.commit()
            case _:
                return make_response("Error", 400)

        return make_response("Success: user's team role has been updated.", 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to update user's team role", 500)
    

@login_required
@tm_members_api.route('/endzone/team/members/update/role/remove', methods = ['PUT'])
def removeRole():
    print("HI")
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)
    
    try:
        data = json.loads(request.get_data())
        if data['role'] != "Remove":
            return make_response("Error: invalid request", 400)
        
        userTeamMember = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == current_user.id).first()
        if userTeamMember.Role == "Member":
            return make_response("You are not an admin/owner of your current team", 400)
        target = db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == data['id']).first()

        match userTeamMember.Role:
            case "Admin":
                if target.Role == "Admin" or target.Role == "Owner":
                    return make_response("You cannot make changes to admins or owners", 400)
                else:
                    db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == data['id']).delete()
                    db.session.commit()
            case "Owner":
                if target.Role == "Owner":
                    return make_response("You cannot make changes to owners", 400)
                else:
                    db.session.query(Team_Member).filter(Team_Member.Team_Code == current_user.Current_Team, Team_Member.User_ID == data['id']).delete()
                    db.session.commit()
            case _:
                return make_response("Error", 400)


        return make_response("Success: user's team role has been updated.", 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to update user's team role", 500)
