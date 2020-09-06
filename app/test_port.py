import socket
import time
import mysql.connector

ip = "127.0.0.1"
port = 3306 
timeout = 3

def isOpen(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
                s.connect((ip, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()

def isDBReady(user, password, dbname):
    try:
        connection = mysql.connector.connect(host=ip,
                                             database=dbname,
                                             user=user,
                                             password=password)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            cursor.close()
            connection.close()
            return True
        else:
            return False
    except:
        return False

if __name__ == "__main__":
    if isDBReady(user="stock", password="stock", dbname="eclass"):
        print("open")
    else:
        print("closed")
