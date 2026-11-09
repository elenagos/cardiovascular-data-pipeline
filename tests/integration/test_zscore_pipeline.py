import pandas as pd
import pytest
from sqlalchemy import text

from analytics.zscore_anomaly_detection import (
    build_zscore_analysis,
    load_rolling_statistics,
    save_zscore_analysis,
)


@pytest.mark.integration
def test_zscore_pipeline_with_real_postgres(
        integration_engine,
):
    rolling_df = pd.DataFrame(
        [
            {
                "measurement_id": 1,
                "patient_id": 1,
                "recorded_at": "2026-10-29T10:00:00+00:00",
                "measurement_type": "SystolicPressure",
                "measurement_value": 120.0,
                "rolling_count": 4,
                "rolling_mean": 120.0,
                "rolling_std": 2.0,
                "rolling_min": 118.0,
                "rolling_max": 122.0,
                "window_size": 5,
                "updated_at": "2026-10-29T10:01:00+00:00",
            },
            {
                "measurement_id": 2,
                "patient_id": 1,
                "recorded_at": "2026-10-29T10:02:00+00:00",
                "measurement_type": "SystolicPressure",
                "measurement_value": 140.0,
                "rolling_count": 4,
                "rolling_mean": 120.0,
                "rolling_std": 5.0,
                "rolling_min": 115.0,
                "rolling_max": 125.0,
                "window_size": 5,
                "updated_at": "2026-10-29T10:03:00+00:00",
            },
        ]
    )

    rolling_df.to_sql(
        "rolling_statistics",
        integration_engine,
        if_exists="append",
        index=False,
    )

    loaded_df = load_rolling_statistics(
        integration_engine
    )

    assert len(loaded_df) == 2

    result = build_zscore_analysis(
        loaded_df
    )

    save_zscore_analysis(
        result,
        integration_engine,
    )

    with integration_engine.connect() as connection:
        saved_rows = connection.execute(
            text(
                """
                SELECT
                    measurement_id,
                    z_score,
                    is_anomaly,
                    anomaly_level
                FROM zscore_analysis
                ORDER BY measurement_id
                """
            )
        ).mappings().all()

    assert len(saved_rows) == 2

    assert saved_rows[0]["is_anomaly"] is False

    assert saved_rows[1]["is_anomaly"] is True

    assert saved_rows[1]["z_score"] == pytest.approx(
        4.0
    )

    assert saved_rows[1]["anomaly_level"] == "HIGH"