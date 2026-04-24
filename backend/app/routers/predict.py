from fastapi import APIRouter, HTTPException
from app.ml.predictor import predict_failure, get_model_metrics


from app.schemas import PredictRequest, PredictResponse
from app.ml.predictor import predict_failure

router = APIRouter(prefix="/api", tags=["predict"])

@router.post("/predict", response_model = PredictResponse)
def predict_machine_failure(payload: PredictRequest):
    try:
        result = predict_failure(payload.model_dump())
        return result
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="학습된 모델이 없습니다. 먼저 train.py를 실행해 모델을 생성해주세요.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 실패: {str(e)}")
    

@router.get("/model/metrics")
def read_model_metrics():
    try:
        return get_model_metrics()
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="학습된 모델이 없습니다. 먼저 train.py를 실행해 모델을 생성하세요.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 metric 조회 실패: {str(e)}")