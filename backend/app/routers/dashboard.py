from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import MachineRecord

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(dataset_id:int, db:Session = Depends(get_db)):
    total_samples = (
        db.query(func.count(MachineRecord.id))
        .filter(MachineRecord.dataset_id==dataset_id)
        .scalar()
    )

    if total_samples == 0:
        raise HTTPException(status_code=404, detail="해당 dataset_id의 데이터가 없습니다.")
    
    failure_samples = (
        db.query(func.count(MachineRecord.id))
        .filter(
            MachineRecord.dataset_id == dataset_id,
            MachineRecord.machine_failure == 1
        )
        .scalar()
    )

    normal_samples = total_samples - failure_samples
    failure_rate = failure_samples / total_samples

    return{
        "dataset_id" : dataset_id,
        "total_samples" : total_samples,
        "normal_samples" : normal_samples,
        "failure_samples" : failure_samples,
        "failure_rate": round(failure_rate, 4),
    }

@router.get("/distributions")
def get_distributions(dataset_id:int, db:Session = Depends(get_db)):
    total_samples = (
        db.query(func.count(MachineRecord.id))
        .filter(MachineRecord.dataset_id == dataset_id)
        .scalar()
    )

    if total_samples == 0:
        raise HTTPException(status_code=404, detail="해당 dataset_id의 데이터가 없습니다.")

    type_distribution_query = (
        db.query(
            MachineRecord.type,
            func.count(MachineRecord.id)
        )
        .filter(MachineRecord.dataset_id == dataset_id)
        .group_by(MachineRecord.type)
        .all()
    )

    type_distribution = [
        {"name" : row[0], "count" : row[1]}
        for row in type_distribution_query
    ]

    failure_type_counts = {
        "TWF": db.query(func.count(MachineRecord.id)).filter(
            MachineRecord.dataset_id == dataset_id,
            MachineRecord.twf == 1
        ).scalar(),
        
        "HDF" : db.query(func.count(MachineRecord.id)).filter(
            MachineRecord.dataset_id == dataset_id,
            MachineRecord.hdf == 1
        ).scalar(),

        "PWF" : db.query(func.count(MachineRecord.id)).filter(
            MachineRecord.dataset_id == dataset_id,
            MachineRecord.pwf == 1
        ).scalar(),

        "OSF" : db.query(func.count(MachineRecord.id)).filter(
            MachineRecord.dataset_id == dataset_id,
            MachineRecord.osf == 1
        ).scalar(),

        "RNF" : db.query(func.count(MachineRecord.id)).filter(
            MachineRecord.dataset_id == dataset_id,
            MachineRecord.rnf == 1
        ).scalar(),
    }

    failure_type_list = [
        {"name" : key, "count" : value}
        for key, value in failure_type_counts.items()
    ]

    return{
        "dataset_id" : dataset_id,
        "type_distribution" : type_distribution,
        "failure_type_counts" : failure_type_list,
    }