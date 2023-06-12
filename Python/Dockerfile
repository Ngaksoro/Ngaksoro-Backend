FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
COPY ngaksoro-key.json .
COPY main.py .
COPY data_soal.py .
COPY model.h5 .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py","--port","8080"]
