import message
import json

from socket import *


class ConnectionException(Exception):
    pass


class Connection:

    MAX_MESSAGE_SIZE = 2048

    def __init__(self, destIP, destPort, sourceIP="", sourcePort=""):
        self.destIP = destIP
        self.destPort = destPort
        self.sourceIP = sourceIP
        self.sourcePort = sourcePort
        self.__socket = None

    # Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
    def connect(self, username, password, action, filename):
        if self.__socket is not None:
            raise ConnectionException('Conexão previamente estabelecida')

        self.__socket = socket(AF_INET, SOCK_DGRAM)

        msg = message.ConnectionMessage(username=username, password=password, action=action, filename=filename)

        self.send(msg)

        #quando só tem uma thread
        (msg, _) = self.receive()


        # mudar para quando não receber o total segm nem o fin voltar enviar a msg inicial
        if msg.get_type() not in (message.TotalSegMessage.TYPE, message.FinMessage.TYPE):
            self.__socket.close()
            self.__socket = None


        #quando recebe um fin o cliente manda fin e fecha o socket
        elif msg.get_type() == message.FinMessage.TYPE:
            msg = message.FinMessage()
            self.send(msg)
            self.__socket.close()
            self.__socket = None

        else
            msg = message.AckClientMessage()
            self.send(msg)


    def close(self):
        if self.__socket is None:
            raise ConnectionException('Conexão não foi previamente estabelecida')
        msg = message.FinMessage()

        self.send(msg)

        self.__socket.close()
        self.__socket = None

    def send(self, msg):
        msgbytes = message.Handler.serialize(msg)
        self.__socket.sendto(msgbytes, (self.destIP, self.destPort))

    def receive(self):
        msgbytes, address = self.__socket.recvfrom(Connection.MAX_MESSAGE_SIZE)
        msg = message.Handler.deserialize(msgbytes)

        return msg, address

    def __str__(self):
        value = \
        {
            "destIP": destIP,
            "destPort": destPort,
            "sourceIP": sourceIP,
            "sourcePort": sourcePort,
            "connected": self.__socket is not None
        }

        return "connection:" + str(value)






def acceptConnection(connection):
    acceptConnectionMessage = {'header': header(0, TYPESYN, 0), 'content': {}}

    content = {}
    content['totalSegments'] = 0
    acceptConnectionMessage['content'] = content

    sendMessage(connection, acceptConnectionMessage)
