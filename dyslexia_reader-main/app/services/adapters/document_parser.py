from __future__ import annotations

import json
from pathlib import Path

import fitz

from app.services.storage_service import LocalStorageService


class DocumentParser:
    def __init__(self):
        self.storage = LocalStorageService()

    def parse(self, file_path: str) -> tuple[list[dict], str]:
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(file_path)

        # 非 PDF 暂时兼容旧逻辑：
        # 只返回一个 text block 或后续接真实 OCR / layout
        return [], ""

    def _parse_pdf(self, file_path: str) -> tuple[list[dict], str]:
        blocks: list[dict] = []
        all_text_parts: list[str] = []
        global_order = 1

        with fitz.open(file_path) as doc:
            for page_index, page in enumerate(doc, start=1):
                page_blocks: list[dict] = []

                # 1. text blocks
                # block tuple: (x0, y0, x1, y1, text, block_no, block_type)
                for item in page.get_text("blocks"):
                    if len(item) < 7:
                        continue

                    x0, y0, x1, y1, text, _, block_type = item

                    # 只收文本 block
                    if block_type != 0:
                        continue

                    text = (text or "").strip()
                    if not text:
                        continue

                    page_blocks.append(
                        {
                            "page": page_index,
                            "block_type": "text",
                            "text_content": text,
                            "image_url": None,
                            "image_caption": None,
                            "bbox": [x0, y0, x1, y1],
                        }
                    )
                    all_text_parts.append(text)

                # 2. image blocks
                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    rects = page.get_image_rects(xref)
                    if not rects:
                        continue

                    rect = rects[0]

                    image_data = doc.extract_image(xref)
                    image_bytes = image_data["image"]
                    image_ext = image_data.get("ext", "png")

                    image_filename = (
                        f"{Path(file_path).stem}_page_{page_index}_img_{xref}.{image_ext}"
                    )
                    image_url = self.storage.save_bytes(image_bytes, image_filename)

                    page_blocks.append(
                        {
                            "page": page_index,
                            "block_type": "image",
                            "text_content": None,
                            "image_url": image_url,
                            "image_caption": None,
                            "bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
                        }
                    )

                # 3. 按页面坐标排序，尽量接近阅读顺序
                page_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))

                for item in page_blocks:
                    item["block_order"] = global_order
                    item["bbox_json"] = json.dumps(item["bbox"], ensure_ascii=False)
                    item.pop("bbox", None)
                    blocks.append(item)
                    global_order += 1

        full_text = "\n\n".join(all_text_parts).strip()
        return blocks, full_text