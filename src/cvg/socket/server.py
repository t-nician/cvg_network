import threading

from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

from cvg.socket.packet import PacketType, PacketData, Address


@dataclass
class ServerSocket:
    host: str = field(default="127.0.0.1")
    port: int = field(default=5000)
    
    key: bytes = field(default=b"d")
    
    authorized_addresses: dict[str, bool] = field(default_factory=dict)
    max_connections: int = field(default=5)
    
    __socket: socket | None = field(default=None)
    __on_packet: ( PacketData ) = field(default=lambda _: ())
    __packet_filter: list[PacketType] = field(default_factory=list)
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        
        self.__socket.bind((self.host, self.port))
        self.__socket.listen(self.max_connections)
        
    
    def __connection(self, connection: socket, address: Address):
        while True:
            packet = PacketData(connection.recv(4096))
            
            if packet.type is PacketType.ERROR and len(packet.payload) == 0:
                break
        
            if len(self.__packet_filter) > 0:
                if self.__packet_filter.count(packet.type) == 0:
                    continue
                
            result = self.__on_packet(packet, address)
                
            if type(result) is PacketData:
                result.id = packet.id
                result = result.encode()
            elif type(result) is bytes:
                result = PacketData(
                    result, 
                    packet.type, 
                    packet.id
                ).encode()

            connection.send(result)
    
    def __loop(self):
        while True:
            connection, address = self.__socket.accept()
            
            threading.Thread(
                target=self.__connection,
                args=(connection, Address(address),)
            ).start()

    def start(self, *filter_packet_types: PacketType):
        def wrapper(func: ( PacketData ) = None):
            if func is not None:
                self.__on_packet = func
                self.__packet_filter = list(filter_packet_types)
                
            self.__loop()
            
        return wrapper
            
            
            
            