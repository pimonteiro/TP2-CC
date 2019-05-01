
import connection


conn = connection.Connection(destIP="127.0.0.1", destPort=12000)
conn.connect(username="luis",password="123", action="get", filename="ficheiro")
print(conn)


conn.close()