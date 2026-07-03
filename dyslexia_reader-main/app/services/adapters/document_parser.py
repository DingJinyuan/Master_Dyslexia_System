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
        global_order = 1

        with fitz.open(file_path) as doc:
            for page_index, page in enumerate(doc, start=1):
                page_blocks: list[dict] = []

                # 1. 尝试提取文本块，优先用 text 模式（对中文编码兼容性更好）
                text_blocks = self._extract_page_text(page)
                for tb in text_blocks:
                    page_blocks.append({
                        "page": page_index,
                        "block_type": "text",
                        "text_content": tb["text"],
                        "image_url": None,
                        "image_caption": None,
                        "bbox": tb["bbox"],
                    })

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

                    page_blocks.append({
                        "page": page_index,
                        "block_type": "image",
                        "text_content": None,
                        "image_url": image_url,
                        "image_caption": None,
                        "bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
                    })

                # 3. 按页面坐标排序（y 优先，x 次之）
                page_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))

                for item in page_blocks:
                    item["block_order"] = global_order
                    item["bbox_json"] = json.dumps(item["bbox"], ensure_ascii=False)
                    item.pop("bbox", None)
                    blocks.append(item)
                    global_order += 1

            full_text = "\n\n".join(
                b["text_content"] for b in blocks if b["block_type"] == "text"
            ).strip()

        return blocks, full_text

    # OCR 实例（延迟加载）
    _ocr_reader = None

    @classmethod
    def _get_ocr(cls):
        if cls._ocr_reader is None:
            import easyocr
            cls._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
        return cls._ocr_reader

    @staticmethod
    def _extract_page_text(page) -> list[dict]:
        """提取页面文本块。
        策略：PyMuPDF 提取 → 中文校验丢乱码 → 英文直接返回 → 中文无有效时 OCR"""
        import re

        def _filter_garbled(results_list):
            """过滤 CID 乱码块（有 CJK 但校验不通过），保留英文和非中文块"""
            if not results_list:
                return results_list
            kept = []
            for r in results_list:
                text = r.get("text", "")
                if DocumentParser._has_cjk(text) and not DocumentParser._is_valid_chinese_text(text):
                    continue  # CJK 乱码块，丢弃
                kept.append(r)
            return kept

        def _has_any_cjk(results_list):
            if not results_list:
                return False
            return DocumentParser._has_cjk("".join(r["text"] for r in results_list))

        results = []

        # 方法 1：优先用 "text" 模式
        plain = page.get_text("text", sort=True)
        if plain and DocumentParser._has_cjk(plain):
            if DocumentParser._is_valid_chinese_text(plain):
                paras = [p.strip() for p in plain.split("\n\n") if p.strip()]
                page_w = page.rect.width
                page_h = page.rect.height
                results = []
                y = 50.0
                for para in paras:
                    h = max(14, page_h / max(len(paras), 1) - 4)
                    results.append({"text": DocumentParser._normalize_text(para), "bbox": [50.0, y, page_w - 50, y + h]})
                    y += h + 4
                if results:
                    filtered = _filter_garbled(results)
                    if filtered:
                        return filtered
            # CJK 校验失败 → 继续降级

        # 方法 2：回退到 "blocks" 模式
        blocks = page.get_text("blocks", sort=True)
        if blocks:
            results = []
            for item in blocks:
                if len(item) < 7:
                    continue
                x0, y0, x1, y1, text, _, block_type = item
                if block_type != 0:
                    continue
                text = DocumentParser._normalize_text((text or "").strip())
                if text:
                    results.append({"text": text, "bbox": [x0, y0, x1, y1]})
            if results:
                if _has_any_cjk(results):
                    # 中文：过滤乱码后返回；如果全被过滤，尝试 rawdict
                    filtered = _filter_garbled(results)
                    if filtered:
                        return filtered
                    raw_results = DocumentParser._extract_via_rawdict(page)
                    if raw_results:
                        filtered2 = _filter_garbled(raw_results)
                        if filtered2:
                            return filtered2
                else:
                    # 英文/非中文：直接返回，无需校验
                    return results

        # 方法 3：rawdict
        raw_results = DocumentParser._extract_via_rawdict(page)
        if raw_results:
            combined = "".join(r["text"] for r in raw_results)
            if DocumentParser._has_cjk(combined):
                filtered = _filter_garbled(raw_results)
                if filtered:
                    return filtered
            else:
                # 非中文 rawdict 直接返回
                return raw_results

        # 方法 4：OCR 兜底（仅中文需要）
        if not results:
            ocr_results = DocumentParser._extract_via_ocr(page)
            if ocr_results:
                return ocr_results
        return results if results else []

    @staticmethod
    def _extract_via_ocr(page) -> list[dict]:
        """OCR 兜底：将 PDF 页面渲染为图片后用 easyocr 识别"""
        try:
            import numpy as np
            pix = page.get_pixmap(dpi=200)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img = img[:, :, :3]  # RGBA → RGB

            reader = DocumentParser._get_ocr()
            ocr_results = reader.readtext(img, detail=1)

            if not ocr_results:
                return []

            page_w = page.rect.width
            page_h = page.rect.height
            scale_x = page_w / pix.width
            scale_y = page_h / pix.height

            results = []
            for bbox, text, conf in ocr_results:
                if not text or not text.strip():
                    continue
                # OCR 坐标转换为 PDF 页面坐标
                x0 = bbox[0][0] * scale_x
                y0 = bbox[0][1] * scale_y
                x1 = bbox[2][0] * scale_x
                y1 = bbox[2][1] * scale_y
                results.append({
                    "text": DocumentParser._normalize_text(text.strip()),
                    "bbox": [x0, y0, x1, y1],
                })
            return results
        except Exception:
            return []

    @staticmethod
    def _extract_via_rawdict(page) -> list[dict]:
        """通过 rawdict 提取文本，手动处理编码"""
        try:
            rd = page.get_text("rawdict")
            results = []
            for block in rd.get("blocks", []):
                if block.get("type") != 0:
                    continue
                block_text_parts = []
                bbox = list(block.get("bbox", [0, 0, 100, 14]))
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        t = span.get("text", "")
                        if t:
                            line_text += t
                    if line_text.strip():
                        block_text_parts.append(line_text.strip())
                if block_text_parts:
                    text = " ".join(block_text_parts)
                    text = DocumentParser._normalize_text(text)
                    if text:
                        results.append({"text": text, "bbox": bbox})
            return results
        except Exception:
            return []

    @staticmethod
    def _has_cjk(text: str) -> bool:
        """检查文本是否包含中文/日文/韩文字符"""
        import re
        if not text:
            return False
        cjk = len(re.findall(r'[一-鿿㐀-䶿豈-﫿]', text))
        total = len(text.replace(" ", "").replace("\n", ""))
        return cjk > 0 and (cjk / max(total, 1)) > 0.05 if total > 0 else False

    @classmethod
    def _is_valid_chinese_text(cls, text: str) -> bool:
        """校验 CJK 文本是否为有效中文（非 CID 乱码）。非中文文本默认返回 True。"""
        import re
        if not text or not cls._has_cjk(text):
            return True  # 非中文不校验
        # 中文标点检测
        if re.search(r'[。，、！？；：""''「」『』【】《》—…]', text):
            return True
        # 常见中文功能词（至少出现 2 个不同的）
        common = r'(?:的|了|是|在|不|我|他|她|这|那|就|也|都|要|会|能|对|和|与|但|而|因|为|所|以|可以|我们|他们|这个|那个|什么|怎么|一个|没有|已经|还是|因为|所以|但是|如果|虽然|然后|不过|只是|一定|可能|应该|需要|进行|通过|使用|根据|关于|对于|以及|或者|并且|而且|因此|然而|此外|例如|其中|其他|所有|每个|整个|全部|部分|基本|主要|特别|非常|比较|更加|最|很|都|也|还|就|才|只|已经|正在|将要|会|能|要|应该|必须|可以|愿意|想|喜欢|知道|觉得|认为|发现|表示|指出|强调|提出|建议|要求|决定|同意|支持|反对|参加|参与|影响|作用|关系|问题|情况|方面|原因|结果|过程|方法|方式|条件|基础|标准|目标|任务|内容|形式|结构|功能|特点|意义|价值|地位|变化|发展|增长|减少|增加|提高|降低|改善|改进|完成|实现|达到|取得|获得|产生|形成|建立|建设|组织|管理|经营|生产|销售|服务|提供|保障|保护|维护|支持|促进|推动|加强|深化|扩大|开展|实施|执行|落实|贯彻|坚持|继续|保持|维持|发挥|利用|运用|采取|采用|选择|确定|制定|规定|限制|控制|调整|改革|创新|开发|研究|分析|评估|检查|监督|指导|领导|负责|承担)'
        matches = set(re.findall(common, text))
        return len(matches) >= 2

    @staticmethod
    def _normalize_text(text: str) -> str:
        """规范化文本：过滤不可见控制字符，修复 PDF 中文字间多余空格"""
        import re
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'(?<=[一-鿿㐀-䶿豈-﫿])\s+(?=[一-鿿㐀-䶿豈-﫿])', '', text)
        return text.strip()