-- 1. Последние измерения
SELECT
    id,
    patient_id,
    recorded_at,
    measurement_type,
    measurement_data
FROM measurements
ORDER BY recorded_at DESC
    LIMIT 50;


-- 2. Количество измерений по типам
SELECT
    measurement_type,
    COUNT(*) AS measurement_count
FROM measurements
GROUP BY measurement_type
ORDER BY measurement_count DESC;


-- 3. Количество измерений по пациентам
SELECT
    patient_id,
    COUNT(*) AS measurement_count
FROM measurements
GROUP BY patient_id
ORDER BY patient_id;


-- 4. Последнее измерение каждого типа для каждого пациента
SELECT DISTINCT ON (patient_id, measurement_type)
    patient_id,
    measurement_type,
    recorded_at,
    measurement_data
FROM measurements
ORDER BY
    patient_id,
    measurement_type,
    recorded_at DESC;