from flask import Blueprint, request, Response
import json


auth = Blueprint('auth', __name__)

@auth.route('/loginattempt', methods = ['POST'])
def loginAttempt(): 
    params = ["email","password"]  
    if request.method == 'POST':
        # Loads data into a dictionary from the request
        data = json.loads(request.get_data())
        # Checks to ensure all parameters are there
        for param in params:
            if param not in data.keys():
                return Response('Missing parameter ' + param, status = 404)
        
        return "email"
    
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                return Response('You are now logged in', 301)
            else:
                return Response('Incorrect password', 404)
        else:
            return Response('Email does not exist', 404)
    data = request.form
    print(data)
    """ 













    
   


    

