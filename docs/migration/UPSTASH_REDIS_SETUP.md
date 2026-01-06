# Hướng Dẫn Setup Upstash Redis (Free Tier)

**Thời gian:** ~5 phút

---

## Bước 1: Đăng Ký Upstash (FREE)

1. Truy cập: **https://upstash.com**
2. Click **"Start for Free"** hoặc **"Sign Up"**
3. Chọn **"Continue with GitHub"** (nhanh nhất)
4. Authorize Upstash app

---

## Bước 2: Tạo Redis Database

1. Sau khi đăng nhập, click **"Create Database"**
2. Điền thông tin:
   - **Name:** `mediai-cache`
   - **Type:** `Regional` (free tier)
   - **Region:** Chọn **US-East-1** (gần Render servers nhất)
   - **Eviction:** `Enable` (xóa key cũ khi đầy)
3. Click **"Create"**

---

## Bước 3: Copy Connection URL

1. Vào database vừa tạo → Tab **"Details"**
2. Tìm phần **"REST API"** hoặc **"Redis Connection"**
3. Copy **"UPSTASH_REDIS_REST_URL"** và **"UPSTASH_REDIS_REST_TOKEN"**

**HOẶC** copy **Redis URL** format:
```
redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
```

> ⚠️ **Lưu ý:** Upstash có 2 loại connection:
> - **REST API** (HTTPS) - Dùng cho serverless
> - **Redis Protocol** (redis://) - Dùng cho traditional apps ← **Chọn cái này**

---

## Bước 4: Thêm vào Render Environment

1. Truy cập: **https://dashboard.render.com**
2. Select service: **`mediai-7owz`** (backend)
3. Click **"Environment"** (left sidebar)
4. Click **"Add Environment Variable"**

**Thêm variable:**
- **Key:** `UPSTASH_REDIS_URL`
- **Value:** `redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379`

5. Click **"Save Changes"**
6. Render sẽ **auto-redeploy** (~2-3 phút)

---

## Bước 5: Verify Connection

Sau khi deploy xong, check Render logs:

**Thành công:**
```
✅ Connected to Upstash Redis
```

**Nếu lỗi:** Redis sẽ fallback và app vẫn chạy bình thường:
```
Redis connection failed: ... Caching disabled.
```

---

## 📊 Upstash Free Tier Limits

| Resource | Limit |
|----------|-------|
| Commands/day | 10,000 |
| Data size | 256 MB |
| Connections | 20 concurrent |

**Đủ dùng cho:** ~500 predictions/day + chat caching

---

## ✅ Done!

Sau khi setup xong, caching sẽ tự động:
- Cache prediction results (1 giờ TTL)
- Cache chat responses (30 phút TTL)
- Giảm response time từ ~500ms → ~50ms cho repeated queries

---

**Cần copy và đặt vào Render:**
```
UPSTASH_REDIS_URL=redis://default:xxxx@xxx.upstash.io:6379
```
