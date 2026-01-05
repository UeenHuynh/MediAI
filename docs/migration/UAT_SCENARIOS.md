# User Acceptance Testing (UAT) Scenarios

**Project**: MediAI - ICU Prediction System
**Version**: 2.0 (Phase 0-4 Deployment)
**Date**: December 30, 2024
**Status**: Ready for UAT

---

## 🎯 UAT OBJECTIVES

Test MediAI system from clinical user perspective:
1. **Usability**: Easy to use for ICU clinicians
2. **Accuracy**: Predictions match clinical expectations
3. **Performance**: Fast enough for real-time decision making
4. **Reliability**: Consistent results, no errors
5. **Clinical Utility**: Useful for patient care

---

## 👥 TEST ROLES

### Primary Users:
- **ICU Physicians**: Make treatment decisions based on predictions
- **ICU Nurses**: Monitor patients, input data
- **Clinical Informaticists**: Validate system accuracy

### Test Participants Needed:
- 2 ICU Physicians
- 2 ICU Nurses
- 1 Clinical Informaticist
- 1 QA Tester (technical)

---

## 📋 UAT SCENARIOS

### SCENARIO 1: New Patient Admission to ICU

**User Role**: ICU Physician
**Objective**: Assess sepsis risk for newly admitted patient

**Pre-conditions**:
- Patient just admitted to ICU
- Vital signs and labs available
- User logged into MediAI

**Steps**:
1. Open MediAI application (http://localhost:8504)
2. Navigate to "Sepsis Prediction" page
3. Enter patient demographics:
   - Age: 68
   - Gender: Male
   - BMI: 27.5
4. Enter vital signs (current values):
   - Heart Rate: 105 bpm
   - Blood Pressure: 110/70 mmHg
   - Temperature: 38.2°C
   - Respiratory Rate: 22 breaths/min
5. Enter lab values (most recent):
   - WBC: 14.5 × 10⁹/L
   - Lactate: 2.8 mmol/L
   - Creatinine: 1.4 mg/dL
   - Platelets: 145 × 10⁹/L
   - [... all 42 required features]
6. Click "Predict Sepsis Risk"

**Expected Results**:
- ✅ Form accepts all inputs without errors
- ✅ Prediction returned within 2 seconds
- ✅ Risk score displayed (0-100%)
- ✅ Risk level shown (LOW/MEDIUM/HIGH/CRITICAL)
- ✅ Top contributing features displayed
- ✅ Clinical recommendation provided
- ✅ Results are clinically plausible

**Acceptance Criteria**:
- [ ] All fields validate correctly
- [ ] Prediction completes < 2 seconds
- [ ] Risk assessment matches clinical judgment
- [ ] Recommendations are actionable
- [ ] No system errors

---

### SCENARIO 2: Deteriorating Patient Monitoring

**User Role**: ICU Nurse
**Objective**: Monitor sepsis risk trends over 24 hours

**Pre-conditions**:
- Patient has been in ICU for 12 hours
- Previous sepsis prediction showed LOW risk (8%)
- Patient now showing signs of deterioration

**Steps**:
1. Log into MediAI
2. Navigate to patient dashboard
3. Enter updated vitals:
   - Heart Rate: 125 bpm (increased)
   - Blood Pressure: 95/60 mmHg (decreased)
   - Temperature: 39.1°C (increased)
   - Respiratory Rate: 28 breaths/min (increased)
4. Enter updated labs:
   - WBC: 18.2 × 10⁹/L (increased)
   - Lactate: 4.2 mmol/L (increased)
   - Creatinine: 2.1 mg/dL (worsening renal function)
5. Request new sepsis prediction

**Expected Results**:
- ✅ Risk score increased from 8% → 45%
- ✅ Risk level escalated from LOW → HIGH
- ✅ Recommendation: "Initiate sepsis protocol"
- ✅ Top features show lactate, WBC, HR as contributors
- ✅ System highlights worsening trend

**Acceptance Criteria**:
- [ ] Trend analysis shows deterioration
- [ ] Escalation is clinically appropriate
- [ ] Recommendation aligns with sepsis guidelines
- [ ] Nurse can easily interpret results

---

### SCENARIO 3: Mortality Risk Assessment

**User Role**: ICU Physician
**Objective**: Assess hospital mortality risk for family discussion

**Pre-conditions**:
- Elderly patient, multiple comorbidities
- Day 3 in ICU, requiring mechanical ventilation
- Family requesting prognosis information

**Steps**:
1. Open MediAI mortality prediction
2. Enter patient data (61 features):
   - Age: 82
   - GCS Score: 8 (low consciousness)
   - Worst vitals in 24h:
     - HR: 145 bpm
     - BP: 85/50 mmHg
     - Temperature: 39.5°C
   - Labs (worst in 24h):
     - Lactate: 6.8 mmol/L
     - Creatinine: 3.2 mg/dL
     - Bilirubin: 2.5 mg/dL
   - ICU flags:
     - Mechanical ventilation: Yes
     - Vasopressors: Yes
     - Dialysis: No
   - Diagnosis flags:
     - Sepsis: Yes
     - Septic shock: Yes
3. Request mortality prediction

**Expected Results**:
- ✅ Mortality risk: 65% (HIGH)
- ✅ Risk level: HIGH
- ✅ Top contributing factors:
   1. Age
   2. GCS score (low)
   3. Lactate level
   4. Vasopressor dependency
   5. Septic shock
- ✅ Recommendation: "Consider goals of care discussion"

**Acceptance Criteria**:
- [ ] Risk assessment is clinically reasonable
- [ ] Contributing factors make clinical sense
- [ ] Recommendation appropriate for situation
- [ ] Physician can explain results to family

---

### SCENARIO 4: Invalid Data Handling

**User Role**: ICU Nurse
**Objective**: Test system robustness with data entry errors

**Steps**:
1. Attempt prediction with invalid inputs:
   - Temperature: 150°C (impossible value)
   - Heart Rate: -50 bpm (negative)
   - Age: 200 years (unrealistic)
2. Attempt prediction with missing critical fields:
   - Omit lactate value
   - Omit blood pressure
3. Enter values outside normal ranges but clinically possible:
   - Heart Rate: 180 bpm (very high but possible)
   - Lactate: 15 mmol/L (critically high but possible)

**Expected Results**:
- ✅ System rejects impossible values with clear error messages
- ✅ System prompts for missing required fields
- ✅ System accepts extreme but clinically possible values
- ✅ Error messages are user-friendly, not technical

**Acceptance Criteria**:
- [ ] All validation errors are caught
- [ ] Error messages guide user to correct input
- [ ] No system crashes or 500 errors
- [ ] Extreme but valid values are accepted

---

### SCENARIO 5: Concurrent Users

**User Role**: Multiple users
**Objective**: Test system under realistic load

**Pre-conditions**:
- 5 users logged in simultaneously
- Peak shift time in ICU

**Steps**:
1. User 1: Request sepsis prediction for Patient A
2. User 2: Request mortality prediction for Patient B
3. User 3: Request sepsis prediction for Patient C
4. User 4: View previous prediction history
5. User 5: Request sepsis prediction for Patient D
6. All actions performed within 30-second window

**Expected Results**:
- ✅ All predictions complete successfully
- ✅ No user experiences delays > 3 seconds
- ✅ No predictions mixed between patients
- ✅ All results are accurate and consistent

**Acceptance Criteria**:
- [ ] All 5 users get correct results
- [ ] No performance degradation
- [ ] No data mix-ups between patients
- [ ] System remains stable

---

### SCENARIO 6: Authentication & Security

**User Role**: Security Tester
**Objective**: Verify access controls

**Steps**:
1. Attempt to access prediction API without login
2. Try invalid credentials (wrong username/password)
3. Login with valid credentials
4. Access prediction endpoints
5. Wait for token expiration (30 minutes)
6. Attempt to use expired token

**Expected Results**:
- ✅ Unauthorized access blocked (401 error)
- ✅ Invalid credentials rejected
- ✅ Valid login succeeds, token provided
- ✅ Predictions work with valid token
- ✅ Expired token rejected (401 error)

**Acceptance Criteria**:
- [ ] No unauthorized access possible
- [ ] Authentication required for all predictions
- [ ] Token expiration enforced
- [ ] HIPAA compliance maintained

---

### SCENARIO 7: Clinical Decision Support

**User Role**: ICU Physician
**Objective**: Use predictions to guide treatment decisions

**Case**: Suspected early sepsis

**Steps**:
1. Enter patient data (6 hours into ICU stay)
2. Review sepsis prediction: 22% risk (MEDIUM)
3. Review top contributing factors:
   - Lactate: 3.2 mmol/L (elevated)
   - WBC: 16 × 10⁹/L (elevated)
   - Temperature trend: +0.8°C in 6h
4. System recommendation: "Consider early antibiotic administration"
5. Physician decides to:
   - Order blood cultures
   - Start empiric antibiotics
   - Increase monitoring frequency

**Expected Results**:
- ✅ Prediction helps identify early sepsis
- ✅ Recommendations align with Sepsis-3 guidelines
- ✅ Contributing factors clinically relevant
- ✅ Decision support is helpful, not intrusive

**Acceptance Criteria**:
- [ ] Physician finds prediction useful
- [ ] Recommendations are evidence-based
- [ ] System complements clinical judgment
- [ ] Workflointegrates smoothly into clinical workflow

---

## 📊 UAT METRICS

### Quantitative Metrics:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Prediction Accuracy | >85% | Compare with clinical outcomes |
| Response Time | <2 seconds | Automated testing |
| Error Rate | <1% | Count errors / total predictions |
| User Task Completion | >95% | Observe user completing scenarios |
| System Uptime | >99% | Monitor during UAT period |

### Qualitative Metrics:

| Metric | Evaluation Method |
|--------|-------------------|
| Ease of Use | User survey (1-5 scale) |
| Clinical Utility | Physician interviews |
| Trust in Predictions | User confidence survey |
| Workflow Integration | Observation + feedback |
| Recommendation Quality | Clinical expert review |

---

## ✅ UAT SIGN-OFF CRITERIA

System passes UAT if:
- [ ] All 7 scenarios completed successfully
- [ ] 90%+ of test cases pass
- [ ] No CRITICAL bugs found
- [ ] All security tests pass
- [ ] Response time < 2 seconds (95th percentile)
- [ ] Clinical users rate usability ≥ 4/5
- [ ] Physicians confirm clinical utility
- [ ] No data integrity issues
- [ ] HIPAA compliance verified

---

## 🐛 DEFECT SEVERITY CLASSIFICATION

### CRITICAL (P0) - Must fix before production:
- System crashes
- Data corruption
- Security vulnerabilities
- Incorrect predictions (>10% error)
- HIPAA violations

### HIGH (P1) - Fix before go-live:
- Slow performance (>5 seconds)
- Missing required features
- Validation errors on valid inputs
- Authentication failures

### MEDIUM (P2) - Fix soon:
- UI/UX issues
- Minor validation problems
- Performance degradation under load
- Confusing error messages

### LOW (P3) - Fix when possible:
- Cosmetic issues
- Documentation gaps
- Minor feature requests
- Enhancement suggestions

---

## 📅 UAT SCHEDULE

### Week 1: Preparation
- Day 1-2: Setup test environment
- Day 3: Train test users
- Day 4-5: Dry run scenarios

### Week 2: Execution
- Day 1: Scenarios 1-3 (Basic functionality)
- Day 2: Scenarios 4-5 (Edge cases + load)
- Day 3: Scenarios 6-7 (Security + clinical)
- Day 4: Regression testing of fixes
- Day 5: Sign-off meeting

---

## 📝 TEST DATA

**Available Test Datasets:**
- `data/sample_kaggle/features_sepsis_6h.csv` (500 cases)
- `data/sample_kaggle/features_mortality_24h.csv` (500 cases)

**Test Accounts:**
- Username: `demo`, Password: `demo123` (Physician)
- Username: `admin`, Password: `admin123` (Admin)

---

## 🎯 SUCCESS CRITERIA

UAT is considered successful when:
1. ✅ All critical scenarios pass
2. ✅ Clinical users approve system
3. ✅ Performance meets SLA (< 2s response)
4. ✅ No P0/P1 bugs remaining
5. ✅ Sign-off from clinical stakeholders
6. ✅ Security audit passed
7. ✅ HIPAA compliance confirmed

---

**Document Owner**: QA Team
**Reviewers**: Clinical Informaticist, ICU Medical Director
**Approval Required**: Medical Director, IT Security
**Version**: 1.0
**Last Updated**: December 30, 2024
