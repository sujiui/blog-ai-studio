"""트렌드 수집기 — 다중 소스에서 최신 트렌드를 수집"""

import json
import os
import subprocess
import sys
from typing import Optional


# 수집 소스 설정
SOURCES = {
    "google_trends": {"timeout": 10, "required": False},
    "news_rss": {"timeout": 10, "required": False},
    "web_search": {"timeout": 15, "required": True},
}

# 최소 성공 소스 수
MIN_SUCCESS_SOURCES = 2


def collect_trends(keywords=None, category=None):
    # type: (list, str) -> dict
    """여러 소스에서 트렌드를 수집한다.

    keywords가 None이면 전체 트렌드를 수집한다 (주제 추천 모드).

    Args:
        keywords: 검색 키워드 리스트 (None이면 전체 트렌드)
        category: 블로그 카테고리 (더 이상 강제하지 않음)

    Returns:
        dict: {
            "trends": [...],
            "sources_status": {"source": "success/fail"},
            "success_count": int
        }
    """
    if keywords is None:
        keywords = []

    results = {
        "trends": [],
        "sources_status": {},
        "success_count": 0,
        "keywords_used": keywords,
    }

    # Google Trends (pytrends)
    gt_result = _collect_google_trends(keywords)
    results["sources_status"]["google_trends"] = "success" if gt_result else "fail"
    if gt_result:
        results["trends"].extend(gt_result)
        results["success_count"] += 1

    # News RSS (feedparser)
    rss_result = _collect_news_rss(keywords)
    results["sources_status"]["news_rss"] = "success" if rss_result else "fail"
    if rss_result:
        results["trends"].extend(rss_result)
        results["success_count"] += 1

    # YouTube Trends
    yt_result = _collect_youtube_trends(keywords)
    results["sources_status"]["youtube"] = "success" if yt_result else "fail"
    if yt_result:
        results["trends"].extend(yt_result)
        results["success_count"] += 1

    # 네이버 블로그 트렌드
    naver_result = _collect_naver_blog_trends(keywords)
    results["sources_status"]["naver_blog"] = "success" if naver_result else "fail"
    if naver_result:
        results["trends"].extend(naver_result)
        results["success_count"] += 1

    # Web Search (Claude CLI)
    web_result = _collect_web_search(keywords, category or "")
    results["sources_status"]["web_search"] = "success" if web_result else "fail"
    if web_result:
        results["trends"].extend(web_result)
        results["success_count"] += 1

    return results


def suggest_topics(max_topics=5):
    # type: (int) -> list
    """트렌드 분석으로 블로그 주제를 추천한다.

    Returns:
        list: [{"topic": "주제", "reason": "추천 이유", "source": "출처"}]
    """
    trend_data = collect_trends()  # 키워드 없이 전체 트렌드

    if not trend_data["trends"]:
        return []

    # Claude CLI로 트렌드에서 블로그 주제 추출
    trends_summary = json.dumps(trend_data["trends"][:20], ensure_ascii=False)

    prompt = (
        "다음 트렌드 데이터에서 블로그 글로 쓰기 좋은 주제 %d개를 추천해줘.\n\n"
        "트렌드 데이터:\n%s\n\n"
        "JSON 배열로 응답:\n"
        '[{"topic": "주제", "reason": "왜 이 주제가 좋은지 한 줄", "source": "트렌드 출처"}]'
    ) % (max_topics, trends_summary)

    env = {k: v for k, v in os.environ.items()}
    env.pop("CLAUDECODE", None)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        if result.returncode == 0:
            content = _parse_output(result.stdout)
            data = json.loads(content)
            if isinstance(data, list):
                return data[:max_topics]
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass

    return []


def is_sufficient(trend_result):
    # type: (dict) -> bool
    """수집된 트렌드가 충분한지 판단한다."""
    return trend_result["success_count"] >= MIN_SUCCESS_SOURCES


def _collect_google_trends(keywords):
    # type: (list) -> Optional[list]
    """Google Trends에서 관련 트렌드를 수집한다."""
    script = '''
import sys
import json
try:
    from pytrends.request import TrendReq
    pytrends = TrendReq(hl="ko-KR", tz=540)
    kw_list = {keywords}
    # 최대 5개만
    kw_list = kw_list[:5]
    pytrends.build_payload(kw_list, cat=0, timeframe="now 7-d", geo="KR")
    related = pytrends.related_queries()
    results = []
    for kw, data in related.items():
        if data and data.get("rising") is not None:
            for _, row in data["rising"].head(3).iterrows():
                results.append({{"source": "google_trends", "keyword": kw, "trend": row["query"], "value": str(row["value"])}})
    print(json.dumps(results, ensure_ascii=False))
except Exception as e:
    print(json.dumps([]), file=sys.stdout)
    print(f"Google Trends error: {{e}}", file=sys.stderr)
'''.replace("{keywords}", repr(keywords))

    try:
        result = subprocess.run(
            ["python3", "-c", script],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data:
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def _collect_news_rss(keywords):
    # type: (list) -> Optional[list]
    """RSS 피드에서 최신 뉴스를 수집한다."""
    # 한국어 뉴스 RSS 피드
    feeds = [
        "https://news.google.com/rss/search?q={kw}&hl=ko&gl=KR&ceid=KR:ko"
    ]

    script = '''
import sys
import json
try:
    import feedparser
    results = []
    keywords = {keywords}
    for kw in keywords[:3]:
        url = f"https://news.google.com/rss/search?q={{kw}}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            results.append({{
                "source": "news_rss",
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "keyword": kw,
            }})
    print(json.dumps(results, ensure_ascii=False))
except Exception as e:
    print(json.dumps([]), file=sys.stdout)
    print(f"RSS error: {{e}}", file=sys.stderr)
'''.replace("{keywords}", repr(keywords))

    try:
        result = subprocess.run(
            ["python3", "-c", script],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data:
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def _collect_youtube_trends(keywords):
    # type: (list) -> Optional[list]
    """YouTube 인기 급상승 동영상에서 트렌드를 수집한다."""
    search_query = " ".join(keywords[:3]) if keywords else "트렌드"

    env = {k: v for k, v in os.environ.items()}
    env.pop("CLAUDECODE", None)

    prompt = (
        "YouTube에서 '%s' 관련 최근 인기 동영상이나 트렌드를 검색해서 정리해줘.\n\n"
        "JSON 배열로 응답:\n"
        '[{"source": "youtube", "title": "제목", "channel": "채널명", '
        '"topic": "주제 키워드", "relevance": "high/medium"}]\n\n'
        "최소 3개, 최대 5개."
    ) % search_query

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=20, env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            content = _parse_output(result.stdout)
            data = json.loads(content)
            if isinstance(data, list) and data:
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def _collect_naver_blog_trends(keywords):
    # type: (list) -> Optional[list]
    """네이버 블로그에서 인기 키워드/주제를 수집한다."""
    search_query = " ".join(keywords[:3]) if keywords else "인기 블로그"

    env = {k: v for k, v in os.environ.items()}
    env.pop("CLAUDECODE", None)

    prompt = (
        "네이버 블로그에서 '%s' 관련 인기 글이나 트렌드 키워드를 검색해서 정리해줘.\n"
        "네이버 블로그에서 많이 다뤄지는 주제, 인기 키워드를 중심으로.\n\n"
        "JSON 배열로 응답:\n"
        '[{"source": "naver_blog", "title": "인기 주제", "keyword": "키워드", '
        '"summary": "한줄 요약", "relevance": "high/medium"}]\n\n'
        "최소 3개, 최대 5개."
    ) % search_query

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=20, env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            content = _parse_output(result.stdout)
            data = json.loads(content)
            if isinstance(data, list) and data:
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def _collect_web_search(keywords, category):
    # type: (list, str) -> Optional[list]
    """Claude CLI의 웹 검색으로 최신 정보를 수집한다."""
    search_query = " ".join(keywords[:3])

    prompt = f"""다음 키워드에 대한 최신 트렌드와 정보를 검색해서 정리해줘.

키워드: {search_query}
카테고리: {category}

JSON 배열로 응답:
[
  {{
    "source": "web_search",
    "title": "정보 제목",
    "summary": "핵심 내용 2-3줄",
    "url": "출처 URL (있으면)",
    "relevance": "high/medium/low"
  }}
]

최소 3개, 최대 5개 결과를 포함해줘. 최신 정보를 우선."""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=30, env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            content = _parse_output(result.stdout)
            data = json.loads(content)
            if isinstance(data, list) and data:
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def _parse_output(raw):
    # type: (str) -> str
    """Claude CLI JSON wrapper 해제."""
    try:
        wrapper = json.loads(raw)
        if isinstance(wrapper, dict) and "result" in wrapper:
            content = wrapper["result"]
        else:
            return raw
    except json.JSONDecodeError:
        content = raw

    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        return content[start:end].strip()
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        return content[start:end].strip()
    return content
