from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection


class StreamInvalidPacketReceivedDuringStream(Exception):
    pass


class StreamIncompletePacketReceived(Exception):
    pass


def __send_and_receive(connection: Connection, packet: Packet) -> Packet:
    connection.socket.send(packet.encode())
    
    result = None
    
    try:
        result = Packet(connection.socket.recv(4096))
    except:
        pass
    
    return result


def stream_transmit(connection: Connection, packet: Packet) -> Packet:
    data = packet.encode()
    
    response = __send_and_receive(
        connection,
        Packet(len(data).to_bytes(8, "big"), PacketType.STREAM_START)
    )

    if response.type is PacketType.STREAM_DATA:
        length = len(data)
        
        iterations = int(length / 4094)
        remainder = length % 4094
                
        chunked_data = [
            data[index : index + 4094] for index in range(0, iterations)
        ]
                
        chunked_data.append(data[length - remainder:length])
        
        for chunk in chunked_data:
            response = __send_and_receive(
                connection,
                Packet(chunk, PacketType.STREAM_DATA, packet.id)
            )
            
            match response.type:
                case PacketType.STREAM_DATA:
                    continue
                case _:
                    raise StreamInvalidPacketReceivedDuringStream(
                        connection, 
                        response
                    )
        
        complete_response = __send_and_receive(
            connection,
            Packet(b"", PacketType.STREAM_END, packet.id)
        )
        
        match complete_response.type:
            case PacketType.STREAM_CHECKSUM:
                pass
            case _:
                pass
        
        return complete_response
        

def stream_receive(connection: Connection, packet: Packet) -> Packet:
    stream_size = int.from_bytes(packet.payload, "big")
    stream_result = b""
    
    __original_state = connection.state
    connection.state = ConnectionState.STREAMING
    
    while True:
        chunk_packet = __send_and_receive(
            connection,
            Packet(b"", PacketType.STREAM_DATA, packet.id)
        )
        
        match chunk_packet.type:
            case PacketType.STREAM_DATA:
                pass
            case PacketType.STREAM_END:
                break
            case _:
                raise StreamInvalidPacketReceivedDuringStream(
                    connection, 
                    packet
                )

        stream_result = stream_result + chunk_packet.payload

    if len(stream_result) != stream_size:
        raise StreamIncompletePacketReceived(connection, packet)
    
    return Packet(stream_result)
    

def send_and_receive(connection: Connection, packet: Packet) -> Packet:
    connection.state(ConnectionState.STREAMING)
    
    raw_packet = packet.encode()
    
    if len(raw_packet) > 4096:
        return stream_transmit(connection, packet)
    
    response = __send_and_receive(connection, packet)
    
    match response.type:
        case PacketType.STREAM_START:
            response = stream_receive(connection, response)
        case _:
            pass
        
    connection.state(ConnectionState.WAITING)
    
    return response


