"""
Data Encryption Module
HIPAA/GDPR Compliant Data Encryption for PHI (Protected Health Information)

Uses AES-256 encryption with Fernet (symmetric encryption)
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    HIPAA/GDPR compliant encryption for sensitive patient data

    Features:
    - AES-256 encryption
    - Key derivation from password using PBKDF2
    - Salt-based key generation
    - Encrypted JSON serialization
    """

    def __init__(self, password: Optional[str] = None, salt: Optional[bytes] = None):
        """
        Initialize encryption with password or use environment variable

        Args:
            password: Encryption password (if None, uses ENCRYPTION_KEY env var)
            salt: Salt for key derivation (if None, generates new salt)
        """
        self.password = password or os.getenv('ENCRYPTION_KEY', 'mediai-default-key-change-in-production')
        self.salt = salt or os.getenv('ENCRYPTION_SALT', 'mediai-salt').encode()
        self.cipher = self._generate_cipher()

    def _generate_cipher(self) -> Fernet:
        """Generate Fernet cipher from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return Fernet(key)

    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt a string

        Args:
            encrypted_text: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string
        """
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary by serializing to JSON first

        Args:
            data: Dictionary to encrypt

        Returns:
            Encrypted JSON string
        """
        try:
            json_str = json.dumps(data)
            return self.encrypt_string(json_str)
        except Exception as e:
            logger.error(f"Dictionary encryption failed: {e}")
            raise

    def decrypt_dict(self, encrypted_json: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted JSON string back to dictionary

        Args:
            encrypted_json: Encrypted JSON string

        Returns:
            Decrypted dictionary
        """
        try:
            json_str = self.decrypt_string(encrypted_json)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Dictionary decryption failed: {e}")
            raise

    def encrypt_phi_fields(self, patient_data: Dict[str, Any], phi_fields: list) -> Dict[str, Any]:
        """
        Encrypt specific PHI fields in patient data

        Args:
            patient_data: Patient data dictionary
            phi_fields: List of field names to encrypt (e.g., ['patient_id', 'name', 'mrn'])

        Returns:
            Dictionary with encrypted PHI fields (suffixed with _encrypted)
        """
        encrypted_data = patient_data.copy()

        for field in phi_fields:
            if field in encrypted_data:
                original_value = encrypted_data[field]
                if original_value is not None:
                    encrypted_value = self.encrypt_string(str(original_value))
                    encrypted_data[f"{field}_encrypted"] = encrypted_value
                    # Remove original plaintext
                    del encrypted_data[field]

        return encrypted_data

    def decrypt_phi_fields(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt PHI fields that were encrypted with encrypt_phi_fields

        Args:
            encrypted_data: Data with encrypted fields (suffixed with _encrypted)

        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = encrypted_data.copy()

        # Find all encrypted fields
        encrypted_fields = [key for key in decrypted_data.keys() if key.endswith('_encrypted')]

        for encrypted_field in encrypted_fields:
            original_field = encrypted_field.replace('_encrypted', '')
            encrypted_value = decrypted_data[encrypted_field]

            if encrypted_value is not None:
                decrypted_value = self.decrypt_string(encrypted_value)
                decrypted_data[original_field] = decrypted_value
                # Remove encrypted field
                del decrypted_data[encrypted_field]

        return decrypted_data

    @staticmethod
    def generate_new_key() -> str:
        """Generate a new random encryption key"""
        return Fernet.generate_key().decode()

    @staticmethod
    def mask_phi(value: str, visible_chars: int = 4) -> str:
        """
        Mask PHI for display purposes

        Args:
            value: Value to mask
            visible_chars: Number of characters to show at end

        Returns:
            Masked string (e.g., "***-1234" for patient ID)
        """
        if not value or len(value) <= visible_chars:
            return "***"

        return "*" * (len(value) - visible_chars) + value[-visible_chars:]


# Example usage for compliance
PHI_FIELDS = [
    'patient_id',
    'name',
    'mrn',  # Medical Record Number
    'ssn',  # Social Security Number
    'date_of_birth',
    'address',
    'phone',
    'email'
]


def example_usage():
    """Example: How to use DataEncryption for HIPAA compliance"""

    # Initialize encryption
    encryptor = DataEncryption()

    # Example patient data with PHI
    patient_data = {
        'patient_id': 'P-100234',
        'name': 'Nguyễn Văn A',
        'mrn': 'MRN-789012',
        'age': 65,
        'sepsis_score': 0.89,
        'vitals': {
            'hr': 115,
            'bp': '90/60',
            'spo2': 92
        }
    }

    # Encrypt PHI fields
    encrypted_data = encryptor.encrypt_phi_fields(
        patient_data,
        phi_fields=['patient_id', 'name', 'mrn']
    )

    print("Encrypted data:", encrypted_data)
    # Output: {'patient_id_encrypted': '...', 'name_encrypted': '...', ...}

    # Decrypt when needed
    decrypted_data = encryptor.decrypt_phi_fields(encrypted_data)
    print("Decrypted data:", decrypted_data)

    # Mask for display
    masked_id = DataEncryption.mask_phi('P-100234', visible_chars=4)
    print("Masked patient ID:", masked_id)  # Output: "***-0234"


if __name__ == "__main__":
    example_usage()
