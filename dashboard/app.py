import html
from textwrap import dedent

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
    initial_sidebar_state="expanded"
)

st_autorefresh(
    interval=5000,
    key="cardio_dashboard_refresh"
)


# ============================================================
# CSS / DESIGN
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       MAIN PAGE
       ====================================================== */

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


    /* ======================================================
       SIDEBAR
       ====================================================== */

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


    /* ======================================================
       SELECTBOX
       ====================================================== */

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


    /* ======================================================
       KPI CARDS
       ====================================================== */

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


    /* ======================================================
       TABS
       ====================================================== */

    button[data-baseweb="tab"] {
        color: #9CCFFF;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF;
        border-bottom-color: #46B5FF;
    }
    


    /* ======================================================
       LIVE BADGE
       ====================================================== */

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


    /* ======================================================
       ALERT CENTER
       ====================================================== */

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


    /* ======================================================
       RISK SUMMARY
       ====================================================== */

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


    /* ======================================================
       TABLES / PROGRESS / ALERTS
       ====================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stProgress"] > div > div {
        background-color: #47B7FF;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

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

df = pd.read_sql(
    query,
    engine
)


# ============================================================
# DATA CLEANING
# ============================================================

if df.empty:
    st.warning("No measurements available.")
    st.stop()


# Extract the first numeric component.
#
# Examples:
# "98.0%" -> 98.0
# "120 mmHg" -> 120.0
# "0.43" -> 0.43
#
numeric_text = (
    df["measurement_data"]
    .astype(str)
    .str.extract(
        r"(-?\d+(?:\.\d+)?)",
        expand=False
    )
)

df["measurement_value"] = pd.to_numeric(
    numeric_text,
    errors="coerce"
)

df["recorded_at"] = pd.to_datetime(
    df["recorded_at"]
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
    patients
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
# PATIENT DATA
# ============================================================

patient_df = (
    df[
        df["patient_id"] == selected_patient
        ]
    .copy()
    .sort_values("recorded_at")
)


def measurement(type_name):
    return patient_df[
        (
                patient_df["measurement_type"]
                == type_name
        )
        &
        patient_df[
            "measurement_value"
        ].notna()
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

alert_events = patient_df[
    patient_df["measurement_type"]
    == "Alert"
    ].copy()


# ============================================================
# ALERT / RISK HELPERS
# ============================================================

def risk_priority(risk):
    priorities = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3
    }

    return priorities.get(
        risk,
        0
    )


def risk_css_class(risk):
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
        event_time=None
):
    safe_title = html.escape(str(title))
    safe_risk = html.escape(str(risk))
    safe_value = html.escape(str(value))
    safe_trigger = html.escape(str(trigger))
    safe_context = html.escape(str(context))
    safe_review = html.escape(str(review))

    css_class = risk_css_class(risk)

    if event_time is not None:
        safe_time = html.escape(str(event_time))
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
        unsafe_allow_html=True
    )


# ============================================================
# CREATE ALERTS
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
                "type": "oxygen",
                "risk": risk,
                "title": "Low Oxygen Saturation",
                "value": f"{latest_low_value:.1f}%",
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
                "time": latest_low[
                    "recorded_at"
                ]
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
            ]
        )

        patient_alerts.append(
            {
                "type": "blood_pressure",
                "risk": risk,
                "title": "Abnormal Blood Pressure",
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
                "time": latest_bp_time
            }
        )


# ------------------------------------------------------------
# RAW SIMULATOR ALERT EVENTS
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
            "type": "simulator",
            "risk": "LOW",
            "title": "Simulator Alert Event",
            "value": (
                f"{len(alert_events)} event(s)"
            ),
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
            "time": latest_simulator_alert[
                "recorded_at"
            ]
        }
    )


# ------------------------------------------------------------
# OVERALL PATIENT RISK
# ------------------------------------------------------------

if patient_alerts:

    overall_risk = max(
        (
            alert["risk"]
            for alert in patient_alerts
        ),
        key=risk_priority
    )

else:

    overall_risk = "LOW"


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [5, 1]
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
        unsafe_allow_html=True
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
        unsafe_allow_html=True
    )


st.markdown(
    f"### Patient {selected_patient}"
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(
    4
)


# ------------------------------------------------------------
# OXYGEN SATURATION KPI
# ------------------------------------------------------------

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
            f"{sat_delta:+.1f}%"
        )

    else:

        kpi1.metric(
            "Oxygen Saturation",
            f"{latest_sat:.1f}%"
        )

else:

    kpi1.metric(
        "Oxygen Saturation",
        "No data"
    )


# ------------------------------------------------------------
# BLOOD PRESSURE KPI
# ------------------------------------------------------------

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
        f"{latest_sys:.0f}/{latest_dia:.0f} mmHg"
    )

else:

    kpi2.metric(
        "Blood Pressure",
        "No data"
    )


# ------------------------------------------------------------
# ACTIVE ALERTS KPI
# ------------------------------------------------------------

kpi3.metric(
    "Active Alert Rules",
    len(patient_alerts)
)


# ------------------------------------------------------------
# RISK KPI
# ------------------------------------------------------------

kpi4.metric(
    "Risk Group",
    overall_risk
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
    "Alert"
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
        / len(expected_types)
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

overview_tab, signals_tab, lab_tab = st.tabs(
    [
        "Overview",
        "Signals",
        "Laboratory"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with overview_tab:

    st.subheader(
        "Patient Overview"
    )

    overview_left, overview_right = st.columns(
        [2, 1]
    )


    # --------------------------------------------------------
    # SATURATION GRAPH
    # --------------------------------------------------------

    with overview_left:

        st.markdown(
            "#### Oxygen Saturation"
        )

        if not saturation.empty:

            fig = px.line(
                saturation,
                x="recorded_at",
                y="measurement_value"
            )

            fig.update_traces(
                line=dict(
                    color="#47B7FF",
                    width=2.5
                )
            )

            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
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
                    b=20
                )
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
                use_container_width=True
            )

        else:

            st.info(
                "No saturation data available."
            )


    # --------------------------------------------------------
    # ALERT CENTER
    # --------------------------------------------------------

    with overview_right:

        risk_summary_html = (
            '<div class="risk-summary">'
            '<div class="risk-summary-title">'
            'Current patient risk group'
            '</div>'
            f'<div class="risk-summary-value">{overall_risk}</div>'
            '</div>'
        )

        st.markdown(
            risk_summary_html,
            unsafe_allow_html=True
)


        if patient_alerts:

            # High-risk alerts are displayed first.
            sorted_alerts = sorted(
                patient_alerts,
                key=lambda item: risk_priority(
                    item["risk"]
                ),
                reverse=True
            )

            for alert in sorted_alerts:

                render_alert_card(
                    title=alert["title"],
                    risk=alert["risk"],
                    value=alert["value"],
                    trigger=alert["trigger"],
                    context=alert["context"],
                    review=alert["review"],
                    event_time=alert["time"]
                )

        else:

            st.success(
                "No active rule-based alerts detected."
            )


        st.caption(
            "Risk groups and thresholds are "
            "rule-based demonstration logic applied "
            "to synthetic simulator data. They are "
            "not medical diagnoses."
        )


    # --------------------------------------------------------
    # RECENT MEASUREMENTS
    # --------------------------------------------------------

    st.subheader(
        "Recent Measurements"
    )

    recent = (
        patient_df[
            [
                "recorded_at",
                "measurement_type",
                "measurement_data"
            ]
        ]
        .sort_values(
            "recorded_at",
            ascending=False
        )
        .head(30)
    )

    recent.columns = [
        "Timestamp",
        "Measurement",
        "Value"
    ]

    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SIGNALS TAB
# ============================================================

with signals_tab:

    st.subheader(
        "Physiological Signals"
    )


    # --------------------------------------------------------
    # BLOOD PRESSURE
    # --------------------------------------------------------

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
                    width=2.5
                )
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
                    width=2.5
                )
            )
        )

        bp_fig.update_layout(
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
                b=20
            )
        )

        bp_fig.update_xaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        bp_fig.update_yaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        st.plotly_chart(
            bp_fig,
            use_container_width=True
        )

    else:

        st.info(
            "No complete blood pressure data available."
        )


    # --------------------------------------------------------
    # ECG
    # --------------------------------------------------------

    st.markdown(
        "#### ECG Signal"
    )

    if not ecg.empty:

        ecg_fig = px.line(
            ecg.tail(500),
            x="recorded_at",
            y="measurement_value"
        )

        ecg_fig.update_traces(
            line=dict(
                color="#4EBEFF",
                width=2
            )
        )

        ecg_fig.update_layout(
            height=430,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
                b=20
            )
        )

        ecg_fig.update_xaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        ecg_fig.update_yaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        st.plotly_chart(
            ecg_fig,
            use_container_width=True
        )

    else:

        st.info(
            "No ECG data available."
        )


    # --------------------------------------------------------
    # OXYGEN SATURATION
    # --------------------------------------------------------

    st.markdown(
        "#### Oxygen Saturation"
    )

    if not saturation.empty:

        sat_fig = px.line(
            saturation,
            x="recorded_at",
            y="measurement_value"
        )

        sat_fig.update_traces(
            line=dict(
                color="#8BD8FF",
                width=2.5
            )
        )

        sat_fig.update_layout(
            height=360,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
                b=20
            )
        )

        sat_fig.update_xaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        sat_fig.update_yaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        st.plotly_chart(
            sat_fig,
            use_container_width=True
        )

    else:

        st.info(
            "No oxygen saturation data available."
        )


# ============================================================
# LABORATORY TAB
# ============================================================

with lab_tab:

    st.subheader(
        "Laboratory Measurements"
    )

    lab1, lab2, lab3 = st.columns(
        3
    )


    # --------------------------------------------------------
    # CHOLESTEROL
    # --------------------------------------------------------

    if not cholesterol.empty:

        latest_cholesterol = (
            cholesterol.iloc[-1][
                "measurement_value"
            ]
        )

        lab1.metric(
            "Cholesterol",
            f"{latest_cholesterol:.2f}"
        )

    else:

        lab1.metric(
            "Cholesterol",
            "No data"
        )


    # --------------------------------------------------------
    # RED BLOOD CELLS
    # --------------------------------------------------------

    if not rbc.empty:

        latest_rbc = (
            rbc.iloc[-1][
                "measurement_value"
            ]
        )

        lab2.metric(
            "Red Blood Cells",
            f"{latest_rbc:.2f}"
        )

    else:

        lab2.metric(
            "Red Blood Cells",
            "No data"
        )


    # --------------------------------------------------------
    # WHITE BLOOD CELLS
    # --------------------------------------------------------

    if not wbc.empty:

        latest_wbc = (
            wbc.iloc[-1][
                "measurement_value"
            ]
        )

        lab3.metric(
            "White Blood Cells",
            f"{latest_wbc:.2f}"
        )

    else:

        lab3.metric(
            "White Blood Cells",
            "No data"
        )


    st.divider()


    # --------------------------------------------------------
    # LAB HISTORY
    # --------------------------------------------------------

    lab_data = patient_df[
        patient_df[
            "measurement_type"
        ].isin(
            [
                "Cholesterol",
                "RedBloodCells",
                "WhiteBloodCells"
            ]
        )
        &
        patient_df[
            "measurement_value"
        ].notna()
        ].copy()


    if not lab_data.empty:

        st.markdown(
            "#### Laboratory History"
        )

        lab_fig = px.line(
            lab_data,
            x="recorded_at",
            y="measurement_value",
            color="measurement_type",
            markers=True
        )

        lab_fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
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
                b=20
            )
        )

        lab_fig.update_xaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        lab_fig.update_yaxes(
            gridcolor=
            "rgba(120,180,220,0.08)"
        )

        st.plotly_chart(
            lab_fig,
            use_container_width=True
        )

    else:

        st.info(
            "No laboratory data available."
        )