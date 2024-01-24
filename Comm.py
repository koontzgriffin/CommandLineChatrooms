import socket
from models.Message import Message

class Comm(object):
    '''
    classdocs
    '''
    BUFSIZE = 8196

    def __init__(self, s : socket = -1):
        '''
        Constructor
        '''
        self._sock = s
    
    def get_sock(self):
        return self._sock

    def _loopRecv(self, size: int):
        data = bytearray(b" "*size)
        mv = memoryview(data)
        while size:
            rsize = self._sock.recv_into(mv,size)
            if rsize == 0:
                return False
            mv = mv[rsize:]
            size -= rsize
        return data
        
    def sendMessage(self, m: Message):
        data = m.marshal()
        self._sock.sendall(data)
    
    def recvMessage(self) -> Message:
        try:
            m = Message()
            mtype = self._loopRecv(4)
            size = self._loopRecv(4)
            data = self._loopRecv(int(size.decode('utf-8')))
            params = b''.join([mtype,size,data])
            m.unmarshal(params)
        except:
            return False
        else:
            return m
    
    def close(self):
        self._sock.close()