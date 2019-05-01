from socket import *
import json


MAX_MESSAGE_SIZE = PDU = 2048  #packet data unit

HEADBYTES = 20 #tem de ser fixo para se poder calcular a quantidade de pacotes, mas não precisa de ser 20

# Função que estabelece o número de segmentos que vão ser enviados
def total_Segments(data):
    if (data % (PDU + HEADBYTES)) != 0:
        segments = (data / PDU) + 1
    else:
        segments = data / PDU

    return segments

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