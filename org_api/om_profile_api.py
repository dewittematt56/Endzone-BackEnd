import json

from sqlalchemy import update
from database.db import db, db_uri
from database.models import *
from flask import Flask, jsonify, make_response, request, Response, redirect, Blueprint
from flask_login import current_user
import json
from flask_login import login_required, current_user

om_profile_api = Blueprint("om_profile_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@om_profile_api.route('/endzone/org/profile/info', methods = ['GET'])
def getOrgProfile(): 
    try:
        orgMember = db.session.query(Org_Member).filter(Org_Member.User_ID == current_user.id).first()
        if orgMember.Role == "Member":
            return make_response("You are not an admin of your current Org", 400)

        org = db.session.query(Org).filter(Org.Org_Code == orgMember.Org_Code).first()
     
        teams = db.session.query(Team).filter(Team.Org_Code == org.Org_Code).all()
        teamsList = ""
        for team in teams:
            if teamsList == "":
                teamsList = team.Team_Name
            else:
                teamsList = teamsList + ", " + team.Team_Name

        response = jsonify({"orgName": org.Org_Name, "address": org.Address, "city": org.City, "zip": org.Zip, 
                            "state": org.State, "compLevel": org.Competition_Level, "teamsList": teamsList})
        print({"orgName": org.Org_Name, "address": org.Address, "city": org.City, "zip": org.Zip, 
                            "state": org.State, "compLevel": org.Competition_Level, "teamsList": teamsList})
        return make_response(response, 200)
    except Exception as e:
        print(e)
        return make_response("Error: Failed to get org profile info", 500)

@login_required
@om_profile_api.route('/endzone/org/profile/info/update', methods = ['PUT'])
def setOrgProfile():
    if request.method != 'PUT':
        return make_response("Error: Incorrect request method", 405)
    data = json.loads(request.get_data())

    orgMember = db.session.query(Org_Member).filter(Org_Member.User_ID == current_user.id).first()

    if (orgMember.Role != "Owner") and (orgMember.Role != "Admin"):
        return make_response("You are not an admin or owner of your current team", 400)
    
    org = db.session.query(Org).filter(Org.Org_Code == orgMember.Org_Code).first()

    if 'orgName' in data:
        try:
            db.session.query(Org).filter(Org.Org_Code == org.Org_Code).update({"Org_Name": data['orgName']})
            db.session.commit()
            return make_response("Success: org's name has been updated.", 200)
        except Exception as e:
            return make_response("Error: failed to update 'org name in database.", 500)
    elif 'address' in data and 'city' in data and 'state' in data and 'state' in data and 'zip' in data:
        try:
            db.session.query(Org).filter(Org.Org_Code == org.Org_Code).update({"Address": data['address'], "City": data['city'], "State": data['state'], "Zip": data['zip']})
            db.session.commit()
            return make_response("Success: orgs's address has been updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update the address in database.", 500)
    elif 'compLevel' in data:
        try:
            db.session.query(Org).filter(Org.Org_Code == org.Org_Code).update({"Competition_Level": data["compLevel"]})
            db.session.commit()
            return make_response("Success: orgs's competition level has been updated.", 200)
        except Exception as e:
            print(e)
            return make_response("Error: failed to update 'competition level' in database.", 500)
    else:
        return make_response("Error: No org fields supplied.", 422)
