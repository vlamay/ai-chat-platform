# Deployment Checklist для Railway

## Pre-deployment проверки

### 1. Локальное тестирование
```bash
cd backend

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение локально
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# В другом терминале протестировать:
curl http://localhost:8000/
curl http://localhost:8000/health
```

### 2. Проверить что все файлы исправлены
- [ ] `backend/app/api/messages.py` содержит `from datetime import datetime` в импортах
- [ ] `backend/app/api/messages.py` строка 107 содержит `datetime.utcnow()` (не `__import__()`)
- [ ] `backend/app/api/chats.py` содержит импорт `from sqlalchemy import delete`
- [ ] `backend/app/api/chats.py` использует `await db.execute(delete(Chat)...)` для удаления
- [ ] `backend/app/main.py` имеет try/except блок в startup_event()

### 3. Проверить docker image locally
```bash
cd backend

# Build image
docker build -t ai-chat-backend:latest .

# Run image
docker run -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/ai_chat \
           -e ANTHROPIC_API_KEY=your-key \
           -p 8000:8000 \
           ai-chat-backend:latest

# Test from another terminal
curl http://localhost:8000/health
```

---

## Railway Deployment

### 1. Убедиться что переменные окружения установлены в Railway:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:port/db` | Должна быть postgres asyncpg URL |
| `ANTHROPIC_API_KEY` | your-api-key | Не может быть пустой для production |
| `SECRET_KEY` | random-min-32-chars | Для JWT токенов |
| `DEBUG` | `false` | Production mode |

### 2. Проверить Railway config
- [ ] Root directory: `backend`
- [ ] Dockerfile path: `Dockerfile` (в backend folder)
- [ ] Port: 8000
- [ ] Build command: (пусто - Docker build)
- [ ] Start command: (пусто - используется CMD из Dockerfile)

### 3. Запустить deployment
```bash
# Push к Railway (если используется git integration)
git push origin main

# Или нажать Deploy button в Railway dashboard
```

### 4. Мониторить логи на Railway:
```bash
# Должны видеть эти строки в порядке:
# "Imports completed successfully"
# "FastAPI application starting up..."
# "Database connection successful"
# "Application startup complete"
# "Uvicorn running on http://0.0.0.0:8000"
```

### 5. Тестировать endpoints:
```bash
# Health check (должен работать сразу)
curl https://your-app.up.railway.app/health
# Expected: {"status": "ok", "version": "1.0.0", "database": "connected"}

# Root endpoint
curl https://your-app.up.railway.app/
# Expected: {"message": "Welcome to AI Chat Platform", "docs": "/docs", "version": "1.0.0"}

# Docs (если включены)
curl https://your-app.up.railway.app/docs
# Expected: 200 OK с Swagger UI HTML
```

---

## Тестирование основного функционала

### 1. User Registration
```bash
curl -X POST https://your-app.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "testpass123"
  }'

# Expected response:
# {
#   "access_token": "...",
#   "refresh_token": "...",
#   "token_type": "bearer",
#   "user": {...}
# }
```

### 2. Create Chat
```bash
TOKEN="your_access_token_from_above"

curl -X POST https://your-app.up.railway.app/api/v1/chats \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "My First Chat",
    "model": "claude-haiku-4-5-20251001"
  }'

# Expected: 201 Created with chat object
```

### 3. Send Message (Streaming) - CRITICAL TEST
```bash
CHAT_ID="chat_id_from_above"
TOKEN="your_access_token"

curl -X POST https://your-app.up.railway.app/api/v1/messages/{CHAT_ID}/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, Claude!"}' \
  --no-buffer

# Expected: 200 OK с streaming SSE events
# data: text chunks will appear here
# No 502 errors!
```

---

## Troubleshooting

### Если все еще видите 502:

1. **Проверить Railway logs:**
   - Ищите ошибки импорта: `ImportError`, `SyntaxError`, `ModuleNotFoundError`
   - Ищите ошибки БД: `AsyncIOError`, `sqlalchemy.exc.*`

2. **Проверить что исправления применены:**
   ```bash
   # В Railway console или локально:
   grep -n "__import__" backend/app/api/messages.py
   # Не должно выводить ничего

   grep -n "from datetime import" backend/app/api/messages.py
   # Должно вывести строку
   ```

3. **Проверить DATABASE_URL:**
   ```bash
   # Должен быть формат:
   # postgresql+asyncpg://username:password@host:port/database

   # НЕ должен быть:
   # postgresql://...  (без +asyncpg)
   # postgres://...    (старый формат)
   ```

4. **Проверить что PORT=8000:**
   - Railway должен проксировать запросы на port 8000
   - Uvicorn должен слушать на 0.0.0.0:8000

5. **Проверить ANTHROPIC_API_KEY:**
   - Если не установлен, streaming endpoint вернет 500
   - Убедитесь что ключ валиден

---

## Post-deployment мониторинг

### 1. Настроить Railway alerts:
- [ ] Monitor for `502` HTTP status codes
- [ ] Monitor logs for `ERROR`, `Exception`, `Failed`
- [ ] Setup email notifications

### 2. Регулярные проверки:
```bash
# Cron job каждый час:
curl -f https://your-app.up.railway.app/health || alert

# Cron job каждый день:
# Протестировать full auth flow
```

### 3. Database мониторинг:
- [ ] Проверить что connections не leak'ят
- [ ] Проверить что pool_size достаточен (текущий: 3)
- [ ] Проверить что migrations выполнены

---

## Откат (если что-то пошло не так)

```bash
# 1. Откатить на предыдущий deployment в Railway:
# Dashboard -> Deployments -> Select previous -> Redeploy

# 2. ИЛИ откатить git:
git revert HEAD
git push origin main
# Railway автоматически перестроит и переразвернет

# 3. Проверить что работает:
curl https://your-app.up.railway.app/health
```

---

## Финальный чек перед production traffic

- [ ] Health check возвращает 200 ✅
- [ ] Регистрация пользователя работает ✅
- [ ] Создание чата работает ✅
- [ ] Streaming message работает БЕЗ 502 ✅
- [ ] Database logs показывают успешные соединения ✅
- [ ] Нет ERROR entries в logs ✅
- [ ] Фронтенд может делать запросы к бэкенду ✅
