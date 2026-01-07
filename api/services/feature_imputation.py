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

        # Calculate continuous risk indicators (0-1 scale for smooth transitions)
        tachycardia_score = min(max(hr - 80, 0) / 50, 1.0)  # 80-130 range
        hypotension_score = min(max(120 - sbp, 0) / 40, 1.0)  # 120-80 range
        fever_score = min(max(temp - 37.0, 0) / 3.0, 1.0)  # 37-40 range
        tachypnea_score = min(max(rr - 16, 0) / 20, 1.0)  # 16-36 range
        hypoxia_score = min(max(98 - spo2, 0) / 12, 1.0)  # 98-86 range

        # Continuous risk score (0.0 to 5.0)
        risk_score = (
            tachycardia_score
            + hypotension_score
            + fever_score
            + tachypnea_score
            + hypoxia_score
        )

        # Normalize to 0-1 for easier scaling
        risk_pct = risk_score / 5.0

        # Impute WBC - smooth scaling from 7.5 (normal) to 25.0 (severe infection)
        if wbc is None:
            wbc = 7.5 + (risk_pct * 17.5)

        # Impute lactate - smooth scaling from 1.2 (normal) to 5.0 (shock)
        # Give extra weight to hypotension (perfusion marker)
        lactate_risk = (risk_pct * 0.6) + (hypotension_score * 0.4)
        if lactate is None:
            lactate = 1.2 + (lactate_risk * 3.8)

        # Impute creatinine - smooth scaling considering age and perfusion
        if creatinine is None:
            age_factor = min((age - 40) / 40, 0.3) if age > 40 else 0
            perfusion_factor = hypotension_score * 0.5
            creatinine = 0.9 + age_factor + perfusion_factor

        # Calculate DBP - smooth correlation with SBP and shock state
        if dbp == 80:  # Default value, calculate from SBP
            dbp_calculated = sbp * 0.6  # MAP formula approximation
            # Further reduce in shock states
            dbp_calculated = dbp_calculated - (hypotension_score * 15)
        else:
            dbp_calculated = float(dbp)

        # CRITICAL: Cubic albumin scaling to avoid hard threshold at 3.10!
        # Model has decision tree split at albumin ≈ 3.05-3.15
        # Use cubic curve to delay crossing threshold until very high risk
        # Formula: 3.5 - (risk_pct^3 * 1.5) gives smooth late decline
        # 0.0→3.5, 0.5→3.31, 0.7→3.0, 1.0→2.0
        albumin = 3.5 - ((risk_pct**3) * 1.5)

        # Platelets - smooth decrease with risk (thrombocytopenia)
        platelets = 230.0 - (risk_pct * 100.0)

        # Bilirubin - smooth increase (liver dysfunction)
        bilirubin = 0.5 + (risk_pct * 1.5)

        # Electrolytes - smooth changes
        sodium = 140.0 - (risk_pct * 8.0)  # Hyponatremia
        potassium = 4.0 + (risk_pct * 0.8)

        # Glucose - stress hyperglycemia
        glucose = 95.0 + (risk_pct * 60.0)

        # Hemoglobin - anemia with sepsis
        hemoglobin = 12.0 - (risk_pct * 3.5)

        # Acid-base - metabolic acidosis
        bicarbonate = 24.0 - (risk_pct * 6.0)
        pao2 = 92.0 - (risk_pct * 20.0)
        paco2 = 40.0 + (risk_pct * 8.0)
        ph = 7.40 - (risk_pct * 0.12)

        # Anion gap - widens with acidosis
        anion_gap = 12.0 + (risk_pct * 6.0)

        # Cardiac markers - stress
        troponin = 0.01 + (risk_pct * 0.25)
        bnp = 80.0 + (risk_pct * 300.0)

        # Coagulation
        inr = 1.0 + (risk_pct * 0.5)

        # Liver enzymes
        ast = 25.0 + (risk_pct * 80.0)
        alt = 25.0 + (risk_pct * 60.0)

        # Calculate SOFA scores based on continuous risk
        resp_sofa = min(int(hypoxia_score * 3), 2)
        cardio_sofa = min(int(hypotension_score * 3), 2)
        renal_sofa = 1 if creatinine > 1.9 else 0

        # Calculate trends - smooth scaling based on deviation from normal
        hr_trend = (hr - 80) * 0.3 if hr > 80 else 0.0
        sbp_trend = (sbp - 120) * 0.5 if sbp < 120 else 0.0
        temp_trend = (temp - 37.0) if temp > 37.0 else 0.0
        rr_trend = (rr - 16) * 0.5 if rr > 16 else 0.0
        lactate_trend = max(lactate - 1.2, 0.0)
        wbc_trend = max(wbc - 10.0, 0.0)

        return {
            "age": age,
            "gender": 1,  # Male default
            "bmi": 25.0,
            "heart_rate": float(hr),
            "sbp": float(sbp),
            "dbp": float(dbp_calculated),
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

    @staticmethod
    def impute_mortality_features(patient_data: Dict) -> Dict:
        """
        Impute 61 mortality features from basic patient data

        Args:
            patient_data: Dict with age, gender, SOFA, LOS, vent/vaso flags, etc.

        Returns:
            Complete 61-feature dict
        """
        # Extract provided data
        age = patient_data.get("age", 65)
        gender = patient_data.get("gender", "M")
        sofa_score = patient_data.get("sofa_score", 4)
        los_hours = patient_data.get("los_hours", 48)
        charlson = patient_data.get("charlson_index", 0)
        mechanical_vent = patient_data.get("mechanical_ventilation", False)
        vasopressor = patient_data.get("vasopressor_use", False)

        # Normalize SOFA to 0-1 (max 24)
        sofa_pct = min(sofa_score / 24.0, 1.0)

        # Calculate age points (APACHE-II style)
        if age < 45:
            age_points = 0
        elif age < 55:
            age_points = 2
        elif age < 65:
            age_points = 3
        elif age < 75:
            age_points = 5
        else:
            age_points = 6

        # Base GCS - decreases with SOFA and interventions
        # CRITICAL: GCS is most important feature (2872.4 gain)
        gcs_base = 15.0 - (sofa_pct * 6.0)  # 15 → 9 with increasing SOFA
        if mechanical_vent:
            gcs_base -= 3.0  # Sedation for ventilation
        gcs_score = max(int(gcs_base), 3)

        # Respiratory parameters - CRITICAL if on ventilation
        # worst_spo2_24h (772.7 gain), worst_fio2_24h (473.3 gain)
        if mechanical_vent:
            worst_spo2_24h = 88.0 + (sofa_pct * 4.0)  # Poor oxygenation
            worst_fio2_24h = 60.0 + (sofa_pct * 35.0)  # High O2 requirement
            worst_pao2_24h = 65.0 + (sofa_pct * 15.0)
        else:
            worst_spo2_24h = 94.0 + (sofa_pct * 3.0)
            worst_fio2_24h = 21.0 + (sofa_pct * 20.0)
            worst_pao2_24h = 85.0 + (sofa_pct * 10.0)

        # Cardiovascular parameters - affected by vasopressors
        if vasopressor:
            worst_map_24h = 55.0 + (sofa_pct * 20.0)  # Low despite pressors
            worst_lactate_24h = 3.5 + (sofa_pct * 3.0)  # Tissue hypoxia
            cardiovascular_sofa = min(int(2 + sofa_pct * 2), 4)
            shock_flag = 1
        else:
            worst_map_24h = 70.0 + (sofa_pct * 15.0)
            worst_lactate_24h = 1.5 + (sofa_pct * 2.0)
            cardiovascular_sofa = min(int(sofa_pct * 2), 2)
            shock_flag = 1 if sofa_score > 8 else 0

        # Vitals - based on SOFA severity
        worst_hr_24h = 85.0 + (sofa_pct * 40.0)
        worst_sbp_24h = 110.0 - (sofa_pct * 30.0)
        min_hr_24h = max(60.0 - (sofa_pct * 10.0), 40)
        max_hr_24h = worst_hr_24h + 10
        min_sbp_24h = max(worst_sbp_24h - 20, 60)
        max_sbp_24h = min(worst_sbp_24h + 30, 160)

        worst_temp_24h = 37.0 + (sofa_pct * 2.5)
        min_temp_24h = max(36.0 - (sofa_pct * 1.0), 34)
        max_temp_24h = worst_temp_24h + 0.5

        worst_rr_24h = 18.0 + (sofa_pct * 15.0)
        min_rr_24h = max(12.0 - (sofa_pct * 4.0), 6)
        max_rr_24h = worst_rr_24h + 8

        # Lab values - worsen with SOFA
        worst_wbc_24h = 10.0 + (sofa_pct * 12.0)
        worst_platelets_24h = 200.0 - (sofa_pct * 100.0)
        worst_hemoglobin_24h = 11.0 - (sofa_pct * 3.0)
        worst_hematocrit_24h = worst_hemoglobin_24h * 3.0

        worst_creatinine_24h = 1.0 + (sofa_pct * 2.5)
        worst_bun_24h = 20.0 + (sofa_pct * 40.0)

        worst_bilirubin_24h = 0.8 + (sofa_pct * 3.0)
        worst_ast_24h = 35.0 + (sofa_pct * 150.0)
        worst_alt_24h = 30.0 + (sofa_pct * 120.0)
        worst_albumin_24h = 3.5 - (sofa_pct * 1.3)

        worst_sodium_24h = 138.0 - (sofa_pct * 8.0)
        worst_potassium_24h = 4.0 + (sofa_pct * 1.5)
        worst_chloride_24h = 102.0 - (sofa_pct * 6.0)
        worst_bicarbonate_24h = 24.0 - (sofa_pct * 8.0)
        worst_glucose_24h = 110.0 + (sofa_pct * 80.0)
        worst_anion_gap_24h = 12.0 + (sofa_pct * 10.0)

        # Acid-base
        worst_ph_24h = 7.40 - (sofa_pct * 0.15)
        worst_paco2_24h = 40.0 + (sofa_pct * 12.0)

        # Coagulation
        worst_inr_24h = 1.0 + (sofa_pct * 1.5)
        worst_ptt_24h = 30.0 + (sofa_pct * 40.0)

        # Cardiac markers
        worst_troponin_24h = 0.03 + (sofa_pct * 0.5)
        worst_bnp_24h = 150.0 + (sofa_pct * 500.0)

        # SOFA component scores
        respiratory_sofa = min(int(sofa_score / 6), 4)
        hepatic_sofa = min(int(sofa_pct * 4), 4)
        coagulation_sofa = min(int(sofa_pct * 4), 4)
        renal_sofa = min(int(sofa_pct * 4), 4)
        neurological_sofa = min(int((15 - gcs_score) / 3), 4)

        # Flags
        ventilation_flag = 1 if mechanical_vent else 0
        vasopressor_flag = 1 if vasopressor else 0
        dialysis_flag = 1 if worst_creatinine_24h > 3.5 else 0
        sepsis_flag = 1 if sofa_score >= 6 else 0
        cardiac_arrest_flag = 1 if sofa_score >= 18 else 0
        trauma_flag = 0

        return {
            # Demographics
            "age": age,
            "gender": 1 if gender == "M" else 0,
            "bmi": 25.0,
            # SOFA components
            "respiratory_sofa": respiratory_sofa,
            "cardiovascular_sofa": cardiovascular_sofa,
            "hepatic_sofa": hepatic_sofa,
            "coagulation_sofa": coagulation_sofa,
            "renal_sofa": renal_sofa,
            "neurological_sofa": neurological_sofa,
            # APACHE-II
            "age_points": age_points,
            "gcs_score": gcs_score,
            # Worst values in 24h - Vitals
            "worst_hr_24h": worst_hr_24h,
            "worst_sbp_24h": worst_sbp_24h,
            "worst_temp_24h": worst_temp_24h,
            "worst_rr_24h": worst_rr_24h,
            "worst_map_24h": worst_map_24h,
            "worst_spo2_24h": worst_spo2_24h,
            # Worst values - Respiratory
            "worst_pao2_24h": worst_pao2_24h,
            "worst_paco2_24h": worst_paco2_24h,
            "worst_ph_24h": worst_ph_24h,
            "worst_fio2_24h": worst_fio2_24h,
            # Worst values - Labs
            "worst_sodium_24h": worst_sodium_24h,
            "worst_potassium_24h": worst_potassium_24h,
            "worst_chloride_24h": worst_chloride_24h,
            "worst_bicarbonate_24h": worst_bicarbonate_24h,
            "worst_anion_gap_24h": worst_anion_gap_24h,
            "worst_glucose_24h": worst_glucose_24h,
            "worst_creatinine_24h": worst_creatinine_24h,
            "worst_bun_24h": worst_bun_24h,
            "worst_hematocrit_24h": worst_hematocrit_24h,
            "worst_wbc_24h": worst_wbc_24h,
            "worst_platelets_24h": worst_platelets_24h,
            "worst_hemoglobin_24h": worst_hemoglobin_24h,
            "worst_bilirubin_24h": worst_bilirubin_24h,
            "worst_albumin_24h": worst_albumin_24h,
            "worst_lactate_24h": worst_lactate_24h,
            "worst_ast_24h": worst_ast_24h,
            "worst_alt_24h": worst_alt_24h,
            "worst_inr_24h": worst_inr_24h,
            "worst_ptt_24h": worst_ptt_24h,
            "worst_troponin_24h": worst_troponin_24h,
            "worst_bnp_24h": worst_bnp_24h,
            # Min/Max vitals
            "min_hr_24h": min_hr_24h,
            "max_hr_24h": max_hr_24h,
            "min_sbp_24h": min_sbp_24h,
            "max_sbp_24h": max_sbp_24h,
            "min_temp_24h": min_temp_24h,
            "max_temp_24h": max_temp_24h,
            "min_rr_24h": min_rr_24h,
            "max_rr_24h": max_rr_24h,
            # ICU details
            "icu_type": 1,  # Medical ICU
            "icu_los_24h": min(los_hours, 24),
            "admission_source": 1,  # Emergency
            "comorbidity_count": charlson,
            # Flags
            "ventilation_flag": ventilation_flag,
            "vasopressor_flag": vasopressor_flag,
            "dialysis_flag": dialysis_flag,
            "sepsis_flag": sepsis_flag,
            "shock_flag": shock_flag,
            "cardiac_arrest_flag": cardiac_arrest_flag,
            "trauma_flag": trauma_flag,
        }
