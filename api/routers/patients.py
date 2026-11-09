from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import PatientAnalyticsResponse, PatientResponse
from api.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])
Database = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[PatientResponse])
def patients(db: Database):
    return patient_service.list_patients(db)


@router.get("/{patient_id}/analytics", response_model=PatientAnalyticsResponse)
def analytics(patient_id: Annotated[int, Path(gt=0)], db: Database):
    result = patient_service.get_patient_analytics(db, patient_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return result
