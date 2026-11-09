from fastapi.testclient import TestClient

from api.main import app
from api.routers import prediction

client = TestClient(app)


def test_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_predict_anomaly(monkeypatch):
    def mock_predict_anomaly(
            features,
    ):
        return {
            "is_outlier": False,
            "anomaly_score": -0.123,
        }

    monkeypatch.setattr(
        prediction,
        "predict_anomaly",
        mock_predict_anomaly,
    )

    payload = {
        "saturation_mean": 97.0,
        "saturation_std": 1.2,
        "systolicpressure_mean": 120.0,
        "diastolicpressure_mean": 80.0,
        "low_saturation_rate": 0.02,
        "abnormal_systolic_rate": 0.05,
        "abnormal_diastolic_rate": 0.03,
        "zscore_anomaly_rate": 0.04,
        "high_zscore_count": 1,
        "max_abs_zscore": 2.5,
    }

    response = client.post(
        "/predict/anomaly",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_outlier"] is False
    assert data["anomaly_score"] == -0.123


def test_predict_anomaly_validation_error():
    payload = {
        "saturation_mean": 97.0,
    }

    response = client.post(
        "/predict/anomaly",
        json=payload,
    )

    assert response.status_code == 422


def test_predict_anomaly_model_missing(
        monkeypatch,
):
    def mock_predict_anomaly(
            features,
    ):
        raise FileNotFoundError(
            "model not found"
        )

    monkeypatch.setattr(
        prediction,
        "predict_anomaly",
        mock_predict_anomaly,
    )

    payload = {
        "saturation_mean": 97.0,
        "saturation_std": 1.2,
        "systolicpressure_mean": 120.0,
        "diastolicpressure_mean": 80.0,
        "low_saturation_rate": 0.02,
        "abnormal_systolic_rate": 0.05,
        "abnormal_diastolic_rate": 0.03,
        "zscore_anomaly_rate": 0.04,
        "high_zscore_count": 1,
        "max_abs_zscore": 2.5,
    }

    response = client.post(
        "/predict/anomaly",
        json=payload,
    )

    assert response.status_code == 503

    data = response.json()

    assert data["detail"] == "model not found"