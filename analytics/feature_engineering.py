from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)

OUTPUT_DIR = Path("analytics/outputs")
OUTPUT_FILE = OUTPUT_DIR / "patient_features.csv"


EXPECTED_MEASUREMENT_TYPES = {
    "ECG",
    "Saturation",
    "SystolicPressure",
    "DiastolicPressure",
    "Cholesterol",
    "RedBloodCells",
    "WhiteBloodCells",
    "Alert",
}


NUMERIC_MEASUREMENT_TYPES = {
    "ECG",
    "Saturation",
    "SystolicPressure",
    "DiastolicPressure",
    "Cholesterol",
    "RedBloodCells",
    "WhiteBloodCells",
}


PATIENT_FEATURE_COLUMNS = [
    "patient_id",

    "total_measurements",
    "first_measurement",
    "last_measurement",
    "observation_minutes",

    "measurement_types_count",
    "available_expected_types",
    "data_completeness",

    "ecg_count",
    "ecg_mean",
    "ecg_std",
    "ecg_min",
    "ecg_max",

    "saturation_count",
    "saturation_mean",
    "saturation_std",
    "saturation_min",
    "saturation_max",

    "systolicpressure_count",
    "systolicpressure_mean",
    "systolicpressure_std",
    "systolicpressure_min",
    "systolicpressure_max",

    "diastolicpressure_count",
    "diastolicpressure_mean",
    "diastolicpressure_std",
    "diastolicpressure_min",
    "diastolicpressure_max",

    "cholesterol_count",
    "cholesterol_mean",
    "cholesterol_std",
    "cholesterol_min",
    "cholesterol_max",

    "redbloodcells_count",
    "redbloodcells_mean",
    "redbloodcells_std",
    "redbloodcells_min",
    "redbloodcells_max",

    "whitebloodcells_count",
    "whitebloodcells_mean",
    "whitebloodcells_std",
    "whitebloodcells_min",
    "whitebloodcells_max",

    "alert_count",

    "low_saturation_count",
    "low_saturation_rate",

    "abnormal_systolic_count",
    "abnormal_systolic_rate",

    "abnormal_diastolic_count",
    "abnormal_diastolic_rate",

    # Z-score features
    "zscore_anomaly_count",
    "zscore_anomaly_rate",
    "high_zscore_count",
    "max_abs_zscore",

    "updated_at",
]


# ============================================================
# DATABASE
# ============================================================

def create_db_engine():
    return create_engine(
        DATABASE_URL
    )


# ============================================================
# LOAD RAW MEASUREMENTS
# ============================================================

def load_measurements(engine):
    query = """
    SELECT
        id,
        patient_id,
        recorded_at,
        measurement_type,
        measurement_data
    FROM measurements
    ORDER BY patient_id, recorded_at
    """

    return pd.read_sql(
        query,
        engine
    )


# ============================================================
# CLEAN DATA
# ============================================================

def clean_measurements(df):
    df = df.copy()

    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"]
    )

    numeric_text = (
        df["measurement_data"]
        .astype(str)
        .str.extract(
            r"(-?\d+(?:\.\d+)?)",
            expand=False
        )
    )

    df["measurement_value"] = pd.to_numeric(
        numeric_text,
        errors="coerce"
    )

    return df


# ============================================================
# BASIC NUMERIC FEATURES
# ============================================================

def create_numeric_features(df):
    numeric_df = df[
        (
            df["measurement_type"].isin(
                NUMERIC_MEASUREMENT_TYPES
            )
        )
        &
        (
            df["measurement_value"].notna()
        )
        ].copy()

    aggregated = (
        numeric_df
        .groupby(
            [
                "patient_id",
                "measurement_type",
            ]
        )["measurement_value"]
        .agg(
            [
                "count",
                "mean",
                "std",
                "min",
                "max",
            ]
        )
        .reset_index()
    )

    features = aggregated.pivot(
        index="patient_id",
        columns="measurement_type"
    )

    features.columns = [
        f"{measurement_type.lower()}_{statistic}"
        for statistic, measurement_type
        in features.columns
    ]

    return features.reset_index()


# ============================================================
# GENERAL PATIENT FEATURES
# ============================================================

def create_general_features(df):
    features = (
        df
        .groupby("patient_id")
        .agg(
            total_measurements=(
                "id",
                "count"
            ),
            first_measurement=(
                "recorded_at",
                "min"
            ),
            last_measurement=(
                "recorded_at",
                "max"
            ),
            measurement_types_count=(
                "measurement_type",
                "nunique"
            ),
        )
        .reset_index()
    )

    features["observation_minutes"] = (
            (
                    features["last_measurement"]
                    - features["first_measurement"]
            )
            .dt.total_seconds()
            / 60
    )

    return features


# ============================================================
# DATA COMPLETENESS
# ============================================================

def create_completeness_features(df):
    available_types = (
        df
        .groupby("patient_id")[
            "measurement_type"
        ]
        .apply(set)
        .reset_index(
            name="available_types"
        )
    )

    available_types[
        "available_expected_types"
    ] = available_types[
        "available_types"
    ].apply(
        lambda values: len(
            values
            & EXPECTED_MEASUREMENT_TYPES
        )
    )

    available_types[
        "data_completeness"
    ] = (
            available_types[
                "available_expected_types"
            ]
            / len(
        EXPECTED_MEASUREMENT_TYPES
    )
    )

    return available_types[
        [
            "patient_id",
            "available_expected_types",
            "data_completeness",
        ]
    ]


# ============================================================
# ALERT FEATURES
# ============================================================

def create_alert_features(df):
    alert_counts = (
        df[
            df["measurement_type"]
            == "Alert"
            ]
        .groupby("patient_id")
        .size()
        .rename("alert_count")
    )

    result = (
        df[
            ["patient_id"]
        ]
        .drop_duplicates()
        .set_index("patient_id")
        .join(alert_counts)
        .fillna(
            {
                "alert_count": 0
            }
        )
        .reset_index()
    )

    result["alert_count"] = (
        result["alert_count"]
        .astype(int)
    )

    return result


# ============================================================
# SATURATION FEATURES
# ============================================================

def create_saturation_features(df):
    saturation = df[
        (
                df["measurement_type"]
                == "Saturation"
        )
        &
        (
            df["measurement_value"].notna()
        )
        ].copy()

    if saturation.empty:
        return pd.DataFrame(
            columns=[
                "patient_id",
                "low_saturation_count",
                "low_saturation_rate",
            ]
        )

    saturation[
        "is_low_saturation"
    ] = (
            saturation[
                "measurement_value"
            ] < 92
    )

    features = (
        saturation
        .groupby("patient_id")
        .agg(
            total_saturation_readings=(
                "measurement_value",
                "count"
            ),
            low_saturation_count=(
                "is_low_saturation",
                "sum"
            ),
        )
        .reset_index()
    )

    features[
        "low_saturation_rate"
    ] = (
            features[
                "low_saturation_count"
            ]
            /
            features[
                "total_saturation_readings"
            ]
    )

    features = features.drop(
        columns=[
            "total_saturation_readings"
        ]
    )

    return features


# ============================================================
# BLOOD PRESSURE FEATURES
# ============================================================

def create_blood_pressure_features(df):
    patient_ids = (
        df[
            ["patient_id"]
        ]
        .drop_duplicates()
        .copy()
    )

    systolic = df[
        (
                df["measurement_type"]
                == "SystolicPressure"
        )
        &
        (
            df["measurement_value"].notna()
        )
        ].copy()

    diastolic = df[
        (
                df["measurement_type"]
                == "DiastolicPressure"
        )
        &
        (
            df["measurement_value"].notna()
        )
        ].copy()


    if not systolic.empty:
        systolic[
            "abnormal_systolic"
        ] = (
                (
                        systolic[
                            "measurement_value"
                        ] > 140
                )
                |
                (
                        systolic[
                            "measurement_value"
                        ] < 90
                )
        )

        systolic_features = (
            systolic
            .groupby("patient_id")
            .agg(
                total_systolic_readings=(
                    "measurement_value",
                    "count"
                ),
                abnormal_systolic_count=(
                    "abnormal_systolic",
                    "sum"
                ),
            )
            .reset_index()
        )

        systolic_features[
            "abnormal_systolic_rate"
        ] = (
                systolic_features[
                    "abnormal_systolic_count"
                ]
                /
                systolic_features[
                    "total_systolic_readings"
                ]
        )

        systolic_features = (
            systolic_features.drop(
                columns=[
                    "total_systolic_readings"
                ]
            )
        )

        patient_ids = (
            patient_ids.merge(
                systolic_features,
                on="patient_id",
                how="left"
            )
        )


    if not diastolic.empty:
        diastolic[
            "abnormal_diastolic"
        ] = (
                (
                        diastolic[
                            "measurement_value"
                        ] > 90
                )
                |
                (
                        diastolic[
                            "measurement_value"
                        ] < 60
                )
        )

        diastolic_features = (
            diastolic
            .groupby("patient_id")
            .agg(
                total_diastolic_readings=(
                    "measurement_value",
                    "count"
                ),
                abnormal_diastolic_count=(
                    "abnormal_diastolic",
                    "sum"
                ),
            )
            .reset_index()
        )

        diastolic_features[
            "abnormal_diastolic_rate"
        ] = (
                diastolic_features[
                    "abnormal_diastolic_count"
                ]
                /
                diastolic_features[
                    "total_diastolic_readings"
                ]
        )

        diastolic_features = (
            diastolic_features.drop(
                columns=[
                    "total_diastolic_readings"
                ]
            )
        )

        patient_ids = (
            patient_ids.merge(
                diastolic_features,
                on="patient_id",
                how="left"
            )
        )

    return patient_ids


# ============================================================
# Z-SCORE FEATURES
# ============================================================

def create_zscore_features(engine):
    query = """
    SELECT
        patient_id,
        z_score,
        is_anomaly,
        anomaly_level
    FROM zscore_analysis
    WHERE z_score IS NOT NULL
    """

    zscore_df = pd.read_sql(
        query,
        engine
    )

    if zscore_df.empty:
        return pd.DataFrame(
            columns=[
                "patient_id",
                "zscore_anomaly_count",
                "zscore_anomaly_rate",
                "high_zscore_count",
                "max_abs_zscore",
            ]
        )


    # Absolute value tells us how large the deviation is,
    # regardless of whether it is above or below the baseline.
    zscore_df[
        "abs_zscore"
    ] = (
        zscore_df[
            "z_score"
        ].abs()
    )


    zscore_df[
        "is_high_zscore"
    ] = (
            zscore_df[
                "anomaly_level"
            ] == "HIGH"
    )


    features = (
        zscore_df
        .groupby("patient_id")
        .agg(
            zscore_evaluated_count=(
                "z_score",
                "count"
            ),

            zscore_anomaly_count=(
                "is_anomaly",
                "sum"
            ),

            high_zscore_count=(
                "is_high_zscore",
                "sum"
            ),

            max_abs_zscore=(
                "abs_zscore",
                "max"
            ),
        )
        .reset_index()
    )


    features[
        "zscore_anomaly_rate"
    ] = (
            features[
                "zscore_anomaly_count"
            ]
            /
            features[
                "zscore_evaluated_count"
            ]
    )


    features = features.drop(
        columns=[
            "zscore_evaluated_count"
        ]
    )


    # Count variables should be integers.
    features[
        "zscore_anomaly_count"
    ] = (
        features[
            "zscore_anomaly_count"
        ]
        .astype(int)
    )

    features[
        "high_zscore_count"
    ] = (
        features[
            "high_zscore_count"
        ]
        .astype(int)
    )


    return features


# ============================================================
# BUILD BASE PATIENT FEATURES
# ============================================================

def build_patient_features(df):
    general_features = (
        create_general_features(df)
    )

    numeric_features = (
        create_numeric_features(df)
    )

    completeness_features = (
        create_completeness_features(df)
    )

    alert_features = (
        create_alert_features(df)
    )

    saturation_features = (
        create_saturation_features(df)
    )

    blood_pressure_features = (
        create_blood_pressure_features(df)
    )


    features = (
        general_features.copy()
    )


    feature_tables = [
        numeric_features,
        completeness_features,
        alert_features,
        saturation_features,
        blood_pressure_features,
    ]


    for table in feature_tables:
        features = (
            features.merge(
                table,
                on="patient_id",
                how="left"
            )
        )


    columns_to_fill_zero = [
        "alert_count",

        "low_saturation_count",
        "low_saturation_rate",

        "abnormal_systolic_count",
        "abnormal_systolic_rate",

        "abnormal_diastolic_count",
        "abnormal_diastolic_rate",
    ]


    for column in columns_to_fill_zero:
        if column in features.columns:
            features[column] = (
                features[column]
                .fillna(0)
            )


    integer_columns = [
        "patient_id",
        "total_measurements",
        "measurement_types_count",
        "available_expected_types",

        "ecg_count",
        "saturation_count",
        "systolicpressure_count",
        "diastolicpressure_count",
        "cholesterol_count",
        "redbloodcells_count",
        "whitebloodcells_count",

        "alert_count",

        "low_saturation_count",
        "abnormal_systolic_count",
        "abnormal_diastolic_count",
    ]


    for column in integer_columns:
        if column in features.columns:
            features[column] = (
                features[column]
                .fillna(0)
                .astype(int)
            )


    return features.sort_values(
        "patient_id"
    )


# ============================================================
# ADD Z-SCORE FEATURES
# ============================================================

def add_zscore_features(
        patient_features,
        engine
):
    zscore_features = (
        create_zscore_features(
            engine
        )
    )


    patient_features = (
        patient_features.merge(
            zscore_features,
            on="patient_id",
            how="left"
        )
    )


    # If a patient does not have enough rolling history yet,
    # no z-score features will exist for that patient.
    # In that case we use zero.
    zscore_zero_columns = [
        "zscore_anomaly_count",
        "zscore_anomaly_rate",
        "high_zscore_count",
        "max_abs_zscore",
    ]


    for column in zscore_zero_columns:
        patient_features[
            column
        ] = (
            patient_features[
                column
            ]
            .fillna(0)
        )


    # Counts should be stored as integers.
    patient_features[
        "zscore_anomaly_count"
    ] = (
        patient_features[
            "zscore_anomaly_count"
        ]
        .astype(int)
    )


    patient_features[
        "high_zscore_count"
    ] = (
        patient_features[
            "high_zscore_count"
        ]
        .astype(int)
    )


    return patient_features


# ============================================================
# METADATA
# ============================================================

def add_metadata(
        patient_features
):
    patient_features = (
        patient_features.copy()
    )

    patient_features[
        "updated_at"
    ] = (
        pd.Timestamp.now(
            tz="UTC"
        )
    )

    return patient_features


# ============================================================
# VALIDATE COLUMNS
# ============================================================

def validate_feature_columns(
        patient_features
):
    actual_columns = set(
        patient_features.columns
    )

    expected_columns = set(
        PATIENT_FEATURE_COLUMNS
    )


    missing_columns = (
            expected_columns
            - actual_columns
    )

    extra_columns = (
            actual_columns
            - expected_columns
    )


    if missing_columns:
        raise ValueError(
            "Missing feature columns: "
            + ", ".join(
                sorted(
                    missing_columns
                )
            )
        )


    if extra_columns:
        raise ValueError(
            "Unexpected feature columns: "
            + ", ".join(
                sorted(
                    extra_columns
                )
            )
        )


    return patient_features[
        PATIENT_FEATURE_COLUMNS
    ]


# ============================================================
# SAVE TO DATABASE
# ============================================================

def save_features_to_database(
        patient_features,
        engine
):
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE patient_features"
            )
        )


    patient_features.to_sql(
        "patient_features",
        engine,
        if_exists="append",
        index=False
    )


# ============================================================
# SAVE CSV
# ============================================================

def save_features_to_csv(
        patient_features
):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    patient_features.to_csv(
        OUTPUT_FILE,
        index=False
    )


# ============================================================
# MAIN
# ============================================================

def main():
    print(
        "Connecting to PostgreSQL..."
    )

    engine = create_db_engine()


    print(
        "Loading raw measurements..."
    )

    df = load_measurements(
        engine
    )


    print(
        f"Loaded {len(df):,} measurements."
    )


    if df.empty:
        print(
            "No measurements found."
        )
        return


    print(
        "Cleaning measurements..."
    )

    df = clean_measurements(
        df
    )


    print(
        "Building base patient features..."
    )

    patient_features = (
        build_patient_features(
            df
        )
    )


    print(
        "Adding Z-score patient features..."
    )

    patient_features = (
        add_zscore_features(
            patient_features,
            engine
        )
    )


    print(
        "Adding metadata..."
    )

    patient_features = (
        add_metadata(
            patient_features
        )
    )


    print(
        "Validating feature columns..."
    )

    patient_features = (
        validate_feature_columns(
            patient_features
        )
    )


    print()
    print(
        "Z-score feature preview:"
    )

    print(
        patient_features[
            [
                "patient_id",
                "zscore_anomaly_count",
                "zscore_anomaly_rate",
                "high_zscore_count",
                "max_abs_zscore",
            ]
        ]
        .to_string(
            index=False
        )
    )


    print()
    print(
        "Saving patient features "
        "to PostgreSQL..."
    )

    save_features_to_database(
        patient_features,
        engine
    )


    print(
        "Saving CSV backup..."
    )

    save_features_to_csv(
        patient_features
    )


    print()
    print(
        f"Saved {len(patient_features)} "
        f"patients to patient_features."
    )

    print(
        f"CSV backup: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()