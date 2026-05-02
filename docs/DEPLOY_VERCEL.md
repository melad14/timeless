# نشر Timeless على Vercel

المشروع يتبع نمط FastAPI الرسمي (`app/main.py` مع متغير `app`). Vercel يكتشف التطبيق تلقائياً عند ربط المستودع أو استخدام `vercel --prod` ([الوثائق](https://vercel.com/docs/frameworks/backend/fastapi)).

## 1. قاعدة البيانات

- **SQLite غير مناسب لـ Vercel**: نظام الملفات للدوال قصيرة العمر ولن يحفظ `*.db` بشكل موثوق.
- في الإنتاج عيّن **`DATABASE_URL`** إلى PostgreSQL (مثلاً [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)، Neon، Supabase، إلخ).
- الصيغة: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require`
- تمت إضافة **`psycopg2-binary`** في `requirements.txt` لدعم PostgreSQL.

## 2. متغيرات البيئة على Vercel

في لوحة المشروع: **Settings → Environment Variables**، أضف على الأقل:

| المتغير | ملاحظات |
|---------|---------|
| `DATABASE_URL` | اتصال PostgreSQL |
| `SECRET_KEY` | مفتاح JWT قوي (≥ 32 حرفاً) |
| `ENCRYPTION_KEY` | مفتاح التشفير (يُشتق داخلياً عبر PBKDF2؛ احتفظ به ثابتاً بين النشرات) |
| `DEBUG` | `False` للإنتاج |
| `CORS_ORIGINS` | قائمة JSON أو مفصولة بفواصل، مثال: `https://your-frontend.vercel.app,https://www.yourdomain.com` |

راجع `.env.example` للقائمة الكاملة.

## 3. CORS

- أضف **عنوان الفرونت إند الفعلي** (بما فيه `https://`) في `CORS_ORIGINS` وإلا المتصفح سيمنع الطلبات.

## 4. النشر

1. ادفع الكود إلى GitHub.
2. في Vercel: **Add New Project** واختر المستودع.
3. Framework: يُكتشف كـ FastAPI / Python؛ اترك الإعدادات الافتراضية ما لم تحتاج أمر بناء مخصص.
4. بعد أول نشر، افتح `/docs` على الدومين للتحقق.

## 5. تشغيل محلي مع Vercel CLI (اختياري)

```bash
npm i -g vercel
vercel dev
```

يتطلب CLI إصداراً حديثاً (انظر وثائق Vercel).

## 6. GitHub

```bash
git remote add origin https://github.com/melad14/timeless.git
git branch -M main
git push -u origin main
```

إذا كان `origin` موجوداً مسبقاً، استخدم `git remote set-url origin https://github.com/melad14/timeless.git`.
