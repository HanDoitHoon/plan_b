from typing import Literal
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    type: Literal["L", "M", "H"]
    air_temperature_k: float = Field(..., gt=0)
    process_temperature_k: float = Field(..., gt=0)
    rotational_speed_rpm: float = Field(..., gt=0)
    torque_nm: float = Field(..., ge=0)
    tool_wear_min: float = Field(..., ge=0)


class PredictResponse(BaseModel):
    predicted_failure: int
    failure_probability: float
    label: str
