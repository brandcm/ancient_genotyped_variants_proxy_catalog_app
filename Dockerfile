FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:80", "--timeout", "150"]