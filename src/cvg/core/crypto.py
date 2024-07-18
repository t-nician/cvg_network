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
    

@dataclass
class ECDHCrypto:
    pem: None | bytes | ECParams = field(default=None)
    params: ECParams = field(default_factory=ECParams)
    
    public_key: ec.EllipticCurvePublicKey = field(default=None)
    private_key: None | ec.EllipticCurvePrivateKey = field(default=None)
    
    def __post_init__(self):
        if type(self.pem) is ECDHCrypto:
            self.params = self.pem
            self.pem = None
        elif type(self.pem) is bytes:
            self.public_key = serialization.load_pem_public_key(self.pem)
        else:
            self.private_key = ec.generate_private_key(*self.params.as_tuple())
            self.public_key = self.private_key.public_key()
    
    def public_key_to_pem(self) -> bytes:
        return self.public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def exchange(
        self, pem_or_public_key: bytes | ec.EllipticCurvePublicKey
    ) -> bytes:
        public_key = pem_or_public_key
        
        if type(public_key) is ECDHCrypto:
            public_key = public_key.public_key
        
        if type(public_key) is bytes:
            public_key = serialization.load_pem_public_key(
                public_key, 
                self.params.backend
            )
        
        return self.private_key.exchange(ec.ECDH(), public_key)
