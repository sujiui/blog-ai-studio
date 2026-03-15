"""WordPress REST API를 사용한 블로그 발행 + 미디어 업로드"""

import mimetypes
import os
import re
import sys
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth
from config.settings import WP_URL, WP_USERNAME, WP_APP_PASSWORD, POST_STATUS


def publish_post(post):
    # type: (dict) -> dict
    """WordPress에 글을 발행합니다. 본문 이미지도 함께 업로드.

    Args:
        post: {
            "title": str,
            "content": str (HTML),
            "excerpt": str,
            "tags": list,
            "images_dir": str (optional, 이미지 디렉토리 경로),
            "thumbnail_path": str (optional, 썸네일 이미지 경로),
        }

    Returns:
        {"id", "link", "status", "title", "uploaded_images": [...]}
    """
    auth = HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)
    content = post["content"]
    uploaded_images = []

    # 1. 본문의 로컬 이미지를 WordPress에 업로드하고 URL 교체
    # images_dir의 부모 디렉토리를 base_dir로 사용해 상대 경로 해석
    images_dir = post.get("images_dir")
    base_dir = os.path.dirname(images_dir) if images_dir else None
    content, uploaded_images = _upload_and_replace_images(content, auth, base_dir=base_dir)

    # 2. images_dir이 있으면 그 안의 이미지도 업로드 (본문에 없는 이미지)
    if images_dir and os.path.isdir(images_dir):
        for fname in sorted(os.listdir(images_dir)):
            fpath = os.path.join(images_dir, fname)
            if _is_image_file(fpath) and fpath not in [u["local_path"] for u in uploaded_images]:
                result = upload_media(fpath, auth=auth)
                if result:
                    uploaded_images.append(result)

    # 3. 태그 ID 조회 또는 생성
    tag_ids = _get_or_create_tags(post.get("tags", []))

    # 4. 썸네일(featured image) 설정
    featured_media_id = None
    thumbnail_path = post.get("thumbnail_path")
    if thumbnail_path and os.path.isfile(thumbnail_path):
        thumb_result = upload_media(thumbnail_path, auth=auth)
        if thumb_result:
            featured_media_id = thumb_result["id"]
            uploaded_images.append(thumb_result)
    elif uploaded_images:
        # 썸네일이 없으면 첫 번째 업로드 이미지를 대표 이미지로
        featured_media_id = uploaded_images[0]["id"]

    # 5. 글 발행
    scheduled_date = post.get("scheduled_date")  # "2026-03-17T09:00:00" 형식
    status = "future" if scheduled_date else POST_STATUS
    payload = {
        "title": post["title"],
        "content": content,
        "excerpt": post.get("excerpt", ""),
        "status": status,
        "tags": tag_ids,
    }
    if scheduled_date:
        payload["date"] = scheduled_date
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    response = requests.post(
        "%s/wp-json/wp/v2/posts" % WP_URL,
        json=payload,
        auth=auth,
        timeout=30,
    )
    response.raise_for_status()

    result = response.json()
    return {
        "id": result["id"],
        "link": result["link"],
        "status": result["status"],
        "title": result["title"]["rendered"],
        "uploaded_images": uploaded_images,
    }


def upload_media(file_path, alt_text=None, auth=None):
    # type: (str, Optional[str], Optional[HTTPBasicAuth]) -> Optional[dict]
    """이미지를 WordPress 미디어 라이브러리에 업로드합니다.

    Args:
        file_path: 로컬 이미지 파일 경로
        alt_text: 대체 텍스트 (SEO용)
        auth: HTTPBasicAuth (None이면 기본 설정 사용)

    Returns:
        {"id": int, "url": str, "local_path": str} 또는 None
    """
    if not os.path.isfile(file_path):
        print("파일이 존재하지 않습니다: %s" % file_path, file=sys.stderr)
        return None

    if auth is None:
        auth = HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)

    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "image/png"

    with open(file_path, "rb") as f:
        file_data = f.read()

    headers = {
        "Content-Disposition": "attachment; filename=%s" % filename,
        "Content-Type": mime_type,
    }

    try:
        response = requests.post(
            "%s/wp-json/wp/v2/media" % WP_URL,
            headers=headers,
            data=file_data,
            auth=auth,
            timeout=60,
        )
        response.raise_for_status()
        media = response.json()

        # alt text 설정
        if alt_text:
            requests.post(
                "%s/wp-json/wp/v2/media/%d" % (WP_URL, media["id"]),
                json={"alt_text": alt_text},
                auth=auth,
                timeout=10,
            )

        return {
            "id": media["id"],
            "url": media["source_url"],
            "local_path": file_path,
        }
    except requests.RequestException as e:
        print("미디어 업로드 실패 (%s): %s" % (filename, e), file=sys.stderr)
        return None


def _upload_and_replace_images(html_content, auth, base_dir=None):
    # type: (str, HTTPBasicAuth, Optional[str]) -> tuple
    """HTML 본문에서 로컬 이미지 경로를 찾아 WordPress에 업로드하고 URL을 교체합니다.

    <img src="/local/path/image.png"> → <img src="https://wp.site/wp-content/uploads/image.png">
    <figure> 태그 안의 이미지도 처리합니다.

    Args:
        base_dir: HTML 파일의 기준 디렉토리. 상대 경로(images/foo.png 등) 해석에 사용.
    """
    uploaded = []

    # img 태그의 src에서 로컬 경로 찾기 (http로 시작하지 않는 경로)
    img_pattern = re.compile(r'(<img\s[^>]*src=")([^"]+)(")')

    def replace_img(match):
        prefix = match.group(1)
        src = match.group(2)
        suffix = match.group(3)

        # 이미 URL이면 건너뜀
        if src.startswith("http"):
            return match.group(0)

        # 절대 경로 또는 base_dir 기준 상대 경로 모두 시도
        candidates = [src]
        if base_dir and not os.path.isabs(src):
            candidates.insert(0, os.path.join(base_dir, src))

        resolved = next((p for p in candidates if os.path.isfile(p)), None)
        if resolved:
            alt_match = re.search(r'alt="([^"]*)"', match.group(0))
            alt_text = alt_match.group(1) if alt_match else None

            result = upload_media(resolved, alt_text=alt_text, auth=auth)
            if result:
                uploaded.append(result)
                return prefix + result["url"] + suffix

        return match.group(0)

    new_content = img_pattern.sub(replace_img, html_content)
    return new_content, uploaded


def _is_image_file(path):
    # type: (str) -> bool
    """파일이 이미지인지 확인합니다."""
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")


def _get_or_create_tags(tag_names):
    # type: (list) -> list
    """태그를 조회하거나 없으면 생성합니다."""
    tag_ids = []
    auth = HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)

    for name in tag_names:
        try:
            # 기존 태그 검색
            res = requests.get(
                "%s/wp-json/wp/v2/tags" % WP_URL,
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
                    "%s/wp-json/wp/v2/tags" % WP_URL,
                    json={"name": name},
                    auth=auth,
                    timeout=10,
                )
                res.raise_for_status()
                tag_ids.append(res.json()["id"])
        except requests.RequestException as e:
            print("태그 처리 실패 (%s): %s" % (name, e), file=sys.stderr)

    return tag_ids
