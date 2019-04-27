import threading
import socket
import json
import sys
import transfereCC

class requestHandler(threading.Thread):
    def __init__(self, socket, client_address, message):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = client_address
        self.data = json.loads(message)["content"]
        self.header = {}
        self.pieces = []
        self.attemp = 0
        self.on = True
        

    def run(self):
        if(self.auth()):
            
            if self.data["action"] == "GET":
                # função de mandar dividir e meter os pedaços no array pieces

                self.pieces = transfereCC.sendFirstMsgToClient(self.socket,self.address,text)
                # Verificar se recebeu
                try:
                    text = transfereCC.recvPacket(self.socket)
                except socket.timeout:
                    print("error")

                # Enviar ficheiro
                retry = 0
                missing = self.pieces
                flag = False
                while(retry < 3 or flag == True):
                    transfereCC.sendPacketsToClient(self.socket, self.address, missing)
                    # Verifica se recebeu todos
                    try:
                        code, text = transfereCC.recvMessage(self.socket)
                        if(code == 3):
                            # TODO get from data['ack'] os indexes
                            missing = []
                        elif(code == 1):
                            flag = True
                    except socket.timeout:
                        print("error")
                        retry+=1
            else:
                #fazer um pedido de get para o endereço do client mas na porta que o servidor é executado.
                pass

            self.socket.sendto(("from thread: ola\n").encode(),self.address)
            self.socket.close()
        
        else:
            self.socket.sendto(("from thread: autenticacao invalida").encode(),self.address)


    #autenticacao do cliente para depois mandar os arquivos
    def auth(self):
        if (self.data["username"] == "teste" and self.data["password"] == "123"):
            return True
        
        else:
            return False

    




    
        