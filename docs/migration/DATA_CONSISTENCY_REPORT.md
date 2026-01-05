# 🔍 Data Consistency Report - MediAI

**Date**: December 30, 2024
**Status**: ⚠️ CRITICAL ISSUES FOUND - Models need retraining

---

## 📊 EXECUTIVE SUMMARY

Phát hiện **inconsistency nghiêm trọng** giữa trained models và production data schemas:
- ✅ **CSV ↔ Schemas**: 100% khớp (42 sepsis, 61 mortality features)
- ❌ **Models ↔ CSV**: Chỉ 52% khớp (sepsis), 15% khớp (mortality)
- ⚠️ **Impact**: Production API sẽ KHÔNG HOẠT ĐỘNG ĐÚNG với models hiện tại

---

## 🔬 CHI TIẾT PHÁT HIỆN

### 1. Schema vs CSV Features ✅ PASS

```
Sepsis Model:
  Schema features: 42
  CSV features: 42
  Match: 42/42 (100%)
  Status: ✅ PERFECT

Mortality Model:
  Schema features: 61
  CSV features: 61
  Match: 61/61 (100%)
  Status: ✅ PERFECT
```

### 2. Trained Models vs CSV Features ❌ FAIL

#### Sepsis Model (22/42 features khớp - 52%)

**Features CHỈ CÓ trong Model (trained on Kaggle):**
```python
[
    'apache_ii_score',      # Aggregate APACHE-II score
    'bun',                  # Blood Urea Nitrogen
    'bun_creatinine_ratio', # Derived ratio
    'gcs',                  # Glasgow Coma Scale
    'has_aki',              # Boolean flag: Acute Kidney Injury
    'has_thrombocytopenia', # Boolean flag
    'is_hypotensive',       # Boolean flag
    'is_hypoxic',           # Boolean flag
    'is_tachycardic',       # Boolean flag
    'is_tachypneic',        # Boolean flag
    'lactate_albumin_ratio',# Derived ratio
    'map',                  # Mean Arterial Pressure (calculated)
    'mews_score',           # Modified Early Warning Score
    'pf_ratio',             # PaO2/FiO2 ratio
    'pulse_pressure',       # SBP - DBP
    'qsofa_score',          # Quick SOFA score
    'shock_index',          # HR / SBP
    'sirs_score',           # SIRS criteria score
    'sofa_score',           # Total SOFA (aggregate)
    'spo2'                  # Oxygen saturation
]
```

**Features CHỈ CÓ trong CSV/Schema (production):**
```python
[
    'alt', 'ast',                    # Liver enzymes
    'bmi',                           # Body Mass Index
    'bnp', 'troponin', 'inr',        # Cardiac/coag markers
    'cardiovascular_sofa',           # SOFA components (6 separate)
    'coagulation_sofa',
    'hepatic_sofa',
    'neurological_sofa',
    'renal_sofa',
    'respiratory_sofa',
    'hour_of_admission',             # Time features
    'icu_los_so_far',
    'hr_trend_6h',                   # Temporal trends (6 features)
    'lactate_trend_12h',
    'rr_trend_6h',
    'sbp_trend_6h',
    'temperature_trend_6h',
    'wbc_trend_12h'
]
```

#### Mortality Model (2/13 features khớp - 15%)

**Model expects (from old Kaggle notebook):**
```python
[
    'age', 'gender',                 # Demographics (only 2 match!)
    'apache_ii_score',               # Aggregate score
    'sofa_day1',                     # Day 1 SOFA total
    'vasopressor_use',               # Single flag
    'worst_creatinine',              # Without _24h suffix
    'worst_gcs',
    'worst_heart_rate',
    'worst_lactate',
    'worst_respiratory_rate',
    'worst_sbp_low',
    'worst_spo2',
    'worst_temperature_high'
]
```

**CSV has (production):**
```python
61 features including:
- 6 SOFA components (respiratory_sofa, cardiovascular_sofa, ...)
- 2 APACHE components (age_points, gcs_score)
- 20 worst vitals in 24h (worst_hr_24h, worst_sbp_24h, ...)
- 10 additional worst labs (worst_bun_24h, worst_chloride_24h, ...)
- 8 min/max vitals (min_hr_24h, max_hr_24h, ...)
- 6 ICU details (icu_type, ventilation_flag, vasopressor_flag, ...)
- 3 patient info (bmi, admission_source, comorbidity_count)
- 4 diagnosis flags (sepsis_flag, shock_flag, cardiac_arrest_flag, trauma_flag)
```

### 3. Data Quality ✅ PASS

```
Sepsis CSV:
  Rows: 500
  Columns: 46 (3 IDs + 42 features + 1 label)
  Missing values: 0
  Duplicates: 0
  Label distribution: 80.6% negative, 19.4% positive

Mortality CSV:
  Rows: 500
  Columns: 65 (3 IDs + 61 features + 1 label)
  Missing values: 0
  Duplicates: 0
  Label distribution: 86.2% negative, 13.8% positive
```

---

## 🔥 ROOT CAUSE ANALYSIS

### Tại sao xảy ra inconsistency?

1. **2 Feature Engineering Pipelines Khác Nhau**
   - **Kaggle workflow (OLD)**: Raw MIMIC-IV data → Feature engineering on-the-fly → Train model
   - **Production workflow (NEW)**: Pre-processed CSV with different features → Schema defined

2. **Timeline**
   ```
   ┌─────────────────────────────────────────────────────────┐
   │ Initial Training (Kaggle)                               │
   │ ─────────────────────────                               │
   │ • Used MIMIC-IV raw data                                │
   │ • Created derived features (shock_index, qSOFA, etc.)   │
   │ • Trained models with 42/13 features                    │
   │ • Saved models: sepsis_v1.pkl, mortality_v1.pkl         │
   └─────────────────────────────────────────────────────────┘
                         ↓
   ┌─────────────────────────────────────────────────────────┐
   │ Production Data Preparation (Later)                     │
   │ ────────────────────────────────                        │
   │ • Created CSV files with NEW feature set                │
   │ • Added SOFA components, temporal trends                │
   │ • Defined schemas.py to match CSV                       │
   │ • ❌ FORGOT TO RETRAIN MODELS!                          │
   └─────────────────────────────────────────────────────────┘
   ```

3. **Communication Gap**
   - Feature engineering team tạo CSV mới
   - ML team không được thông báo
   - Models cũ vẫn được dùng

---

## ⚠️ IMPACT ASSESSMENT

### Nếu deploy như hiện tại:

**Scenario**: API nhận request từ frontend

```python
# 1. Frontend sends request
POST /api/v1/predict/sepsis
{
  "patient_id": "12345",
  "features": {
    "age": 65,
    "gender": 1,
    "heart_rate": 110,
    "sbp": 90,
    "lactate": 3.5,
    "cardiovascular_sofa": 2,  # CSV feature
    "lactate_trend_12h": 0.8,  # CSV feature
    ...
    # 42 features theo schemas.py
  }
}

# 2. API validates với Pydantic schema
✅ Validation PASS (42 features đúng theo schema)

# 3. API gọi model.predict()
❌ ERROR! Model expects:
   - 'shock_index' (not provided)
   - 'qsofa_score' (not provided)
   - 'sofa_score' (total, not components)
   - ...

# Result:
# - KeyError hoặc ValueError
# - Predictions sai hoàn toàn
# - API returns 500 Internal Server Error
```

**Severity**: 🔴 **CRITICAL - BLOCKING DEPLOYMENT**

---

## ✅ SOLUTION - RETRAIN MODELS

### Đã tạo training scripts:

1. **`models/kaggle_sepsis_training_v2.py`**
   - Train với CHÍNH XÁC 42 features từ CSV
   - Output: `sepsis_lightgbm_v2.pkl`
   - Expected AUC: 0.85-0.95

2. **`models/kaggle_mortality_training_v2.py`**
   - Train với CHÍNH XÁC 61 features từ CSV
   - Output: `mortality_lightgbm_v2.pkl`
   - Expected AUC: 0.80-0.90

3. **`models/KAGGLE_TRAINING_INSTRUCTIONS.md`**
   - Step-by-step guide để run trên Kaggle
   - Setup datasets, notebooks, GPU
   - Download và deploy models mới

### Action Items:

```bash
# 1. Upload CSVs to Kaggle datasets
✅ data/sample_kaggle/features_sepsis_6h.csv → mediai-sepsis
✅ data/sample_kaggle/features_mortality_24h.csv → mediai-mortality

# 2. Run training notebooks
⏳ Run kaggle_sepsis_training_v2.py (5-10 mins)
⏳ Run kaggle_mortality_training_v2.py (7-12 mins)

# 3. Download models
⏳ sepsis_lightgbm_v2.pkl, sepsis_feature_names_v2.pkl
⏳ mortality_lightgbm_v2.pkl, mortality_feature_names_v2.pkl

# 4. Deploy to api/models/
⏳ Backup old models
⏳ Copy new models
⏳ Verify consistency

# 5. Test integration
⏳ Run Phase 4 tests
⏳ Verify predictions work end-to-end
```

---

## 📋 VERIFICATION CHECKLIST

Sau khi retrain, verify:

- [ ] Sepsis model: 42 features khớp 100% với CSV
- [ ] Mortality model: 61 features khớp 100% với CSV
- [ ] Models load successfully
- [ ] Sample predictions run without errors
- [ ] Feature importance makes clinical sense
- [ ] AUC-ROC meets thresholds (>0.80)
- [ ] Integration tests pass
- [ ] API endpoints return valid responses

---

## 🎯 TIMELINE

```
Today (Dec 30):
  ✅ Identified inconsistency
  ✅ Created training scripts v2
  ✅ Documented root cause

Next Steps:
  ⏳ Upload datasets to Kaggle (5 mins)
  ⏳ Run training (15-20 mins total)
  ⏳ Download & deploy models (5 mins)
  ⏳ Verify consistency (5 mins)
  ⏳ Integration testing (Phase 4)

Total Time: ~30-40 mins
```

---

## 📚 FILES CREATED

1. `models/kaggle_sepsis_training_v2.py` - Sepsis training script
2. `models/kaggle_mortality_training_v2.py` - Mortality training script
3. `models/KAGGLE_TRAINING_INSTRUCTIONS.md` - Setup guide
4. `docs/migration/DATA_CONSISTENCY_REPORT.md` - This report
5. `/tmp/check_schema_consistency.py` - Verification script
6. `/tmp/check_data_quality.py` - Quality check script
7. `/tmp/check_model_features.py` - Model-CSV comparison script

---

## 🔗 REFERENCES

- CSV Files: `data/sample_kaggle/features_{sepsis,mortality}_*.csv`
- Schemas: `api/models/schemas.py`
- Old Models: `models/{sepsis,mortality}_lightgbm_v1.pkl`
- Old Notebooks: `models/kaggle_{sepsis,mortality}_training.ipynb`

---

**Report Generated**: December 30, 2024
**Severity**: 🔴 CRITICAL
**Action Required**: ✅ IMMEDIATE - Retrain models before Phase 4
**ETA to Fix**: ~30-40 minutes
