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
        params = ["Formation", "WideRecievers", "TightEnds", "RunningBacks"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 400)
            formation = data["Formation"]
            wr = int(data["WideRecievers"])
            te = int(data["TightEnds"])
            rb = int(data["RunningBacks"])
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
            db.session.commit() # this is not working
            return "Success"
        
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

@login_required
@utils_api.route("/endzone/utils/formation/image/<imageId>", methods = ["GET"])
def formationImage(imageId):
    query = db.session.query(Formations).filter(Formations.ID == str(imageId)).all()
    if len(query) == 1:
        if query[0].Image == None:
            return Response("Formation Image Not Found", status=404)
        else:
            return query[0].Image
    else:
        return Response("Formation Image Not Found", status=404)

@login_required
@utils_api.route("/endzone/utils/formation/get", methods = ["GET"])
def getFormation():
    query = db.session.query(Formations).filter(Formations.Org_Code == current_user.Org_Code) .\
        filter(Formations.Team_Code == current_user.Team_Code)
    
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
                db.session.query(Formations).filter(Formations.ID == id).update({"Formation": formation,"wideRecievers": wr,"tightEnds": te,"runningBacks": rb,"Image": image})
            else:
                db.session.query(Formations).filter(Formations.ID == id).update({"Formation": formation, "wideRecievers": wr,"tightEnds": te,"runningBacks": rb})
            db.session.commit()
    
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
            # if resultX not in range(0,5):
            #     return Response("Invalid Geometry", status = 404)
            # if resultY not in range(0, 5):
            #     return Response("Invalid Geometry", status = 404)
            # if playX not in range(0,5):
            #     return Response("Invalid Geometry", status = 404)
            # if playY not in range(0,5):
            #     return Response("Invalid Geometry", status = 404)
            
            # Add to Database
            new_play = Play(gameId, playNumber, drive, possession, yard, hash, down, distance, quarter, motion, dFormation, oFormation, formationStrength, homeScore, awayScore,
                             playType, play, playTypeDir, passZone, coverage, pressureLeft, pressureMiddle, pressureRight, ballCarrier, event,
                              result, resultX, resultY, playX, playY, passX, passY) 
            print(new_play)
            db.session.add(new_play)
            db.session.commit()
            return Response("Successfully created Play")
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
        if request.args.get("gameId"): # Heres the changes I made for the data viewer bug
            game_id = request.args.get("gameId") # and here
            query = db.session.query(Play, Game).filter(Play.Game_ID == game_id).join(Game, Game.Game_ID == Play.Game_ID).order_by(desc(Play.Play_Number))
        else:
            query = db.session.query(Play, Game).join(Game, Game.Game_ID == Play.Game_ID).order_by(desc(Play.Play_Number))
    print(query.all())
    return jsonify(load_play_json(query.all()))

@login_required
@utils_api.route("/endzone/utils/play/update", methods = ['POST'])
def updateViewer():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            id = data["id"]
            column = data["column"]
            value = data["value"]
            if "Pressure" in column:
                value = str(value).lower().strip() == "true"
            play = db.session.query(Play).filter(Play.ID == id).first()
            if play:
                setattr(play, column, value)
                db.session.commit()
                return Response("Successfully updated {}".format(id), status = 200)
            else:
                return Response("Error Code 500: That play does not exist", status = 500)
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
        
        