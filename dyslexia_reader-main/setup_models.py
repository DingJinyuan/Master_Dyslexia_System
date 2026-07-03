"""一次性下载所有运行时需要的模型/数据（约 1.5GB），每个步骤独立容错"""
import os
import subprocess
import sys

PASS = 0
FAIL = 0


def run_step(desc, cmd):
    global PASS, FAIL
    print(f"[ ] {desc} ...")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode == 0:
        print(f"  OK")
        PASS += 1
        return True
    else:
        print(f"  FAIL (exit={result.returncode})，已跳过，不影响后续步骤")
        FAIL += 1
        return False


def main():
    print("=" * 55)
    print("模型/数据下载 — 每个步骤独立运行，失败不影响后续")
    print("=" * 55)
    print()

    # 国内镜像加速
    if "HF_ENDPOINT" not in os.environ:
        print("[提示] 国内网络先设 HuggingFace 镜像可加速 bert-score 下载：")
        print("       $env:HF_ENDPOINT = 'https://hf-mirror.com'")
        print()

    # ---- 步骤 1: spaCy ----
    # 国内网络可能连不上 GitHub，用 pip 安装 wheel 作为备选
    run_step(
        "spaCy 英文模型 en_core_web_sm（~12MB，英文词性标注）",
        ["python", "-m", "spacy", "download", "en_core_web_sm"],
    )

    # ---- 步骤 2: NLTK ----
    run_step(
        "NLTK 数据 punkt_tab + cmudict（~几MB）",
        [
            "python", "-c",
            "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('cmudict', quiet=True); print('done')"
        ],
    )

    # ---- 步骤 3: bert-score ----
    run_step(
        "bert-score RoBERTa 模型（~1.42GB，首次调用时自动下载亦可）",
        [
            "python", "-c",
            "from bert_score import score; score(['hello'], ['hello'], lang='en', verbose=True); print('done')"
        ],
    )

    # ---- 总结 ----
    print()
    print("=" * 55)
    print(f"完成: {PASS} 成功 / {FAIL} 失败 / {PASS + FAIL} 总计")
    if FAIL > 0:
        print()
        print("失败项可手动重试，或等首次调用对应功能时自动下载。")
        print("spaCy 模型也可用 pip 安装（如果 GitHub 不通）：")
        print("  pip install en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl")
    else:
        print("可以启动后端了：uvicorn app.main:app --reload")
    print("=" * 55)


if __name__ == "__main__":
    main()
