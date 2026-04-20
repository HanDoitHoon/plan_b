from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float, ForeignKey, text
from app.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable= False)
    row_count = Column(Integer, nullable =False)
    column_count = Column(Integer, nullable=False)
    uploaded_at=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))



class MachineRecord(Base):
    __tablename__ = "machine_records"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    uid = Column(Integer)
    product_id = Column(String(50))
    type = Column(String(1))
    air_temperature_k = Column(Float)
    process_temperature_k = Column(Float)
    rotational_speed_rpm = Column(Float)
    torque_nm = Column(Float)
    tool_wear_min = Column(Float)
    machine_failure = Column(Integer)
    twf = Column(Integer)
    hdf = Column(Integer)
    pwf = Column(Integer)
    osf = Column(Integer)
    rnf = Column(Integer)


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    air_temperature_k = Column(Float)
    process_temperature_k = Column(Float)
    rotational_speed_rpm = Column(Float)
    torque_nm = Column(Float)
    tool_wear_min = Column(Float)
    predicted_failure = Column(Integer)
    failure_probability = Column(Float)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))