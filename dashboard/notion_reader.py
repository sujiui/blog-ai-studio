"""Notion API에서 콘텐츠 파이프라인 데이터를 읽어오는 모듈"""

import os
import requests

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "9cd5aabbbbd644128abc34a58de7c2f2")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers():
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fetch_all_contents():
    """Notion DB에서 전체 콘텐츠 목록을 가져옵니다."""
    if not NOTION_API_KEY:
        return []

    url = f"{NOTION_API_URL}/databases/{NOTION_DATABASE_ID}/query"

    payload = {
        "sorts": [
            {"property": "발행 예정일", "direction": "descending"}
        ]
    }

    try:
        res = requests.post(url, headers=_headers(), json=payload, timeout=10)
        if not res.ok:
            print(f"Notion API 오류: {res.status_code} {res.text[:200]}")
            return []

        results = res.json().get("results", [])
        return [_parse_page(page) for page in results]
    except Exception as e:
        print(f"Notion 연결 실패: {e}")
        return []


def _parse_page(page):
    """Notion 페이지 데이터를 대시보드용으로 변환합니다."""
    props = page.get("properties", {})

    title = _get_title(props.get("제목", {}))
    category = _get_select(props.get("카테고리", {}))
    status = _get_select(props.get("상태", {}))
    keyword = _get_rich_text(props.get("키워드", {}))
    team = _get_select(props.get("담당 팀", {}))
    score = _get_number(props.get("검수 점수", {}))
    pub_url = _get_url(props.get("발행 URL", {}))
    grade = _get_select(props.get("성과 등급", {}))
    content_id = _get_unique_id(props.get("콘텐츠 ID", {}))

    # 날짜
    pub_scheduled = _get_date(props.get("발행 예정일", {}))
    pub_actual = _get_date(props.get("발행일", {}))

    # 통계
    w1_views = _get_number(props.get("1주차 조회수", {}))
    w2_views = _get_number(props.get("2주차 조회수", {}))
    w3_views = _get_number(props.get("3주차 조회수", {}))
    w1_comments = _get_number(props.get("1주차 댓글", {}))
    w2_comments = _get_number(props.get("2주차 댓글", {}))
    w3_comments = _get_number(props.get("3주차 댓글", {}))

    # 현재 팀 키 결정
    team_key = _status_to_team_key(status)

    # 카테고리 키 결정
    cat_key = _category_to_key(category)

    return {
        "id": page["id"],
        "content_id": content_id,
        "title": title,
        "category": category,
        "category_key": cat_key,
        "status": status,
        "keyword": keyword,
        "team": team,
        "team_key": team_key,
        "score": score,
        "pub_url": pub_url,
        "grade": grade,
        "pub_scheduled": pub_scheduled,
        "pub_actual": pub_actual,
        "stats": {
            "week_1": {"views": w1_views, "comments": w1_comments} if w1_views else None,
            "week_2": {"views": w2_views, "comments": w2_comments} if w2_views else None,
            "week_3": {"views": w3_views, "comments": w3_comments} if w3_views else None,
        },
    }


def _status_to_team_key(status):
    """상태값을 팀 키로 변환"""
    mapping = {
        "🔍 리서치": "research",
        "📐 기획 중": "planning",
        "✍️ 라이팅 중": "writing",
        "🎨 크리에이티브": "creative",
        "📋 검수 중": "editorial",
        "✅ 발행 승인": "done",
        "🔄 수정 필요": "editorial",
        "📤 발행 완료": "published",
    }
    return mapping.get(status, "research")


def _category_to_key(category):
    """카테고리 표시값을 키로 변환"""
    if "AI" in (category or ""):
        return "ai_tech"
    elif "건강" in (category or ""):
        return "health"
    elif "자기계발" in (category or ""):
        return "self_improvement"
    return ""


# Notion property 파서들
def _get_title(prop):
    items = prop.get("title", [])
    return items[0].get("plain_text", "") if items else ""


def _get_rich_text(prop):
    items = prop.get("rich_text", [])
    return items[0].get("plain_text", "") if items else ""


def _get_select(prop):
    sel = prop.get("select")
    return sel.get("name", "") if sel else ""


def _get_number(prop):
    return prop.get("number")


def _get_url(prop):
    return prop.get("url", "")


def _get_date(prop):
    d = prop.get("date")
    return d.get("start", "") if d else ""


def _get_unique_id(prop):
    uid = prop.get("unique_id")
    if uid:
        prefix = uid.get("prefix", "")
        number = uid.get("number", "")
        return f"{prefix}-{number}" if prefix else str(number)
    return ""
