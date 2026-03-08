"""Notion 데이터베이스 동기화 모듈"""

import json
import os
import subprocess
import sys
from datetime import date


def _get_clean_env():
    """중첩 세션 방지를 위해 CLAUDECODE 환경변수를 제거한 env 반환"""
    env = {**os.environ}
    env.pop("CLAUDECODE", None)
    return env

# Notion 데이터소스 ID (콘텐츠 파이프라인 DB)
NOTION_DATA_SOURCE_ID = "a47e6f1d-657c-4c2b-bea1-66ac7ca2da86"

# 카테고리 매핑
CATEGORY_MAP = {
    "ai_tech": "🔵 AI/기술",
    "health": "🟢 건강",
    "self_improvement": "🟠 자기계발",
}

# 상태 매핑
STATUS_MAP = {
    "research": "🔍 리서치",
    "planning": "📐 기획 중",
    "writing": "✍️ 라이팅 중",
    "creative": "🎨 크리에이티브",
    "review": "📋 검수 중",
    "approved": "✅ 발행 승인",
    "revision": "🔄 수정 필요",
    "published": "📤 발행 완료",
}

# 팀 매핑
TEAM_MAP = {
    "research": "🔍 리서치팀",
    "planning": "📐 기획팀",
    "writing": "✍️ 라이팅팀",
    "creative": "🎨 크리에이티브팀",
    "editorial": "📋 편집팀",
}


def update_notion_status(title: str, status: str, team: str, content: str = "", score: float = None, url: str = None):
    """Notion DB의 상태를 업데이트합니다.

    Claude Code CLI를 통해 Notion MCP를 호출합니다.
    """
    prompt = f"""Notion의 '콘텐츠 파이프라인' 데이터베이스에서
제목이 '{title}'인 항목의 상태를 '{STATUS_MAP.get(status, status)}'로,
담당 팀을 '{TEAM_MAP.get(team, team)}'로 업데이트해주세요."""

    if score is not None:
        prompt += f"\n검수 점수를 {score}으로 설정해주세요."
    if url:
        prompt += f"\n발행 URL을 '{url}'로 설정해주세요."
    if content:
        prompt += f"\n\n페이지 본문에 다음 내용을 추가해주세요:\n{content}"

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
        env=_get_clean_env(),
    )

    if result.returncode != 0:
        print(f"Notion 업데이트 실패: {result.stderr}", file=sys.stderr)
    else:
        print(f"Notion 업데이트 완료: {title} → {STATUS_MAP.get(status, status)}")


def create_notion_entry(title: str, category: str, keyword: str, publish_date: str):
    """새 콘텐츠 항목을 Notion DB에 생성합니다."""
    prompt = f"""Notion의 '콘텐츠 파이프라인' 데이터베이스(data_source_id: {NOTION_DATA_SOURCE_ID})에
새 항목을 추가해주세요:
- 제목: {title}
- 카테고리: {CATEGORY_MAP.get(category, category)}
- 상태: 🔍 리서치
- 키워드: {keyword}
- 담당 팀: 🔍 리서치팀
- 발행 예정일: {publish_date}"""

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
        env=_get_clean_env(),
    )

    if result.returncode != 0:
        print(f"Notion 항목 생성 실패: {result.stderr}", file=sys.stderr)
    else:
        print(f"Notion 항목 생성 완료: {title}")
