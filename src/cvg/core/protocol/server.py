from enum import Enum
from dataclasses import dataclass, field

from socket import socket, AF_INET, SOCK_STREAM

from cvg.core.protocol.object import PacketType, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit
    
def __establish_client(self, connection: Connection, packet: Packet):
    connection.socket.send(Packet(b"", PacketType.REQUEST_GRANTED))
    
def __establish_login(self, connection: Connection, packet: Packet):
    pass
    
def __establish_crypto(self, connection: Connection, packet: Packet):
    pass
    
def establish_connection(
    connection: Connection, 
    key: bytes = b"", 
    encrypted: bool = False
) -> bool:
    greeting_packet = Packet(connection.socket.recv(4096))
        
    if greeting_packet.type is PacketType.ENTRANCE_GREET:
        if encrypted:
            __establish_crypto(connection)
            
        if key != b"":
            return __establish_login(connection)
        else:
            return __establish_client(connection)
        
        
        