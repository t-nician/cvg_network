from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

from cvg import protocol
from cvg.object import PacketType, Packet, Address, Connection, ConnectionResult


ADD_CONN_DUPLICATE_ADDRESS = ""


@dataclass
class Server:
    pass_key: bytes = field(default=b"")
    address: str | Address = field(
        default_factory=lambda: Address("127.0.0.1", 5000)
    )
    
    connections: dict[Address, Connection] = field(default_factory=dict)

    __socket: socket = field(
        default_factory=lambda: socket(AF_INET, SOCK_STREAM)
    )
    
    def __post_init__(self):
        if type(self.address) is not Address:
            self.address = Address(self.address)
    
    def __add_connection(self, socket: socket, address: Address):
        assert self.get_connection(address) is None, ADD_CONN_DUPLICATE_ADDRESS
        
        connection = Connection(socket, address, True)
        established = protocol.server_entrance(connection, self.pass_key)
        
        if established.success:
            self.connections[address] = connection
        else:
            socket.send(
                Packet(established.encode(), PacketType.DENIED).to_bytes()
            )
        
    
    def get_connection(self, address: Address) -> Connection | None:
        return self.connections.get(address)
    
    def del_connection(self, address: Address):
        if self.get_connection(address):
            del self.connections[address]
    
    def start(self):
        self.__socket.bind((self.address.host, self.address.port))
        self.__socket.listen(5)
        
        while True:
            socket, address = self.__socket.accept()
            self.__add_connection(socket, Address(address))