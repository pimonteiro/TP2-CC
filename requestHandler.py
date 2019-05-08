import threading
import socket
import json
import sys
import os
from message import Message
from struct import pack
from struct import unpack
from connection import Connection

class requestHandler(threading.Thread):
    def __init__(self, skt, client_address):
        threading.Thread.__init__(self)

        self.conn = Connection(client_address[0], client_address[1])        #client's connection
        self.data = {}                                                      #current data sent from client
        self.pieces = []                                                    #file's chunks
        self.msg = Message()                                                #message to be send
        self.flag = True

        self.__msgaux__(skt[0])


    def __msgaux__(self, mbytes):
        m = Message()
        m.binaryToClass(mbytes)

        self.op = m.getData()                                           #operation data
        self.getHeaderValues(m.getHeaderValues())                       #get the header


    def run(self):    
        if self.auth():

            if self.op["action"].upper() == "GET":
                self.getFile()

            elif self.op["action"].upper() == "PUT":
                self.putFile()

        else:
            self.sendAuthError()
            self.conn.close()


    def sendAuthError(self):
        self.msg.makeMessage("", Message.TYPE_ATE, 0)
        self.conn.send(self.msg)


    def getHeaderValues(self, values):
        self.checksum, self.size, self.nsequence, self.type = values

    
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
            self.conn.send(self.msg)
            self.conn.close()
            return

        #split the file into chunks and store it into a list
        #return the total of segments
        self.total_segments = self.chunkFile(filename)

        #send total segments
        self.msg.makeTotalSegMessage(self.total_segments, self.conn.get_SourcePort())
        self.conn.send(self.msg)
        
        #wait for the answer and process it
        self.process_answer()

        #process the answers untill receive a fin
        while(self.flag):
            self.process_answer()

        #close the scket
        self.conn.close()


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

        self.msg.makeMessage(chunk, Message.TYPE_FIN, self.total_segments-1)
        self.conn.send(self.msg)


    def sendChunk(self, segment):
        chunk = self.pieces[segment]
        self.msg.makeMessage(chunk, Message.TYPE_DAT, segment)
        self.conn.send(self.msg)


    def sendAll(self):
        for n in range(self.total_segments - 1):
            chunk = self.pieces[n]
            self.msg.makeMessage(chunk, Message.TYPE_DAT, n)
            self.conn.send(self.msg)
            
        self.sendLast()


    def waitAnswer(self):
        retry = 0
        self.conn.set_timeout(1)

        while(retry < 3):
            try:
                in_msg, _ = self.conn.receive()
                self.getHeaderValues(in_msg.getHeaderValues())
                
                if self.type in (Message.TYPE_DAT, Message.TYPE_TSG, Message.TYPE_MMS):
                    self.data = in_msg.getData()
                
                return
            
            except TimeoutError:
                self.conn.send(self.msg)
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
