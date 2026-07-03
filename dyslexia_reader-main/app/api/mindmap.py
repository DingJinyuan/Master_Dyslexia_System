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
