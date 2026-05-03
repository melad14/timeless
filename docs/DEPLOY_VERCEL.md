# نشر Timeless على Vercel

المشروع يستخدم **MongoDB** (PyMongo) ونقطة دخول FastAPI في `app/main.py`.

## 1. قاعدة البيانات

- عيّن **`MONGODB_URI`** (مثلاً من [MongoDB Atlas](https://www.mongodb.com/atlas)) في **Vercel → Settings → Environment Variables**.
- عيّن **`MONGODB_DB_NAME`** إن كان اسم قاعدة البيانات في الـ URI مختلفاً عن `timeless` (الافتراضي `timeless`).
- **SQLite / PostgreSQL لم تعد مستخدمة** في هذا المشروع.

## 2. متغيرات بيئة إضافية على Vercel

| المتغير | ملاحظات |
|---------|---------|
| `MONGODB_URI` | `mongodb+srv://...` مع المستخدم وكلمة المرور |
| `MONGODB_DB_NAME` | اختياري؛ افتراضي `timeless` |
| `SECRET_KEY` | JWT |
| `ENCRYPTION_KEY` | مفتاح التشفير (ثابت بين النشرات) |
| `DEBUG` | `False` للإنتاج |
| `CORS_ORIGINS` | JSON أو مفصولة بفواصل |

راجع `.env.example`.

## 3. CORS

أضف عنوان الفرونت إند في `CORS_ORIGINS`.

## 4. النشر

اربط المستودع بـ Vercel أو استخدم `vercel --prod`. بعد النشر تحقق من `/docs` و`/health`.

## 5. GitHub

```bash
git remote add origin https://github.com/melad14/timeless.git
git branch -M main
git push -u origin main
```

إذا وُجد `origin` مسبقاً: `git remote set-url origin https://github.com/melad14/timeless.git`.
