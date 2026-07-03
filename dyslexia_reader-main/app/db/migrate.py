"""
数据库迁移辅助
在应用启动时自动执行，处理 schema 变更
"""

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def run_migrations(engine: Engine) -> None:
    """执行所有待迁移操作"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # 1. 删除废弃的 audio_tracks 表
    if "audio_tracks" in existing_tables:
        try:
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE audio_tracks"))
                conn.commit()
            logger.info("已删除废弃表 audio_tracks")
        except Exception as e:
            logger.warning(f"删除 audio_tracks 失败（可能已不存在）: {e}")

    # 2. 给 documents 表添加 updated_at 列
    if "documents" in existing_tables:
        doc_columns = {col["name"] for col in inspector.get_columns("documents")}
        if "updated_at" not in doc_columns:
            try:
                with engine.connect() as conn:
                    conn.execute(text(
                        "ALTER TABLE documents ADD COLUMN updated_at DATETIME"
                    ))
                    conn.commit()
                logger.info("已为 documents 表添加 updated_at 列")
            except Exception as e:
                logger.warning(f"添加 updated_at 列失败: {e}")
