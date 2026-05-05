# توثيق واجهة الـ API للفرونت إند — Timeless

هذا المستند يشرح كيف يربط تطبيق الويب/الموبايل (الفرونت إند) بخادم **Timeless** (FastAPI).

- عنوان القاعدة الإنتاجي: `https://timeless-lemon.vercel.app/api/v1`
- عنوان القاعدة المحلي: `http://localhost:8000/api/v1`

جميع طلبات الـ API في المشروع تستخدم البادئة **`/api/v1`**.

## 1. تشغيل الخادم محلياً

- الافتراضي من الإعدادات: `host=0.0.0.0`, `port=8000`.
- عنوان القاعدة المحلي للـ API: `http://localhost:8000/api/v1`
- عنوان القاعدة الإنتاجي للـ API: `https://timeless-lemon.vercel.app/api/v1`
- وثائق تفاعلية (Swagger): `http://localhost:8000/docs`
- فحص الصحة: `GET /health` (يعمل على الجذر `https://timeless-lemon.vercel.app/health` في الإنتاج)

## 2. CORS

القيم الافتراضية في `app/config.py` تسمح بـ:

- `http://localhost:3000`
- `http://localhost:8000`

إذا كان الفرونت يعمل على منفذ أو دومين آخر، يجب إضافته في متغير البيئة/الإعدادات على الخادم (`cors_origins`).

## 3. المصادقة (JWT)

- بعد **تسجيل الدخول** أو **إنشاء حساب**، الاستجابة تحتوي على:
  - `access_token`: سلسلة JWT
  - `token_type`: دائماً `"bearer"`
  - `user`: بيانات المستخدم
- لجميع الطلبات المحمية، أرسل الهيدر:

```http
Authorization: Bearer <access_token>
```

- مدة صلاحية التوكن الافتراضية: **30 دقيقة** (`access_token_expire_minutes`).
- عند انتهاء الصلاحية أو التوكن غير الصالح: استجابة **401** مع `detail` مناسب.

## 4. تنسيق الأخطاء

- **400**: طلب غير صالح (مثلاً تاريخ فتح الكبسولة في الماضي، أو تحديث غير مسموح).
- **401**: غير مصدّق أو بيانات دخول خاطئة.
- **403**: حساب معطّل.
- **404**: مورد غير موجود أو لا يخص المستخدم الحالي.
- **500**: خطأ داخلي (غالباً مع رسالة عامة `Internal server error`).

الجسم غالباً يكون JSON:

```json
{ "detail": "رسالة أو نص السبب" }
```

## 5. التواريخ والوقت

- الحقول من نوع `datetime` (مثل `open_date`, `created_at`) تُرسل وتُستقبل بصيغة **ISO 8601** (مثال: `2026-12-31T10:00:00Z` أو مع أوفست منطقة زمنية).
- الخادم يقارن تواريخ الفتح بـ **UTC** (`datetime.utcnow()` في منطق الكبسولات).

## 6. معرّفات MongoDB

- **`user.id` و`user_id` و`id` للكبسولة** في JSON هي **سلاسل نصية** تمثل `ObjectId` في MongoDB (غالباً 24 حرفاً hex)، وليست أرقاماً صحيحة.

## 7. محتوى الكبسولة الزمنية والتشفير

- عند **الإنشاء** (`POST /time-capsules`) و**التحديث** (`PUT`) ترسل الحقل `content` كنص **عادي (plaintext)**؛ الخادم يقوم بالتشفير (AES-GCM) قبل التخزين.
- في الاستجابات **للكبسولات غير المفتوحة**، الحقل `content` في JSON يعكس ما في قاعدة البيانات أي **نص مشفّر (Base64)** وليس المحتوى الأصلي. لا تعرضه للمستخدم كنص رسالة إلا إذا فهمتم أنه مشفر.
- عند **فتح** الكبسولة أو جلب الكبسولات **المفتوحة**، الخادم يعيد `content` **مفكوك التشفير** (نص واضح) في الاستجابة.

## 8. جدول المسارات (ملخص)

| الطريقة | المسار | يحتاج توكن | الوصف |
|--------|--------|------------|--------|
| GET | `/` | لا | معلومات ترحيبية |
| GET | `/health` | لا | حالة الخادم |
| POST | `/api/v1/auth/signup` | لا | تسجيل مستخدم جديد |
| POST | `/api/v1/auth/login` | لا | تسجيل دخول |
| GET | `/api/v1/users/me` | نعم | الملف الشخصي للمستخدم الحالي |
| PUT | `/api/v1/users/me` | نعم | تحديث الملف (username, phone_number) |
| DELETE | `/api/v1/users/me` | نعم | تعطيل الحساب (204 بدون جسم) |
| GET | `/api/v1/users/{user_id}` | لا | مستخدم بالمعرّف (عام) |
| POST | `/api/v1/time-capsules` | نعم | إنشاء كبسولة (`open_date` يجب أن يكون في المستقبل) |
| GET | `/api/v1/time-capsules` | نعم | قائمة كبسولاتي (`skip`, `limit`) |
| GET | `/api/v1/time-capsules/pending` | نعم | المعلقة (غير مفتوحة) |
| GET | `/api/v1/time-capsules/opened` | نعم | المفتوحة مع محتوى مفكوك |
| GET | `/api/v1/time-capsules/{id}` | نعم | تفاصيل؛ المحتوى يُفك إن كانت مفتوحة |
| PUT | `/api/v1/time-capsules/{id}` | نعم | تحديث (فقط إن لم تُفتح وقبل موعد الفتح) |
| POST | `/api/v1/time-capsules/{id}/open` | نعم | فتح عند حلول الموعد |
| DELETE | `/api/v1/time-capsules/{id}` | نعم | حذف (فقط إن لم تُفتح) |
| POST | `/api/v1/time-capsules/check-ready` | لا | مهمة مجدولة داخلية؛ تفتح الكبسولات التي حان وقتها |
| POST | `/api/v1/conversations` | نعم | إنشاء محادثة جديدة مع أعضاء محددين |
| GET | `/api/v1/conversations` | نعم | جلب محادثات المستخدم الحالية |
| GET | `/api/v1/conversations/{id}` | نعم | جلب تفاصيل المحادثة مع الأعضاء |
| PUT | `/api/v1/conversations/{id}` | نعم | تحديث اسم المحادثة |
| POST | `/api/v1/conversations/{id}/members/{user_id}` | نعم | إضافة عضو إلى المحادثة |
| DELETE | `/api/v1/conversations/{id}/members/{user_id}` | نعم | إزالة عضو من المحادثة |
| DELETE | `/api/v1/conversations/{id}` | نعم | حذف المحادثة |
| POST | `/api/v1/messages` | نعم | إرسال رسالة في محادثة |
| GET | `/api/v1/messages/{id}` | نعم | جلب رسالة محددة |
| PUT | `/api/v1/messages/{id}` | نعم | تعديل رسالة المرسل |
| POST | `/api/v1/messages/{id}/read` | نعم | وضع علامة قراءة على رسالة |
| POST | `/api/v1/messages/{id}/favorite` | نعم | تبديل حال المفضلة للرسالة |
| DELETE | `/api/v1/messages/{id}` | نعم | حذف رسالة |
| GET | `/api/v1/messages/conversation/{conversation_id}` | نعم | جلب رسائل محادثة |
| GET | `/api/v1/messages/user/favorites` | نعم | جلب رسائل المستخدم المفضلة |
| POST | `/api/v1/whatsapp/send` | نعم | إرسال رسالة WhatsApp (غير رسمي، محلي فقط) |

**ملاحظة:** ملفات مسارات `conversations` و `messages` مسجلة في `app/api/__init__.py` وتعمل الآن ضمن واجهة الـ API.

## 9. أجسام JSON (أمثلة)

### تسجيل حساب — `POST /api/v1/auth/signup`

```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "min8chars",
  "phone_number": "+966500000000"
}
```

### تسجيل دخول — `POST /api/v1/auth/login`

```json
{
  "email": "user@example.com",
  "password": "min8chars"
}
```

### استجابة التوكن (signup / login)

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "username": "username",
    "phone_number": "+966500000000",
    "is_active": true,
    "is_verified": false,
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### تحديث المستخدم — `PUT /api/v1/users/me`

```json
{
  "username": "new_name",
  "phone_number": "+966511111111"
}
```

### إنشاء كبسولة — `POST /api/v1/time-capsules`

```json
{
  "title": "رسالة للمستقبل",
  "content": "النص الذي سيراه المستخدم بعد فتح الكبسولة",
  "content_type": "text",
  "open_date": "2027-01-01T00:00:00Z"
}
```

`content_type` يجب أن يكون واحداً من: `"text"` | `"image"` | `"video"`.

### تحديث كبسولة — `PUT /api/v1/time-capsules/{id}`

جميع الحقول اختيارية:

```json
{
  "title": "عنوان جديد",
  "content": "محتوى جديد",
  "content_type": "text"
}
```

## 10. تكامل سريع من الفرونت (fetch)

```javascript
const BASE = 'https://timeless-lemon.vercel.app/api/v1';

async function login(email, password) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json(); // { access_token, token_type, user }
}

async function getMyCapsules(token) {
  const res = await fetch(`${BASE}/time-capsules?skip=0&limit=50`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

احفظ `access_token` في ذاكرة آمنة مناسبة للتطبيق (memory + refresh strategy أو تخزين محمي حسب منصتك).

## 11. ملف Postman

يُرفق مع المشروع ملف جاهز للاستيراد:

- `postman/Timeless-API.postman_collection.json`

بعد الاستيراد، عيّن المتغير `baseUrl` إلى:

```text
https://timeless-lemon.vercel.app/api/v1
```

وفي حال أردت اختبار `GET /` أو `GET /health` مباشرة من Postman، استخدم:

```text
https://timeless-lemon.vercel.app
```

ثم نفّذ **Login** ونسخ `access_token` إلى المتغير `accessToken` (أو استخدم سكربت الاختبار المرفق في طلبات Login إن وُجد`).

---

*إصدار الـ API حسب `app/main.py`: 1.0.0 — **Timeless - Time Capsule Backend**.*
