from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PatientResponse(BaseModel):
    patient_id: int


class PatientAnalyticsResponse(BaseModel):
    patient_id: int

    cluster_id: int | None = None
    distance_to_centroid: float | None = None

    anomaly_score: float | None = None
    is_outlier: bool | None = None
    outlier_rank: int | None = None

    zscore_anomaly_count: int | None = None
    zscore_anomaly_rate: float | None = None
    high_zscore_count: int | None = None
    max_abs_zscore: float | None = None


class AnomalyPredictionRequest(BaseModel):
    saturation_mean: float
    saturation_std: float

    systolicpressure_mean: float
    diastolicpressure_mean: float

    low_saturation_rate: float
    abnormal_systolic_rate: float
    abnormal_diastolic_rate: float

    zscore_anomaly_rate: float
    high_zscore_count: int
    max_abs_zscore: float


class AnomalyPredictionResponse(BaseModel):
    is_outlier: bool
    anomaly_score: float