from socket import socket as _socket

from cvg.object import PacketType, Packet, Connection, ConnectionResult


def __packet_exchange(connection: Connection, packet: Packet) -> Packet:
    connection.socket.send(packet.to_bytes())
    return Packet(connection.socket.recv(4096))

SRV_ENT_CORRECT = "Correct Pass Key!"
SRV_ENT_INCORRECT = "Incorrect Pass Key!"

SRV_ENT_UNLOCKED = "Everyone is welcome!"
SRV_ENT_UNKNOWN = "Unknown packet at entrance!"

def __srv_ent_correct(
    connection: Connection, 
    message: str | None = SRV_ENT_CORRECT
) -> ConnectionResult:
    connection.socket.send(
        Packet(message.encode(), PacketType.ACCEPTED).to_bytes()
    )                    
    return ConnectionResult(True, message)

def __srv_ent_incorrect(
    connection: Connection, 
    message: str | None = SRV_ENT_INCORRECT
) -> ConnectionResult:
    connection.socket.send(
        Packet(message.encode(), PacketType.DENIED).to_bytes()
    )                    
    return ConnectionResult(False, message)

def __srv_ent_unknown(
    connection: Connection, 
    message: str | None = SRV_ENT_UNKNOWN
) -> ConnectionResult:
    connection.socket.send(
        Packet(message.encode(), PacketType.ERROR).to_bytes()
    )
    return ConnectionResult(False, message)

def server_entrance(
    connection: Connection,
    pass_key: bytes = b""
) -> ConnectionResult:
    login_packet = Packet(connection.socket.recv(4096))
    
    if login_packet.type == PacketType.CONNECT:
        if pass_key != b"":
            if login_packet.payload == pass_key:
                return __srv_ent_correct(connection)
            else:
                return __srv_ent_incorrect(connection)
        else:
            return __srv_ent_correct(connection, SRV_ENT_UNLOCKED)

    return __srv_ent_unknown(connection)


def client_entrance(
    connection: Connection, 
    pass_key: bytes = b""
) -> ConnectionResult:
    response_packet = __packet_exchange(
        connection, 
        Packet(pass_key, PacketType.CONNECT)
    )
    
    str_payload = str(response_packet.payload)
        
    if str_payload.startswith("b'"):
        str_payload = str_payload.removeprefix("b'")
        str_payload = str_payload.removesuffix("'")
    
    if response_packet.type is PacketType.ACCEPTED:
        return ConnectionResult(True, str_payload)
    else:
        return ConnectionResult(False, str_payload)