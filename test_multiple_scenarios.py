"""
Test multiple scenarios to check if model predictions vary correctly
"""

import sys
sys.path.append('/home/neeyuhuynh/Desktop/MediAI/apps')

from services.model_service import get_model_service

model_service = get_model_service()

# Base normal patient
base_patient = {
    "age": 65,
    "gender": "M",
    "heart_rate": 80,
    "sbp": 120,
    "dbp": 80,
    "temperature": 37.0,
    "respiratory_rate": 16,
    "spo2": 98,
    "gcs": 15,
    "wbc": 8.0,
    "lactate": 1.0,
    "creatinine": 1.0,
    "bilirubin": 0.8,
    "platelets": 250.0,
    "hemoglobin": 13.5,
    "sodium": 140.0,
    "potassium": 4.0,
    "glucose": 100.0,
    "bun": 15.0,
    "ph": 7.4,
    "pao2": 95.0,
    "paco2": 40.0,
    "bicarbonate": 24.0,
    "albumin": 4.0
}

scenarios = []

# Scenario 1: Normal healthy patient
scenarios.append(("Normal healthy", base_patient.copy()))

# Scenario 2: High lactate (sepsis indicator)
high_lactate = base_patient.copy()
high_lactate.update({"lactate": 4.5, "wbc": 16.0})
scenarios.append(("High lactate + WBC", high_lactate))

# Scenario 3: Hypotension (shock)
hypotension = base_patient.copy()
hypotension.update({"sbp": 70, "dbp": 45, "heart_rate": 130})
scenarios.append(("Hypotension + tachycardia", hypotension))

# Scenario 4: Severe hypoxia
hypoxia = base_patient.copy()
hypoxia.update({"spo2": 80, "respiratory_rate": 35, "pao2": 55.0})
scenarios.append(("Severe hypoxia", hypoxia))

# Scenario 5: Multi-organ failure
mof = base_patient.copy()
mof.update({
    "age": 75,
    "lactate": 7.0,
    "sbp": 65,
    "dbp": 40,
    "heart_rate": 140,
    "temperature": 39.5,
    "respiratory_rate": 38,
    "spo2": 82,
    "gcs": 10,
    "wbc": 25.0,
    "creatinine": 4.0,
    "bilirubin": 3.5,
    "platelets": 60.0,
    "hemoglobin": 7.5,
    "ph": 7.15,
    "pao2": 50.0,
    "bicarbonate": 15.0,
    "albumin": 2.0
})
scenarios.append(("Multi-organ failure (CRITICAL)", mof))

# Scenario 6: Moderate sepsis
moderate = base_patient.copy()
moderate.update({
    "age": 70,
    "lactate": 3.0,
    "sbp": 95,
    "heart_rate": 110,
    "temperature": 38.8,
    "respiratory_rate": 25,
    "wbc": 18.0,
    "creatinine": 1.8,
    "platelets": 120.0
})
scenarios.append(("Moderate sepsis", moderate))

# Scenario 7: Renal failure
renal = base_patient.copy()
renal.update({
    "creatinine": 5.0,
    "bun": 60.0,
    "potassium": 6.0,
    "lactate": 2.5
})
scenarios.append(("Renal failure", renal))

# Scenario 8: Respiratory distress
respiratory = base_patient.copy()
respiratory.update({
    "respiratory_rate": 42,
    "spo2": 85,
    "pao2": 60.0,
    "paco2": 60.0,
    "ph": 7.25
})
scenarios.append(("Respiratory distress", respiratory))

print("=" * 100)
print("TESTING MULTIPLE SCENARIOS")
print("=" * 100)

for name, patient in scenarios:
    result = model_service.predict_sepsis(patient)
    risk_score = result.get('risk_score', 0)
    risk_level = result.get('risk_level', 'Unknown')
    risk_color = result.get('risk_color', '')

    print(f"\n{name:35} | Score: {risk_score:6.2%} | Level: {risk_color} {risk_level}")

    # Print key abnormal values
    abnormal = []
    if patient['lactate'] > 2.0:
        abnormal.append(f"Lactate={patient['lactate']:.1f}")
    if patient['sbp'] < 90:
        abnormal.append(f"SBP={patient['sbp']}")
    if patient['heart_rate'] > 100:
        abnormal.append(f"HR={patient['heart_rate']}")
    if patient['spo2'] < 92:
        abnormal.append(f"SpO2={patient['spo2']}")
    if patient['wbc'] > 12 or patient['wbc'] < 4:
        abnormal.append(f"WBC={patient['wbc']:.1f}")
    if patient['creatinine'] > 1.5:
        abnormal.append(f"Creat={patient['creatinine']:.1f}")
    if patient['temperature'] > 38 or patient['temperature'] < 36:
        abnormal.append(f"Temp={patient['temperature']:.1f}")

    if abnormal:
        print(f"{'':35} | Abnormal: {', '.join(abnormal)}")

print("\n" + "=" * 100)
print("\n✅ Test complete!")
print("\nExpected behavior:")
print("  - Normal healthy: LOW risk (0-30%)")
print("  - Moderate issues: MEDIUM risk (30-60%)")
print("  - Severe/MOF: HIGH-CRITICAL risk (60-100%)")
