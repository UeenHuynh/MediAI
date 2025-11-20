"""
Generate synthetic sample data for development and testing
This creates realistic ICU patient data matching MIMIC-IV schema
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Configuration
N_PATIENTS = 1000  # Number of patients to generate
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "sample"


def generate_patients(n=N_PATIENTS):
    """Generate patient demographics"""
    print(f"Generating {n} patients...")

    patients = pd.DataFrame({
        'subject_id': range(10000, 10000 + n),
        'gender': np.random.choice(['M', 'F'], n, p=[0.55, 0.45]),
        'anchor_age': np.random.randint(18, 90, n),
        'anchor_year': np.random.choice(range(2008, 2020), n),
        'dod': None  # Death date (will be set for mortality cases)
    })

    # Set death date for ~10% of patients
    mortality_mask = np.random.random(n) < 0.10
    patients.loc[mortality_mask, 'dod'] = pd.to_datetime('2019-01-01') + pd.to_timedelta(
        np.random.randint(0, 365, mortality_mask.sum()), unit='D'
    )

    return patients


def generate_icustays(patients_df):
    """Generate ICU stays for patients"""
    print("Generating ICU stays...")

    n = len(patients_df)
    base_time = datetime(2019, 1, 1)

    icustays = pd.DataFrame({
        'stay_id': range(20000, 20000 + n),
        'subject_id': patients_df['subject_id'],
        'hadm_id': range(30000, 30000 + n),
        'intime': [base_time + timedelta(days=np.random.randint(0, 365),
                                         hours=np.random.randint(0, 24))
                   for _ in range(n)],
    })

    # ICU length of stay (hours) - log-normal distribution
    los_hours = np.random.lognormal(mean=2.5, sigma=1.2, size=n)
    los_hours = np.clip(los_hours, 1, 720)  # 1 hour to 30 days

    icustays['outtime'] = icustays['intime'] + pd.to_timedelta(los_hours, unit='h')
    icustays['los'] = los_hours / 24  # Convert to days

    return icustays


def generate_vital_signs(icustays_df):
    """Generate vital signs (chartevents) for ICU stays"""
    print("Generating vital signs...")

    # MIMIC-IV item IDs for vital signs
    vital_items = {
        220045: ('heart_rate', 40, 200, 85, 15),  # (name, min, max, mean, std)
        220179: ('sbp', 60, 220, 120, 20),
        220180: ('dbp', 30, 140, 70, 15),
        223761: ('temperature', 35.0, 40.0, 37.0, 0.8),
        220210: ('respiratory_rate', 8, 40, 16, 4),
        220277: ('spo2', 70, 100, 97, 3),
    }

    all_vitals = []

    for _, stay in icustays_df.iterrows():
        stay_id = stay['stay_id']
        intime = stay['intime']
        outtime = stay['outtime']

        # Generate vitals every 1-4 hours
        current_time = intime
        while current_time < outtime:
            for item_id, (name, vmin, vmax, vmean, vstd) in vital_items.items():
                # Generate realistic value with some noise
                value = np.random.normal(vmean, vstd)
                value = np.clip(value, vmin, vmax)

                all_vitals.append({
                    'stay_id': stay_id,
                    'charttime': current_time,
                    'item_id': item_id,
                    'value': value,
                    'valuenum': value,
                    'valueuom': get_unit(item_id)
                })

            # Next measurement time
            current_time += timedelta(hours=np.random.randint(1, 5))

    chartevents = pd.DataFrame(all_vitals)
    chartevents['chartevents_id'] = range(1, len(chartevents) + 1)

    return chartevents


def get_unit(item_id):
    """Get measurement unit for item_id"""
    units = {
        220045: 'bpm',
        220179: 'mmHg',
        220180: 'mmHg',
        223761: '°C',
        220210: 'insp/min',
        220277: '%',
    }
    return units.get(item_id, '')


def generate_lab_values(icustays_df):
    """Generate laboratory values"""
    print("Generating lab values...")

    lab_items = {
        51300: ('wbc', 2, 30, 10, 3),        # White blood cells
        50813: ('lactate', 0.5, 10, 1.5, 1.5),
        50912: ('creatinine', 0.3, 8, 1.0, 0.8),
        51265: ('platelets', 50, 500, 250, 80),
        50885: ('bilirubin', 0.1, 20, 0.8, 1.5),
        50983: ('sodium', 125, 155, 140, 3),
        50971: ('potassium', 2.5, 6.5, 4.0, 0.5),
        50809: ('glucose', 50, 500, 120, 40),
        51222: ('hemoglobin', 6, 18, 12, 2),
    }

    all_labs = []

    for _, stay in icustays_df.iterrows():
        stay_id = stay['stay_id']
        intime = stay['intime']

        # Generate labs at admission and every 6-12 hours
        for hour_offset in [0, 6, 12, 24, 48]:
            labtime = intime + timedelta(hours=hour_offset)

            if labtime > stay['outtime']:
                break

            for item_id, (name, lmin, lmax, lmean, lstd) in lab_items.items():
                value = np.random.normal(lmean, lstd)
                value = np.clip(value, lmin, lmax)

                all_labs.append({
                    'stay_id': stay_id,
                    'charttime': labtime,
                    'item_id': item_id,
                    'value': value,
                    'valuenum': value,
                    'valueuom': get_lab_unit(item_id)
                })

    labevents = pd.DataFrame(all_labs)
    labevents['chartevents_id'] = range(len(chartevents) + 1,
                                         len(chartevents) + len(labevents) + 1)

    return labevents


def get_lab_unit(item_id):
    """Get lab measurement unit"""
    units = {
        51300: 'K/uL',
        50813: 'mmol/L',
        50912: 'mg/dL',
        51265: 'K/uL',
        50885: 'mg/dL',
        50983: 'mEq/L',
        50971: 'mEq/L',
        50809: 'mg/dL',
        51222: 'g/dL',
    }
    return units.get(item_id, '')


def main():
    """Generate all sample data"""
    print("=" * 60)
    print("Sample Data Generator for MediAI")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate data
    patients = generate_patients()
    icustays = generate_icustays(patients)
    chartevents_vitals = generate_vital_signs(icustays)
    chartevents_labs = generate_lab_values(icustays)

    # Combine chartevents
    chartevents = pd.concat([chartevents_vitals, chartevents_labs], ignore_index=True)
    chartevents = chartevents.sort_values(['stay_id', 'charttime'])

    # Save to CSV
    print("\nSaving data to CSV...")
    patients.to_csv(OUTPUT_DIR / 'patients.csv', index=False)
    icustays.to_csv(OUTPUT_DIR / 'icustays.csv', index=False)
    chartevents.to_csv(OUTPUT_DIR / 'chartevents.csv', index=False)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Patients:     {len(patients):,} records")
    print(f"ICU Stays:    {len(icustays):,} records")
    print(f"Chartevents:  {len(chartevents):,} records")
    print(f"\nTotal size:   {(os.path.getsize(OUTPUT_DIR / 'chartevents.csv') / 1024 / 1024):.1f} MB")
    print(f"Output dir:   {OUTPUT_DIR}")
    print("=" * 60)

    print("\n✓ Sample data generated successfully!")
    print("\nNext steps:")
    print("  1. Start Docker services: docker-compose up -d")
    print("  2. Load data: python scripts/load_sample_data.py")


if __name__ == "__main__":
    main()
