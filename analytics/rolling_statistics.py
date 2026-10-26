import pandas as pd
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)


NUMERIC_MEASUREMENT_TYPES = {
    "ECG",
    "Saturation",
    "SystolicPressure",
    "DiastolicPressure",
    "Cholesterol",
    "RedBloodCells",
    "WhiteBloodCells",
}


# Different measurement types arrive with different frequency,
# so we use different rolling windows.
ROLLING_CONFIG = {
    "ECG": {
        "window": 30,
        "min_periods": 10,
    },
    "Saturation": {
        "window": 30,
        "min_periods": 10,
    },
    "SystolicPressure": {
        "window": 5,
        "min_periods": 3,
    },
    "DiastolicPressure": {
        "window": 5,
        "min_periods": 3,
    },
    "Cholesterol": {
        "window": 5,
        "min_periods": 3,
    },
    "RedBloodCells": {
        "window": 5,
        "min_periods": 3,
    },
    "WhiteBloodCells": {
        "window": 5,
        "min_periods": 3,
    },
}


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
    ORDER BY
        patient_id,
        measurement_type,
        recorded_at
    """

    return pd.read_sql(
        query,
        engine,
    )


# ============================================================
# CLEAN DATA
# ============================================================

def clean_measurements(df):
    df = df.copy()

    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"]
    )

    # Extract first numeric value from text.
    #
    # Examples:
    #
    # "98.0%"    -> 98.0
    # "120 mmHg" -> 120.0
    # "0.42"     -> 0.42
    numeric_text = (
        df["measurement_data"]
        .astype(str)
        .str.extract(
            r"(-?\d+(?:\.\d+)?)",
            expand=False,
        )
    )

    df["measurement_value"] = (
        pd.to_numeric(
            numeric_text,
            errors="coerce",
        )
    )

    # Keep only measurement types that make sense
    # for numerical rolling statistics.
    df = df[
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

    return df


# ============================================================
# ROLLING STATISTICS FOR ONE PATIENT + TYPE
# ============================================================

def calculate_group_rolling_statistics(
        group,
        measurement_type,
):
    group = (
        group
        .sort_values("recorded_at")
        .copy()
    )

    config = ROLLING_CONFIG[
        measurement_type
    ]

    window = config["window"]
    min_periods = config["min_periods"]

    # --------------------------------------------------------
    # IMPORTANT
    #
    # shift(1) means that the current measurement is NOT
    # included in the rolling baseline used to evaluate it.
    #
    # Example:
    #
    # previous 30 measurements
    #       ↓
    # rolling mean / std
    #       ↓
    # current value
    #
    # This avoids data leakage.
    # --------------------------------------------------------

    previous_values = (
        group["measurement_value"]
        .shift(1)
    )

    rolling = previous_values.rolling(
        window=window,
        min_periods=min_periods,
    )

    group["rolling_count"] = (
        rolling.count()
    )

    group["rolling_mean"] = (
        rolling.mean()
    )

    group["rolling_std"] = (
        rolling.std()
    )

    group["rolling_min"] = (
        rolling.min()
    )

    group["rolling_max"] = (
        rolling.max()
    )

    group["window_size"] = window

    return group


# ============================================================
# BUILD ROLLING STATISTICS TABLE
# ============================================================

def build_rolling_statistics(df):
    groups = []

    grouped = df.groupby(
        [
            "patient_id",
            "measurement_type",
        ]
    )

    for (
            _patient_id,
            measurement_type,
    ), group in grouped:

        processed_group = (
            calculate_group_rolling_statistics(
                group,
                measurement_type,
            )
        )

        groups.append(
            processed_group
        )

    if not groups:
        return pd.DataFrame(
            columns=[
                "measurement_id",
                "patient_id",
                "recorded_at",
                "measurement_type",
                "measurement_value",
                "rolling_count",
                "rolling_mean",
                "rolling_std",
                "rolling_min",
                "rolling_max",
                "window_size",
                "updated_at",
            ]
        )

    result = pd.concat(
        groups,
        ignore_index=True,
    )

    result = result.rename(
        columns={
            "id": "measurement_id"
        }
    )

    result["updated_at"] = (
        pd.Timestamp.now(
            tz="UTC"
        )
    )

    # rolling_count is conceptually an integer.
    result["rolling_count"] = (
        result["rolling_count"]
        .fillna(0)
        .astype(int)
    )

    columns = [
        "measurement_id",
        "patient_id",
        "recorded_at",
        "measurement_type",
        "measurement_value",
        "rolling_count",
        "rolling_mean",
        "rolling_std",
        "rolling_min",
        "rolling_max",
        "window_size",
        "updated_at",
    ]

    result = result[
        columns
    ]

    result = result.sort_values(
        [
            "patient_id",
            "measurement_type",
            "recorded_at",
        ]
    )

    return result


# ============================================================
# SAVE TO POSTGRESQL
# ============================================================

def save_rolling_statistics(
        rolling_df,
        engine,
):
    # Keep the table schema, but replace old calculated rows.
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE rolling_statistics"
            )
        )

    rolling_df.to_sql(
        "rolling_statistics",
        engine,
        if_exists="append",
        index=False,
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
        raw_df,
        rolling_df,
):
    available_baseline = rolling_df[
        "rolling_mean"
    ].notna()

    print()
    print(
        "Rolling statistics summary"
    )

    print(
        f"Raw numeric measurements: "
        f"{len(raw_df):,}"
    )

    print(
        f"Rows saved: "
        f"{len(rolling_df):,}"
    )

    print(
        f"Rows with rolling baseline: "
        f"{available_baseline.sum():,}"
    )

    print()

    print(
        "Rows by measurement type:"
    )

    if rolling_df.empty:
        print(
            "No rolling statistics generated."
        )
    else:
        print(
            rolling_df[
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
            "No measurements found. "
            "Rolling statistics stopped."
        )
        return

    print(
        "Cleaning numeric measurements..."
    )

    df = clean_measurements(
        df
    )

    print(
        f"Numeric measurements: "
        f"{len(df):,}"
    )

    if df.empty:
        print(
            "No numeric measurements found."
        )
        return

    print(
        "Calculating rolling statistics..."
    )

    rolling_df = (
        build_rolling_statistics(
            df
        )
    )

    print(
        "Saving rolling statistics "
        "to PostgreSQL..."
    )

    save_rolling_statistics(
        rolling_df,
        engine,
    )

    print_summary(
        df,
        rolling_df,
    )


if __name__ == "__main__":
    main()