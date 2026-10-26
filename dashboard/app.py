import html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cardiovascular patient monitoring",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st_autorefresh(
    interval=5000,
    key="cardio_dashboard_refresh",
)


# ============================================================
# CSS / DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            linear-gradient(
                135deg,
                #071426 0%,
                #0B1F36 55%,
                #0D2847 100%
            );
        color: #EAF4FF;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3, h4 {
        color: #F2F8FF !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-weight: 750 !important;
    }


    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #061321 0%,
                #0A2038 100%
            );

        border-right:
            1px solid rgba(98, 181, 255, 0.15);
    }

    [data-testid="stSidebar"] * {
        color: #DCEEFF;
    }


    /* SELECTBOX */

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
    }

    div[data-baseweb="select"] span {
        color: #0B1F36 !important;
        font-weight: 650 !important;
    }

    div[data-baseweb="select"] input {
        color: #0B1F36 !important;
        -webkit-text-fill-color: #0B1F36 !important;
    }

    div[data-baseweb="select"] svg {
        fill: #0B1F36 !important;
        color: #0B1F36 !important;
    }

    ul[role="listbox"] {
        background-color: #FFFFFF !important;
    }

    ul[role="listbox"] li {
        color: #0B1F36 !important;
        background-color: #FFFFFF !important;
        font-weight: 550 !important;
    }

    ul[role="listbox"] li span {
        color: #0B1F36 !important;
    }

    ul[role="listbox"] li:hover {
        background-color: #DFF2FF !important;
        color: #0B1F36 !important;
    }

    li[aria-selected="true"] {
        background-color: #CBEAFF !important;
        color: #0B1F36 !important;
    }


    /* KPI CARDS */

    [data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(18, 48, 78, 0.97),
                rgba(11, 36, 63, 0.97)
            );

        border:
            1px solid rgba(101, 190, 255, 0.20);

        padding: 22px;
        border-radius: 18px;

        box-shadow:
            0 10px 35px rgba(0, 0, 0, 0.22);
    }

    [data-testid="stMetricLabel"] {
        color: #96CFFF !important;
        font-size: 0.9rem;
        font-weight: 550;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2rem;
        font-weight: 720;
    }

    [data-testid="stMetricDelta"] {
        color: #72D2FF !important;
    }


    /* TABS */

    button[data-baseweb="tab"] {
        color: #9CCFFF;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF;
        border-bottom-color: #46B5FF;
    }


    /* LIVE BADGE */

    .live-badge {
        display: inline-block;

        padding: 7px 13px;
        border-radius: 999px;

        background:
            rgba(35, 181, 255, 0.14);

        border:
            1px solid rgba(66, 190, 255, 0.32);

        color: #69CEFF;

        font-weight: 700;
        font-size: 0.85rem;
    }

    .section-description {
        color: #86A9C7;
        margin-top: -8px;
        margin-bottom: 20px;
    }


    /* ALERT CENTER */

    .alert-card {
        width: 100%;
        box-sizing: border-box;

        padding: 20px 21px;
        margin-bottom: 18px;

        border-radius: 18px;

        border:
            1px solid rgba(255, 255, 255, 0.16);

        box-shadow:
            0 10px 28px rgba(0, 0, 0, 0.22);
    }

    .alert-high {
        background:
            linear-gradient(
                135deg,
                #F97316 0%,
                #C2410C 100%
            );
    }

    .alert-medium {
        background:
            linear-gradient(
                135deg,
                #F59E0B 0%,
                #C66A05 100%
            );
    }

    .alert-low {
        background:
            linear-gradient(
                135deg,
                #FBBF24 0%,
                #D97706 100%
            );
    }

    .alert-unclassified {
        background:
            linear-gradient(
                135deg,
                #E58B0B 0%,
                #A95105 100%
            );
    }

    .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 13px;
    }

    .alert-title {
        color: #FFFFFF;
        font-size: 1.08rem;
        font-weight: 760;
        line-height: 1.25;
    }

    .risk-badge {
        display: inline-block;

        background:
            rgba(7, 20, 38, 0.28);

        color: #FFFFFF;

        padding: 5px 9px;
        border-radius: 999px;

        font-size: 0.70rem;
        font-weight: 750;

        white-space: nowrap;
    }

    .alert-value {
        color: #FFFFFF;
        font-size: 1.65rem;
        font-weight: 780;
        margin-bottom: 13px;
    }

    .alert-row {
        color: #FFF8EE;
        font-size: 0.88rem;
        line-height: 1.48;
        margin-top: 9px;
    }

    .alert-label {
        color:
            rgba(255, 255, 255, 0.72);

        font-size: 0.73rem;
        font-weight: 750;

        letter-spacing: 0.05em;
        text-transform: uppercase;

        margin-bottom: 2px;
    }

    .alert-time {
        color:
            rgba(255, 255, 255, 0.70);

        font-size: 0.72rem;

        margin-top: 14px;
        padding-top: 11px;

        border-top:
            1px solid rgba(255, 255, 255, 0.17);
    }


    /* RISK SUMMARY */

    .risk-summary {
        border-radius: 14px;
        padding: 13px 16px;

        background:
            rgba(19, 54, 86, 0.78);

        border:
            1px solid rgba(103, 195, 255, 0.17);

        margin-bottom: 16px;
    }

    .risk-summary-title {
        color: #8FD3FF;

        font-size: 0.75rem;
        text-transform: uppercase;

        letter-spacing: 0.05em;

        margin-bottom: 4px;
    }

    .risk-summary-value {
        color: #FFFFFF;
        font-size: 1.25rem;
        font-weight: 750;
    }


    /* TABLES */

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }


    /* PROGRESS */

    [data-testid="stProgress"] > div {
        background-color: #FFFFFF !important;

        border:
            1px solid rgba(71, 183, 255, 0.25);

        border-radius: 999px !important;

        overflow: hidden;
        height: 12px;
    }

    [data-testid="stProgress"] > div > div {
        background-color: #47B7FF !important;
        border-radius: 999px !important;
    }


    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

engine = create_engine(
    "postgresql+psycopg2://localhost/cardio_pipeline"
)


# ------------------------------------------------------------
# RAW MEASUREMENTS
# ------------------------------------------------------------

measurements_query = """
SELECT
    id,
    patient_id,
    recorded_at,
    measurement_type,
    measurement_data
FROM measurements
ORDER BY recorded_at
"""

df = pd.read_sql(
    measurements_query,
    engine,
)


# ------------------------------------------------------------
# PATIENT FEATURES
# ------------------------------------------------------------

patient_features_query = """
SELECT
    patient_id,
    zscore_anomaly_count,
    zscore_anomaly_rate,
    high_zscore_count,
    max_abs_zscore
FROM patient_features
ORDER BY patient_id
"""

patient_features_df = pd.read_sql(
    patient_features_query,
    engine,
)


# ------------------------------------------------------------
# Z-SCORE ANOMALIES
# ------------------------------------------------------------

zscore_anomalies_query = """
SELECT
    patient_id,
    recorded_at,
    measurement_type,
    measurement_value,
    rolling_mean,
    rolling_std,
    z_score,
    anomaly_level
FROM zscore_analysis
WHERE is_anomaly = TRUE
ORDER BY recorded_at DESC
"""

zscore_anomalies_df = pd.read_sql(
    zscore_anomalies_query,
    engine,
)


# ------------------------------------------------------------
# PATIENT CLUSTERS
# ------------------------------------------------------------

patient_clusters_query = """
SELECT
    patient_id,
    cluster_id,
    distance_to_centroid
FROM patient_clusters
ORDER BY patient_id
"""

patient_clusters_df = pd.read_sql(
    patient_clusters_query,
    engine,
)


# ------------------------------------------------------------
# ISOLATION FOREST RESULTS
# ------------------------------------------------------------

patient_anomalies_query = """
SELECT
    patient_id,
    anomaly_score,
    is_outlier,
    outlier_rank
FROM patient_anomalies
ORDER BY patient_id
"""

patient_anomalies_df = pd.read_sql(
    patient_anomalies_query,
    engine,
)


# ------------------------------------------------------------
# PCA VISUALIZATION DATA
# ------------------------------------------------------------

pca_query = """
SELECT
    pca.patient_id,
    pca.pc1,
    pca.pc2,
    pca.explained_variance_pc1,
    pca.explained_variance_pc2,

    pc.cluster_id,
    pc.distance_to_centroid,

    pa.anomaly_score,
    pa.is_outlier,
    pa.outlier_rank,

    pf.zscore_anomaly_rate,
    pf.max_abs_zscore

FROM patient_pca pca

LEFT JOIN patient_clusters pc
    ON pca.patient_id = pc.patient_id

LEFT JOIN patient_anomalies pa
    ON pca.patient_id = pa.patient_id

LEFT JOIN patient_features pf
    ON pca.patient_id = pf.patient_id

ORDER BY pca.patient_id
"""

pca_df = pd.read_sql(
    pca_query,
    engine,
)


# ------------------------------------------------------------
# FEATURES FOR CLUSTER COMPARISON
# ------------------------------------------------------------

cluster_features_query = """
SELECT
    pc.patient_id,
    pc.cluster_id,

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

cluster_features_df = pd.read_sql(
    cluster_features_query,
    engine,
)


# ============================================================
# DATA CLEANING
# ============================================================

if df.empty:
    st.warning(
        "No measurements available."
    )
    st.stop()


numeric_text = (
    df["measurement_data"]
    .astype(str)
    .str.extract(
        r"(-?\d+(?:\.\d+)?)",
        expand=False,
    )
)

df["measurement_value"] = pd.to_numeric(
    numeric_text,
    errors="coerce",
)

df["recorded_at"] = pd.to_datetime(
    df["recorded_at"]
)


if not zscore_anomalies_df.empty:
    zscore_anomalies_df["recorded_at"] = (
        pd.to_datetime(
            zscore_anomalies_df[
                "recorded_at"
            ]
        )
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Sidebar"
)

patients = sorted(
    df["patient_id"].unique()
)

selected_patient = st.sidebar.selectbox(
    "Patient ID",
    patients,
)

st.sidebar.divider()

st.sidebar.markdown(
    "### Data source"
)

st.sidebar.markdown(
    "PostgreSQL"
)

st.sidebar.markdown(
    "### Refresh"
)

st.sidebar.markdown(
    "Every 5 seconds"
)


# ============================================================
# SELECTED PATIENT DATA
# ============================================================

patient_df = (
    df[
        df["patient_id"]
        == selected_patient
        ]
    .copy()
    .sort_values(
        "recorded_at"
    )
)


selected_features = (
    patient_features_df[
        patient_features_df[
            "patient_id"
        ] == selected_patient
        ]
    .copy()
)


selected_zscore_anomalies = (
    zscore_anomalies_df[
        zscore_anomalies_df[
            "patient_id"
        ] == selected_patient
        ]
    .copy()
    .sort_values(
        "recorded_at",
        ascending=False,
    )
)


# ------------------------------------------------------------
# SELECTED PATIENT CLUSTER
# ------------------------------------------------------------

selected_cluster = (
    patient_clusters_df[
        patient_clusters_df[
            "patient_id"
        ] == selected_patient
        ]
    .copy()
)


selected_cluster_features = (
    cluster_features_df[
        cluster_features_df[
            "patient_id"
        ] == selected_patient
        ]
    .copy()
)


# ------------------------------------------------------------
# SELECTED PATIENT ML ANOMALY
# ------------------------------------------------------------

selected_ml_anomaly = (
    patient_anomalies_df[
        patient_anomalies_df[
            "patient_id"
        ] == selected_patient
        ]
    .copy()
)


# ------------------------------------------------------------
# PCA DISPLAY DATA
# ------------------------------------------------------------

if not pca_df.empty:

    pca_df["cluster_label"] = (
            "Cluster "
            + pca_df["cluster_id"]
            .fillna(-1)
            .astype(int)
            .astype(str)
    )

    pca_df["outlier_status"] = (
        pca_df["is_outlier"]
        .map(
            {
                True: "Outlier",
                False: "Normal",
            }
        )
        .fillna("Unknown")
    )

    pca_df["patient_label"] = (
            "Patient "
            + pca_df["patient_id"]
            .astype(str)
    )

    selected_pca = (
        pca_df[
            pca_df["patient_id"]
            == selected_patient
            ]
        .copy()
    )

else:

    selected_pca = pd.DataFrame()


# ============================================================
# MEASUREMENT HELPERS
# ============================================================

def measurement(
        type_name,
):
    return patient_df[
        (
                patient_df[
                    "measurement_type"
                ] == type_name
        )
        &
        (
            patient_df[
                "measurement_value"
            ].notna()
        )
        ].copy()


saturation = measurement(
    "Saturation"
)

ecg = measurement(
    "ECG"
)

systolic = measurement(
    "SystolicPressure"
)

diastolic = measurement(
    "DiastolicPressure"
)

cholesterol = measurement(
    "Cholesterol"
)

rbc = measurement(
    "RedBloodCells"
)

wbc = measurement(
    "WhiteBloodCells"
)

alert_events = (
    patient_df[
        patient_df[
            "measurement_type"
        ] == "Alert"
        ]
    .copy()
)


# ============================================================
# ALERT HELPERS
# ============================================================

def risk_priority(
        risk,
):
    priorities = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }

    return priorities.get(
        risk,
        0,
    )


def risk_css_class(
        risk,
):
    if risk == "HIGH":
        return "alert-high"

    if risk == "MEDIUM":
        return "alert-medium"

    if risk == "LOW":
        return "alert-low"

    return "alert-unclassified"


def render_alert_card(
        title,
        risk,
        value,
        trigger,
        context,
        review,
        event_time=None,
):
    safe_title = html.escape(
        str(title)
    )

    safe_risk = html.escape(
        str(risk)
    )

    safe_value = html.escape(
        str(value)
    )

    safe_trigger = html.escape(
        str(trigger)
    )

    safe_context = html.escape(
        str(context)
    )

    safe_review = html.escape(
        str(review)
    )

    css_class = risk_css_class(
        risk
    )

    if event_time is not None:
        safe_time = html.escape(
            str(event_time)
        )

        time_html = (
            f'<div class="alert-time">'
            f'Latest relevant event: {safe_time}'
            f'</div>'
        )
    else:
        time_html = ""

    card = (
        f'<div class="alert-card {css_class}">'
        f'<div class="alert-header">'
        f'<div class="alert-title">{safe_title}</div>'
        f'<div class="risk-badge">RISK GROUP: {safe_risk}</div>'
        f'</div>'
        f'<div class="alert-value">{safe_value}</div>'
        f'<div class="alert-row">'
        f'<div class="alert-label">Trigger</div>'
        f'{safe_trigger}'
        f'</div>'
        f'<div class="alert-row">'
        f'<div class="alert-label">Interpretation</div>'
        f'{safe_context}'
        f'</div>'
        f'<div class="alert-row">'
        f'<div class="alert-label">Suggested review</div>'
        f'{safe_review}'
        f'</div>'
        f'{time_html}'
        f'</div>'
    )

    st.markdown(
        card,
        unsafe_allow_html=True,
    )


# ============================================================
# CLUSTER HELPERS
# ============================================================

CLUSTER_PROFILE_FEATURES = {
    "saturation_mean":
        "oxygen saturation",

    "saturation_std":
        "oxygen saturation variability",

    "systolicpressure_mean":
        "systolic blood pressure",

    "diastolicpressure_mean":
        "diastolic blood pressure",

    "low_saturation_rate":
        "low-saturation rate",

    "abnormal_systolic_rate":
        "abnormal systolic rate",

    "abnormal_diastolic_rate":
        "abnormal diastolic rate",

    "zscore_anomaly_rate":
        "Z-score anomaly rate",

    "high_zscore_count":
        "HIGH anomaly count",

    "max_abs_zscore":
        "maximum Z-score magnitude",
}


def build_cluster_profile_text(
        cluster_members,
        all_patients,
):
    """
    Describe the cluster relative to the whole dataset.

    We standardize the difference between the cluster mean
    and the overall dataset mean and take the largest
    differences.
    """

    if (
            cluster_members.empty
            or all_patients.empty
    ):
        return (
            "No cluster profile available."
        )

    descriptions = []

    for (
            feature,
            label,
    ) in CLUSTER_PROFILE_FEATURES.items():

        values = (
            all_patients[
                feature
            ]
            .dropna()
        )

        cluster_values = (
            cluster_members[
                feature
            ]
            .dropna()
        )

        if (
                values.empty
                or cluster_values.empty
        ):
            continue

        dataset_mean = (
            values.mean()
        )

        dataset_std = (
            values.std()
        )

        cluster_mean = (
            cluster_values.mean()
        )

        if (
                pd.isna(dataset_std)
                or dataset_std == 0
        ):
            continue

        standardized_difference = (
                (
                        cluster_mean
                        - dataset_mean
                )
                / dataset_std
        )

        descriptions.append(
            {
                "label": label,
                "difference":
                    standardized_difference,
            }
        )


    if not descriptions:
        return (
            "The cluster is close to the "
            "overall dataset average."
        )


    descriptions = sorted(
        descriptions,
        key=lambda item:
        abs(
            item[
                "difference"
            ]
        ),
        reverse=True,
    )


    parts = []

    for item in descriptions[:3]:

        direction = (
            "higher"
            if item["difference"] > 0
            else "lower"
        )

        parts.append(
            f"{direction} {item['label']}"
        )


    return (
            "Compared with the full synthetic patient "
            "population, this cluster tends to show "
            + ", ".join(parts)
            + "."
    )


# ============================================================
# CREATE RULE-BASED ALERTS
# ============================================================

patient_alerts = []


# ------------------------------------------------------------
# OXYGEN SATURATION
# ------------------------------------------------------------

if not saturation.empty:

    low_sat = saturation[
        saturation[
            "measurement_value"
        ] < 92
        ]

    if not low_sat.empty:

        latest_low = (
            low_sat.iloc[-1]
        )

        latest_low_value = (
            latest_low[
                "measurement_value"
            ]
        )

        minimum_sat = (
            low_sat[
                "measurement_value"
            ].min()
        )

        low_count = len(
            low_sat
        )

        if (
                latest_low_value < 88
                or minimum_sat < 88
        ):
            risk = "HIGH"
        else:
            risk = "MEDIUM"

        patient_alerts.append(
            {
                "type":
                    "oxygen",

                "risk":
                    risk,

                "title":
                    "Low Oxygen Saturation",

                "value":
                    f"{latest_low_value:.1f}%",

                "trigger": (
                    f"{low_count} reading(s) below "
                    f"the configured 92% threshold. "
                    f"Lowest recorded value: "
                    f"{minimum_sat:.1f}%."
                ),

                "context": (
                    "Oxygen saturation is below the "
                    "configured demonstration threshold. "
                    "This rule indicates an abnormal "
                    "SpO₂ pattern in the simulated data."
                ),

                "review": (
                    "Inspect the recent oxygen saturation "
                    "trend and compare it with blood "
                    "pressure and other measurements."
                ),

                "time":
                    latest_low[
                        "recorded_at"
                    ],
            }
        )


# ------------------------------------------------------------
# BLOOD PRESSURE
# ------------------------------------------------------------

if (
        not systolic.empty
        and not diastolic.empty
):

    latest_sys_row = (
        systolic.iloc[-1]
    )

    latest_dia_row = (
        diastolic.iloc[-1]
    )

    latest_sys = (
        latest_sys_row[
            "measurement_value"
        ]
    )

    latest_dia = (
        latest_dia_row[
            "measurement_value"
        ]
    )

    abnormal_bp = (
            latest_sys > 140
            or latest_sys < 90
            or latest_dia > 90
            or latest_dia < 60
    )

    if abnormal_bp:

        if (
                latest_sys > 160
                or latest_dia > 100
                or latest_sys < 80
                or latest_dia < 50
        ):
            risk = "HIGH"
        else:
            risk = "MEDIUM"

        latest_bp_time = max(
            latest_sys_row[
                "recorded_at"
            ],
            latest_dia_row[
                "recorded_at"
            ],
        )

        patient_alerts.append(
            {
                "type":
                    "blood_pressure",

                "risk":
                    risk,

                "title":
                    "Abnormal Blood Pressure",

                "value": (
                    f"{latest_sys:.0f}/"
                    f"{latest_dia:.0f} mmHg"
                ),

                "trigger": (
                    "Configured demo range: "
                    "systolic 90–140 mmHg and "
                    "diastolic 60–90 mmHg."
                ),

                "context": (
                    "The latest blood-pressure reading "
                    "is outside the configured "
                    "rule-based range."
                ),

                "review": (
                    "Inspect recent systolic and "
                    "diastolic trends and compare them "
                    "with oxygen saturation."
                ),

                "time":
                    latest_bp_time,
            }
        )


# ------------------------------------------------------------
# SIMULATOR ALERT
# ------------------------------------------------------------

if not alert_events.empty:

    latest_simulator_alert = (
        alert_events.iloc[-1]
    )

    simulator_text = (
        latest_simulator_alert[
            "measurement_data"
        ]
    )

    patient_alerts.append(
        {
            "type":
                "simulator",

            "risk":
                "LOW",

            "title":
                "Simulator Alert Event",

            "value":
                f"{len(alert_events)} event(s)",

            "trigger": (
                f"Latest simulator message: "
                f"{simulator_text}"
            ),

            "context": (
                "This event was explicitly generated "
                "by the Java health-data simulator."
            ),

            "review": (
                "Compare the event timestamp with "
                "oxygen saturation, blood pressure "
                "and ECG activity."
            ),

            "time":
                latest_simulator_alert[
                    "recorded_at"
                ],
        }
    )


if patient_alerts:

    overall_risk = max(
        (
            alert[
                "risk"
            ]
            for alert
            in patient_alerts
        ),
        key=risk_priority,
    )

else:

    overall_risk = "LOW"


# ============================================================
# HEADER
# ============================================================

header_left, header_right = (
    st.columns(
        [5, 1]
    )
)


with header_left:

    st.title(
        "Cardiovascular patient monitoring"
    )

    st.markdown(
        """
        <div class="section-description">
            Real-time patient monitoring and descriptive analytics
        </div>
        """,
        unsafe_allow_html=True,
    )


with header_right:

    st.markdown(
        """
        <div style="padding-top:18px;">
            <span class="live-badge">
                ● LIVE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    f"### Patient {selected_patient}"
)


# ============================================================
# MAIN KPI
# ============================================================

kpi1, kpi2, kpi3, kpi4 = (
    st.columns(4)
)


if not saturation.empty:

    latest_sat = (
        saturation.iloc[-1][
            "measurement_value"
        ]
    )

    if len(saturation) >= 2:

        previous_sat = (
            saturation.iloc[-2][
                "measurement_value"
            ]
        )

        sat_delta = (
                latest_sat
                - previous_sat
        )

        kpi1.metric(
            "Oxygen Saturation",
            f"{latest_sat:.1f}%",
            f"{sat_delta:+.1f}%",
        )

    else:

        kpi1.metric(
            "Oxygen Saturation",
            f"{latest_sat:.1f}%",
        )

else:

    kpi1.metric(
        "Oxygen Saturation",
        "No data",
    )


if (
        not systolic.empty
        and not diastolic.empty
):

    latest_sys = (
        systolic.iloc[-1][
            "measurement_value"
        ]
    )

    latest_dia = (
        diastolic.iloc[-1][
            "measurement_value"
        ]
    )

    kpi2.metric(
        "Blood Pressure",
        f"{latest_sys:.0f}/{latest_dia:.0f} mmHg",
    )

else:

    kpi2.metric(
        "Blood Pressure",
        "No data",
    )


kpi3.metric(
    "Active Alert Rules",
    len(
        patient_alerts
    ),
)


kpi4.metric(
    "Risk Group",
    overall_risk,
)


# ============================================================
# DATA COMPLETENESS
# ============================================================

expected_types = {
    "ECG",
    "Saturation",
    "SystolicPressure",
    "DiastolicPressure",
    "Cholesterol",
    "RedBloodCells",
    "WhiteBloodCells",
    "Alert",
}


available_types = set(
    patient_df[
        "measurement_type"
    ].unique()
)


available_count = len(
    expected_types
    & available_types
)


completeness = (
        available_count
        / len(
    expected_types
)
)


st.markdown(
    "#### Data completeness"
)

st.progress(
    completeness
)

st.caption(
    f"{available_count} of "
    f"{len(expected_types)} expected data types "
    f"available ({completeness:.0%})"
)


# ============================================================
# TABS
# ============================================================

(
    overview_tab,
    signals_tab,
    lab_tab,
    analytics_tab,
) = st.tabs(
    [
        "Overview",
        "Signals",
        "Blood analysis",
        "Statistical Analytics",
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with overview_tab:

    st.subheader(
        "Patient Overview"
    )

    overview_left, overview_right = (
        st.columns(
            [2, 1]
        )
    )


    with overview_left:

        st.markdown(
            "#### Oxygen Saturation"
        )

        if not saturation.empty:

            fig = px.line(
                saturation,
                x="recorded_at",
                y="measurement_value",
            )

            fig.update_traces(
                line=dict(
                    color="#47B7FF",
                    width=2.5,
                )
            )

            fig.update_layout(
                height=400,
                paper_bgcolor=
                "rgba(0,0,0,0)",
                plot_bgcolor=
                "rgba(0,0,0,0)",
                font=dict(
                    color="#DCEEFF"
                ),
                xaxis_title=None,
                yaxis_title="SpO₂ (%)",
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20,
                ),
            )

            fig.update_xaxes(
                gridcolor=
                "rgba(120,180,220,0.08)"
            )

            fig.update_yaxes(
                gridcolor=
                "rgba(120,180,220,0.08)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.info(
                "No saturation data available."
            )


    with overview_right:

        risk_summary_html = (
            '<div class="risk-summary">'
            '<div class="risk-summary-title">'
            'Current patient risk group'
            '</div>'
            f'<div class="risk-summary-value">'
            f'{overall_risk}'
            f'</div>'
            '</div>'
        )

        st.markdown(
            risk_summary_html,
            unsafe_allow_html=True,
        )


        if patient_alerts:

            sorted_alerts = sorted(
                patient_alerts,
                key=lambda item:
                risk_priority(
                    item["risk"]
                ),
                reverse=True,
            )

            for alert in sorted_alerts:

                render_alert_card(
                    title=
                    alert["title"],
                    risk=
                    alert["risk"],
                    value=
                    alert["value"],
                    trigger=
                    alert["trigger"],
                    context=
                    alert["context"],
                    review=
                    alert["review"],
                    event_time=
                    alert["time"],
                )

        else:

            st.success(
                "No active rule-based alerts detected."
            )


        st.caption(
            "Risk groups and thresholds are "
            "rule-based demonstration logic applied "
            "to synthetic simulator data. "
            "They are not medical diagnoses."
        )


    st.subheader(
        "Recent Measurements"
    )

    recent = (
        patient_df[
            [
                "recorded_at",
                "measurement_type",
                "measurement_data",
            ]
        ]
        .sort_values(
            "recorded_at",
            ascending=False,
        )
        .head(30)
        .copy()
    )

    recent.columns = [
        "Timestamp",
        "Measurement",
        "Value",
    ]

    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SIGNALS
# ============================================================

with signals_tab:

    st.subheader(
        "Physiological Signals"
    )


    st.markdown(
        "#### Blood Pressure"
    )


    if (
            not systolic.empty
            and not diastolic.empty
    ):

        bp_fig = go.Figure()

        bp_fig.add_trace(
            go.Scatter(
                x=systolic[
                    "recorded_at"
                ],
                y=systolic[
                    "measurement_value"
                ],
                mode="lines+markers",
                name="Systolic",
                line=dict(
                    color="#55C2FF",
                    width=2.5,
                ),
            )
        )

        bp_fig.add_trace(
            go.Scatter(
                x=diastolic[
                    "recorded_at"
                ],
                y=diastolic[
                    "measurement_value"
                ],
                mode="lines+markers",
                name="Diastolic",
                line=dict(
                    color="#A7DFFF",
                    width=2.5,
                ),
            )
        )

        bp_fig.update_layout(
            height=390,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            xaxis_title=None,
            yaxis_title="mmHg",
            hovermode="x unified",
            legend=dict(
                orientation="h"
            ),
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            bp_fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No complete blood pressure data available."
        )


    st.markdown(
        "#### ECG Signal"
    )


    if not ecg.empty:

        ecg_fig = px.line(
            ecg.tail(500),
            x="recorded_at",
            y="measurement_value",
        )

        ecg_fig.update_traces(
            line=dict(
                color="#4EBEFF",
                width=2,
            )
        )

        ecg_fig.update_layout(
            height=430,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            xaxis_title=None,
            yaxis_title="ECG",
            hovermode="x unified",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            ecg_fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No ECG data available."
        )


    st.markdown(
        "#### Oxygen Saturation"
    )


    if not saturation.empty:

        sat_fig = px.line(
            saturation,
            x="recorded_at",
            y="measurement_value",
        )

        sat_fig.update_traces(
            line=dict(
                color="#8BD8FF",
                width=2.5,
            )
        )

        sat_fig.update_layout(
            height=360,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            xaxis_title=None,
            yaxis_title="SpO₂ (%)",
            hovermode="x unified",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            sat_fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No oxygen saturation data available."
        )


# ============================================================
# LABORATORY
# ============================================================

with lab_tab:

    st.subheader(
        "Laboratory Measurements"
    )


    lab1, lab2, lab3 = (
        st.columns(3)
    )


    if not cholesterol.empty:

        latest_cholesterol = (
            cholesterol.iloc[-1][
                "measurement_value"
            ]
        )

        lab1.metric(
            "Cholesterol",
            f"{latest_cholesterol:.2f}",
        )

    else:

        lab1.metric(
            "Cholesterol",
            "No data",
        )


    if not rbc.empty:

        latest_rbc = (
            rbc.iloc[-1][
                "measurement_value"
            ]
        )

        lab2.metric(
            "Red Blood Cells",
            f"{latest_rbc:.2f}",
        )

    else:

        lab2.metric(
            "Red Blood Cells",
            "No data",
        )


    if not wbc.empty:

        latest_wbc = (
            wbc.iloc[-1][
                "measurement_value"
            ]
        )

        lab3.metric(
            "White Blood Cells",
            f"{latest_wbc:.2f}",
        )

    else:

        lab3.metric(
            "White Blood Cells",
            "No data",
        )


    st.divider()


    lab_data = (
        patient_df[
            (
                patient_df[
                    "measurement_type"
                ].isin(
                    [
                        "Cholesterol",
                        "RedBloodCells",
                        "WhiteBloodCells",
                    ]
                )
            )
            &
            (
                patient_df[
                    "measurement_value"
                ].notna()
            )
            ]
        .copy()
    )


    if not lab_data.empty:

        st.markdown(
            "#### Laboratory History"
        )

        lab_fig = px.line(
            lab_data,
            x="recorded_at",
            y="measurement_value",
            color="measurement_type",
            markers=True,
        )

        lab_fig.update_layout(
            height=420,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            xaxis_title=None,
            yaxis_title="Value",
            hovermode="x unified",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            lab_fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No laboratory data available."
        )


# ============================================================
# STATISTICAL / ML ANALYTICS
# ============================================================

with analytics_tab:

    # ========================================================
    # PATIENT ANALYTICS SUMMARY
    # ========================================================

    st.subheader(
        "Patient Analytics Summary"
    )

    st.markdown(
        """
        <div class="section-description">
            Combined rule-based, statistical and
            machine-learning patient analytics
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Z-SCORE SUMMARY VALUE
    # --------------------------------------------------------

    if not selected_features.empty:

        summary_feature_row = (
            selected_features.iloc[0]
        )

        summary_anomaly_rate = (
            summary_feature_row[
                "zscore_anomaly_rate"
            ]
        )

        if pd.isna(
                summary_anomaly_rate
        ):
            summary_anomaly_rate = 0.0

    else:

        summary_anomaly_rate = None


    # --------------------------------------------------------
    # CLUSTER SUMMARY VALUES
    # --------------------------------------------------------

    if not selected_cluster.empty:

        summary_cluster_row = (
            selected_cluster.iloc[0]
        )

        summary_cluster_id = int(
            summary_cluster_row[
                "cluster_id"
            ]
        )

        summary_cluster_distance = (
            summary_cluster_row[
                "distance_to_centroid"
            ]
        )

    else:

        summary_cluster_id = None
        summary_cluster_distance = None


    # --------------------------------------------------------
    # ISOLATION FOREST SUMMARY VALUES
    # --------------------------------------------------------

    if not selected_ml_anomaly.empty:

        ml_row = (
            selected_ml_anomaly.iloc[0]
        )

        ml_anomaly_score = (
            ml_row[
                "anomaly_score"
            ]
        )

        ml_is_outlier = bool(
            ml_row[
                "is_outlier"
            ]
        )

        ml_outlier_rank = (
            ml_row[
                "outlier_rank"
            ]
        )

        if pd.isna(
                ml_outlier_rank
        ):
            ml_outlier_rank = None
        else:
            ml_outlier_rank = int(
                ml_outlier_rank
            )

    else:

        ml_anomaly_score = None
        ml_is_outlier = None
        ml_outlier_rank = None


    # --------------------------------------------------------
    # SUMMARY KPI ROW 1
    # --------------------------------------------------------

    (
        summary1,
        summary2,
        summary3,
    ) = st.columns(3)


    summary1.metric(
        "Rule-based Risk",
        overall_risk,
    )


    if summary_anomaly_rate is None:

        summary2.metric(
            "Z-score Anomaly Rate",
            "No data",
        )

    else:

        summary2.metric(
            "Z-score Anomaly Rate",
            f"{summary_anomaly_rate:.2%}",
        )


    if summary_cluster_id is None:

        summary3.metric(
            "Cluster",
            "No data",
        )

    else:

        summary3.metric(
            "Cluster",
            summary_cluster_id,
        )


    # --------------------------------------------------------
    # SUMMARY KPI ROW 2
    # --------------------------------------------------------

    (
        summary4,
        summary5,
        summary6,
    ) = st.columns(3)


    if (
            summary_cluster_distance is None
            or pd.isna(
        summary_cluster_distance
    )
    ):

        summary4.metric(
            "Cluster Distance",
            "No data",
        )

    else:

        summary4.metric(
            "Cluster Distance",
            f"{summary_cluster_distance:.3f}",
        )


    if ml_is_outlier is None:

        summary5.metric(
            "ML Outlier",
            "No data",
        )

    else:

        summary5.metric(
            "ML Outlier",
            (
                "YES"
                if ml_is_outlier
                else "NO"
            ),
        )


    if ml_outlier_rank is None:

        summary6.metric(
            "Outlier Rank",
            "No data",
        )

    else:

        summary6.metric(
            "Outlier Rank",
            f"#{ml_outlier_rank}",
        )


    if (
            ml_anomaly_score is not None
            and not pd.isna(
        ml_anomaly_score
    )
    ):

        st.caption(
            f"Isolation Forest anomaly score: "
            f"{ml_anomaly_score:.4f}. "
            f"Higher values indicate a more unusual "
            f"patient profile relative to the current "
            f"synthetic patient population."
        )


    st.caption(
        "Rule-based risk, Z-score anomalies, KMeans clusters "
        "and Isolation Forest results describe different "
        "statistical aspects of the synthetic patient data. "
        "They are not medical diagnoses."
    )


    st.divider()


    # ========================================================
    # Z-SCORE SECTION
    # ========================================================

    st.subheader(
        "Statistical Anomaly Detection"
    )

    st.markdown(
        """
        <div class="section-description">
            Patient-specific anomaly detection based on
            rolling statistics and Z-scores
        </div>
        """,
        unsafe_allow_html=True,
    )


    (
        anomaly_kpi1,
        anomaly_kpi2,
        anomaly_kpi3,
        anomaly_kpi4,
    ) = st.columns(4)


    if not selected_features.empty:

        feature_row = (
            selected_features.iloc[0]
        )

        anomaly_rate = (
            feature_row[
                "zscore_anomaly_rate"
            ]
        )

        max_abs_zscore = (
            feature_row[
                "max_abs_zscore"
            ]
        )

        high_count = (
            feature_row[
                "high_zscore_count"
            ]
        )

        anomaly_count = (
            feature_row[
                "zscore_anomaly_count"
            ]
        )


        if pd.isna(anomaly_rate):
            anomaly_rate = 0.0

        if pd.isna(max_abs_zscore):
            max_abs_zscore = 0.0

        if pd.isna(high_count):
            high_count = 0

        if pd.isna(anomaly_count):
            anomaly_count = 0


        anomaly_kpi1.metric(
            "Anomaly Rate",
            f"{anomaly_rate:.2%}",
        )

        anomaly_kpi2.metric(
            "Max |Z-score|",
            f"{max_abs_zscore:.2f}",
        )

        anomaly_kpi3.metric(
            "HIGH Anomalies",
            int(high_count),
        )

        anomaly_kpi4.metric(
            "Total Anomalies",
            int(anomaly_count),
        )

    else:

        anomaly_kpi1.metric(
            "Anomaly Rate",
            "No data",
        )

        anomaly_kpi2.metric(
            "Max |Z-score|",
            "No data",
        )

        anomaly_kpi3.metric(
            "HIGH Anomalies",
            "No data",
        )

        anomaly_kpi4.metric(
            "Total Anomalies",
            "No data",
        )


    st.markdown(
        "#### Latest Statistical Anomalies"
    )


    if selected_zscore_anomalies.empty:

        st.info(
            "No statistical anomalies detected "
            "for this patient."
        )

    else:

        anomaly_table = (
            selected_zscore_anomalies[
                [
                    "recorded_at",
                    "measurement_type",
                    "measurement_value",
                    "rolling_mean",
                    "rolling_std",
                    "z_score",
                    "anomaly_level",
                ]
            ]
            .head(10)
            .copy()
        )


        for column in [
            "measurement_value",
            "rolling_mean",
            "rolling_std",
        ]:
            anomaly_table[column] = (
                anomaly_table[column]
                .round(3)
            )


        anomaly_table[
            "z_score"
        ] = (
            anomaly_table[
                "z_score"
            ]
            .round(2)
        )


        anomaly_table = (
            anomaly_table.rename(
                columns={
                    "recorded_at":
                        "Timestamp",

                    "measurement_type":
                        "Measurement",

                    "measurement_value":
                        "Value",

                    "rolling_mean":
                        "Rolling Mean",

                    "rolling_std":
                        "Rolling Std",

                    "z_score":
                        "Z-score",

                    "anomaly_level":
                        "Level",
                }
            )
        )


        st.dataframe(
            anomaly_table,
            use_container_width=True,
            hide_index=True,
        )


    st.markdown(
        "#### Anomalies by Measurement Type"
    )


    if not selected_zscore_anomalies.empty:

        anomaly_counts = (
            selected_zscore_anomalies[
                "measurement_type"
            ]
            .value_counts()
            .reset_index()
        )

        anomaly_counts.columns = [
            "Measurement",
            "Anomaly Count",
        ]

        anomaly_fig = px.bar(
            anomaly_counts,
            x="Measurement",
            y="Anomaly Count",
        )

        anomaly_fig.update_traces(
            marker_color=
            "#47B7FF"
        )

        anomaly_fig.update_layout(
            height=360,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            xaxis_title=None,
            yaxis_title=
            "Detected anomalies",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            anomaly_fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No anomaly distribution available."
        )


    st.markdown(
        "#### Recent Z-score Anomaly Magnitude"
    )


    if not selected_zscore_anomalies.empty:

        zscore_chart_df = (
            selected_zscore_anomalies
            .head(100)
            .copy()
            .sort_values(
                "recorded_at"
            )
        )

        zscore_chart_df[
            "abs_zscore"
        ] = (
            zscore_chart_df[
                "z_score"
            ]
            .abs()
        )

        zscore_fig = px.scatter(
            zscore_chart_df,
            x="recorded_at",
            y="abs_zscore",
            color="anomaly_level",
            hover_data=[
                "measurement_type",
                "measurement_value",
                "rolling_mean",
                "z_score",
            ],
        )

        zscore_fig.add_hline(
            y=3.0,
            line_dash="dash",
            annotation_text=
            "MEDIUM threshold |z| = 3",
        )

        zscore_fig.add_hline(
            y=4.0,
            line_dash="dash",
            annotation_text=
            "HIGH threshold |z| = 4",
        )

        zscore_fig.update_layout(
            height=420,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            xaxis_title=None,
            yaxis_title="|Z-score|",
            margin=dict(
                l=20,
                r=20,
                t=35,
                b=20,
            ),
        )

        st.plotly_chart(
            zscore_fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No Z-score anomaly history available."
        )


    st.caption(
        "Z-score thresholds and anomaly classifications "
        "are demonstration analytics applied to synthetic "
        "patient data. They are not clinical thresholds "
        "or medical diagnoses."
    )


    # ========================================================
    # CLUSTER ANALYTICS
    # ========================================================

    st.divider()

    st.subheader(
        "Machine Learning Cluster Analysis"
    )

    st.markdown(
        """
        <div class="section-description">
            KMeans segmentation based on standardized
            patient-level statistical features
        </div>
        """,
        unsafe_allow_html=True,
    )


    if selected_cluster.empty:

        st.info(
            "No clustering result available. "
            "Run analytics/clustering.py first."
        )

    else:

        cluster_row = (
            selected_cluster.iloc[0]
        )

        cluster_id = int(
            cluster_row[
                "cluster_id"
            ]
        )

        distance_to_centroid = (
            cluster_row[
                "distance_to_centroid"
            ]
        )


        cluster_members = (
            cluster_features_df[
                cluster_features_df[
                    "cluster_id"
                ] == cluster_id
                ]
            .copy()
        )


        cluster_size = len(
            cluster_members
        )


        cluster_kpi1, cluster_kpi2, cluster_kpi3 = (
            st.columns(3)
        )


        cluster_kpi1.metric(
            "Cluster ID",
            cluster_id,
        )


        if pd.isna(
                distance_to_centroid
        ):

            cluster_kpi2.metric(
                "Distance to Centroid",
                "No data",
            )

        else:

            cluster_kpi2.metric(
                "Distance to Centroid",
                f"{distance_to_centroid:.3f}",
            )


        cluster_kpi3.metric(
            "Patients in Cluster",
            cluster_size,
        )


        st.caption(
            "Cluster ID represents an unsupervised "
            "statistical segment. Distance to centroid "
            "measures how far the patient is from the "
            "typical standardized profile of that cluster. "
            "Neither metric is a medical risk score."
        )


        # ----------------------------------------------------
        # CLUSTER PROFILE
        # ----------------------------------------------------

        st.markdown(
            "#### Cluster Profile"
        )


        profile_text = (
            build_cluster_profile_text(
                cluster_members,
                cluster_features_df,
            )
        )


        st.info(
            profile_text
        )


        if not cluster_members.empty:

            cluster_mean = (
                cluster_members[
                    [
                        "saturation_mean",
                        "systolicpressure_mean",
                        "diastolicpressure_mean",
                        "zscore_anomaly_rate",
                        "max_abs_zscore",
                    ]
                ]
                .mean()
            )


            profile1, profile2, profile3 = (
                st.columns(3)
            )


            profile1.metric(
                "Cluster Avg SpO₂",
                (
                    f"{cluster_mean['saturation_mean']:.2f}%"
                    if pd.notna(
                        cluster_mean[
                            "saturation_mean"
                        ]
                    )
                    else "No data"
                ),
            )


            profile2.metric(
                "Cluster Avg Systolic",
                (
                    f"{cluster_mean['systolicpressure_mean']:.1f}"
                    if pd.notna(
                        cluster_mean[
                            "systolicpressure_mean"
                        ]
                    )
                    else "No data"
                ),
            )


            profile3.metric(
                "Cluster Avg Anomaly Rate",
                (
                    f"{cluster_mean['zscore_anomaly_rate']:.2%}"
                    if pd.notna(
                        cluster_mean[
                            "zscore_anomaly_rate"
                        ]
                    )
                    else "No data"
                ),
            )


        # ----------------------------------------------------
        # PATIENT VS CLUSTER
        # ----------------------------------------------------

        st.markdown(
            "#### Patient vs Cluster Average"
        )


        if selected_cluster_features.empty:

            st.info(
                "No patient feature data available "
                "for cluster comparison."
            )

        else:

            patient_row = (
                selected_cluster_features.iloc[0]
            )


            comparison_features = {
                "Saturation Mean":
                    "saturation_mean",

                "Saturation Variability":
                    "saturation_std",

                "Systolic Mean":
                    "systolicpressure_mean",

                "Diastolic Mean":
                    "diastolicpressure_mean",

                "Low Saturation Rate":
                    "low_saturation_rate",

                "Abnormal Systolic Rate":
                    "abnormal_systolic_rate",

                "Abnormal Diastolic Rate":
                    "abnormal_diastolic_rate",

                "Z-score Anomaly Rate":
                    "zscore_anomaly_rate",

                "HIGH Z-score Count":
                    "high_zscore_count",

                "Max |Z-score|":
                    "max_abs_zscore",
            }


            comparison_rows = []


            for (
                    label,
                    feature,
            ) in comparison_features.items():

                patient_value = (
                    patient_row[
                        feature
                    ]
                )

                cluster_value = (
                    cluster_members[
                        feature
                    ].mean()
                )


                if (
                        pd.isna(
                            patient_value
                        )
                        or pd.isna(
                    cluster_value
                )
                ):

                    difference = None

                else:

                    difference = (
                            patient_value
                            - cluster_value
                    )


                comparison_rows.append(
                    {
                        "Feature":
                            label,

                        "Patient":
                            patient_value,

                        "Cluster Average":
                            cluster_value,

                        "Difference":
                            difference,
                    }
                )


            comparison_df = (
                pd.DataFrame(
                    comparison_rows
                )
            )


            for column in [
                "Patient",
                "Cluster Average",
                "Difference",
            ]:

                comparison_df[
                    column
                ] = (
                    comparison_df[
                        column
                    ]
                    .round(4)
                )


            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True,
            )


        st.caption(
            "Cluster profiles are calculated from synthetic "
            "patient features produced by the simulator. "
            "KMeans discovers statistical similarity only; "
            "clusters do not represent diagnoses or clinical groups."
        )

    # ========================================================
    # PCA VISUALIZATION
    # ========================================================

    st.divider()

    st.subheader(
        "Patient Population — PCA Projection"
    )

    st.markdown(
        """
        <div class="section-description">
            Two-dimensional projection of the standardized
            patient-level feature space
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pca_df.empty:

        st.info(
            "No PCA results available. "
            "Run analytics/pca_analysis.py first."
        )

    else:

        explained_pc1 = (
            pca_df["explained_variance_pc1"]
            .iloc[0]
        )

        explained_pc2 = (
            pca_df["explained_variance_pc2"]
            .iloc[0]
        )

        explained_total = (
                explained_pc1
                + explained_pc2
        )

        (
            pca_kpi1,
            pca_kpi2,
            pca_kpi3,
        ) = st.columns(3)

        pca_kpi1.metric(
            "PC1 Explained Variance",
            f"{explained_pc1:.1%}",
        )

        pca_kpi2.metric(
            "PC2 Explained Variance",
            f"{explained_pc2:.1%}",
        )

        pca_kpi3.metric(
            "2D Variance Retained",
            f"{explained_total:.1%}",
        )

        pca_fig = px.scatter(
            pca_df,
            x="pc1",
            y="pc2",
            color="cluster_label",
            symbol="outlier_status",
            hover_name="patient_label",
            hover_data={
                "patient_id": False,
                "cluster_label": True,
                "outlier_status": True,
                "anomaly_score": ":.4f",
                "outlier_rank": True,
                "distance_to_centroid": ":.3f",
                "zscore_anomaly_rate": ":.2%",
                "max_abs_zscore": ":.2f",
                "pc1": ":.3f",
                "pc2": ":.3f",
            },
            labels={
                "pc1": (
                    f"PC1 "
                    f"({explained_pc1:.1%} variance)"
                ),
                "pc2": (
                    f"PC2 "
                    f"({explained_pc2:.1%} variance)"
                ),
                "cluster_label": "Cluster",
                "outlier_status": "Isolation Forest",
                "anomaly_score": "Anomaly Score",
                "outlier_rank": "Outlier Rank",
                "distance_to_centroid": "Cluster Distance",
                "zscore_anomaly_rate": "Z-score Anomaly Rate",
                "max_abs_zscore": "Max |Z-score|",
            },
        )

        pca_fig.update_traces(
            marker=dict(
                size=13,
                opacity=0.82,
                line=dict(
                    width=1,
                ),
            )
        )

        if not selected_pca.empty:

            selected_pca_row = (
                selected_pca.iloc[0]
            )

            pca_fig.add_trace(
                go.Scatter(
                    x=[selected_pca_row["pc1"]],
                    y=[selected_pca_row["pc2"]],
                    mode="markers+text",
                    name=(
                        f"Selected Patient "
                        f"{selected_patient}"
                    ),
                    text=[
                        f"Patient {selected_patient}"
                    ],
                    textposition="top center",
                    marker=dict(
                        symbol="star",
                        size=24,
                        color="#FFFFFF",
                        line=dict(
                            color="#071426",
                            width=2,
                        ),
                    ),
                    hovertemplate=(
                        f"<b>Selected Patient "
                        f"{selected_patient}</b>"
                        "<br>"
                        "PC1: %{x:.3f}"
                        "<br>"
                        "PC2: %{y:.3f}"
                        "<extra></extra>"
                    ),
                )
            )

        pca_fig.add_hline(
            y=0,
            line_dash="dot",
            line_color=
            "rgba(255,255,255,0.20)",
        )

        pca_fig.add_vline(
            x=0,
            line_dash="dot",
            line_color=
            "rgba(255,255,255,0.20)",
        )

        pca_fig.update_layout(
            height=650,
            paper_bgcolor=
            "rgba(0,0,0,0)",
            plot_bgcolor=
            "rgba(0,0,0,0)",
            font=dict(
                color="#DCEEFF"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            margin=dict(
                l=20,
                r=20,
                t=80,
                b=20,
            ),
        )

        pca_fig.update_xaxes(
            gridcolor=
            "rgba(120,180,220,0.08)",
            zeroline=False,
        )

        pca_fig.update_yaxes(
            gridcolor=
            "rgba(120,180,220,0.08)",
            zeroline=False,
        )

        st.plotly_chart(
            pca_fig,
            use_container_width=True,
        )

        if not selected_pca.empty:

            selected_pca_row = (
                selected_pca.iloc[0]
            )

            pca_position1, pca_position2 = (
                st.columns(2)
            )

            pca_position1.metric(
                "Selected Patient PC1",
                f"{selected_pca_row['pc1']:.3f}",
            )

            pca_position2.metric(
                "Selected Patient PC2",
                f"{selected_pca_row['pc2']:.3f}",
            )

        st.caption(
            "Each point represents one patient in a "
            "two-dimensional PCA projection of the "
            "standardized patient feature space. "
            "Patients located closer together have more "
            "similar feature profiles in this projection."
        )

        st.caption(
            "Color represents KMeans cluster membership. "
            "Marker shape represents Isolation Forest "
            "outlier status. The white star highlights "
            "the patient currently selected in the sidebar."
        )

        st.caption(
            "PCA is used for exploratory visualization only. "
            "PC1 and PC2 are mathematical combinations of "
            "the original patient features and are not "
            "clinical measurements or medical risk scores."
        )

