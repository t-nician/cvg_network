from socket import socket as _socket

from cvg.object import PacketType, Packet, Connection, ConnectionResult


def __packet_exchange(connection: Connection, packet: Packet) -> Packet:
    connection.socket.send(packet.to_bytes())
    return Packet(connection.socket.recv(4096))


def server_entrance(
    connection: Connection,
    pass_key: bytes = b""
) -> ConnectionResult:
    connect_packet = Packet(connection.socket.recv(4096))
    
    match connect_packet.type:
        case PacketType.CONNECT:
            if pass_key != b"":
                if connect_packet.payload == pass_key:
                    connection.socket.send(
                        Packet(b"", PacketType.ACCEPTED).to_bytes()
                    )
                    
                    return ConnectionResult(True, "Correct Pass Key!")
                else:
                    connection.socket.send(
                        Packet(b"", PacketType.DENIED).to_bytes()
                    )
                    
                    return ConnectionResult(False, "Incorrect Pass Key!")
            else:
                connection.socket.send(
                    Packet(b"", PacketType.ACCEPTED).to_bytes()
                )
                
                return ConnectionResult(True, "Everyone is welcome!")
        case _:
            connection.socket.send(Packet(b"", PacketType.ERROR).to_bytes())
            return ConnectionResult(True, "Unknown packet at entrance!")

    

def client_entrance(
    connection: Connection, 
    pass_key: bytes = b""
) -> ConnectionResult:
    response_packet = __packet_exchange(
        connection, 
        Packet(pass_key, PacketType.CONNECT)
    )
    
    if response_packet.type is PacketType.ACCEPTED:
        return ConnectionResult(True, str(response_packet.payload))
    else:
        return ConnectionResult(False, str(response_packet.payload))