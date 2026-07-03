# 优读 EASE — 阅读障碍辅助系统 技术文档

> 版本：v1.0 | 日期：2026-07-04 | 作者：jacky | 最后更新：Pinia 缓存、全音色预热、主题切换、自动滚动

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [后端实现](#3-后端实现)
4. [前端实现](#4-前端实现)
5. [核心功能详解](#5-核心功能详解)
6. [API 接口文档](#6-api-接口文档)
7. [部署与运维](#7-部署与运维)
8. [已知问题与优化方向](#8-已知问题与优化方向)

---

## 1. 项目概述

### 1.1 项目定位

优读 EASE 是一款面向**阅读障碍（Dyslexia）**用户的辅助阅读 Web 应用。它帮助用户更轻松地阅读文档，提供文字转语音、词性标注、划词翻译、文本优化、思维导图等辅助功能。

### 1.2 核心能力

| 功能 | 说明 |
|---|---|
| 文档上传与解析 | 支持 PDF/PNG/JPEG/WEBP，4 层降级提取+乱码校验 |
| 词性标注 | 中文 jieba + 英文 spaCy，8 色编码，可显隐切换 |
| TTS 语音朗读 | edge-tts 为主，4 音色全量预热+缓存，切换秒播 |
| 划词翻译 | 选中即查，英文 Free Dictionary + 中文自建词典 |
| 可读性评分 | 中英文双算法，英文四次方根映射（学术论文 1.7→36） |
| AI 文本优化 | LangGraph 迭代改写，口语化/短句/分段，纯本地评估 |
| AI 摘要 | 简短/标准/详细，强制原语种输出 |
| 思维导图 | DeepSeek 大纲+MCP markmap，3 次重试，fastly CDN |
| 阅读辅助 | 阅读尺、焦点屏、4 主题切换、自动滚动 |
| 图文模式 | 共存（嵌入）+分离（侧栏），一键切换 |
| 预热缓存 | Pinia 持久化，优化/摘要/TTS/导图进文章即生成，刷新不丢 |
| 用户管理 | JWT 认证 + 管理员审批，退出清缓存 |

---

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                    Vue 3 前端                        │
│  Vite 7 + Element Plus + Pinia + Vue Router          │
│  localhost:5173                                      │
└────────────────────┬────────────────────────────────┘
                     │ HTTP (axios)
┌────────────────────▼────────────────────────────────┐
│                  FastAPI 后端                        │
│  Python 3.13 + SQLAlchemy + LangGraph                │
│  localhost:8000                                      │
└────────┬───────────────────────┬────────────────────┘
         │                       │
    ┌────▼────┐          ┌──────▼──────┐
    │ SQLite  │          │ DeepSeek API │
    │  数据库  │          │  (文本优化)   │
    └─────────┘          └─────────────┘
```

### 2.2 目录结构

```
frontend/
├── dyslexia_reader-main/       # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层（8 个模块）
│   │   │   ├── auth.py         # 认证（登录/注册/改密）
│   │   │   ├── admin.py        # 管理员审批
│   │   │   ├── documents.py    # 文档上传/查询
│   │   │   ├── nlp.py          # 词性标注/划词翻译
│   │   │   ├── tts.py          # TTS 语音合成
│   │   │   ├── readability.py  # 可读性评分
│   │   │   ├── refine.py       # 文本精炼（优化/摘要）
│   │   │   └── mindmap.py      # 思维导图
│   │   ├── core/               # 配置与安全
│   │   │   ├── config.py       # 全局配置（Pydantic Settings）
│   │   │   └── security.py     # bcrypt 密码哈希 + JWT
│   │   ├── db/                 # 数据库
│   │   │   ├── session.py      # SQLAlchemy 会话工厂
│   │   │   └── migrate.py      # 启动时自动 Schema 迁移
│   │   ├── models/             # ORM 模型
│   │   │   ├── user.py         # User（含 role/status 字段）
│   │   │   ├── document.py     # Document（文档元数据）
│   │   │   ├── document_block.py # DocumentBlock（文本块/图片块）
│   │   │   └── approval.py     # ApprovalRequest（审批流）
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── document_service.py   # 文档处理（解析+存储）
│   │   │   ├── nlp_service.py        # NLP（词性标注+语言检测）
│   │   │   ├── dictionary_service.py # 划词翻译
│   │   │   ├── tts_service.py        # TTS 语音合成（多引擎降级）
│   │   │   ├── readability_service.py # 可读性评分
│   │   │   ├── mindmap_service.py    # 思维导图（LLM+MCP）
│   │   │   ├── storage_service.py    # 本地文件存储
│   │   │   ├── adapters/
│   │   │   │   ├── document_parser.py # PDF 解析器（PyMuPDF+OCR）
│   │   │   │   └── ocr_adapter.py     # OCR 适配器
│   │   │   └── refine/          # 多 Agent 文本精炼管道
│   │   │       ├── base_agent.py       # LLM 客户端基类
│   │   │       ├── full_refine_agent.py # 全文改写 Agent
│   │   │       ├── summary_agent.py    # 摘要 Agent
│   │   │       ├── evaluator.py        # 质量评估器
│   │   │       └── orchestrator.py     # LangGraph 编排
│   │   ├── utils/
│   │   │   └── text_utils.py    # 公共工具（语言检测/文本清洗）
│   │   └── main.py              # 应用入口
│   ├── storage/                 # 文件存储（image/audio/mindmap）
│   ├── test_all_apis.py         # 全量 API 测试脚本
│   ├── requirements.txt
│   └── .env
│
└── vue3_Dyslexia/               # Vue 3 前端
    └── src/
        ├── main.js              # 应用入口
        ├── App.vue              # 根组件
        ├── router/index.js      # 路由（6 个页面）
        ├── stores/userStore.js  # Pinia 状态管理（持久化）
        ├── apis/                # API 封装
        │   ├── auth.js          # 登录/注册/改密
        │   ├── documents.js     # 文档 CRUD
        │   ├── nlp.js           # 词性标注/翻译/可读性/精炼
        │   ├── tts.js           # TTS 语音
        │   ├── admin.js         # 管理员审批
        │   └── mindmap.js       # 思维导图
        ├── utils/
        │   ├── http.js          # axios 封装（拦截器+自动 token）
        │   └── validateRules.js # 表单校验规则
        ├── styles/
        │   ├── var.scss         # SCSS 变量
        │   ├── common.scss      # 全局样式
        │   └── element/index.scss # Element Plus 主题覆盖
        └── views/
            ├── Login/           # 登录/注册/忘记密码
            ├── Home/            # 首页（文档库/阅读历史/设置/审批）
            ├── Upload/          # 文档上传
            ├── ReaderView/      # 标准阅读器
            └── Chenjinshi/      # 沉浸式阅读器（核心）
```

### 2.3 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 后端框架 | FastAPI | 0.115 |
| ASGI 服务器 | Uvicorn | - |
| ORM | SQLAlchemy | 2.0 |
| 鉴权 | JWT (python-jose) + bcrypt | - |
| PDF 解析 | PyMuPDF (fitz) + EasyOCR | - |
| 中文分词 | jieba | - |
| NLP | spaCy (英文) | - |
| TTS | edge-tts + 有道智云 + gTTS + pyttsx3 | - |
| AI/LLM | DeepSeek API (chat/completions) | - |
| 工作流编排 | LangGraph (StateGraph) | - |
| 思维导图 | MCP stdio (markmap-mcp-server) | - |
| 前端框架 | Vue 3 + Composition API | 3.5 |
| 构建工具 | Vite | 7 |
| UI 组件库 | Element Plus | 2.13 |
| 状态管理 | Pinia + persistedstate | 3 |
| 路由 | Vue Router | 5 |
| CSS | SCSS（全局变量注入） | - |
| HTTP 客户端 | axios（拦截器统一处理 token） | 1.13 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） | - |

---

## 3. 后端实现

### 3.1 应用入口

FastAPI 启动时自动建表 + Schema 迁移，注册 8 个路由模块，挂载 3 个静态目录（TTS 音频、存储文件、通用静态文件）。

### 3.2 认证系统

- **密码加密**：直接使用 bcrypt 库（非 passlib，因版本兼容问题）
- **JWT 生成**：HS256 算法，过期 120 分钟
- **三级鉴权**：`get_current_user`（仅验 JWT）、`get_current_approved_user`（需审批通过）、`get_admin_user`（需管理员角色）
- **注册流程**：提交注册 → User（status=pending）→ ApprovalRequest → 管理员审批 → 激活

### 3.3 文档解析器

#### PDF 文本提取策略（4 层降级）

```
方法1: page.get_text("text") → 含 CJK 且校验通过 → 返回
  失败
方法2: page.get_text("blocks") → 含 CJK 且校验通过 → 过滤乱码返回
  失败                          无 CJK（英文）→ 直接返回
方法3: page.get_text("rawdict") → 同上逻辑
  失败
方法4: EasyOCR → 渲染页面为 200DPI 图片 → OCR 识别
```

#### 中文乱码校验

针对 CID 编码 PDF 的错位字符问题，双重校验：
1. 中文标点检测：是否有 。，、！？；： 等
2. 功能词检测：是否包含 2 个以上常见中文功能词（收录 300+ 高频词）

任一通过即认为有效中文，否则丢弃该文本块。

#### 英文文本处理

英文文本（无 CJK 字符）直接返回，不做校验过滤。

### 3.4 TTS 语音合成

**多引擎热备策略**：

```
edge-tts（微软免费，优先）
  失败
有道智云 TTS（指定发音人时优先）
  失败
gTTS（Google）
  失败
pyttsx3（系统离线兜底）
```

**音频缓存**：相同文本+音色+语速的音频 MD5 哈希缓存，重复请求直接返回已生成文件。

**逐句 TTS**：按中英文标点分句，逐句调用 TTS，前端实现高亮跟随播放。

### 3.5 词性标注

- **中文**：jieba.posseg 分词+词性标注，映射 15+ 种标签，每种独立颜色
- **英文**：spaCy en_core_web_sm 模型，18 种标签映射
- **前端**：每个 token 渲染为带颜色背景的 span，支持显隐切换

**颜色编码**：

| 词性 | 颜色 |
|---|---|
| 名词 | #4A90D9（蓝） |
| 动词 | #E74C3C（红） |
| 形容词 | #27AE60（绿） |
| 副词 | #F39C12（橙） |
| 代词 | #1ABC9C（青） |
| 数/量词 | #9B59B6（紫） |
| 介词/连词 | #95A5A6（灰） |
| 助词/标点 | #BDC3C7（浅灰） |

### 3.6 划词翻译

- **中文**：pypinyin 拼音 + jieba 词性 + 自建词典 + 网络词典回退
- **英文**：Free Dictionary API（api.dictionaryapi.dev，免费无需 Key）

### 3.7 可读性评分

#### 设计思路

从两个维度量化文本对阅读障碍者的友好程度：句法复杂度（句子多长、词多难）和统计特征（词汇多样性、长词密度）。中英文使用不同算法，输出 0-100 分和五级标签。

#### 英文算法

第一步：用 textstat 库计算 Flesch Reading Ease：

```
Flesch = 206.835 - 1.015*(词数/句数) - 84.6*(音节数/词数)
```

同时输出 FK Grade、Gunning Fog、SMOG、ARI 作为参考。

第二步：四次方根映射。学术论文 Flesch 仅 1-10，直接展示体验差：

```python
adjusted = 100 * pow(flesch / 100, 0.25)
```

| Flesch | 调整后 | 等级 | 典型文本 |
|---|---|---|---|
| 1.7 | 36 | 较难 | 自然科学论文 |
| 10 | 56 | 中等 | 技术报告 |
| 30 | 74 | 简单 | 科普文章 |
| 60+ | 88+ | 非常简单 | 儿童读物 |

#### 中文算法

中文无国际标准公式，自研减分制模型：

第一步：jieba 分词 + 分句，计算 7 项指标（字符数、词数、句数、唯一词数、平均句长、TTR词汇多样性、长词占比）。

第二步：从满分 100 起扣：

```python
score = 100
      - max(0, avgSentenceLength - 15) * 3    # 句长：超15字扣3分/字
      - longWordRatio * 50                     # 长词：>=4字词占比*50
      - max(0, TTR - 0.8) * 20                 # 词汇多样性：超0.8扣分
```

- 句长惩罚：长句对阅读障碍负担大，25字句扣30分
- 长词惩罚：专业术语密集扣分多
- TTR惩罚：词汇太丰富=读者要不断理解新词

#### 等级划分

| 分数 | 等级 | 含义 |
|---|---|---|
| >=80 | 非常简单 | 适合所有阅读障碍者 |
| 60-79 | 简单 | 大部分无障碍 |
| 40-59 | 中等 | 可能需辅助 |
| 25-39 | 较难 | 建议文本优化 |
| <25 | 非常难 | 强烈建议优化 |

### 3.8 文本精炼管道

基于 LangGraph StateGraph 的多 Agent 迭代系统。核心：生成->评估->反馈->再生成。

#### 为什么迭代

单次调用可能改写不彻底、词汇替换不完全、或丢失信息。迭代让评估器打分，弱项反馈给 Agent 改进，最多 3 轮。

#### 流程图

```
pre_evaluate(基线分) -> [FullRefineAgent|SummaryAgent] -> judge(评估)
                           ^                                  |
                           |______ 不达标 + 微调提示 ________|
```

#### FullRefineAgent（全文改写）

目标：改写成小学生能看懂的大白话，100%保留信息。

1. 句式：长句拆短句，中文<=15字、英文<=12词。不用复杂句式，一律主谓宾。
2. 词汇：书面语换大白话。内置示例映射表（显著提升->大大提高、呈现下降趋势->下降了、相较于->比、其->它的、该->这个），专业术语保留并解释。
3. 排版：每段<=3句，段间空行。
4. 温度 0.7：输出更口语化，避免翻译腔。
5. 强制原语种："必须用中文输出"或"必须用英文输出"。

#### SummaryAgent（摘要生成）

1. 三种长度：简短(2-3句)、标准、详细。
2. 强制原语种：显式指定输出语言。
3. 温度 0.3：保证准确性。

#### DyslexiaEvaluator（质量评估器）

纯本地计算，零 API 调用，每次 <100ms。三维度等权重(1/3)，已移除叙事维度：

**阅读有效性**：FRE + FKGL + 平均句长归一化，各1/3。衡量句法复杂度。

**内容保真**：BLEU（nltk sentence_bleu），以原文为reference。衡量信息保留程度，确保100%原则。

**排版有效性**：段落数(log归一化) + 平均段长(1-avg/200) + 标点密度(punc/chars*15)，各1/3。衡量排版友好度。

总评分 = (阅读 + 内容 + 排版) / 3

终止条件：总评分>=阈值(zh:0.65 en:0.70) 且 内容保真>=0.70。最大3轮兜底。

### 3.9 思维导图

两步流程：

```
Step 1: DeepSeek LLM 提取大纲
  输入：原文
  Prompt：提取结构，生成 4 级标题的 Markdown 大纲
  约束：原文语种输出、每节点 15 字/词
  重试：失败自动重试 3 次（温度递增）

Step 2: MCP stdio 渲染 HTML
  调用：npx -y @jinzcdev/markmap-mcp-server
  工具：markdown_to_mindmap
  输出：HTML 文件保存到 storage/mindmap/
```

### 3.10 数据库设计

**User**：id, email, username, password_hash, role(user/admin), status(pending/approved/rejected), is_active, created_at

**Document**：id, user_id(FK), original_filename, file_type(pdf/image/text), file_url, extracted_text, processing_status, created_at

**DocumentBlock**：id, document_id(FK), page, block_order, block_type(text/image), text_content, image_url, image_caption, bbox_json

**ApprovalRequest**：id, user_id(FK), request_type(register/password_change), payload_json, status, reviewed_by(FK), reviewed_at, created_at

---

## 4. 前端实现

### 4.1 路由

```
/                     Home（首页）
/login                Login（登录）
/register             Register（注册）
/upload               Upload（上传）
/reader_view/:id      ReaderView（标准阅读器）
/chenjinshi/:id       Chenjinshi（沉浸式阅读器）
```

无导航守卫，认证通过 axios 拦截器控制：401 时自动清除登录态并跳转 /login。

### 4.2 HTTP 请求封装

- baseURL: `http://localhost:8000/api/v1`，超时 180 秒
- 请求拦截器：自动注入 JWT Token
- 响应拦截器：自动解包 `res.data`，401 跳转登录

### 4.3 状态管理

Pinia + persistedstate 插件持久化到 localStorage。userStore 存储 username/password/token/role，刷新不丢失。

### 4.4 沉浸式阅读器核心数据流

```
1. loadDocumentData()
   并行请求：文档详情 + 结构化数据
   提取 allBlocks（文本块 + 图片块）

2. POS Tagging
   过滤文本块 并行调用 posTaggingAPI
   buildMixedHtml() 生成排版 HTML

3. 后台预热
   preWarmTTS()      生成音频文件
   preWarmRefine()   并行：文本优化 + 摘要 + 思维导图

4. 用户交互
   划词翻译：mouseup wordLookupAPI WordTooltip 弹窗
   TTS 播放：优先用预热音频 秒开
   文本优化：优先用缓存 秒显示
   可读性评分：优化后评简化版，未优化评原文
   摘要：优先用缓存（标准长度）
   思维导图：优先用缓存 iframe 展示
```

### 4.5 图文混排模式

- **图文共存（默认）**：图片嵌入文本中（max-width:70%, max-height:300px），左侧不触发图片栏
- **图文分离**：文本不嵌入图片，左侧点击标签滑出 360px 图片面板

### 4.6 预热缓存机制

进入文章后，后台静默并行执行 TTS 生成 + 文本优化 + 摘要 + 思维导图。结果存入 ref，后续点击秒开。

### 4.7 阅读辅助工具

| 工具 | 实现 |
|---|---|
| 阅读障碍尺 | 跟随鼠标的水平横线，mousemove 更新 top，高度可调 10-100px |
| 焦点引导屏 | 上下遮罩+中间可视区，::before/::after 伪元素，可视高度 50-500px |
| 字体切换 | 9 种字体，含 Lexend/Inclusive Sans/Andika New Basic 辅助阅读字体（CDN 加载） |
| 阅读主题 | 暖黄/护眼黑/纯白/天空蓝，CSS 变量 `--theme-bg` / `--theme-text` 穿透 scoped 样式 |
| 自动滚动 | setInterval 50ms 匀速滚动，速度 0.5-5px 可调，开关独立控制 |
| 图文模式 | 共存（图片嵌入）+ 分离（图片归左侧面板），点击切换按钮即时生效 |

### 4.8 阅读主题实现

4 种预设主题，CSS 变量穿透 Vue scoped 样式：

```javascript
watch(() => config.selectedTheme, (val) => {
  const themes = {
    warm:  { bg: '#fff9e6', text: '#1f2937' },  // 暖黄（默认）
    dark:  { bg: '#1f2937', text: '#e5e7eb' },  // 护眼黑
    white: { bg: '#ffffff', text: '#1f2937' },  // 纯白
    blue:  { bg: '#eff6ff', text: '#1e40af' },  // 天空蓝
  }
  // 设置 CSS 变量 → 内部组件通过 var(--theme-bg) var(--theme-text) 继承
})
```

### 4.9 预热缓存机制

进入文章后，后台并行执行：

1. **TTS 全音色预热**：4 个声音（晓晓/云希/Jenny/Guy）全部生成音频存 Map
2. **文本优化预热**：调用 full_refine API，结果缓存
3. **摘要预热**：调用 summary API（标准长度），结果缓存
4. **思维导图预热**：调用 mindmap API，HTML URL 缓存

点击播放/优化/摘要/导图 → 优先查缓存 → 命中即秒开，不命中则实时生成。

### 4.10 Pinia 缓存存储

缓存统一由 `cacheStore.js`（Pinia + persistedstate）管理，不再手动操作 localStorage：

```javascript
// stores/cacheStore.js
docCache: {
  [docId]: {
    refine: '...',          // 全文改写结果
    summary: { ... },       // 摘要结果
    mindmap: 'http://...',  // 思维导图 URL
    tts: {                  // 各音色音频 URL
      'zh-CN-XiaoxiaoNeural': '/static/tts/...',
      'zh-CN-YunxiNeural': '/static/tts/...',
      ...
    }
  }
}
```

| 操作 | 行为 |
|---|---|
| 进入文章 | 从 store 读缓存 → 秒开 |
| 预热完成 | 写入 store → 自动持久化 localStorage |
| 用户登出 | `clearAll()` → 清空全部缓存 |
| 刷新页面 | Pinia 自动从 localStorage 恢复 |

---

## 5. 核心功能详解

### 5.1 图文共存/分离模式

`config.displayMode = 'mixed' | 'separated'`

`buildMixedHtml(blocks, tokens, displayMode)` 根据模式决定图片是否嵌入 HTML。切换时 `watch(displayMode)` 自动重建 HTML。图片面板仅在 separated 模式下出现，点击标签展开。

### 5.2 文本优化前后对比

**优化前**：
> 本文通过对比分析AI生成与学者撰写的档案学期刊文献内容，深入探讨了AI技术在学术写作中的应用潜力及其相较于学者创作的相对优势与局限性。

**优化后**：
> 本文对比分析了AI生成的档案学期刊内容。也对比了学者写的内容。我们探讨了AI在学术写作中的潜力。还研究了AI比学者写的好在哪里。也看了AI的不足之处。

### 5.3 英文可读性评分优化

**问题**：原始 Flesch Reading Ease 对学术论文打分极低（1.7/100）。

**解决**：四次方根映射 `adjustedScore = 100 * (fleschScore/100)^0.25`

| 文本类型 | Flesch 原始 | 调整后 | 等级 |
|---|---|---|---|
| 学术论文 | 1.7 | 36 | 较难 |
| 技术文档 | 10 | 56 | 中等 |
| 科普文章 | 30 | 74 | 简单 |
| 儿童读物 | 70+ | 91+ | 非常简单 |

### 5.4 音频缓存

相同文本+音色+语速的音频 MD5 哈希命名，重复播放直接返回已有文件，避免重复调用 edge-tts。

---

## 6. API 接口文档

### 6.1 无需认证

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | / | 健康检查 |
| POST | /api/v1/auth/register | 注册 |
| POST | /api/v1/auth/login | 登录（OAuth2 表单） |
| POST | /api/v1/nlp/pos-tagging | 词性标注 |
| POST | /api/v1/nlp/word-lookup | 划词翻译 |
| POST | /api/v1/tts | 全文 TTS |
| POST | /api/v1/tts/sentences | 逐句 TTS |
| GET | /api/v1/tts/voices | 音色列表 |
| POST | /api/v1/readability | 可读性评分（Form） |
| POST | /api/v1/refine | 文本精炼（JSON） |
| POST | /api/v1/mindmap/generate | 思维导图 |
| POST | /api/v1/admin/seed-admin | 初始化管理员 |

### 6.2 Refine 请求

```json
{
  "original_text": "需要处理的原文",
  "mode": "full_refine",
  "summary_length": "标准",
  "max_iterations": 1,
  "pass_threshold": null
}
```

### 6.3 Refine 响应

```json
{
  "success": true,
  "lang": "zh",
  "refined_text": "改写后的文本",
  "iterations": 1,
  "origin_score": { "total_score": 0.65 },
  "final_score": { "total_score": 0.74 },
  "improvement": { "total_score": "+0.0900" }
}
```

### 6.4 需登录（JWT）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/v1/auth/password-change-request | 改密申请 |
| POST | /api/v1/documents/upload | 上传文档 |
| GET | /api/v1/documents | 文档列表 |
| GET | /api/v1/documents/{id} | 文档详情 |
| GET | /api/v1/documents/{id}/structured | 结构化文档 |
| GET | /api/v1/documents/{id}/paragraphs | 段落列表 |

### 6.5 需管理员

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/v1/admin/approval-requests | 审批列表 |
| POST | /api/v1/admin/approval-requests/{id}/approve | 审批通过 |
| POST | /api/v1/admin/approval-requests/{id}/reject | 审批驳回 |

---

## 7. 部署与运维

### 7.1 环境变量

```env
APP_NAME=Dyslexia Reader Backend
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./dyslexia_reader.db
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
LLM_MODEL_ID=deepseek-chat
TTS_VOICE_ZH=zh-CN-XiaoxiaoNeural
TTS_VOICE_EN=en-US-AriaNeural
YOUDAO_APP_KEY=xxx
YOUDAO_APP_SECRET=xxx
```

### 7.2 启动

```bash
# 后端
cd dyslexia_reader-main
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端
cd vue3_Dyslexia
npm install
npm run dev

# 初始化管理员（admin / Admin@123456）
curl -X POST http://127.0.0.1:8000/api/v1/admin/seed-admin
```

### 7.3 模型安装

```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('cmudict'); nltk.download('punkt_tab')"
```

### 7.4 测试

```bash
python test_all_apis.py   # 后端全量 API 测试
npm run build             # 前端构建检查
```

### 7.5 版本回退

```bash
git checkout v1.0-pre-test      # 测试前快照
git checkout v1.0-pre-optimize  # 优化前快照
```

---

## 8. 已知问题与优化方向

### 8.1 CID 编码中文 PDF

部分早期中文学术 PDF 使用 CID 编码字体，PyMuPDF 和 OCR 均无法正确提取。建议用 Chrome 打开 PDF 打印另存为 PDF 重新编码后上传。

### 8.2 后续优化

- PostgreSQL 生产数据库迁移
- Alembic 正规数据库迁移框架
- 路由导航守卫
- TTS 流式播放
- 漫画解读功能实现
- 多语言界面国际化
