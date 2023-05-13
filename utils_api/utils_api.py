from flask import Blueprint, Response, request, jsonify
from flask_login import login_required, current_user
from database.models import *
import json
from utils_api.utils import *

utils_api = Blueprint("utils_api", __name__, template_folder="pages", static_folder="pages")

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


@login_required
@utils_api.route("/getuser", methods = ["GET"])
def getUser():
    return json.dumps({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "Org_Code": current_user.Org_Code})

@login_required
@utils_api.route("/endzone/utils/formation/add", methods = ["POST"])
def formationAdd():
    try:
        params = ["formation", "wideRecievers", "tightEnds", "runningBacks"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 400)
            formation = data["formation"]
            wr = int(data["wideRecievers"])
            te = int(data["tightEnds"])
            rb = int(data["runningBacks"])
            image = None

            if "image" in data.keys():
                try:
                    image = bytes(data["image"], "ascii")
                except Exception as e:
                    image = None
            else:
                image = None
            if len(formation) == 0:
                return Response("Formation needs to include at least one letter or number", status = 400)

            if wr > 5:
                return Response("You can have a maximum of 5 Wide Recievers in a formation", status = 400)
            elif wr < 0:
                return Response("Negative numbers are not allowed", status = 400)
            if te > 3:
                return Response("You can have a maximum of 3 Tight Ends in a formation", status = 400)
            elif te < 0:
                return Response("Negative numbers are not allowed", status = 400)
            if rb > 3:
                return Response("A maximum of 3 Running Backs are allowed in a formation",status = 400)
            elif rb < 0:
                return Response("Negative numbers are not allowed", status = 400)
            
            new_formation = Formations(formation, wr, te, rb, image) 
            db.session.add(new_formation)
            db.session.commit()            
            return jsonify(load_formation_json([new_formation]))
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

@login_required
@utils_api.route("/endzone/utils/formation/image/<imageId>", methods = ["GET"])
def formationImage(imageId):
    query = db.session.query(Formations).filter(Formations.ID == str(imageId)).all()
    if len(query) == 1:
        if query[0].Image == None:
            return Response("Formation Image Not Found", status=400)
        else:
            return query[0].Image
    else:
        return Response("Formation Image Not Found", status=400)

@login_required
@utils_api.route("/endzone/utils/formation/get", methods = ["GET"])
def getFormation():
    query = db.session.query(Formations).filter(Formations.Org_Code == current_user.Org_Code) .\
        filter(Formations.Team_Code == current_user.Current_Team)
    
    return jsonify(load_formation_json(query.all()))

@login_required
@utils_api.route("/endzone/utils/formation/delete",methods = ["POST"])
def deleteFormation():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            id = data["id"]
            db.session.query(Formations).filter(Formations.ID == id).delete()
            db.session.commit()
            return Response("Successfully deleted")
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
@login_required
@utils_api.route("/endzone/utils/formation/update",methods = ["POST"])
def updateFormation():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())

            id = data["id"]            
            formation = data["formation"]
            wr = data["wideRecievers"]
            te = data["tightEnds"]
            rb = data["runningBacks"]

            if "image" in data.keys():
                try:
                    image = bytes(data["image"], "ascii")
                except Exception as e:
                    image = None
                
            orgCode = current_user.Org_Code

            query = db.session.query(Org).filter(Org.Org_Code == orgCode)
            query_response = query.all()
            
            if len(query_response) == 0:
                return Response("No org is associated with this org code", status = 400)
        
            if hasLetter(formation) == False and hasNumber(formation) == False:
                return Response("Formation needs to include at least one letter or number", status = 400)
            
            if int(wr) > 5:
                return Response("You can have a maximum of 5 wide recievers in a formation",status = 400)
            elif int(wr) < 0:
                return Response("Negative numbers are not allowed", status = 400)
            
            if int(te) > 3:
                return Response("You can have a maximum of 3 tight ends in a formation", status = 400)
            elif int(te) < 0:
                return Response("Negative numbers are not allowed",status = 400)
            
            if int(rb) > 2:
                return Response("A maximum of two running backs are allowed in a formation",status = 400)
            elif int(rb) < 0:
                return Response("Negative numbers are not allowed in a formation",status = 400)
            
            if image:
                db.session.query(Formations).filter(Formations.ID == id).update({"Formation": formation,"Wide_Receivers": wr,"Tight_Ends": te,"Running_Backs": rb,"Image": image})
            else:
                db.session.query(Formations).filter(Formations.ID == id).update({"Formation": formation, "Wide_Receivers": wr,"Tight_Ends": te,"Running_Backs": rb})
            db.session.commit()
            return Response("Successfully Updated " + str(formation))
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
@utils_api.route("/endzone/utils/play/add", methods = ["POST"])
@login_required
def addPlay():
    try:
        params = ["Game_ID", "Play_Number", "Drive", "Possession", "Yard", "Hash", "Down", "Distance", "Quarter", "Motion", "D_Formation", "O_Formation", "Formation_Strength", "Play_Type",
                  "Play_Type_Dir", "Pass_Zone", "Coverage", "Pressure_Left", "Pressure_Middle", "Pressure_Right", "Ball_Carrier", "Event", "Result",
                  "Result_X", "Result_Y", "Play_X", "Play_Y", "Pass_X", "Pass_Y", "Home_Score", "Away_Score"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            print(data)

            # ensure parameters are proper.
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 400)
            
            # Parse request
            gameId = data["Game_ID"]
            playNumber = data["Play_Number"]
            drive = data["Drive"]
            possession = data["Possession"]
            yard = data["Yard"]
            hash = data["Hash"]
            down = data["Down"]
            distance = data["Distance"]
            quarter = data["Quarter"]
            motion = data["Motion"]
            dFormation = data["D_Formation"]
            oFormation = data["O_Formation"]
            formationStrength = data["Formation_Strength"]
            playType = data["Play_Type"]
            homeScore = data["Home_Score"]
            awayScore = data["Away_Score"]
            # To-Do add later
            play = "Unknown"
            playTypeDir = data["Play_Type_Dir"]
            passZone = data["Pass_Zone"]
            coverage = data["Coverage"]
            pressureLeft = data["Pressure_Left"]
            pressureMiddle = data["Pressure_Middle"]
            pressureRight = data["Pressure_Right"]
            ballCarrier = data["Ball_Carrier"]
            event = data["Event"]
            result = data["Result"]
            resultX = data["Result_X"]
            resultY = data["Result_Y"]
            playX = data["Play_X"]
            playY = data["Play_Y"]
            passX = data["Pass_X"]
            passY = data["Pass_Y"]

            # Validation
            formationStrengths = ["Left", "Right", "Balanced", "Unknown"]
            playTypes = ["Inside Run", "Outside Run", "Pass", "Boot Pass", "Option", "Unknown"]
            passZones = ["Flats-Left", "Flats-Right", "Middle-Left", "Middle-Middle", "Middle-Right", "Deep-Left", "Deep-Right", "Unknown", "Non Passing Play", "Not Thrown"]
            coverages = ["Man 0", "Man 1", "Man 2", "Man 3", "Zone 2", "Zone 3", "Zone 4", "Prevent", "Unknown"]
            events = ["Penalty", "Interception", "Touchdown", "Fumble", "Field Goal", "Safety", "None"]

            if int(playNumber) not in range(0,1000):
                return Response("Play number must be in the range of 0 to 999", status = 400)
            
            if int(yard) not in range(1,101):
                return Response("The yardage must be in range of 1 to 100", status = 400)
            
            if hash != "Left" and hash != "Right" and hash != "Middle":
                return Response("Hash must be either Left, Right, or Middle", status = 400)
            
            if int(down) not in range(1,5):
                return Response("Down must be in range from 1 to 4", status = 400)
            
            if int(distance) not in range(1,101):
                return Response("Distance must be in range from 1 to 100", status = 400)
            
            if int(quarter) not in range(1,6):
                return Response("Quarter must be in range from 1 to 5", status = 400)
            
            if formationStrength not in formationStrengths:
                return Response("Formation Strength must be either Left, Right, Balanced, or Unknown", status = 400)
            
            if playType not in playTypes:
                return Response("Play type must be in list {}".format(playTypes), status = 400)
            
            if playTypeDir != "Left" and playTypeDir != "Right" and playTypeDir != "Unknown":
                return Response("PlayTypeDir must be either Left, Right, or Unknown", status = 400)
            
            if passZone not in passZones:
                return Response("Pass zone must be in list {}".format(passZones), status = 400)
            
            if coverage not in coverages:
                return Response("Coverage must be in list {}".format(coverages),status = 400)
            
            if not ballCarrier:
                return Response("Ball carrier needs a number", status = 400)
            
            if event not in events:
                return Response("Event must be in list {}".format(events), status=400)
            # To-Do update later
            if result not in range(-99,100):
                return Response("Result must be a number from -99 to 99", status = 400)
            
            if int(homeScore) < 0 or int(awayScore) < 0:
                return Response("Scores must be positive integers", status = 400)
            
            # Add to Database
            new_play = Play(gameId, playNumber, drive, possession, yard, hash, down, distance, quarter, motion, dFormation, oFormation, formationStrength, homeScore, awayScore,
                             playType, play, playTypeDir, passZone, coverage, pressureLeft, pressureMiddle, pressureRight, ballCarrier, event,
                              result, resultX, resultY, playX, playY, passX, passY) 

            db.session.add(new_play)
            db.session.commit()
            return Response("Successfully created Play")
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

@login_required
@utils_api.route("/endzone/utils/play/update", methods = ["POST"])
def updatePlay():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())

            # Get Data
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

            # Validation Fields

            #To-Do make global variables so only have to be defined once.
            formationStrengths = ["Left", "Right", "Balanced", "Unknown"]
            playTypes = ["Inside Run", "Outside Run", "Pass", "Boot Pass", "Option", "Unknown"]
            passZones = ["Screen Left", "Screen Right", "Flat Left", "Flat Right", "Middle Left", "Middle Middle", "Middle Right", "Deep Left", "Deep Right"]
            coverages = ["Man 0", "Man 1", "Man 2", "Man 3", "Cover 2", "Cover 3", "Cover 4", "Prevent"]
            events = ["Penalty", "Interception", "Touchdown", "Fumble", "Field Goal", "Safety"]
            
            # To - Do Write as Function to match with Play-Add Code
            if playNumber not in range(0,1000):
                return Response("Play number must be in the range of 0 to 999", status = 400)
            
            if yard not in range(1,101):
                return Response("The yardage must be in range of 1 to 100", status = 400)
            
            if hash != "Left" and hash != "Right" and hash != "Middle":
                return Response("Hash must be either Left, Right, or Middle", status = 400)
            
            if down not in range(1,5):
                return Response("Down must be in range from 1 to 4", status = 400)
            
            if distance not in range(1,101):
                return Response("Distance must be in range from 1 to 100", status = 400)
            
            # if quarter not in range(1,6):
            #     return Response("Quarter must be in range from 1 to 5", status = 400)
            
            if formationStrength not in formationStrengths:
                return Response("Formation Strength must be either Left, Right, Balanced, or Unknown", status = 400)
            
            if playType not in playTypes:
                return Response("Play type must be in list {}".format(playTypes), status = 400)
            
            if playTypeDir != "Left" and playTypeDir != "Right" and playTypeDir != "Unknown":
                return Response("PlayTypeDir must be either Left, Right, or Unknown", status = 400)
            
            if passZone not in passZones:
                return Response("Pass zone must be in list {}".format(passZones), status = 400)
            
            if coverage not in coverages:
                return Response("Coverage must be in list {}".format(coverages),status = 400)
            
            if ballCarrier.isdigit() == False:
                return Response("Ball carrier must be a number from 0,99", status = 400)
            
            if event not in events:
                return Response("Event must be in list {}".format(events))
            
            if result not in range(-99,100):
                return Response("Result must be a number from -99 to 99", status = 400)
            if resultX not in range(1,4):
                return Response("Invalid Geometry", status = 400)
            if resultY not in range(0,11):
                return Response("Invalid Geometry", status = 400)
            if playX not in range(1,4):
                return Response("Invalid Geometry", status = 400)
            if playY not in range(0,11):
                return Response("Invalid Geometry", status = 400)
        
            db.session.query(Play).filter(Play.ID == id).update({"Game_ID": data['gameID'],"Play_Number":data["playNumber"],"Possession":data["possession"],
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

@login_required
@utils_api.route("/endzone/utils/play/delete", methods = ["POST"])
def deletePlay():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            id = data["id"]
            db.session.query(Play).filter(Play.ID == id).delete()
            db.session.commit()
            return "Successfully deleted play number: {0}".format(str(id))
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
@login_required
@utils_api.route("/endzone/utils/play/get", methods = ["GET"])
def getPlay():
    if request.method == "GET":
        game_id = request.args.get("gameId")
        print(game_id)
    query = db.session.query(Play, Game).filter(Play.Game_ID == game_id).join(Game, Game.Game_ID == Play.Game_ID).order_by(desc(Play.Play_Number))
    print(query.all())
    return jsonify(load_play_json(query.all()))