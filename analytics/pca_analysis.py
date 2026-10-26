import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, text

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = (
    "postgresql+psycopg2://localhost/cardio_pipeline"
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
            "Missing PCA features: "
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
    # MEDIAN IMPUTATION
    # --------------------------------------------------------

    for column in X.columns:

        median_value = (
            X[
                column
            ]
            .median()
        )


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
# STANDARDIZE
# ============================================================

def standardize_features(X):

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
# PCA
# ============================================================

def run_pca(
        X_scaled,
):

    pca = PCA(
        n_components=2
    )


    components = (
        pca.fit_transform(
            X_scaled
        )
    )


    return (
        components,
        pca,
    )


# ============================================================
# BUILD RESULT
# ============================================================

def build_result(
        patient_df,
        components,
        pca,
):

    explained_variance = (
        pca.explained_variance_ratio_
    )


    result = pd.DataFrame(
        {
            "patient_id":
                patient_df[
                    "patient_id"
                ]
                .astype(int)
                .values,

            "pc1":
                components[
                :, 0
                ],

            "pc2":
                components[
                :, 1
                ],

            "explained_variance_pc1":
                explained_variance[0],

            "explained_variance_pc2":
                explained_variance[1],

            "updated_at":
                pd.Timestamp.now(
                    tz="UTC"
                ),
        }
    )


    return result


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
        result,
        pca,
):

    pc1_variance = (
        pca.explained_variance_ratio_[
            0
        ]
    )

    pc2_variance = (
        pca.explained_variance_ratio_[
            1
        ]
    )

    total_variance = (
            pc1_variance
            + pc2_variance
    )


    print()

    print(
        "PCA summary"
    )

    print(
        f"Patients: "
        f"{len(result)}"
    )

    print(
        f"PC1 explained variance: "
        f"{pc1_variance:.2%}"
    )

    print(
        f"PC2 explained variance: "
        f"{pc2_variance:.2%}"
    )

    print(
        f"PC1 + PC2 explained variance: "
        f"{total_variance:.2%}"
    )


    print()

    print(
        "PCA coordinates:"
    )


    print(
        result[
            [
                "patient_id",
                "pc1",
                "pc2",
            ]
        ]
        .round(3)
        .to_string(
            index=False
        )
    )


# ============================================================
# PRINT COMPONENT LOADINGS
# ============================================================

def print_loadings(
        pca,
):

    loadings = pd.DataFrame(
        pca.components_.T,

        index=
        ML_FEATURES,

        columns=[
            "PC1",
            "PC2",
        ],
    )


    print()

    print(
        "PCA feature loadings:"
    )


    print(
        loadings
        .round(3)
        .to_string()
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
                "TRUNCATE TABLE patient_pca"
            )
        )


    result.to_sql(
        "patient_pca",
        engine,
        if_exists="append",
        index=False,
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


    if patient_df.empty:

        print(
            "No patient features found. "
            "Run feature_engineering.py first."
        )

        return


    if len(
            patient_df
    ) < 3:

        print(
            "Too few patients for PCA."
        )

        return


    print(
        f"Loaded "
        f"{len(patient_df)} patients."
    )


    print(
        "Preparing PCA features..."
    )


    X = (
        prepare_features(
            patient_df
        )
    )


    print(
        "Standardizing features..."
    )


    (
        X_scaled,
        scaler,
    ) = (
        standardize_features(
            X
        )
    )


    print(
        "Running PCA..."
    )


    (
        components,
        pca,
    ) = (
        run_pca(
            X_scaled
        )
    )


    result = (
        build_result(
            patient_df,
            components,
            pca,
        )
    )


    print_summary(
        result,
        pca,
    )


    print_loadings(
        pca
    )


    print()

    print(
        "Saving PCA coordinates "
        "to PostgreSQL..."
    )


    save_results(
        result,
        engine,
    )


    print(
        f"Saved "
        f"{len(result)} "
        f"PCA rows."
    )


if __name__ == "__main__":
    main()