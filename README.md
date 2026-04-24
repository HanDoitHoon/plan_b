# plan_b

--------------------------------------------------
### 프로젝트 소개 

웹앱 이해도를 늘리기 위해 **AI4I2020** Dataset을 시각화 하고 랜덤 포레스트 분류 모델(RandomForestClassifier)을 이용하여 예지보존 모델을 사용한 토이프로젝트 입니다. 
Chat GPT의 도움을 받아 필요한 기능을 생성하였고, Claude Code를 이용하여 프로젝트를 마무리 하였습니다.

#데이터셋 출처 - [AI4I 2020 링크](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)

--------------------------------------------------
###기술 스택

Backend    │ Python, FastAPI, SQLAlchemy 2.x 

Database   │ MySQL (PyMySQL) 

ML         │ scikit-learn, pandas, joblib 

Frontend   │ React (Vite) 

--------------------------------------------------

### 주요 기능 - 

--------------------------------------------------

### 실행 방법 - (.env.example 참고하라고 안내)
# 1. .env.example 내용 수정
    1) DataBase password 변경!
       
# 2. backend 실행 
    1) cd backend
    2) .venv\Scripts\activate
    필요 라이브러리 설치  pip install fastapi uvicorn sqlalchemy pymysql pandas scikit-learn joblib python-dotenv python-multipart
    3) python -m uvicorn app.main:app --reload
    4) http://127.0.0.1:8000 으로 열리고, http://127.0.0.1:8000/docs 에서 API 문서를 확인할 수 있습니다.
       
# 3. frontend 실행
    1) cd frontend
    2) npm run dev
    3) http://localhost:5173 으로 열립니다.
--------------------------------------------------

### 시스템 구조 - 아키텍처 다이어그램

--------------------------------------------------


### ML 모델 성능

Accuracy

F1-score

ROC-AUC 


