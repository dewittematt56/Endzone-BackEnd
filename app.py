from flask import Flask, request, Response, redirect
from flask_login import login_manager, LoginManager, login_user, current_user
from database.db import db, db_uri
from database.models import *
from login_api.login_persona import LoggedInPersona
from web_pages.content_api import content_api  
from utils_api.utils_api import utils_api
from profile_api.profile_api import profile_api
import json
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
app.register_blueprint(content_api)
app.register_blueprint(utils_api)
app.register_blueprint(profile_api)
    
db.init_app(app)
# builds database if not existing
with app.app_context():
    db.create_all()

# set up login system
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(email: str):
    query = db.session.query(User).filter(User.Email == email)
    query_response = query.all()
    # To-Do get Team Codes for user

    if len(query_response) == 1:
        loaded_user = LoggedInPersona(query_response[0].ID ,query_response[0].First_Name, query_response[0].Last_Name, query_response[0].Email, query_response[0].Phone_Number, query_response[0].Current_Squad)
        return loaded_user
    else:
        return

@login_manager.unauthorized_handler
def no_login_redirect():
    return redirect("/login")

@app.route('/login/attempt', methods = ['POST'])
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

@app.route('/account/user/create', methods = ['POST'])
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
            join_team = data["join_action"] # True/False
            if join_team == True:
                team_code = data["team_code"]
            
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
            if join_team:
                team_code = data["team_code"] 
                if len(db.session.query(Team).filter(Team.Team_Code == team_code).all()) == 0:
                    return Response("Invalid team code, please try again", status = 403)
                else:
                    new_user = User(first, last, email, phone, password1, "null", "Complete")
                    db.session.add(new_user)
                    db.session.commit()
                    userId = new_user.get_id()
                    new_teamMember = Team_Member(team_code, userId, "Coach")
                    db.session.add(new_teamMember)
                    db.session.commit()
                    
                    login_user(load_user(new_user.Email))
                    return redirect("/endzone/hub")

            else:
                new_user = User(first, last, email, phone, password1, "null", "Creating Team")
                db.session.add(new_user)
                db.session.commit()
                login_user(load_user(new_user.Email))
                return redirect("/account/team")
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)


@app.route('/account/team/create', methods = ['POST'])
def createTeam():
    try:
        params = ['teamName', 'competitionLevel', 'state', 'address', 'zipCode', "city"]
        if request.method == 'POST':
            data = json.loads(request.get_data())
            for param in params:
                if param not in data.keys():
                    return Response('Please provide a ' + param, status = 404)
        teamName = data["teamName"]
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
        
       
        new_team = Team(teamName, state, address, zipCode, city, competitionLevel)
        updated_user = db.session.query(User.ID == current_user.id)
        updated_user.Stage = "Complete"

        team_owner = Team_Member(new_team.Team_Code, current_user.id, "Owner")
        db.session.add(new_team)
        db.session.add(team_owner)
        db.session.commit()
        return Response("Successfully Created Team", 200)
    except Exception as e:
            print(e)
            return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)


if __name__ == "__main__":
    app.run(use_reloader = True, host = "0.0.0.0", debug=True, port = 80)

    

