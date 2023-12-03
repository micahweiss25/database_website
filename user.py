from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, userID, first_name, last_name, admin, seller, password_hash):
        self.userID = userID
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin
        self.seller = seller
        self.password_hash = password_hash

    def get_id(self):
        return self.userID
        
    