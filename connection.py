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

    def __init__(self, destIp=None, destPort=None, sourceIp=None, sourcePort=None):
        self.destIp = destIp
        self.destPort = destPort
        self.sourceIp = sourceIp
        self.sourcePort = sourcePort
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.status = Connection.DISCONNECTED

        if sourceIp is not None and sourcePort is not None:
            self.__socket.bind((self.sourceIp, self.sourcePort))

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

    def get_status(self):
        return self.status

    def close(self):
        if self.__socket is None:
            raise ConnectionException('Conexão não foi previamente estabelecida')

        self.__socket.close()
        self.__socket = None
        self.status = Connection.CLOSED

    def send(self, msg):
        msgbytes = msg.classToBinary()
        assert len(msgbytes) < Connection.MAX_MESSAGE_SIZE
        self.__socket.sendto(msgbytes, (self.destIp, self.destPort))

    def receive(self):
        msgbytes, address = self.__socket.recvfrom(Connection.MAX_MESSAGE_SIZE)
        msg = Message()
        msg.binaryToClass(msgbytes)

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
