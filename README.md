# Timeless - FastAPI Messaging Backend

A secure, production-ready FastAPI backend for the Timeless messaging application with JWT authentication, AES encryption for messages, and bcrypt password hashing.

**Note: This project has been prepared for database integration. All database components have been removed and replaced with mock implementations that return HTTP 501 Not Implemented errors. The database team should implement the actual database operations following the TODO comments throughout the codebase.**

## Features

- **User Authentication**: JWT-based token authentication
- **Password Security**: bcrypt password hashing with configurable rounds
- **Message Encryption**: AES-256-GCM encryption for all messages
- **User Management**: User registration, login, profile management
- **Conversations**: One-on-one and group conversations (mock implementation)
- **Message Management**: Send, receive, edit, delete messages with encryption (mock implementation)
- **Favorites**: Mark messages as favorites (mock implementation)
- **Message Status**: Track read/unread status (mock implementation)
- **CORS Support**: Configured for cross-origin requests
- **Database Ready**: Prepared for database integration with clear TODO comments

## Project Structure

```
timeless/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main FastAPI application
│   ├── config.py               # Configuration management
│   ├── models/
│   │   └── __init__.py         # Pydantic models (User, Message, Conversation) - Ready for SQLAlchemy conversion
│   ├── schemas/
│   │   └── __init__.py         # Pydantic schemas for validation
│   ├── crud/
│   │   ├── user.py             # User CRUD operations (mock implementations)
│   │   ├── message.py          # Message CRUD operations (mock implementations)
│   │   └── conversation.py     # Conversation CRUD operations (mock implementations)
│   ├── api/
│   │   ├── __init__.py         # API router setup
│   │   ├── dependencies.py     # Dependency injection
│   │   └── routes/
│   │       ├── auth.py         # Authentication endpoints (working)
│   │       ├── users.py        # User endpoints (mock implementations)
│   │       ├── messages.py     # Message endpoints (mock implementations)
│   │       └── conversations.py # Conversation endpoints (mock implementations)
│   ├── security/
│   │   ├── jwt.py              # JWT token handling
│   │   ├── password.py         # Password hashing/verification
│   │   ├── encryption.py       # AES message encryption
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py         # Utility validators
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.10+
- pip or conda

### Setup

1. **Clone and navigate to project:**
   ```bash
   cd timeless
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Configure .env file:**
   - Generate a strong `SECRET_KEY` (minimum 32 characters):
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
   - Generate `ENCRYPTION_KEY` (exactly 32 characters for AES-256):
     ```bash
     python -c "import secrets; print(secrets.token_hex(16))"
     ```

## Seed Data

To populate the MongoDB database with sample users, conversations, messages, and time capsules, run:

```bash
python seeds.py --reset
```

Use `--reset` to drop the existing seed collections before inserting the sample data.

## Running the Application

**Development:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Security Implementation

### 1. JWT Authentication
- Access tokens expire after 30 minutes (configurable)
- Tokens include user ID and generation timestamp
- Used for all protected endpoints
- Bearer token in Authorization header

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/users/me
```

### 2. Password Hashing (bcrypt)
- 12 rounds of bcrypt hashing (configurable)
- Passwords never stored in plain text
- Automatic verification on login

### 3. Message Encryption (AES-256-GCM)
- AES-256 encryption in GCM mode
- PBKDF2 key derivation with 100,000 iterations
- Authentication tag prevents tampering
- Automatic encryption on send, decryption on retrieve

## API Endpoints

**Note: All endpoints except authentication are currently returning HTTP 501 Not Implemented errors. The database team needs to implement the actual database operations following the TODO comments in the route files.**

### Authentication (Working)
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users (Mock Implementation)
- `GET /api/v1/users/me` - Get current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/me` - Update current user profile
- `DELETE /api/v1/users/me` - Deactivate account

### Messages (Mock Implementation)
- `POST /api/v1/messages` - Send message
- `GET /api/v1/messages/{message_id}` - Get message
- `PUT /api/v1/messages/{message_id}` - Update message
- `DELETE /api/v1/messages/{message_id}` - Delete message
- `POST /api/v1/messages/{message_id}/read` - Mark as read
- `POST /api/v1/messages/{message_id}/favorite` - Toggle favorite
- `GET /api/v1/messages/conversation/{conversation_id}` - Get conversation messages
- `GET /api/v1/messages/user/favorites` - Get user's favorite messages

### Conversations (Mock Implementation)
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations` - Get user's conversations
- `GET /api/v1/conversations/{conversation_id}` - Get conversation details
- `PUT /api/v1/conversations/{conversation_id}` - Update conversation
- `POST /api/v1/conversations/{conversation_id}/members/{user_id}` - Add member
- `DELETE /api/v1/conversations/{conversation_id}/members/{user_id}` - Remove member
- `DELETE /api/v1/conversations/{conversation_id}` - Delete conversation

## Database Integration

This project has been prepared for database integration. All database components have been removed and replaced with mock implementations. The database team should:

1. **Add Database Dependencies**: Install SQLAlchemy, database drivers (psycopg2 for PostgreSQL), and Alembic for migrations
2. **Create Database Models**: Convert the Pydantic models in `app/models/__init__.py` to SQLAlchemy models
3. **Implement CRUD Operations**: Replace mock implementations in `app/crud/` files with actual database queries
4. **Update API Routes**: Replace HTTP 501 errors in `app/api/routes/` files with actual database operations
5. **Add Database Configuration**: Add `DATABASE_URL` to environment variables and database session management

### Files Requiring Database Implementation

- `app/models/__init__.py` - Convert Pydantic models to SQLAlchemy
- `app/crud/user.py` - Implement user database operations
- `app/crud/message.py` - Implement message database operations  
- `app/crud/conversation.py` - Implement conversation database operations
- `app/api/routes/users.py` - Replace mock implementations
- `app/api/routes/messages.py` - Replace mock implementations
- `app/api/routes/conversations.py` - Replace mock implementations
- `app/api/dependencies.py` - Add database session dependencies

### Expected Database Schema

The following tables should be created:

**Users Table**
- id (Primary Key)
- email (Unique)
- username (Unique)
- phone_number
- hashed_password
- is_active
- is_verified
- created_at
- updated_at

**Conversations Table**
- id (Primary Key)
- title
- description
- is_group
- created_at
- updated_at

**Messages Table**
- id (Primary Key)
- content (Encrypted)
- sender_id (Foreign Key → Users)
- conversation_id (Foreign Key → Conversations)
- is_read
- is_favorite
- created_at
- updated_at

**Conversation Members (Association Table)**
- user_id (Foreign Key → Users)
- conversation_id (Foreign Key → Conversations)

## Example Usage

### 1. Sign Up
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "phone_number": "+1234567890"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Send Message
```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, this is a secure message!",
    "conversation_id": 1
  }'
```

### 4. Create Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Discussion",
    "description": "Discussion about project",
    "is_group": true,
    "member_ids": [1, 2, 3]
  }'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | JWT secret key (min 32 chars) | your-secret-key-change-this-in-production |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |
| ENCRYPTION_KEY | AES encryption key (32 chars) | your-encryption-key-must-be-32-characters |
| DEBUG | Debug mode | True |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 8000 |
| CORS_ORIGINS | CORS allowed origins | ["http://localhost:3000"] |

**Note: DATABASE_URL will be added by the database team when implementing database operations.**

## Dependencies

### Core
- **fastapi** - Web framework
- **uvicorn** - ASGI server

### Security
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **bcrypt** - bcrypt algorithm
- **pycryptodome** - Cryptography library

### Validation
- **pydantic** - Data validation
- **email-validator** - Email validation

### Development
- **python-dotenv** - Environment variables

**Note: Database dependencies (SQLAlchemy, psycopg2, alembic) will be added by the database team.**

## Production Considerations

1. **Database** (To be implemented by database team):
   - Use PostgreSQL in production
   - Enable SSL connections
   - Set up regular backups
   - Implement connection pooling

2. **Environment**:
   - Set `DEBUG=False` in production
   - Use strong `SECRET_KEY` (minimum 32 characters)
   - Use strong `ENCRYPTION_KEY` (must be 32 bytes)
   - Enable HTTPS only

3. **Security**:
   - Use environment variables for secrets
   - Enable rate limiting
   - Set up monitoring and logging
   - Use firewall rules
   - Regular security audits

4. **Performance**:
   - Use multiple workers (4+ for production)
   - Set up caching (Redis) - to be implemented
   - Optimize database queries - to be implemented
   - Use CDN for static files

5. **Monitoring**:
   - Set up error tracking (Sentry)
   - Monitor API performance
   - Log important events
   - Set up health checks

## Testing

Create a `test_api.py` file with pytest for testing:

```bash
pip install pytest pytest-asyncio httpx
pytest
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
netstat -ano | findstr :8000  # Windows
kill -9 <PID>

# On macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### API Returns 501 Not Implemented
This is expected behavior. The database team needs to implement the actual database operations following the TODO comments in the route files.

### Encryption/Decryption Errors
- Verify `ENCRYPTION_KEY` is exactly 32 characters
- Ensure no modifications to encrypted data
- Check message encoding

### Database Integration (For Database Team)
- Database connection errors will occur until database dependencies are added
- All CRUD operations currently return None/mock data
- API routes return 501 errors until database operations are implemented

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI**
