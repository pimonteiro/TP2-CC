from socket import *

from transfereCC import *


# import nome do import transferCC.nomedafuncao


#inicio da conexão adaptar as funções do recvfrom(2048) e do sendto() - estas funcoes podem ter de estar no transfereCC
def startServer(port):

    socketConnection = socket(AF_INET, SOCK_DGRAM)
    socketConnection.bind(('', port))
    connection = createConnectionObject(socketConnection, ('*', port))

    while True:
        message, address = recvMessage(connection)
        if message['header']['type'] == TYPESYN:
            newConnection = createConnectionObject(socketConnection, address)
            # Verifica:
            #   Usuario/Senha
            #   Ficheiro
            #   Se alguma coisa estiver errada nao aceita conexao
            #   e envia um FIN. Caso contratrio prossegue com um
            #   SIN.

            # Guardar a new connection num mapping (i.e. cache)
            acceptConnection(newConnection)
            print("Type syn")
        if message['header']['type'] == TYPENORMAL:
            print("Type normal")




serverPort = 12000
serverSocket = startServer(serverPort)