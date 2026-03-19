# app/services/tts_service.py

"""
文字转语音服务
引擎优先级: edge-tts → 有道智云TTS(官方API) → gTTS → pyttsx3(离线)
"""

import os
import uuid
import hashlib
import time
import logging
import re
from typing import List
import httpx

from app.core.config import settings  # 使用项目根目录下的 config.py

logger = logging.getLogger(__name__)

# ==================== 检测可用引擎 ====================

try:
    import edge_tts
    logger.info("edge-tts 已加载")
except ImportError:
    edge_tts = None
    logger.warning("edge-tts 未安装")

try:
    from gtts import gTTS
    logger.info("gTTS 已加载")
except ImportError:
    gTTS = None
    logger.warning("gTTS 未安装")

try:
    import pyttsx3 as _pyttsx3_module
    logger.info("pyttsx3 已加载")
except ImportError:
    _pyttsx3_module = None
    logger.warning("pyttsx3 未安装")


def detect_language(text: str) -> str:
    """简单判定中文/英文"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return "en"
    return "zh" if chinese_chars / total_chars > 0.3 else "en"


def _parse_rate(rate: str) -> tuple:
    """解析 rate 如 '+20%' '-30%' → (数值, 是否慢速)"""
    try:
        val = int(rate.replace('%', '').replace('+', ''))
    except (ValueError, AttributeError):
        val = 0
    slow = val < -10
    return val, slow


def _rate_to_youdao_speed(rate: str) -> str:
    """
    将 rate 字符串转为有道 speed 参数
    有道范围: 0.5 ~ 2.0，正常为 1
    我们的 rate: -50% ~ +100%
    """
    val, _ = _parse_rate(rate)
    # -50% → 0.5, 0% → 1.0, +100% → 2.0
    speed = 1.0 + val / 100.0
    speed = max(0.5, min(2.0, speed))
    return str(round(speed, 1))


# ==================== 有道官方 TTS 签名工具 ====================

def _youdao_make_sign(app_key: str, app_secret: str, q: str, salt: str, curtime: str) -> str:
    """
    有道签名 signType=v3
    sign = sha256(appKey + input + salt + curtime + appSecret)
    input = q前10字符 + q长度 + q后10字符 (q长度>20时)
           或 q (q长度<=20时)
    """
    if len(q) > 20:
        input_str = q[:10] + str(len(q)) + q[-10:]
    else:
        input_str = q

    sign_str = app_key + input_str + salt + curtime + app_secret
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
    return sign


# ==================== 有道发音人列表 ====================

YOUDAO_VOICES = {
    # 中文
    "youxiaozhi":  {"name": "有小智", "gender": "男", "lang": "zh"},
    "youxiaoxun":  {"name": "有小薰", "gender": "女", "lang": "zh"},
    "youxiaoqin":  {"name": "有小沁", "gender": "女", "lang": "zh"},
    "youxiaofu":   {"name": "有小芙", "gender": "女", "lang": "zh"},
    "youyuting":   {"name": "有雨婷", "gender": "女", "lang": "zh"},
    "youxiaohao":  {"name": "有小浩", "gender": "男", "lang": "zh"},
    "youxiaonan":  {"name": "有小楠", "gender": "男", "lang": "zh"},
    "youxiaoke":   {"name": "有小课", "gender": "男", "lang": "zh"},
    "youxiaobei":  {"name": "有小贝", "gender": "女", "lang": "zh"},
    # 英文
    "youxiaomei":  {"name": "有小美", "gender": "女", "lang": "en-US"},
    "youxiaoying": {"name": "有小英", "gender": "女", "lang": "en-GB"},
    "youxiaowei":  {"name": "有小伟", "gender": "男", "lang": "en-zh"},
    "youxiaoguan": {"name": "有小官", "gender": "男", "lang": "en-GB"},
    "youyating":   {"name": "有雅婷", "gender": "女", "lang": "en-US"},
    "Saila":       {"name": "Saila",  "gender": "女", "lang": "en-GB"},
    "Auriana":     {"name": "Auriana","gender": "女", "lang": "en-GB"},
    "youxiaodao":  {"name": "有小道", "gender": "女", "lang": "en-US"},
    "youmeimei":   {"name": "有梅梅", "gender": "女", "lang": "en-US"},
    "youyingying": {"name": "有莹莹", "gender": "女", "lang": "en-GB"},
    "youxiaoshao": {"name": "有小绍", "gender": "女", "lang": "zh-en"},
    # 日文
    "youkejiang":  {"name": "有可酱", "gender": "女", "lang": "ja"},
    "yuantianjun": {"name": "原田君", "gender": "男", "lang": "ja"},
    # 韩文
    "piaozhiyou":  {"name": "朴智幼", "gender": "女", "lang": "ko"},
    "piaotaiyan":  {"name": "朴泰言", "gender": "男", "lang": "ko"},
    # 法语
    "faxiaomei":   {"name": "法小美", "gender": "女", "lang": "fr"},
    "faxiaoshuai": {"name": "法小帅", "gender": "男", "lang": "fr"},
    # 德语
    "dexiaomei":   {"name": "德小美", "gender": "女", "lang": "de"},
    "dexiaoshuai": {"name": "德小帅", "gender": "男", "lang": "de"},
    # 西班牙语
    "xixiaomei":   {"name": "西小美", "gender": "女", "lang": "es"},
    "Edgar":       {"name": "埃德加", "gender": "男", "lang": "es"},
    # 俄语
    "exiaomei":    {"name": "俄小美", "gender": "女", "lang": "ru"},
    "exiaoshuai":  {"name": "俄小帅", "gender": "男", "lang": "ru"},
    # 粤语
    "weiyueyue":   {"name": "薇粤粤", "gender": "女", "lang": "yue"},
}


# ==================== 引擎1: edge-tts ====================

async def _edge_tts_generate(text: str, voice: str, rate: str, pitch: str, output_file: str) -> bool:
    if edge_tts is None:
        return False
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
        return False
    except Exception as e:
        logger.warning(f"edge-tts 失败: {e}")
        return False


# ==================== 引擎2: 有道智云 TTS 官方 API ====================

YOUDAO_TTS_API = "https://openapi.youdao.com/ttsapi"


async def _youdao_official_tts_generate(
    text: str,
    lang: str,
    rate: str,
    output_file: str,
    voice_name: str = None
) -> bool:
    """
    有道智云官方 TTS API
    需要 YOUDAO_APP_KEY 和 YOUDAO_APP_SECRET
    """
    app_key = settings.YOUDAO_APP_KEY
    app_secret = settings.YOUDAO_APP_SECRET

    if not app_key or not app_secret or app_key == "你的appKey":
        logger.warning("有道智云 APP_KEY 未配置，跳过有道官方TTS")
        return False

    try:
        # 选择发音人
        if voice_name and voice_name in YOUDAO_VOICES:
            vn = voice_name
        elif lang == "zh":
            vn = getattr(settings, "YOUDAO_VOICE_ZH", "youxiaoqin")
        else:
            vn = getattr(settings, "YOUDAO_VOICE_EN", "youxiaomei")

        # 生成签名参数
        salt = str(uuid.uuid4())
        curtime = str(int(time.time()))
        sign = _youdao_make_sign(app_key, app_secret, text, salt, curtime)
        speed = _rate_to_youdao_speed(rate)

        # 构建请求参数
        data = {
            "q": text,
            "appKey": app_key,
            "salt": salt,
            "sign": sign,
            "signType": "v3",
            "curtime": curtime,
            "format": "mp3",
            "speed": speed,
            "volume": "1.00",
            "voiceName": vn,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                YOUDAO_TTS_API,
                data=data,  # 表单提交
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            )

            content_type = response.headers.get("content-type", "")

            # 成功: Content-Type 为 audio/mp3
            if "audio" in content_type:
                with open(output_file, "wb") as f:
                    f.write(response.content)
                if os.path.exists(output_file) and os.path.getsize(output_file) > 100:
                    logger.info(f"有道官方TTS成功, 发音人: {vn}, 语速: {speed}")
                    return True

            # 失败: Content-Type 为 application/json
            if "json" in content_type:
                error_data = response.json()
                error_code = error_data.get("errorCode", "unknown")
                logger.warning(f"有道官方TTS返回错误, errorCode={error_code}")

                error_messages = {
                    "108": "应用ID无效，请检查 YOUDAO_APP_KEY",
                    "110": "应用未绑定语音合成服务，请到控制台绑定",
                    "202": "签名校验失败，请检查 YOUDAO_APP_SECRET",
                    "401": "账户已欠费",
                    "411": "访问频率受限",
                    "2004": "合成字符过长(最大2048字节)",
                    "2013": f"voiceName参数错误: {vn}",
                }
                msg = error_messages.get(str(error_code), f"错误码: {error_code}")
                logger.warning(f"有道TTS错误详情: {msg}")
                return False

            logger.warning(f"有道官方TTS未知响应, Content-Type: {content_type}")
            return False

    except Exception as e:
        logger.warning(f"有道官方TTS异常: {e}")
        return False


# ==================== 引擎3: gTTS ====================

def _gtts_generate(text: str, lang: str, slow: bool, output_file: str) -> bool:
    if gTTS is None:
        return False
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(output_file)
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
        return False
    except Exception as e:
        logger.warning(f"gTTS 失败: {e}")
        return False


# ==================== 引擎4: pyttsx3 离线 ====================

def _pyttsx3_generate(text: str, rate_percent: int, output_file: str) -> bool:
    if _pyttsx3_module is None:
        return False
    try:
        engine = _pyttsx3_module.init()
        default_rate = 200
        adjusted_rate = int(default_rate * (1 + rate_percent / 100))
        engine.setProperty('rate', max(50, adjusted_rate))
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
        return False
    except Exception as e:
        logger.warning(f"pyttsx3 失败: {e}")
        return False


# ==================== 统一入口 ====================

async def text_to_speech(
    text: str,
    voice: str = None,
    rate: str = "+0%",
    pitch: str = "+0Hz",
    voice_name: str = None,
) -> dict:
    """
    将文本转为语音文件
    引擎优先级: edge-tts → 有道智云官方TTS → gTTS → pyttsx3

    :param text: 要合成的文本
    :param voice: edge-tts 语音名（如 zh-CN-XiaoxiaoNeural）
    :param rate: 语速 如 "-20%", "+30%"
    :param pitch: 音调（仅edge-tts）
    :param voice_name: 有道发音人名（如 youxiaoqin），指定后优先用有道
    """
    lang = detect_language(text)
    if not voice:
        voice = settings.TTS_VOICE_ZH if lang == "zh" else settings.TTS_VOICE_EN

    file_id = str(uuid.uuid4())
    output_file = os.path.join(settings.TTS_OUTPUT_DIR, f"{file_id}.mp3")
    rate_val, slow = _parse_rate(rate)
    engine_used = "none"
    success = False

    # 如果指定了有道发音人，优先用有道
    if voice_name and voice_name in YOUDAO_VOICES:
        success = await _youdao_official_tts_generate(text, lang, rate, output_file, voice_name)
        if success:
            engine_used = "youdao-official"

    # ---- 引擎1: edge-tts ----
    if not success:
        success = await _edge_tts_generate(text, voice, rate, pitch, output_file)
        if success:
            engine_used = "edge-tts"
            logger.info("TTS [edge-tts] 成功")

    # ---- 引擎2: 有道智云官方 TTS ----
    if not success:
        success = await _youdao_official_tts_generate(text, lang, rate, output_file)
        if success:
            engine_used = "youdao-official"
            logger.info("TTS [有道智云] 成功")

    # ---- 引擎3: gTTS ----
    if not success:
        gtts_lang = "zh-cn" if lang == "zh" else "en"
        success = _gtts_generate(text, gtts_lang, slow, output_file)
        if success:
            engine_used = "gtts"
            logger.info("TTS [gTTS] 成功")

    # ---- 引擎4: pyttsx3 离线 ----
    if not success:
        wav_file = os.path.join(settings.TTS_OUTPUT_DIR, f"{file_id}.wav")
        success = _pyttsx3_generate(text, rate_val, wav_file)
        if success:
            output_file = wav_file
            engine_used = "pyttsx3"
            logger.info("TTS [pyttsx3] 成功")

    # ---- 返回 ----
    if success:
        filename = os.path.basename(output_file)
        return {
            "success": True,
            "fileId": file_id,
            "filePath": output_file,
            "audioUrl": f"storage/audio/{filename}",
            "voice": voice_name if engine_used == "youdao-official" else voice,
            "rate": rate,
            "engine": engine_used
        }
    else:
        error_msg = "所有 TTS 引擎均不可用。请配置有道API Key 或安装 gTTS: pip install gTTS"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


async def text_to_speech_by_sentences(
    text: str,
    voice: str = None,
    rate: str = "+0%",
    voice_name: str = None,
) -> dict:
    """按句子切割，逐句生成语音"""
    lang = detect_language(text)
    if not voice:
        voice = settings.TTS_VOICE_ZH if lang == "zh" else settings.TTS_VOICE_EN

    if lang == "zh":
        sentences = re.split(r'(?<=[。！？!?\n])', text)
    else:
        sentences = re.split(r'(?<=[.!?\n])\s*', text)

    sentences = [s.strip() for s in sentences if s.strip()]
    results = []

    for idx, sentence in enumerate(sentences):
        result = await text_to_speech(
            text=sentence,
            voice=voice,
            rate=rate,
            voice_name=voice_name,
        )
        results.append({
            "index": idx,
            "sentence": sentence,
            "fileId": result.get("fileId", ""),
            "audioUrl": result.get("audioUrl", ""),
            "success": result.get("success", False),
            "engine": result.get("engine", ""),
            "error": result.get("error", "")
        })

    return {
        "totalSentences": len(sentences),
        "voice": voice,
        "sentences": results
    }


async def get_available_voices(language: str = None) -> List[dict]:
    """获取可用的语音列表"""
    voices = []

    # ---- edge-tts 语音 ----
    if edge_tts:
        try:
            edge_voices = await edge_tts.list_voices()
            for v in edge_voices:
                if language and not v["Locale"].lower().startswith(language.lower()):
                    continue
                voices.append({
                    "name": v["ShortName"],
                    "locale": v["Locale"],
                    "gender": v["Gender"],
                    "friendlyName": v.get("FriendlyName", v["ShortName"]),
                    "engine": "edge-tts"
                })
        except Exception as e:
            logger.warning(f"获取 edge-tts 语音列表失败: {e}")

    # ---- 有道智云发音人 ----
    has_youdao_key = (
        settings.YOUDAO_APP_KEY
        and settings.YOUDAO_APP_SECRET
        and settings.YOUDAO_APP_KEY != "你的appKey"
    )
    if has_youdao_key:
        for voice_id, info in YOUDAO_VOICES.items():
            vlang = info["lang"]
            if language:
                if language.lower() == "zh" and "zh" not in vlang.lower() and "yue" not in vlang.lower():
                    continue
                if language.lower() == "en" and "en" not in vlang.lower():
                    continue
                if language.lower() not in ("zh", "en") and language.lower() not in vlang.lower():
                    continue
            voices.append({
                "name": voice_id,
                "locale": vlang,
                "gender": info["gender"],
                "friendlyName": f"有道智云 - {info['name']} ({info['gender']})",
                "engine": "youdao-official"
            })

    # ---- gTTS ----
    if gTTS:
        gtts_languages = {
            "zh-CN": "Chinese (Simplified)",
            "zh-TW": "Chinese (Traditional)",
            "en": "English",
            "fr": "French",
            "de": "German",
            "ja": "Japanese",
            "ko": "Korean",
            "es": "Spanish",
            "ru": "Russian",
        }
        for code, name in gtts_languages.items():
            if language and not code.lower().startswith(language.lower()):
                continue
            voices.append({
                "name": f"gtts-{code}",
                "locale": code,
                "gender": "Unknown",
                "friendlyName": f"gTTS - {name}",
                "engine": "gtts"
            })

    # ---- pyttsx3 ----
    if _pyttsx3_module:
        if not language or language.lower() in ("zh", "en"):
            voices.append({
                "name": "pyttsx3-default",
                "locale": "system",
                "gender": "Unknown",
                "friendlyName": "系统离线语音 (pyttsx3)",
                "engine": "pyttsx3"
            })

    return voices
