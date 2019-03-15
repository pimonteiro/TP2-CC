
from socket import *


def startConnection(ip, port, username, password, action, fileName):
    # preencher com a init da conexao
    return 0






# Adicionar comandos e flow da aplicaçao
if __name__ == '__main__':


    print("IP: ")
    ip = input()
    print("Port: ")
    port = input()
    print("Username: ")
    username = input()
    print("Password: ")
    password = input()
    print("GET/PUT: ")
    action = input().upper()
    print("File name: ")
    fileName = input()

    if startConnection(ip,port,username,password,action, fileName) == 0 :
        print("Wrong parameters.")
        exit(1)

    # Conseguiu conectar-se, logo pode receber