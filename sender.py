import socket
import json
import sys
import os
from struct import pack
from struct import unpack
from message import *

HOST, PORT = "127.0.0.1", 9999
send = Message()
send.makeConnectionMessage("teste", "123", "GET", "porra.txt")


# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(send.classToBinary(), (HOST, PORT))
received = sock.recv(1024)

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


with open("porra.txt", "wb") as file:
    sock.settimeout(0.3)

    while True:
        try:
            received = sock.recv(2048)
            pieces.append(received)
        
        except:
            print("tamanho do array = " + str(len(pieces)))
            for chunk in pieces:
                file.write(chunk[25:])

            file.close()
            sock.close()
            print("done")
            sys.exit()
