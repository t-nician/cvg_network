from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

from cvg.socket.packet import PacketType, PacketData, Address


@dataclass
class ClientSocket:
    server_host: str = field(default="127.0.0.1")
    server_port: int = field(default=5000)
    server_key: bytes = field(default=b"d")
    
    __socket: socket | None = field(default=None)
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.connect((self.server_host, self.server_port))
    
    def __get(self, packet: PacketData) -> PacketData:
        self.__socket.send(packet.encode())
        return PacketData(self.__socket.recv(4096))
    
    def login(self) -> bool:
        entrance_response = self.__get(
            PacketData(b"", PacketType.ENTRANCE)
        )
        
        if entrance_response.type is PacketType.LOGIN:
            login_response = self.__get(
                PacketData(self.server_key, PacketType.LOGIN)
            )
            
            if login_response.type is PacketType.ACCEPTED:
                return True
        elif entrance_response.type is PacketType.ACCEPTED:
            return True
        
        return False
    
    def command(self, command: bytes, id: bytes = b"\x00") -> PacketData:
        return self.__get(
            PacketData(command, PacketType.COMMAND, id)
        )