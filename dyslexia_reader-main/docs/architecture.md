# 系统架构设计说明

## 一、目标用户
针对阅读障碍（Dyslexia）用户提供更容易理解、更可听、更可跟读的阅读体验。

## 二、核心能力分层

### 1. 接入层
- Web / App 前端
- 管理员后台

### 2. 应用层
- 认证授权服务
- 审批服务
- 文档服务
- OCR 文本提取服务
- TTS 语音合成服务
- 阅读同步服务

### 3. 数据层
- PostgreSQL：用户、审批、文档、音频记录
- Redis：任务状态、缓存
- MinIO / S3：原始文件与音频文件

## 三、推荐总体架构

```text
前端/移动端
    |
 API Gateway / FastAPI
    |
 -------------------------------------------------
 |         |            |            |            |
认证服务   审批服务     文档服务      OCR服务       TTS服务
 |         |            |            |            |
Postgres  Postgres     MinIO/S3     第三方AI      第三方AI
```

## 四、功能模块说明

### 4.1 用户与审批模块
由于题目要求“修改密码、注册需要管理员同意”，因此采用“申请制流程”：

- 注册：先创建待审批账号
- 改密：生成审批工单，通过后再实际更新

### 4.2 文档导入模块
支持：
- PDF 上传
- 图片上传（PNG/JPG/JPEG/WEBP）

处理流程：
1. 用户上传文件。
2. 后端保存原始文件。
3. 根据文件类型选择解析方式：
   - PDF：直接提取文本或 OCR
   - 图片：OCR
4. 提取结果写入 `documents.extracted_text`。

### 4.3 朗读模块
后端不直接承担“暂停/继续”的状态机，而是：
- 生成音频
- 返回高亮时间戳
- 前端使用音频播放器控制播放、暂停、拖动、倍速

这是更合理的职责划分，因为暂停与拖动属于客户端播放控制能力。

### 4.4 同步高亮模块
可返回两种粒度：
- `word-level marks`
- `sentence-level marks`

推荐先做词级 marks，格式：

```json
[
  {"index": 0, "word": "This", "start_ms": 0, "end_ms": 200},
  {"index": 1, "word": "is", "start_ms": 201, "end_ms": 320}
]
```

前端逻辑：
- 根据音频当前播放时间 `currentTime * 1000`
- 在 marks 中找到当前时间落点
- 高亮对应文本 token

## 五、数据库设计

### users
- id
- email
- username
- password_hash
- role
- status
- is_active
- created_at

### approval_requests
- id
- user_id
- request_type
- payload_json
- status
- reviewed_by
- reviewed_at
- created_at

### documents
- id
- user_id
- original_filename
- file_type
- file_url
- extracted_text
- processing_status
- created_at

### audio_tracks
- id
- document_id
- provider
- audio_url
- marks_json
- speed
- created_at

## 六、可扩展点

1. **阅读个性化配置**
   - 行间距
   - 字距
   - 字号
   - 字体
   - 主题色
2. **文本简化**
   - 调用大模型把长难句改写成更易读版本
3. **生词辅助**
   - 词义解释
   - 图像化解释
4. **阅读理解辅助**
   - 段落总结
   - 问答引导
5. **学习数据分析**
   - 朗读时长
   - 常停顿位置
   - 阅读完成率
