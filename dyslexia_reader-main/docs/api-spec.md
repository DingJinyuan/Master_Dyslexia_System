# API 接口文档

Base URL: `/api/v1`

## 1. 用户认证

### 1.1 注册申请
**POST** `/auth/register`

请求体：
```json
{
  "email": "user@example.com",
  "username": "reader01",
  "password": "Password@123"
}
```

响应：
```json
{
  "message": "注册申请已提交，需管理员审批后方可登录"
}
```

---

### 1.2 登录
**POST** `/auth/login`

请求体：
```json
{
  "username_or_email": "reader01",
  "password": "Password@123"
}
```

响应：
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

---

### 1.3 修改密码申请
**POST** `/auth/password-change-request`

请求头：
```text
Authorization: Bearer <token>
```

请求体：
```json
{
  "old_password": "Password@123",
  "new_password": "NewPassword@123"
}
```

响应：
```json
{
  "message": "修改密码申请已提交，需管理员审批"
}
```

## 2. 文档模块

### 2.1 上传 PDF / 图片
**POST** `/documents/upload`

请求头：
```text
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

表单字段：
- `file`: PDF / PNG / JPEG / WEBP

响应：
```json
{
  "id": 1,
  "original_filename": "article.pdf",
  "file_type": "pdf",
  "file_url": "storage/xxxx.pdf",
  "extracted_text": "这里是提取出的文本",
  "processing_status": "done",
  "created_at": "2026-03-08T12:00:00"
}
```

---

### 2.2 获取文档详情
**GET** `/documents/{document_id}`

请求头：
```text
Authorization: Bearer <token>
```

响应：同上。

## 3. 音频与高亮模块

### 3.1 创建朗读音频
**POST** `/audio/tts`

请求头：
```text
Authorization: Bearer <token>
```

请求体：
```json
{
  "document_id": 1,
  "speed": 1.0,
  "voice": "female_soft",
  "return_word_marks": true
}
```

响应：
```json
{
  "audio_track_id": 10,
  "audio_url": "mock_audio/female_soft_1_0.mp3",
  "speed": 1.0,
  "sync_marks": [
    {"index": 0, "word": "This", "start_ms": 0, "end_ms": 280},
    {"index": 1, "word": "is", "start_ms": 281, "end_ms": 560}
  ]
}
```

说明：
- 播放 / 暂停 / 继续 / 拖动由前端播放器实现。
- 高亮同步依赖 `sync_marks`。

---

### 3.2 获取音频轨道
**GET** `/audio/tracks/{track_id}`

请求头：
```text
Authorization: Bearer <token>
```

响应：同上。

## 4. 管理员审批模块

### 4.1 初始化管理员
**POST** `/admin/seed-admin`

响应：
```json
{
  "message": "默认管理员已创建：admin / Admin@123456"
}
```

---

### 4.2 查看审批列表
**GET** `/admin/approval-requests`

请求头：
```text
Authorization: Bearer <admin-token>
```

响应：
```json
[
  {
    "id": 1,
    "user_id": 2,
    "request_type": "register",
    "payload_json": "{\"email\":\"user@example.com\",\"username\":\"reader01\"}",
    "status": "pending",
    "reviewed_by": null,
    "reviewed_at": null,
    "created_at": "2026-03-08T12:00:00"
  }
]
```

---

### 4.3 审批通过
**POST** `/admin/approval-requests/{request_id}/approve`

请求头：
```text
Authorization: Bearer <admin-token>
```

响应：
```json
{
  "message": "审批通过"
}
```

---

### 4.4 审批驳回
**POST** `/admin/approval-requests/{request_id}/reject`

请求头：
```text
Authorization: Bearer <admin-token>
```

响应：
```json
{
  "message": "审批驳回"
}
```

## 5. 第三方 AI 接口约定

## 5.1 OCR 接口
后端适配器位置：`app/services/adapters/ocr_adapter.py`

建议 HTTP 调用格式：
```http
POST /ocr
Content-Type: multipart/form-data
Authorization: Bearer <ocr-api-key>
```

返回：
```json
{
  "text": "识别到的文字内容"
}
```

## 5.2 TTS 接口
后端适配器位置：`app/services/adapters/tts_adapter.py`

建议 HTTP 调用格式：
```http
POST /tts
Content-Type: application/json
Authorization: Bearer <tts-api-key>
```

请求：
```json
{
  "text": "需要朗读的文本",
  "speed": 1.0,
  "voice": "female_soft",
  "return_word_marks": true
}
```

返回：
```json
{
  "audio_url": "https://storage.example.com/audio/abc.mp3",
  "marks": [
    {"index": 0, "word": "需要", "start_ms": 0, "end_ms": 150}
  ]
}
```
