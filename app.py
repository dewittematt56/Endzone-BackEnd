from flask import Flask, Blueprint, request, Response
from flask_login import login_manager, LoginManager
from database.db import db, db_uri
from database.models import User
from login_api.login_peronsa import LoggedInPersona
from web_pages.content_api import content_api  
import json
import re
from utils_api.utils_api import utils_api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
app.register_blueprint(content_api)
app.register_blueprint(utils_api)   
db.init_app(app)
# builds database if not existing
with app.app_context():
    db.create_all()

# set up login system
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_persona: User):
    """ Module to load a user into our Flask application

    Args:
        email (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Sendd Keyword Arguments of user_persona class to Login Class
    return LoggedInPersona(**user_persona.__dict__)    
    
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
                    return Response('Please Provide a ' + param, status = 404) #deleted the "a", because it would result in a when "an" is needed (GRAMMAR)
            email = data["email"]
            password = data["password"]
            query = db.session.query(User).filter(User.Email == email). \
                filter(User.Password == password)
            
            query_response = query.all()
            if len(query_response) == 0: # ask mater about this
                if len(db.session.query(User).filter(User.Email == email).all()) == 0:
                    # Exposed to end user
                    return Response("No account with that email exists", 404)
                else:
                    # Exposed to end user
                    return Response("Inncorrect Password", 404)
            elif len(query_response) == 1:
                load_user(query_response[0])
                return "Successful login"
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    



@app.route('/account/createuser', methods = ['POST'])
def register():
    
    
    try:
        params = ["first", "last", "email", "password1", "password2", "team_code"]
        if request.method == "POST":
            data = json.loads(request.get_data())

            # Make sure all fields are filled in
            for param in params:
                if param not in data.keys():
                    return Response("Please provide a " + param, status = 404)
            first = data["first"]
            last = data["last"]
            email = data["email"]
            password1 = data["password1"]
            password2 = data["password2"]
            team_code = data["team_code"]
            has_letter = any(map(str.isalpha,password1))
            has_number = any(map(str.isdigit, password1)) # contains if the passwords have a number in them
            special_char = re.compile('[\'@_!#$%^&*()<>?/\\|}{~:]') # compiles the special characters to check for them in password

            # Make sure there isnt already an account with this email
            if len(db.session.query(User).filter(User.Email == email).all()) != 0:
                return Response("There is an account already associated with this email", status = 404)
            
            elif any(map(str.isdigit,first)) or any(map(str.isdigit,last)):
                return Response("Numbers are not allowed in name fields", status = 404) 
            
            elif len(password1) < 8: # Makes sure the password has at least 8 characters
                return Response("Password needs at least 8 characters", status = 404)
            # password requirements: at least 8 characters, a number or 1 special character, not longer than 128 characters, at least 1 letter, 1 upper
            elif password1 != password2:
                return Response("Password fields do not match", status = 404)
            elif has_number == False and special_char.search(password1) == None: # Determines if a password has a number or a special character
                return Response("At least 1 number or special character is needed", status = 404)
            elif has_letter == False:
                return Response("Password needs at least 1 letter")
            # make sure the team code exists
            elif len(db.session.query(User).filter(User.Team_Code == team_code).all()) < 1:
                return Response("Invalid team code, please try again", status = 404)
            
           
            new_user = User(first, last, email, password1, team_code, "Requested", 0)
            db.session.add(new_user)
            db.session.commit()

            return "done"
            

                
                
                
    
    except Exception as e:
        print(e)
        return Response("Error Code 500: Something unexpected happened, please contact endzone.analytics@gmail.com", status = 500)
    
    
        
    



if __name__ == "__main__":

    app.run(use_reloader = True, host = "0.0.0.0", debug=True, port = 80)

    

