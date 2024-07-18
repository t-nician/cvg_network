import base64
import hashlib


from enum import Enum
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


@dataclass
class ECParams:
    curve: ec.EllipticCurve = field(default_factory=ec.SECP384R1)
    backend: ( None ) = field(default_factory=default_backend)
    
    def as_tuple(self) -> tuple[ec.EllipticCurve, ( None )]:
        return (self.curve, self.backend)


private_key = ec.generate_private_key(*ECParams().as_tuple())
public_key = private_key.public_key()
# serializing into PEM
rsa_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM, 
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print(ec.EllipticCurvePublicKey().from_encoded_point(ec.SECP384R1(), rsa_pem))

print(rsa_pem.decode())
