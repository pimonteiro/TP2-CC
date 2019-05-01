import message
import connection


class ClientException(Exception):
    pass


class Client:
    def __init__(self, destIp, destPort):
        self.conn = connection.Connection(destIp=destIp, destPort=destPort)
        self.total_segments = 0
        self.num_received = 0
        self.received = {}

    # Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
    def connect(self, username, password, action, filename):
        msg = message.ConnectionMessage(username=username, password=password, action=action, filename=filename)

        self.conn.set_status(connection.Connection.CONNECTING)

        self.conn.send(msg)
        print("Enviada: ", msg)

        #TODO: Cliente consegue ser unicamente identificado
        (msg, _) = self.conn.receive()
        print("Recebida: ", msg)

        if msg.get_type() not in (message.TotalSegMessage.TYPE, message.FinMessage.TYPE):
            self.conn.close()
            raise ClientException("Error ao estabelecer conexão")

        #quando recebe um fin o cliente manda fin e fecha o socket
        elif msg.get_type() == message.FinMessage.TYPE:
            self.conn.close()
            raise ClientException("Error ao estabelecer conexão")

        else:
            assert msg.get_type() == message.TotalSegMessage.TYPE
            self.total_segments = msg.get_message()["payload"]["totalSegments"]
            msg = message.AckClientMessage()
            self.conn.send(msg)
            print("Enviada: ", msg)

        self.conn.set_status(connection.Connection.CONNECTED)
            
    def receive_data(self):
        self.conn.set_status(connection.Connection.RECEIVING_NORMAL)

        while self.num_received < self.total_segments:
            (msg, _) = self.conn.receive()
            print("Recebida: ", msg)

            if msg.get_type() not in (message.DataMessage.TYPE, message.FinMessage.TYPE):
                self.conn.close()
                raise ClientException("Error ao receber dados")

            self.num_received += 1

            sequence = msg.get_message()["header"]["nsequence"]
            if self.received.get(sequence) is None:
                self.received[sequence] = msg.get_message()["payload"]

            if msg.get_type() == message.FinMessage.TYPE:
                msg = message.FinMessage()
                self.conn.send(msg)
                self.conn.close()

            # TODO: TRATAR DE MISSING MESSAGES

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
