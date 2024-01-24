import socket
from models.Message import Message

class MultiComm(object):
    '''
    classdocs
    '''
    BUFSIZE = 8196

    def __init__(self, s : socket = -1, group = ()):
        '''
        Constructor
        '''
        self._sock = s
        self._group = group
        
    def sendMessage(self, m: Message):
        data = m.marshal()
        self._sock.sendto(data, self._group)
    
    def recvMessage(self) -> Message:
        try:
            m = Message()
            data, address = self._sock.recvfrom(1024)
            if not data:
                return False
            mtype = data[:4]
            size = data[4:8]
            data = data[8:len(data)]
            params = b''.join([mtype,size,data])
            m.unmarshal(params)
        except Exception:
            raise Exception('bad getMessage')
        else:
            return m
    
    def close(self):
        self._sock.close()