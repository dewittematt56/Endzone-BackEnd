import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, jsonify, make_response, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

om_members_api = Blueprint("om_members_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@om_members_api.route('/endzone/org/members/info', methods = ['GET'])
def getMembers(): 
    try:
        userOrgMember = db.session.query(Org_Member).filter(Org_Member.User_ID == current_user.id).first()
        if userOrgMember.Role == "Member":
            return make_response("You are not an admin/owner of your current org", 400)
        
        orgMembers = db.session.query(Org_Member).filter(Org_Member.Org_Code == userOrgMember.Org_Code).all()
        membersList = []
        for x in orgMembers:
            member = db.session.query(User).filter(User.ID == x.User_ID).first()
            membersList.append({"id": member.ID, "First_Name": member.First_Name, "Last_Name": member.Last_Name, "Email": member.Email, "Phone_Number": member.Phone_Number, "Creation_Date": member.Creation_Date, "Role": x.Role})

        response = jsonify({"members": membersList})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get org members", 500)


@login_required
@om_members_api.route('/endzone/org/members/update/role', methods = ['PUT'])
def updateRole():
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)

    try:
        userOrgMember = db.session.query(Org_Member).filter(Org_Member.User_ID == current_user.id).first()
        if userOrgMember.Role == "Member" or userOrgMember.Role == "Coach":
            return make_response("You are not an admin/owner of your current org", 400)
        
        data = json.loads(request.get_data())
        print(data['role'])
        if data['role'] == "null":
            return make_response("Error: Please select a valid 'Role' option", 299)
        
        target = db.session.query(Org_Member).filter(Org_Member.Org_Code == userOrgMember.Org_Code, Org_Member.User_ID == data['id']).first()
        if userOrgMember.Role == "Admin":
            if target.Role == "Admin" or target.Role == "Owner":
                return make_response("You cannot make changes to admins or owners", 299)
            else:
                db.session.query(Org_Member).filter(Org_Member.Org_Code == userOrgMember.Org_Code, Org_Member.User_ID == data['id']).update({"Role": data['role']})
                db.session.commit()
        elif userOrgMember.Role == "Owner":
            if target.Role == "Owner":
                return make_response("You cannot make changes to admins or owners", 299)
            else:
                db.session.query(Org_Member).filter(Org_Member.Org_Code == userOrgMember.Org_Code, Org_Member.User_ID == data['id']).update({"Role": data['role']})
                db.session.commit()
        else:
            return make_response("Error", 400)

        return make_response("Success: user's org role has been updated.", 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to update user's org role", 500)
