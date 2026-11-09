from fastapi import APIRouter, HTTPException

from api.schemas import (
    AnomalyPredictionRequest,
    AnomalyPredictionResponse,
)
from api.services.prediction_service import (
    predict_anomaly,
)

router = APIRouter(
    prefix="/predict",
    tags=["prediction"],
)


@router.post(
    "/anomaly",
    response_model=AnomalyPredictionResponse,
)
def predict_patient_anomaly(
        request: AnomalyPredictionRequest,
):
    try:
        result = predict_anomaly(
            request.model_dump()
        )

        return (
            AnomalyPredictionResponse(
                **result
            )
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=str(
                error
            ),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        ) from error