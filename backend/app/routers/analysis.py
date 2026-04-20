from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import MachineRecord

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

ALLOWED_SENSORS = {
    "air_temperature_k": "Air temperature [K]",
    "process_temperature_k": "Process temperature [K]",
    "rotational_speed_rpm": "Rotational speed [rpm]",
    "torque_nm": "Torque [Nm]",
    "tool_wear_min": "Tool wear [min]",
}


@router.get("/records")
def get_analysis_records(
    dataset_id: int,
    sensor: str,
    type_filter: str | None = Query(default=None),
    failure: int | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=3000),
    db: Session = Depends(get_db),
):
    if sensor not in ALLOWED_SENSORS:
        raise HTTPException(status_code=400, detail="허용되지 않은 sensor 값입니다.")

    query = db.query(MachineRecord).filter(MachineRecord.dataset_id == dataset_id)

    if type_filter and type_filter != "all":
        query = query.filter(MachineRecord.type == type_filter)

    if failure is not None:
        query = query.filter(MachineRecord.machine_failure == failure)

    total_filtered_count = query.count()

    if total_filtered_count == 0:
        raise HTTPException(status_code=404, detail="조건에 맞는 데이터가 없습니다.")

    records = query.order_by(MachineRecord.id.asc()).limit(limit).all()

    values = []
    for i, record in enumerate(records):
        sensor_value = getattr(record, sensor, None)

        if sensor_value is None:
            continue

        values.append(
            {
                "index": record.id if record.id is not None else i + 1,
                "value": float(sensor_value),
                "type": record.type,
                "machine_failure": record.machine_failure,
            }
        )

    if not values:
        raise HTTPException(status_code=404, detail="선택한 센서값 데이터가 없습니다.")

    numeric_values = [item["value"] for item in values]

    return {
        "dataset_id": dataset_id,
        "sensor": sensor,
        "sensor_label": ALLOWED_SENSORS[sensor],
        "type_filter": type_filter if type_filter else "all",
        "failure_filter": failure if failure is not None else "all",
        "total_filtered_count": total_filtered_count,
        "returned_count": len(values),
        "stats": {
            "min": round(min(numeric_values), 4),
            "max": round(max(numeric_values), 4),
            "avg": round(sum(numeric_values) / len(numeric_values), 4),
        },
        "values": values,
    }