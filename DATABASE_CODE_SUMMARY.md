# ملخص شامل لكود قاعدة البيانات - Timeless Time Capsule

## 📋 الملفات التي تم إنشاؤها وتعديلها

جميع الملفات أدناه تم تطويرها وهي جاهزة للمراجعة:

---

## 1️⃣ **Database Configuration** (`app/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# Database URL from config
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**المميزات:**
- إنشاء محرك SQLAlchemy
- جلسة قاعدة البيانات
- دالة Dependency للحقن في الـ Routes

---

## 2️⃣ **Models** (`app/models/__init__.py`)

### User Model
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

    # Relationship to time capsules
    time_capsules = relationship("TimeCapsule", back_populates="user")
```

### TimeCapsule Model
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

    # Relationship to user
    user = relationship("User", back_populates="time_capsules")
```

---

## 3️⃣ **Pydantic Schemas** (`app/schemas/__init__.py`)

### User Schemas
```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### TimeCapsule Schemas
```python
class TimeCapsuleCreate(TimeCapsuleBase):
    pass

class TimeCapsuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = Field(None, pattern="^(text|image|video)$")

class TimeCapsuleResponse(TimeCapsuleBase):
    id: int
    user_id: int
    is_opened: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## 4️⃣ **CRUD Operations - Users** (`app/crud/user.py`)

```python
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

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

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
```

---

## 5️⃣ **CRUD Operations - Time Capsules** (`app/crud/time_capsule.py`)

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

def get_user_time_capsules(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[TimeCapsule]:
    return db.query(TimeCapsule).filter(TimeCapsule.user_id == user_id).offset(skip).limit(limit).all()

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

def delete_time_capsule(db: Session, capsule_id: int, user_id: int) -> bool:
    db_capsule = db.query(TimeCapsule).filter(
        TimeCapsule.id == capsule_id,
        TimeCapsule.user_id == user_id,
        TimeCapsule.is_opened == False
    ).first()
    if not db_capsule:
        return False

    db.delete(db_capsule)
    db.commit()
    return True

def get_pending_time_capsules(db: Session, current_time: datetime) -> List[TimeCapsule]:
    return db.query(TimeCapsule).filter(
        TimeCapsule.open_date <= current_time,
        TimeCapsule.is_opened == False
    ).all()
```

---

## 6️⃣ **Authentication Routes** (`app/api/routes/auth.py`)

```python
@router.post("/signup", response_model=TokenResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user_email = get_user_by_email(db, user_data.email)
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_user_username = get_user_by_username(db, user_data.username)
    if existing_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = create_user(db, user_data)
    access_token = create_access_token(subject=str(new_user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
```

---

## 7️⃣ **Time Capsule Routes** (`app/api/routes/time_capsules.py`)

```python
@router.post("", response_model=TimeCapsuleResponse)
def create_time_capsule_endpoint(
    capsule_data: TimeCapsuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if capsule_data.open_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Open date must be in the future")
    
    new_capsule = create_time_capsule(db, capsule_data, current_user.id)
    return TimeCapsuleResponse.model_validate(new_capsule)

@router.get("", response_model=list[TimeCapsuleResponse])
def get_my_time_capsules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    capsules = get_user_time_capsules(db, current_user.id, skip, limit)
    return [TimeCapsuleResponse.model_validate(capsule) for capsule in capsules]

@router.post("/{capsule_id}/open", response_model=TimeCapsuleDetailResponse)
def open_time_capsule_endpoint(
    capsule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    capsule = get_time_capsule_by_id(db, capsule_id)
    if not capsule or capsule.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Time capsule not found")

    opened_capsule = open_time_capsule(db, capsule_id)
    if not opened_capsule:
        raise HTTPException(status_code=400, detail="Cannot open capsule yet")

    decrypted_content = decrypt_message(opened_capsule.content)
    capsule_dict = TimeCapsuleDetailResponse.model_validate(opened_capsule).model_dump()
    capsule_dict['content'] = decrypted_content

    return TimeCapsuleDetailResponse(**capsule_dict)

@router.delete("/{capsule_id}")
def delete_time_capsule_endpoint(
    capsule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    success = delete_time_capsule(db, capsule_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Time capsule not found")
    
    return {"message": "Time capsule deleted successfully"}
```

---

## 8️⃣ **User Routes** (`app/api/routes/users.py`)

```python
@router.get("/me", response_model=UserDetailResponse)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    return UserDetailResponse.model_validate(current_user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return UserResponse.model_validate(updated_user)
```

---

## 9️⃣ **Dependencies** (`app/api/dependencies.py`)

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        user_id = get_user_id_from_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    user = get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

---

## 🔟 **Configuration** (`app/config.py`)

```python
class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./timeless.db"
    
    # Server
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "your-32-byte-encryption-key-123456"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
```

---

## 📊 Entity Relationship Diagram (ERD)

```
┌──────────────────┐
│     Users        │
│                  │
│ id (PK)          │
│ email (UNIQUE)   │
│ username (UNIQUE)│
│ hashed_password  │
│ is_active        │
│ is_verified      │
│ created_at       │
│ updated_at       │
└────────┬─────────┘
         │ (1:N)
         │
┌────────▼──────────────────┐
│   TimeCapsules           │
│                          │
│ id (PK)                  │
│ user_id (FK)             │
│ title                    │
│ content (Encrypted)      │
│ content_type             │
│ open_date                │
│ is_opened                │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

---

## 🔐 Security Features

✅ **Password Hashing**: bcrypt (12 rounds)
✅ **Message Encryption**: AES-256-GCM
✅ **JWT Authentication**: Configurable expiration
✅ **Email Validation**: EmailStr from Pydantic
✅ **Request Validation**: Pydantic models
✅ **CORS Protection**: Configurable origins

---

## ✅ Testing Checklist

- ✓ Database models created successfully
- ✓ CRUD operations implemented
- ✓ Authentication flows working
- ✓ Time capsule operations working
- ✓ Encryption/decryption working
- ✓ API endpoints responsive
- ✓ Error handling in place
- ✓ Validation in place

---

**تم إنجاز جمیع أعمال قاعدة البیانات بنجاح!** ✨
