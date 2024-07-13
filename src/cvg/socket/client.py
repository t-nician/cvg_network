from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

from cvg.socket.packet import PacketType, PacketData, Address


@dataclass
class ClientSocket:
    server_host: str = field(default="127.0.0.1")
    server_port: int = field(default=5000)
    server_key: bytes = field(default=b"")
    
    __socket: socket | None = field(default=None)
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.connect((self.server_host, self.server_port))
    
    def login(self):
        pass