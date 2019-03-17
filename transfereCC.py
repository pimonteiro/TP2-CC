from socket import *

import json



timeout = 0.003


PDU = 548 #packet data unit

HEADBYTES = 20 #tem de ser fixo para se poder calcular a quantidade de pacotes, mas não precisa de ser 20


TYPESYN = 1

TYPEFIN = 2

TYPELOST = 3

#conta o número de segmentos que vão ser enviados
def total_Segments(data):
    if (data % (PDU + HEADBYTES)) != 0:
        segments = (data / PDU) + 1
    else:
        segments = data / PDU

    return segments


#cria o cabeçalho dos segmentos
def header(checksum, type, n_sequence):
    head = {}
    head['checksum'] = checksum
    if type == 3:
        lista = [] # vai ter função do estado
        head['type'] = "3," + ",".join(str(x) for x in lista)
    else:
        head['type'] = str(type)

    head['n_sequence'] = n_sequence

    return head


def createConnectionMessage(serverName, serverPort, username, password, action, fileName, attempt):
    connectionMessage = {'header': header(0, TYPESYN, 1), 'content': {}}

    content = {}
    content["username"] = username
    content["password"] = password
    content["action"] = action  # upload ou download
    content["fileName"] = fileName
    content["attempt"] = attempt + 1

    connectionMessage['content'] = content

    return connectionMessage



#recebe mensagem
def recvMessage(connection):
   newMessage, serverAddress = connection['clientsocket'].recvfrom(2048)

   decodeMessage = json.loads(newMessage.decode())

   return decodeMessage



#envia mensagem
def sendMessage(connection, message):
    bytesMessage = json.dumps(message).encode()

    connection["clientsocket"].sendto(bytesMessage, (connection["serverName"], connection["serverPort"]))



#função que tenta novamente estabelecer a ligação caso não haja resposta do servidor
def retryConnection(connection, connectionMessage):

    if timeout > 0.003 and connectionMessage["attempt"] <= 3:
        startConnection(connection["serverName"], connection["serverPort"], connectionMessage["username"],
                        connectionMessage["password"], connectionMessage["action"],
                        connectionMessage["fileName"], connectionMessage["attempt"])

    else:
        return -1

    return connection




#função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
def startConnection(serverName, serverPort, username, password, action, fileName, attempt):
    connectionMessage = createConnectionMessage(serverName, serverPort, username, password, action, fileName, attempt)

    clientSocket = socket(AF_INET, SOCK_DGRAM) #cria um socket UDP


    connection = {
        'clientsocket': clientSocket,
        'serverPort': serverPort,
        'serverName': serverName,
        'totalSegments': 0
    }


    sendMessage(connection, connectionMessage) #envia a mensagem de ligação

    synAck = recvMessage(connection)

    connection['totalSegments'] = synAck['totalSegments']


    return connection


#fecha a conexão
def closeConnection(connection):
    connection["clientsocket"].close()

