from message import Message
from connection import Connection
import json


class ClientException(Exception):
    pass


class Client:
    def __init__(self, destIp, destPort):
        self.conn = Connection(destIp=destIp, destPort=destPort)
        self.total_segments = 0
        self.num_received = 0
        self.received = {}
        self.msg = Message()
        self.flag = True

        self.data = -1
        self.checksum = -1
        self.type = "0"
        self.nsequence = -1
        self.size = -1



    def getHeaderValues(self, values):
        self.checksum, self.size, self.nsequence, self.type = values

    # Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
    def connect(self, username, password, action, filename):
        self.msg.makeConnectionMessage(username=username, password=password, action=action, filename=filename)

        self.conn.set_status(Connection.CONNECTING)

        self.conn.send(self.msg)
        self.waitAnswer()

        #TODO: Cliente consegue ser unicamente identificado

        if self.type == Message.TYPE_ATE:
            self.conn.close()
            raise ClientException("Error: wrong credentials.")

        if self.type == Message.TYPE_FNF:
            self.conn.close()
            raise ClientException("Error: file not found.")

        if self.type not in (Message.TYPE_TSG, Message.TYPE_FIN):
            self.conn.close()
            raise ClientException("Error: can't estabilish connection.")


        ##ACHO que está a mais
        #quando recebe um fin o cliente manda fin e fecha o socket
        if self.type == Message.TYPE_FIN:
            self.conn.close()
            raise ClientException("Error: can't estabilish connection.")

        else:
            assert self.type == Message.TYPE_TSG
            port = int(self.data["port"])
            self.conn.set_port(port)
            self.total_segments = int(self.data['data'])
            self.msg.makeMessage("", Message.TYPE_ACK, 0)
            self.conn.send(self.msg)
            print("Enviada: ", self.msg)

        self.conn.set_status(Connection.CONNECTED)
            
    def receive_data(self, status=Connection.RECEIVING_NORMAL):
        self.conn.set_status(status)

        while self.flag:
            self.waitAnswer()

            if self.type not in (Message.TYPE_DAT, Message.TYPE_FIN):
                self.conn.close()
                raise ClientException("Error ao receber dados")

            if self.received.get(self.nsequence) is None:
                self.num_received += 1
                self.received[self.nsequence] = self.data

            if self.type == Message.TYPE_FIN:
                missed = self.get_missing()
                if len(missed) == 0:
                    self.msg.makeMessage("",Message.TYPE_FIN, 0)
                    self.conn.send(self.msg)
                    self.conn.close()
                    self.conn.set_status(Connection.CLOSED)
                    self.flag = False
                else:
                    self.msg.makeMissingMessage(missed)
                    self.conn.send(self.msg)
                    self.receive_data(Connection.RECEIVING_MISSING)


    def get_missing(self):
        received = set(self.received.keys())
        total = set(range(self.total_segments))
        return total.difference(received)


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



def main():
    client = Client("127.0.0.1", 9999)
    client.connect(username="teste", password="123", action="get", filename="TP1.pdf")
    client.receive_data()

    with open("TP1.pdf", "wb") as file:
        for n in range(client.total_segments):
            file.write(client.received[n])


        



if __name__ == '__main__':
    main()
