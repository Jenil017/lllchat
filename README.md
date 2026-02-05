# FastAPI Realtime Chat Backend

Production-ready realtime single-room chat backend built with FastAPI, WebSockets, PostgreSQL, and Redis.

## Features

- 🔐 **JWT Authentication** - Secure user registration and login with bcrypt password hashing
- 💬 **Realtime Messaging** - WebSocket-based instant messaging for all users in a global chat room
- 📜 **Message History** - Cursor-based pagination for efficient message retrieval
- ✏️ **Edit & Delete Messages** - Users can edit and soft-delete their own messages with realtime updates
- 👥 **Presence Tracking** - Track online users with Redis-based presence management
- ⌨️ **Typing Indicators** - Realtime typing notifications
- 🚦 **Rate Limiting** - Redis-based sliding window rate limiter to prevent spam (5 messages per 5 seconds)
- ❤️ **Heartbeat/Ping-Pong** - WebSocket connection health monitoring
- 📊 **Clean Architecture** - Service layer pattern with dependency injection

## Tech Stack

- **Python 3.12+** with async/await
- **FastAPI** - Modern async web framework
- **WebSockets** - Realtime bidirectional communication
- **PostgreSQL** - Relational database with asyncpg driver
- **SQLAlchemy 2.0** - Async ORM
- **Redis** - Caching, presence, and rate limiting
- **Alembic** - Database migrations
- **JWT** - JSON Web Token authentication
- **bcrypt** - Password hashing
- **Pydantic v2** - Data validation

## Project Structure

```
ChatApplicationBackend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication routes
│   │   ├── users.py      # User routes
│   │   ├── messages.py   # Message routes
│   │   └── websocket.py  # WebSocket endpoint
│   ├── core/             # Core infrastructure
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database setup
│   │   ├── security.py   # JWT & password hashing
│   │   ├── websocket_manager.py  # WebSocket connections
│   │   └── rate_limiter.py       # Rate limiting
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   └── message.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── message.py
│   │   └── websocket.py
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── message_service.py
│   │   └── presence_service.py
│   └── main.py           # FastAPI app
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md
```

## Installation

### Prerequisites

- Python 3.12 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher

### Setup

1. **Clone the repository** (if applicable)

2. **Create virtual environment**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Update `.env` with your database and Redis credentials:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatdb
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-super-secret-key-change-this-in-production
```

5. **Create PostgreSQL database**

```bash
createdb chatdb
```

6. **Run database migrations**

```bash
alembic upgrade head
```

7. **Start the server**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `GET /auth/me` - Get current user info (requires JWT)

### Users

- `GET /users/online` - Get list of currently online users

### Messages

- `GET /messages?limit=50&cursor=<timestamp>` - Get message history with pagination
- `PATCH /messages/{id}` - Edit own message (requires JWT)
- `DELETE /messages/{id}` - Delete own message (requires JWT)

### WebSocket

- `WS /ws/chat?token=<jwt>` - WebSocket connection for realtime chat

## WebSocket Protocol

All WebSocket messages follow this structure:

```json
{
  "event": "event_name",
  "data": {}
}
```

### Client → Server Events

**send_message** - Send a new message
```json
{
  "event": "send_message",
  "data": {
    "content": "Hello, world!"
  }
}
```

**typing** - Indicate user is typing
```json
{
  "event": "typing",
  "data": {}
}
```

**ping** - Heartbeat ping
```json
{
  "event": "ping",
  "data": {}
}
```

### Server → Client Events

**new_message** - New message broadcast
```json
{
  "event": "new_message",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "username": "john",
    "content": "Hello!",
    "created_at": "2026-02-05T10:30:00Z",
    "updated_at": null,
    "is_deleted": false
  }
}
```

**message_edited** - Message was edited
```json
{
  "event": "message_edited",
  "data": {
    "message_id": "uuid",
    "content": "Updated content",
    "updated_at": "2026-02-05T10:31:00Z"
  }
}
```

**message_deleted** - Message was deleted
```json
{
  "event": "message_deleted",
  "data": {
    "message_id": "uuid"
  }
}
```

**user_joined** - User connected
```json
{
  "event": "user_joined",
  "data": {
    "user_id": "uuid",
    "username": "john"
  }
}
```

**user_left** - User disconnected
```json
{
  "event": "user_left",
  "data": {
    "user_id": "uuid",
    "username": "john"
  }
}
```

**user_typing** - User is typing
```json
{
  "event": "user_typing",
  "data": {
    "user_id": "uuid",
    "username": "john"
  }
}
```

**pong** - Heartbeat response
```json
{
  "event": "pong",
  "data": {}
}
```

## Rate Limiting

Rate limiting is enforced on message sending:
- **Limit**: 5 messages per 5 seconds per user
- **Implementation**: Redis-based sliding window algorithm

If exceeded, the server sends an error event:

```json
{
  "event": "error",
  "data": {
    "message": "Rate limit exceeded. Please slow down."
  }
}
```

## Development

### Running Tests

(Tests to be implemented)

```bash
pytest
```

### Creating New Migrations

After modifying models:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use a production-grade ASGI server like Gunicorn with Uvicorn workers
3. Configure CORS origins in `app/main.py` to restrict access
4. Use environment variables for secrets (never commit `.env`)
5. Set up SSL/TLS for secure connections
6. Configure Redis persistence
7. Set up database backups
8. Use connection pooling for PostgreSQL

Example production command:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## License

This project is for educational purposes.
