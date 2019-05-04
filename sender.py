import socket
import json
import sys
import os
from struct import pack
from struct import unpack
from message import *

HOST, PORT = "127.0.0.1", 9999
send = Message()
send.makeConnectionMessage("teste", "123", "GET", "setup_JustNN.exe")


# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(send.classToBinary(), (HOST, PORT))
received = sock.recv(250)

checksum, size, nsequence, tipo = unpack('LHLc', received[:25])
tipo = tipo.decode('utf-8')

if tipo == Message.TYPE_TSG:
    msg = json.loads(received[25:].decode('utf-8'))
else:
    msg = None

destport = int(msg["port"])

send.makeMessage("", Message.TYPE_ACK, 0)
sock.sendto(send.classToBinary(), ("127.0.0.1", destport))
pieces = []


with open("setup_JustNN.exe", "wb") as file:
    sock.settimeout(3)

    while True:
        try:
            received = sock.recv(570)
            pieces.append(received[25:])
        
        except:
            print("tamanho do array = " + str(len(pieces)))
            print("deu timeout")
            for chunk in pieces:
                file.write(chunk)

            print("escreveu tudo")
            file.close()
            sock.close()
            print("fechou arquivo")
            sys.exit()
