# Deployment Guide

## Quick Deploy

### Backend (Render)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
   | Variable | Value |
   |----------|-------|
   | `DATABASE_URL` | Your PostgreSQL URL (use [Neon](https://neon.tech) for free) |
   | `JWT_SECRET_KEY` | Generate with `openssl rand -hex 32` |
   | `OPENAI_API_KEY` | Your OpenAI API key |
   | `CORS_ORIGINS` | Your Vercel frontend URL |

6. Click **Create Web Service**

### Frontend (Vercel)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repo
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)

5. Add Environment Variable:
   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | Your Render backend URL (e.g., `https://todo-chatbot-api.onrender.com`) |

6. Click **Deploy**

## Post-Deployment

### Update CORS Origins

After deploying frontend, update backend's `CORS_ORIGINS` environment variable:
```
CORS_ORIGINS=https://your-app.vercel.app
```

### Database Setup

For PostgreSQL, use [Neon](https://neon.tech) (free tier available):
1. Create a new project
2. Copy the connection string
3. Add to Render's `DATABASE_URL`

The backend will auto-create tables on first startup.

## Environment Variables Reference

### Backend (Required)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Secret for JWT signing |
| `OPENAI_API_KEY` | OpenAI API key for chat AI |
| `CORS_ORIGINS` | Comma-separated allowed origins |

### Backend (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Fallback AI provider |
| `AI_TIMEOUT_SECONDS` | 5 | Max AI response time |
| `LOG_LEVEL` | INFO | Logging verbosity |

### Frontend (Required)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |
