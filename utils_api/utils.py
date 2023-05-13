from database.models import *
from sqlalchemy import *

def load_formation_json(formations: "list[Formations]") -> "list[dict]":
        json = []
        for formation in formations:
            json.append({
                "id": formation.ID,
                "Formation": formation.Formation,
                "RunningBacks": formation.Running_Backs,
                "TightEnds": formation.Tight_Ends,
                "WideReceivers": formation.Wide_Receivers
            })
        return json
    
def load_play_json(plays: "list[Play]") -> "list[dict]":
        json = []
        for play in plays:
            print(play)
            json.append({
                "id": play.Play.ID,
                "Game_ID": play.Play.Game_ID,
                "Play_Number": play.Play.Play_Number,
                "Drive": play.Play.Drive,
                "Possession": play.Play.Possession,
                "Yard": play.Play.Yard,
                "Hash": play.Play.Hash,
                "Down": play.Play.Down,
                "Distance": play.Play.Distance,
                "Quarter": play.Play.Quarter,
                "Motion": play.Play.Motion,
                "D_Formation": play.Play.D_Formation,
                "O_Formation": play.Play.O_Formation,
                "Formation_Strength": play.Play.Formation_Strength,
                "Home_Score": play.Play.Home_Score,
                "Away_Score": play.Play.Away_Score,
                "Play_Type": play.Play.Play_Type,
                "Play_Type_Dir": play.Play.Play_Type_Dir,
                "Pass_Zone": play.Play.Pass_Zone,
                "Coverage": play.Play.Coverage,
                "Pressure_Left": play.Play.Pressure_Left,
                "Pressure_Middle": play.Play.Pressure_Middle,
                "Pressure_Right": play.Play.Pressure_Right,
                "Ball_Carrier": play.Play.Ball_Carrier,
                "Event": play.Play.Event,
                "Result": play.Play.Result,
                "Result_X": play.Play.Result_X,
                "Result_Y": play.Play.Result_Y,
                "Play_X": play.Play.Play_X,
                "Play_Y": play.Play.Play_Y,
                "Pass_X": play.Play.Pass_X,
                "Pass_Y": play.Play.Pass_Y,
                "Creation_Date": play.Play.Creation_Date,
                "Home_Team": play.Game.Home_Team,
                "Away_Team": play.Game.Away_Team
            })
        return json
    