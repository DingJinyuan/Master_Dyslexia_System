# 阅读障碍辅助阅读应用后端（FastAPI）

本项目是一个面向阅读障碍群体的辅助阅读应用后端示例，支持：

- 用户注册、登录
- 注册申请需管理员审批
- 密码修改需管理员审批
- 上传图片 / PDF 文档
- 提取文本（OCR / PDF 文本解析）
- 生成朗读音频（TTS）
- 返回同步高亮所需的 `word/sentence time marks`
- **结构化解析文档内容，将文字块和图片块分别输出给前端**

---

## 1. 技术栈

- **后端框架**：FastAPI
- **数据库**：PostgreSQL（示例默认也可用 SQLite 跑通）
- **缓存/任务队列**：Redis（建议生产环境启用）
- **对象存储**：MinIO / S3
- **OCR 接口**：可接第三方视觉/OCR模型
- **TTS 接口**：可接第三方语音合成模型
- **PDF 解析**：PyMuPDF
- **鉴权**：JWT

---

## 2. 目录结构

```text
app/
  api/                  # 路由层
  core/                 # 配置与安全
  db/                   # 数据库连接
  models/               # ORM 模型
  schemas/              # 请求/响应模型
  services/             # 业务逻辑
  services/adapters/    # 外部 AI / OCR / TTS / 文档解析适配器
  main.py               # 入口

docs/
  architecture.md
  api-spec.md
  

## 3. 快速启动

```bash
python -m venv .venv
source .venv/bin/activate   # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

启动后访问：

- Swagger 文档：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

## 4. 默认管理员

先调用：

```http
POST /api/v1/admin/seed-admin
```

默认管理员账号：

- 用户名：`admin`
- 密码：`Admin@123456`

## 5. 关键业务说明

### 5.1 注册审批
1. 用户提交注册信息。
2. 系统创建 `users` 记录，状态为 `pending`。
3. 同时生成 `approval_requests(type=register)`。
4. 管理员审批通过后，用户状态改为 `approved`。
5. 用户才可以登录。

### 5.2 密码修改审批
1. 已登录用户提交旧密码和新密码。
2. 系统验证旧密码正确。
3. 生成 `approval_requests(type=password_change)`。
4. 管理员审批后，系统正式更新密码。

### 5.3 OCR 文本提取
- PDF：优先直接解析可复制文本。
- 图片：通过 OCR 接口识别文字。
- 如果未来接入多模态模型，可在 `ocr_adapter.py` 中替换为实际 HTTP 接口。

### 5.4 朗读与同步高亮
- 后端生成音频及时间戳 marks。
- 前端负责：
  - 播放 / 暂停
  - 倍速调整 UI
  - 根据 `start_ms/end_ms` 控制文字高亮

## 6. AI 接口适配说明

### OCR 适配器输入/输出
输入：
- 文件（二进制）

输出：
```json
{
  "text": "识别出的完整文本"
}
```

### TTS 适配器输入/输出
输入：
```json
{
  "text": "要朗读的文本",
  "speed": 1.0,
  "voice": "female_soft",
  "return_word_marks": true
}
```

输出：
```json
{
  "audio_url": "https://your-storage/audio/xxx.mp3",
  "marks": [
    {"index": 0, "word": "Hello", "start_ms": 0, "end_ms": 320},
    {"index": 1, "word": "world", "start_ms": 321, "end_ms": 680}
  ]
}
```

## 7. 生产环境建议

- 将 OCR/TTS 改为异步任务（Celery / RQ）
- 上传文件病毒扫描
- PDF 页数、图片大小、并发速率限制
- 管理员审批操作日志审计
- RBAC 权限分级
- 文本分句与段落级高亮
- 支持 dyslexia-friendly 字体配置与阅读主题参数持久化



### 接口总览

当前主要分为 4 类：

认证与用户管理

管理员审批

文档上传与读取

音频朗读与高亮

1. 认证与用户管理接口
1）POST /api/v1/auth/register
功能

普通用户注册。
注册后不会立即生效，而是进入待审批状态，必须管理员审核通过后才能登录。

请求作用

创建用户

默认状态设为 pending

自动生成一条审批记录

成功返回
{
  "message": "注册申请已提交，需管理员审批后方可登录"
}
常见失败返回
用户名或邮箱已存在
{
  "detail": "email or username already exists"
}
2）POST /api/v1/auth/login
功能

用户登录，返回 JWT 访问令牌。

适用对象

管理员登录

审批通过后的普通用户登录

当前实现特点

这个接口已经改成兼容 Swagger 的 OAuth2 password 方式，因此 Swagger 右上角 Authorize 可以直接用用户名和密码登录。

成功返回
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
字段说明

access_token：JWT 令牌，用于后续访问受保护接口

token_type：令牌类型，当前固定为 bearer

常见失败返回
用户名或密码错误
{
  "detail": "用户名或密码错误"
}
账号尚未审批通过
{
  "detail": "账号尚未审批通过"
}
3）POST /api/v1/auth/password-change-request
功能

用户发起修改密码申请。
此接口不会立即修改密码，而是生成一条“改密审批记录”，等待管理员审核。

请求作用

校验旧密码

生成密码修改审批申请

管理员通过后才真正生效

成功返回
{
  "message": "修改密码申请已提交，需管理员审批"
}
常见失败返回
旧密码错误
{
  "detail": "old password is incorrect"
}
未登录或 token 无效
{
  "detail": "Could not validate credentials"
}
2. 管理员审批接口
4）POST /api/v1/admin/seed-admin
功能
初始化默认管理员账号。

作用
如果系统中还没有管理员，就创建一个默认管理员：
用户名：admin
密码：Admin@123456
成功返回
你当前实际返回的是：

{
  "message": "默认管理员已创建：admin / Admin@123456"
}
可能的其他返回
如果已经存在管理员，通常会返回“已存在”的提示信息，具体取决于代码实现。

5）GET /api/v1/admin/approval-requests
功能
管理员查看待审批或全部审批记录。

作用
用于查看：
注册申请
密码修改申请
成功返回
你当前实际拿到的是列表结构，例如：

[
  {
    "id": 1,
    "user_id": 2,
    "request_type": "register",
    "payload_json": "{\"email\": \"user001@example.com\", \"username\": \"user001\"}",
    "status": "pending",
    "reviewed_by": null,
    "reviewed_at": null,
    "created_at": "2026-03-08T14:01:42.113010"
  }
]
字段说明
id：审批记录 ID
user_id：申请对应的用户 ID
request_type：申请类型
当前包括：
register
password_change
payload_json：申请内容，JSON 字符串形式保存
status：审批状态
pending
approved
rejected
reviewed_by：审批人 ID
reviewed_at：审批时间
created_at：申请创建时间

常见失败返回
未授权
{
  "detail": "Could not validate credentials"
}
非管理员访问
{
  "detail": "Admin only"
}
6）POST /api/v1/admin/approval-requests/{id}/approve
功能
管理员通过某条审批记录。
作用
根据审批类型不同，执行不同操作：
如果是注册申请
把用户状态从 pending 改为 approved
如果是改密申请
将新密码哈希写入用户表
正式完成密码变更
成功返回
通常是消息类返回，例如：

{
  "message": "审批通过成功"
}
或类似含义的提示。
常见失败返回
审批记录不存在
{
  "detail": "Approval request not found"
}
未授权
{
  "detail": "Could not validate credentials"
}
非管理员
{
  "detail": "Admin only"
}
7）POST /api/v1/admin/approval-requests/{id}/reject
功能
管理员驳回某条审批记录。
作用
将审批状态改为 rejected，但不执行实际账号通过或密码修改。
成功返回
一般为：

{
  "message": "审批驳回成功"
}
常见失败返回
审批记录不存在
{
  "detail": "Approval request not found"
}
未授权
{
  "detail": "Could not validate credentials"
}
3. 文档上传与读取接口
8）POST /api/v1/documents/upload
功能
上传 PDF 或图片文件，并提取文字内容。
支持内容
PDF
图片（jpg/png 等）
后端完成的事情
接收文件
保存文档记录
调用 OCR / PDF 解析逻辑
提取文本
写入数据库
成功返回
你当前接口已返回 200 OK。
具体返回结构通常会包含文档信息，例如：

{
  "id": 1,
  "filename": "example.pdf",
  "content_type": "application/pdf",
  "extracted_text": "......",
  "created_at": "2026-03-08T14:10:00"
}
常见返回字段
根据当前系统设计，一般会有：
id / document_id
文件名
文件类型
提取后的文本
创建时间
常见失败返回
不支持的文件格式
{
  "detail": "Unsupported file type"
}
未授权
{
  "detail": "Could not validate credentials"
}
9）GET /api/v1/documents/{document_id}
功能
获取某个文档的详细信息和提取后的文本。
作用
前端可以用这个接口读取：
文档基本信息
OCR/PDF 提取出的正文内容
成功返回
你当前已经成功访问 /api/v1/documents/1，通常返回类似：

{
  "id": 1,
  "filename": "example.pdf",
  "content_type": "application/pdf",
  "text": "......提取出的文本内容......",
  "created_by": 2,
  "created_at": "2026-03-08T14:10:00"
}
典型用途
文本展示
给 TTS 接口传入 document_id
前端渲染阅读页面
常见失败返回
文档不存在
{
  "detail": "Document not found"
}
未授权
{
  "detail": "Could not validate credentials"
}
4. 音频朗读与高亮接口
10）POST /api/v1/audio/tts
功能
将文档内容或文本转换为语音，并返回同步高亮所需的时间戳。

你当前实际测试的请求
{
  "document_id": 1,
  "speed": 1.0,
  "voice": "female_soft",
  "return_word_marks": true
}
请求字段说明
document_id：需要朗读的文档 ID
speed：朗读速度
voice：音色，如 female_soft
return_word_marks：是否返回逐词高亮时间戳
成功返回
你当前实际返回的是：

{
  "audio_track_id": 1,
  "audio_url": "mock_audio/female_soft_1_0.mp3",
  "speed": 1,
  "sync_marks": [
    {
      "index": 0,
      "word": "Assignment",
      "start_ms": 0,
      "end_ms": 280
    },
    {
      "index": 1,
      "word": "2",
      "start_ms": 280,
      "end_ms": 560
    }
  ]
}
字段说明
audio_track_id：音频记录 ID
audio_url：音频地址
当前是 mock 地址，说明现在使用的是模拟 TTS
speed：实际朗读速度
sync_marks：同步高亮数据列表
sync_marks 子字段说明
index：词序号
word：当前词
start_ms：开始时间，单位毫秒
end_ms：结束时间，单位毫秒

作用
前端可以根据：
audio_url 播放音频
sync_marks 做边读边高亮

常见失败返回
文档不存在
{
  "detail": "Document not found"
}
未授权
{
  "detail": "Could not validate credentials"
}
TTS 服务异常
{
  "detail": "TTS generation failed"
}
当前系统接口功能总结
认证类
/api/v1/auth/register：注册申请
/api/v1/auth/login：登录并获取 token
/api/v1/auth/password-change-request：修改密码申请

审批类
/api/v1/admin/seed-admin：初始化默认管理员
/api/v1/admin/approval-requests：查看审批列表
/api/v1/admin/approval-requests/{id}/approve：审批通过
/api/v1/admin/approval-requests/{id}/reject：审批驳回

文档类
/api/v1/documents/upload：上传文件并提取文本
/api/v1/documents/{document_id}：获取文档详情

音频类
/api/v1/audio/tts：生成朗读结果与同步高亮时间戳