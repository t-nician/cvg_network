import threading

from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

from cvg.socket.packet import PacketType, PacketData, Address


@dataclass
class ServerSocket:
    host: str = field(default="127.0.0.1")
    port: int = field(default=5000)
    
    key: bytes = field(default=b"")
    
    max_connections: int = field(default=5)
    
    __socket: socket | None = field(default=None)
    __on_packet: ( PacketData ) = field(default=lambda _: ())
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        
        self.__socket.bind((self.host, self.port))
        self.__socket.listen(self.max_connections)
    
    def start(self):
        def wrapper(func: ( PacketData ) = None):
            if func is not None:
                self.__on_packet = func
                
            self.__loop()
            
        return wrapper
    
    def __connection(self, connection: socket, address: Address):
        print("listening", connection, address)
    
    def __loop(self):
        while True:
            connection, address = self.__socket.accept()
            
            threading.Thread(
                target=self.__connection,
                args=(self, connection, Address(address),)
            ).start()
            
            #self.__connection(connection, Address(address))
            #packet = PacketData(connection.recv(4096))
            
            #if packet.type is PacketType.ERROR and len(packet.payload) == 0:
                #pass
            
            #self.__on_packet(packet, Address(address))
            
            
            
            