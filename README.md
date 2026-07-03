# 优读 EASE — 阅读障碍辅助系统

面向**阅读障碍（Dyslexia）**用户的辅助阅读 Web 应用。支持文档上传解析、词性标注、TTS 语音朗读、划词翻译、AI 文本优化、可读性评分、思维导图等功能。

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 20+（仅思维导图 MCP 需要）
- DeepSeek API Key（文本优化/摘要/思维导图需要）

### 后端启动

```bash
cd dyslexia_reader-main

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 下载模型
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('cmudict'); nltk.download('punkt_tab')"

# 配置环境变量（复制 .env.example 为 .env，填入 API Key）
cp .env.example .env

# 启动
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 初始化管理员（admin / Admin@123456）
curl -X POST http://127.0.0.1:8000/api/v1/admin/seed-admin
```

### 前端启动

```bash
cd vue3_Dyslexia
npm install
npm run dev
```

打开 http://localhost:5173

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLAlchemy + LangGraph |
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| AI | DeepSeek API |
| TTS | edge-tts + 有道智云 + gTTS + pyttsx3 |
| PDF | PyMuPDF + EasyOCR |
| NLP | jieba + spaCy |
| 思维导图 | MCP markmap-server |

## 核心功能

- **文档解析**：PDF/图片上传，4 层降级策略提取文本
- **词性标注**：中文 jieba + 英文 spaCy，8 色编码
- **TTS 朗读**：多引擎热备 + 音频缓存 + 全音色预热
- **划词翻译**：选中即查，支持中英文
- **可读性评分**：中英文双算法，0-100 分五级标签
- **AI 文本优化**：LangGraph 多轮迭代，口语化改写
- **AI 摘要**：三种长度，强制原语种
- **思维导图**：LLM 提取大纲 + markmap 渲染
- **阅读辅助**：阅读障碍尺、焦点引导屏、自动滚动、4 主题切换
- **图文模式**：共存/分离一键切换

## 项目结构

```
frontend/
├── dyslexia_reader-main/    # 后端
├── vue3_Dyslexia/           # 前端
├── paper/                   # 测试论文
├── FEATURES.md              # 详细技术文档
└── README.md
```

## 文档

- [FEATURES.md](FEATURES.md) — 完整技术文档（架构、API、实现原理）
- [CLAUDE.md](CLAUDE.md) — 开发指南

## 版本

- `v1.0-pre-test` — 2026-07-02 测试前快照
- `v1.0-pre-optimize` — 代码优化前快照
