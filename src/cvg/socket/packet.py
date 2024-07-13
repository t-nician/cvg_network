from enum import Enum
from dataclasses import dataclass, field


P_INIT_PAYLOAD_LEN = "payload detected but is too short for a ID & PacketType!"


class PacketType(Enum):
    ERROR = b"\xff"
    
    ENTRANCE = b"\xf0"
    LOGIN = b"\xf1"
    
    ACCEPTED = b"\xf2"
    DENIED = b"\xf3"
    
    COMMAND  = b"\x01"
    STREAM = b"\x02"


@dataclass
class Address:
    host: str = field(default="")
    port: int = field(default=-1)
    
    def __init__(self, address: tuple[str, int]):
        self.host = address[0]
        self.port = address[1]
        
    def __str__(self) -> str:
        return self.host + ":" + str(self.port)
    
    
@dataclass
class PacketData:
    payload: bytes = field(default=b"")
    
    type: PacketType = field(default=PacketType.ERROR)
    id: bytes = field(default=b"\x00")
    
    def __post_init__(self):
        if type(self.payload) is str:
            self.payload = self.payload.encode()
            
        raw_len = len(self.payload)
        
        assert raw_len == 0 or raw_len >= 2, P_INIT_PAYLOAD_LEN
        
        if self.type is PacketType.ERROR and raw_len > 0:
            self.id = self.payload[0:1]
            
            try:
                self.type = PacketType(self.payload[1:2])
                self.payload = self.payload[2::]
            except:
                pass
    
    def encode(self) -> bytes:
        return self.id + self.type.value + self.payload