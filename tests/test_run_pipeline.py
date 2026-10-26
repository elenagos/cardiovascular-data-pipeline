from analytics.run_pipeline import (
    PIPELINE_STEPS,
    PROJECT_ROOT,
    validate_scripts,
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()


def test_pipeline_contains_expected_steps():
    names = [
        step["name"]
        for step in PIPELINE_STEPS
    ]

    assert "Rolling statistics" in names
    assert "Z-score anomaly detection" in names
    assert "Patient feature engineering" in names
    assert "KMeans clustering" in names
    assert "Isolation Forest" in names
    assert "PCA analysis" in names
    assert "Cluster analysis" in names


def test_pipeline_has_seven_steps():
    assert len(PIPELINE_STEPS) == 7


def test_pipeline_scripts_exist():
    for step in PIPELINE_STEPS:
        script_path = (
                PROJECT_ROOT
                / step["script"]
        )

        assert script_path.exists(), (
            f"Missing pipeline script: "
            f"{script_path}"
        )


def test_pipeline_validation_passes():
    assert validate_scripts() is True