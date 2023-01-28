import getpass
import socket
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class Credentials:
    def __init__(self) -> None:
        self.password = getpass.getuser().encode()
        self.salt = socket.gethostname().encode()

    def decrypt(self, encrypted):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()
    
    def encrypt(self, credentials):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        f = Fernet(key)
        return f.encrypt(credentials.encode()).decode()