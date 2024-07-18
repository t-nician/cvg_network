

from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit


def login(
    connection: Connection, 
    key: bytes = b"", 
    id: bytes = b"\x00"
) -> bool:
    granted_or_denied: Packet = send_and_receive(
        connection,
        Packet(key, PacketType.ENTRANCE_PASSWORD, id)
    )
        
    if granted_or_denied.type is PacketType.REQUEST_GRANTED:
        connection.state(ConnectionState.WAITING)
        return True
    elif granted_or_denied.type is PacketType.REQUEST_DENIED:
        connection.state(ConnectionState.GREETING)
        return False
    else:
        raise Exception(connection, granted_or_denied)


def establish_connection(
    connection: Connection,
    key: bytes = b"",
    id: bytes = b"\x00"
) -> bool:
    password_or_accepted: Packet = send_and_receive(
        connection,
        Packet(b"", PacketType.ENTRANCE_GREET, id)
    )
    
    if password_or_accepted.type is PacketType.ENTRANCE_PASSWORD:
        return login(connection, key, id)
    elif password_or_accepted.type is PacketType.REQUEST_GRANTED:
        return True
    elif password_or_accepted.type is PacketType.REQUEST_DENIED:
        return False
    else:
        raise Exception(connection, password_or_accepted)