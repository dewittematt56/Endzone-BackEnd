from flask_login import UserMixin

class LoggedInPersona(UserMixin):
    def __init__(self, **kwargs):
        self.id = kwargs["ID"]
        self.Email = kwargs["Email"]
        self.Password = kwargs["Password"] 
        self.First_Name = kwargs["First_Name"]
        self.Last_Name = kwargs["Last_Name"]
        self.Team_Code = kwargs["Team_Code"]
        self.Access = kwargs["Access"]
        self.IS_Reviewed = kwargs["IS_Reviewed"]

    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated 
    def get_id(self):
        return self.id 
    def get_email(self):
        return self.Email
    def get_password(self):
        return self.Password
    