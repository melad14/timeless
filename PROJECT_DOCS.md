# 📚 دليل مشروع Timeless - Backend API

## مقدمة عن المشروع

**Timeless** هو تطبيق كبسولات زمنية آمن يسمح للمستخدمين بإنشاء رسائل مشفرة تُفتح في تاريخ محدد في المستقبل. المشروع مبني باستخدام **FastAPI** مع قاعدة بيانات **SQLAlchemy** وتشفير **AES-256-GCM** للرسائل.

### الميزات الرئيسية
- 🔐 **أمان متقدم**: تشفير AES-256-GCM للرسائل
- 👤 **إدارة المستخدمين**: تسجيل، تسجيل دخول، تحديث الملف الشخصي
- ⏰ **كبسولات زمنية**: إنشاء رسائل تُفتح في المستقبل
- 📱 **API جاهز للفرونت اند**: RESTful API مع توثيق تلقائي
- 🛡️ **حماية JWT**: رموز أمان محمية للوصول
- 🔒 **تشفير كلمات المرور**: bcrypt hashing

---

## متطلبات النظام

### البرمجيات المطلوبة
- **Python 3.10** أو أحدث
- **pip** (مثبت عادة مع Python)
- **Git** (اختياري للتحميل من GitHub)

### المكتبات المطلوبة
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pycryptodome==3.19.0
bcrypt==4.1.2
PyJWT==2.8.0
email-validator==2.1.0
python-dotenv==1.0.0
requests==2.31.0
httpx==0.25.2
```

---

## 🚀 خطوات التثبيت والتشغيل

### الخطوة 1: تحميل المشروع

```bash
# تحميل من GitHub (إذا كان متوفراً)
git clone https://github.com/your-repo/timeless.git
cd timeless

# أو نسخ الملفات يدوياً إلى مجلد جديد
```

### الخطوة 2: إنشاء البيئة الافتراضية

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### الخطوة 3: تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### الخطوة 4: إعداد متغيرات البيئة

```bash
# نسخ ملف البيئة النموذجي
cp .env.example .env
```

**تحرير ملف `.env` وتعديل القيم التالية:**

```env
# قاعدة البيانات
DATABASE_URL=sqlite:///./timeless.db

# الخادم
DEBUG=True
HOST=0.0.0.0
PORT=8000

# الأمان (غيّر هذه القيم في الإنتاج!)
SECRET_KEY=your-super-secret-key-change-this-in-production-32-chars-min
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENCRYPTION_KEY=your-32-byte-encryption-key-change-this-too-123456789

# CORS (أضف دومين الفرونت اند الخاص بك)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### الخطوة 5: تشغيل الخادم

```bash
# للتطوير مع إعادة التحميل التلقائي
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# للإنتاج
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### الخطوة 6: التحقق من التشغيل

افتح المتصفح واذهب إلى: `http://localhost:8000/docs`

ستجد واجهة Swagger UI مع جميع الـ endpoints المتاحة.

---

## 📋 شرح مفصل للـ API Endpoints

### 🔐 Authentication Endpoints

#### 1. تسجيل مستخدم جديد
```
POST /api/v1/auth/signup
```

**الطلب:**
```json
{
  "email": "user@example.com",
  "username": "myusername",
  "password": "securepassword123",
  "phone_number": "+1234567890"
}
```

**الاستجابة الناجحة:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "myusername",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-04-25T10:00:00",
    "updated_at": "2026-04-25T10:00:00"
  }
}
```

**أخطاء محتملة:**
- `400 Bad Request`: البريد الإلكتروني أو اسم المستخدم موجود مسبقاً
- `422 Unprocessable Entity`: بيانات غير صحيحة

#### 2. تسجيل الدخول
```
POST /api/v1/auth/login
```

**الطلب:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**الاستجابة الناجحة:** نفس استجابة التسجيل

**أخطاء محتملة:**
- `401 Unauthorized`: بريد إلكتروني أو كلمة مرور خاطئة

---

### 👤 User Management Endpoints

#### 3. الحصول على معلومات المستخدم الحالي
```
GET /api/v1/users/me
```

**Headers مطلوبة:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**الاستجابة الناجحة:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myusername",
  "phone_number": "+1234567890",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-04-25T10:00:00",
  "updated_at": "2026-04-25T10:00:00"
}
```

#### 4. الحصول على مستخدم بالـ ID
```
GET /api/v1/users/{user_id}
```

**الاستجابة الناجحة:** معلومات المستخدم (بدون كلمة المرور)

**أخطاء محتملة:**
- `404 Not Found`: المستخدم غير موجود

#### 5. تحديث معلومات المستخدم
```
PUT /api/v1/users/me
```

**الطلب:**
```json
{
  "username": "newusername",
  "phone_number": "+0987654321"
}
```

**الاستجابة الناجحة:** معلومات المستخدم المحدثة

#### 6. إلغاء تفعيل الحساب
```
DELETE /api/v1/users/me
```

**الاستجابة الناجحة:** `204 No Content`

---

### ⏰ Time Capsule Endpoints

#### 7. إنشاء كبسولة زمنية جديدة
```
POST /api/v1/time-capsules
```

**Headers مطلوبة:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**الطلب:**
```json
{
  "title": "رسالة لنفسي في المستقبل",
  "content": "محتوى الرسالة المشفر",
  "content_type": "text",
  "open_date": "2027-12-31T23:59:59"
}
```

**ملاحظات مهمة:**
- `content`: يجب أن يكون المحتوى مشفراً من جانب الفرونت اند
- `open_date`: يجب أن يكون تاريخ في المستقبل
- `content_type`: `"text"`, `"image"`, أو `"video"`

**الاستجابة الناجحة:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "رسالة لنفسي في المستقبل",
  "content": "encrypted_content_here",
  "content_type": "text",
  "open_date": "2027-12-31T23:59:59",
  "is_opened": false,
  "created_at": "2026-04-25T10:00:00",
  "updated_at": "2026-04-25T10:00:00"
}
```

**أخطاء محتملة:**
- `400 Bad Request`: تاريخ الفتح في الماضي
- `401 Unauthorized`: رمز غير صحيح

#### 8. الحصول على كبسولات المستخدم
```
GET /api/v1/time-capsules
```

**Parameters:**
- `skip`: عدد الكبسولات المراد تخطيها (افتراضي: 0)
- `limit`: عدد الكبسولات المراد إرجاعها (1-100، افتراضي: 50)

**الاستجابة الناجحة:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "رسالة لنفسي",
    "content": "encrypted_content",
    "content_type": "text",
    "open_date": "2027-12-31T23:59:59",
    "is_opened": false,
    "created_at": "2026-04-25T10:00:00",
    "updated_at": "2026-04-25T10:00:00"
  }
]
```

#### 9. الحصول على الكبسولات المعلقة (غير المفتوحة)
```
GET /api/v1/time-capsules/pending
```

**الاستجابة الناجحة:** نفس تنسيق الـ endpoint السابق

#### 10. الحصول على الكبسولات المفتوحة (مع المحتوى المفكك)
```
GET /api/v1/time-capsules/opened
```

**الاستجابة الناجحة:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "رسالة لنفسي",
    "content": "المحتوى المفكك والمقروء",
    "content_type": "text",
    "open_date": "2026-04-24T23:59:59",
    "is_opened": true,
    "created_at": "2026-04-20T10:00:00",
    "updated_at": "2026-04-25T10:00:00",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "myusername",
      "is_active": true,
      "is_verified": false,
      "created_at": "2026-04-20T10:00:00",
      "updated_at": "2026-04-25T10:00:00"
    }
  }
]
```

#### 11. الحصول على كبسولة محددة
```
GET /api/v1/time-capsules/{capsule_id}
```

**الاستجابة الناجحة:** تفاصيل الكبسولة مع معلومات المستخدم

#### 12. تحديث كبسولة (قبل تاريخ الفتح فقط)
```
PUT /api/v1/time-capsules/{capsule_id}
```

**الطلب:** (حقول اختيارية)
```json
{
  "title": "عنوان جديد",
  "content": "محتوى مشفر جديد"
}
```

#### 13. فتح كبسولة زمنية
```
POST /api/v1/time-capsules/{capsule_id}/open
```

**الاستجابة الناجحة:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "رسالة لنفسي",
  "content": "المحتوى المفكك والمقروء",
  "content_type": "text",
  "open_date": "2026-04-24T23:59:59",
  "is_opened": true,
  "created_at": "2026-04-20T10:00:00",
  "updated_at": "2026-04-25T10:00:00",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "myusername",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-04-20T10:00:00",
    "updated_at": "2026-04-25T10:00:00"
  }
}
```

**أخطاء محتملة:**
- `400 Bad Request`: الكبسولة لم يحن وقت فتحها أو مفتوحة مسبقاً
- `403 Forbidden`: الكبسولة لا تنتمي للمستخدم
- `404 Not Found`: الكبسولة غير موجودة

#### 14. حذف كبسولة
```
DELETE /api/v1/time-capsules/{capsule_id}
```

**الاستجابة الناجحة:** `204 No Content`

---

## 🔗 دليل الربط مع الفرونت اند

### إعداد الاتصال الأساسي

#### 1. إعداد Axios في React/Vue/Angular

```javascript
// إعداد Axios للتعامل مع JWT
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// إنشاء instance من axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor لإضافة JWT token تلقائياً
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor للتعامل مع انتهاء الـ token
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // توجيه المستخدم لتسجيل الدخول
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### 2. إدارة حالة المستخدم (React مع Context)

```javascript
// AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from './api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // التحقق من صحة الـ token والحصول على معلومات المستخدم
      api.get('/users/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('access_token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await api.post('/auth/signup', userData);
      const { access_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Signup failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### التعامل مع التشفير

#### 1. تشفير المحتوى قبل الإرسال

```javascript
// crypto.js - دوال التشفير
import CryptoJS from 'crypto-js';

// مفتاح التشفير (يجب أن يطابق المفتاح في الباك اند)
const ENCRYPTION_KEY = process.env.REACT_APP_ENCRYPTION_KEY || 'your-32-byte-encryption-key-change-this-too-123456789';

// تشفير النص
export const encryptMessage = (message) => {
  try {
    const encrypted = CryptoJS.AES.encrypt(message, ENCRYPTION_KEY).toString();
    return encrypted;
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt message');
  }
};

// فك تشفير النص
export const decryptMessage = (encryptedMessage) => {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedMessage, ENCRYPTION_KEY);
    const decrypted = bytes.toString(CryptoJS.enc.Utf8);
    return decrypted;
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error('Failed to decrypt message');
  }
};
```

#### 2. إنشاء كبسولة زمنية مع التشفير

```javascript
// TimeCapsuleService.js
import api from './api';
import { encryptMessage } from './crypto';

class TimeCapsuleService {
  // إنشاء كبسولة جديدة
  async createCapsule(capsuleData) {
    try {
      // تشفير المحتوى قبل الإرسال
      const encryptedContent = encryptMessage(capsuleData.content);
      
      const payload = {
        ...capsuleData,
        content: encryptedContent
      };
      
      const response = await api.post('/time-capsules', payload);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create capsule');
    }
  }

  // الحصول على الكبسولات
  async getCapsules(params = {}) {
    try {
      const response = await api.get('/time-capsules', { params });
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch capsules');
    }
  }

  // الحصول على الكبسولات المفتوحة (المحتوى مفكك تلقائياً من الباك اند)
  async getOpenedCapsules(params = {}) {
    try {
      const response = await api.get('/time-capsules/opened', { params });
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch opened capsules');
    }
  }

  // فتح كبسولة
  async openCapsule(capsuleId) {
    try {
      const response = await api.post(`/time-capsules/${capsuleId}/open`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to open capsule');
    }
  }

  // تحديث كبسولة
  async updateCapsule(capsuleId, updateData) {
    try {
      // تشفير المحتوى إذا كان موجوداً
      let payload = { ...updateData };
      if (updateData.content) {
        payload.content = encryptMessage(updateData.content);
      }
      
      const response = await api.put(`/time-capsules/${capsuleId}`, payload);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update capsule');
    }
  }

  // حذف كبسولة
  async deleteCapsule(capsuleId) {
    try {
      await api.delete(`/time-capsules/${capsuleId}`);
      return true;
    } catch (error) {
      throw new Error('Failed to delete capsule');
    }
  }
}

export default new TimeCapsuleService();
```

### أمثلة على استخدام الـ API في React

#### 1. مكون تسجيل الدخول

```javascript
// Login.js
import React, { useState } from 'react';
import { useAuth } from './AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(email, password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="login-form">
      <h2>تسجيل الدخول</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>البريد الإلكتروني:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>كلمة المرور:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'جاري تسجيل الدخول...' : 'دخول'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

#### 2. مكون إنشاء كبسولة زمنية

```javascript
// CreateCapsule.js
import React, { useState } from 'react';
import TimeCapsuleService from './TimeCapsuleService';

const CreateCapsule = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [openDate, setOpenDate] = useState('');
  const [contentType, setContentType] = useState('text');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const capsuleData = {
        title,
        content,
        content_type: contentType,
        open_date: new Date(openDate).toISOString()
      };

      await TimeCapsuleService.createCapsule(capsuleData);
      
      setSuccess(true);
      // إعادة تعيين النموذج
      setTitle('');
      setContent('');
      setOpenDate('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-capsule">
      <h2>إنشاء كبسولة زمنية جديدة</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>العنوان:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        
        <div>
          <label>المحتوى:</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            rows="5"
          />
        </div>
        
        <div>
          <label>نوع المحتوى:</label>
          <select value={contentType} onChange={(e) => setContentType(e.target.value)}>
            <option value="text">نص</option>
            <option value="image">صورة</option>
            <option value="video">فيديو</option>
          </select>
        </div>
        
        <div>
          <label>تاريخ الفتح:</label>
          <input
            type="datetime-local"
            value={openDate}
            onChange={(e) => setOpenDate(e.target.value)}
            min={new Date().toISOString().slice(0, 16)}
            required
          />
        </div>
        
        {error && <div className="error">{error}</div>}
        {success && <div className="success">تم إنشاء الكبسولة بنجاح!</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? 'جاري الإنشاء...' : 'إنشاء الكبسولة'}
        </button>
      </form>
    </div>
  );
};

export default CreateCapsule;
```

#### 3. مكون عرض الكبسولات

```javascript
// CapsuleList.js
import React, { useState, useEffect } from 'react';
import TimeCapsuleService from './TimeCapsuleService';

const CapsuleList = () => {
  const [capsules, setCapsules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, pending, opened

  useEffect(() => {
    loadCapsules();
  }, [filter]);

  const loadCapsules = async () => {
    setLoading(true);
    setError('');
    
    try {
      let data;
      if (filter === 'opened') {
        data = await TimeCapsuleService.getOpenedCapsules();
      } else if (filter === 'pending') {
        data = await TimeCapsuleService.getCapsules(); // يمكن تحسين هذا
      } else {
        data = await TimeCapsuleService.getCapsules();
      }
      
      setCapsules(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCapsule = async (capsuleId) => {
    try {
      const openedCapsule = await TimeCapsuleService.openCapsule(capsuleId);
      // تحديث القائمة
      setCapsules(capsules.map(capsule => 
        capsule.id === capsuleId ? openedCapsule : capsule
      ));
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>جاري التحميل...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="capsule-list">
      <h2>كبسولاتي الزمنية</h2>
      
      <div className="filters">
        <button onClick={() => setFilter('all')}>الكل</button>
        <button onClick={() => setFilter('pending')}>المعلقة</button>
        <button onClick={() => setFilter('opened')}>المفتوحة</button>
      </div>
      
      <div className="capsules">
        {capsules.map(capsule => (
          <div key={capsule.id} className="capsule-card">
            <h3>{capsule.title}</h3>
            <p>تاريخ الفتح: {new Date(capsule.open_date).toLocaleDateString('ar')}</p>
            <p>الحالة: {capsule.is_opened ? 'مفتوحة' : 'معلقة'}</p>
            
            {capsule.is_opened ? (
              <div className="capsule-content">
                <p>{capsule.content}</p>
              </div>
            ) : (
              <button 
                onClick={() => handleOpenCapsule(capsule.id)}
                disabled={new Date(capsule.open_date) > new Date()}
              >
                {new Date(capsule.open_date) > new Date() ? 'لم يحن وقت الفتح' : 'فتح الكبسولة'}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CapsuleList;
```

---

## 🔧 استكشاف الأخطاء وإصلاحها

### مشاكل شائعة وحلولها

#### 1. خطأ "ModuleNotFoundError"
```
خطأ: ModuleNotFoundError: No module named 'fastapi'
```

**الحل:**
```bash
# تأكد من تفعيل البيئة الافتراضية
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# ثم تثبيت المكتبات
pip install -r requirements.txt
```

#### 2. خطأ "Port 8000 already in use"
```
خطأ: [Errno 48] Address already in use
```

**الحل:**
```bash
# استخدام port مختلف
uvicorn app.main:app --port 8001 --reload

# أو إيقاف العملية التي تستخدم الـ port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

#### 3. خطأ في قاعدة البيانات
```
خطأ: Database error
```

**الحل:**
```bash
# حذف ملف قاعدة البيانات وإعادة التشغيل
rm timeless.db

# ثم تشغيل الخادم (سينشئ قاعدة بيانات جديدة)
uvicorn app.main:app --reload
```

#### 4. خطأ في التشفير
```
خطأ: Failed to decrypt message
```

**الحل:**
- تأكد من أن مفتاح التشفير في الفرونت اند مطابق للباك اند
- تحقق من صحة البيانات المشفرة
- تأكد من عدم تغيير المفتاح بعد إنشاء الكبسولات

#### 5. خطأ "401 Unauthorized"
```
خطأ: Invalid token
```

**الحل:**
- تأكد من صحة الـ JWT token
- تحقق من انتهاء صلاحية الـ token (30 دقيقة افتراضياً)
- أعد تسجيل الدخول

#### 6. خطأ CORS
```
خطأ: CORS error
```

**الحل:**
- أضف دومين الفرونت اند إلى `CORS_ORIGINS` في ملف `.env`
- أعد تشغيل الخادم

---

## 🛡️ الأمان وأفضل الممارسات

### إعدادات الأمان المطلوبة

#### 1. متغيرات البيئة الحساسة
```env
# لا تستخدم هذه القيم في الإنتاج!
SECRET_KEY=generate-a-32-character-random-string
ENCRYPTION_KEY=generate-a-32-byte-random-key
```

#### 2. إعداد HTTPS في الإنتاج
```bash
# استخدم HTTPS في الإنتاج
uvicorn app.main:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

#### 3. مراقبة الخادم
- استخدم أدوات مثل Prometheus و Grafana
- قم بتسجيل الأخطاء والأنشطة المشبوهة
- راقب استخدام الموارد

#### 4. نسخ احتياطي لقاعدة البيانات
```bash
# نسخ احتياطي دوري
sqlite3 timeless.db .dump > backup.sql

# أو استخدم PostgreSQL في الإنتاج مع pg_dump
```

### أفضل الممارسات للفرونت اند

#### 1. التعامل الآمن مع الـ tokens
```javascript
// حفظ الـ token بشكل آمن
localStorage.setItem('access_token', token);

// التحقق من انتهاء الصلاحية
const token = localStorage.getItem('access_token');
if (token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  if (payload.exp * 1000 < Date.now()) {
    // Token منتهي الصلاحية
    localStorage.removeItem('access_token');
  }
}
```

#### 2. التحقق من صحة البيانات
```javascript
// التحقق من صحة تاريخ الفتح
const validateOpenDate = (date) => {
  const openDate = new Date(date);
  const now = new Date();
  return openDate > now;
};

// التحقق من قوة كلمة المرور
const validatePassword = (password) => {
  return password.length >= 8 && 
         /[A-Z]/.test(password) && 
         /[a-z]/.test(password) && 
         /[0-9]/.test(password);
};
```

#### 3. معالجة الأخطاء
```javascript
// معالجة أخطاء الشبكة
const handleApiError = (error) => {
  if (!error.response) {
    // مشكلة في الشبكة
    return 'تحقق من اتصال الإنترنت';
  }
  
  switch (error.response.status) {
    case 400:
      return 'بيانات غير صحيحة';
    case 401:
      return 'يجب تسجيل الدخول أولاً';
    case 403:
      return 'ليس لديك صلاحية للوصول';
    case 404:
      return 'الصفحة غير موجودة';
    case 500:
      return 'خطأ في الخادم، حاول مرة أخرى لاحقاً';
    default:
      return 'حدث خطأ غير متوقع';
  }
};
```

---

## 📊 مراقبة الأداء

### مؤشرات مهمة للمتابعة

#### 1. أداء الـ API
- متوسط وقت الاستجابة لكل endpoint
- معدل الأخطاء (error rate)
- عدد الطلبات في الدقيقة

#### 2. قاعدة البيانات
- حجم قاعدة البيانات
- عدد الاستعلامات البطيئة
- استخدام الذاكرة

#### 3. التشفير
- وقت عمليات التشفير/فك التشفير
- معدل فشل عمليات التشفير

### أدوات المراقبة المقترحة

#### 1. FastAPI Middleware للقياس
```python
# app/main.py
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

#### 2. تسجيل الأخطاء
```python
# إعداد logging
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 🚀 نشر التطبيق في الإنتاج

### خطوات النشر

#### 1. إعداد الخادم
```bash
# تثبيت Python و pip
sudo apt update
sudo apt install python3 python3-pip

# إنشاء مستخدم منفصل للتطبيق
sudo useradd -m -s /bin/bash timeless
sudo su - timeless
```

#### 2. إعداد PostgreSQL
```bash
# تثبيت PostgreSQL
sudo apt install postgresql postgresql-contrib

# إنشاء قاعدة بيانات
sudo -u postgres psql
CREATE DATABASE timeless_db;
CREATE USER timeless_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE timeless_db TO timeless_user;
\q
```

#### 3. إعداد البيئة
```bash
# نسخ الملفات
git clone https://github.com/your-repo/timeless.git
cd timeless

# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements.txt

# إعداد متغيرات البيئة
cp .env.example .env
# تحرير .env مع القيم المناسبة للإنتاج
```

#### 4. إعداد Nginx (اختياري)
```nginx
# /etc/nginx/sites-available/timeless
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 5. إعداد SSL مع Let's Encrypt
```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com
```

#### 6. إعداد Systemd Service
```ini
# /etc/systemd/system/timeless.service
[Unit]
Description=Timeless API
After=network.target

[Service]
User=timeless
WorkingDirectory=/home/timeless/timeless
Environment="PATH=/home/timeless/timeless/venv/bin"
ExecStart=/home/timeless/timeless/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل وتشغيل الخدمة
sudo systemctl enable timeless
sudo systemctl start timeless
sudo systemctl status timeless
```

---

## 📞 الدعم والمساعدة

### الموارد المفيدة

#### 1. توثيق FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

#### 2. أدوات التطوير
- [Swagger UI](http://localhost:8000/docs) - توثيق تفاعلي
- [ReDoc](http://localhost:8000/redoc) - توثيق بديل
- [SQLite Browser](https://sqlitebrowser.org/) - لفحص قاعدة البيانات

#### 3. أمثلة إضافية
- [FastAPI Examples](https://github.com/tiangolo/fastapi/tree/master/docs_src)
- [SQLAlchemy Examples](https://sqlalchemy.org/)

### نصائح للمطورين

#### 1. اختبار الـ API
```bash
# استخدم pytest للاختبارات
pip install pytest httpx
pytest tests/
```

#### 2. تطوير الفرونت اند
- استخدم TypeScript للتحقق من الأنواع
- طبق مبادئ SOLID في الكود
- استخدم React/Vue مع state management

#### 3. الأمان
- قم بتدوير مفاتيح التشفير دورياً
- راقب محاولات الدخول الفاشلة
- طبق rate limiting على الـ API

---

**تم إنشاء هذا الدليل بواسطة AI Assistant لمشروع Timeless. للمساعدة الإضافية أو الاستفسارات، يرجى مراجعة ملفات المشروع أو التوثيق الرسمي.**</content>
<parameter name="filePath">c:\Users\View\Downloads\timeless\timeless\PROJECT_DOCS.md