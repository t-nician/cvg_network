import threading

from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

from cvg.socket.packet import PacketType, PacketData, Address


@dataclass
class ServerSocket:
    host: str = field(default="127.0.0.1")
    port: int = field(default=5000)
    
    key: bytes = field(default=b"d")
    
    max_connections: int = field(default=5)
    
    __socket: socket | None = field(default=None)
    __on_packet: ( PacketData ) = field(default=lambda _: ())
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        
        self.__socket.bind((self.host, self.port))
        self.__socket.listen(self.max_connections)
    
    def __entrance(self, packet: PacketData, connection: socket, address: Address):
        if self.key != b"":
            connection.send(
                PacketData(b"", PacketType.LOGIN, packet.id).encode()
            )
            
            key_packet = PacketData(connection.recv(4096))
            
            if key_packet.type is PacketType.LOGIN:
                if key_packet.payload == self.key:
                    connection.send(
                        PacketData(b"", PacketType.ACCEPTED, packet.id).encode()
                    )
                else:
                    connection.send(
                        PacketData(b"", PacketType.DENIED, packet.id).encode()
                    )
                    return None
        else:
            connection.send(
                PacketData(b"", PacketType.ACCEPTED, packet.id).encode()
            )
        
    
    def __connection(self, connection: socket, address: Address):
        while True:
            print("waiting on packet.")
            packet = PacketData(connection.recv(4096))
            
            if packet.type is PacketType.ERROR and len(packet.payload) == 0:
                print("client dropped connection.")
                break
            
            print("packet received.")
            if packet.type is PacketType.ENTRANCE:
                self.__entrance(packet, connection, address)
            elif packet.type is PacketType.LOGIN:
                self.__login(packet, connection, address)
            else:
                connection.send(self.__on_packet(packet, address).encode())
                print("response sent to client.")
    
    def __loop(self):
        while True:
            print("waiting for client.")
            connection, address = self.__socket.accept()
            
            print("client accepted establishing connection.")
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
            
            
            
            