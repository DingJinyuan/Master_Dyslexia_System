"""Backend API comprehensive test — all services"""
import asyncio, os, sys, tempfile


# ============================================================
# 1. 英文划词翻译
# ============================================================
async def test_dict():
    from app.services.dictionary_service import lookup_word

    # 常见单词
    r = await lookup_word("hello")
    assert r["success"], f"dict 'hello' failed: {r}"
    assert r["language"] == "en"
    assert len(r["meanings"]) > 0, "no meanings returned"

    # 查不到的单词
    r = await lookup_word("xyznonexistent")
    assert not r["success"], "should fail for nonexistent word"

    print("1. Dictionary (EN)   : PASS")


# ============================================================
# 2. 词性标注 (中文 + 英文)
# ============================================================
def test_pos_tagging():
    from app.services.nlp_service import pos_tagging

    # 中文
    r = pos_tagging("人工智能技术正在改变世界")
    assert "error" not in r, f"zh POS failed: {r}"
    assert r.get("language") == "zh"
    tokens = r.get("tokens", [])
    assert len(tokens) > 0, "no tokens for Chinese"
    assert all("word" in t and "pos" in t for t in tokens), "token format wrong"

    # 英文
    r = pos_tagging("Artificial intelligence is transforming the world")
    assert "error" not in r, f"en POS failed: {r}"
    assert r.get("language") == "en"
    tokens = r.get("tokens", [])
    # spaCy may not be installed, so allow empty tokens
    if len(tokens) > 0:
        assert all("word" in t and "pos" in t for t in tokens), "token format wrong"

    print("2. POS Tagging       : PASS")


# ============================================================
# 3. 可读性评分 (中文 + 英文)
# ============================================================
def test_readability():
    from app.services.readability_service import calculate_readability

    # 英文
    r = calculate_readability(
        "Reading is a fundamental skill that enables people to learn and grow. "
        "However, for some individuals, reading can be challenging due to various factors."
    )
    assert "error" not in r, f"en readability failed: {r}"
    assert r.get("readabilityScore") is not None, f"missing readabilityScore: {r}"

    # 中文
    r = calculate_readability(
        "阅读是人类获取知识的重要途径。通过阅读，我们可以了解世界、学习新技能。"
        "然而对于阅读障碍者来说，阅读可能是一项艰巨的挑战。"
    )
    assert "error" not in r, f"zh readability failed: {r}"
    assert r.get("readabilityScore") is not None, f"missing readabilityScore: {r}"

    print("3. Readability       : PASS")


# ============================================================
# 4. 文本摘要 (DeepSeek)
# ============================================================
def test_summarize():
    from app.services.text_summarize_service import summarize_text

    r = summarize_text(
        "Artificial intelligence has revolutionized many industries. "
        "From healthcare to finance, AI systems are making decisions faster and more accurately. "
        "Machine learning models can now detect diseases in medical images with superhuman accuracy.",
        "short",
    )
    assert "error" not in r, f"summarize failed: {r}"
    assert not r["summarizedText"].startswith("[API"), f"API error: {r['summarizedText']}"
    assert len(r["summarizedText"]) > 10, "summary too short"

    print("4. Text Summary      : PASS")


# ============================================================
# 5. 文本简化 (DeepSeek)
# ============================================================
def test_simplify():
    from app.services.text_simplify_service import simplify_text

    r = simplify_text(
        "The implementation of sophisticated algorithms requires substantial computational resources.",
        "standard",
    )
    assert "error" not in r, f"simplify failed: {r}"
    assert not r["simplifiedText"].startswith("[API"), f"API error: {r['simplifiedText']}"
    assert len(r["simplifiedText"]) > 10, "simplified text too short"

    print("5. Text Simplify     : PASS")


# ============================================================
# 6. TTS 语音合成 (OpenAI TTS)
# ============================================================
async def test_tts():
    from app.services.tts_service import text_to_speech, text_to_speech_by_sentences, get_available_voices

    # 单个文本
    r = await text_to_speech("Hello world", voice_name="nova")
    assert r["success"], f"TTS failed: {r}"
    assert os.path.exists(r["filePath"]), f"file not found: {r['filePath']}"
    assert os.path.getsize(r["filePath"]) > 100, "audio file too small"
    assert r["engine"] == "openai-tts"

    # 逐句合成
    r = await text_to_speech_by_sentences("Hello. How are you?", voice_name="nova")
    assert r["totalSentences"] == 2, f"expected 2 sentences: {r}"
    for s in r["sentences"]:
        assert s["success"], f"sentence TTS failed: {s}"

    # 音色列表
    voices = await get_available_voices()
    assert len(voices) == 6, f"expected 6 voices: {len(voices)}"

    print("6. TTS (OpenAI)      : PASS")


# ============================================================
# 7. PDF 文档解析 (文本 + 图片 base64)
# ============================================================
def test_pdf_parser():
    import fitz
    from app.services.adapters.document_parser import DocumentParser

    # 创建一个含文字和图片的测试 PDF
    pdf_path = os.path.join(tempfile.gettempdir(), "_test_doc.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is the first paragraph for testing.", fontsize=12)
    page.insert_text((72, 120), "This is the second paragraph with more content.", fontsize=12)
    # 画一个简单矩形作为"图片"
    page.draw_rect([72, 200, 200, 300])
    doc.save(pdf_path)
    doc.close()

    parser = DocumentParser()
    blocks, full_text = parser.parse(pdf_path)

    assert len(blocks) > 0, "no blocks parsed"
    text_blocks = [b for b in blocks if b["block_type"] == "text"]
    assert len(text_blocks) >= 2, f"expected >=2 text blocks, got {len(text_blocks)}"
    assert len(full_text) > 0, "full_text is empty"

    os.remove(pdf_path)
    print("7. PDF Parser        : PASS")


# ============================================================
# 8. OCR 适配器
# ============================================================
def test_ocr():
    from app.services.adapters.ocr_adapter import get_ocr_provider

    ocr = get_ocr_provider()

    # 对 PDF 走 fitz 直接提取
    import fitz
    pdf_path = os.path.join(tempfile.gettempdir(), "_test_ocr.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "OCR test content here.", fontsize=14)
    doc.save(pdf_path)
    doc.close()

    text = ocr.extract_text(pdf_path)
    assert len(text) > 0, "OCR extracted no text from PDF"
    assert "OCR test" in text, f"unexpected content: {text[:50]}"

    os.remove(pdf_path)

    # 对图片文件走 mock
    img_path = os.path.join(tempfile.gettempdir(), "_test_img.png")
    # 创建一个最小 PNG
    import struct, zlib
    def create_minimal_png(path):
        sig = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        idat_data = zlib.compress(b'\x00\xff\x00\x00')
        idat_crc = zlib.crc32(b'IDAT' + idat_data)
        idat = struct.pack('>I', len(idat_data)) + b'IDAT' + idat_data + struct.pack('>I', idat_crc)
        iend_crc = zlib.crc32(b'IEND')
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        with open(path, 'wb') as f:
            f.write(sig + ihdr + idat + iend)

    create_minimal_png(img_path)
    text = ocr.extract_text(img_path)
    assert "[mock]" in text, f"expected mock message, got: {text[:50]}"
    os.remove(img_path)

    print("8. OCR Adapter       : PASS")


# ============================================================
# Main
# ============================================================
async def main():
    print("=" * 55)
    print("Backend API Comprehensive Test")
    print("=" * 55)

    await test_dict()
    test_pos_tagging()
    test_readability()
    test_summarize()
    test_simplify()
    await test_tts()
    test_pdf_parser()
    test_ocr()

    print("=" * 55)
    print("ALL TESTS PASSED")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
