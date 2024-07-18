from enum import Enum
from dataclasses import dataclass, field

from socket import socket, AF_INET, SOCK_STREAM

from cvg.core.protocol.server import establish_connection

from cvg.core.protocol.object import PacketType, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit


class ServerState(Enum):
    CREATED = "created"
    BINDING = "initialized"
    LISTENING = "listening"
    

@dataclass
class ProtocolServer:
    host: str | tuple[str, int] | Address = field(default="127.0.0.1")
    port: int = field(default=5000)
    
    key: bytes = field(default=b"")
    
    encrypted: bool = field(default=False)
    
    __server_socket: socket | None = field(default=None)
    __server_state: ServerState = field(default=ServerState.CREATED)

    def __post_init__(self):
        _host = self.host
        _type = type(_host)
        
        if _type is Address:
            self.host = _host.host
            self.port = _host.port
        elif _type is tuple:
            self.host = _host[0]
            self.port = _host[1]
        
        if self.encrypted:
            pass # TODO load encryption params.
    
    def state(self, target: ServerState):
        match target:
            case ServerState.BINDING:
                assert self.__server_state is ServerState.CREATED
            case ServerState.LISTENING:
                assert self.__server_state is ServerState.BINDING
        
        self.__server_state = target
    
    def bind(self):
        self.state(ServerState.BINDING)
        
        self.__server_socket = socket(AF_INET, SOCK_STREAM)
        self.__server_socket.bind((self.host, self.port))
        self.__server_socket.listen(5) # TODO change to configurable value here
    
    def start(self):
        if self.__server_state is not ServerState.BINDING:
            self.bind()
        
        self.state(ServerState.LISTENING)
        
        while True:
            connection = Connection(self.__server_socket.accept())
            print("[server]", establish_connection(connection, self.key))
            #self.establish(Connection(connection, Address(address)))