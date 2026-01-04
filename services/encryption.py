"""
Data Encryption Service using Fernet symmetric encryption.
Protects sensitive user data at rest in the database.
"""

import os
import base64
import logging
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionService:
    """Handle encryption and decryption of sensitive data."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service.
        
        Args:
            encryption_key: Base64-encoded encryption key. If None, reads from env.
        """
        self.logger = logging.getLogger(__name__)
        
        # Get encryption key from environment or parameter
        key = encryption_key or os.getenv('ENCRYPTION_KEY')
        
        if not key:
            # Generate a new key if none provided (development only)
            if os.getenv('ENVIRONMENT') == 'production':
                raise ValueError(
                    "ENCRYPTION_KEY must be set in production. "
                    "Generate one using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
                )
            else:
                self.logger.warning("⚠️ No ENCRYPTION_KEY found. Generating temporary key for development.")
                key = Fernet.generate_key().decode()
        
        # Initialize Fernet cipher
        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")
    
    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """
        Encrypt plaintext data.
        
        Args:
            plaintext: Data to encrypt (string or bytes)
            
        Returns:
            Base64-encoded encrypted data as string
        """
        try:
            # Convert to bytes if string
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            
            # Encrypt
            encrypted = self.cipher.encrypt(plaintext)
            
            # Return as base64 string for database storage
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt encrypted data.
        
        Args:
            ciphertext: Base64-encoded encrypted data
            
        Returns:
            Decrypted plaintext as string
        """
        try:
            # Decode from base64
            encrypted = base64.b64decode(ciphertext.encode('utf-8'))
            
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted)
            
            # Return as string
            return decrypted.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field] is not None:
                try:
                    encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
                except Exception as e:
                    self.logger.error(f"Failed to encrypt field '{field}': {e}")
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field] is not None:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception as e:
                    self.logger.error(f"Failed to decrypt field '{field}': {e}")
                    # Keep encrypted value if decryption fails
        
        return decrypted_data
    
    @staticmethod
    def generate_key_from_password(password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Generate encryption key from password using PBKDF2.
        
        Args:
            password: User password
            salt: Salt for key derivation (auto-generated if None)
            
        Returns:
            Fernet-compatible encryption key
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def generate_new_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded encryption key as string
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')


# Global instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get or create global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# List of sensitive fields that should be encrypted
SENSITIVE_FIELDS = [
    'email',
    'phone_number',
    'medical_history',
    'api_key',
    'access_token',
    'refresh_token',
    'personal_notes'
]


def encrypt_sensitive_data(data: dict) -> dict:
    """
    Convenience function to encrypt sensitive fields in data.
    
    Args:
        data: Dictionary with user data
        
    Returns:
        Dictionary with sensitive fields encrypted
    """
    service = get_encryption_service()
    fields_to_encrypt = [f for f in SENSITIVE_FIELDS if f in data]
    return service.encrypt_dict(data, fields_to_encrypt)


def decrypt_sensitive_data(data: dict) -> dict:
    """
    Convenience function to decrypt sensitive fields in data.
    
    Args:
        data: Dictionary with encrypted data
        
    Returns:
        Dictionary with sensitive fields decrypted
    """
    service = get_encryption_service()
    fields_to_decrypt = [f for f in SENSITIVE_FIELDS if f in data]
    return service.decrypt_dict(data, fields_to_decrypt)
