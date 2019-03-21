
from transfereCC import *


connection = startConnection("127.0.0.1", 12000, "Luis", "123", "download", "bicho", 1)
print(connection)


closeConnection(connection)