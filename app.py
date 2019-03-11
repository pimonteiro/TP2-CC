def startConnection(ip, port, username, password, fileName):
    return 0


if __name__ == '__main__':
    print("IP: ")
    ip = input()
    print("Port: ")
    port = input()
    print("Username: ")
    username = input()
    print("Password: ")
    password = input()
    print("File name: ")
    fileName = input()

    if startConnection(ip,port,username,password,fileName) == 0 :
        print("Wrong parameters.")
        exit(1)

