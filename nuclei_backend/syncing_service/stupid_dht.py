import socket
import struct


class DistributedHashTables:
    """
    Produces a DHT and manages the DHT
    """

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.dht = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)
        self.socket.setblocking(False)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 1)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 3)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5)
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0)
        )
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)

    def produce(self):
        """
        Produces a DHT
        """
        while True:
            try:
                connection, address = self.socket.accept()
                connection.setblocking(False)
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                connection.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 1)
                connection.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 3)
                connection.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 5)
                connection.setsockopt(
                    socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0)
                )
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)
                connection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
            except BlockingIOError:
                continue

            data = connection.recv(1024)
            if not data:
                continue

            data = data.decode()
            if data.startswith("GET"):
                key = data.split(" ")[1]
                if key in self.dht:
                    connection.sendall(self.dht[key].encode())
                else:
                    connection.sendall(b"NOT FOUND")
            elif data.startswith("SET"):
                key, value = data.split(" ")[1].split("=")
                self.dht[key] = value
                connection.sendall(b"OK")
            elif data.startswith("DEL"):
                key = data.split(" ")[1]
                if key in self.dht:
                    del self.dht[key]
                    connection.sendall(b"OK")
                else:
                    connection.sendall(b"NOT FOUND")
            else:
                connection.sendall(b"INVALID COMMAND")

            connection.close()

    def check_if_dht_is_live(self):
        """
        Checks to see if the DHT is live
        """
        try:
            connection = socket.create_connection((self.ip, self.port))
            connection.close()
        except ConnectionRefusedError:
            return False
        else:
            return True

    def update(self):
        """
        Updates the DHT with the latest data from the network and returns the updated DHT But checks to see if the DHT is already up to date
        """
        if self.check_if_dht_is_live():
            return self.dht

        try:
            connection = socket.create_connection((self.ip, self.port))
        except ConnectionRefusedError:
            return self.dht

        connection.sendall(b"GET ALL")
        data = connection.recv(1024)
        data = data.decode()
        self.dht = dict([i.split("=") for i in data.split("\n") if i])

        return self.dht
