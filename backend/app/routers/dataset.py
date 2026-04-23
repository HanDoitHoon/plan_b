from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import insert as sa_insert
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import Dataset, MachineRecord

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

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

_RECORD_COLS = [
    "dataset_id", "uid", "product_id", "type",
    "air_temperature_k", "process_temperature_k",
    "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    "machine_failure", "twf", "hdf", "pwf", "osf", "rnf",
]


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="파일 크기가 50MB를 초과합니다.")

    try:
        df = pd.read_csv(BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="CSV 파일을 읽을 수 없습니다.")

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

    int_zero_cols = ["machine_failure", "twf", "hdf", "pwf", "osf", "rnf"]
    df[int_zero_cols] = df[int_zero_cols].fillna(0).astype(int)
    df = df.where(pd.notnull(df), None)
    df["dataset_id"] = dataset.id

    records = df[_RECORD_COLS].to_dict("records")

    db.execute(sa_insert(MachineRecord), records)
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


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="해당 dataset이 없습니다.")

    target_file_name = dataset.file_name

    try:
        deleted_records_count = (
            db.query(MachineRecord)
            .filter(MachineRecord.dataset_id == dataset_id)
            .delete(synchronize_session=False)
        )

        db.delete(dataset)
        db.commit()

        return {
            "message": "Dataset deleted successfully",
            "dataset_id": dataset_id,
            "file_name": target_file_name,
            "deleted_records_count": deleted_records_count,
        }

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="삭제 중 오류가 발생했습니다.")
