"""
后端 API 全量测试脚本
覆盖 19 个接口，测试前需先启动服务器: uvicorn app.main:app --host 127.0.0.1 --port 8000
"""
import requests
import json
import sys
import os

BASE = "http://127.0.0.1:8000"
API = f"{BASE}/api/v1"

PASS = 0
FAIL = 0
ERRORS = []


def test(name, method, url, expected_status=None, data=None, files=None, headers=None, auth_token=None, form_data=None):
    global PASS, FAIL
    if url.startswith("http"):
        full_url = url
    elif url.startswith("/api"):
        full_url = f"{BASE}{url}"
    else:
        full_url = f"{API}{url}"

    req_headers = headers or {}
    if auth_token:
        req_headers["Authorization"] = f"Bearer {auth_token}"

    try:
        if method == "GET":
            resp = requests.get(full_url, headers=req_headers, timeout=30)
        elif method == "POST":
            if form_data:
                resp = requests.post(full_url, data=form_data, headers=req_headers, timeout=30)
            elif files:
                resp = requests.post(full_url, files=files, data=data or {}, headers=req_headers, timeout=30)
            else:
                resp = requests.post(full_url, json=data or {}, headers=req_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        status = resp.status_code
        body = resp.text[:300]

        if expected_status:
            ok = status in expected_status if isinstance(expected_status, (list, tuple)) else status == expected_status
        else:
            ok = 200 <= status < 300

        if ok:
            PASS += 1
            print(f"  [PASS] {name} -> {status}")
        else:
            FAIL += 1
            msg = f"  [FAIL] {name} -> expected {expected_status}, got {status}: {body}"
            print(msg)
            ERRORS.append(msg)
        return resp
    except Exception as e:
        FAIL += 1
        msg = f"  [FAIL] {name} -> exception: {e}"
        print(msg)
        ERRORS.append(msg)
        return None


def run_all_tests():
    global PASS, FAIL, ERRORS
    PASS = FAIL = 0
    ERRORS = []

    token_user = None
    token_admin = None
    doc_id = None

    # ========== 1. 健康检查 ==========
    print("\n" + "="*60)
    print("模块: Root / 健康检查")
    print("="*60)
    test("GET /", "GET", f"{BASE}/", expected_status=200)

    # ========== 2. Admin: 初始化管理员 ==========
    print("\n" + "="*60)
    print("模块: Admin")
    print("="*60)
    test("POST /admin/seed-admin", "POST", "/admin/seed-admin", expected_status=200)

    # ========== 3. Auth: 注册用户 ==========
    print("\n" + "="*60)
    print("模块: Auth")
    print("="*60)
    test("POST /auth/register (user)", "POST", "/auth/register",
         expected_status=200,
         data={"email": "testuser@test.com", "username": "testuser",
               "password": "Test@123456", "role": "user"})

    test("POST /auth/register (admin)", "POST", "/auth/register",
         expected_status=200,
         data={"email": "testadmin@test.com", "username": "testadmin",
               "password": "Test@123456", "role": "admin"})

    test("POST /auth/register (duplicate)", "POST", "/auth/register",
         expected_status=400,
         data={"email": "testuser@test.com", "username": "testuser2",
               "password": "Test@123456", "role": "user"})

    # 注册但未审批的用户尝试登录 → 403
    test("POST /auth/login (未审批)", "POST", "/auth/login",
         expected_status=403,
         form_data={"username": "testuser", "password": "Test@123456"})

    # ========== 4. Admin: 登录 + 审批 ==========
    print("\n" + "="*60)
    print("模块: Admin 审批流程")
    print("="*60)
    # 管理员登录
    resp = test("POST /auth/login (admin)", "POST", "/auth/login",
                expected_status=200,
                form_data={"username": "admin", "password": "Admin@123456"})
    if resp:
        token_admin = resp.json().get("access_token")

    # 获取审批列表
    resp = test("GET /admin/approval-requests", "GET", "/admin/approval-requests",
                expected_status=200, auth_token=token_admin)
    requests_list = resp.json() if resp else []

    # 审批通过用户
    user_req = next((r for r in requests_list if r.get("request_type") == "register" and "testuser" in str(r.get("payload_json", ""))), None)
    if user_req:
        req_id = user_req["id"]
        test(f"POST /admin/approval-requests/{req_id}/approve", "POST",
             f"/admin/approval-requests/{req_id}/approve",
             expected_status=200, auth_token=token_admin)
    else:
        print("  [WARN] 未找到 testuser 的审批请求，跳过审批")

    # 审批通过 admin
    admin_req = next((r for r in requests_list if r.get("request_type") == "register" and "testadmin" in str(r.get("payload_json", ""))), None)
    if admin_req:
        req_id = admin_req["id"]
        test(f"POST /admin/approval-requests/{req_id}/approve", "POST",
             f"/admin/approval-requests/{req_id}/approve",
             expected_status=200, auth_token=token_admin)
    else:
        print("  [WARN] 未找到 testadmin 的审批请求，跳过审批")

    # 已审批用户登录
    resp = test("POST /auth/login (已审批 user)", "POST", "/auth/login",
                expected_status=200,
                form_data={"username": "testuser", "password": "Test@123456"})
    if resp:
        token_user = resp.json().get("access_token")

    resp = test("POST /auth/login (已审批 admin)", "POST", "/auth/login",
                expected_status=200,
                form_data={"username": "testadmin", "password": "Test@123456"})
    if resp:
        token_admin = resp.json().get("access_token")

    # 错误登录
    test("POST /auth/login (错误密码)", "POST", "/auth/login",
         expected_status=401,
         form_data={"username": "testuser", "password": "WrongPassword123"})

    # ========== 5. Auth: 修改密码 ==========
    print("\n" + "="*60)
    print("模块: Auth / 密码修改")
    print("="*60)
    test("POST /auth/password-change-request", "POST", "/auth/password-change-request",
         expected_status=200, auth_token=token_user,
         data={"old_password": "Test@123456", "new_password": "NewPass@123456"})

    test("POST /auth/password-change-request (无 token)", "POST", "/auth/password-change-request",
         expected_status=401,
         data={"old_password": "Test@123456", "new_password": "NewPass@123456"})

    # ========== 6. Documents: 上传 ==========
    print("\n" + "="*60)
    print("模块: Documents")
    print("="*60)
    # 创建临时测试 PDF
    pdf_path = os.path.join(os.path.dirname(__file__), "_test_upload.pdf")
    if not os.path.exists(pdf_path):
        # 创建一个最小的 PDF 用于测试
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
                    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
                    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
                    b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
                    b"0000000058 00000 n \n0000000115 00000 n \n"
                    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF")

    with open(pdf_path, "rb") as f:
        resp = test("POST /documents/upload", "POST", "/documents/upload",
                    expected_status=200, auth_token=token_user,
                    files={"file": ("test.pdf", f, "application/pdf")})
    if resp:
        doc_id = resp.json().get("id")

    # 不需要的文件清理
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    # ========== 7. Documents: 列表 / 详情 / 结构化 / 段落 ==========
    print("\n" + "="*60)
    print("模块: Documents 查询")
    print("="*60)
    test("GET /documents", "GET", "/documents", expected_status=200, auth_token=token_user)

    if doc_id:
        test(f"GET /documents/{doc_id}", "GET", f"/documents/{doc_id}",
             expected_status=200, auth_token=token_user)
        test(f"GET /documents/{doc_id}/structured", "GET", f"/documents/{doc_id}/structured",
             expected_status=200, auth_token=token_user)
        test(f"GET /documents/{doc_id}/paragraphs", "GET", f"/documents/{doc_id}/paragraphs",
             expected_status=200, auth_token=token_user)
    else:
        print("  [WARN] no document_id, skip document query tests")

    # 权限测试：访问不存在的文档
    test("GET /documents/99999 (不存在)", "GET", "/documents/99999",
         expected_status=404, auth_token=token_user)

    # ========== 8. NLP ==========
    print("\n" + "="*60)
    print("模块: NLP (词性标注 / 划词翻译)")
    print("="*60)
    test("POST /nlp/pos-tagging (中文)", "POST", "/nlp/pos-tagging",
         expected_status=200,
         data={"text": "今天天气真好，我们去公园散步吧。"})

    test("POST /nlp/pos-tagging (英文)", "POST", "/nlp/pos-tagging",
         expected_status=200,
         data={"text": "The quick brown fox jumps over the lazy dog."})

    test("POST /nlp/pos-tagging (空文本)", "POST", "/nlp/pos-tagging",
         expected_status=422,
         data={"text": ""})

    test("POST /nlp/word-lookup", "POST", "/nlp/word-lookup",
         expected_status=200,
         data={"word": "hello", "sourceLang": "en"})

    test("POST /nlp/word-lookup (中文)", "POST", "/nlp/word-lookup",
         expected_status=200,
         data={"word": "你好", "sourceLang": "zh"})

    # ========== 9. TTS ==========
    print("\n" + "="*60)
    print("模块: TTS")
    print("="*60)
    test("GET /tts/voices", "GET", "/tts/voices", expected_status=200)

    # TTS 生成（可能因无 API key 而返回 500，但接口本身应该可访问）
    resp = test("POST /tts (全文)", "POST", "/tts",
                expected_status=[200, 500],
                data={"text": "你好世界，这是一段测试文本。", "rate": "+0%"})

    resp = test("POST /tts/sentences (逐句)", "POST", "/tts/sentences",
                expected_status=200,
                data={"text": "第一句话。第二句话。第三句话。", "rate": "+0%"})

    # ========== 10. Readability ==========
    print("\n" + "="*60)
    print("模块: Readability (可读性评分)")
    print("="*60)
    test("POST /readability (中文)", "POST", "/readability",
         expected_status=200,
         form_data={"text": "这是一段测试文本，用来检测中文可读性评分是否正常工作。"})

    test("POST /readability (英文)", "POST", "/readability",
         expected_status=200,
         form_data={"text": "This is a sample text for testing English readability scoring functionality."})

    # ========== 11. Refine ==========
    print("\n" + "="*60)
    print("模块: Refine (多Agent文本精炼)")
    print("="*60)
    test("POST /refine (full_refine)", "POST", "/refine",
         expected_status=200,
         data={"original_text": "人工智能正在改变我们的生活。智能手机和自动驾驶汽车都使用了人工智能技术。",
               "mode": "full_refine", "max_iterations": 1})

    test("POST /refine (summary)", "POST", "/refine",
         expected_status=200,
         data={"original_text": "人工智能技术正在深刻地改变着我们的生活方式。从智能手机到自动驾驶汽车，人工智能的应用越来越广泛。",
               "mode": "summary", "summary_length": "简短", "max_iterations": 1})

    test("POST /refine (invalid mode)", "POST", "/refine",
         expected_status=422,
         data={"original_text": "test", "mode": "invalid", "max_iterations": 1})

    # ========== 13. Admin: reject (需要新的待审批) ==========
    print("\n" + "="*60)
    print("模块: Admin / Reject")
    print("="*60)
    # 注册一个用来被 reject 的用户
    test("POST /auth/register (to_reject)", "POST", "/auth/register",
         expected_status=200,
         data={"email": "reject@test.com", "username": "rejectuser",
               "password": "Test@123456", "role": "user"})

    resp = test("GET /admin/approval-requests", "GET", "/admin/approval-requests",
                expected_status=200, auth_token=token_admin)
    if resp:
        reject_req = next((r for r in resp.json() if "rejectuser" in str(r.get("payload_json", "")) and r.get("status") == "pending"), None)
        if reject_req:
            rid = reject_req["id"]
            test(f"POST /admin/approval-requests/{rid}/reject", "POST",
                 f"/admin/approval-requests/{rid}/reject",
                 expected_status=200, auth_token=token_admin)
        else:
            print("  [WARN] rejectuser approval request not found")

    # 已审批的再次 approve → 404
    test("POST /admin/approval-requests/99999/approve", "POST",
         "/admin/approval-requests/99999/approve",
         expected_status=404, auth_token=token_admin)

    # ========== 14. 权限测试 ==========
    print("\n" + "="*60)
    print("模块: 权限校验")
    print("="*60)
    test("GET /documents (无 token)", "GET", "/documents", expected_status=401)
    test("GET /admin/approval-requests (非 admin)", "GET", "/admin/approval-requests",
         expected_status=403, auth_token=token_user)

    # ========== 15. Mindmap (思维导图生成) ==========
    print("\n" + "="*60)
    print("模块: Mindmap / 思维导图生成")
    print("="*60)

    test("POST /mindmap/generate (空文本)", "POST", "/mindmap/generate",
         expected_status=422,
         data={"text": "", "max_depth": 3})

    resp = test("POST /mindmap/generate (中文)", "POST", "/mindmap/generate",
                expected_status=[200, 500],  # 500 allowed if MCP/LLM unavailable
                data={"text": "人工智能发展史：第一次浪潮是符号主义。第二次浪潮是专家系统。第三次浪潮是深度学习。目前大语言模型成为主流。", "max_depth": 3})
    if resp is not None and resp.status_code == 200:
        body = resp.json()
        if body.get("success") and body.get("html_url", "").startswith("/storage/mindmap/"):
            # Verify file is accessible (HTTP URL, not relative)
            html_url = body["html_url"]
            if not html_url.startswith("http"):
                html_url = f"{BASE}{html_url}"
            test("GET 导图 HTML 文件", "GET", html_url, expected_status=200)

    resp = test("POST /mindmap/generate (英文)", "POST", "/mindmap/generate",
                expected_status=[200, 500],
                data={"text": "Artificial Intelligence has revolutionized many fields. Machine Learning enables pattern recognition. Deep Learning uses neural networks.", "max_depth": 3})

    # ========== 结果汇总 ==========
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    total = PASS + FAIL
    print(f"  Passed: {PASS}/{total}")
    print(f"  Failed: {FAIL}/{total}")
    if ERRORS:
        print("\nError details:")
        for e in ERRORS:
            print(f"  - {e}")
    print()
    return FAIL == 0


if __name__ == "__main__":
    # 启动前检查服务器
    try:
        r = requests.get(f"{BASE}/", timeout=5)
    except requests.ConnectionError:
        print("[ERROR] Server not running! Please start: uvicorn app.main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)

    print("="*60)
    print("Dyslexia Reader 后端 API 全量测试")
    print(f"目标: {BASE}")
    print("="*60)

    success = run_all_tests()
    sys.exit(0 if success else 1)
