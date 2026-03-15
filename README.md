# AI Chat Platform

A fullstack AI chat application with real-time streaming responses from Claude API.

**Live Demo**: (coming soon)

## Features

**Real-time AI Chat**: Stream responses from Claude API directly to your browser
**User Authentication**: Register, login, and secure JWT-based sessions
**Chat History**: Persistent conversations stored in PostgreSQL
**Model Selection**: Choose between claude-haiku (fast) and claude-sonnet (quality)
**Responsive Design**: Mobile-first UI with TailwindCSS
**Dark Mode**: Built-in dark/light theme support

## Tech Stack

### Frontend
- **React** 18 with TypeScript
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **Zustand** - State management
- **Axios** - HTTP client
- **React Router** - Routing
- **Marked** - Markdown rendering

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM with async support
- **PostgreSQL** - Database
- **Anthropic SDK** - Claude API integration
- **JWT** - Authentication
- **WebSockets** - Real-time streaming (future)

### DevOps
- **Docker** & **Docker Compose** - Containerization
- **Vercel** - Frontend hosting
- **Railway** - Backend + Database hosting

## Project Structure

```
ai-chat-platform/
├── frontend/                 # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── store/           # Zustand stores
│   │   ├── types/           # TypeScript types
│   │   └── api/             # API client
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                  # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/             # API routes
│   │   │   ├── auth.py      # Authentication
│   │   │   ├── chats.py     # Chat CRUD
│   │   │   └── messages.py  # Messages & streaming
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── core/            # Config & database
│   │   └── main.py          # App entry
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml        # Local development
└── README.md

```

## Getting Started

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend)
- Anthropic API Key (get one at https://console.anthropic.com/)

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone https://github.com/vlamay/ai-chat-platform.git
cd ai-chat-platform

# Create .env file with your Anthropic API key
cp backend/.env.example backend/.env
# Edit backend/.env and add your ANTHROPIC_API_KEY

# Start all services
docker-compose up

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations (auto-created on startup)
# Start the server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Documentation

### Authentication Endpoints

#### Register User
```bash
POST /api/v1/auth/register

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-03-15T12:00:00Z"
  }
}
```

#### Login
```bash
POST /api/v1/auth/login

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

### Chat Endpoints

#### Create Chat
```bash
POST /api/v1/chats
Authorization: Bearer <access_token>

{
  "title": "AI Discussion",
  "model": "claude-haiku-4-5-20251001"
}
```

#### List User's Chats
```bash
GET /api/v1/chats
Authorization: Bearer <access_token>
```

#### Get Chat with Messages
```bash
GET /api/v1/chats/{chat_id}
Authorization: Bearer <access_token>
```

#### Get Chat Messages
```bash
GET /api/v1/messages/{chat_id}
Authorization: Bearer <access_token>
```

#### Stream Message Response
```bash
POST /api/v1/messages/{chat_id}/stream
Authorization: Bearer <access_token>

{
  "content": "Hello, Claude!"
}

Response: Server-Sent Events stream with Claude's response
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  name VARCHAR NOT NULL,
  avatar_url VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Chats Table
```sql
CREATE TABLE chats (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title VARCHAR NOT NULL DEFAULT 'New Chat',
  model VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Messages Table
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  chat_id UUID REFERENCES chats(id),
  role VARCHAR NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  tokens_used INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Deployment

### Deploy Backend to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway init

# 4. Add PostgreSQL
railway add -d postgresql

# 5. Deploy
railway up
```

### Deploy Frontend to Vercel

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
vercel
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=sk-ant-xxx...
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
```

## Architecture

```
User Browser
    ↓
Frontend (React)
    ↓ HTTP/WebSocket
Backend (FastAPI)
    ↓
PostgreSQL Database
    ↓
Claude API
```

### Data Flow

1. **User sends message** → Frontend → Backend (HTTP POST)
2. **Backend receives message** → Saves to DB → Calls Claude API
3. **Claude responds** → Backend streams response via Server-Sent Events
4. **Frontend receives** → Renders in real-time → Saves to local cache

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Linting & Formatting
```bash
# Backend
cd backend
black . && flake8 .

# Frontend
cd frontend
npm run lint && npm run format
```

### Build for Production
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
pip install -r requirements.txt
```

## Performance Considerations

- **Database**: Indexed queries on user_id, chat_id
- **Frontend**: Lazy loading of chat history
- **Backend**: Async/await for non-blocking I/O
- **API**: Server-Sent Events for real-time streaming

## Security

- JWT authentication with refresh tokens
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React escaping)
- Input validation (Pydantic)

## Future Enhancements

- [ ] WebSocket support for real-time collaboration
- [ ] Conversation sharing
- [ ] Prompt templates
- [ ] Usage analytics & cost tracking
- [ ] Multiple AI providers
- [ ] Voice input/output
- [ ] Code syntax highlighting
- [ ] Export conversations as PDF/Markdown

## Contributing

This is a portfolio project. Feel free to fork and customize!

## License

MIT License - see LICENSE file for details

## Author

**Vladyslav Maidaniuk**
- GitHub: [@vlamay](https://github.com/vlamay)
- Portfolio: [vlamay.github.io](https://vlamay.github.io)

---
