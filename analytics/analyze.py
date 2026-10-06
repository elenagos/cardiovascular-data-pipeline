import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://localhost/cardio_pipeline"
)

query = """
SELECT
    id,
    patient_id,
    recorded_at,
    measurement_type,
    measurement_data
FROM measurements
ORDER BY recorded_at
"""

df = pd.read_sql(query, engine)

print("Rows:", len(df))
print()

print("Measurement types:")
print(df["measurement_type"].value_counts())
print()

df["measurement_value"] = pd.to_numeric(
    df["measurement_data"],
    errors="coerce"
)

numeric_df = df.dropna(
    subset=["measurement_value"]
).copy()

summary = (
    numeric_df
    .groupby(
        ["patient_id", "measurement_type"]
    )["measurement_value"]
    .agg(
        count="count",
        mean="mean",
        min="min",
        max="max",
        std="std"
    )
    .reset_index()
)

print("Summary:")
print(summary)
print()

summary.to_csv(
    "analytics/measurement_summary.csv",
    index=False
)

print(
    "Saved analytics/measurement_summary.csv"
)

heart_rate = numeric_df[
    numeric_df["measurement_type"] == "HeartRate"
    ]

if not heart_rate.empty:
    print()
    print("Heart Rate Summary:")
    print(
        heart_rate.groupby("patient_id")[
            "measurement_value"
        ].agg(
            ["count", "mean", "min", "max", "std"]
        )
    )

saturation = numeric_df[
    numeric_df["measurement_type"] == "Saturation"
    ]

if not saturation.empty:
    print()
    print("Saturation Summary:")
    print(
        saturation.groupby("patient_id")[
            "measurement_value"
        ].agg(
            ["count", "mean", "min", "max", "std"]
        )
    )

ecg = numeric_df[
    numeric_df["measurement_type"] == "ECG"
    ]

if not ecg.empty:
    print()
    print("ECG Summary:")
    print(
        ecg.groupby("patient_id")[
            "measurement_value"
        ].agg(
            ["count", "mean", "min", "max", "std"]
        )
    )

heart_rate_anomalies = heart_rate[
    (heart_rate["measurement_value"] < 50) |
    (heart_rate["measurement_value"] > 120)
    ]

saturation_anomalies = saturation[
    saturation["measurement_value"] < 92
    ]

print()
print("Heart Rate Anomalies:")
print(
    heart_rate_anomalies[
        [
            "patient_id",
            "recorded_at",
            "measurement_value"
        ]
    ]
)

print()
print("Low Oxygen Saturation:")
print(
    saturation_anomalies[
        [
            "patient_id",
            "recorded_at",
            "measurement_value"
        ]
    ]
)
heart_rate_anomalies.to_csv(
    "analytics/heart_rate_anomalies.csv",
    index=False
)

saturation_anomalies.to_csv(
    "analytics/saturation_anomalies.csv",
    index=False
)
import matplotlib.pyplot as plt

for patient_id, patient_data in heart_rate.groupby("patient_id"):

    patient_data = patient_data.sort_values(
        "recorded_at"
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        patient_data["recorded_at"],
        patient_data["measurement_value"]
    )

    plt.title(
        f"Heart Rate Over Time - Patient {patient_id}"
    )

    plt.xlabel("Time")
    plt.ylabel("Heart Rate")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        f"analytics/plots/heart_rate_patient_{patient_id}.png"
    )

    plt.close()