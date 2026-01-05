"""
Smart feature imputation for web predictions
Uses medical correlations and realistic defaults
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FeatureImputer:
    """Impute missing features using medical correlations"""

    @staticmethod
    def impute_sepsis_features(vital_signs: Dict) -> Dict:
        """
        Impute 42 sepsis features from basic vitals
        
        Args:
            vital_signs: Dict with age, HR, temp, RR, BP, SpO2, optional labs
        
        Returns:
            Complete 42-feature dict
        """
        # Extract provided vitals
        age = vital_signs.get("age", 65)
        hr = vital_signs.get("heart_rate", 80)
        temp = vital_signs.get("temperature", 37.0)
        rr = vital_signs.get("respiratory_rate", 18)
        sbp = vital_signs.get("systolic_bp", 120)
        dbp = vital_signs.get("diastolic_bp", 80)
        spo2 = vital_signs.get("spo2", 96)
        
        # Optional labs
        wbc = vital_signs.get("wbc")
        lactate = vital_signs.get("lactate")
        creatinine = vital_signs.get("creatinine")
        
        # Calculate risk indicators
        is_tachycardic = hr > 100
        is_hypotensive = sbp < 100
        is_febrile = temp > 38.0
        is_tachypneic = rr > 22
        is_hypoxic = spo2 < 94
        
        # Risk score (0-5)
        risk_score = sum([is_tachycardic, is_hypotensive, is_febrile, is_tachypneic, is_hypoxic])
        
        # Impute WBC based on infection signs
        if wbc is None:
            if risk_score >= 3:
                wbc = 15.0 + (risk_score * 2)  # High WBC if multiple risk factors
            elif is_febrile:
                wbc = 12.0
            else:
                wbc = 7.5  # Normal
        
        # Impute lactate based on perfusion
        if lactate is None:
            if is_hypotensive and is_tachycardic:
                lactate = 3.0 + (risk_score * 0.5)  # High lactate in shock
            elif is_hypotensive:
                lactate = 2.0
            else:
                lactate = 1.2  # Normal
        
        # Impute creatinine based on age and BP
        if creatinine is None:
            if age > 70:
                creatinine = 1.3  # Higher in elderly
            elif is_hypotensive:
                creatinine = 1.5  # Acute kidney injury risk
            else:
                creatinine = 1.0  # Normal
        
        # Impute other labs based on risk
        if risk_score >= 3:  # High risk
            platelets = 120.0
            bilirubin = 1.8
            sodium = 135.0
            potassium = 4.5
            glucose = 150.0
            hemoglobin = 10.5
            bicarbonate = 20.0
            pao2 = 75.0
            paco2 = 45.0
            ph = 7.32
            albumin = 2.8
            anion_gap = 16.0
            troponin = 0.2
            bnp = 400.0
            inr = 1.4
            ast = 100.0
            alt = 75.0
        elif risk_score >= 1:  # Medium risk
            platelets = 180.0
            bilirubin = 1.2
            sodium = 138.0
            potassium = 4.2
            glucose = 120.0
            hemoglobin = 11.5
            bicarbonate = 22.0
            pao2 = 85.0
            paco2 = 42.0
            ph = 7.38
            albumin = 3.2
            anion_gap = 13.0
            troponin = 0.05
            bnp = 200.0
            inr = 1.1
            ast = 45.0
            alt = 40.0
        else:  # Low risk
            platelets = 220.0
            bilirubin = 0.8
            sodium = 140.0
            potassium = 4.0
            glucose = 100.0
            hemoglobin = 13.0
            bicarbonate = 24.0
            pao2 = 95.0
            paco2 = 40.0
            ph = 7.40
            albumin = 3.8
            anion_gap = 12.0
            troponin = 0.01
            bnp = 80.0
            inr = 1.0
            ast = 25.0
            alt = 25.0
        
        # Calculate SOFA scores
        resp_sofa = 2 if is_hypoxic else (1 if spo2 < 96 else 0)
        cardio_sofa = 2 if sbp < 90 else (1 if sbp < 100 else 0)
        renal_sofa = 1 if creatinine > 1.9 else 0
        
        # Calculate trends
        hr_trend = 15.0 if is_tachycardic else 0.0
        sbp_trend = -20.0 if is_hypotensive else 0.0
        temp_trend = 1.0 if is_febrile else 0.0
        rr_trend = 8.0 if is_tachypneic else 0.0
        lactate_trend = lactate - 1.2 if lactate > 2.0 else 0.0
        wbc_trend = wbc - 10.0 if wbc > 12.0 else 0.0
        
        return {
            "age": age,
            "gender": 1,  # Male default
            "bmi": 25.0,
            "heart_rate": float(hr),
            "sbp": float(sbp),
            "dbp": float(dbp),
            "temperature": float(temp),
            "respiratory_rate": float(rr),
            "wbc": float(wbc),
            "lactate": float(lactate),
            "creatinine": float(creatinine),
            "platelets": float(platelets),
            "bilirubin": float(bilirubin),
            "sodium": float(sodium),
            "potassium": float(potassium),
            "glucose": float(glucose),
            "hemoglobin": float(hemoglobin),
            "bicarbonate": float(bicarbonate),
            "pao2": float(pao2),
            "paco2": float(paco2),
            "ph": float(ph),
            "anion_gap": float(anion_gap),
            "albumin": float(albumin),
            "troponin": float(troponin),
            "bnp": float(bnp),
            "inr": float(inr),
            "ast": float(ast),
            "alt": float(alt),
            "respiratory_sofa": resp_sofa,
            "cardiovascular_sofa": cardio_sofa,
            "hepatic_sofa": 0,
            "coagulation_sofa": 0,
            "renal_sofa": renal_sofa,
            "neurological_sofa": 0,
            "lactate_trend_12h": float(lactate_trend),
            "hr_trend_6h": float(hr_trend),
            "wbc_trend_12h": float(wbc_trend),
            "sbp_trend_6h": float(sbp_trend),
            "temperature_trend_6h": float(temp_trend),
            "rr_trend_6h": float(rr_trend),
            "hour_of_admission": 12,
            "icu_los_so_far": 4.0,
        }
