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
CREATE TABLE IF NOT EXISTS patient_features (
                                                patient_id INTEGER PRIMARY KEY,

                                                total_measurements BIGINT,
                                                first_measurement TIMESTAMPTZ,
                                                last_measurement TIMESTAMPTZ,
                                                observation_minutes DOUBLE PRECISION,

                                                measurement_types_count INTEGER,
                                                available_expected_types INTEGER,
                                                data_completeness DOUBLE PRECISION,

                                                ecg_count BIGINT,
                                                ecg_mean DOUBLE PRECISION,
                                                ecg_std DOUBLE PRECISION,
                                                ecg_min DOUBLE PRECISION,
                                                ecg_max DOUBLE PRECISION,

                                                saturation_count BIGINT,
                                                saturation_mean DOUBLE PRECISION,
                                                saturation_std DOUBLE PRECISION,
                                                saturation_min DOUBLE PRECISION,
                                                saturation_max DOUBLE PRECISION,

                                                systolicpressure_count BIGINT,
                                                systolicpressure_mean DOUBLE PRECISION,
                                                systolicpressure_std DOUBLE PRECISION,
                                                systolicpressure_min DOUBLE PRECISION,
                                                systolicpressure_max DOUBLE PRECISION,

                                                diastolicpressure_count BIGINT,
                                                diastolicpressure_mean DOUBLE PRECISION,
                                                diastolicpressure_std DOUBLE PRECISION,
                                                diastolicpressure_min DOUBLE PRECISION,
                                                diastolicpressure_max DOUBLE PRECISION,

                                                cholesterol_count BIGINT,
                                                cholesterol_mean DOUBLE PRECISION,
                                                cholesterol_std DOUBLE PRECISION,
                                                cholesterol_min DOUBLE PRECISION,
                                                cholesterol_max DOUBLE PRECISION,

                                                redbloodcells_count BIGINT,
                                                redbloodcells_mean DOUBLE PRECISION,
                                                redbloodcells_std DOUBLE PRECISION,
                                                redbloodcells_min DOUBLE PRECISION,
                                                redbloodcells_max DOUBLE PRECISION,

                                                whitebloodcells_count BIGINT,
                                                whitebloodcells_mean DOUBLE PRECISION,
                                                whitebloodcells_std DOUBLE PRECISION,
                                                whitebloodcells_min DOUBLE PRECISION,
                                                whitebloodcells_max DOUBLE PRECISION,

                                                alert_count INTEGER,

                                                low_saturation_count INTEGER,
                                                low_saturation_rate DOUBLE PRECISION,

                                                abnormal_systolic_count INTEGER,
                                                abnormal_systolic_rate DOUBLE PRECISION,

                                                abnormal_diastolic_count INTEGER,
                                                abnormal_diastolic_rate DOUBLE PRECISION,

                                                updated_at TIMESTAMPTZ DEFAULT NOW()
    );
