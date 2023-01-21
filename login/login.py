from flask_login import UserMixin

class UserLogin(UserMixin):
    def __init__(self, id, first_name, last_name, email, password, team_id, access, IS_Reviewed):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password 
        self.team_id = team_id
        self.access = access
        self.IS_Reviewed = IS_Reviewed

    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated 
    def get_id(self):
        return self.id 
    def get_email(self):
        return self.email
    def get_password(self):
        return self.password
    