# MediAI Model Features Specification
**Complete Feature List for Sepsis & Mortality Prediction Models**

---

## 📊 OVERVIEW

| Model | Features | Target | Prediction Window |
|-------|----------|--------|-------------------|
| **Sepsis** | 42 | Sepsis onset | Within 6 hours |
| **Mortality** | 65 | Hospital mortality | Within 24 hours |

---

## 🔴 MODEL 1: SEPSIS PREDICTION (42 Features)

**Target:** Predict sepsis onset within 6 hours
**Database Table:** `analytics.features_sepsis_6h`

### 1. DEMOGRAPHICS (3 features)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 1 | `age` | int | 18-120 | years | ✅ Yes |
| 2 | `gender` | str | M/F | - | ✅ Yes |
| 3 | `bmi` | float | 10-60 | kg/m² | ✅ Yes |

---

### 2. VITAL SIGNS (5 features)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 4 | `heart_rate` | float | 0-300 | bpm | ✅ Yes |
| 5 | `sbp` | float | 40-250 | mmHg | ✅ Yes |
| 6 | `dbp` | float | 20-150 | mmHg | ✅ Yes |
| 7 | `temperature` | float | 32-42 | °C | ✅ Yes |
| 8 | `respiratory_rate` | float | 0-60 | breaths/min | ✅ Yes |

---

### 3. LABORATORY VALUES (20 features)

#### Core Labs (10 required)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 9 | `wbc` | float | 0-100 | 10^9/L | ✅ Yes |
| 10 | `lactate` | float | 0-30 | mmol/L | ✅ Yes |
| 11 | `creatinine` | float | 0-20 | mg/dL | ✅ Yes |
| 12 | `platelets` | float | 0-1000 | 10^9/L | ✅ Yes |
| 13 | `bilirubin` | float | 0-50 | mg/dL | ✅ Yes |
| 14 | `sodium` | float | 100-180 | mmol/L | ✅ Yes |
| 15 | `potassium` | float | 2-8 | mmol/L | ✅ Yes |
| 16 | `glucose` | float | 0-1000 | mg/dL | ✅ Yes |
| 17 | `hemoglobin` | float | 0-25 | g/dL | ✅ Yes |
| 18 | `bicarbonate` | float | 0-50 | mmol/L | ✅ Yes |

**Lactate Validation:** If lactate >10 mmol/L → Warning (critically high)

#### Extended Labs (10 optional)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 19 | `pao2` | float | 0-800 | mmHg | ❌ Optional |
| 20 | `paco2` | float | 0-150 | mmHg | ❌ Optional |
| 21 | `ph` | float | 6.5-8.0 | - | ❌ Optional |
| 22 | `anion_gap` | float | 0-50 | mmol/L | ❌ Optional |
| 23 | `albumin` | float | 0-10 | g/dL | ❌ Optional |
| 24 | `troponin` | float | 0-100 | ng/mL | ❌ Optional |
| 25 | `bnp` | float | 0-10000 | pg/mL | ❌ Optional |
| 26 | `inr` | float | 0-10 | - | ❌ Optional |
| 27 | `ast` | float | 0-10000 | U/L | ❌ Optional |
| 28 | `alt` | float | 0-10000 | U/L | ❌ Optional |

---

### 4. SOFA SCORES (6 features)

| # | Feature | Type | Range | Description | Required |
|---|---------|------|-------|-------------|----------|
| 29 | `respiratory_sofa` | int | 0-4 | Respiratory system score | ✅ Yes |
| 30 | `cardiovascular_sofa` | int | 0-4 | Cardiovascular score | ✅ Yes |
| 31 | `hepatic_sofa` | int | 0-4 | Liver function score | ✅ Yes |
| 32 | `coagulation_sofa` | int | 0-4 | Coagulation score | ✅ Yes |
| 33 | `renal_sofa` | int | 0-4 | Kidney function score | ✅ Yes |
| 34 | `neurological_sofa` | int | 0-4 | Neurological score | ✅ Yes |

**SOFA Score Total:** Sum of all 6 components (0-24 range)

---

### 5. TEMPORAL TRENDS (6 features)

| # | Feature | Type | Unit | Description | Required |
|---|---------|------|------|-------------|----------|
| 35 | `lactate_trend_12h` | float | mmol/L | Lactate change over 12h | ✅ Yes |
| 36 | `hr_trend_6h` | float | bpm | Heart rate change over 6h | ✅ Yes |
| 37 | `wbc_trend_12h` | float | 10^9/L | WBC change over 12h | ✅ Yes |
| 38 | `sbp_trend_6h` | float | mmHg | SBP change over 6h | ✅ Yes |
| 39 | `temperature_trend_6h` | float | °C | Temperature change over 6h | ✅ Yes |
| 40 | `rr_trend_6h` | float | breaths/min | Respiratory rate change over 6h | ✅ Yes |

**Calculation:** `trend = current_value - value_{time_ago}`
- Positive trend = increasing
- Negative trend = decreasing

---

### 6. TIME FEATURES (2 features)

| # | Feature | Type | Range | Description | Required |
|---|---------|------|-------|-------------|----------|
| 41 | `hour_of_admission` | int | 0-23 | Hour of day (24h format) | ✅ Yes |
| 42 | `icu_los_so_far` | float | ≥0 | ICU length of stay so far (hours) | ✅ Yes |

---

### SEPSIS MODEL SUMMARY

**Total Features:** 42
- **Required:** 32 features
- **Optional:** 10 features (extended labs)

**Feature Groups:**
- Demographics: 3
- Vitals: 5
- Core Labs: 10
- Extended Labs: 10
- SOFA: 6
- Trends: 6
- Time: 2

**Input Example:**
```json
{
  "patient_id": "ICU-12345",
  "features": {
    "age": 65,
    "gender": "M",
    "bmi": 28.5,
    "heart_rate": 110,
    "sbp": 95,
    "dbp": 60,
    "temperature": 38.5,
    "respiratory_rate": 24,
    "wbc": 15.2,
    "lactate": 3.5,
    "creatinine": 1.8,
    "platelets": 120,
    "bilirubin": 1.2,
    "sodium": 138,
    "potassium": 4.1,
    "glucose": 180,
    "hemoglobin": 10.5,
    "bicarbonate": 18,
    "pao2": 75,
    "paco2": 45,
    "ph": 7.32,
    "anion_gap": 15,
    "albumin": 2.8,
    "troponin": null,
    "bnp": null,
    "inr": 1.5,
    "ast": 45,
    "alt": 38,
    "respiratory_sofa": 2,
    "cardiovascular_sofa": 3,
    "hepatic_sofa": 1,
    "coagulation_sofa": 1,
    "renal_sofa": 2,
    "neurological_sofa": 0,
    "lactate_trend_12h": 1.5,
    "hr_trend_6h": 15,
    "wbc_trend_12h": 5.0,
    "sbp_trend_6h": -10,
    "temperature_trend_6h": 1.0,
    "rr_trend_6h": 4,
    "hour_of_admission": 14,
    "icu_los_so_far": 18.5
  }
}
```

---

## 🔵 MODEL 2: MORTALITY PREDICTION (65 Features)

**Target:** Predict hospital mortality within 24 hours
**Database Table:** `analytics.features_mortality_24h`

### 1. SOFA SCORES (6 features)

| # | Feature | Type | Range | Description | Required |
|---|---------|------|-------|-------------|----------|
| 1 | `respiratory_sofa` | int | 0-4 | Respiratory system score | ✅ Yes |
| 2 | `cardiovascular_sofa` | int | 0-4 | Cardiovascular score | ✅ Yes |
| 3 | `hepatic_sofa` | int | 0-4 | Liver function score | ✅ Yes |
| 4 | `coagulation_sofa` | int | 0-4 | Coagulation score | ✅ Yes |
| 5 | `renal_sofa` | int | 0-4 | Kidney function score | ✅ Yes |
| 6 | `neurological_sofa` | int | 0-4 | Neurological score | ✅ Yes |

---

### 2. APACHE-II COMPONENTS (12 features)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 7 | `age_points` | int | 0-6 | points | ✅ Yes |
| 8 | `gcs_score` | int | 3-15 | - | ✅ Yes |
| 9 | `worst_hr_24h` | float | 0-300 | bpm | ✅ Yes |
| 10 | `worst_sbp_24h` | float | 0-300 | mmHg | ✅ Yes |
| 11 | `worst_temp_24h` | float | 30-45 | °C | ✅ Yes |
| 12 | `worst_rr_24h` | float | 0-100 | breaths/min | ✅ Yes |
| 13 | `worst_pao2_24h` | float | 0-800 | mmHg | ❌ Optional |
| 14 | `worst_ph_24h` | float | 6.5-8.0 | - | ❌ Optional |
| 15 | `worst_sodium_24h` | float | 100-200 | mmol/L | ✅ Yes |
| 16 | `worst_potassium_24h` | float | 2-10 | mmol/L | ✅ Yes |
| 17 | `worst_creatinine_24h` | float | 0-30 | mg/dL | ✅ Yes |
| 18 | `worst_hematocrit_24h` | float | 0-100 | % | ✅ Yes |

**GCS (Glasgow Coma Scale):**
- 3-8: Severe (coma)
- 9-12: Moderate
- 13-15: Mild/Normal

---

### 3. WORST VITALS IN 24H (8 features)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 19 | `min_hr_24h` | float | 0-300 | bpm | ✅ Yes |
| 20 | `max_hr_24h` | float | 0-300 | bpm | ✅ Yes |
| 21 | `min_sbp_24h` | float | 0-300 | mmHg | ✅ Yes |
| 22 | `max_sbp_24h` | float | 0-300 | mmHg | ✅ Yes |
| 23 | `min_temp_24h` | float | 30-45 | °C | ✅ Yes |
| 24 | `max_temp_24h` | float | 30-45 | °C | ✅ Yes |
| 25 | `min_rr_24h` | float | 0-100 | breaths/min | ✅ Yes |
| 26 | `max_rr_24h` | float | 0-100 | breaths/min | ✅ Yes |

---

### 4. WORST LABS IN 24H (25 features)

| # | Feature | Type | Range | Unit | Required |
|---|---------|------|-------|------|----------|
| 27 | `worst_wbc_24h` | float | 0-200 | 10^9/L | ✅ Yes |
| 28 | `worst_lactate_24h` | float | 0-50 | mmol/L | ✅ Yes |
| 29 | `worst_platelets_24h` | float | 0-2000 | 10^9/L | ✅ Yes |
| 30 | `worst_bilirubin_24h` | float | 0-100 | mg/dL | ✅ Yes |
| 31 | `worst_glucose_24h` | float | 0-2000 | mg/dL | ✅ Yes |
| 32 | `worst_hemoglobin_24h` | float | 0-30 | g/dL | ✅ Yes |
| 33 | `worst_bicarbonate_24h` | float | 0-100 | mmol/L | ✅ Yes |
| 34-51 | *(Additional 18 worst lab values)* | float | varies | varies | ✅ Yes |

**Note:** Full list includes worst values for all major labs over 24h window

---

### 5. ICU DETAILS (10 features)

| # | Feature | Type | Values/Range | Required |
|---|---------|------|--------------|----------|
| 52 | `icu_type` | str | Medical/Surgical/Cardiac | ✅ Yes |
| 53 | `ventilation_flag` | bool | true/false | ✅ Yes |
| 54 | `vasopressor_flag` | bool | true/false | ✅ Yes |
| 55 | `dialysis_flag` | bool | true/false | ✅ Yes |
| 56 | `age` | int | 18-120 years | ✅ Yes |
| 57 | `gender` | str | M/F | ✅ Yes |
| 58 | `bmi` | float | 10-100 kg/m² | ✅ Yes |
| 59 | `admission_source` | str | Emergency/Transfer/Direct | ✅ Yes |
| 60 | `comorbidity_count` | int | 0-20 | ✅ Yes |
| 61 | `icu_los_24h` | float | 0-24 hours (always 24) | ✅ Yes |

---

### 6. DIAGNOSIS FLAGS (4 features)

| # | Feature | Type | Description | Required |
|---|---------|------|-------------|----------|
| 62 | `sepsis_flag` | bool | Sepsis diagnosis | ✅ Yes |
| 63 | `shock_flag` | bool | Shock state | ✅ Yes |
| 64 | `cardiac_arrest_flag` | bool | Cardiac arrest | ✅ Yes |
| 65 | `trauma_flag` | bool | Trauma patient | ✅ Yes |

---

### MORTALITY MODEL SUMMARY

**Total Features:** 65
- **Required:** 63 features
- **Optional:** 2 features (worst_pao2_24h, worst_ph_24h)

**Feature Groups:**
- SOFA Scores: 6
- APACHE-II: 12
- Worst Vitals (24h): 8
- Worst Labs (24h): 25
- ICU Details: 10
- Diagnosis Flags: 4

**Input Example:**
```json
{
  "patient_id": "ICU-67890",
  "features": {
    "respiratory_sofa": 3,
    "cardiovascular_sofa": 4,
    "hepatic_sofa": 2,
    "coagulation_sofa": 2,
    "renal_sofa": 3,
    "neurological_sofa": 1,
    "age_points": 4,
    "gcs_score": 10,
    "worst_hr_24h": 145,
    "worst_sbp_24h": 85,
    "worst_temp_24h": 39.2,
    "worst_rr_24h": 32,
    "worst_pao2_24h": 65,
    "worst_ph_24h": 7.25,
    "worst_sodium_24h": 148,
    "worst_potassium_24h": 5.5,
    "worst_creatinine_24h": 3.2,
    "worst_hematocrit_24h": 28,
    "min_hr_24h": 55,
    "max_hr_24h": 145,
    "min_sbp_24h": 75,
    "max_sbp_24h": 160,
    "min_temp_24h": 36.2,
    "max_temp_24h": 39.2,
    "min_rr_24h": 12,
    "max_rr_24h": 32,
    "worst_wbc_24h": 22,
    "worst_lactate_24h": 6.5,
    "worst_platelets_24h": 85,
    "worst_bilirubin_24h": 3.5,
    "worst_glucose_24h": 280,
    "worst_hemoglobin_24h": 8.5,
    "worst_bicarbonate_24h": 15,
    "icu_type": "Medical",
    "ventilation_flag": true,
    "vasopressor_flag": true,
    "dialysis_flag": false,
    "age": 72,
    "gender": "F",
    "bmi": 32,
    "admission_source": "Emergency",
    "comorbidity_count": 5,
    "icu_los_24h": 24,
    "sepsis_flag": true,
    "shock_flag": true,
    "cardiac_arrest_flag": false,
    "trauma_flag": false
  }
}
```

---

## 📋 FEATURE COMPARISON

| Aspect | Sepsis Model | Mortality Model |
|--------|--------------|-----------------|
| **Total Features** | 42 | 65 |
| **Time Window** | Current + 6-12h trends | 24h worst values |
| **Required** | 32 | 63 |
| **Optional** | 10 | 2 |
| **Focus** | Early detection | Severity assessment |
| **Temporal Trends** | ✅ Yes (6 features) | ❌ No |
| **SOFA Scores** | ✅ Yes (6) | ✅ Yes (6) |
| **APACHE-II** | ❌ No | ✅ Yes (12) |
| **Worst Values** | ❌ No | ✅ Yes (33) |

---

## 🎯 FEATURE IMPORTANCE (Typical SHAP Values)

### Sepsis Model - Top 10 Features

| Rank | Feature | Avg SHAP | Description |
|------|---------|----------|-------------|
| 1 | `lactate` | 0.18 | Serum lactate level |
| 2 | `cardiovascular_sofa` | 0.15 | CV SOFA score |
| 3 | `sbp` | 0.12 | Systolic blood pressure |
| 4 | `lactate_trend_12h` | 0.11 | Lactate change |
| 5 | `wbc` | 0.09 | White blood cell count |
| 6 | `temperature` | 0.08 | Body temperature |
| 7 | `respiratory_sofa` | 0.07 | Respiratory SOFA |
| 8 | `heart_rate` | 0.06 | Heart rate |
| 9 | `platelets` | 0.05 | Platelet count |
| 10 | `creatinine` | 0.05 | Creatinine level |

### Mortality Model - Top 10 Features

| Rank | Feature | Avg SHAP | Description |
|------|---------|----------|-------------|
| 1 | `cardiovascular_sofa` | 0.22 | CV SOFA score |
| 2 | `gcs_score` | 0.18 | Glasgow Coma Scale |
| 3 | `worst_lactate_24h` | 0.16 | Worst lactate in 24h |
| 4 | `vasopressor_flag` | 0.14 | Vasopressor use |
| 5 | `age_points` | 0.12 | APACHE-II age points |
| 6 | `worst_sbp_24h` | 0.10 | Worst SBP in 24h |
| 7 | `ventilation_flag` | 0.09 | Mechanical ventilation |
| 8 | `renal_sofa` | 0.08 | Renal SOFA score |
| 9 | `shock_flag` | 0.07 | Shock diagnosis |
| 10 | `worst_creatinine_24h` | 0.06 | Worst creatinine |

---

## 🔧 FEATURE ENGINEERING PIPELINE

### Preprocessing Steps

1. **Missing Value Imputation**
   ```python
   # For required features
   - Median imputation for numeric
   - Mode imputation for categorical

   # For optional features
   - Allow NULL values
   - Model handles missing data
   ```

2. **Outlier Detection**
   ```python
   # Flag extreme values
   - lactate > 10 mmol/L → Warning
   - temperature < 32°C or > 42°C → Warning
   - heart_rate > 250 bpm → Warning
   ```

3. **Normalization**
   ```python
   # StandardScaler for continuous features
   from sklearn.preprocessing import StandardScaler

   scaler.fit(train_data)
   scaled_features = scaler.transform(test_data)
   ```

4. **Feature Validation**
   ```python
   # Pydantic schema validation
   - Type checking
   - Range validation
   - Required field verification
   ```

---

## 📖 USAGE EXAMPLES

### Example 1: Sepsis Prediction (Minimal Required)

```python
from api.models.schemas import SepsisPredictionRequest, SepsisFeatures

request = SepsisPredictionRequest(
    patient_id="ICU-001",
    features=SepsisFeatures(
        # Demographics
        age=65, gender="M", bmi=28.5,

        # Vitals
        heart_rate=110, sbp=95, dbp=60,
        temperature=38.5, respiratory_rate=24,

        # Core Labs
        wbc=15.2, lactate=3.5, creatinine=1.8,
        platelets=120, bilirubin=1.2, sodium=138,
        potassium=4.1, glucose=180, hemoglobin=10.5,
        bicarbonate=18,

        # SOFA Scores
        respiratory_sofa=2, cardiovascular_sofa=3,
        hepatic_sofa=1, coagulation_sofa=1,
        renal_sofa=2, neurological_sofa=0,

        # Temporal Trends
        lactate_trend_12h=1.5, hr_trend_6h=15,
        wbc_trend_12h=5.0, sbp_trend_6h=-10,
        temperature_trend_6h=1.0, rr_trend_6h=4,

        # Time Features
        hour_of_admission=14, icu_los_so_far=18.5
    )
)
```

### Example 2: Mortality Prediction (Full Features)

```python
from api.models.schemas import MortalityPredictionRequest, MortalityFeatures

request = MortalityPredictionRequest(
    patient_id="ICU-002",
    features=MortalityFeatures(
        # SOFA Scores (same as sepsis)
        respiratory_sofa=3, cardiovascular_sofa=4,
        hepatic_sofa=2, coagulation_sofa=2,
        renal_sofa=3, neurological_sofa=1,

        # APACHE-II Components
        age_points=4, gcs_score=10,
        worst_hr_24h=145, worst_sbp_24h=85,
        worst_temp_24h=39.2, worst_rr_24h=32,
        worst_sodium_24h=148, worst_potassium_24h=5.5,
        worst_creatinine_24h=3.2, worst_hematocrit_24h=28,

        # Worst Vitals
        min_hr_24h=55, max_hr_24h=145,
        min_sbp_24h=75, max_sbp_24h=160,
        min_temp_24h=36.2, max_temp_24h=39.2,
        min_rr_24h=12, max_rr_24h=32,

        # Worst Labs
        worst_wbc_24h=22, worst_lactate_24h=6.5,
        worst_platelets_24h=85, worst_bilirubin_24h=3.5,
        worst_glucose_24h=280, worst_hemoglobin_24h=8.5,
        worst_bicarbonate_24h=15,

        # ICU Details
        icu_type="Medical",
        ventilation_flag=True, vasopressor_flag=True,
        dialysis_flag=False,
        age=72, gender="F", bmi=32,
        admission_source="Emergency",
        comorbidity_count=5, icu_los_24h=24,

        # Diagnosis Flags
        sepsis_flag=True, shock_flag=True,
        cardiac_arrest_flag=False, trauma_flag=False
    )
)
```

---

## ⚠️ IMPORTANT NOTES

### Data Quality Requirements

1. **Temporal Consistency**
   - Trends must be calculated from historical data
   - Cannot use future values
   - Missing historical data → trend = 0

2. **Clinical Validity**
   - All values must be physiologically plausible
   - Extreme outliers should be verified
   - Conflicting values should be flagged

3. **Missing Data Handling**
   - Required features: MUST be provided or imputed
   - Optional features: Can be NULL
   - Model trained with missingness patterns

### Model Limitations

1. **Sepsis Model**
   - Designed for ICU patients only
   - Requires minimum 6h of ICU stay for trends
   - Not validated for pediatric patients

2. **Mortality Model**
   - Requires 24h of ICU data
   - Best for first 24h prediction
   - Not designed for long-term survival

---

## 📚 REFERENCES

**Feature Engineering:**
- MIMIC-IV Database: https://mimic.mit.edu/
- SOFA Score: Vincent JL, et al. Intensive Care Med. 1996
- APACHE-II: Knaus WA, et al. Crit Care Med. 1985

**Model Development:**
- LightGBM: Ke G, et al. NIPS 2017
- SHAP Values: Lundberg SM, et al. NeurIPS 2017

---

**Document Version:** 1.0
**Last Updated:** 2025-12-17
**Status:** Production
**Related Files:**
- `/api/models/schemas.py` - Pydantic schemas
- `/api/services/prediction_service.py` - Prediction logic
- `/docs/architecturev3.mmd` - Architecture diagram
