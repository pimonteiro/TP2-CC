import threading
import socket
import json
import sys
import os
from message import Message
from struct import pack
from struct import unpack
from connection import Connection
from client import Client


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

        self.op = m.getData()                                                   #operation data
        self.getHeaderValues(m.getHeader())                                                  #get the header
        self.my_server_port = self.op["my_server_port"]


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
        self.checksum,  self.type, self.nsequence, self.size = values

    
    def updateData(self):
        print("My data: " + str(self.data))
        self.data = json.loads(self.data.decode('utf-8'))


    def chunkFile(self, filename):
        with open("shared/" + str(filename), "rb") as file:
            chunk = True

            while chunk:
                chunk = file.read(1024)
                self.pieces.append(chunk)

            file.close()

            return len(self.pieces)



    def getFile(self):
        filename = self.op["filename"]

        #verify if file exists
        if not os.path.exists("shared/" + filename):
            self.msg.makeMessage("", Message.TYPE_FNF, 0)
            print("Enviada: " + str(self.msg))
            self.conn.send(self.msg)
            self.conn.close()
            return

        #split the file into chunks and store it into a list
        #return the total of segments
        self.total_segments = self.chunkFile(filename)

        #send total segments
        self.msg.makeTotalSegMessage(self.total_segments, self.conn.get_SourcePort())
        self.conn.send(self.msg)
        print("Enviado: " + str(self.msg))
        self.conn.set_status(Connection.CONNECTING)
        
        #wait for the answer and process it
        self.process_answer()

        #process the answers untill receive a fin
        while(self.flag):
            self.process_answer()

        #close the scket
        self.conn.close()
        print("Closing server part.")
        self.conn.set_status(Connection.CLOSED)

    def putFile(self):
        self.msg.makeMessage("", Message.TYPE_COR, 0)
        print("Enviada: " + str(self.msg))
        self.conn.send(self.msg)

        self.conn.set_status(Connection.CLOSED)

        try:
            print("Starting temporary client!")
            client = Client(self.conn.get_destIP(), self.my_server_port)
            client.connect(username=self.op["username"], password=self.op["password"], action="get", filename=self.op["filename"],
                           my_server_port=self.my_server_port)
            client.receive_data()
            with open(self.op["filename"], "wb") as file:
                print("Finishing file transfer....")
                for n in range(client.total_segments):
                    file.write(client.received[n])
            self.conn.close()
            print("Closing temporary client!")
        except socket.timeout:
            print("Timeout, exiting.")
            exit(-1)


    def auth(self):
        if (self.op["username"] == "teste" and self.op["password"] == "123"):
            return True
        
        else:
            return False

                

    def sendLast(self, index=-1):
        if(index == -1):
            chunk = self.pieces[self.total_segments-1]
            index = self.total_segments - 1
        else:
            chunk = self.pieces[index]

        self.msg.makeMessage(chunk, Message.TYPE_FIN, index)
        print("Enviada: " + str(self.msg))
        self.conn.send(self.msg)


    def sendChunk(self, segment):
        chunk = self.pieces[segment]
        self.msg.makeMessage(chunk, Message.TYPE_DAT, segment)
        print("Enviada: " + str(self.msg))
        self.conn.send(self.msg)


    def sendAll(self):
        for n in range(self.total_segments - 1):
            chunk = self.pieces[n]
            self.msg.makeMessage(chunk, Message.TYPE_DAT, n)
            print("Enviada: " + str(self.msg))
            self.conn.send(self.msg)
            
        self.sendLast()


    def waitAnswer(self):
        retry = 0
        self.conn.set_timeout(10)

        while(retry < 3):
            try:
                in_msg, _ = self.conn.receive()
                print("Recebida: " + str(in_msg))
                self.getHeaderValues(in_msg.getHeader())
                
                if self.type in (Message.TYPE_DAT, Message.TYPE_TSG, Message.TYPE_FIN, Message.TYPE_MMS):
                    self.data = in_msg.getData()

                return
            
            except Exception as e:
                print(str(e))
                if self.conn.get_sock_stat() == False:
                    print("Closing server.....")
                    self.conn.close()
                    exit(1)
                self.conn.send(self.msg)
                retry += 1

        raise socket.timeout


    def process_answer(self):
        self.waitAnswer()
        #if self.type == message.ConnectionMessage.TYPE:
        #    self.process_connect(msg, address)

        if self.type == Message.TYPE_ACK:
            self.process_ack()
            self.conn.set_status(Connection.CONNECTED)

        #if self.type == message.DataMessage.TYPE:
        #    self.process_data(msg, address)

        #if self.type == message.TotalSegMessage.TYPE:
        #    self.process_totalseg(msg, address)

        if self.type == Message.TYPE_MMS:
            self.process_missing()

        elif self.type == Message.TYPE_FIN:
            self.flag = False


    def process_missing(self):
        #self.updateData()
        missing = self.data["data"]
        size = len(missing)

        for i in range(size-1):
            n = missing[i]
            self.sendChunk(n)

        self.sendLast(missing.pop())


    
    def process_ack(self):
        #send all chunks of the file
        print("Enviando tudo.....")
        self.sendAll()
