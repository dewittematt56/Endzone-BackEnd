from database.models import *
from sqlalchemy import *

def load_formation_json(formations: "list[Formations]") -> "list[dict]":
        json = []
        for formation in formations:
            json.append({
                "id": formation.ID,
                "Formation": formation.Formation,
                "RunningBacks": formation.runningBacks,
                "TightEnds": formation.tightEnds,
                "WideReceivers": formation.wideReceivers
            })
        return json
    

