from enum import Enum
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit
from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address

from cvg.core.crypto import ECParams, ECDHCrypto


def receive_crypto(connection, crypto: ECDHCrypto):
    pass


def transmit_crypto(connection, crypto: ECDHCrypto):
    pass