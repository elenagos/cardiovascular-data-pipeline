import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

REGISTERED_MODEL_NAME = (
    "CardioPulseIsolationForest"
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://localhost/cardio_pipeline",
)


MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5001",
)


MLFLOW_EXPERIMENT_NAME = (
    "cardiopulse-isolation-forest"
)


# Expected approximate fraction of unusual patients.
#
# This is a demo / analytical assumption,
# not a medical threshold.
CONTAMINATION = 0.10


N_ESTIMATORS = 300


RANDOM_STATE = 42


ARTIFACT_DIR = (
        Path(__file__).resolve().parent.parent
        / "artifacts"
        / "isolation_forest"
)


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
# MLFLOW
# ============================================================

def configure_mlflow():
    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )

    mlflow.set_experiment(
        MLFLOW_EXPERIMENT_NAME
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
        engine,
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
        scaler,
    )


# ============================================================
# TRAIN ISOLATION FOREST
# ============================================================

def train_isolation_forest(
        X_scaled,
):
    model = (
        IsolationForest(
            n_estimators=N_ESTIMATORS,
            contamination=CONTAMINATION,
            random_state=RANDOM_STATE,
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
        raw_scores,
    )


# ============================================================
# BUILD RESULTS
# ============================================================

def build_results(
        patient_df,
        predictions,
        raw_scores,
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
            ascending=False,
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
        result,
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
        engine,
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
        index=False,
    )


# ============================================================
# SAVE MODEL ARTIFACTS
# ============================================================

def save_model_artifacts(
        model,
        scaler,
        patient_count,
):
    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
            ARTIFACT_DIR
            / "model.joblib"
    )

    scaler_path = (
            ARTIFACT_DIR
            / "scaler.joblib"
    )

    metadata_path = (
            ARTIFACT_DIR
            / "metadata.json"
    )

    joblib.dump(
        model,
        model_path,
    )

    joblib.dump(
        scaler,
        scaler_path,
    )

    metadata = {
        "model_type":
            "IsolationForest",

        "features":
            ML_FEATURES,

        "contamination":
            CONTAMINATION,

        "random_state":
            RANDOM_STATE,

        "n_estimators":
            N_ESTIMATORS,

        "patient_count":
            patient_count,

        "registered_model_name":
            REGISTERED_MODEL_NAME,

        "trained_at":
            pd.Timestamp.now(
                tz="UTC"
            ).isoformat(),
    }

    with metadata_path.open(
            "w",
            encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )

    print(
        "Saved model artifacts:"
    )

    print(
        f" - {model_path}"
    )

    print(
        f" - {scaler_path}"
    )

    print(
        f" - {metadata_path}"
    )


# ============================================================
# MLFLOW PARAMETERS
# ============================================================

def log_mlflow_parameters(
        patient_count,
):
    mlflow.log_param(
        "model_type",
        "IsolationForest",
    )

    mlflow.log_param(
        "contamination",
        CONTAMINATION,
    )

    mlflow.log_param(
        "n_estimators",
        N_ESTIMATORS,
    )

    mlflow.log_param(
        "random_state",
        RANDOM_STATE,
    )

    mlflow.log_param(
        "patient_count",
        patient_count,
    )

    mlflow.log_param(
        "feature_count",
        len(
            ML_FEATURES
        ),
    )

    mlflow.log_param(
        "features",
        ",".join(
            ML_FEATURES
        ),
    )


# ============================================================
# MLFLOW METRICS
# ============================================================

def log_mlflow_metrics(
        result,
):
    patient_count = len(
        result
    )

    outlier_count = int(
        result[
            "is_outlier"
        ]
        .sum()
    )

    outlier_rate = (
        outlier_count
        / patient_count
        if patient_count > 0
        else 0.0
    )

    mean_anomaly_score = float(
        result[
            "anomaly_score"
        ]
        .mean()
    )

    max_anomaly_score = float(
        result[
            "anomaly_score"
        ]
        .max()
    )

    mlflow.log_metric(
        "outlier_count",
        outlier_count,
    )

    mlflow.log_metric(
        "outlier_rate",
        outlier_rate,
    )

    mlflow.log_metric(
        "mean_anomaly_score",
        mean_anomaly_score,
    )

    mlflow.log_metric(
        "max_anomaly_score",
        max_anomaly_score,
    )


# ============================================================
# MLFLOW ARTIFACTS
# ============================================================

def log_mlflow_artifacts():
    mlflow.log_artifacts(
        str(
            ARTIFACT_DIR
        ),
        artifact_path="isolation_forest",
    )


# ============================================================
# MLFLOW MODEL REGISTRY
# ============================================================

def register_mlflow_model(
        model,
        X,
):
    input_example = (
        X
        .head(1)
        .copy()
    )

    model_info = (
        mlflow.sklearn.log_model(
            sk_model=model,
            name="isolation_forest_model",
            registered_model_name=REGISTERED_MODEL_NAME,
            input_example=input_example,
            skops_trusted_types=[
                "sklearn.tree._tree.Tree",
            ],
        )
    )

    client = MlflowClient()

    versions = (
        client.search_model_versions(
            f"name='{REGISTERED_MODEL_NAME}'"
        )
    )

    latest_version = max(
        versions,
        key=lambda version: int(
            version.version
        ),
    )

    client.set_registered_model_alias(
        name=REGISTERED_MODEL_NAME,
        alias="champion",
        version=latest_version.version,
    )

    print()

    print(
        "Registered model in MLflow:"
    )

    print(
        f" - name: "
        f"{REGISTERED_MODEL_NAME}"
    )

    print(
        f" - version: "
        f"{latest_version.version}"
    )

    print(
        " - alias: champion"
    )

    print(
        f" - model URI: "
        f"{model_info.model_uri}"
    )

    return model_info


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
        "Configuring MLflow..."
    )

    configure_mlflow()

    print(
        f"MLflow tracking URI: "
        f"{MLFLOW_TRACKING_URI}"
    )

    print(
        f"MLflow experiment: "
        f"{MLFLOW_EXPERIMENT_NAME}"
    )

    with mlflow.start_run(
            run_name="isolation-forest-training"
    ) as run:
        print()

        print(
            f"MLflow run ID: "
            f"{run.info.run_id}"
        )

        log_mlflow_parameters(
            patient_count=len(
                patient_df
            )
        )

        print()

        print(
            "Training Isolation Forest..."
        )

        (
            model,
            predictions,
            raw_scores,
        ) = (
            train_isolation_forest(
                X_scaled
            )
        )

        result = (
            build_results(
                patient_df,
                predictions,
                raw_scores,
            )
        )

        print_summary(
            result
        )

        log_mlflow_metrics(
            result
        )

        print()

        print(
            "Saving results "
            "to PostgreSQL..."
        )

        save_results(
            result,
            engine,
        )

        print(
            f"Saved "
            f"{len(result)} "
            f"patient anomaly results."
        )

        print()

        print(
            "Saving model artifacts..."
        )

        save_model_artifacts(
            model=model,
            scaler=scaler,
            patient_count=len(
                patient_df
            ),
        )

        print()

        print(
            "Logging artifacts "
            "to MLflow..."
        )

        log_mlflow_artifacts()

        print()

        print(
            "Registering model "
            "in MLflow Model Registry..."
        )

        register_mlflow_model(
            model=model,
            X=X,
        )

        print()

        print(
            "MLflow run completed."
        )

        print(
            f"Run ID: "
            f"{run.info.run_id}"
        )


if __name__ == "__main__":
    main()