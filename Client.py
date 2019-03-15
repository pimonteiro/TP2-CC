from socket import *
from struct import *
import time

serverName = '127.0.0.1'

serverPort = 12000

timeout = 0.003



#função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
def startConnectionRequest(username, password, action, fileName, attempt):
    client = {}
    client["username"] = username
    client["password"] = password
    client["action"] = action
    client["fileName"] = fileName
    client["attempt"] = attempt + 1

    return client


#função que tenta novamente estabelecer a ligação caso não haja resposta do servidor
def retryConnection(client):

    if timeout > 0.003 and client["attempt"] <= 3:
        startConnectionRequest(client["username"], client["password"], client["action"], client["fileName"], client["attempt"])

    else:
        return -1

    return client


#cria o cabeçalho dos segmentos
def header(checksum, ack, n_sequence):
    head = {}
    head["checksum"] = checksum
    if ack == 3:
        lista = [] # vai ter função do estado
        head["ack"] = "3," +  ",".join(str(x) for x in lista)
    else:
        head["ack"] = str(ack)

    head["n_sequence"] = n_sequence

    return header





clientSocket = socket(AF_INET, SOCK_DGRAM)  # tipo de conexão e protocolo de transporte - UDP
message = input('Input lowercase sentence:')
clientSocket.sendto(message.encode(), (serverName,
                                           serverPort))  # converte a string para byte -enconde - send to - cola o destino à mensagem e manda o resultado para clientSocket
modifiedMessage, serverAddress = clientSocket.recvfrom(
        2048)  # recebe uma mensagem da rede no máximo de 2048 bytes qdo um pacote chega da internet ao socket do cliente os dados do pacote vão para a variável modifeidMessage e o endereço donde veio o pacote vai para serverAddress
print(modifiedMessage.decode())  # imprime a mensagem enviada
clientSocket.close()  # fecha a conexão

