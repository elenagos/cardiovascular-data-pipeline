import numpy as np
import pandas as pd

from analytics.pca_analysis import (
    ML_FEATURES,
    prepare_features,
    run_pca,
    standardize_features,
)


def create_patient_dataframe():
    return pd.DataFrame(
        {
            "patient_id": [1, 2, 3, 4, 5],

            "saturation_mean": [
                98.0,
                97.0,
                95.0,
                93.0,
                91.0,
            ],

            "saturation_std": [
                0.5,
                0.8,
                1.2,
                2.0,
                3.0,
            ],

            "systolicpressure_mean": [
                120.0,
                125.0,
                130.0,
                140.0,
                150.0,
            ],

            "diastolicpressure_mean": [
                75.0,
                78.0,
                82.0,
                88.0,
                95.0,
            ],

            "low_saturation_rate": [
                0.0,
                0.0,
                0.05,
                0.10,
                0.30,
            ],

            "abnormal_systolic_rate": [
                0.0,
                0.0,
                0.05,
                0.15,
                0.40,
            ],

            "abnormal_diastolic_rate": [
                0.0,
                0.0,
                0.05,
                0.10,
                0.35,
            ],

            "zscore_anomaly_rate": [
                0.01,
                0.02,
                0.03,
                0.08,
                0.20,
            ],

            "high_zscore_count": [
                0,
                0,
                1,
                2,
                5,
            ],

            "max_abs_zscore": [
                1.5,
                2.0,
                3.2,
                4.0,
                6.0,
            ],
        }
    )


def test_prepare_features_returns_expected_columns():
    df = create_patient_dataframe()

    result = prepare_features(df)

    assert list(result.columns) == ML_FEATURES
    assert len(result) == 5


def test_prepare_features_fills_missing_values():
    df = create_patient_dataframe()

    df.loc[
        0,
        "saturation_mean",
    ] = np.nan

    result = prepare_features(df)

    assert (
            result["saturation_mean"]
            .isna()
            .sum()
            == 0
    )


def test_standardized_features_have_zero_mean():
    df = create_patient_dataframe()

    X = prepare_features(df)

    X_scaled, _ = standardize_features(X)

    means = X_scaled.mean(axis=0)

    assert np.allclose(
        means,
        0,
        atol=1e-7,
    )


def test_pca_returns_two_components():
    df = create_patient_dataframe()

    X = prepare_features(df)

    X_scaled, _ = standardize_features(X)

    components, pca = run_pca(X_scaled)

    assert components.shape == (5, 2)

    assert len(
        pca.explained_variance_ratio_
    ) == 2


def test_pca_explained_variance_is_valid():
    df = create_patient_dataframe()

    X = prepare_features(df)

    X_scaled, _ = standardize_features(X)

    _, pca = run_pca(X_scaled)

    total_variance = (
        pca.explained_variance_ratio_
        .sum()
    )

    assert total_variance > 0
    assert total_variance <= 1