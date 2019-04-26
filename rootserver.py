import socketserver
import socket
import json
import requestHandler

HOST, PORT = "localhost", 9999

server = socketserver.UDPServer((HOST,PORT),None)

while True:
    skt, addr = server.get_request()
    msg = skt[0].decode("utf-8")
    skt = skt[1]
    print("endereco: " + str(addr))
    print("socket: " + str(skt))
    print("mensagem: " + str(msg))
    rh = requestHandler.requestHandler(skt,addr,msg)
    rh.start()

