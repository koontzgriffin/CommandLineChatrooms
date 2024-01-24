from Comm import Comm
from MultiComm import MultiComm
from models.Message import Message
from models.User import User
from models.Room import Room
from models.Chat import Chat
import models.Payloads as Payloads
import socket
import select
import sys
import os
import struct

class ClientOperations(object):

    def __init__(self, s : socket):
        self.TCPcomm = Comm(s)
        self.MCsoc = socket.socket()
        self.MCcomm = MultiComm()
        self._currentUser = User()
        self._currentRoom = ''
        self._prevChats = []

    def _return_to_lobby(self):
        self.TCPcomm.close()
        self.MCcomm.close()

        s = socket.socket()
        # connect to localhost:5000
        s.connect(("localhost",50000))
        self.TCPcomm = Comm(s)

    def login(self, user : User):
        request = Message()
        request.setType('LGIN')
        request.setPayload(Payloads.LGIN(user))
        self.TCPcomm.sendMessage(request)
        response = self.TCPcomm.recvMessage()
        if response.getType() == 'GOOD':
            self._currentUser = user
            print(response.getPayload()['message'])
            return 1
        elif response.getType() == 'ERRO':
            print(response.getPayload()['message'])
            return -1
        else:
            raise Exception('Unexpected Response')

    def logout(self, user : User):
        request = Message()
        request.setType('LOUT')
        request.setPayload(Payloads.LOUT(user))
        self.TCPcomm.sendMessage(request)
        response = self.TCPcomm.recvMessage()
        if response.getType() == 'GOOD':
            self._currentUser = User()
            print(response.getPayload()['message'])
            return 1
        elif response.getType() == 'ERRO':
            print(response.getPayload()['message'])
            return -1
        else:
            raise Exception('Unexpected Response')
        
    def createUser(self, user : User):
        request = Message()
        request.setType('CUSR')
        request.setPayload(Payloads.CUSR(user))
        self.TCPcomm.sendMessage(request)
        response = self.TCPcomm.recvMessage()
        if response.getType() == 'GOOD':
            print(response.getPayload()['message'])
            return 1
        elif response.getType() == 'ERRO':
            print(response.getPayload()['message'])
            return -1
        else:
            raise Exception('Unexpected Response')
        
    def join(self, room : Room):
        request = Message()
        request.setType('JOIN')
        request.setPayload(Payloads.JOIN(room))
        self.TCPcomm.sendMessage(request)
        response = self.TCPcomm.recvMessage()
        if response.getType() == 'CONN':
            port = response.getPayload()['TCPport']
            # disconect from lobby server
            self.TCPcomm.close()
            # connect to room TCPserver
            commsoc = socket.socket()
            print(f'attempting to connect to {port}')
            commsoc.connect(("localhost", port))
            self.TCPcomm = Comm(commsoc)

            # connect to the room Multicast
            multicast_group = response.getPayload()['GRP']
            multicast_port = response.getPayload()['MCport']

            self.MCsoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Set the SO_REUSEPORT option
            self.MCsoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            # Bind the socket to the server address
            self.MCsoc.bind(('', multicast_port))
            # Tell the operating system to add the socket to the multicast group
            group = socket.inet_aton(multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.MCsoc.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            # initialize MCcomm
            self.MCcomm = MultiComm(self.MCsoc, (multicast_group, multicast_port))
            # set the current room
            self._currentRoom = room.get_name()
            # receive the prevChats
            msg = self.TCPcomm.recvMessage()
            if msg.getType() == 'PREV':
                chats = msg.getPayload()['chats']
                self._prevChats = []
                for chat in chats:
                    c = Chat()
                    c.from_dict(chat)
                    self._prevChats.append(c)
            elif msg.getType() == 'ERRO':
                print(response.getPayload()['message'])
                return -1
            else:
                raise Exception('Unexpected Response')
            return 1
        elif response.getType() == 'ERRO':
            print(response.getPayload()['message'])
            return -1
        else:
            raise Exception('Unexpected Response')    

    def list(self):
        request = Message()
        request.setType('LTRQ')
        request.setPayload(Payloads.LTRQ())
        self.TCPcomm.sendMessage(request)
        response = self.TCPcomm.recvMessage()
        if response.getType() == 'LTRS':
            rooms = response.getPayload()['rooms']
            print('\n---Active Rooms---\n')
            for room in rooms: # print the room names
                print(f'  - {room}\n')
            return 1
        elif response.getType() == 'ERRO':
            print(response.getPayload()['message'])
            return -1
        else:
            raise Exception('Unexpected Response')
        
        
    def sendChat(self, chat):
        c = Chat(self._currentUser.get_name(), self._currentRoom, chat)
        request = Message()
        request.setType('CHAT')
        request.setPayload(Payloads.CHAT(c))
        self.TCPcomm.sendMessage(request)
        response = self.TCPcomm.recvMessage()
        if response.getType() == 'GOOD':
            return 1
        elif response.getType() == 'ERRO':
            print(response.getPayload()['message'])
            return -1
        else:
            raise Exception('Unexpected Response')
        
    def addPrevChat(self, chat : Chat):
        if len(self._prevChats) < 10:
            self._prevChats.append(chat)
        else:
            self._prevChats.pop(0)
            self._prevChats.append(chat)
        
    def printChat(self):
        os.system('clear')
        for chat in self._prevChats:
            print(f'{chat.get_contents()}\n~{chat.get_creator()} @{chat.get_datetime()}\n')
        print('enter a chat ("\quit" to leave)> ')

    def chatUI(self):
        loop = True
        self.printChat()
        while loop:
            inputs = [sys.stdin, self.MCsoc]
            outputs = []
            excepts = []
            ready_inputs, ready_outputs, ready_excepts = select.select(inputs, outputs, excepts, 1)

            for ready_input in ready_inputs:
                if ready_input == sys.stdin:
                    chat = input()
                    if chat == '\quit':  # Check for '\quit'
                        print('Quitting')
                        loop = False # stop the loop
                        break
                    self.sendChat(chat)
                elif ready_input == self.MCsoc:
                    msg = self.MCcomm.recvMessage()
                    chat = Chat()
                    chat.from_dict(msg.getPayload())
                    self.addPrevChat(chat)
                    self.printChat()
        self._prevChats = []
        os.system('clear')
        self._return_to_lobby()

    def run(self):
        while True:
            command = input("enter a command> ")
            args = command.split()
            if len(args) < 1:
                continue
            elif args[0] == "login":
                if len(args) < 3:
                    print('missing arguments. -"login <username> <password>"')
                else:
                    print("loging in...")
                    self.login(User(args[1], args[2]))

            elif args[0] == "list": 
                print("listing...")
                self.list()

            elif args[0] == "newuser":
                print("creating user...")
                if len(args) < 3:
                    print('missing arguments. -"newuser <name> <password>"')
                else:
                    u = User(args[1], args[2])
                    self.createUser(u)

            elif args[0] == "logout":
                print("logging out...")
                self.logout(self._currentUser)

            elif args[0] == "join":
                if len(args) < 2:
                    print('missing arguments.  -"join <roomname>"')
                else:
                    print('joining room...')
                    room = Room(args[1])
                    self.join(room)
                    self.chatUI()

            elif args[0] == "help":
                print('Commands:\n -"login <username> <password>"\n -"list"\n -"newuser <username> <password>"\n -"join <roomname>"\n -"logout"\n -"help"\n -"exit"')
            
            elif args[0] == 'exit':
                print('exiting...')
                break

            else:
                print('Invalad command. -"help" for list off commands.')