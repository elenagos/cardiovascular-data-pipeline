import pandas as pd
import pytest
from sqlalchemy import text

from analytics.rolling_statistics import (
    build_rolling_statistics,
    clean_measurements,
    load_measurements,
    save_rolling_statistics,
)


@pytest.mark.integration
def test_rolling_statistics_with_real_postgres(
        integration_engine,
):
    input_df = pd.DataFrame(
        [
            {
                "patient_id": 1,
                "recorded_at": "2026-10-29T10:00:00+00:00",
                "measurement_type": "SystolicPressure",
                "measurement_data": "120",
            },
            {
                "patient_id": 1,
                "recorded_at": "2026-10-29T10:01:00+00:00",
                "measurement_type": "SystolicPressure",
                "measurement_data": "122",
            },
            {
                "patient_id": 1,
                "recorded_at": "2026-10-29T10:02:00+00:00",
                "measurement_type": "SystolicPressure",
                "measurement_data": "124",
            },
            {
                "patient_id": 1,
                "recorded_at": "2026-10-29T10:03:00+00:00",
                "measurement_type": "SystolicPressure",
                "measurement_data": "126",
            },
        ]
    )

    input_df.to_sql(
        "measurements",
        integration_engine,
        if_exists="append",
        index=False,
    )

    raw_df = load_measurements(
        integration_engine
    )

    assert len(raw_df) == 4

    clean_df = clean_measurements(
        raw_df
    )

    assert len(clean_df) == 4

    result = build_rolling_statistics(
        clean_df
    )

    assert len(result) == 4

    save_rolling_statistics(
        result,
        integration_engine,
    )

    with integration_engine.connect() as connection:
        saved_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM rolling_statistics
                """
            )
        ).scalar_one()

    assert saved_count == 4