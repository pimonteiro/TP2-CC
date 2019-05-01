import socket
import json
import sys
import os

HOST, PORT = "127.0.0.1", 9999
data = {}
payload = {}
header = {}

payload["filename"] = "exercicio2.pdf"

data["header"] = header
data["payload"] = payload

pieces = []


# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(json.dumps(data).encode(), (HOST, PORT))
received = sock.recv(250)

msg = json.loads(received.decode("utf-8"))
print(str(msg))
sys.exit()

with open("exercicio2.pdf", "wb") as file:
    sock.settimeout(0.003)

    while True:
        try:
            received = sock.recv(250)
            pieces.append(bytes(received))
        
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
