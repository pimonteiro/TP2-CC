from message import Message
from connection import Connection
import rootserver
import argparse
import socket


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

        if self.type not in (Message.TYPE_TSG, Message.TYPE_FIN, Message.TYPE_COR):
            self.conn.close()
            raise ClientException("Error: can't estabilish connection.")

        if self.type == Message.TYPE_COR:
            self.conn.close()
            print("Change of roles........... Closing this client.")


        else:
            assert self.type == Message.TYPE_TSG
            port = int(self.data["port"])
            self.conn.set_port(port)
            self.total_segments = int(self.data['data'])
            self.msg.makeMessage("", Message.TYPE_ACK, 0)
            self.conn.send(self.msg)
            print("Enviada: ", self.msg)

        self.conn.set_status(Connection.CONNECTED)

    def receive_data(self, status=Connection.CONNECTED):
        self.conn.set_status(status)

        while self.num_received < self.total_segments:
            flag = self.waitAnswer()

            if self.type in (Message.TYPE_MMS, Message.TYPE_DAT):
                self.conn.set_status(Connection.RECEIVING_NORMAL)

            if flag == 0:
                continue # Checksum failed so we discard the packet

            # TODO adicionar clausulas por causa do estado do cliente

            if self.type not in (Message.TYPE_DAT, Message.TYPE_FIN):
                if self.msg.getType() == Message.TYPE_TSG:
                    continue
                if self.msg.getType() == Message.TYPE_SYN:
                    raise ClientException("Wrong packet order: SYN")
                #self.conn.close()
                #raise ClientException("Error ao receber dados")

            if self.type in (Message.TYPE_MMS, Message.TYPE_DAT, Message.TYPE_FIN):
                if self.received.get(self.nsequence) is None:
                    self.num_received += 1
                    self.received[self.nsequence] = self.data

            if self.type == Message.TYPE_FIN:
                missed = self.get_missing()
                if len(missed) == 0:
                    self.msg.makeMessage("",Message.TYPE_FIN, 0)
                    self.conn.send(self.msg)
                    self.conn.send(self.msg)
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
        self.conn.set_timeout(10)

        while(retry < 3):
            try:
                in_msg, _ = self.conn.receive()
                print("Recebida: " + str(in_msg))
                # Verifying if message is None means that checksum failed
                if in_msg is None and self.conn.get_status() != Connection.CONNECTING:
                    return 0
                elif in_msg is None and self.conn.get_status() == Connection.CONNECTING:
                    raise socket.timeout

                self.getHeaderValues(in_msg.getHeader())
                
                if self.type in (Message.TYPE_DAT, Message.TYPE_TSG, Message.TYPE_MMS, Message.TYPE_FIN):
                    self.data = in_msg.getData()
                
                return 1
            
            except socket.timeout:
                if self.conn.get_status() in (Connection.RECEIVING_NORMAL, Connection.RECEIVING_MISSING):
                    missed = self.get_missing()
                    self.msg.makeMissingMessage(missed)
                    self.conn.send(self.msg)
                    print("Enviada anterior: " + str(self.msg))
                    self.conn.set_status(Connection.RECEIVING_MISSING)
                elif self.conn.get_status() == Connection.CONNECTING:
                    print("Enviada anterior: " + str(self.msg))
                    self.conn.send(self.msg)
                else:
                    print("Enviada anterior: " + str(self.msg))
                    self.conn.send(self.msg)
                retry += 1

        raise socket.timeout



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

    server = rootserver.RootServer(Connection.get_my_ip(), args.my_server_port)
    if args.server_port is None:
        server.start()
        return

    print("Internal server starting.....")
    #server.daemon = True
    server.start()

    print("Starting client........")

    try:
        client = Client(args.server_ip, args.server_port)
        client.connect(username=args.username, password=args.password, action=args.action, filename=args.filename, my_server_port=args.my_server_port)

        if client.conn.get_sock_stat() == False:
            print("Client closed")
            return
        else:
            print(client.conn.get_status())
        client.receive_data()
        with open(args.filename, "wb") as file:
            print("Finishing file transfer....")
            for n in range(client.total_segments):
                file.write(client.received[n])

        print("Stoping internal server......")
        server.join()

    except socket.timeout:
        print("Timeout. Try again later.")
        exit(-1)


if __name__ == '__main__':
    main()