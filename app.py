from flask import Flask, request, Response, redirect, jsonify, make_response
from flask_login import login_manager, LoginManager, login_user, current_user, logout_user, login_required
from database.db import db, db_uri
from database.models import *
from login_api.login_persona import LoggedInPersona

from web_pages.content_api import content_api  
from utils_api.utils_api import utils_api
from data_api.data_api import data_api
# from reports_api.reports_api import report_api, report_executor
from profile_api.profile_api import profile_api
from flask_executor import Executor
from threading import Lock
from io import BytesIO
from reports_api.reports.pregame_report import PregameReport
import json
import re



application = Flask(__name__)

application.config['SECRET_KEY'] = 'secret key'
application.config['SQLALCHEMY_DATABASE_URI'] = db_uri
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config['EXECUTOR_TYPE'] = 'thread'
application.config['EXECUTOR_MAX_WORKERS'] = 5
report_executor = Executor(application)


application.register_blueprint(content_api)
application.register_blueprint(utils_api)
application.register_blueprint(data_api)
# application.register_blueprint(report_api)
application.register_blueprint(profile_api)

# Executors

report_executor.init_app(application)

db.init_app(application)

# builds database if not existing
with application.app_context():
    db.create_all()

# set up login system
login_manager = LoginManager()
login_manager.init_app(application)
@login_manager.user_loader
def load_user(email: str):
    query = db.session.query(User).filter(User.Email == email)
    query_response = query.all()
    # To-Do get org Codes for user

    if len(query_response) == 1:
        loaded_user = LoggedInPersona(query_response[0].ID ,query_response[0].First_Name, query_response[0].Last_Name, query_response[0].Email, query_response[0].Phone_Number, query_response[0].Current_Team)
        return loaded_user
    else:
        return

@login_manager.unauthorized_handler
def no_login_redirect():
    return redirect("/login")

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
        params = ["first", "last", "email", "password1", "password2", "phone", "join_action"]
        if request.method == "POST":
            data = json.loads(request.get_data())
            # Make sure all fields are filled in
            for param in params:
                if param not in data.keys():
                    return Response("Please provide a " + param, status = 400)
            first = data["first"]
            last = data["last"]
            email = data["email"]
            password1 = data["password1"]
            password2 = data["password2"]
            phone = data["phone"]
            join_org = data["join_action"] # True/False
            if join_org == True:
                org_code = data["org_code"]
            
            first_has_number = any(map(str.isdigit,first))
            last_has_number = any(map(str.isdigit,last))
            pass_has_letter = any(map(str.isalpha,password1))
            pass_has_number = any(map(str.isdigit, password1)) # contains if the passwords have a number in them
            special_char = re.compile('[\'@_!#$%^&*()<>?/\\|}{~:]') # compiles the special characters to check for them in password
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
                org_code = data["org_code"] 
                if len(db.session.query(Org).filter(Org.Org_Code == org_code).all()) == 0:
                    return Response("Invalid org code, please try again", status = 403)
                else:
                    new_user = User(first, last, email, phone, password1, "null", "Complete")
                    db.session.add(new_user)
                    db.session.commit()
                    userId = new_user.get_id()
                    new_orgMember = Org_Member(org_code, userId, "Coach")
                    db.session.add(new_orgMember)
                    db.session.commit()
                    
                    login_user(load_user(new_user.Email))
                    return redirect("/endzone/hub")

            else:
                new_user = User(first, last, email, phone, password1, "null", "Creating Org")
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
        params = ['orgName', 'competitionLevel', 'state', 'address', 'zipCode', "city"]
        if request.method == 'POST':
            data = json.loads(request.get_data())
            for param in params:
                if param not in data.keys():
                    return Response('Please provide a ' + param, status = 404)
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
            return Response("State must be the uppercase two letter abbreviation of the state", status = 404)
        elif any(map(str.isdigit,state)) == True:
            return Response("No numbers in the state field", status = 404)
        elif " " in state:
            return Response("State should be comprised of 2 letters", status = 404)
        
        # Conditional for competition levels
        if competitionLevel not in comp_levels:
            return Response("Please input either Youth, High School, College, or Professional", status = 404)
        
        # Zip code conditionals
        if len(zipCode) != 5:
            return Response("Please input 5 number zip code", status = 404)
        elif any(map(str.isalpha,zipCode)):
            return Response("Zip code can only be comprised of numbers", status = 404)
        elif special_char.search(zipCode) != None:
            return Response("Zip code can only be comprised of numbers")
        elif " " in zipCode:
            return Response("No spaces are allowed in the zip code field")
        
        # Address Conditionals
        if any(map(str.isalpha, address)) == False:
            return Response("Address needs to have letters included", status = 404)
        elif any(map(str.isdigit, address)) == False:
            return Response("Address needs to have numbers included", status = 404)

        # City conditional
        if any(map(str.isdigit, city)):
            return Response("City field cannot include numbers", status = 404)
        
      
        new_org = Org(orgName, state, address, zipCode, city, competitionLevel)
        new_team = Team(orgName, new_org.Org_Code)
        
        updated_user = db.session.query(User.ID == current_user.id)
        updated_user.Stage = "Complete"

        org_owner = Org_Member(new_org.Org_Code, current_user.id, "Owner")
        team_owner = Team_Member(new_team.Team_Code, current_user.id, "Owner")
        db.session.add(new_org)
        db.session.add(org_owner)
        db.session.add(new_team)
        db.session.add(team_owner)

        db.session.commit()
        return Response("Successfully Created Org", 200)
    except Exception as e:
            print(e)
            return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)

thread_lock = Lock()


def run_report():
    with thread_lock:
        report = PregameReport()
        pdf = report.combine_reports()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
        return response

@application.route("/endzone/reports/test")
def test():
    job_1 = report_executor.submit(run_report)
    response = job_1.result()
    return response


if __name__ == "__main__":
    application.run(use_reloader = True, host = "0.0.0.0", debug=True, port = 80)

    

