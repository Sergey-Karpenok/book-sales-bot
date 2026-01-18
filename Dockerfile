FROM python:3.13-slim

WORKDIR /app

# Установка пакетов
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY bot.py .

# Логи в stdout (docker logs)
CMD ["python", "bot.py"]

