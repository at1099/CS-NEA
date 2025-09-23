import socket
import pickle

#Used to send data to and connect to servers
class Network:
    def __init__(self, server):
        #Attributes
        #client stores the client's socket server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server stores the server's IP address
        self.server = server
        #Stores the port of the server being connected to
        self.port = 5555
        #Used to establish a connection with the server
        self.c = self.Connect()

    def Connect(self):
        #Tries to connect to the given port and server, otherwise tries again
        try:
            self.client.connect((self.server, self.port))
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def Send(self, data):
        #Tries to send inputted data to the server
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        #Otherwise server has closed
        except socket.error as e:
            print(e)