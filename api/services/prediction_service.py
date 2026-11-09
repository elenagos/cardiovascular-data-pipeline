import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


ARTIFACT_DIR = (
        PROJECT_ROOT
        / "artifacts"
        / "isolation_forest"
)


MODEL_PATH = (
        ARTIFACT_DIR
        / "model.joblib"
)


SCALER_PATH = (
        ARTIFACT_DIR
        / "scaler.joblib"
)


METADATA_PATH = (
        ARTIFACT_DIR
        / "metadata.json"
)


@lru_cache(maxsize=1)
def load_artifacts():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Isolation Forest model not found: {MODEL_PATH}"
        )

    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            f"Isolation Forest scaler not found: {SCALER_PATH}"
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Isolation Forest metadata not found: {METADATA_PATH}"
        )

    model = joblib.load(
        MODEL_PATH
    )

    scaler = joblib.load(
        SCALER_PATH
    )

    with METADATA_PATH.open(
            "r",
            encoding="utf-8",
    ) as file:
        metadata = json.load(
            file
        )

    return (
        model,
        scaler,
        metadata,
    )


def predict_anomaly(
        features: dict,
):
    (
        model,
        scaler,
        metadata,
    ) = load_artifacts()

    feature_names = (
        metadata[
            "features"
        ]
    )

    missing_features = [
        feature
        for feature in feature_names
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            "Missing prediction features: "
            + ", ".join(
                missing_features
            )
        )

    input_df = pd.DataFrame(
        [
            {
                feature:
                    features[
                        feature
                    ]
                for feature in feature_names
            }
        ],
        columns=feature_names,
    )

    X_scaled = (
        scaler.transform(
            input_df
        )
    )

    prediction = (
        model.predict(
            X_scaled
        )[0]
    )

    raw_score = (
        model.decision_function(
            X_scaled
        )[0]
    )

    anomaly_score = (
        -float(
            raw_score
        )
    )

    return {
        "is_outlier":
            bool(
                prediction == -1
            ),

        "anomaly_score":
            anomaly_score,
    }