import base64
import hashlib


from enum import Enum
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

@dataclass
class ECParams:
    curve: ec.EllipticCurve = field(default_factory=ec.SECP521R1)
    backend: ( None ) = field(default_factory=default_backend)
    
    def as_tuple(self) -> tuple[ec.EllipticCurve, ( None )]:
        return (self.curve, self.backend)


# Generate Alice's key pair
alice_private_key = ec.generate_private_key(*ECParams().as_tuple())
alice_public_key = alice_private_key.public_key()

# Serialize Alice's public key (you can send this over the Internet)
alice_public_key_pem = alice_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print("Alice public key (PEM format):\n", alice_public_key_pem.decode())

# Generate Bob's key pair
bob_private_key = ec.generate_private_key(*ECParams().as_tuple())
bob_public_key = bob_private_key.public_key()

# Serialize Bob's public key (you can send this over the Internet)
bob_public_key_pem = bob_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
print("Bob public key (PEM format):\n", bob_public_key_pem.decode())

# Calculate shared secret
alice_shared_secret = alice_private_key.exchange(ec.ECDH(), bob_public_key)
bob_shared_secret = bob_private_key.exchange(ec.ECDH(), alice_public_key)

print(len(alice_shared_secret))

# Ensure both shared secrets match
print("Equal shared secrets:", alice_shared_secret == bob_shared_secret)
