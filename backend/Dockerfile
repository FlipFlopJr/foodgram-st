FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./foodgram/ .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
