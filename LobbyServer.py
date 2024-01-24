import socket
from Comm import Comm
from LobbyOperations import LobbyOperations

if __name__ == "__main__":
    # create the server socket
    #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    serversoc = socket.socket()

    # set blocking 0
    serversoc.setblocking(0)

    # bind to local host:5000
    serversoc.bind(("localhost",50000))
                   
    # make passive with backlog=5
    serversoc.listen(5)
    
    # wait for incoming connections
    while True:
        print("Listening on ", 50000)

        # run ops
        lobbyOps = LobbyOperations(serversoc)
        lobbyOps.run()
    
    # close the server socket
    serversoc.close()