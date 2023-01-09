import socket
import json


class Client:
    HOST = "127.0.0.1"  # The defualt IP address
    PORT = 65432  # The default port used by the server
    CONN_STATE_CONNECTED = 200
    CONN_STATE_CONNECTING = 201
    CONN_STATE_DISCONNECTED = 202
    CONN_STATE_REFUSED = 203
    CONN_STATE_RESET = 204
    CONN_STATE_ABORTED = 205
    CONN_STATE_TIMEOUT = 206
    CUR_CONN_STATE = CONN_STATE_DISCONNECTED
    BUFFER_SIZE = 10240 # max of 10mb data transfer


    def __init__(self):
        self.server_info = None
        Client.CUR_CONN_STATE = Client.CONN_STATE_DISCONNECTED


    def sndData(self, cmd):
        data = cmd
        data = bytes(data, 'utf-8')
        try:
            self.sock.sendall(data)
        except ConnectionResetError:
            pass


    def recvData(self):
        data = self.sock.recv(self.BUFFER_SIZE).decode('utf-8')
        return data


    def startComms(self, host=HOST, port=PORT):
        #Begin connection to server process
        Client.CUR_CONN_STATE = Client.CONN_STATE_CONNECTING # Set connection state to "Connecting"
        Client.HOST = str(host)
        Client.PORT = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10) # set timeout to 10 seconds
        try:
            self.sock.connect((Client.HOST, Client.PORT)) # Connect to server
            Client.CUR_CONN_STATE = Client.CONN_STATE_CONNECTED # Set connection state to "Connected"
            server_info = self.sock.recv(self.BUFFER_SIZE).decode('utf-8') # Download server information
            self.server_info = json.loads(server_info)
        except ConnectionRefusedError: # handle connection refused error
            Client.CUR_CONN_STATE = Client.CONN_STATE_REFUSED
        except ConnectionResetError: # handle connection reset error
            Client.CUR_CONN_STATE = Client.CONN_STATE_RESET
        except ConnectionAbortedError: # handle connection aborted error
            Client.CUR_CONN_STATE = Client.CONN_STATE_ABORTED
        except TimeoutError: # handle the timeout error
            Client.CUR_CONN_STATE = Client.CONN_STATE_TIMEOUT
        except socket.gaierror: # refuse connection to unresolved host
            Client.CUR_CONN_STATE = Client.CONN_STATE_REFUSED
            pass

    def endComms(self):
        self.sock.shutdown(0)
        self.sock.close()
        self.server_info = None
        Client.CUR_CONN_STATE = Client.CONN_STATE_DISCONNECTED


