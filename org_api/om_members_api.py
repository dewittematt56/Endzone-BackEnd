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
@om_members_api.route('/endzone/org/members/get', methods = ['GET'])
def getOrgMembers(): 
    try:
        dbTeams = db.session.query(Org_Member).filter((Org_Member.User_ID == current_user.id) and (Org_Member.Role == "Admin" or Org_Member.Role == "Owner")).all()
        if len(dbTeams) == 0:
            return make_response("You are not an admin or owner of any org", 400)

        userOrgMember = dbTeams[0]
        orgMembers = db.session.query(Org_Member).filter(Org_Member.Org_Code == userOrgMember.Org_Code).all()

        membersList = []
        for x in orgMembers:
            temp = db.session.query(User).filter(User.ID == x.User_ID).all()
            member = temp[0]
            membersList.append({"firstName": member.First_Name, "lastName": member.Last_Name, "email": member.Email})

        response = jsonify({"members": membersList})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get org members", 500)
