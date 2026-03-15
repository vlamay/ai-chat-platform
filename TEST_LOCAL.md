# Local Testing Guide

## Option 1: Quick Test with Docker Compose (Recommended)

### Prerequisites
- Docker & Docker Compose installed
- Anthropic API Key

### Run

```bash
# Navigate to project
cd ~/Documents/claude/ai-chat-platform

# Copy environment
cp backend/.env.example backend/.env

# Edit .env and add your ANTHROPIC_API_KEY
# Then run:
docker-compose up
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Test Flow
1. Go to http://localhost:5173
2. Click "Sign up"
3. Create account (any test email)
4. Start a new chat
5. Type a message
6. Watch Claude's response stream in real-time!

---

## Option 2: Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16 (running locally)
- Anthropic API Key

### Step 1: Set up PostgreSQL

```bash
# On macOS with Homebrew
brew install postgresql
brew services start postgresql

# Create database
createdb ai_chat

# Verify
psql ai_chat -c "SELECT 1;"
```

### Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env

# Edit .env and add:
# - ANTHROPIC_API_KEY=sk-ant-xxx...
# - DATABASE_URL=postgresql://localhost/ai_chat

# Run migrations (auto-creates tables)
uvicorn app.main:app --reload --port 8000
```

Backend should now be at: http://localhost:8000

Verify: http://localhost:8000/docs

### Step 3: Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment
cp .env.example .env.local

# Environment is already correct (localhost:8000)

# Start dev server
npm run dev
```

Frontend should now be at: http://localhost:5173

### Test the Application

1. **Create Account**
   - Go to http://localhost:5173/register
   - Fill in: email, name, password
   - Click "Sign up"

2. **Login**
   - Should redirect to main chat page
   - See empty chat list

3. **Create New Chat**
   - Click "+ New Chat" button
   - Chat loads with empty message list

4. **Send Message**
   - Type in message input: "Hello Claude!"
   - Click "Send"
   - Watch response stream in real-time

5. **Test Features**
   - Create another chat
   - Create multiple messages in same chat
   - Switch between chats (sidebar)
   - See chat history loads correctly
   - Delete a chat
   - Logout

### Debugging

**Backend Issues:**

```bash
# Check logs
# Should see: "Application startup complete"

# Test endpoint
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"1.0.0"}

# Check database connection
# Look for "SELECT 1;" in startup logs
```

**Frontend Issues:**

```bash
# Check console in browser DevTools
# Should see: HTTP requests to localhost:8000/api/v1

# Test API manually
curl http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test","password":"test123"}'
```

---

## Testing API Endpoints Manually

### 1. Register User

```bash
curl http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "secure_password"
  }'

# Response:
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "test@example.com",
    "name": "Test User",
    "created_at": "2024-03-15T12:00:00Z"
  }
}
```

Save the `access_token` for next requests.

### 2. Create Chat

```bash
curl http://localhost:8000/api/v1/chats \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Test Chat",
    "model": "claude-haiku-4-5-20251001"
  }'
```

### 3. Send Message (Stream)

```bash
curl http://localhost:8000/api/v1/messages/CHAT_ID/stream \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"content": "Hello Claude!"}' \
  -N

# Response: Server-Sent Events stream
# data: Hello
# data:  there
# data: !
# ...
```

---

## Common Issues & Solutions

### PostgreSQL Connection Error

**Error**: `could not connect to server`

**Solution**:
```bash
# Ensure PostgreSQL is running
brew services list  # macOS
# or
systemctl status postgresql  # Linux

# Create database if missing
createdb ai_chat
```

### Port Already in Use

**Error**: `Address already in use: ('0.0.0.0', 8000)`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### CORS Error in Frontend

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
- Ensure backend is running at `http://localhost:8000`
- Check `VITE_API_URL` in frontend `.env.local`
- Verify backend `ALLOWED_ORIGINS` includes `http://localhost:5173`

### Anthropic API Error

**Error**: `401 Unauthorized` or `Invalid API key`

**Solution**:
- Get API key from https://console.anthropic.com
- Add to `backend/.env`: `ANTHROPIC_API_KEY=sk-ant-xxx...`
- Restart backend

### Database Migration Error

**Error**: `relation "users" does not exist`

**Solution**:
- FastAPI auto-creates tables on startup
- Check backend logs for errors
- Manually create: `psql ai_chat -f schema.sql` (if exists)

---

## Performance Notes

### First Run
- Backend: Takes ~2-3 seconds to start (dependency loading)
- Frontend: Takes ~10-15 seconds to build (first Vite build)
- Database: Auto-creates tables on startup

### Response Times
- Register: ~100ms
- Login: ~150ms
- Create Chat: ~50ms
- Send Message: ~2-3s (includes Claude API call)
- Stream Response: Real-time text appearance (depends on Claude)

### Development
- Backend auto-reloads on file changes
- Frontend hot-reloads on file changes
- Use browser DevTools to inspect network requests

---

## Next Steps

1. ✅ Test locally (this guide)
2. ✅ Verify all features work
3. → Deploy to production (see DEPLOYMENT.md)
4. → Add to portfolio (vlamay.github.io)
5. → Share on GitHub

---

## Troubleshooting Checklist

- [ ] PostgreSQL running and `ai_chat` database created
- [ ] Backend started: `uvicorn app.main:app --reload`
- [ ] Frontend started: `npm run dev`
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] ANTHROPIC_API_KEY in backend/.env
- [ ] VITE_API_URL correct in frontend/.env.local
- [ ] Browser opens http://localhost:5173
- [ ] Can create account
- [ ] Can send message to Claude
- [ ] Response streams in real-time

If all ✅, you're ready to deploy! 🚀
