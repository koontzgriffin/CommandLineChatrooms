from datetime import datetime

class Chat(object):
    
    def __init__(self, creator = '', room = '', contents = ''):
        self._creator = creator
        self._room = room
        self._contents = contents
        self._datetime = datetime.now().strftime("%H:%M:%S, %m/%d/%Y")

    def set_creator(self, creator):
        self._creator = creator

    def get_creator(self):
        return self._creator
    
    def set_room(self, room):
        self._room = room
    
    def get_room(self):
        return self._room
    
    def set_contents(self, contents):
        self._contents = contents

    def get_contents(self):
        return self._contents
    
    def set_datetime(self):
        self._datetime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    def get_datetime(self):
        return self._datetime
    
    def from_dict(self, chat : dict):
        self._creator = chat['creator']
        self._room = chat['room']
        self._contents = chat['contents']
        self._datetime = chat['datetime']

    def to_dict(self):
        return {'creator' : self._creator, 'room' : self._room, 'contents' : self._contents, 'datetime': self._datetime}