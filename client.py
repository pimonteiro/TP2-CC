from socket import *

import json



timeout = 0.003



#função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
def startConnection(serverName, serverPort, username, password, action, fileName, attempt):
    connectionMessage = {}
    connectionMessage["username"] = username
    connectionMessage["password"] = password
    connectionMessage["action"] = action #upload ou download
    connectionMessage["fileName"] = fileName
    connectionMessage["attempt"] = attempt + 1


    clientSocket = socket(AF_INET, SOCK_DGRAM) #cria um socket UDP

    totalSegments = 0


    connection = {
        'clientsocket': clientSocket,
        'serverPort': serverPort,
        'serverName': serverName,
        'totalSegments': totalSegments
    }


    sendMessage(connection, connectionMessage) #envia a mensagem de ligação

    synAck = recvMessage(connection)

    connection['totalSegments'] = synAck['totalSegments']


    return connection



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



def closeConnection(connection):
    connection["clientsocket"].close()






connection = startConnection("127.0.0.1", 12000, "Luis", "123", "download", "bicho", 1)
print(connection)

closeConnection(connection)