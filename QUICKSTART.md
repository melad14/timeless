# Timeless Backend Quick Start Guide

## Quick Start (5 minutes)

### Windows

1. **Run Setup Script:**
   ```bash
   setup.bat
   ```

2. **Edit Configuration:**
   - Open `.env` file
   - Update `DATABASE_URL` if needed
   - Generate strong `SECRET_KEY` and `ENCRYPTION_KEY`

3. **Start Server:**
   ```bash
   run.bat
   ```

### macOS / Linux

1. **Run Setup Script:**
   ```bash
   bash setup.sh
   ```

2. **Edit Configuration:**
   - Open `.env` file
   - Update `DATABASE_URL` if needed
   - Generate strong `SECRET_KEY` and `ENCRYPTION_KEY`

3. **Start Server:**
   ```bash
   bash run.sh
   ```

## Using Docker (Recommended for Production)

### Prerequisites
- Docker installed (https://www.docker.com/products/docker-desktop)

### Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000

### Stop Services

```bash
docker-compose down
```

## Generate Security Keys

### Secret Key (for JWT)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Encryption Key (for AES-256)
```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

## API Testing

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. View API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Sign Up
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "phone_number": "+1234567890"
  }'
```

Response will include JWT token:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

### 4. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

## Basic Workflow

### 1. Create Users
Both users need to sign up

### 2. Create Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Direct Message",
    "is_group": false,
    "member_ids": [1, 2]
  }'
```

### 3. Send Message
```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! This message is encrypted with AES-256",
    "conversation_id": 1
  }'
```

### 4. Get Messages
```bash
curl -X GET http://localhost:8000/api/v1/messages/conversation/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Port 8000 Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- For Docker: `docker-compose ps`

### Module Not Found Error
```bash
# Reactivate virtual environment
# Windows
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Permission Denied on Script
```bash
# macOS/Linux
chmod +x setup.sh run.sh
```

## Environment File Configuration

### Minimal Configuration (Development)
```env
DATABASE_URL=sqlite:///./timeless.db
SECRET_KEY=dev-secret-key-32-chars-minimum-here
ENCRYPTION_KEY=dev-encryption-32chars-for-aes256
DEBUG=True
```

### Production Configuration
```env
DATABASE_URL=postgresql://user:password@host:5432/db?sslmode=require
SECRET_KEY=<strong-random-32-chars-minimum>
ENCRYPTION_KEY=<strong-random-32-chars>
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]
```

## Useful Commands

### Virtual Environment
```bash
# Windows - Activate
venv\Scripts\activate.bat

# macOS/Linux - Activate
source venv/bin/activate

# Deactivate
deactivate
```

### Database Management
```bash
# Create database (PostgreSQL)
createdb timeless_db

# Drop database
dropdb timeless_db

# Reset database
dropdb timeless_db && createdb timeless_db
```

### Development
```bash
# Run tests
pytest

# Format code
black app/

# Check lint
flake8 app/

# Type checking
mypy app/
```

## Next Steps

1. **Setup Frontend**: Connect your React/Vue/Angular frontend to the API
2. **Setup Monitoring**: Implement error tracking and logging
3. **Setup CI/CD**: Configure GitHub Actions or GitLab CI for automation
4. **Setup Reverse Proxy**: Use Nginx for production deployment
5. **Setup SSL**: Configure HTTPS with Let's Encrypt

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Pydantic Documentation: https://docs.pydantic.dev/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- JWT.io: https://jwt.io/

## Support

For issues or questions, check:
1. The comprehensive README.md
2. API Documentation at http://localhost:8000/docs
3. Issue tracker on GitHub

---

**Happy Coding! 🚀**
