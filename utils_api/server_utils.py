from flask import Response
from typing import Optional, Union

def check_required_params(required_params: 'list[str]', recieved_params: 'list[str]') -> Optional[Union[Response, None]]:
    for param in required_params:
        if param not in recieved_params:
            return Response("Please provide a " + param, status = 400)
    return None

def validate_play_input(json_data: dict) -> Optional[Union[Response, None]]:
    for key in json_data.keys():
        if key == "Play_Number":
            if int(json_data[key]) not in range(0,1000):
                return Response("Play number must be in the range of 0 to 999", status = 400)
        elif key == "Yard":
            if int(json_data[key]) not in range(1,101):
                return Response("The yardage must be in range of 1 to 100", status = 400)
        elif key == "Hash":
            hash = json_data[key]
            if hash not in  ["Left", "Right", "Middle"]:
                return Response("Hash must be either Left, Right, or Middle", status = 400)
        elif key == "Down":
            if int(json_data[key]) not in range(1,5):
                return Response("Down must be in range from 1 to 4", status = 400)
        elif key == "Distance":
            if int(json_data[key]) not in range(1,101):
                return Response("Distance must be in range from 1 to 100", status = 400)
        elif key == "Quarter":
            if int(json_data[key]) not in range(1,6):
                return Response("Quarter must be in range from 1 to 5", status = 400)
        elif key == "Formation_Strength":
            if json_data[key] not in ["Left", "Right", "Unknown"]:
                return Response("Formation Strength must be either Left, Right, Balanced, or Unknown", status = 400)
        elif key == "Play_Type":
            play_types = ["Inside Run", "Outside Run", "Pass", "Boot Pass", "Option", "Unknown"]
            if json_data[key] not in play_types:
                return Response("Play type must be in list {}".format(play_types), status = 400)
        elif key == "Play_Type_Dir": 
            if json_data[key] not in ["Left", "Right", "Unknown"]:
                return Response("PlayTypeDir must be either Left, Right, or Unknown", status = 400)
        elif key == "Pass_Zone":   
            pass_zones = ["Flats-Left", "Flats-Right", "Middle-Left", "Middle-Middle", "Middle-Right", "Deep-Left", "Deep-Right", "Unknown", "Non Passing Play", "Not Thrown"]
            if json_data[key] not in pass_zones:
                return Response("Pass zone must be in list {}".format(pass_zones), status = 400)
        elif key == "Coverage":
             coverages = ["Man 0", "Man 1", "Man 2", "Man 3", "Zone 2", "Zone 3", "Zone 4", "Prevent", "Unknown"]
             if json_data[key] not in coverages:
                return Response("Coverage must be in list {}".format(coverages),status = 400)
        elif key == "Ball_Carrier": 
            if not json_data[key]:
                return Response("Ball carrier needs a number", status = 400)
        elif key == "Event":
            events = ["Penalty", "Interception", "Touchdown", "Fumble", "Field Goal", "Punt", "Safety", "None"]
            if json_data[key] not in events:
                return Response("Event must be in list {}".format(events), status=400)
        elif key == "Result":
            if json_data[key] not in range(-99,100):
                return Response("Result must be a number from -99 to 99", status = 400)
        elif key == "Home_Score" or key == "Away_Score":
            if int(json_data[key]) < 0:
                return Response("Scores must be positive integers", status = 400)
    return None