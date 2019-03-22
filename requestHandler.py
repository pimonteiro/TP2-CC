import threading
import socket
import json
import sys

class requestHandler(threading.Thread):
    def __init__(self, socket, client_address, message):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = client_address
        self.data = json.loads(message)["content"]
        self.header = {}
        self.pieces = []
        self.on = True

    def run(self):
        if(self.auth()):
            if(self.data["action"] == "GET"):
                #função de mandar dividir e meter os pedaços no array pieces
                #iniciar a thread do agent udp para mandar os pedaços dos arquivos

            else:
                #fazer um pedido de get para o endereço do client mas na porta que o servidor é executado.

            self.socket.sendto(("from thread: ola\n").encode(),self.address)
        
        else:
            self.socket.sendto(("from thread: autenticacao invalida").encode(),self.address)


    #autenticacao do cliente para depois mandar os arquivos
    def auth(self):
        if (self.data["username"] == "teste" and self.data["password"] == "123"):
            return True
        
        else:
            return False

    




    
        