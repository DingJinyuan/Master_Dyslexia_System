# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个面向阅读障碍（Dyslexia）用户的辅助阅读应用，采用前后端分离架构。后端为 FastAPI，前端为 Vue 3 + Vite。核心功能包括：文档上传与 OCR 文本提取、TTS 语音合成与同步高亮、沉浸式阅读器、词性标注、划词翻译、可读性评分、文本摘要与简化。

## 目录结构

```
frontend/
├── dyslexia_reader-main/    # FastAPI 后端
│   ├── app/
│   │   ├── api/             # 路由层（auth, admin, documents, tts, nlp, readability, refine）
│   │   ├── core/            # 配置（config.py）与安全（security.py — JWT + bcrypt 直接调用）
│   │   ├── db/              # SQLAlchemy session、Base、migrate.py（启动时自动执行 schema 迁移）
│   │   ├── models/          # ORM 模型（User, ApprovalRequest, Document, DocumentBlock）
│   │   │                     # AudioTrack 模型文件仍存在但已从 __init__.py 移除，不再自动建表
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── services/        # 业务逻辑层
│   │   │   └── adapters/    # OCR/TTS/文档解析适配器
│   │   │       └── document_parser.py  # 使用 PyMuPDF4LLM 解析 PDF（自动去页眉页脚、处理多栏、输出 Markdown 段落）
│   │   ├── utils/           # 公共工具（text_utils.py — detect_language, preprocess_text）
│   │   └── main.py          # 应用入口，注册路由、CORS、静态文件挂载、日志配置、DB 迁移
│   ├── docs/                # 架构说明与 API 规格（api-spec.md）
│   ├── storage/             # 上传文件与 TTS 音频输出
│   ├── test_all_apis.py     # 后端 API 全量自动化测试脚本
│   └── dyslexia_reader.db   # SQLite 数据库文件（开发环境）
│
├── FEATURES.md              # 功能说明文档
└── vue3_Dyslexia/           # Vue 3 前端
    └── src/
        ├── apis/            # API 调用封装（auth, admin, documents, tts, nlp）
        ├── components/      # 全局组件
        ├── router/          # Vue Router 路由定义
        ├── stores/          # Pinia 状态管理（userStore）
        ├── styles/          # SCSS 全局样式与 Element Plus 主题覆盖
        ├── utils/           # http.js（axios 封装 + 拦截器）、validateRules.js
        └── views/           # 页面视图
            ├── Login/       # 登录、注册、忘记密码
            ├── Home/        # 首页（文档库、导入、系统设置、管理员审批）
            ├── Upload/      # 文档上传
            ├── ReaderView/  # 标准阅读器
            └── Chenjinshi/  # 沉浸式阅读器（核心功能：TTS 朗读、高亮、划词翻译、可读性评分、摘要、漫画生成）
```

## 常用命令

### 后端（dyslexia_reader-main）

```bash
cd dyslexia_reader-main

# 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动开发服务器（默认 http://127.0.0.1:8000）
uvicorn app.main:app --reload

# 初始化默认管理员
curl -X POST http://127.0.0.1:8000/api/v1/admin/seed-admin
# 管理员账号: admin / Admin@123456

# 运行全量 API 测试
python test_all_apis.py

# API 文档
# Swagger: http://127.0.0.1:8000/docs
# ReDoc:   http://127.0.0.1:8000/redoc
```

### 前端（vue3_Dyslexia）

```bash
cd vue3_Dyslexia
npm install
npm run dev        # 开发服务器（默认 http://localhost:5173）
npm run build      # 生产构建（含 type-check）
npm run lint       # ESLint + oxlint
npm run format     # Prettier 格式化
```

## API 接口完整列表（共 19 个）

### 无需认证

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 健康检查 |
| POST | `/api/v1/auth/register` | 注册（含 `role` 字段：`user`/`admin`，默认 `user`） |
| POST | `/api/v1/auth/login` | 登录（OAuth2 表单格式 `username`+`password`） |
| POST | `/api/v1/nlp/pos-tagging` | 词性标注（中：jieba / 英：spaCy） |
| POST | `/api/v1/nlp/word-lookup` | 划词翻译（英：Free Dictionary API） |
| POST | `/api/v1/tts` | 全文 TTS（edge-tts → 有道智云 → gTTS → pyttsx3 多引擎自动降级） |
| POST | `/api/v1/tts/sentences` | 逐句 TTS（支持高亮跟随） |
| GET | `/api/v1/tts/voices` | 获取可用音色列表（含 edge-tts + 有道智云 + gTTS + pyttsx3） |
| POST | `/api/v1/readability` | 可读性评分（Form 提交 `text`） |
| POST | `/api/v1/refine` | 多 Agent 迭代文本精炼（JSON：`original_text`, `mode`, `max_iterations`, `pass_threshold`） |
| POST | `/api/v1/admin/seed-admin` | 初始化默认管理员 |

### 需登录（JWT）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/password-change-request` | 修改密码申请（需管理员审批） |
| POST | `/api/v1/documents/upload` | 上传文档（PDF/PNG/JPEG/WEBP，最大 50MB） |
| GET | `/api/v1/documents` | 文档列表（分页：`page`, `page_size`） |
| GET | `/api/v1/documents/{id}` | 文档详情（含 `extracted_text`） |
| GET | `/api/v1/documents/{id}/structured` | 结构化文档（文本块+图片块分离） |
| GET | `/api/v1/documents/{id}/paragraphs` | 段落列表（用于逐段朗读） |

### 需管理员

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/approval-requests` | 审批列表 |
| POST | `/api/v1/admin/approval-requests/{id}/approve` | 审批通过 |
| POST | `/api/v1/admin/approval-requests/{id}/reject` | 审批驳回 |

## 架构要点

### 文本精炼迭代系统（Refine）

`POST /api/v1/refine` 是基于 LangGraph 的多 Agent 迭代流水线，替代了旧的 `/summarize` 和 `/simplify` 接口。

**文件结构**：
```
app/services/refine/
├── base_agent.py          # BaseAgent — LLM client、语言检测、迭代提示
├── full_refine_agent.py   # FullRefineAgent — 全文改写（100%保留信息）
├── summary_agent.py       # SummaryAgent — 摘要（精简+保留关键词）
├── evaluator.py           # DyslexiaEvaluator — 4维评估（阅读/内容/排版/叙事）
└── orchestrator.py        # LangGraph StateGraph — 编排+迭代循环
```

**LangGraph 流程**：
```
pre_evaluate(算基线分) → refine/summary agent → judge(评估)
  ↑                                                  ↓
  └──────── should_continue? ←───────────────────────┘
              YES → 回流（带微调提示）
              NO  → END
```

**迭代终止条件**（AND 关系）：
- `total_score >= pass_threshold`（zh: 0.65, en: 0.70）
- `content.dimension_score >= 0.70`（内容保真硬约束）
- `iter_count >= max_iterations`（最大 3 轮兜底）

**评估维度**（DyslexiaEvaluator，4 维等权重 0.25）：
- 阅读有效性：FRE 易读度、FKGL 年级难度、平均句长
- 内容保真：BLEU、BERTScore、关键词保留率（DeepSeek 提取）
- 排版有效性：段落数量、平均段长、标点规范
- 叙事有效性：正式度、自然流畅度（DeepSeek 评分）

**请求示例**：
```json
{
  "original_text": "需要处理的原文",
  "mode": "full_refine",       // full_refine | summary
  "summary_length": "标准",     // 简短/标准/详细（仅 summary）
  "max_iterations": 3,
  "pass_threshold": null       // null 时自动按语言选择
}
```

### 用户审批流程

用户注册和修改密码都需要管理员审批才能生效：
1. 用户提交申请 → 创建 `approval_requests` 记录（type: `register` / `password_change`）
2. 管理员通过 `/api/v1/admin/approval-requests/{id}/approve` 审批
3. 系统执行实际操作（激活用户 / 更新密码）

**注册时可选择角色**：`POST /auth/register` 的 `role` 字段可选 `"user"`（默认）或 `"admin"`，注册后都需审批。通过审批后角色生效。

`get_current_user` 只验证 JWT 有效性，不检查用户状态。需要已审批用户时用 `get_current_approved_user`，管理员接口用 `get_admin_user`。

### TTS 引擎链

`tts_service.py` 采用多引擎自动降级策略：
1. **edge-tts**（优先）— 微软免费 TTS，需安装 `pip install edge-tts`
2. **有道智云 TTS**（指定 voiceName 时优先，否则作为 fallback）— 需配置 `YOUDAO_APP_KEY`/`YOUDAO_APP_SECRET`
3. **gTTS**（第三选择）— Google TTS，需安装 `pip install gTTS`
4. **pyttsx3**（离线兜底）— 系统自带语音，需安装 `pip install pyttsx3`

TTS 音频输出到 `storage/audio/`，通过 `/static/tts/{filename}` 提供访问。

### 前端路由与权限

路由没有导航守卫——所有页面都可以直接访问。认证控制通过 axios 拦截器实现：401 响应时自动清除 store 并跳转 `/login`。

登录接口返回 `role` 字段（`user`/`admin`），前端 `userStore` 存储后用于：
- 首页"审批管理"入口仅 `role === 'admin'` 可见
- 管理员用户名旁显示紫色 `[管理员]` 标签

注册页面支持选择角色（普通用户 / 管理员），`registerAPI` 传 `role` 参数。

### 沉浸式阅读器（Chenjinshi）数据流

1. `loadDocumentData()` → 并行请求文档详情和结构化数据 → 存储 `allBlocks`（全部块：文本+图片）
2. 按文本块并行调用词性标注 API（每个文本块独立标注）→ 图文混排 `buildMixedHtml()` → 渲染到 DOM
3. 划词翻译：mouseup 事件选中文字 → `wordLookupAPI` → 弹出 WordTooltip
4. 朗读（两种模式）：
   - **全文模式**：调用 `POST /api/v1/tts` → 返回单个音频 URL → Audio 播放
   - **逐句高亮模式**：调用 `POST /api/v1/tts/sentences` → 返回逐句音频列表 → 顺序播放 + `highlightSentenceInDom()` 高亮当前句子 + 自动滚动
5. 可读性评分：弹窗触发 `POST /api/v1/readability`
6. 文本摘要：弹窗触发 `POST /api/v1/refine` (mode=summary)
7. 文本优化：`POST /api/v1/refine` (mode=full_refine) → 返回改写后文本替换显示
8. 图片点击放大：事件委托监听 `.image-block img` 点击 → teleport 全屏预览

### PDF 解析（PyMuPDF4LLM）

`DocumentParser` 使用 PyMuPDF4LLM 解析 PDF：
- `to_markdown(header=False, footer=False)` 自动去除页眉/页脚/页码
- 内置 ML 布局分析，正确处理双栏论文的阅读顺序
- 输出 Markdown 格式，按 `\n\n` 分割即为自然段落
- 一个 `DocumentBlock` 对应一个自然段

### OCR/TTS 适配器模式

`services/adapters/` 中的适配器设计为可替换。`.env` 中 `OCR_PROVIDER` 和 `TTS_PROVIDER` 控制提供商标识。

### 数据库

开发环境使用 SQLite（`dyslexia_reader.db`），生产环境预期 PostgreSQL。`db/session.py` 自动检测 SQLite 并设置 `check_same_thread=False`。表在 `main.py` 启动时通过 `Base.metadata.create_all` 自动创建，不使用 Alembic 迁移。

## 注意事项

- **main.js bug**：`src/main.js` 第 10 行和第 16 行重复调用了 `createPinia()`，会创建两个独立的 Pinia 实例，导致 `pinia-plugin-persistedstate` 只在第一个实例上生效。应删除第 16 行的 `app.use(createPinia())`。
- **密码加密**：`security.py` 直接使用 `bcrypt` 库（非 passlib），因 passlib 与 bcrypt >= 4.1 不兼容。
- **spaCy 英文词性标注**需要模型 `en_core_web_sm`：`python -m spacy download en_core_web_sm`。未安装时英文词性标注返回 500 错误，中文标注正常。
- **英文可读性评分**需要 NLTK cmudict 数据：`python -c "import nltk; nltk.download('cmudict')"`。缺失时自动回退到简化评分算法。
- API Key（DeepSeek、有道）需在 `.env` 中配置 `DEEPSEEK_API_KEY`、`YOUDAO_APP_KEY`、`YOUDAO_APP_SECRET`。未配置时 AI 相关功能返回 API 错误信息，有道 TTS 自动跳过（降级到 edge-tts/gTTS/pyttsx3）。
- 后端 CORS 仅允许 `http://localhost:5173`，部署时需修改。
- `http.js` 中 axios baseURL 硬编码为 `http://localhost:8000/api/v1`，响应拦截器自动取 `res.data`。
- 数据库迁移在 `main.py` 启动时通过 `app/db/migrate.py` 自动执行（删除废弃表、添加新列），不使用 Alembic。
- 已有文档的旧 block 数据仍为旧解析器格式。只有新上传的 PDF 会使用 PyMuPDF4LLM 解析为段落。
- `AudioTrack` 模型文件保留但已从 `models/__init__.py` 移除，`audio_tracks` 表在启动迁移中被删除。
- 旧的 `/summarize` 和 `/simplify` 接口已删除，统一由 `/refine` 替代（mode=`summary` / `full_refine`）。
- 登录接口返回 `{ access_token, token_type, role, username }`，前端 `userStore` 存储 role 用于角色区分 UI。
- 前端 `tsconfig.json` 缺失（项目既有问题），需 `npx vite build` 而非 `npm run build` 跳过 type-check。
- 上传文档后自动跳转到沉浸式阅读器（`/chenjinshi/{id}`），而非标准阅读器。
- Git tag `v1.0-pre-test` 为 2026-07-02 测试前版本快照，可通过 `git checkout v1.0-pre-test` 回退。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | FastAPI 0.115 + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| 鉴权 | JWT (python-jose) + bcrypt |
| PDF 解析 | PyMuPDF + PyMuPDF4LLM（布局分析、去页眉页脚、段落输出）|
| 中文分词 | jieba |
| NLP | spaCy（英文）+ jieba（中文） |
| TTS | edge-tts + 有道智云 + gTTS + pyttsx3（多引擎自动降级） |
| 前端框架 | Vue 3.5 + Composition API |
| 构建工具 | Vite 7 |
| UI 组件库 | Element Plus 2.13（按需自动导入） |
| 状态管理 | Pinia 3 + pinia-plugin-persistedstate |
| 路由 | Vue Router 5 |
| CSS | SCSS（全局变量注入所有组件） |
| HTTP | axios（统一拦截器处理 token 和错误） |
| AI | DeepSeek API（文本总结/简化）、有道词典 API（划词翻译）、有道 TTS |
