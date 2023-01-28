from database.db import db

class User(db.Model):
    """ Class representation of the User table in the Endzone database
    Args:
        db (_type_): Model of Database
    """
    
    __tablename__ = 'Users'
    ID = db.Column(db.Integer, primary_key= True, autoincrement = True)
    Email = db.Column(db.String(320), unique= True, nullable = False)
    Password = db.Column(db.String(128), unique= False , nullable = False)

    First_Name = db.Column(db.String(50), unique = False, nullable = False)
    Last_Name = db.Column(db.String(50), unique = False, nullable = False)
    Team_Code = db.Column(db.String(25), unique = False, nullable = False)
    Access = db.Column(db.String(25), nullable = False, default = "Coach")
    IS_Reviewed = db.Column(db.Boolean, nullable = False, default = False)

    def __init__(self, id, first_name, last_name, email, password, team_id, access, IS_Reviewed) -> None:
        self.ID = id
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Email = email
        self.Password = password 
        self.Team_Code = team_id
        self.Access = access
        self.IS_Reviewed = IS_Reviewed

    def test_cases(self):
        pass

