import subprocess
import sys
import time
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


PIPELINE_STEPS = [
    {
        "name":
            "Rolling statistics",

        "script":
            "analytics/rolling_statistics.py",
    },

    {
        "name":
            "Z-score anomaly detection",

        "script":
            "analytics/zscore_anomaly_detection.py",
    },

    {
        "name":
            "Patient feature engineering",

        "script":
            "analytics/feature_engineering.py",
    },

    {
        "name":
            "KMeans clustering",

        "script":
            "analytics/clustering.py",
    },

    {
        "name":
            "Isolation Forest",

        "script":
            "analytics/isolation_forest.py",
    },

    {
        "name":
            "PCA analysis",

        "script":
            "analytics/pca_analysis.py",
    },

    {
        "name":
            "Cluster analysis",

        "script":
            "analytics/cluster_analysis.py",
    },
]


# ============================================================
# HELPERS
# ============================================================

def print_header():
    print()
    print("=" * 70)
    print("CARDIOPULSE ANALYTICS PIPELINE")
    print("=" * 70)

    print(
        f"Project root: "
        f"{PROJECT_ROOT}"
    )

    print(
        f"Python: "
        f"{sys.executable}"
    )

    print("=" * 70)
    print()


def validate_scripts():

    missing_scripts = []

    for step in PIPELINE_STEPS:

        script_path = (
                PROJECT_ROOT
                / step["script"]
        )

        if not script_path.exists():

            missing_scripts.append(
                str(script_path)
            )


    if missing_scripts:

        print(
            "Pipeline cannot start."
        )

        print(
            "Missing scripts:"
        )

        for script in missing_scripts:

            print(
                f" - {script}"
            )

        return False


    return True


def run_step(
        index,
        total_steps,
        step,
):

    name = step["name"]

    script_path = (
            PROJECT_ROOT
            / step["script"]
    )


    print()
    print("-" * 70)

    print(
        f"[{index}/{total_steps}] "
        f"{name}"
    )

    print(
        f"Script: "
        f"{step['script']}"
    )

    print("-" * 70)
    print()


    start_time = (
        time.perf_counter()
    )


    try:

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
            ],

            cwd=PROJECT_ROOT,

            check=False,
        )


    except Exception as error:

        elapsed = (
                time.perf_counter()
                - start_time
        )


        return {
            "name":
                name,

            "status":
                "FAILED",

            "elapsed":
                elapsed,

            "return_code":
                None,

            "error":
                str(error),
        }


    elapsed = (
            time.perf_counter()
            - start_time
    )


    if result.returncode == 0:

        status = "OK"

    else:

        status = "FAILED"


    return {
        "name":
            name,

        "status":
            status,

        "elapsed":
            elapsed,

        "return_code":
            result.returncode,

        "error":
            None,
    }


def print_summary(
        results,
        total_elapsed,
):

    print()
    print()
    print("=" * 70)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 70)


    for index, result in enumerate(
            results,
            start=1,
    ):

        name = result["name"]
        status = result["status"]
        elapsed = result["elapsed"]

        print(
            f"[{index}/{len(PIPELINE_STEPS)}] "
            f"{name:<32} "
            f"{status:<8} "
            f"{elapsed:.2f} sec"
        )


    print("-" * 70)

    print(
        f"Total elapsed time: "
        f"{total_elapsed:.2f} sec"
    )


    failed_steps = [
        result
        for result in results
        if result["status"] != "OK"
    ]


    if failed_steps:

        print()

        print(
            "Pipeline status: FAILED"
        )

        print()

        for result in failed_steps:

            print(
                f"Failed step: "
                f"{result['name']}"
            )

            if (
                    result[
                        "return_code"
                    ]
                    is not None
            ):

                print(
                    f"Return code: "
                    f"{result['return_code']}"
                )

            if result["error"]:

                print(
                    f"Error: "
                    f"{result['error']}"
                )

    else:

        print(
            "Pipeline status: SUCCESS"
        )


    print("=" * 70)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print_header()


    if not validate_scripts():

        sys.exit(1)


    pipeline_start = (
        time.perf_counter()
    )


    results = []


    total_steps = len(
        PIPELINE_STEPS
    )


    for index, step in enumerate(
            PIPELINE_STEPS,
            start=1,
    ):

        result = run_step(
            index,
            total_steps,
            step,
        )


        results.append(
            result
        )


        if result["status"] != "OK":

            print()

            print(
                f"Pipeline stopped because "
                f"'{result['name']}' failed."
            )

            break


    total_elapsed = (
            time.perf_counter()
            - pipeline_start
    )


    print_summary(
        results,
        total_elapsed,
    )


    pipeline_failed = any(
        result["status"] != "OK"
        for result in results
    )


    if pipeline_failed:

        sys.exit(1)


    sys.exit(0)


if __name__ == "__main__":
    main()