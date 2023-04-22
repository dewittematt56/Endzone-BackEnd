from flask_login import UserMixin

class LoggedInPersona(UserMixin):
    def __init__(self, id, first_name, last_name, email, phone, curTeam):
        self.id = id
        self.Email = email
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Org_Code = "test"
        self.Team_Code = "test"
        self.Phone = phone
        self.Current_Team = curTeam
        

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
    def get_phone(self):
        return self.Phone
    