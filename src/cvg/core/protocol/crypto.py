from enum import Enum
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from cvg.core.protocol.shared import send_and_receive, stream_receive, stream_transmit
from cvg.core.protocol.object import PacketType, ConnectionState, Packet, Connection, Address

from cvg.core.crypto import ECParams, ECDHCrypto


class ReceivedInvalidOrMissingPacket(Exception):
    pass


def decrypt_packet(packet: Packet, key: bytes) -> Packet:
    cipher = AES.new(
        key=key,
        nonce=packet.payload[0:16],
        mode=AES.MODE_EAX
    )
        
    return cipher.decrypt(packet.payload[16::])


def encrypt_packet(packet: Packet, key: bytes) -> Packet:
    cipher = AES.new(
        key=key,
        mode=AES.MODE_EAX
    )
    
    return Packet(
        cipher.nonce + cipher.encrypt(packet.to_bytes()),
        PacketType.CRYPTO_DATA,
        packet.id
    )


def crypto_send_and_receive(connection: Connection, packet: Packet):
    print("[crypto-s-r]", packet)
    response_packet = send_and_receive(
        connection,
        encrypt_packet(packet, connection.secret_key)
    )
    
    if response_packet.type is PacketType.CRYPTO_DATA:
        return decrypt_packet(response_packet, connection.secret_key)


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
      
    if crypto_check.type is PacketType.CRYPTO_DATA:
    
        if decrypt_packet(crypto_check, encryption_key).payload == b"hello!":
            connection.secret_key = encryption_key
        
            connection.socket.send(
                encrypt_packet(
                    Packet(b"", PacketType.OK, id), 
                    encryption_key
                ).to_bytes()
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
    
    connection.secret_key = encryption_key
    
    crypto_check_status = crypto_send_and_receive(
        connection,
        Packet(
            b"hello!",
            PacketType.CRYPTO_CHECK,
            id
        )
    )
    
    if crypto_check_status.type is not PacketType.OK:
        raise Exception("crypto exchange failed!")
    
    