from socket import *


import json


serverPort = 12000



#inicio da conexão
def startServer():

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    totalSegments = 0
    firstSegment = 1

    synAck = {
        'totalSegments': totalSegments,
        'firstSegment': firstSegment,
    }

    synMessage, clientAddress = serverSocket.recvfrom(2048)

    decodeMessage = json.loads(synMessage.decode())


    bytesMessage = json.dumps(synAck).encode()

    serverSocket.sendto(bytesMessage, clientAddress)


    return serverSocket





serverSocket = startServer()