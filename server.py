import socket
from _thread import *
import threading
from player import OnlineObject
import pickle
import time

#Sets the IP address as the default, this will be set later and port of the server
server = "0.0.0.0"
port = 5555
#Sets the players and the online objects which will be sent back to the clients
players = [OnlineObject(800, 300, 0, 0, 1, False, False, False, False, False, False, False, 0, 0), OnlineObject(300, 300, 0, 0, 1, False, False, False, False, False, False, False, 0, 1)]

def threaded_client(conn, player, s):
    #Sends data at the start when the connection is established
    conn.send(pickle.dumps(players[player]))
    #Initialises the reply variable
    reply = ""
    
    #Loop which runs whilst user is connected to server
    while True:
        #Tries to save received data into data variable
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data

            #If the data is empty then the user has disconnected with the server
            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = players[0]
                else:
                    reply = players[1]
                    
            #Updates the reply based on the received data and sends it to the other client
            conn.sendall(pickle.dumps(reply))
        except:
            break
        
    #Closes the server once the while loop is broken
    print("Lost connection")
    conn.close()

def broadcast_ip(serverIP, port):
    #Initialises the udp servers
    udp_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #Sets the broadcast message to the inputted serverIP and port
    broadcast_message = f"{serverIP}:{port}"

    while True:
        #Broadcast server IP and port to the network on the two port numbers below
        udp_broadcast_socket.sendto(broadcast_message.encode(), ('<broadcast>', 37020))
        udp_broadcast_socket.sendto(broadcast_message.encode(), ('<broadcast>', 37021))
        #Prints data out so that user knows it is working
        print(f"Broadcasting server IP {broadcast_message} to the network")
        #Broadcasts every 5 seconds
        time.sleep(5)  

def Run():
    while True:
        #Gets the server's local IP address
        serverIP = socket.gethostbyname(socket.gethostname())

        #Creates and starts a thread for broadcasting the server's IP, so that if one client joins, the server can still broadcast the address to any other clients trying to join
        broadcast_thread = threading.Thread(target=broadcast_ip, args=(serverIP, 5555), daemon=True)
        broadcast_thread.start()

        #Runs the TCP server in the main thread
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Binds to all available interfaces
        s.bind(('0.0.0.0', 5555))
        #Server listens for a maximum of 2 clients to join
        s.listen(2)
        print("TCP Server is listening on port 5555...")

        #Sets the currentPlayer so that it will know which player it is receiving data from and which player to send this data to
        currentPlayer = 0

        while True:
            #The accept() method waits for a connection from a client before running the next line of code
            conn, addr = s.accept()
            #Starts a new thread to send and receive information with a client once one has connected
            start_new_thread(threaded_client, (conn, currentPlayer, s))
            #Adds one to currentPlayer so that the next thread created is with the other player
            currentPlayer += 1
            #If the currentPlayer is too big then the server will fail to receive the latest player because the server only listens for at most 2 players, so the connection is closed.
            if currentPlayer > 2:
                s.close()
                quit()
                break

#Run() subroutine is started to open the server
Run()