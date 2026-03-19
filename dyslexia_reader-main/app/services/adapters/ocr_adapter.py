from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import fitz
import httpx

from app.core.config import settings


class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError


class MockOCRProvider(OCRProvider):
    def extract_text(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            text_parts = []
            with fitz.open(file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text("text"))
            return "\n".join(text_parts).strip() or "[mock] pdf 已上传，但未提取到可复制文本。"
        return "[mock] 图片已上传，请接入真实 OCR 服务提取文字。"


class HTTPOCRProvider(OCRProvider):
    def extract_text(self, file_path: str) -> str:
        with open(file_path, "rb") as f, httpx.Client(timeout=60) as client:
            response = client.post(
                settings.ocr_api_url,
                headers={"Authorization": f"Bearer {settings.ocr_api_key}"},
                files={"file": f},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("text", "")



def get_ocr_provider() -> OCRProvider:
    if settings.ocr_provider == "http":
        return HTTPOCRProvider()
    return MockOCRProvider()
