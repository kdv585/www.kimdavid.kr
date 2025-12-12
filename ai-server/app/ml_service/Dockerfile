FROM python:3.11-slim

WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK 데이터 다운로드
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('averaged_perceptron_tagger_eng', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('omw-1.4', quiet=True)"

# app 디렉토리 복사 (train.csv, test.csv 포함)
# Dockerfile context는 app/ml_service/이므로
# app/ml_service/app/ -> /app/app/
# app/ml_service/common/ -> /app/common/
COPY app/ ./app/
COPY common/ ./common/

# main.py 복사
COPY main.py .

EXPOSE 9003

# 환경변수로 포트 설정 가능 (기본값 9003)
ENV PORT=9003

# PYTHONPATH 설정
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9003"]
