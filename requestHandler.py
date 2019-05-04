import threading
import socket
import json
import sys
import os
from message import *
from struct import pack
from struct import unpack

class requestHandler(threading.Thread):
    def __init__(self, skt, client_address):
        threading.Thread.__init__(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      #connection socket
        self.socket.bind(('127.0.0.1',0))                                   #bind a free port
        self.port = self.socket.getsockname()[1]                            #socket port
        self.client_address = client_address                                #client address
        self.op = json.loads(skt[0][25:].decode('utf-8'))                   #operation data
        self.data = {}                                                      #current data sent from client
        self.pieces = []                                                    #file's chunks
        self.msg = Message()                                                #message to be send
        self.flag = True

        self.total_segments = 0
        self.checksum = 0
        self.nsequence = 0
        self.type = 0
        self.size = 0
        self.getHeaderValues(skt[0][:25])


    def run(self):    
        if self.auth():

            if self.op["action"] == "GET":
                self.getFile()

            elif self.op["action"] == "PUT":
                self.putFile()


    def getHeaderValues(self, msg):
        self.checksum, self.size, self.nsequence, self.type = unpack('LHLc', msg)
        self.type = self.type.decode('utf-8')

    
    def updateData(self):
        tmp = self.socket.recv(self.size).decode('utf-8')

        self.data = json.loads(tmp)


    def chunkFile(self, filename):
        with open("/tmp/" + str(filename), "rb") as file:
            chunk = True

            while chunk:
                chunk = file.read(512)
                self.pieces.append(bytes(chunk))

            file.close()

            return len(self.pieces)



    def getFile(self):
        filename = self.op["filename"]

        #verify if file exists
        if not os.path.exists("/tmp/" + filename):
            self.msg.makeMessage("", Message.TYPE_FNF, 0)
            self.socket.sendto(self.msg.classToBinary(), self.client_address)
            self.socket.close()
            return

        #split the file into chunks and store it into a list
        #return the total of segments
        self.total_segments = self.chunkFile(filename)

        #send total segments
        self.msg.makeTotalSegMessage(self.total_segments, self.port)
        self.socket.sendto(self.msg.classToBinary(), self.client_address)
        
        #wait for the answer and process it
        self.process_answer()

        #process the answers untill receive a fin
        while(self.flag):
            self.process_answer()

        #close the scket
        self.socket.close()

        
            




    def putFile(self):
        pass



    def auth(self):
        if (self.op["username"] == "teste" and self.op["password"] == "123"):
            return True
        
        else:
            return False

                

    def sendLast(self):
        chunk = self.pieces[self.total_segments]
        self.msg.makeMessage(chunk, Message.TYPE_FIN, self.total_segments)
        self.socket.sendto(self.msg.classToBinary(), self.client_address)


    def sendChunk(self, segment):
        chunk = self.pieces[segment]
        self.msg.makeMessage(chunk, Message.TYPE_DAT, segment)
        self.socket.sendto(self.msg.classToBinary(), self.client_address)


    def sendAll(self):
        for n in range(self.total_segments - 1):
            chunk = self.pieces[n]
            self.msg.makeMessage(chunk, Message.TYPE_DAT, n)
            self.socket.sendto(self.msg.classToBinary(), self.client_address)

        self.sendLast()


    def waitAnswer(self):
        retry = 0
        #self.socket.settimeout(10)

        while(retry < 3):
            try:
                print("aqui: %d", retry)
                in_msg = self.socket.recv(Message.HEADER_SIZE)
                self.getHeaderValues(in_msg)
                return
            
            except:
                self.socket.sendto(self.msg.classToBinary(), self.client_address)
                retry += 1

        raise Exception


    def process_answer(self):
        self.waitAnswer()
        #if self.type == message.ConnectionMessage.TYPE:
        #    self.process_connect(msg, address)

        if self.type == Message.TYPE_ACK:
            self.process_ack()

        #if self.type == message.DataMessage.TYPE:
        #    self.process_data(msg, address)

        #if self.type == message.TotalSegMessage.TYPE:
        #    self.process_totalseg(msg, address)

        if self.type == Message.TYPE_MMS:
            self.process_missing()

        elif self.type == Message.TYPE_FIN:
            self.flag = False


    def process_missing(self):
        self.updateData()
        missing = self.data["data"]

        for n in missing:
            self.sendChunk(n)

    
    def process_ack(self):
        #send all chunks of the file
        self.sendAll()








#        if(self.auth()):
#            
#            if self.data["action"] == "GET":
#                # função de mandar dividir e meter os pedaços no array pieces
#
#                #self.pieces = transfereCC.sendFirstMsgToClient(self.socket,self.client_address,text)
#                # Verificar se recebeu
#                try:
#                    text = transfereCC.recvPacket(self.socket)
#                except socket.timeout:
#                    print("error")
#
#                # Enviar ficheiro
#                retry = 0
#                missing = self.pieces
#                flag = False
#                while(retry < 3 or flag == True):
#                    transfereCC.sendPacketsToClient(self.socket, self.client_address, missing)
#                    # Verifica se recebeu todos
#                    try:
#                        code, text = transfereCC.recvMessage(self.socket)
#                        if(code == 3):
#                            # TODO get from data['ack'] os indexes
#                            missing = []
#                        elif(code == 1):
#                            flag = True
#                    except socket.timeout:
#                        print("error")
#                        retry+=1
#            else:
#                #fazer um pedido de get para o endereço do client mas na porta que o servidor é executado.
#                pass
#
#            self.socket.sendto(("from thread: ola\n").encode(),self.client_address)
#            self.socket.close()
#        
#        else:
#            self.socket.sendto(("from thread: autenticacao invalida").encode(),self.client_address)

    #autenticacao do cliente para depois mandar os arquivos
