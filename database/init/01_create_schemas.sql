-- Initialize database schemas for MIMIC-IV data
-- This script runs automatically when PostgreSQL container starts

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA raw TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA staging TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO postgres;

-- Create sample patients table (raw layer)
CREATE TABLE IF NOT EXISTS raw.patients (
    subject_id INTEGER PRIMARY KEY,
    gender VARCHAR(1),
    anchor_age INTEGER,
    anchor_year INTEGER,
    dod TIMESTAMP
);

-- Create sample ICU stays table (raw layer)
CREATE TABLE IF NOT EXISTS raw.icustays (
    stay_id INTEGER PRIMARY KEY,
    subject_id INTEGER REFERENCES raw.patients(subject_id),
    hadm_id INTEGER,
    intime TIMESTAMP,
    outtime TIMESTAMP,
    los NUMERIC
);

-- Create sample chartevents table (raw layer)
CREATE TABLE IF NOT EXISTS raw.chartevents (
    chartevents_id SERIAL PRIMARY KEY,
    stay_id INTEGER REFERENCES raw.icustays(stay_id),
    charttime TIMESTAMP,
    item_id INTEGER,
    value NUMERIC,
    valuenum NUMERIC,
    valueuom VARCHAR(50)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_subject_id ON raw.patients(subject_id);
CREATE INDEX IF NOT EXISTS idx_icustays_stay_id ON raw.icustays(stay_id);
CREATE INDEX IF NOT EXISTS idx_icustays_subject_id ON raw.icustays(subject_id);
CREATE INDEX IF NOT EXISTS idx_chartevents_stay_id ON raw.chartevents(stay_id);
CREATE INDEX IF NOT EXISTS idx_chartevents_charttime ON raw.chartevents(charttime);
CREATE INDEX IF NOT EXISTS idx_chartevents_item_id ON raw.chartevents(item_id);

-- Create prediction history table (analytics layer)
CREATE TABLE IF NOT EXISTS analytics.prediction_history (
    prediction_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50),
    model_type VARCHAR(20),  -- 'sepsis' or 'mortality'
    risk_score NUMERIC(5,4),
    risk_level VARCHAR(20),
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    features JSONB,
    result JSONB
);

CREATE INDEX IF NOT EXISTS idx_prediction_history_patient_id ON analytics.prediction_history(patient_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_model_type ON analytics.prediction_history(model_type);
CREATE INDEX IF NOT EXISTS idx_prediction_history_time ON analytics.prediction_history(prediction_time DESC);

-- Insert initial comment
COMMENT ON SCHEMA raw IS 'Bronze layer - Raw data from source systems';
COMMENT ON SCHEMA staging IS 'Silver layer - Cleaned and validated data';
COMMENT ON SCHEMA analytics IS 'Gold layer - Business-ready data and features';
