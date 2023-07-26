from flask import Blueprint, Response, request, jsonify, current_app
from flask_login import login_required, current_user
from database.models import *
import json
from utils_api.utils import *
from server_utils import check_required_params, validate_play_input

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
        if request.method == "POST":
            data = json.loads(request.get_data())
            param_check = check_required_params(["formation", "wideRecievers", "tightEnds", "runningBacks"], data.keys())
            if param_check: return param_check
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
            
            if len(db.session.query(Formations).filter(Formations.Org_Code == current_user.Org_Code) .\
                filter(Formations.Formation == formation).all()) > 0:
                return Response("A formation with that name already exists.", status = 400)
            
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
        filter(Formations.Team_Code == current_user.Current_Team).order_by(asc(Formations.Formation))
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
        if request.method == "POST":
            data = json.loads(request.get_data())
            # ensure parameters are proper.
            param_check = check_required_params(["Game_ID", "Play_Number", "Drive", "Possession", "Yard", "Hash", "Down", "Distance", "Quarter", "Motion", "D_Formation", "O_Formation", "Formation_Strength", "Play_Type",
                  "Play_Type_Dir", "Pass_Zone", "Coverage", "Pressure_Left", "Pressure_Middle", "Pressure_Right", "Ball_Carrier", "Event", "Result",
                  "Result_X", "Result_Y", "Play_X", "Play_Y", "Pass_X", "Pass_Y", "Home_Score", "Away_Score"], data.keys())
            if param_check: return param_check
            validation_check = validate_play_input(data)
            if validation_check: return validation_check
            
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
            # Add to Database
            new_play = Play(gameId, playNumber, drive, possession, yard, hash, down, distance, quarter, motion, dFormation, oFormation, formationStrength, homeScore, awayScore,
                             playType, play, playTypeDir, passZone, coverage, pressureLeft, pressureMiddle, pressureRight, ballCarrier, event,
                              result, resultX, resultY, playX, playY, passX, passY) 

            db.session.add(new_play)
            db.session.commit()
            return jsonify(load_one_play(new_play))
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
    temp = current_app.config["message_queue"]
    current_app.config["message_queue"] = 'luffy'
    
    if request.method == "GET":
        if request.args.get("gameId"): # Heres the changes I made for the data viewer bug
            game_ids = request.args.get("gameId") # and here
            if "," in game_ids:
                game_ids = game_ids.split(",")
                query = db.session.query(Play, Game).filter(Play.Game_ID.in_(game_ids)).join(Game, Game.Game_ID == Play.Game_ID).filter(Game.Team_Code == current_user.Current_Team).order_by(desc(Play.Play_Number))
            else:
                game_id = game_ids
                query = db.session.query(Play, Game).filter(Play.Game_ID == game_id).join(Game, Game.Game_ID == Play.Game_ID).filter(Game.Team_Code == current_user.Current_Team).order_by(desc(Play.Play_Number))
        else:
            query = db.session.query(Play, Game).join(Game, Game.Game_ID == Play.Game_ID).filter(Game.Team_Code == current_user.Current_Team).order_by(desc(Play.Play_Number))
    return jsonify(load_play_json(query.all()))

@login_required
@utils_api.route("/endzone/utils/penalty/add", methods = ["POST"])
def addPenalty():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            param_check = check_required_params(["game_id", "penalty_name", "offending_team", "offending_player", "penalty_yards"], data.keys())
            if param_check: 
                return param_check
            else:
                play_number = str(data["play_number"])
                game_id = str(data["game_id"])
                penalty_name = str(data["penalty_name"])
                side_of_ball = str(data["side_of_ball"])
                offending_team = str(data["offending_team"])
                offending_player = str(data["offending_player"])
                penalty_yards = int(data["penalty_yards"])
                new_penalty = Penalty(play_number, game_id, penalty_name, side_of_ball, offending_team, offending_player, penalty_yards) 
                db.session.add(new_penalty)
                db.session.commit()       
                return Response("Penalty Added", status = 200)   
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
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
        
        
