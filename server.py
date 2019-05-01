import message
import connection
import os


class ServerException(Exception):
    pass


class ConnectionStatus:
    def __init__(self):
        self.connections = {}

    def add_connection(self, address):
        if self.connections.get(address) is None:
            (dest_ip, dest_port) = address
            conn = connection.Connection(destIp=dest_ip, destPort=dest_port)
            self.connections[address] = {
                "connection": conn,
                "filename": "",
                "total_segments": 0,
                "num_transmitted": 0,
                "transmitted": {}
            }

    def get_connection(self, address):
        return self.connections[address]

    def remove_connection(self, address):
        del self.connections[address]


class Server:
    def __init__(self, sourceIp, sourcePort):
        self.conn = connection.Connection(sourceIp=sourceIp, sourcePort=sourcePort)
        self.status = ConnectionStatus()

    def run(self):
        while True:
            (msg, address) = self.conn.receive()
            print("Cliente: ", address, " recebida: ", msg)
            self.status.add_connection(address)

            conn = self.status.get_connection(address)

            if msg.get_type() == message.ConnectionMessage.TYPE:
                self.process_connect(msg, address)

            if msg.get_type() == message.AckClientMessage.TYPE:
                self.process_ack(msg, address)

            if msg.get_type() == message.DataMessage.TYPE:
                self.process_data(msg, address)

            if msg.get_type() == message.TotalSegMessage.TYPE:
                self.process_totalseg(msg, address)

            if msg.get_type() == message.MissingMessage.TYPE:
                self.process_missing(msg, address)

            if msg.get_type() == message.FinMessage.TYPE:
                self.process_fin(msg, address)

    def process_connect(self, msg, address):
        conn = self.status.get_connection(address)
        if conn["connection"].get_status() != connection.Connection.DISCONNECTED:
            return

        # VERIFICAR CREDENCIAIS DO CLIENTE

        if not os.path.exists(msg.get_filename()):
            msg = message.FinMessage()
            conn["connection"].send(msg)
            conn["connection"].close()
            self.status.remove_connection(address)
            return

        size = os.path.getsize(msg.get_filename())

        conn["filename"] = msg.get_filename()
        total_segments = (int) (size / message.Handler.MAX_PAYLOAD_SIZE)
        inc = 0
        if (message.Handler.MAX_PAYLOAD_SIZE * total_segments) != size:
            inc = 1
        total_segments = total_segments + inc
        conn["total_segments"] = total_segments

        conn["connection"].set_status(connection.Connection.CONNECTING)

        msg = message.TotalSegMessage()
        msg.set_total_segments(total_segments)
        conn["connection"].send(msg)

        print("Cliente: ", address ,"enviada: ", msg)

    def process_ack(self, msg, address):
        conn = self.status.get_connection(address)
        if conn["connection"].get_status() != connection.Connection.CONNECTING:
            return

        conn["connection"].set_status(connection.Connection.CONNECTED)

        with open(conn["filename"], 'r') as f:
            while conn["num_transmitted"] < conn["total_segments"]:
                bytes = f.read(message.Handler.MAX_PAYLOAD_SIZE)
                size = len(bytes)
                data_msg = message.DataMessage(bytes, size, conn["num_transmitted"])
                conn["connection"].send(data_msg)

                print("Client: ", address, " enviado: ", data_msg)

                conn["transmitted"][conn["num_transmitted"]] = data_msg
                conn["num_transmitted"] += 1

    def process_missing(self, msg, address):
        pass

    def process_fin(self, msg, address):
        pass

    def process_data(self, msg, address):
        pass

    def process_totalseg(self, msg, address):
        pass


def main():
    server = Server("127.0.0.1", 12000)
    server.run()


if __name__ == '__main__':
    main()
