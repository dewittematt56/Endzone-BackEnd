from flask import Blueprint, Response, request
from flask_login import login_required, current_user
import json
from database.models import *
import re

utils_api = Blueprint("utils_api", __name__, template_folder="pages", static_folder="pages")


@login_required
@utils_api.route("/getuser", methods = ["GET"])
def getUser():
    return json.dumps({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "Team_Code": current_user.Team_Code})



def hasNumber(parameter):
    if any(map(str.isdigit, parameter)):
        return True
    else:
        return False
def hasLetter(parameter):
    if any(map(str.isalpha,parameter)):
        return True
    else:
        return False

    
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
        
            if hasLetter(formation) == False and hasNumber(formation) == False:
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
           
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    

@utils_api.route("/endzone/utils/formation/delete",methods = ["POST"])
def deleteFormation():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            id = data["id"]
            

            
            db.session.query(Formations).filter(Formations.ID == id).delete()
            db.session.commit()
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
@utils_api.route("/endzone/utils/formation/update",methods = ["POST"])
def updateFormation():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())

            id = data["id"]
            
            formation = data["Formation"]
            wr = data["wr"]
            te = data["te"]
            rb = data["rb"]
            image = data["image"]
            teamCode = data["teamCode"]
            squadCode = data["squadCode"]
            query = db.session.query(Team).filter(Team.Team_Code == teamCode)
            query_response = query.all()
            
            if len(query_response) == 0:
                return Response("No team is associated with this team code", status = 404)
        
            if hasLetter(formation) == False and hasNumber(formation) == False:
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
            
            db.session.query(Formations).filter(Formations.ID == id).update({"Formation": data['Formation'],"wideRecievers":data["wr"],"tightEnds":data["te"],"runningBacks":data["rb"],"Image":data["image"],
                                                                            "Team_Code":data["teamCode"],"Squad_Code":data["squadCode"]})
            db.session.commit()
    
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
        

    
        
@utils_api.route("/endzone/utils/play/add", methods = ["POST"])
def addPlay():
    try:
        
        params = ["gameID", "playNumber", "possession", "yard", "hash", "down", "distance", "quarter", "dFormation", "oFormation", "formationStrength", "playType", "play",
                  "playTypeDir", "passZone", "coverage", "pressureLeft", "pressureMiddle", "pressureRight", "ballCarrier", "event", "result",
                  "resultX", "resultY", "playX", "playY"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 403)
                
            gameId = data["gameID"]
            playNumber = data["playNumber"]
            possession = data["possession"]
            yard = data["yard"]
            hash = data["hash"]
            down = data["down"]
            distance = data["distance"]
            quarter = data["quarter"]
            dFormation = data["dFormation"]
            oFormation = data["oFormation"]
            formationStrength = data["formationStrength"]
            playType = data["playType"]
            play = data["play"]
            playTypeDir = data["playTypeDir"]
            passZone = data["passZone"]
            coverage = data["coverage"]
            pressureLeft = data["pressureLeft"]
            pressureMiddle = data["pressureMiddle"]
            pressureRight = data["pressureRight"]
            ballCarrier = data["ballCarrier"]
            event = data["event"]
            result = data["result"]
            resultX = data["resultX"]
            resultY = data["resultY"]
            playX = data["playX"]
            playY = data["playY"]

            formationStrengths = ["Left", "Right", "Balanced", "Unknown"]
            playTypes = ["Inside Run", "Outside Run", "Pass", "Boot Pass", "Option", "Unknown"]
            passZones = ["Screen Left", "Screen Right", "Flat Left", "Flat Right", "Middle Left", "Middle Middle", "Middle Right", "Deep Left", "Deep Right"]
            coverages = ["Man 0", "Man 1", "Man 2", "Man 3", "Cover 2", "Cover 3", "Cover 4", "Prevent"]
            events = ["Penalty", "Interception", "Touchdown", "Fumble", "Field Goal", "Safety"]

            if playNumber not in range(0,1000):
                return Response("Play number must be in the range of 0 to 999", status = 404)
            
            if yard not in range(1,101):
                return Response("The yardage must be in range of 1 to 100", status = 404)
            
            if hash != "Left" and hash != "Right" and hash != "Middle":
                return Response("Hash must be either Left, Right, or Middle", status = 404)
            
            if down not in range(1,5):
                return Response("Down must be in range from 1 to 4", status = 404)
            
            if distance not in range(1,101):
                return Response("Distance must be in range from 1 to 100", status = 404)
            
            if quarter not in range(1,6):
                return Response("Quarter must be in range from 1 to 5", status = 404)
            
            if formationStrength not in formationStrengths:
                return Response("Formation Strength must be either Left, Right, Balanced, or Unknown", status = 404)
            
            if playType not in playTypes:
                return Response("Play type must be in list {}".format(playTypes), status = 404)
            
            if playTypeDir != "Left" and playTypeDir != "Right" and playTypeDir != "Unknown":
                return Response("PlayTypeDir must be either Left, Right, or Unknown", status = 404)
            
            if passZone not in passZones:
                return Response("Pass zone must be in list {}".format(passZones), status = 404)
            
            if coverage not in coverages:
                return Response("Coverage must be in list {}".format(coverages),status = 404)
            
            if ballCarrier.isdigit() == False:
                return Response("Ball carrier must be a number from 0,99", status = 404)
            
            if event not in events:
                return Response("Event must be in list {}".format(events))
            
            if result not in range(-99,100):
                return Response("Result must be a number from -99 to 99", status = 404)
            if resultX not in range(1,4):
                return Response("Invalid Geometry", status = 404)
            if resultY not in range(0,11):
                return Response("Invalid Geometry", status = 404)
            if playX not in range(1,4):
                return Response("Invalid Geometry", status = 404)
            if playY not in range(0,11):
                return Response("Invalid Geometry", status = 404)
            

            new_play = plays(gameId, playNumber, possession, yard, hash, down, distance, quarter, dFormation, oFormation, formationStrength,
                             playType, play, playTypeDir, passZone, coverage, pressureLeft, pressureMiddle, pressureRight, ballCarrier, event,
                              result, resultX, resultY, playX, playY ) 
            db.session.add(new_play)
            db.session.commit()
            

    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    


@utils_api.route("/endzone/utils/play/update", methods = ["POST"])
def updatePlay():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())

            id = data["id"]

            gameId = data["gameID"]
            playNumber = data["playNumber"]
            possession = data["possession"]
            yard = data["yard"]
            hash = data["hash"]
            down = data["down"]
            distance = data["distance"]
            quarter = data["quarter"]
            dFormation = data["dFormation"]
            oFormation = data["oFormation"]
            formationStrength = data["formationStrength"]
            playType = data["playType"]
            play = data["play"]
            playTypeDir = data["playTypeDir"]
            passZone = data["passZone"]
            coverage = data["coverage"]
            pressureLeft = data["pressureLeft"]
            pressureMiddle = data["pressureMiddle"]
            pressureRight = data["pressureRight"]
            ballCarrier = data["ballCarrier"]
            event = data["event"]
            result = data["result"]
            resultX = data["resultX"]
            resultY = data["resultY"]
            playX = data["playX"]
            playY = data["playY"]

            formationStrengths = ["Left", "Right", "Balanced", "Unknown"]
            playTypes = ["Inside Run", "Outside Run", "Pass", "Boot Pass", "Option", "Unknown"]
            passZones = ["Screen Left", "Screen Right", "Flat Left", "Flat Right", "Middle Left", "Middle Middle", "Middle Right", "Deep Left", "Deep Right"]
            coverages = ["Man 0", "Man 1", "Man 2", "Man 3", "Cover 2", "Cover 3", "Cover 4", "Prevent"]
            events = ["Penalty", "Interception", "Touchdown", "Fumble", "Field Goal", "Safety"]

            if playNumber not in range(0,1000):
                return Response("Play number must be in the range of 0 to 999", status = 404)
            
            if yard not in range(1,101):
                return Response("The yardage must be in range of 1 to 100", status = 404)
            
            if hash != "Left" and hash != "Right" and hash != "Middle":
                return Response("Hash must be either Left, Right, or Middle", status = 404)
            
            if down not in range(1,5):
                return Response("Down must be in range from 1 to 4", status = 404)
            
            if distance not in range(1,101):
                return Response("Distance must be in range from 1 to 100", status = 404)
            
            if quarter not in range(1,6):
                return Response("Quarter must be in range from 1 to 5", status = 404)
            
            if formationStrength not in formationStrengths:
                return Response("Formation Strength must be either Left, Right, Balanced, or Unknown", status = 404)
            
            if playType not in playTypes:
                return Response("Play type must be in list {}".format(playTypes), status = 404)
            
            if playTypeDir != "Left" and playTypeDir != "Right" and playTypeDir != "Unknown":
                return Response("PlayTypeDir must be either Left, Right, or Unknown", status = 404)
            
            if passZone not in passZones:
                return Response("Pass zone must be in list {}".format(passZones), status = 404)
            
            if coverage not in coverages:
                return Response("Coverage must be in list {}".format(coverages),status = 404)
            
            if ballCarrier.isdigit() == False:
                return Response("Ball carrier must be a number from 0,99", status = 404)
            
            if event not in events:
                return Response("Event must be in list {}".format(events))
            
            if result not in range(-99,100):
                return Response("Result must be a number from -99 to 99", status = 404)
            if resultX not in range(1,4):
                return Response("Invalid Geometry", status = 404)
            if resultY not in range(0,11):
                return Response("Invalid Geometry", status = 404)
            if playX not in range(1,4):
                return Response("Invalid Geometry", status = 404)
            if playY not in range(0,11):
                return Response("Invalid Geometry", status = 404)
        
            db.session.query(plays).filter(plays.ID == id).update({"Game_ID": data['gameID'],"Play_Number":data["playNumber"],"Possession":data["possession"],
                                                                   "Yard":data["yard"],"Hash":data["hash"], "Down":data["down"], "Distance" : data["distance"],
                                                                   "Quarter":data["quarter"], "D_Formation" : data["dFormation"], "O_Formation" : data["oFormation"],
                                                                   "Formation_Strength" : data["formationStrength"], "Play_Type" : data["playType"], "Play" : data["play"],
                                                                   "Play_Type_Dir" : data["playTypeDir"], "Pass_Zone" : data["passZone"], "Coverage" : data["coverage"],
                                                                   "Pressure_Left" : data["pressureLeft"], "Pressure_Middle" : data["pressureMiddle"], "Pressure_Right" : data["pressureRight"],
                                                                   "Ball_Carrier" : data["ballCarrier"], })
            db.session.commit()
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    

@utils_api.route("/endzone/utils/play/delete", methods = ["POST"])
def deletePlay():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            id = data["id"]
            

            
            db.session.query(plays).filter(plays.ID == id).delete()
            db.session.commit()
            return "Teste"
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
