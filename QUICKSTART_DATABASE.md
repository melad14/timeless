# 🚀 كيفية تشغيل Timeless Backend

## Prerequisites

- Python 3.10 أو أحدث
- pip (مثبت عادة مع Python)

---

## Installation Steps

### 1. إنشاء Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 3. التكوين

```bash
# Copy environment file
cp .env.example .env

# تحرير .env وإضافة القيم المناسبة
# - database_url (SQLite للتطوير، PostgreSQL للإنتاج)
# - secret_key (مفتاح سري قوي 32+ حرف)
# - encryption_key (مفتاح تشفير 32 بايت)
```

### 4. تشغيل الخادم

```bash
# الطريقة 1: مع auto-reload (للتطوير)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# الطريقة 2: بدون reload (للإنتاج)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# الطريقة 3: محدد عدد العمليات
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## Testing the API

### استخدام Swagger UI

اذهب إلى: `http://localhost:8000/docs`

ستجد:
- جميع الـ endpoints
- تفاصيل الطلب والاستجابة
- القدرة على الاختبار مباشرة

### استخدام cURL

```bash
# 1. SignUp
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123",
    "phone_number": "+1234567890"
  }'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-04-11T10:00:00",
    "updated_at": "2026-04-11T10:00:00"
  }
}

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'

# 3. Get Current User (مع Token)
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 4. Create Time Capsule
curl -X POST "http://localhost:8000/api/v1/time-capsules" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "رسالة لنفسي",
    "content": "محتوى الرسالة",
    "content_type": "text",
    "open_date": "2026-12-31T23:59:59"
  }'

# 5. Get My Time Capsules
curl -X GET "http://localhost:8000/api/v1/time-capsules" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 6. Open Time Capsule (بعد انقضاء الوقت)
curl -X POST "http://localhost:8000/api/v1/time-capsules/1/open" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### استخدام Python

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# 1. SignUp
response = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": "user@example.com",
    "username": "myuser",
    "password": "password123",
    "phone_number": "+1234567890"
})
print(response.json())
token = response.json()["access_token"]

# 2. Create Time Capsule
headers = {"Authorization": f"Bearer {token}"}
future_date = (datetime.now() + timedelta(days=365)).isoformat()

response = requests.post(
    f"{BASE_URL}/time-capsules",
    headers=headers,
    json={
        "title": "رسالتي في المستقبل",
        "content": "محتوى مهم",
        "content_type": "text",
        "open_date": future_date
    }
)
print(response.json())

# 3. Get All Capsules
response = requests.get(f"{BASE_URL}/time-capsules", headers=headers)
capsules = response.json()
print(f"عدد الكبسولات: {len(capsules)}")
for capsule in capsules:
    print(f"- {capsule['title']} (سيفتح في {capsule['open_date']})")
```

---

## Use PostMan

1. **استيراد URL:** `http://localhost:8000/openapi.json`
2. ستتم استيراد جميع الـ endpoints تلقائياً
3. أضف Authorization header مع Bearer token

---

## Database

### SQLite (التطوير - الإعدادي)

قاعدة البيانات تُنشأ تلقائياً في:
```
./timeless.db
```

### PostgreSQL (الإنتاج)

تحديث `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/timeless_db
```

---

## Troubleshooting

### خطأ: ModuleNotFoundError

```bash
# التأكد من تفعيل virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# ثم تثبيت المتطلبات
pip install -r requirements.txt
```

### خطأ: "Port 8000 already in use"

```bash
# استخدام port مختلف
uvicorn app.main:app --port 8001 --reload
```

### خطأ في قاعدة البيانات

```bash
# حذف sqlite db واعادة البدء
rm timeless.db

# ثم تشغيل الخادم (سينشئه من جديد)
uvicorn app.main:app --reload
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | إنشاء حساب جديد |
| POST | `/auth/login` | تسجيل الدخول |
| GET | `/users/me` | معلومات الملف الشخصي |
| GET | `/users/{id}` | معلومات مستخدم آخر |
| PUT | `/users/me` | تحديث الملف الشخصي |
| POST | `/time-capsules` | إنشاء كبسولة زمنية |
| GET | `/time-capsules` | عرض كل الكبسولات |
| GET | `/time-capsules/pending` | الكبسولات المنتظرة |
| GET | `/time-capsules/opened` | الكبسولات المفتوحة |
| GET | `/time-capsules/{id}` | تفاصيل كبسولة |
| PUT | `/time-capsules/{id}` | تحديث الكبسولة |
| POST | `/time-capsules/{id}/open` | فتح الكبسولة |
| DELETE | `/time-capsules/{id}` | حذف الكبسولة |
| POST | `/time-capsules/check-ready` | فحص الكبسولات الجاهزة |

---

## Important Notes

⚠️ **أمان:**
- عدّل `secret_key` و `encryption_key` في `.env`
- استخدم HTTPS في الإنتاج
- حماية متغيرات البيئة

⚠️ **الإنتاج:**
- استخدم PostgreSQL بدلاً من SQLite
- أضف مراقبة (Monitoring)
- استخدم Redis للـ caching
- أضف HTTPS و SSL

---

**Happy Coding! 🚀**
