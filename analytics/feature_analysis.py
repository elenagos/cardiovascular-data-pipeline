from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)

OUTPUT_DIR = Path(
    "analytics/outputs/feature_analysis"
)


# ============================================================
# DATABASE
# ============================================================

def create_db_engine():
    return create_engine(
        DATABASE_URL
    )


# ============================================================
# LOAD FEATURES
# ============================================================

def load_patient_features(engine):
    query = """
    SELECT *
    FROM patient_features
    ORDER BY patient_id
    """

    return pd.read_sql(
        query,
        engine
    )


# ============================================================
# SUMMARY STATISTICS
# ============================================================

def print_summary(df):
    print()
    print("Feature summary:")
    print()

    numeric_df = df.select_dtypes(
        include="number"
    )

    print(
        numeric_df
        .describe()
        .T
        .to_string()
    )


# ============================================================
# FEATURE DISTRIBUTIONS
# ============================================================

def plot_distributions(df):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    selected_features = [
        "saturation_mean",
        "systolicpressure_mean",
        "diastolicpressure_mean",
        "zscore_anomaly_rate",
        "high_zscore_count",
        "max_abs_zscore",
        "data_completeness",
    ]

    for feature in selected_features:
        if feature not in df.columns:
            continue

        values = (
            df[feature]
            .dropna()
        )

        if values.empty:
            continue

        plt.figure()

        plt.hist(
            values,
            bins=10
        )

        plt.title(
            f"Distribution of {feature}"
        )

        plt.xlabel(
            feature
        )

        plt.ylabel(
            "Number of patients"
        )

        plt.tight_layout()

        output_file = (
                OUTPUT_DIR
                / f"{feature}_distribution.png"
        )

        plt.savefig(
            output_file
        )

        plt.close()


# ============================================================
# CORRELATION MATRIX
# ============================================================

def create_correlation_matrix(df):
    numeric_df = (
        df
        .select_dtypes(
            include="number"
        )
        .drop(
            columns=["patient_id"],
            errors="ignore"
        )
    )

    correlation = (
        numeric_df.corr()
    )

    output_file = (
            OUTPUT_DIR
            / "correlation_matrix.csv"
    )

    correlation.to_csv(
        output_file
    )

    print()
    print(
        f"Correlation matrix saved to: "
        f"{output_file}"
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
        "Loading patient features..."
    )

    df = load_patient_features(
        engine
    )

    print(
        f"Loaded {len(df)} patients."
    )

    if df.empty:
        print(
            "No patient features found."
        )
        return

    print_summary(
        df
    )

    print(
        "Creating feature distributions..."
    )

    plot_distributions(
        df
    )

    print(
        "Creating correlation matrix..."
    )

    create_correlation_matrix(
        df
    )

    print()
    print(
        "Feature analysis completed."
    )


if __name__ == "__main__":
    main()