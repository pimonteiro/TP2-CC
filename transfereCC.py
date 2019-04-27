from socket import *

import json




MAX_MESSAGE_SIZE = PDU = 2048  #packet data unit

HEADBYTES = 20 #tem de ser fixo para se poder calcular a quantidade de pacotes, mas não precisa de ser 20

TYPESYN = 1

TYPEFIN = 2

TYPELOST = 3

TYPENORMAL = 4


def createConnectionObject(socketConnection, address):
    connection = {
        'socket': socketConnection,
        'address': address,
        'totalSegments': 0
    }

    return connection


# Função que estabelece o número de segmentos que vão ser enviados
def total_Segments(data):
    if (data % (PDU + HEADBYTES)) != 0:
        segments = (data / PDU) + 1
    else:
        segments = data / PDU

    return segments


# Função que define o conteúdo do cabeçalho
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

# Criação da mensagem a ser enviada pelo cliente para estabelecer conexão
def createConnectionMsg(username, password, action, fileName):
    connectionMessage = {'header': header(0, TYPESYN, 0), 'content': {}}

    content = {}
    content["username"] = username
    content["password"] = password
    content["action"] = action  # upload ou download
    content["fileName"] = fileName

    connectionMessage['content'] = content

    return connectionMessage


# Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
def startConnection(serverName, serverPort, username, password, action, fileName):
    socketConnection = socket(AF_INET, SOCK_DGRAM) #cria um socket UDP

    connection = createConnectionObject(socketConnection, (serverName, serverPort))

    startConnectionMessage = createConnectionMsg(username, password, action, fileName)

    sendMessage(connection, startConnectionMessage) #envia a mensagem de ligação

    message, address = recvMessage(connection)

    assert connection['address'] == address
    connection['totalSegments'] = message['totalSegments']

    return connection


# Fecha a conexão
def closeConnection(connection):
    connection["socket"].close()


def acceptConnection(connection):
    acceptConnectionMessage = {'header': header(0, TYPESYN, 0), 'content': {}}

    content = {}
    content['totalSegments'] = 0
    acceptConnectionMessage['content'] = content

    sendMessage(connection, acceptConnectionMessage)


# Envia mensagem para o cliente (o address tem o IP do cliente e a porta)
def sendMessage(sock, addr, message):
    bytesMessage = json.dumps(message).encode()
    bytesLength = len(bytesMessage)
    append = ('0' * (MAX_MESSAGE_SIZE - bytesLength)).encode()
    bytesMessage += bytesMessage + append
    sock.sendto(bytesMessage, addr)


#recebe mensagens enviadas pelo cliente para o servidor
def recvMessage(sock):
    bytesMessage, address = sock.recvfrom(MAX_MESSAGE_SIZE)
    message = json.loads(bytesMessage.decode())

    if data['ack'] == TYPEFIN:
        sock.close()
        return 1, {}
    elif data['ack'] == TYPESYN:

    elif data['ack'] == TYPELOST:
        return 3, data

    return message, address


def sendPacketsToClient(sock, add, data_list):
    for i in range(0,len(data_list)):
        data = {
            'checksum': 0,
            'n_sequence': i,
            'content': data_list[i]
        }
        if(i == len(data_list)-1):
            data['ack'] = TYPEFIN;

        sendMessage(sock, add, data)