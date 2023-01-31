from database.db import db
import uuid

# Creates a team key
def gen_primary_key():
    return str(uuid.uuid4)

class User(db.Model):
    """ Class representation of the User table in the Endzone database
    Args:
        db (_type_): Model of Database
    """
    
    __tablename__ = 'Users'
    ID = db.Column(db.String(36), primary_key= True)
    Email = db.Column(db.String(320), unique= True, nullable = False)
    Password = db.Column(db.String(128), unique= False , nullable = False)
    Phone_Number =  db.Column(db.String(15), unique = False, nullable = False)
    First_Name = db.Column(db.String(50), unique = False, nullable = False)
    Last_Name = db.Column(db.String(50), unique = False, nullable = False)
    Team_Code = db.Column(db.String(25), unique = False, nullable = False)
    Stage = db.Column(db.String(25), unique = False, nullable = False)

    def __init__(self, first_name, last_name, email, phone_number, password, team_id, stage) -> None:
        self.ID = gen_primary_key()
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Password = password 
        self.Email = email
        self.Phone_Number = phone_number
        self.Team_Code = team_id
        self.Stage = stage
        
    def get_id(self) -> str:
        return self.ID

class Team_Member(db.Model):
    """_summary_

    Args:
        db (_type_): _description_

    Returns:
        _type_: _description_
    """

    __tablename__ = "Team_Member"
    ID = db.Column(db.Integer, primary_key= True, autoincrement = True)
    Team_Code = db.Column(db.String(36))
    User_ID = db.Column(db.Integer)
    Role = db.Column(db.String(25), default = "Coach")

    def __init__(self, team_code, user_id, role) -> None:
        self.Team_Code = team_code
        self.User_ID = user_id
        self.Role = role
        super().__init__()

    def get_id(self) -> str:
        return self.ID

class Team(db.Model):
    """_summary_

    Args:
        db (_type_): _description_
    """

    __tablename__ = "Team"
    Team_Code = db.Column(db.String(36), primary_key= True, nullable = False, unique= True)
    Team_Name = db.Column(db.String(50), unique= False, nullable = False)
    State = db.Column(db.String(2), nullable = False)
    Address = db.Column(db.String(320), nullable = False)
    Zip = db.Column(db.String(5), nullable = False)
    Competition_Level = db.Column(db.String(50), nullable = True)
    
    def __init__(self, team_name: str, state: str, address: str, zip: str, comp_level: str) -> None:
        self.Team_Code = gen_primary_key()
        self.Team_Name = team_name
        self.State = state
        self.Address = address
        self.Zip = zip
        self.Competition_Level = comp_level

    def get_id(self) -> str:
        return self.ID