import socket
import json

HOST, PORT = "127.0.0.1", 9999
data = {}
data["username"] = "leonardo"


# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(json.dumps(data).encode(), (HOST, PORT))
received = sock.recv(1024)

print("Sent:     {}".format(data))
print("Received: {}".format(received.decode("utf-8")))