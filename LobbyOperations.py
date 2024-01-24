from Comm import Comm
from models.Message import Message
from models.Room import Room
from models.User import User
import models.Payloads as Payloads
import socket
from UserDB import UserDB
import select, socket, sys
from utils import get_free_tcp_port
import threading
from ChatServer import ChatServer
import time

class LobbyOperations(object):

    def __init__(self, server):
        self._server = server
        self._inputs = [server]
        self._outputs = []
        self._Comm = Comm()
        self._currentUsers = []
        self._activeRooms = {}
        self._UserDB = UserDB()

        self.free_multicasts = [['224.3.29.71', 10000], ['224.3.29.81', 10010],  ['224.3.29.81', 10020],  ['224.3.29.91', 10030],  ['224.3.29.91', 10040]]

        self._route = { 'LGIN': self.login,
                        'LOUT': self.logout,
                        'JOIN': self.join,
                        'LTRQ': self.list,
                        'CUSR': self.createUser}
        
    def _getRequest(self):
        req = self._Comm.recvMessage()
        if req == False:
            return False, False
        reqcmd = req.getType()
        reqPayload = req.getPayload()

        return reqcmd,reqPayload
    
    def _putResponseGood(self, message : str):
        resp = Message()
        resp.setType('GOOD')
        resp.setPayload(Payloads.GOOD(message))
        self._Comm.sendMessage(resp)

    def _putResponseError(self, message : str):
        resp = Message()
        resp.setType('ERRO')
        resp.setPayload(Payloads.ERRO(message))
        self._Comm.sendMessage(resp)

    def _updateActiveRooms(self):
        keys_to_remove = []
        for key in self._activeRooms.keys():
            room = self._activeRooms[key]
            if not room['thread'].is_alive():
                self.free_multicasts.append([room['GRP'], room['MCport']])
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._activeRooms[key]

    def login(self, payload : dict):
        #compare passwords & login user
        user = User(payload['username'], payload['password'], self._Comm.get_sock())
        if self._UserDB.search(user.get_name(), user.get_password()):
            self._currentUsers.append(user)
            self._putResponseGood('you are now logged in!')
        else:
            self._putResponseError('invalad username or password.')

    def logout(self, payload : dict):
        #logout user
        for user in self._currentUsers:
            if user.get_name() == payload['username']:
                self._currentUsers.remove(user)
                self._putResponseGood('you are now logged out!')
                return
        self._putResponseError('Could not logout.')

    def join(self, payload : dict):
        self._updateActiveRooms()
        # check if chat room is active
        if payload['room'] in self._activeRooms.keys():
            # is active
            print('sending connection info for active room')
            conns = self._activeRooms[payload['room']]
            resp = Message()
            resp.setType('CONN')
            resp.setPayload(Payloads.CONN(conns['TCPport'], conns['GRP'], conns['MCport']))
            self._Comm.sendMessage(resp)
        else:
            # start thread with new port and multicast
            TCPport = get_free_tcp_port()
            multicast = self.free_multicasts.pop()
            t = threading.Thread(name=payload['room'], target=ChatServer, args=(TCPport, multicast))
            t.start()

            time.sleep(1)
            #send to client
            resp = Message()
            resp.setType('CONN')
            resp.setPayload(Payloads.CONN(TCPport, multicast[0], multicast[1]))
            self._Comm.sendMessage(resp)

            # add room to active rooms
            self._activeRooms[payload['room']] = {'TCPport' : TCPport, 'GRP' : multicast[0], 'MCport': multicast[1], 'thread': t}
            print('added new active room')

    def list(self, payload : dict):
        self._updateActiveRooms()
        print('sending list')
        rooms = [str(key) for key in self._activeRooms.keys()]
        resp = Message()
        resp.setType('LTRS')
        resp.setPayload(Payloads.LTRS(rooms))
        self._Comm.sendMessage(resp)

    def createUser(self, payload : dict):
        self._UserDB.newUser(payload['username'], payload['password'])
        self._putResponseGood(f'user created')

    def run(self):
        while self._inputs:
            readable, writable, exceptional = select.select(
                self._inputs, self._outputs, self._inputs)
            
            for s in readable:
                if s is self._server:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    self._inputs.append(connection)
                    print(f'new connection {client_address}')
                else:
                    self._Comm = Comm(s)
                    cmd, payload = self._getRequest()
                    if cmd: #cmd and payload
                        self._route[cmd](payload)
                    else:
                        self._inputs.remove(s)
                        s.close()
                        print(f'Closed connection to {s}')

            for s in exceptional:
                self._inputs.remove(s)
                if s in self._outputs:
                    self._outputs.remove(s)
                s.close()
                print(f'Closed connection to {s}')