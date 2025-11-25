# 🏥 MediAI - Kaggle Training Instructions

## 📦 Files Created

1. **kaggle_sepsis_training.ipynb** - Sepsis prediction model (42 features)
2. **kaggle_mortality_training.ipynb** - Mortality prediction model (65 features)

---

## 🚀 Quick Start Guide

### Step 1: Upload to Kaggle

1. Go to https://www.kaggle.com/code
2. Click **"New Notebook"**
3. Click **"File" → "Upload Notebook"**
4. Select `kaggle_sepsis_training.ipynb` or `kaggle_mortality_training.ipynb`

### Step 2: Configure Dataset

1. Click **"Add Data"** button (right sidebar)
2. Search for: `akshaybe/updated-mimic-iv`
3. Click **"Add"** to attach dataset

### Step 3: Enable GPU (Optional but Recommended)

1. Click **"Settings"** (right sidebar)
2. Under **"Accelerator"**, select **"GPU T4 x2"**
3. Click **"Save"**

### Step 4: Run Training

1. Click **"Run All"** or press **Ctrl+Enter** on each cell
2. Wait ~15-20 minutes for training to complete
3. Monitor progress in cell outputs

### Step 5: Download Trained Models

1. After training completes, click **"Output"** tab (right sidebar)
2. Download these files:
   - `sepsis_lightgbm_v1.pkl` (~5MB)
   - `sepsis_feature_names.pkl`
   - `sepsis_model_metadata.json`
   - `mortality_lightgbm_v1.pkl` (~5MB)
   - `mortality_feature_names.pkl`
   - `mortality_model_metadata.json`

---

## 📊 Model Specifications

### Sepsis Model (42 Features)

**Feature Categories:**
- Demographics (2): age, gender
- Vital Signs (8): HR, BP, temp, RR, SpO2, GCS, MAP
- Lab Values (15): WBC, lactate, creatinine, bilirubin, platelets, hemoglobin, sodium, potassium, glucose, BUN, pH, PaO2, PaCO2, bicarbonate, albumin
- Clinical Scores (5): SOFA, APACHE-II, qSOFA, SIRS, MEWS
- Derived Features (12): shock index, P/F ratio, BUN/Cr ratio, etc.

**Target:** Sepsis diagnosis (binary: 0=No Sepsis, 1=Sepsis)

**Expected Performance:**
- AUC-ROC: 0.85-0.92
- Accuracy: 80-88%
- Sensitivity: 75-85%
- Specificity: 82-90%

---

### Mortality Model (65 Features)

**Feature Categories:**
- Demographics (2): age, gender
- Worst Vitals in 24h (16): worst HR, BP ranges, temperature ranges, RR, SpO2, GCS
- Worst Lab Values in 24h (20): worst WBC, lactate, creatinine, bilirubin, platelets, hemoglobin, sodium, potassium, glucose, BUN, pH, blood gases, albumin, INR, troponin, BNP
- Clinical Scores (8): SOFA (day 1-3), APACHE-II/III, SAPS-II, qSOFA, SIRS
- Interventions (5): ventilation days, vasopressor use, dialysis, transfusion, ICU LOS
- Comorbidities (8): CHF, CKD, COPD, diabetes, cancer, liver disease, hypertension, immunosuppression
- Derived Features (6): shock index, P/F ratio, BUN/Cr ratio, anion gap, SOFA trend, lactate/albumin ratio

**Target:** Hospital mortality (binary: 0=Survived, 1=Died)

**Expected Performance:**
- AUC-ROC: 0.82-0.90
- Accuracy: 78-86%
- Sensitivity: 70-82%
- Specificity: 80-88%

---

## 🔧 Troubleshooting

### Issue: Dataset not found
**Solution:** 
- Make sure you added `akshaybe/updated-mimic-iv` dataset
- Try alternative: Search "MIMIC-IV" in Kaggle datasets
- Use synthetic data mode (notebooks will auto-generate demo data)

### Issue: GPU out of memory
**Solution:**
- Reduce `num_boost_round` from 1000 to 500
- Reduce `max_depth` from 6 to 4
- Use CPU instead of GPU (remove `'device': 'gpu'` from params)

### Issue: Training too slow
**Solution:**
- Enable GPU in Settings
- Reduce dataset size with sampling: `df = df.sample(n=5000)`
- Reduce number of boosting rounds

### Issue: Low AUC score
**Solution:**
- Check class balance (should be ~50/50 after SMOTE)
- Verify feature engineering (no NaN values)
- Try different hyperparameters:
  - Increase `learning_rate` to 0.1
  - Increase `num_leaves` to 63
  - Adjust `min_data_in_leaf`

---

## 📝 Example Usage After Download

```python
import joblib
import numpy as np

# Load trained model
model = joblib.load('sepsis_lightgbm_v1.pkl')
feature_names = joblib.load('sepsis_feature_names.pkl')

# Example patient data (42 features)
patient_data = {
    'age': 65,
    'gender': 1,
    'heart_rate': 105,
    'sbp': 95,
    'temperature': 38.5,
    'lactate': 3.2,
    'sofa_score': 6,
    # ... other 35 features
}

# Convert to numpy array in correct order
X = np.array([[patient_data[feat] for feat in feature_names]])

# Predict
sepsis_probability = model.predict(X)[0]
sepsis_prediction = 1 if sepsis_probability >= 0.5 else 0

print(f"Sepsis Probability: {sepsis_probability:.2%}")
print(f"Prediction: {'SEPSIS' if sepsis_prediction == 1 else 'NO SEPSIS'}")
```

---

## 🎯 Next Steps for MediAI Integration

After downloading trained models:

1. **Copy files to MediAI repo:**
   ```bash
   mkdir -p models/sepsis models/mortality
   cp sepsis_lightgbm_v1.pkl models/sepsis/
   cp sepsis_feature_names.pkl models/sepsis/
   cp mortality_lightgbm_v1.pkl models/mortality/
   cp mortality_feature_names.pkl models/mortality/
   ```

2. **Update config.yaml:**
   ```yaml
   models:
     sepsis:
       path: models/sepsis/sepsis_lightgbm_v1.pkl
       features: models/sepsis/sepsis_feature_names.pkl
       threshold: 0.5
     mortality:
       path: models/mortality/mortality_lightgbm_v1.pkl
       features: models/mortality/mortality_feature_names.pkl
       threshold: 0.5
   ```

3. **Create API endpoint:**
   ```python
   # api/predict.py
   from fastapi import FastAPI
   import joblib
   
   app = FastAPI()
   sepsis_model = joblib.load('models/sepsis/sepsis_lightgbm_v1.pkl')
   
   @app.post("/predict/sepsis")
   def predict_sepsis(patient_data: dict):
       # Feature extraction
       features = extract_features(patient_data)
       # Prediction
       prob = sepsis_model.predict([features])[0]
       return {"sepsis_probability": float(prob)}
   ```

4. **Test models:**
   ```bash
   python scripts/test_models.py
   ```

---

## 📚 Resources

- **MIMIC-IV Documentation:** https://mimic.mit.edu/docs/iv/
- **LightGBM Docs:** https://lightgbm.readthedocs.io/
- **Kaggle Notebook Tutorial:** https://www.kaggle.com/docs/notebooks
- **SOFA Score Calculator:** https://www.mdcalc.com/sofa-score
- **APACHE-II Calculator:** https://www.mdcalc.com/apache-ii-score

---

## ⚠️ Important Notes

1. **Data Privacy:** MIMIC-IV requires PhysioNet credentialing. Kaggle datasets may be pre-processed versions.
2. **Model Validation:** Always validate on your local clinical data before deployment.
3. **Clinical Use:** These models are for research/educational purposes. Consult medical professionals for clinical decisions.
4. **Performance:** Actual performance depends on data quality and distribution.
5. **Updates:** Retrain models periodically with new data for best performance.

---

## 🤝 Support

If you encounter issues:
1. Check Kaggle notebook comments/discussions
2. Review error messages in notebook outputs
3. Try synthetic data mode first
4. Consult MIMIC-IV documentation

---

**Happy Training! 🚀**

*Generated by MediAI Development Team*
*Last Updated: November 2025*
