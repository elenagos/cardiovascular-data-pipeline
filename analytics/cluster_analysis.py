from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)

OUTPUT_DIR = Path(
    "analytics/outputs"
)

CLUSTER_PROFILES_FILE = (
        OUTPUT_DIR / "cluster_profiles.csv"
)

FEATURE_IMPORTANCE_FILE = (
        OUTPUT_DIR / "cluster_feature_importance.csv"
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
# LOAD DATA
# ============================================================

def load_cluster_data(engine):
    query = """
    SELECT
        pc.patient_id,
        pc.cluster_id,
        pc.distance_to_centroid,

        pf.saturation_mean,
        pf.saturation_std,

        pf.systolicpressure_mean,
        pf.diastolicpressure_mean,

        pf.low_saturation_rate,
        pf.abnormal_systolic_rate,
        pf.abnormal_diastolic_rate,

        pf.zscore_anomaly_rate,
        pf.high_zscore_count,
        pf.max_abs_zscore

    FROM patient_clusters pc

    JOIN patient_features pf
        ON pc.patient_id = pf.patient_id

    ORDER BY
        pc.cluster_id,
        pc.patient_id
    """

    return pd.read_sql(
        query,
        engine
    )


# ============================================================
# CLUSTER SIZES
# ============================================================

def calculate_cluster_sizes(df):
    sizes = (
        df
        .groupby("cluster_id")
        .size()
        .reset_index(
            name="patient_count"
        )
    )

    return sizes


# ============================================================
# CLUSTER MEAN PROFILES
# ============================================================

def calculate_cluster_profiles(df):
    profiles = (
        df
        .groupby(
            "cluster_id"
        )[ML_FEATURES]
        .mean()
        .reset_index()
    )

    cluster_sizes = (
        calculate_cluster_sizes(df)
    )

    profiles = profiles.merge(
        cluster_sizes,
        on="cluster_id",
        how="left"
    )

    # Put patient_count near cluster_id.
    columns = [
        "cluster_id",
        "patient_count",
        *ML_FEATURES,
    ]

    return profiles[
        columns
    ]


# ============================================================
# FEATURE DIFFERENTIATION
# ============================================================

def calculate_feature_importance(df):
    """
    Estimate which features differentiate clusters most.

    We standardize every feature across all patients, then
    calculate the mean standardized value for each cluster.

    A feature receives a high differentiation score when
    cluster means are far apart from each other.
    """

    standardized = df[
        ML_FEATURES
    ].copy()


    # --------------------------------------------------------
    # STANDARDIZE
    # --------------------------------------------------------

    for feature in ML_FEATURES:

        mean_value = (
            standardized[
                feature
            ].mean()
        )

        std_value = (
            standardized[
                feature
            ].std()
        )


        if (
                pd.isna(std_value)
                or std_value == 0
        ):

            standardized[
                feature
            ] = 0.0

        else:

            standardized[
                feature
            ] = (
                    (
                            standardized[
                                feature
                            ]
                            - mean_value
                    )
                    / std_value
            )


    standardized[
        "cluster_id"
    ] = df[
        "cluster_id"
    ].values


    # --------------------------------------------------------
    # MEAN STANDARDIZED VALUE PER CLUSTER
    # --------------------------------------------------------

    cluster_means = (
        standardized
        .groupby(
            "cluster_id"
        )[ML_FEATURES]
        .mean()
    )


    # --------------------------------------------------------
    # DIFFERENTIATION SCORE
    #
    # largest cluster mean - smallest cluster mean
    # --------------------------------------------------------

    scores = []

    for feature in ML_FEATURES:

        feature_values = (
            cluster_means[
                feature
            ]
        )

        score = (
                feature_values.max()
                - feature_values.min()
        )

        scores.append(
            {
                "feature": feature,
                "differentiation_score": score,
            }
        )


    result = pd.DataFrame(
        scores
    )


    result = (
        result
        .sort_values(
            "differentiation_score",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    return result


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
        cluster_sizes,
        profiles,
        feature_importance
):
    print()
    print(
        "Cluster sizes:"
    )

    print(
        cluster_sizes.to_string(
            index=False
        )
    )


    print()
    print(
        "Cluster mean profiles:"
    )

    print(
        profiles
        .round(3)
        .to_string(
            index=False
        )
    )


    print()
    print(
        "Features that differentiate clusters most:"
    )

    print(
        feature_importance
        .head(10)
        .round(3)
        .to_string(
            index=False
        )
    )


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
        profiles,
        feature_importance
):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    profiles.to_csv(
        CLUSTER_PROFILES_FILE,
        index=False
    )


    feature_importance.to_csv(
        FEATURE_IMPORTANCE_FILE,
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
        "Loading cluster data..."
    )

    df = load_cluster_data(
        engine
    )


    if df.empty:

        print(
            "No cluster data found. "
            "Run clustering.py first."
        )

        return


    print(
        f"Loaded {len(df)} patients."
    )


    cluster_sizes = (
        calculate_cluster_sizes(
            df
        )
    )


    profiles = (
        calculate_cluster_profiles(
            df
        )
    )


    feature_importance = (
        calculate_feature_importance(
            df
        )
    )


    print_summary(
        cluster_sizes,
        profiles,
        feature_importance
    )


    save_outputs(
        profiles,
        feature_importance
    )


    print()
    print(
        f"Saved: {CLUSTER_PROFILES_FILE}"
    )

    print(
        f"Saved: {FEATURE_IMPORTANCE_FILE}"
    )


if __name__ == "__main__":
    main()