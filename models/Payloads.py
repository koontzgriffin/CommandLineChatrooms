from models.User import User
from models.Room import Room
from models.Chat import Chat

def LGIN(user : User):
    return dict(username = user.get_name(), password = user.get_password())

def LOUT(user : User):
    return dict(username = user.get_name())

def CUSR(user : User):
    return dict(username = user.get_name(), password=user.get_password())

def ROOM(room : Room):
    return dict(name=room.get_name())

def JOIN(room : Room):
    return dict(room=room.get_name())

def GOOD(msg):
    return dict(message=msg)

def ERRO(msg):
    return dict(message=msg)

def CONN(tcp, group, mcast):
    return dict(TCPport=tcp, GRP=group, MCport=mcast)

def LTRQ():
    return dict()

def LTRS(rooms : list):
    return dict(rooms=rooms)

def DELR(roomname, user):
    return dict(name=roomname, owner=user)

def CHAT(chat : Chat):
    return dict(creator=chat.get_creator(), room=chat.get_room(), contents=chat.get_contents(), datetime=chat.get_datetime())

def PREV(chats : list):
    return dict(chats=chats)