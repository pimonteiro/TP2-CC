from message import Message
from connection import Connection
import rootserver
import argparse

class ClientException(Exception):
    pass


class Client:
    def __init__(self, destIp, destPort):
        self.conn = Connection(destIp=destIp, destPort=destPort)
        self.total_segments = 0
        self.num_received = 0
        self.received = {}

    # Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
    def connect(self, username, password, action, filename, my_server_port):
        msg = Message()
        msg.makeConnectionMessage(username=username, password=password, action=action, filename=filename, my_server_port=my_server_port)

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
        if msg.getType() == Message.TYPE_FIN:
            self.conn.close()
            raise ClientException("Error: can't estabilish connection.")

        else:
            assert msg.getType() == Message.TYPE_TSG
            port = msg.getData()['port']
            self.conn.set_port(port)
            print(self.conn)
            self.total_segments = int(msg.getData()['data'])
            msg = Message()
            msg.makeMessage("", Message.TYPE_ACK, 0)
            self.conn.send(msg)
            print("Enviada: ", msg)

        self.conn.set_status(Connection.CONNECTED)
            
    def receive_data(self):
        self.conn.set_status(Connection.RECEIVING_NORMAL)

        while self.num_received < self.total_segments:
            (msg, _) = self.conn.receive()
            #print("Recebida: ", msg)

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
                    msg.makeMessage("", Message.TYPE_FIN, 0)
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
        total = set(range(self.total_segments))
        return total.difference(received)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Parâmetros para o programa.")
    parser.add_argument('--username', type=str, help='Utilizador para autenticação')
    parser.add_argument('--password', type=str, help='password do utilizador')
    parser.add_argument('--action', type=str, help='Ação', choices=['GET', 'PUT'])
    parser.add_argument('--filename', type=str, help='Ficheiro pedido')
    parser.add_argument('--server_port', type=int, help='Porta do servidor')
    parser.add_argument('--server_ip', type=str, help='IP do servidor')
    parser.add_argument('--my_server_port', type=int, help='Porta do cliente caso assuma a posição de servidor')


    return parser.parse_args()


def main():
    args = parse_arguments()

    server = rootserver.RootServer("127.0.0.1", args.my_server_port)
    if args.server_port is None:
        server.start()
        return

    #server.daemon = True
    server.start()

    print("Starting client.....s")

    client = Client(args.server_ip, args.server_port)
    client.connect(username=args.username, password=args.password, action=args.action, filename=args.filename, my_server_port=args.my_server_port)
    client.receive_data()

    print(client.received)

    with open(args.filename, "wb") as file:
        for n in range(client.total_segments):
            print(client.received[n])
            file.write(client.received[n])

    server.stop()


if __name__ == '__main__':
    main()
