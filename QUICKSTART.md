# FastAPI Chat Backend - Quick Start Guide

## Prerequisites Setup

You need PostgreSQL and Redis running. Choose one option:

### Option 1: Docker (EASIEST - Recommended)

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop/

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Your `.env` is already configured** with the correct credentials!

4. **Skip to "Running the Application" below**

---

### Option 2: Install PostgreSQL and Redis Manually

#### Install PostgreSQL

1. Download from https://www.postgresql.org/download/windows/
2. Install with default settings (remember your password!)
3. Add to PATH: `C:\Program Files\PostgreSQL\15\bin`

#### Create Database

Open PowerShell and run:
```bash
# Log into PostgreSQL (it will ask for password)
psql -U postgres

# Create database
CREATE DATABASE chatdb;

# Create user
CREATE USER chatuser WITH PASSWORD 'chatpass';

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE chatdb TO chatuser;

# Exit
\q
```

#### Install Redis

1. Download from https://github.com/microsoftarchive/redis/releases
2. Install and start Redis service

#### Update .env

If you used different credentials, update your `.env` file:
```env
DATABASE_URL=postgresql+asyncpg://chatuser:chatpass@localhost:5432/chatdb
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secret-key-change-this-in-production
```

---

## Running the Application

Once PostgreSQL and Redis are running:

### 1. Run Database Migrations

```bash
alembic upgrade head
```

### 2. Start the Server

```bash
uvicorn app.main:app --reload
```

### 3. Test the API

Visit: http://localhost:8000/docs

---

## Quick Test

### Register a User
```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

Copy the `access_token` from the response.

### Test WebSocket

Use a WebSocket client (like Postman or wscat):
```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c "ws://localhost:8000/ws/chat?token=YOUR_TOKEN_HERE"

# Send a message
{"event":"send_message","data":{"content":"Hello!"}}
```

---

## Troubleshooting

### Port Already in Use
- PostgreSQL: Change port in docker-compose.yml and .env
- Redis: Change port in docker-compose.yml and .env

### Connection Refused
- Make sure Docker Desktop is running
- Run: `docker-compose ps` to check services are up

### Database Errors
- Run: `docker-compose down -v` then `docker-compose up -d` to reset

---

## Next Steps

1. Read the [README.md](README.md) for full API documentation
2. Check [walkthrough.md](C:/Users/Asus/.gemini/antigravity/brain/33398860-f500-4447-be9c-acc54f473a57/walkthrough.md) for architecture details
3. Build a frontend to connect to this backend!
