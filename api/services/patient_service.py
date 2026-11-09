from sqlalchemy import text
from sqlalchemy.orm import Session


def list_patients(db: Session):
    return (
        db.execute(
            text("SELECT DISTINCT patient_id FROM measurements ORDER BY patient_id")
        )
        .mappings()
        .all()
    )


def get_patient_analytics(db: Session, patient_id: int):
    return (
        db.execute(
            text("""
        SELECT patients.patient_id, pc.cluster_id, pc.distance_to_centroid,
               pa.anomaly_score, pa.is_outlier, pa.outlier_rank,
               pca.pc1, pca.pc2, pf.zscore_anomaly_rate
        FROM (SELECT DISTINCT patient_id FROM measurements) patients
        LEFT JOIN patient_clusters pc ON pc.patient_id = patients.patient_id
        LEFT JOIN patient_anomalies pa ON pa.patient_id = patients.patient_id
        LEFT JOIN patient_pca pca ON pca.patient_id = patients.patient_id
        LEFT JOIN patient_features pf ON pf.patient_id = patients.patient_id
        WHERE patients.patient_id = :patient_id
    """),
            {"patient_id": patient_id},
        )
        .mappings()
        .one_or_none()
    )
