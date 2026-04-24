from pathlib import Path
import joblib
import pandas as pd
import threading

MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "predictive_maintenance_model.joblib"
_model_bundle = None
_lock = threading.Lock()


def load_model_bundle():
    global _model_bundle

    with _lock:
        if _model_bundle is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError("학습된 모델 파일이 없습니다. 먼저 train.py를 실행해주세요")
            _model_bundle = joblib.load(MODEL_PATH)

    return _model_bundle



def get_model_metrics():
    bundle = load_model_bundle()

    return {
        "dataset_id": bundle.get("dataset_id"),
        "feature_columns": bundle.get("feature_columns", []),
        "metrics": bundle.get("metrics", {}),
    }






def predict_failure(payload: dict):
    bundle = load_model_bundle()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    missing = [col for col in feature_columns if col not in payload]
    if missing:
        raise ValueError(f"입력값에 필수 피처가 없습니다: {missing}")

    input_df = pd.DataFrame([payload])[feature_columns]

    predicted = int(model.predict(input_df)[0])

    if hasattr(model, "predict_proba"):
        failure_probability = float(model.predict_proba(input_df)[0][1])
    else:
        failure_probability = float(predicted)

    return {
        "predicted_failure": predicted,
        "failure_probability": round(failure_probability, 4),
        "label": "고장" if predicted == 1 else "정상",
    }