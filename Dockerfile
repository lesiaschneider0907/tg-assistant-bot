FROM python:3.12-slim

WORKDIR /app

# сначала копируем только requirements чтобы кешировать слой с зависимостями
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь код
COPY . .

CMD ["python", "-m", "bot.main"]
