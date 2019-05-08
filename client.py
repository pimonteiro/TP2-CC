from message import Message
from connection import Connection


class ClientException(Exception):
    pass


class Client:
    def __init__(self, destIp, destPort):
        self.conn = Connection(destIp=destIp, destPort=destPort)
        self.total_segments = 0
        self.num_received = 0
        self.received = {}

    # Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
    def connect(self, username, password, action, filename):
        msg = Message()
        msg.makeConnectionMessage(username=username, password=password, action=action, filename=filename)

        self.conn.set_status(Connection.CONNECTING)

        self.conn.send(msg)
        print("Enviada: ", msg)

        #TODO: Cliente consegue ser unicamente identificado
        (msg, _) = self.conn.receive()
        print("Recebida: ", msg)

        if msg.getType() == Message.TYPE_ATE:
            self.conn.close()
            raise ClientException("Error: wrong credentials.")

        if msg.getType() == Message.TYPE_FNF:
            self.conn.close()
            raise ClientException("Error: file not found.")

        if msg.getType() not in (Message.TYPE_TSG, Message.TYPE_FIN):
            self.conn.close()
            raise ClientException("Error: can't estabilish connection.")


        ##ACHO que está a mais
        #quando recebe um fin o cliente manda fin e fecha o socket
        elif msg.Message.TYPE_FIN() == Message.TYPE_FIN:
            self.conn.close()
            raise ClientException("Error: can't estabilish connection.")

        else:
            assert msg.getType() == Message.TYPE_TSG
            port = msg.getData()['port']
            self.total_segments = int(msg.getData()['data'])
            msg = Message()
            msg.makeMessage("", Message.TYPE_ACK)
            self.conn.send(msg)
            print("Enviada: ", msg)

        self.conn.set_status(Connection.CONNECTED)
            
    def receive_data(self):
        self.conn.set_status(Connection.RECEIVING_NORMAL)

        while self.num_received < self.total_segments:
            (msg, _) = self.conn.receive()
            print("Recebida: ", msg)

            if msg.getType() not in (Message.TYPE_DAT, Message.TYPE_FIN):
                self.conn.close()
                raise ClientException("Error ao receber dados")

            sequence = msg.getSequence()
            if self.received.get(sequence) is None:
                self.num_received += 1
                self.received[sequence] = msg.getData()

            if msg.getType() == Message.TYPE_FIN:
                missed = self.get_missing()
                if missed.__len__() == 0:
                    msg = Message()
                    msg.makeMessage("",Message.TYPE_FIN)
                    self.conn.send(msg)
                    self.conn.close()
                    self.conn.set_status(Connection.CLOSED)
                else:
                    msg = Message()
                    msg.makeMissingMessage(missed)
                    self.conn.send(msg)
                    self.conn.set_status(Connection.RECEIVING_MISSING)


    def get_missing(self):
        received = set(self.received.keys())
        total = set(range(1, self.total_segments))
        return total.difference(received)


def main():
    client = Client("127.0.0.1", 12000)
    client.connect(username="vanessa", password="123", action="get", filename="porra")
    client.receive_data()


if __name__ == '__main__':
    main()
