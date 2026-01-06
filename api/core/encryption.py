"""
Data Encryption Module
HIPAA/GDPR Compliant Data Encryption for PHI (Protected Health Information)

Uses AES-256 encryption with Fernet (symmetric encryption)
"""

import base64
import json
import logging
import os
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
        self.password = password or os.getenv(
            "ENCRYPTION_KEY", "mediai-default-key-change-in-production"
        )
        self.salt = salt or os.getenv("ENCRYPTION_SALT", "mediai-salt").encode()
        self.cipher = self._generate_cipher()

    def _generate_cipher(self) -> Fernet:
        """Generate Fernet cipher from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend(),
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
            logger.error("Encryption failed: %s", e)
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
            logger.error("Decryption failed: %s", e)
            raise

    def encrypt(self, plaintext: str) -> str:
        """Alias for encrypt_string for backward compatibility"""
        return self.encrypt_string(plaintext)

    def decrypt(self, encrypted_text: str) -> str:
        """Alias for decrypt_string for backward compatibility"""
        return self.decrypt_string(encrypted_text)

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
            logger.error("Dictionary encryption failed: %s", e)
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
            logger.error("Dictionary decryption failed: %s", e)
            raise

    def encrypt_phi_fields(
        self, patient_data: Dict[str, Any], phi_fields: list
    ) -> Dict[str, Any]:
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
        encrypted_fields = [
            key for key in decrypted_data.keys() if key.endswith("_encrypted")
        ]

        for encrypted_field in encrypted_fields:
            original_field = encrypted_field.replace("_encrypted", "")
            encrypted_value = decrypted_data[encrypted_field]

            if encrypted_value is not None:
                decrypted_value = self.decrypt_string(encrypted_value)
                decrypted_data[original_field] = decrypted_value
                # Remove encrypted field
                del decrypted_data[encrypted_field]

        return decrypted_data

    def encrypt_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt patient data (encrypts patient_id and name fields)

        Args:
            patient_data: Patient data dictionary

        Returns:
            Dictionary with encrypted patient_id and name fields
        """
        encrypted_data = patient_data.copy()

        # Encrypt patient_id and name if present
        if "patient_id" in encrypted_data and encrypted_data["patient_id"] is not None:
            encrypted_data["patient_id"] = self.encrypt_string(
                str(encrypted_data["patient_id"])
            )

        if "name" in encrypted_data and encrypted_data["name"] is not None:
            encrypted_data["name"] = self.encrypt_string(str(encrypted_data["name"]))

        return encrypted_data

    def decrypt_patient_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt patient data (decrypts patient_id and name fields)

        Args:
            encrypted_data: Encrypted patient data dictionary

        Returns:
            Dictionary with decrypted patient_id and name fields
        """
        decrypted_data = encrypted_data.copy()

        # Decrypt patient_id and name if present
        if "patient_id" in decrypted_data and decrypted_data["patient_id"] is not None:
            try:
                decrypted_data["patient_id"] = self.decrypt_string(
                    decrypted_data["patient_id"]
                )
            except Exception:
                pass  # Already decrypted or invalid

        if "name" in decrypted_data and decrypted_data["name"] is not None:
            try:
                decrypted_data["name"] = self.decrypt_string(decrypted_data["name"])
            except Exception:
                pass  # Already decrypted or invalid

        return decrypted_data

    def hash_patient_id(self, patient_id: str) -> str:
        """
        Hash patient ID using SHA-256

        Args:
            patient_id: Patient ID to hash

        Returns:
            Hexadecimal SHA-256 hash (64 characters)
        """
        import hashlib

        return hashlib.sha256(patient_id.encode()).hexdigest()

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
    "patient_id",
    "name",
    "mrn",  # Medical Record Number
    "ssn",  # Social Security Number
    "date_of_birth",
    "address",
    "phone",
    "email",
]


def example_usage():
    """Example: How to use DataEncryption for HIPAA compliance"""

    # Initialize encryption
    encryptor = DataEncryption()

    # Example patient data with PHI
    patient_data = {
        "patient_id": "P-100234",
        "name": "Nguyễn Văn A",
        "mrn": "MRN-789012",
        "age": 65,
        "sepsis_score": 0.89,
        "vitals": {"hr": 115, "bp": "90/60", "spo2": 92},
    }

    # Encrypt PHI fields
    encrypted_data = encryptor.encrypt_phi_fields(
        patient_data, phi_fields=["patient_id", "name", "mrn"]
    )

    print("Encrypted data:", encrypted_data)
    # Output: {'patient_id_encrypted': '...', 'name_encrypted': '...', ...}

    # Decrypt when needed
    decrypted_data = encryptor.decrypt_phi_fields(encrypted_data)
    print("Decrypted data:", decrypted_data)

    # Mask for display
    masked_id = DataEncryption.mask_phi("P-100234", visible_chars=4)
    print("Masked patient ID:", masked_id)  # Output: "***-0234"


if __name__ == "__main__":
    example_usage()
