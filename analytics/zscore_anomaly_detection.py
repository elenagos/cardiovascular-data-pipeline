import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)


MEDIUM_Z_THRESHOLD = 3.0
HIGH_Z_THRESHOLD = 4.0


# Avoid division by extremely small standard deviation.
STD_EPSILON = 1e-9


# ============================================================
# DATABASE
# ============================================================

def create_db_engine():
    return create_engine(
        DATABASE_URL
    )


# ============================================================
# LOAD ROLLING STATISTICS
# ============================================================

def load_rolling_statistics(engine):
    query = """
    SELECT
        measurement_id,
        patient_id,
        recorded_at,
        measurement_type,
        measurement_value,
        rolling_mean,
        rolling_std
    FROM rolling_statistics
    ORDER BY
        patient_id,
        measurement_type,
        recorded_at
    """

    return pd.read_sql(
        query,
        engine
    )


# ============================================================
# Z-SCORE
# ============================================================

def calculate_z_scores(df):
    df = df.copy()

    valid_baseline = (
            df["rolling_mean"].notna()
            &
            df["rolling_std"].notna()
            &
            (
                    df["rolling_std"].abs()
                    > STD_EPSILON
            )
    )

    df["z_score"] = np.nan

    df.loc[
        valid_baseline,
        "z_score"
    ] = (
            (
                    df.loc[
                        valid_baseline,
                        "measurement_value"
                    ]
                    -
                    df.loc[
                        valid_baseline,
                        "rolling_mean"
                    ]
            )
            /
            df.loc[
                valid_baseline,
                "rolling_std"
            ]
    )

    return df


# ============================================================
# ANOMALY CLASSIFICATION
# ============================================================

def classify_anomalies(df):
    df = df.copy()

    absolute_z = (
        df["z_score"].abs()
    )

    df["is_anomaly"] = (
            absolute_z
            >= MEDIUM_Z_THRESHOLD
    )

    df["anomaly_level"] = "NORMAL"

    df.loc[
        (
                absolute_z
                >= MEDIUM_Z_THRESHOLD
        )
        &
        (
                absolute_z
                < HIGH_Z_THRESHOLD
        ),
        "anomaly_level"
    ] = "MEDIUM"

    df.loc[
        absolute_z
        >= HIGH_Z_THRESHOLD,
        "anomaly_level"
    ] = "HIGH"

    # Measurements without enough rolling history
    # cannot yet be evaluated statistically.
    df.loc[
        df["z_score"].isna(),
        "anomaly_level"
    ] = "INSUFFICIENT_HISTORY"

    df["is_anomaly"] = (
        df["is_anomaly"]
        .fillna(False)
        .astype(bool)
    )

    return df


# ============================================================
# BUILD FINAL TABLE
# ============================================================

def build_zscore_analysis(df):
    df = calculate_z_scores(
        df
    )

    df = classify_anomalies(
        df
    )

    df["updated_at"] = (
        pd.Timestamp.now(
            tz="UTC"
        )
    )

    columns = [
        "measurement_id",
        "patient_id",
        "recorded_at",
        "measurement_type",
        "measurement_value",
        "rolling_mean",
        "rolling_std",
        "z_score",
        "is_anomaly",
        "anomaly_level",
        "updated_at",
    ]

    return df[
        columns
    ]


# ============================================================
# SAVE TO DATABASE
# ============================================================

def save_zscore_analysis(
        result,
        engine
):
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE "
                "zscore_analysis"
            )
        )

    result.to_sql(
        "zscore_analysis",
        engine,
        if_exists="append",
        index=False
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(result):
    evaluated = result[
        result["z_score"].notna()
    ]

    anomalies = result[
        result["is_anomaly"]
    ]

    print()
    print(
        "Z-score anomaly detection summary"
    )

    print(
        f"Total measurements: "
        f"{len(result):,}"
    )

    print(
        f"Evaluated measurements: "
        f"{len(evaluated):,}"
    )

    print(
        f"Detected anomalies: "
        f"{len(anomalies):,}"
    )

    if len(evaluated) > 0:
        anomaly_rate = (
                len(anomalies)
                / len(evaluated)
        )

        print(
            f"Anomaly rate: "
            f"{anomaly_rate:.2%}"
        )

    print()

    print(
        "By anomaly level:"
    )

    print(
        result[
            "anomaly_level"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Anomalies by measurement type:"
    )

    if anomalies.empty:
        print(
            "No anomalies detected."
        )
    else:
        print(
            anomalies[
                "measurement_type"
            ]
            .value_counts()
            .to_string()
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
        "Loading rolling statistics..."
    )

    rolling_df = (
        load_rolling_statistics(
            engine
        )
    )

    print(
        f"Loaded {len(rolling_df):,} rows."
    )

    if rolling_df.empty:
        print(
            "No rolling statistics found. "
            "Run rolling_statistics.py first."
        )
        return

    print(
        "Calculating z-scores..."
    )

    result = (
        build_zscore_analysis(
            rolling_df
        )
    )

    print(
        "Saving z-score analysis..."
    )

    save_zscore_analysis(
        result,
        engine
    )

    print_summary(
        result
    )


if __name__ == "__main__":
    main()