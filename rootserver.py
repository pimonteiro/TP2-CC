import socketserver
import requestHandler
from threading import Thread



class RootServer(Thread):
    def __init__(self, host="localhost", port=9999):
        Thread.__init__(self)
        self.__host = host
        self.__port = port
        self.__flag = False

    def run(self):
        server = socketserver.UDPServer((self.__host, self.__port), None)

        while not self.__flag:
            skt, addr = server.get_request()
            print("Starting helper server thread....")
            rh = requestHandler.requestHandler(skt, addr)
            rh.start()

    def stop(self):
        self.__flag = True