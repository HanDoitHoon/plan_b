from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import Dataset, MachineRecord

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


COLUMN_MAP = {
    "UDI": "uid",
    "Product ID": "product_id",
    "Type": "type",
    "Air temperature [K]": "air_temperature_k",
    "Process temperature [K]": "process_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": "machine_failure",
    "TWF": "twf",
    "HDF": "hdf",
    "PWF": "pwf",
    "OSF": "osf",
    "RNF": "rnf",
}


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")

    content = await file.read()

    try:
        df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV 읽기 실패: {str(e)}")

    missing_columns = [col for col in COLUMN_MAP.keys() if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"필수 컬럼 누락: {missing_columns}",
        )

    dataset = Dataset(
        file_name=file.filename,
        row_count=len(df),
        column_count=len(df.columns),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    df = df.rename(columns=COLUMN_MAP)
    df = df.where(pd.notnull(df), None)

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "dataset_id": dataset.id,
                "uid": int(row["uid"]) if row["uid"] is not None else None,
                "product_id": row["product_id"],
                "type": row["type"],
                "air_temperature_k": float(row["air_temperature_k"]) if row["air_temperature_k"] is not None else None,
                "process_temperature_k": float(row["process_temperature_k"]) if row["process_temperature_k"] is not None else None,
                "rotational_speed_rpm": float(row["rotational_speed_rpm"]) if row["rotational_speed_rpm"] is not None else None,
                "torque_nm": float(row["torque_nm"]) if row["torque_nm"] is not None else None,
                "tool_wear_min": float(row["tool_wear_min"]) if row["tool_wear_min"] is not None else None,
                "machine_failure": int(row["machine_failure"]) if row["machine_failure"] is not None else 0,
                "twf": int(row["twf"]) if row["twf"] is not None else 0,
                "hdf": int(row["hdf"]) if row["hdf"] is not None else 0,
                "pwf": int(row["pwf"]) if row["pwf"] is not None else 0,
                "osf": int(row["osf"]) if row["osf"] is not None else 0,
                "rnf": int(row["rnf"]) if row["rnf"] is not None else 0,
            }
        )

    db.bulk_insert_mappings(MachineRecord, records)
    db.commit()

    return {
        "message": "Upload success",
        "dataset_id": dataset.id,
        "file_name": dataset.file_name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
    }


@router.get("")
def get_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).order_by(Dataset.id.desc()).all()

    return [
        {
            "id": d.id,
            "file_name": d.file_name,
            "row_count": d.row_count,
            "column_count": d.column_count,
            "uploaded_at": d.uploaded_at,
        }
        for d in datasets
    ]