import os
import re
import sys

import pandas as pd
from sqlalchemy import create_engine

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://localhost/cardio_pipeline",
)


ALLOWED_MEASUREMENT_TYPES = {
    "Alert",
    "Cholesterol",
    "DiastolicPressure",
    "ECG",
    "RedBloodCells",
    "Saturation",
    "SystolicPressure",
    "HeartRate",
    "WhiteBloodCells",
}


NUMERIC_MEASUREMENT_TYPES = {
    "Cholesterol",
    "DiastolicPressure",
    "ECG",
    "RedBloodCells",
    "Saturation",
    "SystolicPressure",
    "HeartRate",
    "WhiteBloodCells",
}


# These are conservative data-quality bounds.
#
# They are NOT diagnostic or clinical thresholds.
PLAUSIBILITY_BOUNDS = {
    "Saturation": {
        "min": 0.0,
        "max": 100.0,
    },
    "SystolicPressure": {
        "min": 0.0,
        "max": 300.0,
    },
    "DiastolicPressure": {
        "min": 0.0,
        "max": 300.0,
    },
}


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

def load_measurements(engine):
    query = """
    SELECT
        id,
        patient_id,
        recorded_at,
        measurement_type,
        measurement_data
    FROM measurements
    ORDER BY id
    """

    return pd.read_sql(
        query,
        engine,
    )


# ============================================================
# NUMERIC EXTRACTION
# ============================================================

def extract_numeric_value(value):
    if pd.isna(value):
        return None

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        str(value),
    )

    if match is None:
        return None

    return float(
        match.group(0)
    )


# ============================================================
# QUALITY CHECK HELPERS
# ============================================================

def check_non_empty(df):
    invalid_count = int(
        len(df) == 0
    )

    return {
        "name": "Dataset is not empty",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_patient_ids(df):
    invalid = (
            df["patient_id"].isna()
            |
            (
                    df["patient_id"]
                    <= 0
            )
    )

    invalid_count = int(
        invalid.sum()
    )

    return {
        "name": "Valid patient IDs",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_recorded_at(df):
    invalid_count = int(
        df[
            "recorded_at"
        ]
        .isna()
        .sum()
    )

    return {
        "name": "recorded_at is present",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_measurement_types(df):
    missing = (
            df[
                "measurement_type"
            ]
            .isna()
            |
            (
                    df[
                        "measurement_type"
                    ]
                    .astype(str)
                    .str.strip()
                    == ""
            )
    )

    unsupported = (
        ~df[
            "measurement_type"
        ]
        .isin(
            ALLOWED_MEASUREMENT_TYPES
        )
    )

    invalid = (
            missing
            |
            unsupported
    )

    invalid_count = int(
        invalid.sum()
    )

    return {
        "name": "Measurement types are valid",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_measurement_data(df):
    invalid = (
            df[
                "measurement_data"
            ]
            .isna()
            |
            (
                    df[
                        "measurement_data"
                    ]
                    .astype(str)
                    .str.strip()
                    == ""
            )
    )

    invalid_count = int(
        invalid.sum()
    )

    return {
        "name": "Measurement data is present",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_duplicate_ids(df):
    invalid_count = int(
        df[
            "id"
        ]
        .duplicated()
        .sum()
    )

    return {
        "name": "No duplicate measurement IDs",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_numeric_measurements(df):
    numeric_df = (
        df[
            df[
                "measurement_type"
            ]
            .isin(
                NUMERIC_MEASUREMENT_TYPES
            )
        ]
            .copy()
    )

    numeric_df[
        "parsed_value"
    ] = (
        numeric_df[
            "measurement_data"
        ]
        .apply(
            extract_numeric_value
        )
    )

    invalid_count = int(
        numeric_df[
            "parsed_value"
        ]
        .isna()
        .sum()
    )

    return {
        "name": "Numeric measurements are parseable",
        "status":
            "PASS"
            if invalid_count == 0
            else "FAIL",
        "invalid_count": invalid_count,
        "critical": True,
    }


def check_plausibility(df):
    warning_count = 0

    for (
            measurement_type,
            bounds,
    ) in (
            PLAUSIBILITY_BOUNDS.items()
    ):
        subset = (
            df[
                df[
                    "measurement_type"
                ]
                == measurement_type
                ]
            .copy()
        )

        if subset.empty:
            continue

        subset[
            "parsed_value"
        ] = (
            subset[
                "measurement_data"
            ]
            .apply(
                extract_numeric_value
            )
        )

        outside_bounds = (
                subset[
                    "parsed_value"
                ]
                .notna()
                &
                (
                        (
                                subset[
                                    "parsed_value"
                                ]
                                < bounds[
                                    "min"
                                ]
                        )
                        |
                        (
                                subset[
                                    "parsed_value"
                                ]
                                > bounds[
                                    "max"
                                ]
                        )
                )
        )

        warning_count += int(
            outside_bounds.sum()
        )

    return {
        "name": "Values within plausibility bounds",
        "status":
            "PASS"
            if warning_count == 0
            else "WARN",
        "invalid_count": warning_count,
        "critical": False,
    }


# ============================================================
# RUN CHECKS
# ============================================================

def run_quality_checks(df):
    checks = [
        check_non_empty(
            df
        ),
        check_patient_ids(
            df
        ),
        check_recorded_at(
            df
        ),
        check_measurement_types(
            df
        ),
        check_measurement_data(
            df
        ),
        check_duplicate_ids(
            df
        ),
        check_numeric_measurements(
            df
        ),
        check_plausibility(
            df
        ),
    ]

    return checks


# ============================================================
# SUMMARY
# ============================================================

def print_quality_report(
        df,
        checks,
):
    print()
    print(
        "=" * 70
    )

    print(
        "CARDIOPULSE DATA QUALITY REPORT"
    )

    print(
        "=" * 70
    )

    print(
        f"Rows checked: "
        f"{len(df):,}"
    )

    print()

    for check in checks:
        print(
            f"[{check['status']}] "
            f"{check['name']}"
        )

        print(
            f"    invalid rows: "
            f"{check['invalid_count']:,}"
        )

    critical_failures = [
        check
        for check in checks
        if (
                check[
                    "critical"
                ]
                and
                check[
                    "status"
                ]
                == "FAIL"
        )
    ]

    warnings = [
        check
        for check in checks
        if check[
               "status"
           ] == "WARN"
    ]

    print()
    print(
        "-" * 70
    )

    print(
        f"Critical failures: "
        f"{len(critical_failures)}"
    )

    print(
        f"Warnings: "
        f"{len(warnings)}"
    )

    if critical_failures:
        overall_status = (
            "FAILED"
        )
    elif warnings:
        overall_status = (
            "PASSED WITH WARNINGS"
        )
    else:
        overall_status = (
            "PASSED"
        )

    print(
        f"Overall status: "
        f"{overall_status}"
    )

    print(
        "=" * 70
    )

    return (
            len(
                critical_failures
            )
            == 0
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
        "Loading measurements "
        "for data quality checks..."
    )

    df = (
        load_measurements(
            engine
        )
    )

    checks = (
        run_quality_checks(
            df
        )
    )

    passed = (
        print_quality_report(
            df,
            checks,
        )
    )

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()