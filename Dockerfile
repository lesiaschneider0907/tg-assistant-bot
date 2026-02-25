FROM python:3.12-slim

WORKDIR /app

# сначала копируем только requirements чтобы кешировать слой с зависимостями
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь код
COPY . .

CMD ["python", "-m", "bot.main"]
```

Теперь заполни `.env` реальными значениями — придумай любые для локальной разработки:
```
BOT_TOKEN=сюда_токен_от_botfather
DB_HOST=db
DB_PORT=5432
DB_NAME=assistant
DB_USER=postgres
DB_PASSWORD=придумай_любой_пароль