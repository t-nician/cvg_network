from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive
from cvg.core.protocol.crypto import crypto_server_establish

def login(
    connection: Connection,
    key: bytes = b"", 
    id: bytes = b"\x00"
) -> bool:
    password_packet = send_and_receive(
        connection, 
        Packet(b"", PacketType.ENTRANCE_PASSWORD, id)
    )
    
    if password_packet.type is PacketType.ENTRANCE_PASSWORD:
        if key == password_packet.payload:
            connection.state(ConnectionState.WAITING)
            connection.socket.send(
                Packet(b"", PacketType.REQUEST_GRANTED, id).encode()
            )
            
            return True
        
        connection.state(ConnectionState.GREETING)
        connection.socket.send(
            Packet(b"", PacketType.REQUEST_DENIED, id).encode()
        )
        
        return False
    else:
        connection.state(ConnectionState.GREETING)
        raise Exception(connection, password_packet)


def establish_connection(
    connection: Connection,
    key: bytes = b"",
) -> bool:
    greeting_packet = Packet(connection.socket.recv(4096))
    
    if connection.server_crypto:
        crypto_server_establish(connection, greeting_packet.id)
        greeting_packet = Packet(connection.socket.recv(4096))
    
    if key != b"":
        return login(connection, key, greeting_packet.id)
    
    connection.state(ConnectionState.WAITING)
    connection.socket.send(Packet(b"", PacketType.REQUEST_GRANTED).encode())
    
    return True