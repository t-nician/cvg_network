from enum import Enum
from dataclasses import dataclass, field

from socket import socket, AF_INET, SOCK_STREAM

from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit
    

def __exchange_crypto(connection: Connection):
    pass


def login(
    connection: Connection,
    key: bytes = b"", 
    id: bytes = b"\x00"
) -> bool:
    password_packet = send_and_receive(
        connection, 
        Packet(b"", PacketType.ENTRANCE_PASSWORD)
    )
    
    if password_packet.type is PacketType.ENTRANCE_PASSWORD:
        if key == password_packet.payload:
            connection.state(ConnectionState.WAITING)
            connection.socket.send(
                Packet(b"", PacketType.REQUEST_GRANTED).encode()
            )
            
            return True
        
        connection.state(ConnectionState.GREETING)
        connection.socket.send(
            Packet(b"", PacketType.REQUEST_DENIED).encode()
        )
        
        return False
    else:
        raise Exception(connection, password_packet)


def establish_connection(
    connection: Connection,
    key: bytes = b""
) -> bool:
    greeting_packet = Packet(connection.socket.recv(4096))
    
    if key != b"":
        return login(connection, key, greeting_packet.id)
    
    connection.state(ConnectionState.WAITING)
    connection.socket.send(Packet(b"", PacketType.REQUEST_GRANTED).encode())
    
    return True