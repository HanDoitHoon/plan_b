# plan_b — 예지보전 웹 애플리케이션

AI4I 2020 데이터셋을 활용하여 설비 센서 데이터를 시각화하고,  
RandomForestClassifier로 고장 여부를 예측하는 풀스택 토이프로젝트입니다.

> 웹 애플리케이션 구조(FastAPI + React)에 대한 이해도를 높이기 위해 제작하였으며,  
> ChatGPT로 기능을 구현하고 Claude Code로 코드 품질을 개선하였습니다.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Python, FastAPI, SQLAlchemy 2.x |
| Database | MySQL (PyMySQL) |
| ML | scikit-learn, pandas, joblib |
| Frontend | React (Vite) |

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| CSV 업로드 | AI4I 2020 CSV 파일을 업로드하여 MySQL에 저장, 데이터셋 삭제 가능 |
| 대시보드 | 전체 샘플 수, 정상/고장 비율, 고장 유형별(TWF·HDF·PWF·OSF·RNF) 분포 시각화 |
| 센서 분석 | 5가지 센서값을 장비 타입(L/M/H)·고장 여부 필터로 조회 및 차트 확인 |
| ML 예측 | 센서값 입력 시 고장 여부와 고장 확률을 실시간 예측, 모델 평가 지표 표시 |

---

## 시스템 구조

```
[React Frontend]
      │
      │  REST API
      ▼
[FastAPI Backend]
   ├── /api/datasets    → CSV 업로드 / 삭제
   ├── /api/dashboard   → 통계 집계
   ├── /api/analysis    → 센서 데이터 조회
   └── /api/predict     → ML 추론
          │
          ├── [MySQL]            ← 원본 데이터 저장
          └── [model.joblib]     ← 학습된 모델 저장
```

**ML 파이프라인**

```
DB 데이터 로드
  → ColumnTransformer (OneHotEncoder + passthrough)
    → RandomForestClassifier (n_estimators=300, class_weight="balanced")
      → model.joblib 저장
        → /api/predict 요청 시 추론
```


## 데이터셋

[AI4I 2020 Predictive Maintenance Dataset](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) — UCI Machine Learning Repository

- 10,000행 / 14개 피처
- 고장률 약 3% (불균형 데이터)

---

## ML 모델 성능

| 지표 | 수치 |
|------|------|
| Accuracy | 0.9800 |
| Precision | 0.9118 |
| Recall | 0.4559 |
| F1-score | 0.6078 |
| ROC-AUC | 0.9585 |

> Recall이 낮은 이유: 고장률이 약 3%인 불균형 데이터셋 특성상 고장 샘플이 적습니다.  
> `class_weight="balanced"` 옵션으로 불균형을 보정하였습니다.

---

## 실행 방법

### 1. 환경 설정

`backend/.env.example`을 복사하여 `backend/.env` 파일을 생성하고, DB 정보를 수정합니다.

```bash
cp backend/.env.example backend/.env
```

```env
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=plan_b_db
```

### 2. Backend 실행

```bash
cd backend

# 라이브러리 설치 (최초 1회)
pip install fastapi uvicorn sqlalchemy pymysql pandas scikit-learn joblib python-dotenv python-multipart

# 서버 실행
python -m uvicorn app.main:app --reload
```

| 주소 | 설명 |
|------|------|
| http://127.0.0.1:8000 | API 서버 |
| http://127.0.0.1:8000/docs | Swagger API 문서 |

### 3. Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

→ http://localhost:5173

### 4. CSV 업로드

1. http://localhost:5173 접속
2. 데이터셋 페이지에서 AI4I 2020 CSV 파일 업로드

### 5. ML 모델 학습

```bash
cd backend
python -m app.ml.train --dataset-id 1
```

> `dataset-id`는 업로드한 데이터셋의 ID로 변경하세요. (업로드 후 화면에서 확인 가능)

---