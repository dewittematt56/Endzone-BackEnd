from database.db import db
import uuid

# Creates a team key
def gen_primary_key():
    return str(uuid.uuid4())

class User(db.Model):
    """ Class representation of the Use"testr table in the Endzone database
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

class Formations(db.Model):
    __tablename__ = "Formation"
    ID = db.Column(db.Integer, autoincrement = True, primary_key= True)
    Formation = db.Column(db.String(50), unique = False, nullable = False)
    wideRecievers = db.Column(db.Integer, nullable = False)
    tightEnds = db.Column(db.Integer, nullable = False)
    runningBacks = db.Column(db.Integer, nullable = False)
    Image = db.Column(db.String(100), nullable = False, primary_key = True) # Confused on how to do the blob thing
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
    



class plays(db.Model):
    __tablename__ = "plays"
    ID = db.Column(db.String(36), primary_key = True)
    Game_ID = db.Column(db.String(36), unique = False, nullable = False)
    Play_Number = db.Column(db.Integer, autoincrement = True, nullable = False) # 0-999*
    Possession = db.Column(db.String(100), nullable = False)
    Yard = db.Column(db.Integer, nullable = False) # 1-100*
    Hash = db.Column(db.String, nullable = False) # make this left right or middle*
    Down = db.Column(db.Integer, nullable = False) # 1,2,3,4*
    Distance = db.Column(db.Integer, nullable = False) # between 1-100*
    Quarter = db.Column(db.Integer, nullable = False) # make this between 1 and 5 *
    D_Formation = db.Column(db.String(25), nullable = False)
    O_Formation = db.Column(db.String(25), nullable = False)
    Formation_Strength = db.Column(db.String(10), nullable = False) # make this either left, right or balanced, unknown*
    Play_Type = db.Column(db.String(35), nullable = False) # [Inside Run, Outside Run, Pass, Boot Pass, Option, Unknown]*
    Play = db.Column(db.String(100), nullable = False)
    Play_Type_Dir = db.Column(db.String(35), nullable = False) # [left, right, unknown]*
    Pass_Zone = db.Column(db.String(35), nullable = False) # [Screen Left, Screen Right, Flat Left, Flat Right, Middle Left, Middle Middle Middle Right, Deep Left, Deep Right]*
    Coverage = db.Column(db.String(35), nullable = False) # [Man 0, Man 1, Man 2, Man 3, Cover 2, Cover 3, Cover 4, Prevent]*
    Pressure_Left = db.Column(db.Boolean(35), nullable = False) # ask mater*
    Pressure_Middle = db.Column(db.Boolean(35), nullable = False) # ask mater*
    Pressure_Right = db.Column(db.Boolean(35), nullable = False) # ask mater*
    Ball_Carrier = db.Column(db.String(2), nullable = False) # 0-99
    Event = db.Column(db.String(35), nullable = False) # Penalty, Interception, Touchdown, Fumble, Field Goal, Saftey
    Result = db.Column(db.Integer, nullable = False) # -99-99
    Result_X = db.Column(db.Float(35), nullable = False) # Switch Name -> Result_X | Float {1, 3} RETURN ("Invalid Geometry")
    Result_Y = db.Column(db.Float(35), nullable = False) # Float {0, 10} RETURN ("Invalid Geometry")
    Play_X = db.Column(db.Float(35), nullable = False) # Switch Name -> Result_X | Float {1, 3} RETURN ("Invalid Geometry")
    Play_Y = db.Column(db.Float(35), nullable = False) # Float {0, 10} RETURN ("Invalid Geometry")
    

    def __init__(self, gameId : str, playNumber  : int, possession : str, yard : int, hash : str, down : int, distance : int, quarter : int, dFormation : str, 
                 oFormation : str, formationStrength : str, playType : str, play : str, playTypeDir : str, passZone : str, coverage : str, pressureLeft : str, 
                 pressureMiddle : str, pressureRight : str, ballCarrier : str, event : str, result : str, resultX : str, resultY : str, playX: str, playY: str) -> None:
        self.ID = gen_primary_key()
        self.Game_ID = gameId
        self.Play_Number = playNumber
        self.Possession = possession
        self.Yard = yard
        self.Hash = hash
        self.Down = down
        self.Distance = distance
        self.Quarter = quarter
        self.D_Formation = dFormation
        self.O_Formation = oFormation
        self.Formation_Strength = formationStrength
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


        def get_id(self) -> str:
            return self.ID
        
class Squad(db.Model): # This class is messing up the file, no idea why
    __tablename__ = "Squad"
    Squad_ID = db.Column(db.String(35), unique = False, nullable = False, primary_key = True)
    Team_Code = db.Column(db.String(35), unique = False, nullable = False)
    Squad_Name = db.Column(db.String(50), unique = False, nullable = False)

    def __init__(self, teamCode: str, squadName: str) -> None:
       self.Squad_ID = gen_primary_key()
       self.Team_Code = teamCode
       self.Squad_Name = squadName