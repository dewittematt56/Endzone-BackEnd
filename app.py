from flask import Flask, Blueprint, request, Response
from flask_login import login_manager, LoginManager

from database.db import db, db_uri
from database.models import User
<<<<<<< Updated upstream
from login.login import UserLogin
from flask import Blueprint, request, Response
import json
=======

from login_api.login_peronsa import LoggedInPersona
>>>>>>> Stashed changes

from web_pages.pages_api import pages_api
import json



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    

app.register_blueprint(pages_api)

db.init_app(app)
# builds database if not existing
with app.app_context():
    db.create_all()

# set up login system
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(email):
    query = db.session.query(User).filter(User.email == email)
    response = query.all()
    return UserLogin(response[0].id,response[0].first_name[0], response[0].last_name, response[0].email, response[0].password, response[0].team_id, response[0].access, response[0].IS_Reviewed)    
    
<<<<<<< Updated upstream

@app.route('/loginattempt', methods = ['POST'])

=======
@app.route('/login/attempt', methods = ['POST'])
>>>>>>> Stashed changes
def loginAttempt(): 
    try:
        params = ["email","password"]  
        if request.method == 'POST':
            # Loads data into a dictionary from the request
            data = json.loads(request.get_data())
            # Checks to ensure all parameters are there
            for param in params:
                if param not in data.keys():
                    return Response('Missing parameter ' + param, status = 404)
            email = data["email"]
            password = data["password"]
            query = db.session.query(User).filter(User.email == email). \
                filter(User.password == password)
            
            if len(query.all()) == 0:
                query = db.session.query(User).filter(User.email == email)
                if len(query.all()) == 0:
                    return Response("Login failed, email not found", 404)
                else:
                    return Response("Login failed, incorrect password", 404)
            elif len(query.all()) == 1:
                load_user(email)
        
                return "Successful login"
    except Exception as e:
        return Response("Something unexpected happened", status = 500)
if __name__ == "__main__":
    app.run(use_reloader = True, host = "0.0.0.0", debug=True, port = 80)

    

