"""
Unit tests for encryption utilities
Run with: pytest tests/test_encryption.py -v
"""

import sys
from pathlib import Path

import pytest

# Add apps to path
apps_path = Path(__file__).parent.parent / "apps"
sys.path.insert(0, str(apps_path))

from apps.utils.encryption import DataEncryption


class TestEncryption:
    """Test encryption functionality"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup encryption manager for each test"""
        self.manager = DataEncryption()

    def test_encryption_decryption(self):
        """Test basic encryption and decryption"""
        original = "sensitive patient data"
        encrypted = self.manager.encrypt(original)
        decrypted = self.manager.decrypt(encrypted)

        assert encrypted != original, "Encrypted text should differ from original"
        assert decrypted == original, "Decrypted text should match original"

    def test_encrypt_patient_data(self):
        """Test encrypting patient data dictionary"""
        patient_data = {
            "patient_id": "P001",
            "name": "John Doe",
            "age": 65,
            "diagnosis": "Sepsis",
        }

        encrypted = self.manager.encrypt_patient_data(patient_data)

        assert "patient_id" in encrypted
        assert encrypted["patient_id"] != patient_data["patient_id"]
        assert "name" in encrypted
        assert encrypted["name"] != patient_data["name"]

    def test_decrypt_patient_data(self):
        """Test decrypting patient data dictionary"""
        patient_data = {
            "patient_id": "P001",
            "name": "John Doe",
            "age": 65,
        }

        encrypted = self.manager.encrypt_patient_data(patient_data)
        decrypted = self.manager.decrypt_patient_data(encrypted)

        assert decrypted["patient_id"] == patient_data["patient_id"]
        assert decrypted["name"] == patient_data["name"]
        assert decrypted["age"] == patient_data["age"]

    def test_hash_patient_id(self):
        """Test patient ID hashing"""
        patient_id = "P12345"
        hashed1 = self.manager.hash_patient_id(patient_id)
        hashed2 = self.manager.hash_patient_id(patient_id)

        assert hashed1 == hashed2, "Same input should produce same hash"
        assert hashed1 != patient_id, "Hash should differ from original"
        assert len(hashed1) == 64, "SHA-256 hash should be 64 characters"

    def test_different_ids_different_hashes(self):
        """Test that different IDs produce different hashes"""
        id1 = "P001"
        id2 = "P002"

        hash1 = self.manager.hash_patient_id(id1)
        hash2 = self.manager.hash_patient_id(id2)

        assert hash1 != hash2, "Different IDs should have different hashes"

    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        encrypted = self.manager.encrypt("")
        decrypted = self.manager.decrypt(encrypted)

        assert decrypted == "", "Empty string should decrypt to empty string"

    def test_encrypt_special_characters(self):
        """Test encrypting text with special characters"""
        original = "Patient@123!#$%^&*()"
        encrypted = self.manager.encrypt(original)
        decrypted = self.manager.decrypt(encrypted)

        assert decrypted == original, "Special characters should be preserved"

    def test_encrypt_unicode(self):
        """Test encrypting unicode text"""
        original = "Bệnh nhân: Nguyễn Văn A"
        encrypted = self.manager.encrypt(original)
        decrypted = self.manager.decrypt(encrypted)

        assert decrypted == original, "Unicode should be preserved"
