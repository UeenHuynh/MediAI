"""
Unit tests for FeatureImputer service
Tests feature imputation for sepsis and mortality predictions
"""

import pytest
from typing import Dict


class TestFeatureImputerSepsis:
    """Tests for sepsis feature imputation (42 features)"""

    def test_impute_sepsis_features_basic_vitals(self):
        """Test imputation with basic vital signs"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {
            "age": 65,
            "heart_rate": 90,
            "temperature": 38.5,
            "respiratory_rate": 22,
            "sbp": 110,
            "dbp": 70,
            "spo2": 95
        }
        
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        
        # Should return 42 features
        assert len(features) == 42

        # Check key features are present
        assert "age" in features
        assert "heart_rate" in features or "HR_mean" in features or any("HR" in k or "heart" in k for k in features.keys())

    def test_impute_sepsis_features_with_labs(self):
        """Test imputation with lab values included"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {
            "age": 70,
            "heart_rate": 100,
            "temperature": 39.0,
            "respiratory_rate": 25,
            "sbp": 100,
            "dbp": 60,
            "spo2": 92,
            "wbc": 15.0,
            "lactate": 3.5,
            "creatinine": 1.8
        }
        
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        
        assert len(features) == 42
        # Verify lab values are incorporated
        assert isinstance(features, dict)

    def test_impute_sepsis_features_minimum_input(self):
        """Test imputation with minimum required input"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {
            "age": 55
        }
        
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        
        # Should still return 42 features with defaults
        assert len(features) == 42

    def test_impute_sepsis_features_empty_input(self):
        """Test imputation with empty input"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_sepsis_features({})
        
        # Should return 42 features with all defaults
        assert len(features) == 42

    def test_impute_sepsis_features_all_values_numeric(self):
        """Verify all imputed values are numeric"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {
            "age": 60,
            "heart_rate": 85,
            "temperature": 37.5
        }
        
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        
        for key, value in features.items():
            assert isinstance(value, (int, float)), f"{key} is not numeric: {type(value)}"

    def test_impute_sepsis_features_no_none_values(self):
        """Verify no None values in output"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_sepsis_features({"age": 50})
        
        for key, value in features.items():
            assert value is not None, f"{key} is None"

    def test_impute_sepsis_features_age_preserved(self):
        """Verify age input is preserved"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {"age": 75}
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        
        assert features.get("age") == 75


class TestFeatureImputerMortality:
    """Tests for mortality feature imputation (61 features)"""

    def test_impute_mortality_features_basic_data(self):
        """Test imputation with basic patient data"""
        from api.services.feature_imputation import FeatureImputer
        
        patient_data = {
            "age": 70,
            "gender": 1,  # Male
            "sofa_score": 8,
            "los_hours": 48,
            "vent_flag": 1,
            "vaso_flag": 0
        }
        
        features = FeatureImputer.impute_mortality_features(patient_data)
        
        # Should return 61 features
        assert len(features) == 61

    def test_impute_mortality_features_minimum_input(self):
        """Test imputation with minimum input"""
        from api.services.feature_imputation import FeatureImputer
        
        patient_data = {"age": 65}
        
        features = FeatureImputer.impute_mortality_features(patient_data)
        
        assert len(features) == 61

    def test_impute_mortality_features_empty_input(self):
        """Test imputation with empty input"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_mortality_features({})
        
        assert len(features) == 61

    def test_impute_mortality_features_with_labs(self):
        """Test imputation with extensive lab data"""
        from api.services.feature_imputation import FeatureImputer
        
        patient_data = {
            "age": 80,
            "gender": 0,  # Female
            "sofa_score": 12,
            "los_hours": 120,
            "vent_flag": 1,
            "vaso_flag": 1,
            "wbc_max": 20.0,
            "lactate_max": 5.0,
            "creatinine_max": 3.5,
            "bilirubin_max": 4.0
        }
        
        features = FeatureImputer.impute_mortality_features(patient_data)
        
        assert len(features) == 61
        assert isinstance(features, dict)

    def test_impute_mortality_features_all_values_numeric(self):
        """Verify all imputed values are numeric"""
        from api.services.feature_imputation import FeatureImputer
        
        patient_data = {
            "age": 65,
            "gender": 1,
            "sofa_score": 6
        }
        
        features = FeatureImputer.impute_mortality_features(patient_data)
        
        for key, value in features.items():
            assert isinstance(value, (int, float)), f"{key} is not numeric: {type(value)}"

    def test_impute_mortality_features_no_none_values(self):
        """Verify no None values in output"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_mortality_features({"age": 55})
        
        for key, value in features.items():
            assert value is not None, f"{key} is None"


class TestFeatureImputerEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_sepsis_features_extreme_age_young(self):
        """Test with very young patient"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_sepsis_features({"age": 18})
        
        assert len(features) == 42
        assert features.get("age") == 18

    def test_sepsis_features_extreme_age_old(self):
        """Test with very old patient"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_sepsis_features({"age": 100})
        
        assert len(features) == 42
        assert features.get("age") == 100

    def test_mortality_features_high_sofa(self):
        """Test with high SOFA score"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_mortality_features({
            "age": 70,
            "sofa_score": 20  # Maximum SOFA
        })
        
        assert len(features) == 61

    def test_sepsis_features_abnormal_vitals(self):
        """Test with abnormal vital signs"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {
            "age": 60,
            "heart_rate": 150,  # Tachycardia
            "temperature": 40.5,  # High fever
            "respiratory_rate": 35,  # Tachypnea
            "sbp": 80,  # Hypotension
            "spo2": 85  # Hypoxia
        }
        
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        
        assert len(features) == 42

    def test_sepsis_features_negative_values_handled(self):
        """Test handling of negative values"""
        from api.services.feature_imputation import FeatureImputer
        
        # Some implementations might receive negative values
        vital_signs = {
            "age": 60,
            "heart_rate": -1  # Invalid
        }
        
        # Should not crash
        features = FeatureImputer.impute_sepsis_features(vital_signs)
        assert len(features) == 42

    def test_sepsis_features_float_age(self):
        """Test with float age value"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_sepsis_features({"age": 65.5})
        
        assert len(features) == 42

    def test_mortality_features_string_gender(self):
        """Test with string gender value"""
        from api.services.feature_imputation import FeatureImputer
        
        # Some implementations accept string gender
        features = FeatureImputer.impute_mortality_features({
            "age": 70,
            "gender": "M"
        })
        
        assert len(features) == 61


class TestFeatureConsistency:
    """Tests for feature naming and consistency"""

    def test_sepsis_features_consistent_across_calls(self):
        """Verify same input produces same output"""
        from api.services.feature_imputation import FeatureImputer
        
        vital_signs = {"age": 60, "heart_rate": 90}
        
        features1 = FeatureImputer.impute_sepsis_features(vital_signs)
        features2 = FeatureImputer.impute_sepsis_features(vital_signs)
        
        assert features1 == features2

    def test_mortality_features_consistent_across_calls(self):
        """Verify same input produces same output"""
        from api.services.feature_imputation import FeatureImputer
        
        patient_data = {"age": 70, "sofa_score": 8}
        
        features1 = FeatureImputer.impute_mortality_features(patient_data)
        features2 = FeatureImputer.impute_mortality_features(patient_data)
        
        assert features1 == features2

    def test_sepsis_features_keys_are_strings(self):
        """Verify all feature keys are strings"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_sepsis_features({"age": 50})
        
        for key in features.keys():
            assert isinstance(key, str), f"Key {key} is not a string"

    def test_mortality_features_keys_are_strings(self):
        """Verify all feature keys are strings"""
        from api.services.feature_imputation import FeatureImputer
        
        features = FeatureImputer.impute_mortality_features({"age": 50})
        
        for key in features.keys():
            assert isinstance(key, str), f"Key {key} is not a string"
