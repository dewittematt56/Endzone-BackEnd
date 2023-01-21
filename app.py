from flask import Flask
from flask_login import login_manager, LoginManager
from database.db import db, db_uri
from database.models import User
from login_api.login_peronsa import LoggedInPersona
from flask import Blueprint, request, Response
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    
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
    
@app.route('/loginattempt', methods = ['POST'])
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
                    return Response('Please Provide a ' + param, status = 404)
            email = data["email"]
            password = data["password"]
            query = db.session.query(User).filter(User.Email == email). \
                filter(User.Password == password)
            
            query_response = query.all()
            if len(query_response) == 0:
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


if __name__ == "__main__":

    app.run(use_reloader = True, host = "0.0.0.0", debug=True, port = 80)

    

