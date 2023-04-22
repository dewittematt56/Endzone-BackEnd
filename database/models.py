from database.db import db
import uuid
import datetime
from flask_login import current_user
import datetime
from sqlalchemy import DateTime

# Creates a org key
def gen_primary_key():
    return str(uuid.uuid4())

class User(db.Model):
    """ Class representation of the User table in the Endzone database
    Args:
        db (_type_): Model of Database
    """
    
    __tablename__ = 'User'
    ID = db.Column(db.String(36), primary_key= True)
    Email = db.Column(db.String(320), unique= True, nullable = False)
    Password = db.Column(db.String(128), unique= False , nullable = False)
    Phone_Number =  db.Column(db.String(15), unique = False, nullable = False)
    First_Name = db.Column(db.String(50), unique = False, nullable = False)
    Last_Name = db.Column(db.String(50), unique = False, nullable = False)
    Current_Team = db.Column(db.String(50), unique = False, nullable = True)
    Stage = db.Column(db.String(25), unique = False, nullable = False)
    # To-Do add join date

    def __init__(self, first_name, last_name, email, phone_number, password, Current_Team, stage) -> None:
        self.ID = gen_primary_key()
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Password = password 
        self.Email = email
        self.Phone_Number = phone_number
        self.Current_Team = Current_Team
        self.Stage = stage
        
    def get_id(self) -> str:
        return self.ID

class Org_Member(db.Model):
    """_summary_

    Args:
        db (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    __tablename__ = "Org_Member"
    ID = db.Column(db.String(36), primary_key= True)
    Org_Code = db.Column(db.String(36))
    User_ID = db.Column(db.String(36))
    Role = db.Column(db.String(25), default = "Coach")

    def __init__(self, org_code, user_id, role) -> None:
        self.ID = gen_primary_key()
        self.Org_Code = org_code

        self.User_ID = user_id
        self.Role = role

    def get_id(self) -> str:
        return self.ID

class Org(db.Model):
    """_summary_

    Args:
        db (_type_): _description_
    """

    __tablename__ = "Org"
    Org_Code = db.Column(db.String(36), primary_key= True, nullable = False, unique= True)
    Org_Name = db.Column(db.String(50), unique= False, nullable = False)
    State = db.Column(db.String(2), nullable = False)
    City = db.Column(db.String(100), nullable = False)
    Address = db.Column(db.String(320), nullable = False)
    Zip = db.Column(db.String(5), nullable = False)
    Competition_Level = db.Column(db.String(50), nullable = True)
    
    def __init__(self, org_name: str, state: str, address: str, zip: str, city: str, comp_level: str) -> None:
        self.Org_Code = gen_primary_key()
        self.Org_Name = org_name
        self.State = state
        self.Address = address
        self.City = city
        self.Zip = zip
        self.Competition_Level = comp_level

    def get_id(self) -> str:
        return self.ID

class Formations(db.Model):
    __tablename__ = "Formation"
    ID = db.Column(db.Integer, autoincrement = True, primary_key= True)
    Formation = db.Column(db.String(50), unique = False, nullable = False)
    Wide_Receivers = db.Column(db.Integer, nullable = False)
    Tight_Ends = db.Column(db.Integer, nullable = False)
    Running_Backs = db.Column(db.Integer, nullable = False)
    Image = db.Column(db.LargeBinary, nullable = True) # Confused on how to do the blob thing
    Org_Code = db.Column(db.String(36), nullable = False)
    Team_Code = db.Column(db.String(36), primary_key= True, nullable = False)
    Creator = db.Column(db.String(36), unique = False, nullable = False)
    Creation_Date = db.Column(DateTime(), default=datetime.datetime.utcnow, nullable = False)

    def __init__(self, formation: str, wideReceivers: int, tightEnds: int, runningBacks: int, image: str)-> None:
        self.Formation = formation
        self.Wide_Receivers = wideReceivers
        self.Tight_Ends = tightEnds
        self.Running_Backs = runningBacks
        self.Image = image
        self.Org_Code = current_user.Org_Code
        self.Team_Code = current_user.Team_Code
        self.Creator = current_user.id
        self.Creation_Date = datetime.datetime.utcnow()

    def get_id(self) -> str:
        return self.ID

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
    
class Play(db.Model):
    __tablename__ = "Play"
    ID = db.Column(db.String(36), primary_key = True)
    Game_ID = db.Column(db.String(36), unique = False, nullable = False)
    Play_Number = db.Column(db.Integer, autoincrement = True, nullable = False)
    Drive = db.Column(db.Integer, nullable = False) 
    Possession = db.Column(db.String(100), nullable = False)
    Yard = db.Column(db.Integer, nullable = False) 
    Hash = db.Column(db.String, nullable = False) 
    Down = db.Column(db.Integer, nullable = False)
    Distance = db.Column(db.Integer, nullable = False)
    Quarter = db.Column(db.Integer, nullable = False)
    Motion = db.Column(db.String(25), nullable = False, default = "None")
    D_Formation = db.Column(db.String(25), nullable = False)
    O_Formation = db.Column(db.String(25), nullable = False)
    Formation_Strength = db.Column(db.String(10), nullable = False) 
    Home_Score = db.Column(db.Integer, nullable = False, default = 0)
    Away_Score = db.Column(db.Integer, nullable = False, default = 0)
    Play_Type = db.Column(db.String(35), nullable = False)
    Play = db.Column(db.String(100), nullable = True, default = "Unknown")
    Play_Type_Dir = db.Column(db.String(35), nullable = False)
    Pass_Zone = db.Column(db.String(35), nullable = True, default = "Non Passing Play")
    Coverage = db.Column(db.String(35), nullable = False)
    Pressure_Left = db.Column(db.Boolean(35), nullable = False, default = False) 
    Pressure_Middle = db.Column(db.Boolean(35), nullable = False, default = False)
    Pressure_Right = db.Column(db.Boolean(35), nullable = False, default = False)
    Ball_Carrier = db.Column(db.Integer, nullable = False, default = -99)
    Event = db.Column(db.String(35), nullable = False, default = "None") 
    Result = db.Column(db.Integer, nullable = False) 
    Result_X = db.Column(db.Float(35), nullable = False) 
    Result_Y = db.Column(db.Float(35), nullable = False) 
    Play_X = db.Column(db.Float(35), nullable = False) 
    Play_Y = db.Column(db.Float(35), nullable = False)
    Pass_X = db.Column(db.Float(35), nullable = True, default = 0) 
    Pass_Y = db.Column(db.Float(35), nullable = True, default = 0)  
    Creator = db.Column(db.String(36), unique = False, nullable = False)
    Creation_Date = db.Column(DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, gameId : str, playNumber: int, drive: int, possession : str, yard : int, hash : str, down : int, distance : int, quarter : int, motion: str, dFormation : str, 
                 oFormation : str, formationStrength : str, homeScore: int, awayScore: int, playType : str, play : str, playTypeDir : str, passZone : str, coverage : str, pressureLeft : bool, 
                 pressureMiddle : bool, pressureRight : bool, ballCarrier : str, event : str, result : str, resultX : str, resultY : str, playX: float, playY: float, passX: float, passY: float) -> None:
        self.ID = gen_primary_key()
        self.Game_ID = gameId
        self.Play_Number = playNumber
        self.Drive = drive
        self.Possession = possession
        self.Yard = yard
        self.Hash = hash
        self.Down = down
        self.Distance = distance
        self.Quarter = quarter
        self.Motion = motion
        self.D_Formation = dFormation
        self.O_Formation = oFormation
        self.Formation_Strength = formationStrength
        self.Home_Score = homeScore
        self.Away_Score = awayScore
        self.Play_Type = playType
        self.Play = play
        self.Play_Type_Dir = playTypeDir
        self.Pass_Zone = passZone
        self.Coverage = coverage
        self.Pressure_Left = pressureLeft
        self.Pressure_Middle = pressureMiddle
        self.Pressure_Right = pressureRight
        self.Ball_Carrier = ballCarrier
        self.Event = event
        self.Result = result
        self.Result_X = resultX
        self.Result_Y = resultY
        self.Play_X = playX
        self.Play_Y = playY
        self.Pass_X = passX
        self.Pass_Y = passY
        self.Creator = current_user.id
        self.Creation_Date = datetime.datetime.utcnow()

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
    Org_Code = db.Column(db.String(50), unique= False, nullable = False)
    
    
    def __init__(self, team_code: str, team_name: str, org_code: str) -> None:
        self.Team_Code = gen_primary_key()
        self.Team_Name = team_name
        self.Org_Code = org_code

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
    Team_Code = db.Column(db.String(36), primary_key = True)
    User_ID = db.Column(db.String(36), primary_key = True)
    Role = db.Column(db.String(25), default = "Owner")

    def __init__(self, team_code, user_id, role) -> None:
        self.Team_Code = team_code
        self.User_ID = user_id
        self.Role = role

    def get_id(self) -> str:
        return self.ID

class Game(db.Model):
    __tablename__ = "Game"
    Game_ID = db.Column(db.String(36), primary_key = True)
    Home_Team = db.Column(db.String(36), unique = False, nullable = False)
    Away_Team = db.Column(db.String(36), unique = False, nullable = False)
    Game_Date = db.Column(DateTime(), default=datetime.datetime.utcnow)
    Game_Type = db.Column(db.String(10), unique = False, nullable = False)
    Team_Code = db.Column(db.String(36), unique = False, nullable = False)
    Creator = db.Column(db.String(36), unique = False, nullable = False)
    Creation_Date = db.Column(DateTime(), default=datetime.datetime.utcnow, nullable = False)

    def __init__(self, home_team: str, away_team: str, game_date: datetime.datetime, type: str) -> None:
        self.Game_ID = gen_primary_key()
        self.Home_Team = home_team
        self.Away_Team = away_team
        self.Game_Date = game_date
        self.Game_Type = type
        self.Team_Code = current_user.Team_Code
        self.Creator = current_user.id
        self.Creation_Date = datetime.datetime.utcnow()