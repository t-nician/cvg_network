from cvg.core.protocol.object import PacketType, Packet, Connection


class StreamInvalidPacketReceived(Exception):
    pass


class StreamIncompletePacketReceived(Exception):
    pass


def __send_and_receive(connection: Connection, packet: Packet) -> Packet:
    connection.socket.send(packet.encode())
    return Packet(connection.socket.recv(4096))


def __stream_transmit(connection: Connection, data: bytes) -> Packet:
    pass


def __stream_receive(connection: Connection, packet: Packet) -> Packet:
    stream_size = int(packet.payload)
    stream_result = b""
    
    while True:
        stream_chunk = __send_and_receive(
            connection,
            Packet(b"", PacketType.CONTINUE, packet.id)
        )
        
        if stream_chunk.type is PacketType.STREAM_END:
            break
        elif stream_chunk.type is PacketType.STREAM_DATA:
            raise StreamInvalidPacketReceived(connection, packet)
        
        stream_result = stream_result + stream_chunk.payload

    if len(stream_result) != stream_size:
        raise StreamIncompletePacketReceived(connection ,packet)
    
    return Packet(stream_result)
    

def send_and_receive(connection: Connection, packet: Packet) -> Packet:
    raw_packet = packet.encode()
    
    if len(raw_packet) > 4096:
        return __stream_transmit(connection, raw_packet)
    
    response = __send_and_receive(connection, packet)
    
    if response.type is PacketType.STREAM_START:
        response = __stream_receive(connection, response)
    else:
        return response