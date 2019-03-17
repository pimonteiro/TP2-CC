from socket import *


import json


serverPort = 12000

PDU = 548

HEADBYTES = 20 #tem de ser fixo para se poder calcular a quantidade de pacotes, mas não precisa de ser 20


#conta o número de segmentos que vão ser enviados
def total_Segments(data):
    if (data % (PDU + HEADBYTES)) != 0:
        segments = (data / PDU) + 1
    else:
        segments = data / PDU

    return segments


#cria o cabeçalho dos segmentos
def header(checksum, ack, n_sequence):
    head = {}
    head['checksum'] = checksum
    if ack == 3:
        lista = [] # vai ter função do estado
        head['ack'] = "3," + ",".join(str(x) for x in lista)
    else:
        head['ack'] = str(ack)

    head['n_sequence'] = n_sequence

    return head



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