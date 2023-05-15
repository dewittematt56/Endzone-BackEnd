from flask import Blueprint, Response, request, jsonify, render_template
from flask_login import login_required
from database.models import *
import json

data_api = Blueprint("data_api", __name__)

@login_required
@data_api.route("/endzone/data/game/create", methods = ["POST"])
def gameCreate():
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())

            params = ["home_team", "away_team", "game_date", "game_type"]
            for param in params:
                if param not in data.keys():
                    return Response('Please Provide a ' + param, status = 400)
            
            
            home_team = data["home_team"]
            away_team = data["away_team"]
            if len(home_team) >= 36 or len(away_team) >= 36:
                return Response('A Home or Away team must be less than 36 characters.' + param, status = 400)
            
            try:
                game_date = data["game_date"]
                game_date = datetime.datetime.strptime(game_date, '%m/%d/%Y')
            except Exception as e:
                return Response(str(e) + param, status = 500)
            
            game_type = data["game_type"]
            if game_type not in ["ai", "manual"]:
                return Response("Not a valid game type, must be 'AI' or  'Manual'", status = 400)

            new_game = Game(home_team, away_team, game_date, game_type) 
            db.session.add(new_game)
            db.session.commit()
            return new_game.Game_ID
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
