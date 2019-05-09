from message import Message
import json
import threading

from socket import *


class ConnectionException(Exception):
    pass


class Connection:

    MAX_MESSAGE_SIZE = 2048

    DISCONNECTED = "DISCONNECTED"

    CONNECTING = "CONNECTING"

    CONNECTED = "CONNECTED"

    RECEIVING_NORMAL = "RECEIVING_NORMAL"

    RECEIVING_MISSING = "RECEIVING_MISSING"

    CLOSED = "CLOSED"

    def __init__(self, destIp=None, destPort=None):
        self.destIp = destIp
        self.destPort = destPort
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.status = Connection.DISCONNECTED

        self.__socket.bind(("127.0.0.1", 0))
        self.sourcePort = self.__socket.getsockname()[1]
        self.sourceIp = self.__socket.getsockname()[0]

        self.lock = threading.Lock()

    def set_status(self, status):
        assert status in {
            Connection.DISCONNECTED,
            Connection.CONNECTING,
            Connection.CONNECTED,
            Connection.RECEIVING_NORMAL,
            Connection.RECEIVING_MISSING,
            Connection.CLOSED
        }

        with self.lock:
            self.status = status

    def get_status(self):
        with self.lock:
            return self.status

    def set_port(self, pp):
        with self.lock:
            self.destPort = pp

    def close(self):
        if self.__socket is None:
            raise ConnectionException('Conexão não foi previamente estabelecida')

        with self.lock:
            self.__socket.close()
            self.__socket = None
            self.status = Connection.CLOSED

    def get_SourcePort(self):
        with self.lock:
            return self.sourcePort

    def set_timeout(self,time):
        with self.lock:
            self.__socket.settimeout(time)

    def send(self, msg):
        msgbytes = msg.classToBinary()
        assert len(msgbytes) < Connection.MAX_MESSAGE_SIZE

        with self.lock:
            self.__socket.sendto(msgbytes, (self.destIp, self.destPort))

    def receive(self):
        with self.lock:
            msgbytes, address = self.__socket.recvfrom(Connection.MAX_MESSAGE_SIZE)
        
        msg = Message()
        msg.binaryToClass(msgbytes)
        if msg.verifyIntegrity() == False:
            msg = None
        return msg, address

    def receive_lite(self):
        with self.lock:
            msgbytes, _ = self.__socket.recvfrom(Connection.MAX_MESSAGE_SIZE)
        
        return msgbytes

    def keepAlive(self, msg):        
        with self.lock:
            self.__socket.sendto(msg, (self.destIp, self.destPort))

    def __str__(self):
        value = \
        {
            "destIp": self.destIp,
            "destPort": self.destPort,
            "sourceIp": self.sourceIp,
            "sourcePort": self.sourcePort,
            "connected": self.__socket is not None
        }

        return "connection:" + str(value)
