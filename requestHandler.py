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

            if self.op["action"].upper() == "GET":
                self.getFile()

            elif self.op["action"].upper() == "PUT":
                self.putFile()

        else:
            self.sendAuthError()
            self.socket.close()


    def sendAuthError(self):
        self.msg.makeMessage("", Message.TYPE_ATE, 0)
        self.socket.sendto(self.msg.classToBinary(), self.client_address)


    def getHeaderValues(self, msg):
        self.checksum, self.size, self.nsequence, self.type = unpack('LHLc', msg)
        self.type = self.type.decode('utf-8')

    
    def updateData(self):
        self.data = json.loads(self.data.decode('utf-8'))


    def chunkFile(self, filename):
        with open("/tmp/" + str(filename), "rb") as file:
            chunk = True

            while chunk:
                chunk = file.read(1024)
                self.pieces.append(chunk)

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

                

    def sendLast(self, index=-1):
        if(index == -1):
            chunk = self.pieces[self.total_segments-1]
        else:
            chunk = self.pieces[index]

        print("size of chunk:", sys.getsizeof(chunk))
        self.msg.makeMessage(chunk, Message.TYPE_FIN, self.total_segments-1)
        self.socket.sendto(self.msg.classToBinary(), self.client_address)
        print("size of message:", sys.getsizeof(self.msg.classToBinary()))


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
        self.socket.settimeout(1)

        while(retry < 3):
            try:
                in_msg = self.socket.recv(2048)
                self.getHeaderValues(in_msg[:25])
                self.data = in_msg[:25]
                return
            
            except TimeoutError:
                self.socket.sendto(self.msg.classToBinary(), self.client_address)
                retry += 1

        raise TimeoutError


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
        size = len(missing)

        for i in range(size-1):
            n = missing[i]
            self.sendChunk(n)

        self.sendLast(size-1)

        

    
    def process_ack(self):
        #send all chunks of the file
        self.sendAll()
