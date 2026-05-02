"""AES Encryption utilities for message encryption/decryption"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import base64
from typing import Tuple
from app.config import get_settings


class MessageEncryption:
    """Handle AES-256 encryption and decryption for messages"""
    
    def __init__(self):
        self.settings = get_settings()
        # Ensure the key is 32 bytes for AES-256
        key = self.settings.encryption_key
        if isinstance(key, str):
            key = key.encode('utf-8')
        self.key = PBKDF2(key, b'timeless_salt', dkLen=32, count=100000)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext message using AES-256-GCM
        Returns: base64 encoded string of (iv + ciphertext + tag)
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        cipher = AES.new(self.key, AES.MODE_GCM)
        iv = cipher.nonce
        
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        # Combine iv + ciphertext + tag and encode to base64
        encrypted_data = iv + ciphertext + tag
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt AES-256-GCM encrypted message
        Args: base64 encoded string from encrypt()
        Returns: decrypted plaintext string
        """
        try:
            encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
            
            # Extract components (IV is 16 bytes, tag is 16 bytes)
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:-16]
            tag = encrypted_data[-16:]
            
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# Global instance
encryption = MessageEncryption()


def encrypt_message(message: str) -> str:
    """Encrypt a message"""
    return encryption.encrypt(message)


def decrypt_message(encrypted_message: str) -> str:
    """Decrypt a message"""
    return encryption.decrypt(encrypted_message)
