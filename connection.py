from message import Message
import json

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

        tmp_sock = Connection.get_my_ip()
        self.__socket.bind((tmp_sock, 0))
        self.sourcePort = self.__socket.getsockname()[1]
        self.sourceIp = self.__socket.getsockname()[0]

    @staticmethod
    def get_my_ip():
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        tmp = s.getsockname()[0]
        s.close()
        return tmp

    def set_status(self, status):
        assert status in {
            Connection.DISCONNECTED,
            Connection.CONNECTING,
            Connection.CONNECTED,
            Connection.RECEIVING_NORMAL,
            Connection.RECEIVING_MISSING,
            Connection.CLOSED
        }
        self.status = status

    def get_destIP(self):
        return self.destIp

    def get_status(self):
        return self.status

    def set_port(self, pp):
        self.destPort = pp

    def close(self):
        if self.__socket is None:
            raise ConnectionException('Conexão não foi previamente estabelecida')

        self.__socket.close()
        self.__socket = None
        self.status = Connection.CLOSED

    def get_SourcePort(self):
        return self.sourcePort

    def set_timeout(self,time):
        self.__socket.settimeout(time)

    def send(self, msg):
        msgbytes = msg.classToBinary()
        assert len(msgbytes) < Connection.MAX_MESSAGE_SIZE
        print(self)
        self.__socket.sendto(msgbytes, (self.destIp, self.destPort))

    def receive(self):
        msgbytes, address = self.__socket.recvfrom(Connection.MAX_MESSAGE_SIZE)
        msg = Message()
        msg.binaryToClass(msgbytes)
        if msg.verifyIntegrity() == False:
            msg = None
        return msg, address

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
