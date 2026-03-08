"""발행 후 성과 추적 모듈

WordPress REST API로 조회수/댓글 수를 가져와
Notion DB와 로컬 대시보드에 기록합니다.

사용법:
    # 발행 URL 등록
    python -m src.tracker register <content_id> <wordpress_url>

    # 통계 수집 (모든 발행된 글)
    python -m src.tracker collect

    # 특정 글 통계 확인
    python -m src.tracker status <content_id>
"""

import json
import os
import sys
import requests
import logging
from datetime import date, datetime, timedelta

from config.settings import WP_URL, WP_USERNAME, WP_APP_PASSWORD

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
TRACKER_FILE = os.path.join(OUTPUT_DIR, "tracker.json")


def load_tracker() -> dict:
    """추적 데이터 로드"""
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"posts": {}}


def save_tracker(data: dict):
    """추적 데이터 저장"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_post(content_id: str, wp_url: str):
    """발행된 글을 추적 목록에 등록합니다."""
    tracker = load_tracker()

    # WordPress post ID 추출 (URL 또는 직접 입력)
    post_id = None
    if wp_url.isdigit():
        post_id = int(wp_url)
    else:
        # URL에서 post slug로 조회
        try:
            slug = wp_url.rstrip("/").split("/")[-1]
            res = requests.get(
                f"{WP_URL}/wp-json/wp/v2/posts",
                params={"slug": slug},
                timeout=10,
            )
            if res.ok and res.json():
                post_id = res.json()[0]["id"]
        except Exception as e:
            logger.warning(f"WordPress 조회 실패: {e}")

    tracker["posts"][content_id] = {
        "wp_url": wp_url,
        "wp_post_id": post_id,
        "published_date": date.today().isoformat(),
        "stats": {
            "week_1": None,
            "week_2": None,
            "week_3": None,
        },
        "grade": None,
    }

    save_tracker(tracker)

    # 로컬 summary.json 업데이트
    summary_path = os.path.join(OUTPUT_DIR, content_id, "summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)
        summary["wp_url"] = wp_url
        summary["published_date"] = date.today().isoformat()
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"✅ 등록 완료: {content_id} → {wp_url}")

    # Notion 업데이트
    _update_notion_tracking(content_id, tracker["posts"][content_id])


def collect_stats():
    """모든 발행 글의 통계를 수집합니다."""
    tracker = load_tracker()
    today = date.today()

    for content_id, post in tracker["posts"].items():
        pub_date = date.fromisoformat(post["published_date"])
        days_since = (today - pub_date).days

        # 어떤 주차 통계를 수집해야 하는지 결정
        week = None
        if 6 <= days_since <= 8 and post["stats"]["week_1"] is None:
            week = "week_1"
        elif 13 <= days_since <= 15 and post["stats"]["week_2"] is None:
            week = "week_2"
        elif 20 <= days_since <= 22 and post["stats"]["week_3"] is None:
            week = "week_3"

        if week is None:
            continue

        logger.info(f"📊 {content_id} — {week} 통계 수집 중...")
        stats = _fetch_wp_stats(post)

        if stats:
            post["stats"][week] = {
                "date": today.isoformat(),
                "views": stats["views"],
                "comments": stats["comments"],
                "likes": stats.get("likes", 0),
            }

            # 3주차까지 완료되면 성과 등급 매기기
            if week == "week_3":
                post["grade"] = _calculate_grade(post["stats"])

            save_tracker(tracker)
            _update_notion_tracking(content_id, post)

            print(f"📊 {content_id} {week}: 조회 {stats['views']}, 댓글 {stats['comments']}")
        else:
            print(f"⚠️ {content_id} 통계 수집 실패")

    print("📊 통계 수집 완료!")


def show_status(content_id: str = None):
    """추적 현황을 보여줍니다."""
    tracker = load_tracker()

    if content_id:
        posts = {content_id: tracker["posts"].get(content_id)}
        if posts[content_id] is None:
            print(f"❌ {content_id}는 추적 목록에 없습니다.")
            return
    else:
        posts = tracker["posts"]

    if not posts:
        print("📭 추적 중인 글이 없습니다.")
        return

    print(f"\n{'='*70}")
    print(f"📊 Blog AI Studio — 성과 추적 현황")
    print(f"{'='*70}\n")

    for cid, post in posts.items():
        print(f"📝 {cid}")
        print(f"   URL: {post['wp_url']}")
        print(f"   발행일: {post['published_date']}")
        print(f"   등급: {post.get('grade', '측정 중...')}")
        print()

        for week_key, week_label in [("week_1", "1주차"), ("week_2", "2주차"), ("week_3", "3주차")]:
            stats = post["stats"].get(week_key)
            if stats:
                print(f"   {week_label}: 조회 {stats['views']:,} | 댓글 {stats['comments']} | 좋아요 {stats.get('likes', 0)}")
            else:
                pub_date = date.fromisoformat(post["published_date"])
                target_date = pub_date + timedelta(weeks=int(week_key[-1]))
                if date.today() < target_date:
                    print(f"   {week_label}: ⏳ {target_date} 이후 수집 예정")
                else:
                    print(f"   {week_label}: ⚠️ 미수집")
        print()


def _fetch_wp_stats(post: dict) -> dict:
    """WordPress에서 글 통계를 가져옵니다."""
    post_id = post.get("wp_post_id")
    if not post_id or not WP_URL:
        return None

    try:
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)

        # 글 정보 조회
        res = requests.get(
            f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            timeout=10,
        )
        if not res.ok:
            return None

        post_data = res.json()

        # 댓글 수 조회
        comments_res = requests.get(
            f"{WP_URL}/wp-json/wp/v2/comments",
            params={"post": post_id},
            auth=auth,
            timeout=10,
        )
        comment_count = len(comments_res.json()) if comments_res.ok else 0

        return {
            "views": post_data.get("jetpack_featured_media_url", 0),  # Jetpack 조회수 (있을 경우)
            "comments": comment_count,
        }
    except Exception as e:
        logger.warning(f"WordPress 통계 조회 실패: {e}")
        return None


def _calculate_grade(stats: dict) -> str:
    """3주간 통계를 기반으로 성과 등급을 매깁니다."""
    total_views = 0
    total_comments = 0

    for week in ["week_1", "week_2", "week_3"]:
        if stats[week]:
            total_views += stats[week].get("views", 0)
            total_comments += stats[week].get("comments", 0)

    # 성과 등급 기준
    score = total_views + (total_comments * 50)  # 댓글 1개 = 조회 50 가치

    if score >= 5000:
        return "🏆 S"
    elif score >= 2000:
        return "🥇 A"
    elif score >= 500:
        return "🥈 B"
    elif score >= 100:
        return "🥉 C"
    else:
        return "❌ D"


def _update_notion_tracking(content_id: str, post: dict):
    """Notion DB에 추적 데이터를 업데이트합니다."""
    import subprocess

    stats_summary = ""
    for week_key, week_label in [("week_1", "1주차"), ("week_2", "2주차"), ("week_3", "3주차")]:
        s = post["stats"].get(week_key)
        if s:
            stats_summary += f"\n- {week_label}: 조회 {s['views']:,} | 댓글 {s['comments']}"

    grade = post.get("grade", "측정 중")

    prompt = f"""Notion의 '콘텐츠 파이프라인' 데이터베이스에서
콘텐츠 ID나 제목에 '{content_id}'가 포함된 항목을 찾아서:
- 상태를 '📤 발행 완료'로 변경
- 발행 URL을 '{post["wp_url"]}'로 설정
- 발행일을 '{post["published_date"]}'로 설정
{f"- 성과 등급을 '{grade}'로 설정" if post.get("grade") else ""}

페이지 본문에 다음 내용을 추가해주세요:
## 📊 성과 추적
- 발행일: {post["published_date"]}
- 등급: {grade}
{stats_summary if stats_summary else "- 아직 통계 수집 전"}
"""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True, text=True, timeout=60, env=env,
    )

    if result.returncode != 0:
        logger.warning(f"Notion 추적 업데이트 실패: {result.stderr[:200]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    args = sys.argv[1:]
    if not args:
        print("사용법:")
        print("  python -m src.tracker register <content_id> <wordpress_url>")
        print("  python -m src.tracker collect")
        print("  python -m src.tracker status [content_id]")
        sys.exit(0)

    command = args[0]

    if command == "register" and len(args) >= 3:
        register_post(args[1], args[2])
    elif command == "collect":
        collect_stats()
    elif command == "status":
        show_status(args[1] if len(args) >= 2 else None)
    else:
        print(f"알 수 없는 명령: {command}")
