"""Claude Code CLI를 사용한 블로그 글 생성 (Max 구독 활용)"""

import os
import subprocess
import json
import sys

from config.settings import TOPICS, POST_MIN_LENGTH, POST_MAX_LENGTH


def generate_post(topic_key: str) -> dict:
    """Claude Code CLI로 블로그 글을 생성합니다.

    Max 구독을 활용하므로 API 과금이 없습니다.

    Returns:
        {"title": str, "content": str, "excerpt": str, "tags": list[str]}
    """
    topic = TOPICS[topic_key]

    prompt = f"""당신은 한국어 블로그 전문 작가입니다.
아래 조건에 맞는 블로그 글을 작성하고, 반드시 JSON 형식으로만 출력해주세요.

## 조건
- 주제 분야: {topic["name"]}
- 관련 키워드 중 2~3개 활용: {", ".join(topic["keywords"])}
- 어조: {topic["tone"]}
- 글자 수: {POST_MIN_LENGTH}~{POST_MAX_LENGTH}자
- SEO 친화적인 제목
- HTML 형식으로 본문 작성 (<h2>, <h3>, <p>, <ul>, <li>, <strong> 태그 활용)
- 도입부에서 독자의 관심을 끌 것
- 실용적인 팁이나 인사이트 포함
- 자연스러운 마무리

## 출력 형식
아래 JSON 형식으로만 출력하세요. 다른 텍스트 없이 JSON만 출력합니다:
{{"title": "제목", "excerpt": "2줄 요약", "tags": ["태그1", "태그2", "태그3"], "content": "<h2>...</h2><p>...</p>"}}"""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )

    if result.returncode != 0:
        print(f"Claude Code 실행 실패: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return _parse_response(result.stdout)


def _parse_response(output: str) -> dict:
    """Claude Code CLI 응답을 파싱합니다."""
    try:
        # --output-format json 응답에서 result 추출
        response = json.loads(output)
        text = response.get("result", output)
    except (json.JSONDecodeError, TypeError):
        text = output

    # JSON 블록 추출 (```json ... ``` 또는 순수 JSON)
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        post = json.loads(text)
    except json.JSONDecodeError:
        print(f"JSON 파싱 실패. 원본 응답:\n{text[:500]}", file=sys.stderr)
        sys.exit(1)

    required = ["title", "content"]
    for key in required:
        if key not in post:
            print(f"필수 필드 누락: {key}", file=sys.stderr)
            sys.exit(1)

    return {
        "title": post["title"],
        "content": post["content"],
        "excerpt": post.get("excerpt", ""),
        "tags": post.get("tags", []),
    }
