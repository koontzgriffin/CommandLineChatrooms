from models.User import User

class Room(object):
    def __init__(self, name : str, description = '', owner = '', password = '', ):
        self._name = name
        self._description = description
        self._owner = owner
        self._password = password

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name
    
    def set_description(self, description):
        self._description = description

    def get_description(self):
        return self._description
    
    def set_owner(self, owner : User):
        self._owner = owner.get_name()

    def get_owner(self):
        return self._owner

    def set_password(self, password):
        self._password = password
    
    def get_password(self):
        return self._password
    
    