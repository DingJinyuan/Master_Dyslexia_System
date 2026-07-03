# 文本精炼迭代系统 — 设计规格

## 目标

用 LangGraph 构建多 Agent 迭代流水线，替代现有单次调用的 `/simplify` 和 `/summarize` 接口。通过"改写→评估→回流微调"循环，在保留内容保真度的前提下最大化可读性。

## 文件结构

```
app/services/refine/
├── __init__.py               # 导出 RefineOrchestrator
├── base_agent.py             # BaseAgent（LLM client、lang 检测、通用调用、迭代提示）
├── full_refine_agent.py      # FullRefineAgent(BaseAgent) — 全文改写
├── summary_agent.py          # SummaryAgent(BaseAgent) — 摘要
├── evaluator.py              # DyslexiaEvaluator（从 ai.py 迁移，保持接口不变）
└── orchestrator.py           # LangGraph StateGraph + 迭代循环

app/api/
└── refine.py                 # POST /api/v1/refine
```

删除文件：
- `app/services/text_simplify_service.py`
- `app/services/text_summarize_service.py`
- `app/api/text_simplify.py`
- `app/api/summarize.py`

## 状态定义

```python
class RefineState(TypedDict):
    original_text: str
    mode: str                # "full_refine" | "summary"
    lang: str                # "zh" | "en"
    max_iterations: int      # 默认 3
    pass_threshold: float    # 总分合格线，null 时按语言自动选

    refined_text: str        # 当前轮结果
    iter_count: int

    origin_score: dict       # 原文基线分
    current_score: dict      # 本轮评估分
    score_history: list      # [{iter: N, score: {...}}]

    done: bool
    result: dict
```

## LangGraph 图结构

```
START → pre_evaluate → routing → refine_agent (mode=full_refine)
                                → summary_agent (mode=summary)
       ↓
     judge
       ↓
   should_continue?
     ├─ YES → refine_agent / summary_agent（回流）
     └─ NO  → END
```

### 各节点职责

| 节点 | 职责 |
|------|------|
| `pre_evaluate` | 用 DyslexiaEvaluator 算原文基线 `origin_score`，保存状态 |
| `routing` | 根据 `mode` 路由到对应 Agent |
| `refine_agent` | 调用 DeepSeek 做全文改写，读取上一轮 judge 反馈做微调 |
| `summary_agent` | 调用 DeepSeek 做摘要，读取上一轮 judge 反馈做微调 |
| `judge` | 用 DyslexiaEvaluator 评估 `refined_text`，写入 `current_score` |
| `should_continue` | 判断终止条件，决定继续迭代还是结束 |

## 迭代终止条件

```python
def should_continue(state):
    if state["iter_count"] >= state["max_iterations"]:
        return "end"
    
    sc = state["current_score"]
    threshold = state["pass_threshold"] or (0.65 if state["lang"] == "zh" else 0.70)
    
    if sc["total_score"] >= threshold and sc["content"]["dimension_score"] >= 0.70:
        return "end"
    return "continue"
```

- `total_score >= pass_threshold`：总分达标
- `content.dimension_score >= 0.70`：内容保真硬约束，防止为可读性牺牲信息
- `iter_count >= max_iterations`：最大 3 轮兜底

## 两个 Agent 的 Prompt 场景隔离

### FullRefineAgent

```
System: 你是面向阅读障碍用户的文本优化专家。核心原则：
- 100% 保留原文全部信息，不得删减任何事实、数字、人名、术语
- 只调整：句式结构（长句拆分）、排版分段、词汇替换（复杂词→简单词）
- 拆分后每句不超过 {max_sentence_len} 字/词
- 保持原文语种输出

User: 原文：{original_text}
{iteration_hint}
请输出优化后的全文：
```

### SummaryAgent

```
System: 你是面向阅读障碍用户的文本摘要专家。核心原则：
- 精简压缩原文，保留核心关键词和专业术语
- 用简单句式重述，去除次要细节
- {length_hint}
- 保持原文语种输出

User: 原文：{original_text}
{iteration_hint}
请输出摘要：
```

### 迭代微调提示（BaseAgent._build_iteration_hint）

```python
def _build_iteration_hint(self, prev_score, mode):
    hints = []
    content = prev_score["content"]  # content_fidelity
    reading = prev_score["reading"]  # reading_effectiveness
    
    if mode == "full_refine":
        if content["dimension_score"] < 0.70:
            hints.append("上一轮内容保真度不足，请确保不丢失任何原文信息")
        if reading["dimension_score"] < 0.60:
            hints.append("上一轮可读性偏低，请进一步拆分长句、替换复杂词")
    else:  # summary
        if content["keyword_keep"] < 0.70:
            hints.append("上一轮关键词保留不足，请保留更多核心术语")
        if reading["dimension_score"] < 0.65:
            hints.append("上一轮仍偏冗长，请进一步精简")
    
    if hints:
        return "【微调指导】\n" + "\n".join(f"- {h}" for h in hints)
    return ""
```

## BaseAgent 公共层

```python
class BaseAgent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
            timeout=settings.LLM_TIMEOUT,
        )
    
    def _detect_lang(self, text: str) -> str: ...
    
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str: ...
    
    def _build_iteration_hint(self, prev_score: dict, mode: str) -> str: ...
    
    @property
    def max_sentence_len(self): ...
```

## API 接口

```
POST /api/v1/refine

Request:
{
    "original_text": "要处理的原文",
    "mode": "full_refine",       // 必填：full_refine | summary
    "max_iterations": 3,         // 可选，默认 3
    "pass_threshold": null       // 可选，null 时 zh=0.65 en=0.70
}

Response (200):
{
    "mode": "full_refine",
    "lang": "zh",
    "refined_text": "优化后的文本",
    "iterations": 2,
    "origin_score": {
        "total_score": 0.42,
        "reading": {...}, "content": {...}, "layout": {...}, "narrative": {...}
    },
    "final_score": {
        "total_score": 0.78,
        "reading": {...}, "content": {...}, "layout": {...}, "narrative": {...}
    },
    "improvement": {
        "total_score": "+0.36",
        "reading": "+0.15", "content": "-0.02", "layout": "+0.20", "narrative": "+0.18"
    },
    "score_history": [
        {"iteration": 1, "total_score": 0.71, "content_fidelity": 0.68},
        {"iteration": 2, "total_score": 0.78, "content_fidelity": 0.82}
    ]
}
```

## 依赖

requirements.txt 新增：
```
langgraph>=0.2.0
langdetect
rouge-score
bert-score
nltk
numpy
```

## 评估维度（复用 DyslexiaEvaluator，不修改权重）

| 维度 | 权重 | 子指标 |
|------|------|--------|
| reading_effectiveness | 0.25 | FRE 易读度、FKGL 年级难度、平均句长 |
| content_fidelity | 0.25 | BLEU 词汇重合、BERTScore 语义相似、关键词保留率 |
| layout_effectiveness | 0.25 | 段落数量、平均段长、标点规范度 |
| narrative_effectiveness | 0.25 | 正式度、自然流畅度 |

## 删除项

- `app/api/text_simplify.py` — 被 `/refine` 替换
- `app/api/summarize.py` — 被 `/refine` 替换
- `app/services/text_simplify_service.py` — 被 `refine/` 模块替换
- `app/services/text_summarize_service.py` — 被 `refine/` 模块替换
- `app/schemas/text_simplify.py` — 相关 schema 移到新模块或删除
- `main.py` 中 `text_simplify` 和 `summarize` 的路由注册

## 前端影响

前端 `Chenjinshi` 沉浸式阅读器中调用 `/simplify` 和 `/summarize` 的地方，改为调用 `/refine` 并传 `mode` 参数。
