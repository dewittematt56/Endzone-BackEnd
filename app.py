from flask import Flask, request, Response, redirect, render_template
from flask_login import login_manager, LoginManager, login_user, current_user, logout_user, login_required
import json
import re

from database.db import db, db_uri
from database.models import *
from login_api.login_persona import LoggedInPersona

# Endzone API's
from reports_api.reports_api import reports_api
import server_utils
from web_pages.content_api import content_api  
from utils_api.utils_api import utils_api
from data_api.data_api import data_api
from profile_api.profile_api import profile_api
from org_api.om_profile_api import om_profile_api
from org_api.om_members_api import om_members_api
from team_api.tm_members_api import tm_members_api
from team_api.tm_profile_api import tm_profile_api

from api_tools.tars_api import tars_api
from api_tools.autopilot_api import autopilot_api, socketio

application = Flask(__name__, template_folder="web_pages/pages")

application.config['SECRET_KEY'] = 'secret key'
application.config['SQLALCHEMY_DATABASE_URI'] = db_uri
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config["message_queue"] = {}

application.register_blueprint(content_api)
application.register_blueprint(utils_api)
application.register_blueprint(data_api)
application.register_blueprint(reports_api)
application.register_blueprint(profile_api)
application.register_blueprint(om_profile_api)
application.register_blueprint(om_members_api)
application.register_blueprint(tm_members_api)
application.register_blueprint(tm_profile_api)
application.register_blueprint(tars_api)
application.register_blueprint(autopilot_api)

# Executors
db.init_app(application)


# builds database if not existing
with application.app_context():
    db.create_all()

socketio.init_app(application)

# set up login system
login_manager = LoginManager()
login_manager.init_app(application)
@login_manager.user_loader
def load_user(email: str):
    query_user = db.session.query(User).filter(User.Email == email).all()

    # To-Do get org Codes for user
    if len(query_user) == 1:
        current_team = query_user[0].Current_Team
        # If no Current Team is Set
        if not current_team:
            current_team = query_user[0].Default_Team
        query_team = db.session.query(Team).filter(Team.Team_Code == current_team).all()
        if len(query_team) == 1:
            loaded_user = LoggedInPersona(query_user[0].ID ,query_user[0].First_Name, query_user[0].Last_Name, query_user[0].Email, query_user[0].Phone_Number, current_team, query_team[0].Org_Code)
        else:
            loaded_user = LoggedInPersona(query_user[0].ID ,query_user[0].First_Name, query_user[0].Last_Name, query_user[0].Email, query_user[0].Phone_Number, current_team, 'Unknown')
        return loaded_user
    else:
        return

@login_manager.unauthorized_handler
def no_login_redirect():
    return redirect("/login")

@application.errorhandler(404)
def page_not_found(e):
    return render_template('/public/page_not_found/index.html')

@application.route('/login/attempt', methods = ['POST'])
def loginAttempt(): 
    try:
        params = ["email","password"]  
        if request.method == 'POST':
            # Loads data into a dictionary from the request
            data = json.loads(request.get_data())
            # Checks to ensure all parameters are there
            for param in params:
                if param not in data.keys():
                    # Exposed to end user
                    return Response('Please Provide a ' + param, status = 403)
            email = data["email"]
            password = data["password"]
            query = db.session.query(User).filter(User.Email == email). \
                filter(User.Password == password)
            
            query_response = query.all()
            if len(query_response) == 0:
                if len(db.session.query(User).filter(User.Email == email).all()) == 0:
                    # Exposed to end user
                    return Response("No account with that email exists", 403)
                else:
                    # Exposed to end user
                    return Response("Incorrect Password", 403)
            elif len(query_response) == 1:
                if query_response[0].Email == email and query_response[0].Password == password:
                    login_user(load_user(query_response[0].Email))
                    return redirect("/endzone/hub")
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@application.route('/account/user/create', methods = ['POST'])
def register():    
    try:
        if request.method == "POST":
            data = json.loads(request.get_data())
            # Make sure all fields are filled in
            param_check = server_utils.check_required_params(["first", "last", "email", "password1", "password2", "phone", "join_action"], data.keys())
            if param_check: return param_check

            # Get Data from Payload
            first = data["first"]
            last = data["last"]
            email = data["email"]
            password1 = data["password1"]
            password2 = data["password2"]
            phone = data["phone"]
            join_org = data["join_action"] # True/False

            if join_org == True:
                # WE JOIN ORGANIZATIONS BY TEAM CODE (PARENT -> CHILD)
                team_code = data["team_code"]
            
            first_has_number = any(map(str.isdigit,first))
            last_has_number = any(map(str.isdigit,last))
            pass_has_letter = any(map(str.isalpha,password1))
            pass_has_number = any(map(str.isdigit, password1)) # contains if the passwords have a number in them
            special_char = re.compile('[@_!#$%^&<>?/|~:\']') # compiles the special characters to check for them in password
            # Make sure there isn't already an account with this email
            if len(db.session.query(User).filter(User.Email == email).all()) != 0:
                return Response("There is an account already associated with this email", status = 403)
            
            # Conditionals for the name fields
            if any(map(str.isdigit,first)) or any(map(str.isdigit,last)):
                return Response("Numbers are not allowed in name fields", status = 403) 
            elif " " in first or " " in last:
                return Response("Spaces are not allowed in name field", status = 403)           
            elif first_has_number == True or last_has_number == True:
                return Response("Numbers not allowed in name fields", status = 403)

            # Conditionals for the passwords
            if len(password1) < 8: 
                return Response("Password needs at least 8 characters", status = 403)
            elif password1 != password2:
                return Response("Password fields do not match", status = 403)
            elif pass_has_number == False and special_char.search(password1) == None: 
                return Response("At least 1 number or special character is needed", status = 403)
            elif pass_has_letter == False:
                return Response("Password needs at least 1 letter")
            elif " " in password1:
                return Response("Spaces are not allowed in the password field", status = 403)
            if join_org:
                team_code = data["team_code"] 
                team_query = db.session.query(Team).filter(Team.Team_Code == team_code).all()
                if len(team_query) == 0:
                    return Response("Invalid org code, please try again", status = 403)
                elif len(team_query) == 1:
                    org_query = db.session.query(Org).filter(Org.Org_Code == team_query[0].Org_Code).all()
                    if len(org_query) == 1:
                        new_user = User(first, last, email, phone, password1, team_query[0].Team_Code, "Complete")
                        db.session.add(Team_Member(team_query[0].Team_Code, new_user.get_id(), "Coach"))
                        db.session.add(Org_Member(org_query[0].Org_Code, new_user.get_id(), "Coach"))
                        db.session.add(new_user)
                        db.session.commit()
                        login_user(load_user(new_user.Email))
                        return redirect("/endzone/hub")
                    else:
                        return Response("Odd, The team you specified does not have an organization please contact endzone.analytics@gmail.com", status = 500)
                else:
                    return Response("Odd, There are multiple teams with that team code. please contact endzone.analytics@gmail.com", status = 500)
            else:
                new_user = User(first, last, email, phone, password1, "Creating Org", "Creating Org")
                db.session.add(new_user)
                db.session.commit()
                login_user(load_user(new_user.Email))
                return redirect("/account/org")
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

@application.route('/account/org/create', methods = ['POST'])
def createOrg():
    try:
        if request.method == 'POST':
            data = json.loads(request.get_data())
            param_check = server_utils.check_required_params(['orgName', 'competitionLevel', 'state', 'address', 'zipCode', "city"], data.keys())
            if param_check: return param_check

            orgName = data["orgName"]
            competitionLevel = data["competitionLevel"]
            state = data["state"]
            address = data["address"]
            zipCode = data["zipCode"]
            city = data["city"]
            comp_levels = ["Youth", "High School", "College", "Professional"]
            states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
            'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
            'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
            'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
            'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
            special_char = re.compile('[\'@_!#$%^&*()<>?/\\|}{~:]')
            # state conditionals 
            if state not in states:
                return Response("State must be the uppercase two letter abbreviation of the state", status = 400)
            elif any(map(str.isdigit,state)) == True:
                return Response("No numbers in the state field", status = 400)
            elif " " in state:
                return Response("State should be comprised of 2 letters", status = 400)
            
            # Conditional for competition levels
            if competitionLevel not in comp_levels:
                return Response("Please input either Youth, High School, College, or Professional", status = 400)
            
            # Zip code conditionals
            if len(zipCode) != 5:
                return Response("Please input 5 number zip code", status = 400)
            elif any(map(str.isalpha,zipCode)):
                return Response("Zip code can only be comprised of numbers", status = 400)
            elif special_char.search(zipCode) != None:
                return Response("Zip code can only be comprised of numbers")
            elif " " in zipCode:
                return Response("No spaces are allowed in the zip code field")
            
            # Address Conditionals
            if any(map(str.isalpha, address)) == False:
                return Response("Address needs to have letters included", status = 400)
            elif any(map(str.isdigit, address)) == False:
                return Response("Address needs to have numbers included", status = 400)

            # City conditional
            if any(map(str.isdigit, city)):
                return Response("City field cannot include numbers", status = 400)
            
            updated_user = db.session.query(User).get(current_user.id)

            new_org = Org(orgName, state, address, zipCode, city, competitionLevel)
            new_team = Team(orgName + ' - ' + competitionLevel, new_org.Org_Code)
            org_owner = Org_Member(new_org.Org_Code, current_user.id, "Owner")
            team_owner = Team_Member(new_team.Team_Code, current_user.id, "Owner")

            # Update Some User Props
            updated_user.Stage = "Complete"
            updated_user.Current_Team = new_team.Team_Code
            updated_user.Default_Team = new_team.Team_Code
            
            db.session.add(new_org)
            db.session.add(org_owner)
            db.session.add(new_team)
            db.session.add(team_owner)

            db.session.commit()
            return Response("Successfully Created Org", 200)
    except Exception as e:
            print(e)
            return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)



if __name__ == "__main__":
    application.run(use_reloader = True, host = "0.0.0.0", debug=True, port = 80)

    

