import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)


# Expected approximate fraction of unusual patients.
#
# This is a demo / analytical assumption,
# not a medical threshold.
CONTAMINATION = 0.10


RANDOM_STATE = 42


ML_FEATURES = [
    "saturation_mean",
    "saturation_std",

    "systolicpressure_mean",
    "diastolicpressure_mean",

    "low_saturation_rate",
    "abnormal_systolic_rate",
    "abnormal_diastolic_rate",

    "zscore_anomaly_rate",
    "high_zscore_count",
    "max_abs_zscore",
]


# ============================================================
# DATABASE
# ============================================================

def create_db_engine():
    return create_engine(
        DATABASE_URL
    )


# ============================================================
# LOAD PATIENT FEATURES
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
# PREPARE FEATURES
# ============================================================

def prepare_features(df):
    missing_features = [
        feature
        for feature in ML_FEATURES
        if feature not in df.columns
    ]


    if missing_features:
        raise ValueError(
            "Missing ML features: "
            + ", ".join(
                missing_features
            )
        )


    X = (
        df[
            ML_FEATURES
        ]
        .copy()
    )


    # --------------------------------------------------------
    # HANDLE MISSING VALUES
    # --------------------------------------------------------

    for column in X.columns:

        median_value = (
            X[
                column
            ]
            .median()
        )


        # If the whole feature is NaN,
        # median will also be NaN.
        if pd.isna(
                median_value
        ):

            median_value = 0.0


        X[
            column
        ] = (
            X[
                column
            ]
            .fillna(
                median_value
            )
        )


    return X


# ============================================================
# STANDARDIZATION
# ============================================================

def scale_features(X):
    scaler = (
        StandardScaler()
    )


    X_scaled = (
        scaler.fit_transform(
            X
        )
    )


    return (
        X_scaled,
        scaler
    )


# ============================================================
# TRAIN ISOLATION FOREST
# ============================================================

def train_isolation_forest(
        X_scaled
):
    model = (
        IsolationForest(
            n_estimators=300,

            contamination=
            CONTAMINATION,

            random_state=
            RANDOM_STATE,
        )
    )


    predictions = (
        model.fit_predict(
            X_scaled
        )
    )


    raw_scores = (
        model.decision_function(
            X_scaled
        )
    )


    return (
        model,
        predictions,
        raw_scores
    )


# ============================================================
# BUILD RESULTS
# ============================================================

def build_results(
        patient_df,
        predictions,
        raw_scores
):
    result = pd.DataFrame(
        {
            "patient_id":
                patient_df[
                    "patient_id"
                ]
                .astype(int)
                .values,

            # Convert score direction:
            #
            # larger score =
            # more anomalous patient
            "anomaly_score":
                -raw_scores,

            # IsolationForest returns:
            #
            #  1 = normal
            # -1 = outlier
            "is_outlier":
                predictions == -1,
        }
    )


    # --------------------------------------------------------
    # OUTLIER RANK
    # --------------------------------------------------------
    #
    # Rank 1 = most anomalous patient.

    result[
        "outlier_rank"
    ] = (
        result[
            "anomaly_score"
        ]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )


    result[
        "updated_at"
    ] = (
        pd.Timestamp.now(
            tz="UTC"
        )
    )


    return result


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
        result
):
    outliers = (
        result[
            result[
                "is_outlier"
            ]
        ]
        .copy()
    )


    print()

    print(
        "Isolation Forest summary"
    )


    print(
        f"Total patients: "
        f"{len(result)}"
    )


    print(
        f"Detected outliers: "
        f"{len(outliers)}"
    )


    if len(result) > 0:

        outlier_rate = (
                len(outliers)
                / len(result)
        )


        print(
            f"Outlier rate: "
            f"{outlier_rate:.2%}"
        )


    print()

    print(
        "Most unusual patients:"
    )


    print(
        result[
            [
                "patient_id",
                "anomaly_score",
                "is_outlier",
                "outlier_rank",
            ]
        ]
        .sort_values(
            "outlier_rank"
        )
        .head(10)
        .round(
            {
                "anomaly_score": 4
            }
        )
        .to_string(
            index=False
        )
    )


# ============================================================
# SAVE DATABASE
# ============================================================

def save_results(
        result,
        engine
):
    with engine.begin() as connection:

        connection.execute(
            text(
                "TRUNCATE TABLE "
                "patient_anomalies"
            )
        )


    result.to_sql(
        "patient_anomalies",
        engine,
        if_exists="append",
        index=False
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Connecting to PostgreSQL..."
    )


    engine = (
        create_db_engine()
    )


    print(
        "Loading patient features..."
    )


    patient_df = (
        load_patient_features(
            engine
        )
    )


    print(
        f"Loaded "
        f"{len(patient_df)} patients."
    )


    if patient_df.empty:

        print(
            "No patient features found. "
            "Run feature_engineering.py first."
        )

        return


    if len(
            patient_df
    ) < 5:

        print(
            "Too few patients "
            "for meaningful Isolation Forest analysis."
        )

        return


    print(
        "Preparing ML features..."
    )


    X = (
        prepare_features(
            patient_df
        )
    )


    print()

    print(
        "Features used:"
    )


    for feature in ML_FEATURES:

        print(
            f" - {feature}"
        )


    print(
        "\nStandardizing features..."
    )


    X_scaled, scaler = (
        scale_features(
            X
        )
    )


    print(
        "Training Isolation Forest..."
    )


    (
        model,
        predictions,
        raw_scores
    ) = (
        train_isolation_forest(
            X_scaled
        )
    )


    result = (
        build_results(
            patient_df,
            predictions,
            raw_scores
        )
    )


    print_summary(
        result
    )


    print()

    print(
        "Saving results "
        "to PostgreSQL..."
    )


    save_results(
        result,
        engine
    )


    print(
        f"Saved "
        f"{len(result)} "
        f"patient anomaly results."
    )


if __name__ == "__main__":
    main()