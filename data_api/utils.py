from database.models import *

def load_game_json(games: "list[Game]"):
    i = 0
    json = []
    for game in games: 
        json.append({
            "id" : i,
            "Home_Team" : game.Home_Team,
            "Away_Team" : game.Away_Team,
            "Game_Date" : game.Game_Date,
            "Game_Type" : game.Game_Type,
            "Creation_Date" : game.Creation_Date,
            "Game_ID" : game.Game_ID
        }) 
        i = i + 1
    return json
