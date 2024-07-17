# I was overthinking it. I have a simpler idea for implementation.

import time
import threading

from socket import socket, AF_INET, SOCK_STREAM

from cvg.server import Server
from cvg.object import PacketType, Packet, Address, Connection

from cvg.protocol import server_entrance, client_entrance

def client():
    time.sleep(2)
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(("127.0.0.1", 1234))
    
    print(
        "client", 
        client_entrance(Connection(client, Address("127.0.0.1", 1234)))
    )

server = socket(AF_INET, SOCK_STREAM)
server.bind(("127.0.0.1", 1234))
server.listen(5)

threading.Thread(target=client).start()

connection, address = server.accept()
print(
    "server", 
    server_entrance(Connection(connection, Address("127.0.0.1", 1234)))
)
