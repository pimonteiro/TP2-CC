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
        self.msg = Message()

        self.data = -1
        self.checksum = -1
        self.type = "0"
        self.nsequence = -1
        self.size = -1



    def getHeaderValues(self, values):
        print(values)
        self.checksum, self.type, self.nsequence, self.size = values

    # Função que estabelece os requisitos que o cliente envia ao servidor para estabelecer a conexão
    def connect(self, username, password, action, filename, my_server_port):
        self.msg.makeConnectionMessage(username=username, password=password, action=action, filename=filename,
                                  my_server_port=my_server_port)
        self.conn.set_status(Connection.CONNECTING)

        self.conn.send(self.msg)
        print("Enviada: ", self.msg)
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

        while self.num_received < self.total_segments:
            flag = self.waitAnswer()

            if flag == 0:
                continue # Checksum failed so we discard the packet

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
                
                else:
                    self.msg.makeMissingMessage(missed)
                    self.conn.send(self.msg)
                    self.conn.set_status(Connection.RECEIVING_MISSING)
                    

    def get_missing(self):
        received = set(self.received.keys())
        total = set(range(self.total_segments))
        return total.difference(received)


    def waitAnswer(self):
        retry = 0
        self.conn.set_timeout(1)

        while(retry < 3):
            try:
                print(str(self.conn))
                in_msg, _ = self.conn.receive()
                print("Recebida: " + str(in_msg))
                # Verifying if message is None means that checksum failed
                if in_msg is None and self.conn.get_status() != Connection.CONNECTING:
                    return 0
                elif in_msg is None and self.conn.get_status() == Connection.CONNECTING:
                    raise TimeoutError

                self.getHeaderValues(in_msg.getHeader())
                
                if self.type in (Message.TYPE_DAT, Message.TYPE_TSG, Message.TYPE_MMS):
                    self.data = in_msg.getData()
                
                return 1
            
            except TimeoutError:
                self.conn.send(self.msg)
                retry += 1

        raise TimeoutError



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

    print("Starting client........")

    client = Client(args.server_ip, args.server_port)
    client.connect(username=args.username, password=args.password, action=args.action, filename=args.filename, my_server_port=args.my_server_port)
    client.receive_data()

    print(client.received)

    with open(args.filename, "wb") as file:
        for n in range(client.total_segments):
            print(client.received[n])
            file.write(client.received[n])

    server.stop()
    print("Stoping internaç server......")


if __name__ == '__main__':
    main()