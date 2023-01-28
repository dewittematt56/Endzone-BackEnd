from flask import Blueprint
from flask_login import login_required, current_user
import json
utils_api = Blueprint("utils_api", __name__, template_folder="pages", static_folder="pages")


@login_required
@utils_api.route("/getuser", methods = ["GET"])
def getUser():
    return json.dumps({"first_name": current_user.First_Name, "last_name": current_user.Last_Name, "Team_Code": current_user.Team_Code})