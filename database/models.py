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
    phone_number = db.Column(db.String)

    First_Name = db.Column(db.String(50), unique = False, nullable = False)
    Last_Name = db.Column(db.String(50), unique = False, nullable = False)
    Team_Code = db.Column(db.String(25), unique = False, nullable = False)
    Access = db.Column(db.String(25), nullable = False, default = "Coach")
    IS_Reviewed = db.Column(db.Boolean, nullable = False, default = False)

    def __init__(self, first_name, last_name, email, password, team_id, access, IS_Reviewed) -> None:
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Email = email
        self.Password = password 
        self.Team_Code = team_id
        self.Access = access
        self.IS_Reviewed = IS_Reviewed

<<<<<<< Updated upstream
    def test_cases(self):
        pass
=======
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

class Formations(db.Model):
    __tablename__ = "Formation"
    ID = db.Column(db.Integer, autoincrement = True, primary_key= True)
    Formation = db.Column(db.String(50), unique = False, nullable = False)
    wideRecievers = db.Column(db.Integer, nullable = False)
    tightEnds = db.Column(db.Integer, nullable = False)
    runningBacks = db.Column(db.Integer, nullable = False)
    Image = db.Column(db.String(100), nullable = False, primary_key = True)
    Team_Code = db.Column(db.String(36), nullable = False)
    Squad_Code = db.Column(db.String(36), primary_key= True, nullable = False)

    def __init__(self, formation: str, wideRecievers: int, tightEnds: int, runningBacks: int, image: str, teamCode: str, squadCode: str)-> None:
        
        self.Formation = formation
        self.wideRecievers = wideRecievers
        self.tightEnds = tightEnds
        self.runningBacks = runningBacks
        self.Image = image
        self.Team_Code = teamCode
        self.Squad_Code = squadCode

    def get_id(self) -> str:
        return self.ID

        
>>>>>>> Stashed changes
