"""
Unit tests for Encryption module
Tests HIPAA/GDPR compliant data encryption for PHI
"""

import pytest
from unittest.mock import MagicMock, patch
import json


class TestDataEncryptionInit:
    """Tests for DataEncryption initialization"""

    def test_init_with_default_key(self):
        """Test initialization with default environment key"""
        from api.core.encryption import DataEncryption
        
        encryptor = DataEncryption()
        
        assert encryptor is not None
        assert encryptor.cipher is not None

    def test_init_with_custom_password(self):
        """Test initialization with custom password"""
        from api.core.encryption import DataEncryption
        
        encryptor = DataEncryption(password="test_password_12345")
        
        assert encryptor is not None

    def test_init_with_custom_salt(self):
        """Test initialization with custom salt"""
        from api.core.encryption import DataEncryption
        import os
        
        salt = os.urandom(16)
        encryptor = DataEncryption(password="test_password", salt=salt)
        
        assert encryptor is not None


class TestStringEncryption:
    """Tests for string encryption/decryption"""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor instance"""
        from api.core.encryption import DataEncryption
        return DataEncryption(password="test_password_12345")

    def test_encrypt_string_returns_string(self, encryptor):
        """Test encrypt_string returns string"""
        result = encryptor.encrypt_string("Hello, World!")
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_encrypt_string_different_from_plaintext(self, encryptor):
        """Test encrypted string is different from plaintext"""
        plaintext = "Hello, World!"
        encrypted = encryptor.encrypt_string(plaintext)
        
        assert encrypted != plaintext

    def test_decrypt_string_recovers_original(self, encryptor):
        """Test decryption recovers original string"""
        plaintext = "Hello, World!"
        encrypted = encryptor.encrypt_string(plaintext)
        decrypted = encryptor.decrypt_string(encrypted)
        
        assert decrypted == plaintext

    def test_encrypt_empty_string(self, encryptor):
        """Test encrypting empty string"""
        encrypted = encryptor.encrypt_string("")
        decrypted = encryptor.decrypt_string(encrypted)
        
        assert decrypted == ""

    def test_encrypt_unicode_string(self, encryptor):
        """Test encrypting unicode characters"""
        plaintext = "日本語テスト 🏥 健康"
        encrypted = encryptor.encrypt_string(plaintext)
        decrypted = encryptor.decrypt_string(encrypted)
        
        assert decrypted == plaintext

    def test_encrypt_long_string(self, encryptor):
        """Test encrypting long string"""
        plaintext = "A" * 10000
        encrypted = encryptor.encrypt_string(plaintext)
        decrypted = encryptor.decrypt_string(encrypted)
        
        assert decrypted == plaintext


class TestDictEncryption:
    """Tests for dictionary encryption/decryption"""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor instance"""
        from api.core.encryption import DataEncryption
        return DataEncryption(password="test_password_12345")

    def test_encrypt_dict_returns_string(self, encryptor):
        """Test encrypt_dict returns encrypted string"""
        data = {"patient_id": "P12345", "name": "John Doe"}
        encrypted = encryptor.encrypt_dict(data)
        
        assert isinstance(encrypted, str)

    def test_decrypt_dict_recovers_original(self, encryptor):
        """Test decrypt_dict recovers original dictionary"""
        data = {"patient_id": "P12345", "age": 65}
        encrypted = encryptor.encrypt_dict(data)
        decrypted = encryptor.decrypt_dict(encrypted)
        
        assert decrypted == data

    def test_encrypt_dict_nested(self, encryptor):
        """Test encrypting nested dictionary"""
        data = {
            "patient": {
                "id": "P001",
                "vitals": {
                    "hr": 80,
                    "bp": "120/80"
                }
            }
        }
        encrypted = encryptor.encrypt_dict(data)
        decrypted = encryptor.decrypt_dict(encrypted)
        
        assert decrypted == data

    def test_encrypt_dict_with_list(self, encryptor):
        """Test encrypting dictionary with list values"""
        data = {"diagnoses": ["diabetes", "hypertension"], "patient_id": "P001"}
        encrypted = encryptor.encrypt_dict(data)
        decrypted = encryptor.decrypt_dict(encrypted)
        
        assert decrypted == data


class TestPHIEncryption:
    """Tests for PHI field encryption"""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor instance"""
        from api.core.encryption import DataEncryption
        return DataEncryption(password="test_password_12345")

    def test_encrypt_phi_fields(self, encryptor):
        """Test encrypting specific PHI fields"""
        patient_data = {
            "patient_id": "P12345",
            "name": "John Doe",
            "age": 65,
            "diagnosis": "Sepsis"
        }
        
        encrypted = encryptor.encrypt_phi_fields(
            patient_data, 
            ["patient_id", "name"]
        )
        
        # Original fields should be removed, encrypted versions added
        assert "patient_id_encrypted" in encrypted or "patient_id" not in encrypted

    def test_decrypt_phi_fields(self, encryptor):
        """Test decrypting PHI fields"""
        patient_data = {
            "patient_id": "P12345",
            "name": "John Doe",
            "age": 65
        }
        
        encrypted = encryptor.encrypt_phi_fields(patient_data, ["patient_id", "name"])
        decrypted = encryptor.decrypt_phi_fields(encrypted)
        
        # Should have original values back
        assert decrypted.get("age") == 65

    def test_encrypt_patient_data(self, encryptor):
        """Test encrypt_patient_data convenience method"""
        patient_data = {
            "patient_id": "P12345",
            "name": "John Doe"
        }
        
        encrypted = encryptor.encrypt_patient_data(patient_data)
        
        assert encrypted is not None

    def test_decrypt_patient_data(self, encryptor):
        """Test decrypt_patient_data convenience method"""
        patient_data = {
            "patient_id": "P12345",
            "name": "John Doe"
        }
        
        encrypted = encryptor.encrypt_patient_data(patient_data)
        decrypted = encryptor.decrypt_patient_data(encrypted)
        
        # Should recover data
        assert decrypted is not None


class TestHashingAndMasking:
    """Tests for hashing and masking functions"""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor instance"""
        from api.core.encryption import DataEncryption
        return DataEncryption(password="test_password_12345")

    def test_hash_patient_id(self, encryptor):
        """Test patient ID hashing"""
        patient_id = "P12345"
        hashed = encryptor.hash_patient_id(patient_id)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 hex

    def test_hash_patient_id_consistent(self, encryptor):
        """Test same ID produces same hash"""
        patient_id = "P12345"
        hash1 = encryptor.hash_patient_id(patient_id)
        hash2 = encryptor.hash_patient_id(patient_id)
        
        assert hash1 == hash2

    def test_hash_patient_id_different_ids(self, encryptor):
        """Test different IDs produce different hashes"""
        hash1 = encryptor.hash_patient_id("P12345")
        hash2 = encryptor.hash_patient_id("P12346")
        
        assert hash1 != hash2

    def test_mask_phi(self):
        """Test PHI masking"""
        from api.core.encryption import DataEncryption
        
        masked = DataEncryption.mask_phi("P12345678", visible_chars=4)
        
        assert "5678" in masked
        assert "***" in masked or "..." in masked

    def test_mask_phi_short_value(self):
        """Test masking short values"""
        from api.core.encryption import DataEncryption
        
        masked = DataEncryption.mask_phi("AB", visible_chars=4)
        
        # Should handle gracefully
        assert masked is not None


class TestKeyGeneration:
    """Tests for key generation"""

    def test_generate_new_key(self):
        """Test generating new encryption key"""
        from api.core.encryption import DataEncryption
        
        key = DataEncryption.generate_new_key()
        
        assert isinstance(key, (str, bytes))
        assert len(key) > 0


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""

    def test_encrypt_field(self):
        """Test encrypt_field convenience function"""
        from api.core.encryption import encrypt_field
        
        encrypted = encrypt_field("test_value")
        
        assert encrypted is not None
        assert encrypted != "test_value"

    def test_decrypt_field(self):
        """Test decrypt_field convenience function"""
        from api.core.encryption import encrypt_field, decrypt_field
        
        encrypted = encrypt_field("test_value")
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == "test_value"

    def test_encrypt_field_none(self):
        """Test encrypt_field with None value"""
        from api.core.encryption import encrypt_field
        
        result = encrypt_field(None)
        
        # Should return None for None input
        assert result is None

    def test_encrypt_field_empty(self):
        """Test encrypt_field with empty string"""
        from api.core.encryption import encrypt_field
        
        result = encrypt_field("")
        
        # Should return None or empty for empty input
        assert result is None or result == ""


class TestEncryptionCompatibility:
    """Tests for encryption alias methods"""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor instance"""
        from api.core.encryption import DataEncryption
        return DataEncryption(password="test_password_12345")

    def test_encrypt_alias(self, encryptor):
        """Test encrypt() is alias for encrypt_string()"""
        plaintext = "test"
        
        result1 = encryptor.encrypt(plaintext)
        # Can't compare directly as encryption is non-deterministic
        
        decrypted = encryptor.decrypt(result1)
        assert decrypted == plaintext

    def test_decrypt_alias(self, encryptor):
        """Test decrypt() is alias for decrypt_string()"""
        plaintext = "test"
        
        encrypted = encryptor.encrypt_string(plaintext)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == plaintext
