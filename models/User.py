
class User(object):
    def __init__(self, name = '', password = '', s = None):
        self._name = name
        self._password = password
        self._sock = s

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_password(self, password):
        self._password = password
    
    def get_password(self):
        return self._password
    
    def set_sock(self, s):
        self._sock = s
    
    def get_sock(self):
        return self._sock

    
