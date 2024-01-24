import socket
import struct
from Comm import Comm
from MultiComm import MultiComm
from ChatOperations import ChatOperations

def ChatServer(port, multicast):
    print('New Chat Server Thread Started...')
    #  create the TCP socket
    #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    TCPsoc = socket.socket()

    # set blocking 0
    TCPsoc.setblocking(0)

    # bind to local host:5000
    TCPsoc.bind(("localhost",port))
                   
    # make passive with backlog=5
    TCPsoc.listen(5)

    # create multicast socket
    multicast_group = multicast[0]
    server_address = ('', multicast[1])

    # Create the socket
    MCsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the time-to-live (TTL) for the socket
    ttl = struct.pack('b', 1)
    MCsock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


    MCComm = MultiComm(MCsock, (multicast_group, server_address[1]))
    
    # wait for incoming connections
    print("Chat server listening on ", port)

    # run ops
    chatOps = ChatOperations(TCPsoc, MCComm)
    chatOps.run()

    # close the server socket
    TCPsoc.close()