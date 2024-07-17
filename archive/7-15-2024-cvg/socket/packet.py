from enum import Enum
from dataclasses import dataclass, field


P_INIT_PAYLOAD_LEN = "payload detected but is too short for a ID & PacketType!"


class PacketType(Enum):
    ERROR = b"\xff"
    ACCESS = b"\x00"
    
    GRANTED = b"\xf0"
    DENIED = b"\xf1"

    COMMAND = b"\x01"
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
        
        if self.type is PacketType.ERROR:
            assert raw_len == 0 or raw_len >= 2, P_INIT_PAYLOAD_LEN
            
            self.id = self.payload[0:1]
            
            try:
                self.type = PacketType(self.payload[1:2])
                self.payload = self.payload[2::]
            except:
                pass
    
    def encode(self) -> bytes:
        return self.id + self.type.value + self.payload