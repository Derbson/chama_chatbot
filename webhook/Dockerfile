FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webhook.py .

# Variável para facilitar execução
ENV FLASK_APP=webhook.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
