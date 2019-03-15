from socket import *


serverPort = 12000

PDU = 548

HEADBYTES = 20 #tem de ser fixo para se poder calcular a quantidade de pacotes

#conta o número de segmentos que vão ser enviados
def n_Segments(data):
    if (data % (PDU + HEADBYTES)) != 0:
        segments = (data / PDU) + 1
    else:
        segments = data / PDU

    return segments






serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))  # atribui a porta 12000 ao socket do servidor
print("The server is ready to receive")
while True:
    message, clientAddress = serverSocket.recvfrom(
           2048)  # qdo um pacote chega da internet ao socket do server os dados do pacote vão para message e end donde veio o pacote vai para clientAddress
    modifiedMessage = message.decode().upper()  # converte a mensagem numa string e depois passa para maiusculas
    serverSocket.sendto(modifiedMessage.encode(),
                            clientAddress)  # envia o segmento com o endereço do cliente colado aos dados para o cliente