from enum import Enum
from socket import socket as _socket
from dataclasses import dataclass, field


class PacketType(Enum):
    ERROR = b"\xf0"
    UNKNOWN = b"\xf1"
    
    GREET = b"\x00"
    PASSWORD = b"\x01"
    
    GRANTED = b"\xb0"
    DENIED = b"\xb1"
    
    EVENT = b"\xe0"
    EXECUTE = b"\xe1"
    
    STREAM = b"\xd0"
    

class InvalidPayloadLength(Exception):
    pass


class InvalidPacketType(Exception):
    pass


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


@dataclass
class Connection:
    socket: _socket | None = field(default=None)
    address: Address | None = field(default=None)
    
    connected: bool = field(default=False)