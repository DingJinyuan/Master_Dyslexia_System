# 思维导图 MCP 接入 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在沉浸式阅读器中新增思维导图功能 — DeepSeek LLM 提取大纲 + MCP 渲染 HTML + iframe 模态展示

**Architecture:** 后端新增 mindmap API 路由，MindmapService 封装两步流程（LLM → MCP），HTML 写入 storage/mindmap/ 通过已有 /storage 挂载访问；前端新增 MindMapModal 组件用 iframe 嵌入，ReaderPanel 加按钮触发

**Tech Stack:** Python `mcp` SDK, `@jinzcdev/markmap-mcp-server` (npx stdio), DeepSeek (AsyncOpenAI), Vue 3 + Element Plus el-dialog

## Global Constraints

- 后端遵循现有模式：router → service → response schema，复用 `AsyncOpenAI`（`app/core/config.py` settings）
- 前端遵循现有模式：`apis/` 封装 → Chenjinshi `index.vue` 状态管理 → Modal 组件，对齐 `summaryState` 模式
- API 无需认证（对齐 `/refine`, `/readability`）
- `mcp` 包需加入 `requirements.txt`
- 前端无需新增 npm 依赖（iframe 嵌入）
- 测试写入 `test_all_apis.py`，遵循现有 `test()` helper 模式

---

### Task 1: 安装 mcp 依赖并配置

**Files:**
- Modify: `dyslexia_reader-main/requirements.txt`
- Modify: `dyslexia_reader-main/app/core/config.py`

**Interfaces:**
- Produces: `settings.MCP_MINDMAP_TIMEOUT` (int, default 60)

- [ ] **Step 1: 在 requirements.txt 中添加 mcp 包**

```
mcp>=1.0.0
```

追加到 `requirements.txt` 末尾（在 `# ---- Optional ----` 之前）。

- [ ] **Step 2: 安装依赖**

```bash
cd dyslexia_reader-main && pip install mcp>=1.0.0
```

- [ ] **Step 3: 在 config.py 中添加配置项**

在 `app/core/config.py` 的 `Settings` 类中，`TTS_OUTPUT_DIR` 之后添加：

```python
    # ====== MCP 思维导图 ======
    MCP_MINDMAP_TIMEOUT: int = 60
```

- [ ] **Step 4: 验证配置可读取**

```bash
cd dyslexia_reader-main && python -c "from app.core.config import settings; print(settings.MCP_MINDMAP_TIMEOUT)"
```

Expected: `60`

- [ ] **Step 5: Commit**

```bash
git add dyslexia_reader-main/requirements.txt dyslexia_reader-main/app/core/config.py
git commit -m "chore: add mcp dependency and MCP_MINDMAP_TIMEOUT config"
```

---

### Task 2: 创建 MindmapRequest/Response Schema

**Files:**
- Create: `dyslexia_reader-main/app/schemas/mindmap.py`

**Interfaces:**
- Produces: `MindmapRequest(text: str, max_depth: int)`, `MindmapResponse(success: bool, markdown: str, html_url: str, error: str)`

- [ ] **Step 1: 创建 schema 文件**

```python
"""思维导图 — 请求/响应 Schema"""

from pydantic import BaseModel, Field
from typing import Optional


class MindmapRequest(BaseModel):
    text: str = Field(..., min_length=1, description="需要提取大纲的原文")
    max_depth: int = Field(4, ge=2, le=6, description="导图最大层级深度")


class MindmapResponse(BaseModel):
    success: bool
    markdown: Optional[str] = Field(None, description="LLM 生成的 Markdown 大纲")
    html_url: Optional[str] = Field(None, description="MCP 渲染后的 HTML 导图 URL")
    error: Optional[str] = Field(None, description="错误信息")
```

- [ ] **Step 2: 验证导入**

```bash
cd dyslexia_reader-main && python -c "from app.schemas.mindmap import MindmapRequest, MindmapResponse; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add dyslexia_reader-main/app/schemas/mindmap.py
git commit -m "feat: add MindmapRequest/MindmapResponse schemas"
```

---

### Task 3: 创建 MindmapService

**Files:**
- Create: `dyslexia_reader-main/app/services/mindmap_service.py`

**Interfaces:**
- Produces: `MindmapService` class
  - `async generate(text: str, max_depth: int = 4) -> dict` — 返回 `{"markdown": str, "html_url": str}`
  - `async _llm_extract_outline(text: str, max_depth: int) -> str`
  - `async _mcp_render(markdown: str) -> str`

- [ ] **Step 1: 编写 MindmapService 实现**

```python
"""思维导图生成服务 — LLM 大纲提取 + MCP HTML 渲染"""

import os
import uuid
import logging
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import settings

logger = logging.getLogger(__name__)


class MindmapService:
    """思维导图生成：DeepSeek LLM 提取大纲 → MCP 渲染 HTML"""

    def __init__(self):
        self._llm = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
            timeout=settings.MCP_MINDMAP_TIMEOUT,
        )
        self._server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@jinzcdev/markmap-mcp-server"],
        )

    async def generate(self, text: str, max_depth: int = 4) -> dict:
        """主流程：LLM 提取大纲 → MCP 渲染 HTML → 写入文件返回 URL"""
        markdown = await self._llm_extract_outline(text, max_depth)

        if not markdown or not markdown.strip():
            raise ValueError("LLM 返回的大纲为空")

        html = await self._mcp_render(markdown)

        if not html or not html.strip():
            raise ValueError("MCP 渲染的 HTML 为空")

        output_dir = os.path.join("storage", "mindmap")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.html"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return {
            "markdown": markdown,
            "html_url": f"/storage/mindmap/{filename}",
        }

    async def _llm_extract_outline(self, text: str, max_depth: int) -> str:
        """DeepSeek LLM 从原文提取 Markdown 大纲"""
        system_prompt = (
            f"你是思维导图专家。从文本中提取结构，生成不超过{max_depth}级标题的Markdown大纲。"
            f"要求：\n"
            f"1. 使用 # ## ### #### 标题层级，不超过{max_depth}级\n"
            f"2. 保留核心概念、关键词、逻辑关系\n"
            f"3. 每个节点简洁（不超过15字）\n"
            f"4. 只输出Markdown，不要任何解释或其他内容"
        )

        try:
            response = await self._llm.chat.completions.create(
                model=settings.LLM_MODEL_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM 大纲提取失败: {e}")
            raise RuntimeError(f"大纲提取失败: {e}")

    async def _mcp_render(self, markdown: str) -> str:
        """通过 MCP stdio 调用 markmap-mcp-server 渲染 HTML"""
        try:
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("markdown-to-mindmap", {
                        "markdown": markdown,
                    })
                    # result.content 是 list[TextContent]，取第一个的 text
                    if result.content and len(result.content) > 0:
                        return result.content[0].text
                    raise RuntimeError("MCP 返回内容为空")
        except Exception as e:
            logger.error(f"MCP 渲染失败: {e}")
            raise RuntimeError(f"思维导图渲染失败，请确认 Node.js v20+ 已安装: {e}")
```

- [ ] **Step 2: 验证导入**

```bash
cd dyslexia_reader-main && python -c "from app.services.mindmap_service import MindmapService; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add dyslexia_reader-main/app/services/mindmap_service.py
git commit -m "feat: add MindmapService — LLM outline + MCP HTML render"
```

---

### Task 4: 创建 mindmap API 路由

**Files:**
- Create: `dyslexia_reader-main/app/api/mindmap.py`

**Interfaces:**
- Produces: `router: APIRouter` with `POST /mindmap/generate`
- Consumes: `MindmapService.generate(text, max_depth)`, `MindmapRequest`, `MindmapResponse`

- [ ] **Step 1: 创建路由文件**

```python
"""思维导图生成 API — POST /api/v1/mindmap/generate"""

from fastapi import APIRouter, HTTPException

from app.schemas.mindmap import MindmapRequest, MindmapResponse
from app.services.mindmap_service import MindmapService

router = APIRouter(prefix="/mindmap", tags=["mindmap"])

_service = MindmapService()


@router.post("/generate", response_model=MindmapResponse, summary="生成思维导图")
async def api_generate_mindmap(req: MindmapRequest):
    """
    两步生成思维导图：
    1. DeepSeek LLM 从原文提取 Markdown 大纲
    2. MCP markmap-mcp-server 渲染为交互式 HTML
    返回 Markdown 大纲和 HTML 文件 URL
    """
    try:
        result = await _service.generate(req.text, req.max_depth)
        return MindmapResponse(
            success=True,
            markdown=result["markdown"],
            html_url=result["html_url"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"思维导图生成异常: {e}")
```

- [ ] **Step 2: 验证路由导入**

```bash
cd dyslexia_reader-main && python -c "from app.api.mindmap import router; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add dyslexia_reader-main/app/api/mindmap.py
git commit -m "feat: add POST /api/v1/mindmap/generate route"
```

---

### Task 5: 在 main.py 注册路由

**Files:**
- Modify: `dyslexia_reader-main/app/main.py:8` (import line)
- Modify: `dyslexia_reader-main/app/main.py:59-66` (router registration area)

- [ ] **Step 1: 在 main.py 导入 mindmap 路由**

在 `app/main.py` 第 8 行，把 `from app.api import admin, auth, documents, nlp, tts, readability, refine` 改为：

```python
from app.api import admin, auth, documents, nlp, tts, readability, refine, mindmap
```

- [ ] **Step 2: 注册路由**

在 `app.include_router(readability.router, prefix="/api/v1")` 之后添加：

```python
app.include_router(mindmap.router, prefix="/api/v1")
```

- [ ] **Step 3: 验证服务启动**

```bash
cd dyslexia_reader-main && timeout 5 uvicorn app.main:app --host 127.0.0.1 --port 8000 2>&1 || true
```

Expected: 启动日志中出现 `/api/v1/mindmap` 相关路由注册信息

- [ ] **Step 4: 验证 Swagger 文档可见**

启动服务后访问 `http://127.0.0.1:8000/docs`，确认 mindmap 标签和 `POST /api/v1/mindmap/generate` 出现在 Swagger 中。

- [ ] **Step 5: Commit**

```bash
git add dyslexia_reader-main/app/main.py
git commit -m "feat: register mindmap router in main.py"
```

---

### Task 6: 后端集成测试

**Files:**
- Modify: `dyslexia_reader-main/test_all_apis.py`

- [ ] **Step 1: 在测试文件中添加 mindmap 测试用例**

在 `test_all_apis.py` 的 `run_all_tests()` 函数末尾（`print("\n" + "="*60)` 结果汇总之前）添加：

```python
    # ========== 17. 思维导图生成 ==========
    print("\n" + "="*60)
    print("模块: Mindmap / 思维导图生成")

    # 正常请求 — 中文
    resp = test(
        "生成中文思维导图",
        "POST",
        "/mindmap/generate",
        expected_status=200,
        data={"text": "# 人工智能发展史\n\n人工智能经历了三次浪潮。第一次是1950年代的符号主义。第二次是1980年代的专家系统。第三次是2010年代的深度学习。目前大语言模型成为主流。", "max_depth": 3},
    )
    if resp and resp.status_code == 200:
        body = resp.json()
        if body.get("success") and body.get("html_url", "").startswith("/storage/mindmap/"):
            print("  [PASS] 中文思维导图 — html_url 格式正确")
            PASS += 1
        else:
            FAIL += 1
            msg = f"  [FAIL] 中文思维导图 — success={body.get('success')}, html_url={body.get('html_url', 'MISSING')[:80]}"
            print(msg)
            ERRORS.append(msg)

    # 英文测试
    resp = test(
        "生成英文思维导图",
        "POST",
        "/mindmap/generate",
        expected_status=200,
        data={"text": "Artificial Intelligence has revolutionized many fields. Machine Learning enables pattern recognition. Deep Learning uses neural networks. Transformers power modern LLMs.", "max_depth": 3},
    )
    if resp and resp.status_code == 200:
        body = resp.json()
        if body.get("success") and body.get("markdown"):
            print("  [PASS] 英文思维导图 — 生成成功")
            PASS += 1
        else:
            FAIL += 1
            print(f"  [FAIL] 英文思维导图 — {resp.text[:100]}")
            ERRORS.append(f"英文思维导图失败: {resp.text[:100]}")

    # 空文本校验
    test(
        "空文本应返回 422",
        "POST",
        "/mindmap/generate",
        expected_status=422,
        data={"text": "", "max_depth": 3},
    )

    # 测试 HTML URL 可访问
    resp = test(
        "生成导图并验证 URL 可访问",
        "POST",
        "/mindmap/generate",
        expected_status=200,
        data={"text": "测试文本", "max_depth": 2},
    )
    if resp and resp.status_code == 200:
        html_url = resp.json().get("html_url", "")
        if html_url:
            test(
                "访问生成的 HTML 文件",
                "GET",
                html_url,
                expected_status=200,
            )
```

- [ ] **Step 2: 启动后端服务并运行测试**

```bash
cd dyslexia_reader-main
# 终端1: 启动服务
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 终端2: 运行测试
python test_all_apis.py
```

Expected: Mindmap 模块测试全部 PASS

- [ ] **Step 3: 验证 HTML 导图文件可以被浏览器加载**

在浏览器访问 `http://127.0.0.1:8000/storage/mindmap/<filename>.html`，确认可缩放、可折叠节点的交互式思维导图正常显示。

- [ ] **Step 4: Commit**

```bash
git add dyslexia_reader-main/test_all_apis.py
git commit -m "test: add mindmap API integration tests"
```

---

### Task 7: 前端 — 创建 mindmap API 封装

**Files:**
- Create: `vue3_Dyslexia/src/apis/mindmap.js`

**Interfaces:**
- Produces: `generateMindmapAPI(data)` — `data: { text: string, max_depth: number }`, returns `Promise<{ success, markdown, html_url, error }>`

- [ ] **Step 1: 创建 API 封装文件**

```javascript
import httpInstance from '@/utils/http'

/**
 * 生成思维导图（LLM 大纲提取 + MCP HTML 渲染）
 * @param {Object} data - 请求参数
 * @param {string} data.text - 文档全文
 * @param {number} [data.max_depth=4] - 导图最大层级（2-6）
 * @returns {Promise<Object>} { success, markdown, html_url, error }
 */
export const generateMindmapAPI = (data) => {
  return httpInstance({
    url: 'mindmap/generate',
    method: 'POST',
    data: {
      text: data.text,
      max_depth: data.max_depth || 4,
    },
  })
}
```

- [ ] **Step 2: 验证导入**

```bash
cd vue3_Dyslexia && node -e "require('./src/apis/mindmap.js'); console.log('OK')" 2>&1 || echo "ESM — 需要 Vite 环境，跳过 Node 直接验证"
```

- [ ] **Step 3: Commit**

```bash
git add vue3_Dyslexia/src/apis/mindmap.js
git commit -m "feat: add generateMindmapAPI frontend wrapper"
```

---

### Task 8: 前端 — 创建 MindMapModal 组件

**Files:**
- Create: `vue3_Dyslexia/src/views/Chenjinshi/Components/MindMapModal.vue`

**Interfaces:**
- Props: `visible: Boolean`, `loading: Boolean`, `error: String`, `htmlUrl: String`
- Events: `update:visible`, `retry`

- [ ] **Step 1: 创建 MindMapModal 组件**

```vue
<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  htmlUrl: { type: String, default: '' },
})

defineEmits(['update:visible', 'retry'])
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="🧠 思维导图"
    width="90%"
    top="3vh"
    destroy-on-close
    :close-on-click-modal="false"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="mindmap-loading">
      <div class="loading-spinner"></div>
      <p>AI 正在分析文档结构，生成思维导图...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="mindmap-error">
      <p class="error-text">{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">🔄 重试</button>
    </div>

    <!-- 导图 iframe -->
    <iframe
      v-else-if="htmlUrl"
      :src="htmlUrl"
      class="mindmap-iframe"
      frameborder="0"
    />

    <!-- 空状态 -->
    <div v-else class="mindmap-empty">
      <p>暂无思维导图数据</p>
    </div>
  </el-dialog>
</template>

<style scoped>
.mindmap-iframe {
  width: 100%;
  height: 80vh;
  border: none;
  border-radius: 8px;
  background: #fff;
}

.mindmap-loading,
.mindmap-error,
.mindmap-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.error-text {
  color: #ef4444;
  margin-bottom: 16px;
  max-width: 500px;
}

.retry-btn {
  padding: 8px 20px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #1d4ed8;
}
</style>
```

- [ ] **Step 2: Verify imports resolve**

```bash
cd vue3_Dyslexia && npx vue-tsc --noEmit src/views/Chenjinshi/Components/MindMapModal.vue 2>&1 || echo "Type check skipped (no tsconfig)"
```

- [ ] **Step 3: Commit**

```bash
git add vue3_Dyslexia/src/views/Chenjinshi/Components/MindMapModal.vue
git commit -m "feat: add MindMapModal component with iframe embed"
```

---

### Task 9: 前端 — 在 ReaderPanel 添加「思维导图」按钮

**Files:**
- Modify: `vue3_Dyslexia/src/views/Chenjinshi/Components/ReaderPanel.vue`

- [ ] **Step 1: 添加 emit 事件声明**

在 `defineEmits` 数组中，`'generate-summary'` 之后添加：

```javascript
  'generate-mindmap', // 新增：触发生成思维导图
```

- [ ] **Step 2: 添加按钮**

在「📝 生成文本摘要」按钮之后、「漫画生成」section 之前，添加：

```html
        <button class="func-btn" @click="emit('generate-mindmap')">
          🧠 思维导图
        </button>
```

完整上下文（在 `<div class="panel-section">` 阅读辅助 section 内）：

```html
        <button class="func-btn" @click="emit('calculate-readability')">📊 可读性评分</button>
        <button class="func-btn" @click="emit('generate-summary')" :disabled="isGenerating">📝 生成文本摘要</button>
        <button class="func-btn" @click="emit('generate-mindmap')">🧠 思维导图</button>
```

- [ ] **Step 3: Commit**

```bash
git add vue3_Dyslexia/src/views/Chenjinshi/Components/ReaderPanel.vue
git commit -m "feat: add mindmap button to ReaderPanel"
```

---

### Task 10: 前端 — 在 Chenjinshi/index.vue 集成思维导图

**Files:**
- Modify: `vue3_Dyslexia/src/views/Chenjinshi/index.vue`

- [ ] **Step 1: 导入 MindMapModal 组件和 API**

在 `<script setup>` 顶部的 import 区，`import SummaryModal` 之后添加：

```javascript
import MindMapModal from './Components/MindMapModal.vue'
```

在 API import 行（`from '@/apis/nlp.js'`），追加 `generateMindmapAPI`：

把：
```javascript
import { wordLookupAPI, posTaggingAPI, readabilityScoreAPI, refineTextAPI } from '@/apis/nlp.js'
```

改为：
```javascript
import { wordLookupAPI, posTaggingAPI, readabilityScoreAPI, refineTextAPI } from '@/apis/nlp.js'
import { generateMindmapAPI } from '@/apis/mindmap.js'
```

- [ ] **Step 2: 添加 mindmapState 状态**

在 `summaryState` 定义之后添加：

```javascript
// 思维导图状态
const mindmapState = ref({
  visible: false,
  loading: false,
  error: '',
  htmlUrl: '',
})
```

- [ ] **Step 3: 添加 generateMindmap 和 closeMindmapModal 方法**

在 `closeSummaryModal` 函数之后添加：

```javascript
// 生成思维导图
const generateMindmap = async () => {
  const text = originalText.value
  if (!text || text.includes('加载中') || text.includes('无可用') || text.includes('文档格式异常')) {
    mindmapState.value = { visible: true, loading: false, error: '暂无可用文本用于生成思维导图', htmlUrl: '' }
    return
  }
  mindmapState.value = { visible: true, loading: true, error: '', htmlUrl: '' }
  try {
    const res = await generateMindmapAPI({ text, max_depth: 4 })
    if (res?.success) {
      mindmapState.value = { visible: true, loading: false, error: '', htmlUrl: res.html_url }
    } else {
      mindmapState.value = { visible: true, loading: false, error: res?.error || '生成失败', htmlUrl: '' }
    }
  } catch (err) {
    const errMsg = err.response?.data?.detail || err.message || '思维导图生成失败'
    mindmapState.value = { visible: true, loading: false, error: errMsg, htmlUrl: '' }
  }
}

const closeMindmapModal = () => {
  mindmapState.value = { visible: false, loading: false, error: '', htmlUrl: '' }
}
```

- [ ] **Step 4: 在 ReaderPanel 上绑定事件**

在 `<ReaderPanel>` 组件上，`@generate-summary` 之后添加：

```html
      @generate-mindmap="generateMindmap"
```

- [ ] **Step 5: 在模板中添加 MindMapModal**

在 `<SummaryModal>` 之后、`<!-- 图片全屏预览 -->` 之前添加：

```html
    <!-- 思维导图弹窗 -->
    <MindMapModal
      :visible="mindmapState.visible"
      :loading="mindmapState.loading"
      :error="mindmapState.error"
      :html-url="mindmapState.htmlUrl"
      @update:visible="closeMindmapModal"
      @retry="generateMindmap"
    />
```

- [ ] **Step 6: 验证前端编译**

```bash
cd vue3_Dyslexia && npx vite build --mode development 2>&1 | tail -5
```

Expected: 构建成功，无报错。

- [ ] **Step 7: Commit**

```bash
git add vue3_Dyslexia/src/views/Chenjinshi/index.vue
git commit -m "feat: integrate mindmap generation into Chenjinshi reader"
```

---

### Task 11: 端到端测试与验证

**Files:**
- 无新建/修改（验证步骤）

- [ ] **Step 1: 启动全栈服务**

```bash
# 终端1: 后端
cd dyslexia_reader-main
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 终端2: 前端
cd vue3_Dyslexia
npm run dev
```

- [ ] **Step 2: 运行后端 API 测试**

```bash
cd dyslexia_reader-main && python test_all_apis.py
```

Expected: 所有测试 PASS，包括 mindmap 模块。

- [ ] **Step 3: 手动端到端验证清单**

访问 `http://localhost:5173`，登录后执行：

- [ ] 打开一个已有文档进入沉浸式阅读器（`/chenjinshi/:id`）
- [ ] 鼠标移到右侧触发 ReaderPanel 滑出
- [ ] 确认「🧠 思维导图」按钮出现在「📝 生成文本摘要」下方
- [ ] 点击「🧠 思维导图」
- [ ] 确认弹窗打开，显示 loading spinner 和 "AI 正在分析文档结构..."
- [ ] 等待生成完成，确认 iframe 加载思维导图 HTML
- [ ] 在导图上测试：节点折叠/展开、缩放、拖拽平移
- [ ] 关闭弹窗，确认状态重置
- [ ] 再次点击按钮，确认正常重新生成
- [ ] 测试长文档（>5000字），确认不超时

- [ ] **Step 4: 测试错误场景**

- [ ] 在未安装 `@jinzcdev/markmap-mcp-server` 的环境（或临时禁用 npx）下点击按钮 → 确认显示 "请确认 Node.js v20+ 已安装" 错误提示
- [ ] 传入空白页面 → 确认显示 "暂无可用文本"

- [ ] **Step 5: 最终 Commit（如有修正）**

```bash
git status
# 如有任何修正，add + commit
```
