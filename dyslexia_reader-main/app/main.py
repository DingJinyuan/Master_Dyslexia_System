import os
import logging
import sys  # 新增：导入 sys 模块
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import admin, audio, auth, documents, nlp, tts, readability,summarize, text_simplify
from app.core.config import settings
from app.db.session import Base, engine
from app.models import ApprovalRequest, AudioTrack, Document, User

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 日志
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 静态目录挂载 ----------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

storage_dir = os.path.join(project_root, "storage")
static_dir = os.path.join(project_root, "static")
tts_dir = settings.TTS_OUTPUT_DIR

if not os.path.isabs(tts_dir):
    tts_dir = os.path.join(project_root, tts_dir)

if os.path.exists(tts_dir):
    # /static/tts 对应 tts_service 里返回的 audioUrl 前缀
    app.mount("/static/tts", StaticFiles(directory=tts_dir), name="tts-static")
else:
    print(f" 警告：TTS 输出目录 {tts_dir} 不存在！")

if os.path.exists(storage_dir):
    app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")
else:
    logger.warning(f"Storage 目录 {storage_dir} 不存在")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ---------- 路由注册 ----------
app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(audio.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(nlp.router, prefix="/api/v1")   # NLP 相关接口

app.include_router(tts.router, prefix="/api/v1")
app.include_router(text_simplify.router, prefix="/api/v1", tags=["simplify"])
app.include_router(readability.router, prefix="/api/v1", tags=["readability"])

app.include_router(summarize.router, prefix="/api/v1", tags=["总结功能"])
# ---------- 健康检查 ----------
@app.get("/", tags=["健康检查"])
async def root():
    return {"message": "Dyslexia Reader Backend is running"}


