# Data Source Documentation

**Version:** 1.0
**Last Updated:** 2025-01-21
**Status:** FINAL - Use this as single source of truth

---

## Official Data Source

### ✅ Kaggle Dataset (RECOMMENDED)

**Dataset:** `akshaybe/updated-mimic-iv`
**URL:** https://www.kaggle.com/datasets/akshaybe/updated-mimic-iv
**Size:** ~5 GB (cleaned ICU data)
**Access:** Public - No approval required

#### Download Method

```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("akshaybe/updated-mimic-iv")
print("Path to dataset files:", path)
```

Or use provided script:
```bash
python scripts/download_data.py
```

#### What's Included

The Kaggle dataset contains the following cleaned tables:

1. **icustays.csv** - ICU stay information (~73K stays)
2. **patients.csv** - Patient demographics
3. **admissions.csv** - Hospital admissions
4. **chartevents.csv** - Vital signs (heart rate, BP, temperature, etc.)
5. **labevents.csv** - Laboratory results (WBC, lactate, creatinine, etc.)
6. **diagnoses_icd.csv** - ICD-10 diagnosis codes

#### Advantages

✅ **No approval required** (publicly available)
✅ **Pre-cleaned** (outliers removed, types validated)
✅ **Smaller size** (~5GB vs 15GB)
✅ **Faster download** (Kaggle CDN)
✅ **Same schema** (compatible with MIMIC-IV item IDs)

---

## Alternative: PhysioNet MIMIC-IV (NOT RECOMMENDED)

**Dataset:** MIMIC-IV v3.1 ICU Module
**URL:** https://physionet.org/content/mimiciv/3.1/
**Size:** ~15 GB (ICU module)
**Access:** Requires credentialed access (2-3 days approval)

### Why NOT Recommended

❌ Requires PhysioNet account
❌ Must complete CITI training (2 hours)
❌ Wait 1-3 business days for approval
❌ Larger download (15GB)
❌ Raw data (needs more cleaning)

### When to Use PhysioNet

Only use PhysioNet if:
- You need the full MIMIC-IV dataset (not just ICU)
- You need specific tables not in Kaggle version
- You're doing research requiring official PhysioNet citation

---

## Dataset Comparison

| Aspect | Kaggle (RECOMMENDED) | PhysioNet |
|--------|---------------------|-----------|
| **Access** | Public, instant | Credentialed, 1-3 days |
| **Size** | ~5 GB | ~15 GB (ICU only) |
| **Training Required** | None | CITI course (2 hours) |
| **Data Quality** | Pre-cleaned | Raw |
| **Download Speed** | Fast (Kaggle CDN) | Slower |
| **Item IDs** | Same as MIMIC-IV | Official MIMIC-IV |
| **Schema** | Compatible | Official |
| **Use Case** | ML development | Research |

---

## Tables & Schema

Both sources use the same table structure. See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for complete schema.

### Core Tables

```
icustays         - ICU stay metadata (stay_id, intime, outtime, los)
patients         - Demographics (subject_id, gender, age)
admissions       - Hospital admissions (hadm_id, admission_type, mortality)
chartevents      - Vitals (itemid, charttime, valuenum)
labevents        - Labs (itemid, charttime, valuenum)
diagnoses_icd    - Diagnoses (icd_code, icd_version)
```

### Important Item IDs

Our models use these MIMIC-IV item IDs (same in both sources):

**Vitals:**
- 220045 = Heart Rate
- 220179 = Systolic BP
- 220180 = Diastolic BP
- 223761 = Temperature
- 220210 = Respiratory Rate
- 220277 = SpO2

**Labs:**
- 51301 = WBC
- 50813 = Lactate
- 50912 = Creatinine
- 50971 = Potassium
- 50983 = Sodium
- 51265 = Platelets
- 51222 = Hemoglobin
- ... (see DATABASE_SCHEMA.md for full list)

---

## Setup Instructions

### Step 1: Install kagglehub

```bash
pip install kagglehub
```

### Step 2: Configure Kaggle Credentials

```bash
# Go to https://www.kaggle.com/settings
# Click "Create New API Token"
# This downloads kaggle.json

# Place in ~/.kaggle/
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Download Dataset

```bash
# Option 1: Use provided script (recommended)
python scripts/download_data.py

# Option 2: Direct download
python -c "import kagglehub; print(kagglehub.dataset_download('akshaybe/updated-mimic-iv'))"
```

### Step 4: Verify Download

```bash
# Check downloaded files
python scripts/download_data.py
# Output shows:
#   ✓ icustays.csv           (XXX MB)
#   ✓ patients.csv           (XXX MB)
#   ✓ chartevents.csv        (XXX MB)
#   ...
```

### Step 5: Ingest to Database

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Ingest data
python scripts/ingest_mimic_iv.py --data-path <path-from-step-3>
```

---

## Data Statistics

### Kaggle Dataset (`akshaybe/updated-mimic-iv`)

```
ICU Stays:        ~73,000 stays
Patients:         ~60,000 unique patients
Chartevents:      ~200M rows (vitals)
Labevents:        ~100M rows (labs)
Diagnoses:        ~500K diagnosis entries
Time Range:       2008-2019 (de-identified)
Age Range:        18-90+ years (de-identified)
Mortality Rate:   ~10% (hospital mortality)
Sepsis Incidence: ~6% (using SEPSIS-3 criteria)
```

---

## Sample Data (for Testing)

If you want to test without downloading the full dataset:

```bash
# Generate synthetic sample data (1000 patients)
python scripts/generate_sample_data.py

# Output: data/sample/*.csv
# - Matches MIMIC-IV schema exactly
# - Realistic distributions
# - Fast for development/testing
```

---

## Data Quality Notes

### Kaggle Dataset Cleaning

The Kaggle dataset has been pre-cleaned:
- ✅ Outliers removed (e.g., heart rate > 300)
- ✅ Invalid values filtered
- ✅ Types validated (numeric columns)
- ✅ Duplicates removed

### Additional Cleaning in Our Pipeline

We perform additional cleaning in staging layer:
```sql
-- Remove physiologically impossible values
WHERE heart_rate BETWEEN 0 AND 300
  AND sbp BETWEEN 40 AND 250
  AND temperature BETWEEN 32 AND 42
```

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) Section 2 (Staging Layer) for details.

---

## Citation

### If Using Kaggle Dataset

```
Dataset: Updated MIMIC-IV
Author: Akshay Behl
Source: Kaggle
URL: https://www.kaggle.com/datasets/akshaybe/updated-mimic-iv
Accessed: [Date]
```

### If Using PhysioNet (Original)

```
Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023).
MIMIC-IV (version 3.1). PhysioNet. https://doi.org/10.13026/6mm1-ek67

Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., ... & Stanley, H. E. (2000).
PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals.
Circulation, 101(23), e215-e220.
```

---

## Troubleshooting

### "kagglehub not found"
```bash
pip install kagglehub
```

### "Kaggle credentials not found"
```bash
# Setup Kaggle API token (see Step 2 above)
# Or manually set environment variables:
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_key
```

### "Download failed"
```bash
# Check internet connection
# Verify Kaggle credentials
kaggle datasets list  # Should work if credentials OK

# Or download manually from Kaggle website
# https://www.kaggle.com/datasets/akshaybe/updated-mimic-iv
# Then extract to data/raw/
```

### "Tables not found after ingestion"
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check data was ingested
psql -U postgres -d mimic_iv -c "\dt raw.*"

# Re-run ingestion if needed
python scripts/ingest_mimic_iv.py --data-path /path/to/data --force
```

---

## Summary

**✅ USE THIS:** Kaggle `akshaybe/updated-mimic-iv`
- Public, instant access
- Pre-cleaned, smaller size
- Perfect for ML development

**❌ DON'T USE:** PhysioNet MIMIC-IV
- Unless you need full dataset
- Or doing official research

**Next Steps:**
1. Install kagglehub
2. Download dataset: `python scripts/download_data.py`
3. Ingest to database: `python scripts/ingest_mimic_iv.py`
4. Build analytics layer: `dbt run --models marts.*`
5. Start developing! 🚀

---

**Questions?** See [CLAUDE.md](CLAUDE.md) for complete development guide.
