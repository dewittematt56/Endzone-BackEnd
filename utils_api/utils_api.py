from flask import Blueprint, Response, request
from flask_login import login_required, current_user
import json
from database.models import *

utils_api = Blueprint("utils_api", __name__, template_folder="pages", static_folder="pages")


@login_required
@utils_api.route("/getuser", methods = ["GET"])
def getUser():
    return json.dumps({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "Team_Code": current_user.Team_Code})



@utils_api.route("/endzone/utils/formation/add", methods = ["POST"])
def addFormation():
    try:
        
        params = ["formation", "wideRecievers", "tightEnds", "runningBacks", "image", "teamCode", "squadCode"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 403)
            
            formation = data["formation"]
            wr = data["wideRecievers"]
            te = data["tightEnds"]
            rb = data["runningBacks"]
            image = data["image"]
            
            teamCode = data["teamCode"]
            
            squadCode = data["squadCode"]
            query = db.session.query(Team).filter(Team.Team_Code == teamCode)
            query_response = query.all()
            
            if len(query_response) == 0:
                return Response("No team is associated with this team code", status = 404)
            
            new_formation = Formations(formation, wr, te, rb, image, teamCode, squadCode) 
            db.session.add(new_formation)
            db.session.commit() # this is not working
            return "Test"
           
            

    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)