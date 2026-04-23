from pathlib import Path
import argparse
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.database import SessionLocal
from app.db_models import MachineRecord


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "predictive_maintenance_model.joblib"

FEATURE_COLUMNS = [
    "type",
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
]
TARGET_COLUMN = "machine_failure"


def load_dataframe(dataset_id: int) -> pd.DataFrame:
    db = SessionLocal()
    try:
        records = (
            db.query(MachineRecord)
            .filter(MachineRecord.dataset_id == dataset_id)
            .all()
        )

        if not records:
            raise ValueError(f"dataset_id={dataset_id} 에 해당하는 데이터가 없습니다.")

        rows = []
        for record in records:
            rows.append(
                {
                    "type": record.type,
                    "air_temperature_k": record.air_temperature_k,
                    "process_temperature_k": record.process_temperature_k,
                    "rotational_speed_rpm": record.rotational_speed_rpm,
                    "torque_nm": record.torque_nm,
                    "tool_wear_min": record.tool_wear_min,
                    "machine_failure": record.machine_failure,
                }
            )

        df = pd.DataFrame(rows)
        df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])

        return df
    finally:
        db.close()


def train_model(dataset_id: int):
    df = load_dataframe(dataset_id)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    class_counts = y.value_counts()
    if len(class_counts) < 2:
        raise ValueError("데이터에 클래스가 1종류뿐입니다. 정상/고장 데이터가 모두 필요합니다.")
    if class_counts.min() < 10:
        raise ValueError(
            f"클래스별 샘플 수가 너무 적습니다 (최소 {class_counts.min()}개). "
            "stratified split을 위해 클래스별 최소 10개 이상이 필요합니다."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    categorical_features = ["type"]
    numeric_features = [
        "air_temperature_k",
        "process_temperature_k",
        "rotational_speed_rpm",
        "torque_nm",
        "tool_wear_min",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    bundle = {
        "model": pipeline,
        "feature_columns": FEATURE_COLUMNS,
        "dataset_id": dataset_id,
        "metrics": metrics,
    }

    joblib.dump(bundle, MODEL_PATH)

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", type=int, required=True)
    args = parser.parse_args()

    metrics = train_model(args.dataset_id)

    print("학습 완료")
    print(f"모델 저장 위치: {MODEL_PATH}")
    print("평가 지표:")
    for key, value in metrics.items():
        print(f"- {key}: {value}")