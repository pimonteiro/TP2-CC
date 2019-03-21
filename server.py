from socket import *

from transfereCC import *

import json


serverPort = 12000


def createSynAck():
    synAck = {'header': header(0,1,1), 'totalSegments': 100, 'content': {}}

    return synAck


#inicio da conexão adaptar as funções do recvfrom(2048) e do sendto() - estas funcoes podem ter de estar no transfereCC
def startServer():

    serverSocket = socket(AF_INET, SOCK_DGRAM)

    serverSocket.bind(('', serverPort))

    synAck = createSynAck()

    print(synAck)

    clientMsg = rcvMsgFromClient(serverSocket)

    sendMsgToClient(synAck, clientMsg)


    return serverSocket





serverSocket = startServer()