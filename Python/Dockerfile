FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
COPY bucket-read.json .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py","--port","8080"]
