from enum import Enum
from socket import socket as _socket

from dataclasses import dataclass, field

from cvg.core.crypto import ECDHCrypto

class InvalidPayloadLength(Exception):
    pass


class InvalidPacketType(Exception):
    pass


class PacketType(Enum):
    UNKNOWN = b"\xf0"
    
    OK = b"\xf1"
    BAD = b"\xf2"
    
    ENTRANCE_GREET = b"\x00"
    ENTRANCE_PASSWORD = b"\x01"
    
    CRYPTO_INFO = b"\xb0"
    CRYPTO_DATA = b"\xb1"
    CRYPTO_CHECK = b"\xb2"
    
    REQUEST_GRANTED = b"\xb0"
    REQUEST_DENIED = b"\xb1"
    
    EVENT_BROADCAST = b"\xe0"
    EVENT_LISTEN = b"\xe1"
    
    COMMAND_RUN = b"\xc0"
    COMMAND_RESULT = b"\xc1"

    STREAM_START = b"\xd0"
    STREAM_DATA = b"\xd1"
    STREAM_END = b"\xd2"
    
    STREAM_CHECKSUM = b"\xd3"


INVALID_PAYLOAD_LENGTH = "Payload must be 2 bytes minimum!"

INVALID_PACKET_TYPE = "Invalid PacketType.\"{0}\"\n\nAvailable PacketType.(s):"
INVALID_PACKET_TYPE = INVALID_PACKET_TYPE + "\n" + "".join(
    [("  " * 5) + "PacketType." + type.name + "\n" for type in PacketType]
).removesuffix("\n")


@dataclass
class Address:
    host: str = field(default="")
    port: int = field(default=-1)
    
    def __post_init__(self):
        if type(self.host) is tuple:
            self.port = self.host[1]
            self.host = self.host[0]
    
    def __eq__(self, comp) -> bool:
        if isinstance(comp, Address):  
            return self.host == comp.host and self.port == comp.port
        return False
    
    def __hash__(self) -> int:
        return hash((self.host, self.port))
    
    def as_tuple(self) -> tuple[str, int]:
        return (self.host, self.port)


@dataclass
class Packet:
    payload: bytes = field(default=b"")
    type: PacketType = field(default=PacketType.UNKNOWN)
    
    id: bytes = field(default=b"\x00")

    def __post_init__(self):
        if self.type is PacketType.UNKNOWN:
            if len(self.payload) < 2:
                raise InvalidPayloadLength(INVALID_PAYLOAD_LENGTH)
            
            self.id = self.payload[0:1]
            
            try:
                self.type = PacketType(self.payload[1:2])
            except:
                raise InvalidPacketType(
                    INVALID_PACKET_TYPE.format(
                        str(self.payload[1:2])
                    )
                )
            
            self.payload = self.payload[2::]

    def to_bytes(self) -> bytes:
        return self.id + self.type.value + self.payload
    
    def encode(self) -> bytes:
        return self.to_bytes()


class ConnectionState(Enum):
    GREETING = "greeting"
    WAITING = "waiting"
    
    COMMANDING = "commanding"
    STREAMING = "streaming"


@dataclass
class Connection:
    socket: tuple[_socket, tuple[int, str]] | _socket | None = field(
        default=None
    )
    
    address: Address | None = field(default=None)
    
    client_crypto: ECDHCrypto | None = field(default=None)
    server_crypto: ECDHCrypto | None = field(default=None)
    
    secret_key: bytes = field(default=None)
        
    received_packets: list[Packet] = field(default_factory=list)
    transmitted_packets: list[Packet] = field(default_factory=list)
    
    __connection_state: ConnectionState = field(
        default=ConnectionState.GREETING
    )
    
    def __post_init__(self):
        if type(self.socket) is tuple:
            self.address = Address(self.socket[1])
            self.socket = self.socket[0]
    
    def state(self, target: ConnectionState):
        current_state = self.get_state()
        
        match target:
            case ConnectionState.WAITING:
                commanding, streaming, greeting = (
                    current_state is ConnectionState.COMMANDING,
                    current_state is ConnectionState.STREAMING,
                    current_state is ConnectionState.GREETING
                )
                assert commanding or streaming or greeting, "" # TODO add msg
            case ConnectionState.COMMANDING:
                assert current_state is ConnectionState.WAITING, "" # TODO msg
            case ConnectionState.STREAMING:
                waiting, greeting = (
                    current_state is ConnectionState.WAITING,
                    current_state is ConnectionState.GREETING
                )
                
                assert waiting or greeting, "" # TODO add msg
        
        self.connection_state = target

    def get_state(self) -> ConnectionState:
        return self.__connection_state