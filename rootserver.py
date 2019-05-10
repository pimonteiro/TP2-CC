import socketserver
import requestHandler
from threading import Thread



class RootServer(Thread):
    def __init__(self, host="localhost", port=9999):
        Thread.__init__(self)
        self.__host = host
        self.__port = port
        self.__flag = False
        self.__singleUse = False

    def run(self):
        server = socketserver.UDPServer((self.__host, self.__port), None)

        while not self.__flag:
            skt, addr = server.get_request()
            print("Starting helper server thread....")
            rh = requestHandler.requestHandler(skt, addr)
            if self.__singleUse:
                self.__flag = True
            rh.start()

        print("Exiting server thread.")
    def stop(self):
        self.__flag = True

    def oneTime(self):
        self.__singleUse = True