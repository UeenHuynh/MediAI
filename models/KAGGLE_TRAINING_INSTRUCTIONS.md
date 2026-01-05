# 🏥 MediAI - Kaggle Training Instructions

Hướng dẫn train lại models trên Kaggle với features mới (V2)

---

## 📋 TẠI SAO CẦN TRAIN LẠI?

**Vấn đề phát hiện:**
- Models cũ (v1) train với 42 features KHÁC so với CSV production
- CSV production có 42 features (sepsis) và 61 features (mortality)
- Model expects derived features (shock_index, qSOFA), nhưng CSV có SOFA components + temporal trends

**Giải pháp:**
- Train lại models với **CHÍNH XÁC** features từ CSV files
- Đảm bảo: Model features = CSV features = Schema features

---

## 🚀 SETUP TRÊN KAGGLE

### Step 1: Tạo Kaggle Datasets

#### 1.1 Sepsis Dataset
1. Vào Kaggle → Your Work → Datasets → New Dataset
2. Upload file: `data/sample_kaggle/features_sepsis_6h.csv`
3. Dataset name: `mediai-sepsis`
4. Make private
5. Create

#### 1.2 Mortality Dataset
1. Vào Kaggle → Your Work → Datasets → New Dataset
2. Upload file: `data/sample_kaggle/features_mortality_24h.csv`
3. Dataset name: `mediai-mortality`
4. Make private
5. Create

### Step 2: Tạo Kaggle Notebooks

#### 2.1 Sepsis Training Notebook
1. Vào Kaggle → Your Work → Notebooks → New Notebook
2. Settings:
   - Type: Notebook
   - Language: Python
   - Accelerator: **GPU T4 x2** (IMPORTANT!)
   - Internet: ON
3. Add Data:
   - Click "Add data" → Search "mediai-sepsis" → Add your dataset
4. Copy-paste code từ `models/kaggle_sepsis_training_v2.py` vào notebook
5. Title: "MediAI - Sepsis Model V2 Training"

#### 2.2 Mortality Training Notebook
1. Tương tự như Sepsis
2. Add Data: "mediai-mortality"
3. Copy code từ `models/kaggle_mortality_training_v2.py`
4. Title: "MediAI - Mortality Model V2 Training"

---

## ▶️ CHẠY TRAINING

### Sepsis Model

1. **Run All Cells** (hoặc Ctrl+Enter từng cell)
2. **Expected Runtime**: 5-10 minutes với GPU
3. **Expected Outputs**:
   ```
   ✅ Features: 42
   ✅ Samples: 500
   ✅ AUC-ROC: ~0.85-0.95
   ```

4. **Download Files** (từ Output tab):
   - `sepsis_lightgbm_v2.pkl` (~2-5 MB)
   - `sepsis_feature_names_v2.pkl`
   - `sepsis_model_metadata_v2.json`
   - `sepsis_feature_importance_v2.csv`
   - `sepsis_feature_importance_v2.png`
   - `sepsis_roc_curve_v2.png`

### Mortality Model

1. **Run All Cells**
2. **Expected Runtime**: 7-12 minutes với GPU (61 features)
3. **Expected Outputs**:
   ```
   ✅ Features: 61
   ✅ Samples: 500
   ✅ AUC-ROC: ~0.80-0.90
   ```

4. **Download Files**:
   - `mortality_lightgbm_v2.pkl` (~3-7 MB)
   - `mortality_feature_names_v2.pkl`
   - `mortality_model_metadata_v2.json`
   - `mortality_feature_importance_v2.csv`
   - `mortality_feature_importance_v2.png`
   - `mortality_roc_curve_v2.png`

---

## 📥 SAU KHI TRAINING XONG

### 1. Copy models về local

```bash
# Tạo thư mục backup
mkdir -p api/models/backup_v1
mv api/models/*.pkl api/models/backup_v1/ 2>/dev/null || true

# Copy models mới từ Kaggle downloads
cp ~/Downloads/sepsis_lightgbm_v2.pkl api/models/
cp ~/Downloads/sepsis_feature_names_v2.pkl api/models/
cp ~/Downloads/mortality_lightgbm_v2.pkl api/models/
cp ~/Downloads/mortality_feature_names_v2.pkl api/models/

# Verify
ls -lh api/models/*.pkl
```

### 2. Test models locally

```bash
# Test sepsis model
python3 -c "
import joblib
model = joblib.load('api/models/sepsis_lightgbm_v2.pkl')
features = joblib.load('api/models/sepsis_feature_names_v2.pkl')
print(f'✅ Sepsis model loaded: {len(features)} features')
"

# Test mortality model
python3 -c "
import joblib
model = joblib.load('api/models/mortality_lightgbm_v2.pkl')
features = joblib.load('api/models/mortality_feature_names_v2.pkl')
print(f'✅ Mortality model loaded: {len(features)} features')
"
```

### 3. Verify consistency

```bash
python3 /tmp/check_model_features.py
```

Expected output:
```
🎉 TẤT CẢ ĐỀU KHỚP! Models, CSV, và Schemas đồng bộ 100%
```

---

## 🔧 TROUBLESHOOTING

### Lỗi: "GPU not available"
**Solution**: Settings → Accelerator → GPU T4 x2

### Lỗi: "Dataset not found"
**Solution**:
1. Kiểm tra dataset path trong code:
   ```python
   CSV_PATH = '/kaggle/input/mediai-sepsis/features_sepsis_6h.csv'
   ```
2. Đảm bảo dataset name khớp với tên bạn đã tạo

### Lỗi: "Out of memory"
**Solution**: Reduce `num_boost_round` từ 1000 → 500

### AUC quá thấp (<0.70)
**Reasons**:
- Data quality issues
- Class imbalance không được handle đúng
- Check label distribution: `df['sepsis_label'].value_counts()`

---

## 📊 EXPECTED METRICS

### Sepsis Model (42 features)
- **AUC-ROC**: 0.85 - 0.95
- **Accuracy**: 0.75 - 0.85
- **Recall**: 0.70 - 0.90 (ưu tiên cao, tránh miss sepsis cases)
- **Training time**: 5-10 mins

### Mortality Model (61 features)
- **AUC-ROC**: 0.80 - 0.90
- **Accuracy**: 0.80 - 0.90
- **Recall**: 0.65 - 0.85
- **Training time**: 7-12 mins

---

## ✅ CHECKLIST SAU KHI HOÀN THÀNH

- [ ] Sepsis model trained & downloaded
- [ ] Mortality model trained & downloaded
- [ ] Models copied to `api/models/`
- [ ] Feature consistency verified (run check script)
- [ ] Metadata files saved
- [ ] Feature importance plots reviewed
- [ ] AUC-ROC >= expected thresholds
- [ ] Models tested locally with sample predictions

---

## 🎯 NEXT STEPS

After models are trained and verified:

1. **Update API service** to use v2 models
2. **Run integration tests** (Phase 4)
3. **Deploy to staging**
4. **Monitor predictions** in production

---

**Last Updated**: December 30, 2024
**Version**: 2.0
**Status**: Ready for Kaggle Training
