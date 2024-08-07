from enum import Enum
from dataclasses import dataclass, field

from socket import socket, AF_INET, SOCK_STREAM

from cvg.core.protocol.server import establish_connection

from cvg.core.protocol.object import PacketType, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit

from cvg.core.protocol.crypto import ECParams, ECDHCrypto, encrypt_packet, decrypt_packet

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
    
    crypto: ECDHCrypto = field(default_factory=ECDHCrypto)
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
    
    def __listener(self, connection: Connection):
        while True:
            packet = Packet(connection.socket.recv(4096))
            
            print("[__listener]", packet)
            
            if packet.type is PacketType.CRYPTO_DATA:
                connection.socket.send(
                    encrypt_packet(
                        decrypt_packet(
                            packet, 
                            connection.secret_key
                        ), 
                        connection.secret_key
                    ).to_bytes()
                )
            else:
                print("[server]", packet)
    
    def state(self, target: ServerState):
        current_state = self.get_state()
        
        match target:
            case ServerState.BINDING:
                assert current_state is ServerState.CREATED # TODO msg
            case ServerState.LISTENING:
                assert current_state is ServerState.BINDING # TODO msg
        
        self.__server_state = target
    
    def get_state(self) -> ServerState:
        return self.__server_state
    
    def bind(self):
        self.state(ServerState.BINDING)
        
        self.__server_socket = socket(AF_INET, SOCK_STREAM)
        self.__server_socket.bind((self.host, self.port))
        self.__server_socket.listen(5) # TODO change to configurable value here
    
    def start(self):
        if self.get_state() is not ServerState.BINDING:
            self.bind()
        
        self.state(ServerState.LISTENING)
        
        while True:
            connection = Connection(
                self.__server_socket.accept(), 
                server_crypto=self.crypto
            )
            
            result = establish_connection(connection, self.key)
            
            print(f"[server] [{connection.address}] established ", result)
            
            self.__listener(connection)
            #self.establish(Connection(connection, Address(address)))