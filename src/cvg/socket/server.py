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
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        
        self.__socket.bind((self.host, self.port))
        self.__socket.listen(self.max_connections)
    
    def __accept(self, packet: PacketData, connection: socket, address: Address):
        connection.send(
            PacketData(b"", PacketType.ACCEPTED, packet.id).encode()
        )
    
    def __deny(self, packet: PacketData, connection: socket, address: Address):
        connection.send(
            PacketData(b"", PacketType.DENIED, packet.id).encode()
        )
    
    def __entrance(self, packet: PacketData, connection: socket, address: Address):
        if self.key != b"":
            connection.send(
                PacketData(b"", PacketType.LOGIN, packet.id).encode()
            )
            
            key_packet = PacketData(connection.recv(4096))
            
            if (
                key_packet.type is PacketType.LOGIN 
                and key_packet.payload == self.key
            ):
                self.__accept(key_packet, connection, address)
                self.authorized_addresses[str(address)] = True
            else:
                self.__deny(key_packet, connection, address)    
                self.authorized_addresses[str(address)] = False
        else:
            self.__accept(packet, connection, address)
            self.authorized_addresses[str(address)] = True
        
    
    def __connection(self, connection: socket, address: Address):
        while True:
            packet = PacketData(connection.recv(4096))
            
            if packet.type is PacketType.ERROR and len(packet.payload) == 0:
                break
            
            if packet.type is PacketType.ENTRANCE:
                self.__entrance(packet, connection, address)
            elif self.authorized_addresses.get(str(address)) is True:
                connection.send(
                    PacketData(self.__on_packet(packet, address)).encode()
                )
            else:
                self.__deny(packet, connection, address)
    
    def __loop(self):
        while True:
            connection, address = self.__socket.accept()
            
            threading.Thread(
                target=self.__connection,
                args=(connection, Address(address),)
            ).start()

    def start(self):
        def wrapper(func: ( PacketData ) = None):
            if func is not None:
                self.__on_packet = func
                
            self.__loop()
            
        return wrapper
            
            
            
            