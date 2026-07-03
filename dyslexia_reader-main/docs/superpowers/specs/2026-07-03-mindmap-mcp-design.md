# 思维导图 MCP 接入 — 设计文档

> 日期：2026-07-03
> 状态：已确认
> 关联：`POST /api/v1/refine` 设计模式（复用 AI 集成架构）

## 1. 需求概述

在沉浸式阅读器（Chenjinshi）中新增「思维导图」功能：

**两步链路**：
1. DeepSeek LLM 从文档全文提取结构化 Markdown 大纲
2. MCP 调用 `@jinzcdev/markmap-mcp-server` 的 `markdown-to-mindmap` tool 渲染为交互式 HTML
3. 前端 MindMapModal 通过 iframe 嵌入展示

**输入**：整篇文档全文
**输出**：交互式 HTML 思维导图（可缩放、折叠/展开节点）
**展示**：模态弹窗（参考现有可读性评分/摘要弹窗模式）

## 2. 架构链路

```
[文档原始文本]
      ↓
[DeepSeek LLM]  ← 生成 Markdown 大纲
      ↓
[Markdown 大纲]
      ↓
[MCP Client (stdio)]  ←  npx -y @jinzcdev/markmap-mcp-server
      ↓                    tool: markdown-to-mindmap
[HTML 交互式导图]
      ↓
[写入 storage/mindmap/ → 返回 URL]
      ↓
[MindMapModal]  ←  iframe 嵌入 HTML
```

**MCP 通信方式**：`npx -y @jinzcdev/markmap-mcp-server` 通过 stdio 启动子进程，`mcp` Python SDK 通过 `StdioServerParameters` + `stdio_client` 连接。

## 3. 后端设计

### 3.1 新增文件

| 文件 | 职责 |
|---|---|
| `app/api/mindmap.py` | 路由 `POST /api/v1/mindmap/generate` |
| `app/schemas/mindmap.py` | Pydantic 请求/响应模型 |
| `app/services/mindmap_service.py` | 两步：LLM 生成大纲 → MCP 渲染 HTML |

### 3.2 修改文件

| 文件 | 改动 |
|---|---|
| `app/main.py` | `from app.api import mindmap` + `app.include_router(mindmap.router, prefix="/api/v1")` |
| `app/core/config.py` | 新增 `MCP_MINDMAP_TIMEOUT: int = 60` |

### 3.3 API 规格

```
POST /api/v1/mindmap/generate
Headers: 无需认证（对齐 /refine, /readability 的公开接口策略）

Request:
{
  "text": "文档全文内容...",
  "max_depth": 4          // 导图最大层级，默认 4，范围 2-6
}

Response (200):
{
  "success": true,
  "markdown": "# 主题\n## 分支1\n### 子节点...",
  "html_url": "/storage/mindmap/abc123.html"
}

Response (500):
{
  "success": false,
  "error": "..."
}
```

### 3.4 MindmapService 伪代码

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

class MindmapService:
    def __init__(self):
        self._llm = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
        )
        self._server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@jinzcdev/markmap-mcp-server"],
        )

    async def generate(self, text: str, max_depth: int = 4) -> dict:
        # 步骤 1：DeepSeek LLM 提取 Markdown 大纲
        markdown = await self._llm_extract_outline(text, max_depth)

        # 步骤 2：MCP 渲染为 HTML
        html = await self._mcp_render(markdown)

        # 步骤 3：写入文件并返回 URL
        filename = f"{uuid.uuid4().hex}.html"
        filepath = os.path.join("storage", "mindmap", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return {
            "markdown": markdown,
            "html_url": f"/storage/mindmap/{filename}",
        }

    async def _llm_extract_outline(self, text: str, max_depth: int) -> str:
        response = await self._llm.chat.completions.create(
            model=settings.LLM_MODEL_ID,
            messages=[{
                "role": "system",
                "content": f"你是思维导图专家。从文本中提取结构，生成不超过{max_depth}级的Markdown大纲。只输出Markdown，不要其他内容。"
            }, {
                "role": "user",
                "content": text,
            }],
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()

    async def _mcp_render(self, markdown: str) -> str:
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("markdown-to-mindmap", {
                    "markdown": markdown,
                })
                return result.content[0].text
```

**错误处理**：
- LLM 调用失败 → 500 + "大纲提取失败: {message}"
- npx 执行超时 → 500 + "MCP 服务启动超时，请确认已安装 Node.js v20+"
- tool 调用失败 → 500 + "思维导图渲染失败: {message}"
- 返回内容为空 → 500 + "思维导图内容为空"

## 4. 前端设计

### 4.1 新增文件

| 文件 | 职责 |
|---|---|
| `src/apis/mindmap.js` | `generateMindmapAPI(data)` — 调用 `POST /mindmap/generate` |
| `src/views/Chenjinshi/Components/MindMapModal.vue` | 弹窗组件，iframe 嵌入 MCP 渲染的 HTML 导图 |

### 4.2 修改文件

| 文件 | 改动 |
|---|---|
| `src/views/Chenjinshi/index.vue` | 新增 `mindmapState`、`generateMindmap()`、`closeMindmapModal()` |
| `src/views/Chenjinshi/Components/ReaderPanel.vue` | 右侧面板新增「🧠 思维导图」按钮 |

### 4.3 前端新增依赖

无需新增 npm 包。交互（缩放/折叠）由 MCP 生成的 HTML 自带，前端只用 iframe 嵌入。

### 4.4 MindMapModal 设计

**模板结构**：
```
<el-dialog v-model="visible" width="90%" top="3vh" destroy-on-close>
  <div v-if="loading" class="loading-container">
    <div class="spinner"></div>
    <p>AI 正在分析文档结构...</p>
  </div>
  <div v-else-if="error" class="error-container">
    <p class="error-text">{{ error }}</p>
    <button @click="$emit('retry')">重试</button>
  </div>
  <iframe
    v-else-if="htmlUrl"
    :src="htmlUrl"
    class="mindmap-iframe"
  />
</el-dialog>
```

**Props**：
- `visible: Boolean`
- `loading: Boolean`
- `error: String`
- `htmlUrl: String` — 后端返回的导图 HTML URL

**Events**：
- `update:visible` — 关闭弹窗
- `retry` — 重新生成

### 4.5 Chenjinshi/index.vue 集成

```javascript
const mindmapState = ref({
  visible: false,
  loading: false,
  error: '',
  htmlUrl: '',
})

const generateMindmap = async () => {
  const text = originalText.value
  if (!text || text.includes('加载中')) {
    mindmapState.value = { visible: true, loading: false, error: '暂无可用文本', htmlUrl: '' }
    return
  }
  mindmapState.value = { visible: true, loading: true, error: '', htmlUrl: '' }
  try {
    const res = await generateMindmapAPI({ text, max_depth: 4 })
    mindmapState.value = { ...mindmapState.value, loading: false, htmlUrl: res.html_url }
  } catch (err) {
    mindmapState.value = { ...mindmapState.value, loading: false, error: err.message || '生成失败' }
  }
}

const closeMindmapModal = () => {
  mindmapState.value = { visible: false, loading: false, error: '', htmlUrl: '' }
}
```

## 5. 数据流

```
用户点击「🧠 思维导图」按钮
    ↓
readerPanel @generate-mindmap → index.vue generateMindmap()
    ↓
MindMapModal visible=true + loading=true
    ↓
generateMindmapAPI({ text, max_depth: 4 })
    ↓ POST /api/v1/mindmap/generate
后端 MindmapService.generate(text, 4)
    ↓ 步骤 1
DeepSeek LLM → Markdown 大纲
    ↓ 步骤 2
MCP stdio → npx @jinzcdev/markmap-mcp-server → tool: markdown-to-mindmap
    ↓ 步骤 3
HTML 写入 storage/mindmap/xxx.html
    ↓
返回 { markdown, html_url }
    ↓
MindMapModal loading=false, <iframe src="html_url">
    ↓
交互式思维导图渲染完成
```

## 6. 错误处理

| 场景 | 后端行为 | 前端行为 |
|---|---|---|
| 文档文本为空/无效 | 400 校验 | 按钮禁用 + tooltip 提示 |
| DeepSeek 调用失败 | 500 + "大纲提取失败" | MindMapModal 显示 error + 重试按钮 |
| MCP Server 启动失败 | 500 + "MCP 服务启动超时" | MindMapModal 显示 error + 提示安装 Node.js |
| MCP tool 调用失败 | 500 + "思维导图渲染失败" | MindMapModal 显示 error + 重试按钮 |
| HTML 写入失败 | 500 + "文件写入失败" | MindMapModal 显示 error |
| 网络超时 | axios 180s 兜底 | 超时提示 |

## 7. 测试要点

- [ ] `POST /api/v1/mindmap/generate` 中文文本 → 中文大纲 + HTML
- [ ] `POST /api/v1/mindmap/generate` 英文文本 → 英文大纲 + HTML
- [ ] MCP Server 未安装/Node.js 缺失 → 友好错误
- [ ] MindMapModal iframe 正常加载 HTML → 缩放/折叠交互正常
- [ ] 关闭弹窗后状态重置，再次打开正常
- [ ] 按钮在文本无效时正确禁用
- [ ] 长文档（>10000 字）不超时
- [ ] HTML 文件可被 StaticFiles 正确挂载访问
