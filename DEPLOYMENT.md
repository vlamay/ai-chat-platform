# Deployment Guide

## Overview

This guide covers deploying the AI Chat Platform to production using:
- **Frontend**: Vercel (free tier available)
- **Backend**: Railway (free tier available)
- **Database**: Railway PostgreSQL

## Environment Variables (Updated)

### Railway (Backend)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ auto | Set by Railway PostgreSQL plugin |
| `SECRET_KEY` | ✅ | Random 32+ character string for JWT signing |
| `ANTHROPIC_API_KEY` | ✅ | From https://console.anthropic.com |
| `SENTRY_DSN` | optional | From https://sentry.io for error tracking |
| `REDIS_URL` | optional | From Railway Redis plugin for caching |
| `ALLOWED_ORIGINS` | optional | Comma-separated list of frontend URLs (e.g., https://your-app.vercel.app) |
| `DEBUG` | optional | Set to `false` in production |

### Vercel (Frontend)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | ✅ | Railway backend URL + `/api/v1` |
| `VITE_SENTRY_DSN` | optional | Frontend Sentry DSN (separate from backend) |

## Prerequisites

1. **GitHub Account**: Push your repo to GitHub
2. **Vercel Account**: https://vercel.com (free)
3. **Railway Account**: https://railway.app (free)
4. **Anthropic API Key**: https://console.anthropic.com

## Step 1: Push to GitHub

```bash
# If not already done
git remote add origin https://github.com/YOUR_USERNAME/ai-chat-platform.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Choose `ai-chat-platform` repository
5. Select `backend` as the deployment target

### 2.2 Configure Environment Variables

In Railway Dashboard for Backend:
```
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
SECRET_KEY=generate-a-random-string-min-32-chars-here
ANTHROPIC_API_KEY=sk-ant-xxx...
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=false
SENTRY_DSN=https://your-key@sentry.io/project-id
REDIS_URL=redis://[user]:[password]@[host]:[port]
ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-app.com
```

See the **Environment Variables** section above for complete variable reference.


### 2.3 Add PostgreSQL

1. Go to Railway Dashboard
2. Click "New"
3. Select "PostgreSQL"
4. Railway will auto-add `DATABASE_URL` to backend

### 2.4 Generate Railway Dockerfile (if needed)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.5 Update Frontend .env

Once backend is deployed, get the Railway URL and update frontend:

```env
VITE_API_URL=https://your-backend.railway.app/api/v1
```

## Step 3: Deploy Frontend to Vercel

### 3.1 Connect to Vercel

1. Go to https://vercel.com/new
2. Import from GitHub
3. Select `ai-chat-platform`
4. Set Root Directory: `frontend`

### 3.2 Configure Environment

```
VITE_API_URL=https://your-backend.railway.app/api/v1
```

### 3.3 Deploy

1. Click "Deploy"
2. Wait for build to complete
3. You'll get a live URL: `https://ai-chat-platform-xxx.vercel.app`

## Step 4: Post-Deployment

### 4.1 Test the Application

1. Visit your Vercel URL
2. Create a new account
3. Start a chat with Claude
4. Verify streaming works

### 4.2 Monitor

**Backend Logs** (Railway):
```
railway logs
```

**Frontend Analytics** (Vercel):
- Dashboard → Project → Analytics

### 4.3 Update Portfolio

Add to your `vlamay.github.io`:

```markdown
## AI Chat Platform

Real-time AI chat application powered by Claude API.

**Live Demo**: [https://ai-chat-platform-xxx.vercel.app](https://ai-chat-platform-xxx.vercel.app)

**Tech Stack**:
- Frontend: React + TypeScript + TailwindCSS
- Backend: FastAPI + PostgreSQL
- Real-time: Server-Sent Events streaming
- Deployment: Vercel + Railway

**Features**:
- User authentication with JWT
- Real-time AI chat with streaming responses
- Responsive mobile design
- Dark mode support

**Repository**: [GitHub](https://github.com/YOUR_USERNAME/ai-chat-platform)
```

## Troubleshooting

### Backend won't start

**Issue**: Railway build fails
**Solution**:
- Check logs: `railway logs`
- Ensure `requirements.txt` is in `/backend` directory
- Verify `backend/app/main.py` exists

### Database connection fails

**Issue**: `DATABASE_URL` is empty
**Solution**:
- Railway auto-adds PostgreSQL service
- If not, add PostgreSQL plugin manually
- Railway will populate `DATABASE_URL` automatically

### Frontend can't connect to backend

**Issue**: CORS error or 404
**Solution**:
- Verify `VITE_API_URL` in Vercel environment
- Check backend CORS settings in `app/main.py`
- Add Vercel domain to `ALLOWED_ORIGINS`

### Streaming doesn't work

**Issue**: Messages show as one big block
**Solution**:
- Check browser console for errors
- Verify backend `messages.py` has `StreamingResponse`
- Test with `curl` to verify endpoint works

## Performance Optimization

### Frontend

```bash
cd frontend
npm run build
```

Check bundle size:
```bash
npm run build -- --analyze
```

### Backend

Enable compression in `app/main.py`:

```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

## Maintenance

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Database Backups

Railway provides daily backups for free tier.

To export database:
```bash
pg_dump postgresql://[connection_string] > backup.sql
```

## Costs

**Vercel**: Free for frontend (up to 100GB/month bandwidth)
**Railway**: Free tier ($5 credit, ~20-30 hours runtime)
**Anthropic API**: Pay-as-you-go (~$0.003 per 1K input tokens)

For heavy usage, upgrade Railway to paid plan.

## Custom Domain

### Vercel

1. Go to Project Settings
2. Domains
3. Add your custom domain
4. Follow DNS instructions

### Railway

Use Railway's free domain or connect your own in settings.

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Vercel
3. ✅ Configure custom domain
4. ✅ Update portfolio website
5. ✅ Share on GitHub

Good luck! 🚀
