import time
import socket
import threading

from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit

from cvg.core.protocol.client import establish_connection

from cvg.core.network.server import ServerState, ProtocolServer

#server = ProtocolServer("127.0.0.1", 5000, b"")

#server.start()

server = ProtocolServer(key=b"b")

def client():
    time.sleep(2)
    
    connection = Connection(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM),
        Address("127.0.0.1", 5000)
    )

    connection.socket.connect(("127.0.0.1", 5000))
    
    print("[client]", establish_connection(connection, key=b"b"))
    

threading.Thread(target=server.start).start()
client()

"""
def server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.bind(("127.0.0.1", 5000))
    server.listen(1)
    
    socket_connection, address = server.accept()
    
    client_connection = Connection(socket_connection, Address(address))
    client_connection.state(ConnectionState.WAITING)
    
    packet = Packet(socket_connection.recv(4096))

    if packet.type is PacketType.STREAM_START:
        print(f"[{client_connection.address}] [{packet.type}] receiving.")
        packet = stream_receive(client_connection, packet)
        
    print(
        f"[{client_connection.address}] [{packet.type}]", 
        len(packet.payload)
    )
    
    if packet.type is PacketType.COMMAND_RUN:
        client_connection.socket.send(
            Packet(b"world", PacketType.COMMAND_RESULT).encode()
        )

"""