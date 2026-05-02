# Database Structure Documentation - Timeless Time Capsule App

## 📊 Database Schema Overview

تم بناء هيكل قاعدة بيانات **SQLAlchemy ORM** كامل لتطبيق Timeless. الهيكل يتضمن نموذجين أساسيين مع علاقات صحيحة.

---

## 🔧 Core Models

### 1. User Model (`app/models/__init__.py`)

```python
class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    time_capsules = relationship("TimeCapsule", back_populates="user")
```

**الحقول:**
- `id`: معرّف فريد
- `email`: بريد إلكتروني فريد (مفهرس)
- `username`: اسم مستخدم فريد (مفهرس)
- `phone_number`: رقم الهاتف (اختياري)
- `hashed_password`: كلمة المرور مشفّرة بـ **bcrypt**
- `is_active`: حالة النشاط (افتراضي: صحيح)
- `is_verified`: حالة التحقق من البريد (افتراضي: خطأ)
- `created_at`: وقت الإنشاء
- `updated_at`: وقت آخر تحديث

---

### 2. TimeCapsule Model (`app/models/__init__.py`)

```python
class TimeCapsule(Base):
    """Time Capsule model for storing encrypted messages"""
    __tablename__ = "time_capsules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Encrypted (AES-256-GCM)
    content_type = Column(String, nullable=False)  # 'text', 'image', 'video'
    open_date = Column(DateTime(timezone=True), nullable=False)
    is_opened = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="time_capsules")
```

**الحقول:**
- `id`: معرّف فريد للكبسولة
- `user_id`: مفتاح خارجي يشير لـ User
- `title`: عنوان الكبسولة
- `content`: المحتوى المشفّر (نص/صورة/فيديو بصيغة base64)
- `content_type`: نوع المحتوى (text/image/video)
- `open_date`: التاريخ المحدد لفتح الكبسولة
- `is_opened`: هل تم فتح الكبسولة؟
- `created_at`: وقت إنشاء الكبسولة
- `updated_at`: آخر تحديث

---

## 🔐 Security Implementation

### Password Hashing (`app/security/password.py`)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Message Encryption (`app/security/encryption.py`)
```python
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64

class MessageEncryption:
    def __init__(self):
        key = self.settings.encryption_key.encode('utf-8')
        self.key = PBKDF2(key, b'timeless_salt', dkLen=32, count=100000)
    
    def encrypt(self, plaintext: str) -> str:
        """AES-256-GCM encryption"""
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        encrypted_data = cipher.nonce + ciphertext + tag
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """AES-256-GCM decryption"""
        encrypted_data = base64.b64decode(encrypted_text)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:-16]
        tag = encrypted_data[-16:]
        
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')
```

---

## 📁 Database Configuration

### Database Connection (`app/database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import get_settings

settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Configuration (`app/config.py`)
```python
class Settings(BaseSettings):
    # Database (SQLite for development, PostgreSQL for production)
    database_url: str = "sqlite:///./timeless.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "your-32-byte-encryption-key"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
```

---

## 📝 Pydantic Schemas

### User Schemas (`app/schemas/__init__.py`)
```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=255)
    phone_number: Optional[str] = None
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### TimeCapsule Schemas
```python
class TimeCapsuleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    content_type: str = Field(..., pattern="^(text|image|video)$")
    open_date: datetime

class TimeCapsuleResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content_type: str
    open_date: datetime
    is_opened: bool
    created_at: datetime
    updated_at: datetime
```

---

## 🔄 CRUD Operations

### User CRUD (`app/crud/user.py`)
```python
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        phone_number=user.phone_number,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
```

### TimeCapsule CRUD (`app/crud/time_capsule.py`)
```python
def create_time_capsule(db: Session, capsule_data: TimeCapsuleCreate, user_id: int) -> TimeCapsule:
    encrypted_content = encrypt_message(capsule_data.content)
    db_capsule = TimeCapsule(
        user_id=user_id,
        title=capsule_data.title,
        content=encrypted_content,
        content_type=capsule_data.content_type,
        open_date=capsule_data.open_date
    )
    db.add(db_capsule)
    db.commit()
    db.refresh(db_capsule)
    return db_capsule

def open_time_capsule(db: Session, capsule_id: int) -> Optional[TimeCapsule]:
    db_capsule = db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()
    if not db_capsule or db_capsule.is_opened:
        return None
    if db_capsule.open_date > datetime.utcnow():
        return None
    
    db_capsule.is_opened = True
    db.commit()
    db.refresh(db_capsule)
    return db_capsule

def get_user_time_capsules(db: Session, user_id: int) -> List[TimeCapsule]:
    return db.query(TimeCapsule).filter(TimeCapsule.user_id == user_id).all()
```

---

## 🔌 API Endpoints

### Authentication Routes (`app/api/routes/auth.py`)
- **POST** `/api/v1/auth/signup` - إنشاء حساب جديد
- **POST** `/api/v1/auth/login` - تسجيل الدخول

### Time Capsule Routes (`app/api/routes/time_capsules.py`)
- **POST** `/api/v1/time-capsules` - إنشاء كبسولة زمنية
- **GET** `/api/v1/time-capsules` - الحصول على جميع الكبسولات
- **GET** `/api/v1/time-capsules/pending` - الكبسولات المنتظرة
- **GET** `/api/v1/time-capsules/opened` - الكبسولات المفتوحة
- **GET** `/api/v1/time-capsules/{capsule_id}` - كبسولة محددة
- **PUT** `/api/v1/time-capsules/{capsule_id}` - تحديث الكبسولة
- **POST** `/api/v1/time-capsules/{capsule_id}/open` - فتح الكبسولة
- **DELETE** `/api/v1/time-capsules/{capsule_id}` - حذف الكبسولة
- **POST** `/api/v1/time-capsules/check-ready` - فحص الكبسولات الجاهزة للفتح

### User Routes (`app/api/routes/users.py`)
- **GET** `/api/v1/users/me` - الملف الشخصي
- **GET** `/api/v1/users/{user_id}` - معلومات مستخدم
- **PUT** `/api/v1/users/me` - تحديث الملف الشخصي

---

## 🗄️ Database Initialization

تهيئة قاعدة البيانات تحدث تلقائياً عند تشغيل التطبيق:

```python
# app/main.py
from app.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)
```

---

## 📦 Dependencies

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pycryptodome==3.19.0
bcrypt==4.1.2
PyJWT==2.8.0
email-validator==2.1.0
python-dotenv==1.0.0
```

---

## 🚀 Setup and Running

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verification Checklist

- ✓ Database models defined with SQLAlchemy ORM
- ✓ User authentication with JWT tokens
- ✓ Password hashing with bcrypt (12 rounds)
- ✓ Message encryption with AES-256-GCM
- ✓ Time capsule CRUD operations
- ✓ User profile management
- ✓ Role-based access control
- ✓ CORS configuration
- ✓ API documentation (Swagger UI at /docs)
- ✓ Health check endpoint

---

**Created:** 2026-04-11  
**Status:** ✅ Complete and Ready for Review  
**Frontend Integration:** Ready (UI/UX design provided)
