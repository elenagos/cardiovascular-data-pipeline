import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
)


N_CLUSTERS = 3


# Features intentionally chosen to represent
# different aspects of patient behaviour.
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
# PREPARE ML DATA
# ============================================================

def prepare_features(df):
    available_features = [
        column
        for column in ML_FEATURES
        if column in df.columns
    ]

    if len(available_features) != len(
            ML_FEATURES
    ):
        missing = set(
            ML_FEATURES
        ) - set(
            available_features
        )

        raise ValueError(
            "Missing ML features: "
            + ", ".join(
                sorted(missing)
            )
        )

    X = (
        df[
            ML_FEATURES
        ]
        .copy()
    )

    # Replace missing values with median.
    #
    # Median is safer than blindly using zero
    # for physiological measurements.
    for column in X.columns:
        X[column] = (
            X[column]
            .fillna(
                X[column].median()
            )
        )

    return X


# ============================================================
# STANDARDIZE FEATURES
# ============================================================

def scale_features(X):
    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X
    )

    return (
        X_scaled,
        scaler
    )


# ============================================================
# KMEANS
# ============================================================

def train_kmeans(X_scaled):
    model = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=42,
        n_init=20
    )

    cluster_labels = (
        model.fit_predict(
            X_scaled
        )
    )

    return (
        model,
        cluster_labels
    )


# ============================================================
# BUILD RESULT
# ============================================================

def build_cluster_results(
        df,
        X_scaled,
        model,
        cluster_labels
):
    result = pd.DataFrame(
        {
            "patient_id": (
                df[
                    "patient_id"
                ]
                .astype(int)
                .values
            ),

            "cluster_id": (
                cluster_labels
                .astype(int)
            ),
        }
    )

    # Distance from each patient to the center
    # of the cluster assigned by KMeans.
    distances = (
        model.transform(
            X_scaled
        )
    )

    result[
        "distance_to_centroid"
    ] = [
        distances[
            row_index,
            cluster_id
        ]
        for row_index, cluster_id
        in enumerate(
            cluster_labels
        )
    ]

    result[
        "updated_at"
    ] = (
        pd.Timestamp.now(
            tz="UTC"
        )
    )

    return result


# ============================================================
# CLUSTER PROFILE
# ============================================================

def print_cluster_profiles(
        patient_df,
        cluster_results
):
    combined = (
        patient_df.merge(
            cluster_results[
                [
                    "patient_id",
                    "cluster_id",
                ]
            ],
            on="patient_id",
            how="inner"
        )
    )

    print()
    print(
        "Cluster sizes:"
    )

    print(
        combined[
            "cluster_id"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print()
    print(
        "Cluster feature profiles:"
    )

    profiles = (
        combined
        .groupby(
            "cluster_id"
        )[ML_FEATURES]
        .mean()
        .round(3)
    )

    print(
        profiles.to_string()
    )


# ============================================================
# MODEL QUALITY
# ============================================================

def evaluate_clustering(
        X_scaled,
        cluster_labels
):
    unique_clusters = len(
        set(cluster_labels)
    )

    if (
            unique_clusters > 1
            and len(X_scaled) > unique_clusters
    ):
        score = silhouette_score(
            X_scaled,
            cluster_labels
        )

        print()
        print(
            f"Silhouette score: "
            f"{score:.3f}"
        )

        return score

    print()
    print(
        "Silhouette score cannot "
        "be calculated."
    )

    return None


# ============================================================
# SAVE TO DATABASE
# ============================================================

def save_clusters(
        result,
        engine
):
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE patient_clusters"
            )
        )

    result.to_sql(
        "patient_clusters",
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

    engine = create_db_engine()


    print(
        "Loading patient features..."
    )

    patient_df = (
        load_patient_features(
            engine
        )
    )

    print(
        f"Loaded {len(patient_df)} patients."
    )


    if len(patient_df) < N_CLUSTERS:
        print(
            "Not enough patients "
            "for clustering."
        )
        return


    print(
        "Preparing ML features..."
    )

    X = prepare_features(
        patient_df
    )


    print()
    print(
        "Features used for clustering:"
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
        "Training KMeans..."
    )

    model, cluster_labels = (
        train_kmeans(
            X_scaled
        )
    )


    cluster_results = (
        build_cluster_results(
            patient_df,
            X_scaled,
            model,
            cluster_labels
        )
    )


    evaluate_clustering(
        X_scaled,
        cluster_labels
    )


    print_cluster_profiles(
        patient_df,
        cluster_results
    )


    print()
    print(
        "Patient assignments:"
    )

    print(
        cluster_results[
            [
                "patient_id",
                "cluster_id",
                "distance_to_centroid",
            ]
        ]
        .sort_values(
            [
                "cluster_id",
                "patient_id",
            ]
        )
        .to_string(
            index=False
        )
    )


    print()
    print(
        "Saving clusters "
        "to PostgreSQL..."
    )

    save_clusters(
        cluster_results,
        engine
    )


    print(
        f"Saved {len(cluster_results)} "
        f"patient cluster assignments."
    )


if __name__ == "__main__":
    main()