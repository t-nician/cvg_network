

from cvg.core.protocol.object import PacketType, Packet, Connection, Address
from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit


def exchange_crypto(connection: Connection):
    pass


def acknowledge_server(
    connection: Connection,
    key: bytes = b""
) -> bool:
    pass