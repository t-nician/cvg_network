from enum import Enum
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit
from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address

from cvg.core.crypto import ECParams, ECDHCrypto

def crypto_client_establish(
    connection: Connection, pem: bytes, id: bytes = "\x00"
):
    connection.client_crypto = ECDHCrypto()
    connection.server_crypto = ECDHCrypto(pem)
    
    crypto_check = send_and_receive(
        connection,
        Packet(
            connection.client_crypto.public_key_to_pem(),
            PacketType.CRYPTO_INFO,
            id
        )
    )
    
    secret = connection.client_crypto.exchange(
        connection.server_crypto
    )
    
    encryption_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 key length
        salt=b"",
        info=b"",
        backend=default_backend()
    ).derive(secret)
      
    if crypto_check.type is PacketType.CRYPTO_CHECK:
        cipher = AES.new(
            encryption_key, 
            nonce=crypto_check.payload[0:16],
            mode=AES.MODE_EAX
        )
        if cipher.decrypt(crypto_check.payload[16::]) == b"hello!":
            connection.socket.send(
                Packet(b"", PacketType.OK, id).to_bytes()
            )


def crypto_server_establish(connection: Connection, id: bytes = "\x00"):
    client_pem = send_and_receive(
        connection,
        Packet(
            connection.server_crypto.public_key_to_pem(), 
            PacketType.CRYPTO_INFO, 
            id
        )
    )
    
    connection.client_crypto = ECDHCrypto(client_pem.payload)
    
    secret = connection.server_crypto.exchange(
        connection.client_crypto
    )
    
    encryption_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 key length
        salt=b"",
        info=b"",
        backend=default_backend()
    ).derive(secret)
    
    cipher = AES.new(encryption_key, mode=AES.MODE_EAX)
    payload = cipher.nonce + cipher.encrypt(b"hello!")
    
    crypto_check_status = send_and_receive(
        connection,
        Packet(
            payload,
            PacketType.CRYPTO_CHECK,
            id
        )
    )
    
    if crypto_check_status.type is PacketType.OK:
        return None