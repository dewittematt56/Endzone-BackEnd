from flask_login import UserMixin

class LoggedInPersona(UserMixin):
    def __init__(self, first_name, last_name, email, team_code, access):
        self.Email = email
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Team_Code = team_code
        self.Access = access

    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated 
    def get_id(self):
        return self.Email 
    def is_active(self):
        return True
    def get_email(self):
        return self.Email
    def get_password(self):
        return self.Password
    