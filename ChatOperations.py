from Comm import Comm
from MultiComm import MultiComm
from models.Message import Message
from models.Room import Room
from models.User import User
from models.Chat import Chat
import models.Payloads as Payloads
import socket
from UserDB import UserDB
import select, socket, sys

class ChatOperations(object):

    def __init__(self, TCPserver : socket, Multicast : MultiComm):
        # TCP 
        self._TCPserver = TCPserver
        self._inputs = [TCPserver]
        self._outputs = []
        self._TCPComm = Comm()

        # Multicast
        self._MCComm = Multicast

        self._prevChats = []

        self._route = {'CHAT':self.received_chat}

    def _getRequest(self):
        req = self._TCPComm.recvMessage()
        if req == False: 
            return False, False
        reqcmd = req.getType()
        reqPayload = req.getPayload()
        return reqcmd,reqPayload
    
    def _putResponseGood(self, message : str):
        resp = Message()
        resp.setType('GOOD')
        resp.setPayload(Payloads.GOOD(message))
        self._TCPComm.sendMessage(resp)

    def _putResponseError(self, message : str):
        resp = Message()
        resp.setType('ERRO')
        resp.setPayload(Payloads.ERRO(message))
        self._TCPComm.sendMessage(resp)

    def addPrevChat(self, chat : Chat):
        if len(self._prevChats) < 10:
            self._prevChats.append(chat)
        else:
            self._prevChats.pop(0)
            self._prevChats.append(chat)

    def sendPrevChats(self):
        msg = Message()
        msg.setType('PREV')
        chats = []
        for chat in self._prevChats:
            chats.append(chat.to_dict())
        msg.setPayload(Payloads.PREV(chats))
        self._TCPComm.sendMessage(msg)

    def brodcast_chat(self, chat : dict):
        msg = Message()
        msg.setType('CHAT')
        msg.setPayload(chat)
        self._MCComm.sendMessage(msg)

    def received_chat(self, payload : dict):
        chat = Chat()
        chat.from_dict(payload)
        self.addPrevChat(chat)

        contents =  payload['contents']
        self._putResponseGood(f'got your chat: "{contents}"')
        self.brodcast_chat(payload)

    def run(self):
        connections = 0
        while self._inputs:
            readable, writable, exceptional = select.select(
                self._inputs, self._outputs, self._inputs)

            for s in readable:
                if s is self._TCPserver:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    self._inputs.append(connection)
                    print(f'new chat connection {client_address}')
                    connections += 1
                    # send prev chats
                    self._TCPComm = Comm(connection)
                    self.sendPrevChats()

                else:
                    self._TCPComm = Comm(s)
                    cmd, payload = self._getRequest()
                    if cmd: 
                        self._route[cmd](payload)
                    else:
                        connections -= 1
                        self._inputs.remove(s)
                        s.close()
                        print(f'Closed connection to {s}')

            for s in exceptional:
                self._inputs.remove(s)
                if s in self._outputs:
                    self._outputs.remove(s)
                s.close()
                print(f'Closed connection to {s}')
            
            if connections == 0:
                break
        
        print('chat server shutting down')
        self._TCPComm.close()
        self._MCComm.close()