from database.db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    first_name = db.Column(db.String(50),unique=True,nullable=False)
    last_name = db.Column(db.String(50),unique=True,nullable=False)
    email = db.Column(db.String(320),unique=True,nullable=False)
    password = db.Column(db.String(128),nullable=False)
    team_id = db.Column(db.Integer,unique=True)
    access = db.Column(db.String(25),nullable=False)
    IS_Reviewed=db.Column(db.Boolean,nullable=False)

    def __init__(self, id, first_name, last_name, email, password, team_id, access, IS_Reviewed):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password 
        self.team_id = team_id
        self.access = access
        self.IS_Reviewed = IS_Reviewed