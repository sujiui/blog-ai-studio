"""나노바나나 이미지 생성기 — Gemini API 기본 + 구글 이미지 검색 폴백

기본: Gemini(google.genai)로 이미지 생성
폴백: 생성 실패 시 구글에서 관련 이미지를 검색해서 다운로드
인포그래픽은 AI 티가 나므로 제외 — 자연스러운 일러스트/사진 스타일 위주
"""

import json
import os
import subprocess
import sys
import time
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# 모델 설정 (리서치 기반)
MODELS = {
    "body": "gemini-3.1-flash-image-preview",     # Nano Banana 2 — 4-8초, Pro급+Flash속도
    "thumbnail": "gemini-3-pro-image-preview",     # Nano Banana Pro — 최고 품질
    "fallback": "gemini-2.5-flash-image",          # 초기 모델 — 폴백용
}

# 이미지 배치 전략 (리서치: 200-300자당 1장, 1500-3000자 글에 5-10장)
IMAGE_PLACEMENT = {
    "hero": "최상단 — SNS 미리보기, OG 이미지",
    "section_start": "각 섹션 시작 — 가독성, 체류시간",
    "diagram": "프로세스/비교 부분",
    "cta": "글 하단 — CTA 영역",
}

# 스타일별 이미지 전략 (인포그래픽 제외)
STYLE_IMAGE_MAP = {
    "info_delivery": {
        "style": "현대적이고 세련된 제품/서비스 스크린샷 느낌",
        "prompt_hint": "modern, clean, product screenshot style, realistic",
        "avoid": "infographic, chart, diagram, text overlay",
    },
    "review_experience": {
        "style": "실제 제품/서비스 사용 장면, 비교 이미지",
        "prompt_hint": "realistic product photo, hands-on experience, comparison layout",
        "avoid": "infographic, cartoon, abstract",
    },
    "essay_emotional": {
        "style": "감성적 일러스트, 따뜻한 색감, 부드러운 톤",
        "prompt_hint": "warm, emotional, soft illustration, pastel colors, dreamy atmosphere",
        "avoid": "infographic, technical, cold, corporate",
    },
    "list_curation": {
        "style": "각 항목 대표 이미지, 밝고 컬러풀한 사진",
        "prompt_hint": "bright, colorful, clean product photo, lifestyle photography",
        "avoid": "infographic, chart, text-heavy",
    },
    "expert_analysis": {
        "style": "깔끔한 데이터 시각화 느낌이지만 사진/일러스트 위주",
        "prompt_hint": "clean, professional, business photography, modern illustration",
        "avoid": "infographic, AI-generated chart, complex diagram",
    },
    "friendly_chat": {
        "style": "캐주얼한 일상 사진, 밈 스타일",
        "prompt_hint": "casual, everyday life, fun, relatable, lifestyle photo",
        "avoid": "infographic, formal, corporate",
    },
    "tutorial_howto": {
        "style": "단계별 스크린샷/가이드 이미지",
        "prompt_hint": "step-by-step guide, screenshot style, clean UI, tutorial illustration",
        "avoid": "infographic, abstract art",
    },
}

# 이미지 사이즈
SIZES = {
    "thumbnail": "16:9",
    "hero": "16:9",
    "body": "16:9",
    "square": "1:1",
}


def generate_image(description, style_id="info_delivery", image_type="body", output_path=None):
    # type: (str, str, str, Optional[str]) -> Optional[str]
    """이미지를 생성하고 파일 경로를 반환한다.

    전략: Gemini 생성 시도 → 실패 시 구글 이미지 검색 폴백

    Args:
        description: 이미지 설명 (기획서에서 가져옴)
        style_id: 스타일 프리셋 ID
        image_type: body / thumbnail / hero
        output_path: 저장 경로 (None이면 자동 생성)

    Returns:
        저장된 이미지 파일 경로 또는 None (실패 시)
    """
    if output_path is None:
        output_path = "/tmp/blog_image_%d.png" % int(time.time())

    # 1차: Gemini 이미지 생성
    result = _generate_with_gemini(description, style_id, image_type, output_path)
    if result:
        return result

    # 2차: 폴백 모델로 재시도
    result = _generate_with_gemini(description, style_id, image_type, output_path, use_fallback=True)
    if result:
        return result

    # 3차: 구글 이미지 검색 폴백
    print("Gemini 생성 실패 — 구글 이미지 검색으로 폴백", file=sys.stderr)
    result = _search_web_image(description, output_path)
    if result:
        return result

    print("이미지 생성 최종 실패: %s" % description[:50], file=sys.stderr)
    return None


def generate_placeholder(description, output_path):
    # type: (str, str) -> str
    """이미지 생성 실패 시 placeholder 텍스트 파일을 생성한다."""
    placeholder_path = output_path.rsplit(".", 1)[0] + "_placeholder.txt"
    with open(placeholder_path, "w", encoding="utf-8") as f:
        f.write("[이미지: %s — 생성 실패, 수동 업로드 필요]\n" % description)
    return placeholder_path


def _generate_with_gemini(description, style_id, image_type, output_path, use_fallback=False):
    # type: (str, str, str, str, bool) -> Optional[str]
    """Gemini API로 이미지를 생성한다."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY가 설정되지 않았습니다.", file=sys.stderr)
        return None

    # 모델 선택
    if use_fallback:
        model = MODELS["fallback"]
    elif image_type == "thumbnail":
        model = MODELS["thumbnail"]
    else:
        model = MODELS["body"]

    # 프롬프트 구성
    prompt = _build_prompt(description, style_id, image_type)
    aspect = SIZES.get(image_type, "16:9")

    # 3회 재시도
    for attempt in range(3):
        result = _call_gemini_api(api_key, model, prompt, aspect, output_path)
        if result:
            return result

        wait_time = (3 ** attempt)  # 1, 3, 9초
        print("이미지 생성 실패 (시도 %d/3), %d초 후 재시도..." % (attempt + 1, wait_time),
              file=sys.stderr)
        time.sleep(wait_time)

    return None


def _build_prompt(description, style_id, image_type):
    # type: (str, str, str) -> str
    """이미지 생성 프롬프트를 구성한다. 인포그래픽 제외."""
    style_info = STYLE_IMAGE_MAP.get(style_id, STYLE_IMAGE_MAP["info_delivery"])

    prompt_parts = [
        description,
        style_info["prompt_hint"],
        "high quality, detailed, professional blog image",
        "no text, no watermarks, no logos",
        "NOT: %s" % style_info["avoid"],
    ]

    if image_type == "thumbnail":
        prompt_parts.append("eye-catching hero image, suitable for social media preview")

    return ". ".join(prompt_parts)


def _call_gemini_api(api_key, model, prompt, aspect_ratio, output_path):
    # type: (str, str, str, str, str) -> Optional[str]
    """google.genai 라이브러리로 Gemini API를 호출한다."""
    # prompt 안의 따옴표 이스케이프
    safe_prompt = prompt.replace("\\", "\\\\").replace("'", "\\'")
    safe_key = api_key.replace("'", "\\'")
    safe_path = output_path.replace("'", "\\'")

    script = "\n".join([
        "from google import genai",
        "from google.genai import types",
        "import sys",
        "",
        "client = genai.Client(api_key='%s')" % safe_key,
        "",
        "try:",
        "    response = client.models.generate_content(",
        "        model='%s'," % model,
        "        contents='%s'," % safe_prompt,
        "        config=types.GenerateContentConfig(",
        "            response_modalities=['IMAGE', 'TEXT'],",
        "            image_config=types.ImageConfig(aspect_ratio='%s')," % aspect_ratio,
        "        ),",
        "    )",
        "",
        "    for part in response.candidates[0].content.parts:",
        "        if part.inline_data is not None:",
        "            with open('%s', 'wb') as f:" % safe_path,
        "                f.write(part.inline_data.data)",
        "            sys.exit(0)",
        "",
        "    print('No image in response', file=sys.stderr)",
        "    sys.exit(1)",
        "except Exception as e:",
        "    print('Gemini error: ' + str(e), file=sys.stderr)",
        "    sys.exit(1)",
    ])

    try:
        result = subprocess.run(
            ["python3", "-c", script],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            if size > 1000:  # 최소 1KB 이상이어야 유효한 이미지
                return output_path
        if result.stderr:
            print("Gemini stderr: %s" % result.stderr.strip()[:200], file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("Gemini timeout (120s)", file=sys.stderr)
    except FileNotFoundError:
        print("python3 not found", file=sys.stderr)

    return None


def _search_web_image(description, output_path):
    # type: (str, str) -> Optional[str]
    """주제 관련 이미지를 검색해서 다운로드한다 (폴백용).

    전략:
    1. Claude CLI + WebSearch로 Pexels/Pixabay/Wikimedia 직접 다운로드 URL 탐색
    2. Pixabay API 검색 (API 키 없어도 일부 동작)
    3. Wikimedia Commons API 검색 (완전 무료, 주제 적합성 높음)
    """
    env = {k: v for k, v in os.environ.items()}
    env.pop("CLAUDECODE", None)

    # 1차: Claude CLI + WebSearch — 직접 다운로드 가능한 관련 이미지 URL 탐색
    prompt = (
        '다음 이미지 설명에 딱 맞는 무료 이미지를 찾아줘. '
        'Pexels(images.pexels.com), Pixabay(pixabay.com/get/...), '
        'Wikimedia Commons(upload.wikimedia.org) 중에서 찾아줘. '
        '반드시 .jpg 또는 .png로 끝나는 직접 다운로드 URL만 응답해줘. '
        '웹 페이지 URL 말고 이미지 파일 URL이어야 해. '
        '다른 설명 없이 URL 한 줄만.\n\n'
        '설명: %s' % description
    )

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=60, env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            url = _extract_url(result.stdout)
            if url and _is_direct_image_url(url):
                downloaded = _download_image(url, output_path)
                if downloaded:
                    return downloaded
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 2차: Wikimedia Commons API — 무료, 주제 관련성 높음
    try:
        english_query = _to_english_query(description, env)
        wiki_result = _search_wikimedia(english_query, output_path)
        if wiki_result:
            return wiki_result
    except Exception:
        pass

    print("이미지 검색 폴백 모두 실패: %s" % description[:50], file=sys.stderr)
    return None


def _is_direct_image_url(url):
    # type: (str) -> bool
    """직접 다운로드 가능한 이미지 URL인지 확인한다."""
    url_lower = url.lower().split("?")[0]
    return any(url_lower.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp"))


def _to_english_query(description, env):
    # type: (str, dict) -> str
    """한국어 설명을 영문 검색어로 변환한다."""
    # 간단한 키워드 추출 (Claude CLI 없이도 동작)
    korean_to_eng = {
        "바둑": "go game board", "알파고": "alphago AI", "이세돌": "go game player",
        "AI": "artificial intelligence", "인공지능": "artificial intelligence",
        "미래": "future technology", "로봇": "robot", "컴퓨터": "computer",
        "건강": "health", "수면": "sleep", "의료": "medical",
    }
    query = description
    for kor, eng in korean_to_eng.items():
        if kor in description:
            return eng
    # 영문이 이미 포함된 경우 그대로 사용
    english_words = [w for w in description.split() if w.isascii() and len(w) > 2]
    if english_words:
        return " ".join(english_words[:3])
    return "technology abstract"


def _search_wikimedia(query, output_path):
    # type: (str, str) -> Optional[str]
    """Wikimedia Commons API로 이미지를 검색하고 다운로드한다."""
    try:
        result = subprocess.run(
            [
                "curl", "-sL", "-G",
                "https://commons.wikimedia.org/w/api.php",
                "--data-urlencode", "action=query",
                "--data-urlencode", "generator=search",
                "--data-urlencode", "gsrnamespace=6",
                "--data-urlencode", "gsrsearch=%s" % query,
                "--data-urlencode", "gsrlimit=5",
                "--data-urlencode", "prop=imageinfo",
                "--data-urlencode", "iiprop=url|mime",
                "--data-urlencode", "format=json",
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            mime = info.get("mime", "")
            url = info.get("url", "")
            if url and mime in ("image/jpeg", "image/png", "image/webp"):
                downloaded = _download_image(url, output_path)
                if downloaded:
                    return downloaded
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        pass
    return None


def _extract_url(raw_output):
    # type: (str) -> Optional[str]
    """Claude CLI 응답에서 URL을 추출한다."""
    try:
        wrapper = json.loads(raw_output)
        if isinstance(wrapper, dict) and "result" in wrapper:
            text = wrapper["result"]
        else:
            text = raw_output
    except json.JSONDecodeError:
        text = raw_output

    # URL 추출
    for word in text.split():
        word = word.strip('"\'`<>()[]')
        if word.startswith("http"):
            return word
    return None


def _download_image(url, output_path):
    # type: (str, str) -> Optional[str]
    """URL에서 이미지를 다운로드한다."""
    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", output_path, "-m", "15", url],
            capture_output=True, timeout=20,
        )
        if result.returncode == 0 and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            if size > 5000:  # 최소 5KB
                return output_path
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None
