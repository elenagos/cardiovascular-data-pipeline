CREATE TABLE IF NOT EXISTS measurements (
                                            id BIGSERIAL PRIMARY KEY,
                                            patient_id INTEGER NOT NULL,
                                            recorded_at TIMESTAMPTZ NOT NULL,
                                            measurement_type VARCHAR(100) NOT NULL,
    measurement_data TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

CREATE INDEX IF NOT EXISTS idx_measurements_patient_time
    ON measurements(patient_id, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_measurements_type
    ON measurements(measurement_type);