"""WordPress REST API를 사용한 블로그 발행"""

import requests
from requests.auth import HTTPBasicAuth
from config.settings import WP_URL, WP_USERNAME, WP_APP_PASSWORD, POST_STATUS


def publish_post(post: dict) -> dict:
    """WordPress에 글을 발행합니다.

    Args:
        post: {"title", "content", "excerpt", "tags"}

    Returns:
        WordPress API 응답 (id, link 포함)
    """
    # 태그 ID 조회 또는 생성
    tag_ids = _get_or_create_tags(post.get("tags", []))

    payload = {
        "title": post["title"],
        "content": post["content"],
        "excerpt": post.get("excerpt", ""),
        "status": POST_STATUS,
        "tags": tag_ids,
    }

    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=payload,
        auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )
    response.raise_for_status()

    result = response.json()
    return {
        "id": result["id"],
        "link": result["link"],
        "status": result["status"],
        "title": result["title"]["rendered"],
    }


def _get_or_create_tags(tag_names: list) -> list:
    """태그를 조회하거나 없으면 생성합니다."""
    tag_ids = []
    auth = HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)

    for name in tag_names:
        # 기존 태그 검색
        res = requests.get(
            f"{WP_URL}/wp-json/wp/v2/tags",
            params={"search": name},
            auth=auth,
            timeout=10,
        )
        res.raise_for_status()
        tags = res.json()

        if tags:
            tag_ids.append(tags[0]["id"])
        else:
            # 새 태그 생성
            res = requests.post(
                f"{WP_URL}/wp-json/wp/v2/tags",
                json={"name": name},
                auth=auth,
                timeout=10,
            )
            res.raise_for_status()
            tag_ids.append(res.json()["id"])

    return tag_ids
