from enum import Enum
import json

class Message(object):
    '''
    classdocs
    '''
    # Constants
    CMDS = Enum('CMDS', {'LGIN': 'LGIN', 'LOUT': 'LOUT', 'CUSR': 'CUSR', 'ROOM':'ROOM', 'JOIN':'JOIN', 
                'CONN':'CONN', 'CHAT':'CHAT', 'DELR': 'DELR', 'GOOD': 'GOOD', 'ERRO': 'ERRO','LTRQ':'LTRQ', 'LTRS':'LTRS', 'PREV':'PREV'})

    def __init__(self):
        '''
        Constructor
        '''
        self._cmd = Message.CMDS['GOOD']
        self._payload = dict() # dictionary

    def __str__(self):
        return f'Type = {self.getType()}, Payload = {self.getPayload()}' 
        
    def reset(self):
        self._cmd = Message.CMDS['GOOD']
        self._payload = dict()
    
    def setType(self, mtype: str):
        self._cmd = Message.CMDS[mtype]
        
    def getType(self) -> str:
        return self._cmd.value
    
    def setPayload(self, d: dict):
        self._payload = d
        
    def getPayload(self) -> dict:
        return self._payload
        
    def marshal(self) -> str:
        size = len(json.dumps(self._payload))
        header = '{}{:04}'.format(self._cmd.value, size)
        return b''.join([header.encode('utf-8'), json.dumps(self._payload).encode('utf-8')])
    
    def unmarshal(self, value: bytes):
        self.reset()
        if value:
            self._cmd = Message.CMDS[value[0:4].decode('utf-8')]
            self._payload = json.loads(value[8:].decode('utf-8'))