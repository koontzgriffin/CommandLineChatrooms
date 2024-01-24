import socket
from ClientOperations import ClientOperations
import time

if __name__ == "__main__":
    # create the socket
    # defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    commsoc = socket.socket()
    
    # connect to localhost:5000
    commsoc.connect(("localhost",50000))
    
    # run the application protocol
    print('Starting interface...')
    Operations = ClientOperations(commsoc)
    Operations.run()

    # close the comm socket
    commsoc.close()