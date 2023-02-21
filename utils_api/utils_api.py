from flask import Blueprint, Response, request
from flask_login import login_required, current_user
from database.models import *
from psycopg2 import Binary
import json

utils_api = Blueprint("utils_api", __name__, template_folder="pages", static_folder="pages")

@login_required
@utils_api.route("/getuser", methods = ["GET"])
def getUser():
    return json.dumps({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "Team_Code": current_user.Team_Code})


@utils_api.route("/endzone/utils/formation/add", methods = ["POST"])
def addFormation():
    try:
        params = ["formation", "wideRecievers", "tightEnds", "runningBacks", "image"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 403)
            formation = data["formation"]
            wr = int(data["wideRecievers"])
            te = int(data["tightEnds"])
            rb = int(data["runningBacks"])
            image = bytes(data["image"], "ascii")
            teamCode = current_user.Team_Code
            squadCode = "test"
 
            if len(formation) == 0:
                return Response("Formation needs to include at least one letter or number", status = 404)
            
            if wr > 5:
                return Response("You can have a maximum of 5 wide recievers in a formation",status = 404)
            elif wr < 0:
                return Response("Negative numbers are not allowed",status = 404)
            
            if te > 3:
                return Response("You can have a maximum of 3 tight ends in a formation", status = 404)
            elif te < 0:
                return Response("Negative numbers are not allowed",status = 404)
            
            if rb > 2:
                return Response("A maximum of two running backs are allowed in a formation",status = 404)
            elif rb < 0:
                return Response("Negative numbers are not allowed",status = 404)
            
            new_formation = Formations(formation, wr, te, rb, image, teamCode, squadCode) 
            db.session.add(new_formation)
            db.session.commit() # this is not working
            return "Success"
        
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    

@utils_api.route("/endzone/utils/formation/delete",methods = ["POST"])
def deleteFormation():
    if request.method == "POST":
        data = json.loads(request.get_data())
        id = data["id"]
        

        
        db.session.query(Formations).filter(Formations.ID == id).delete()
        db.session.commit()
        return "test"