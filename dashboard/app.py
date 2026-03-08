"""Blog AI Studio 로컬 대시보드"""

import json
import os
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
TRACKER_FILE = os.path.join(OUTPUT_DIR, "tracker.json")

TEAMS = {
    "research": {"name": "리서치팀", "emoji": "🔍", "color": "#3B82F6"},
    "planning": {"name": "기획팀", "emoji": "📐", "color": "#8B5CF6"},
    "writing": {"name": "라이팅팀", "emoji": "✍️", "color": "#10B981"},
    "creative": {"name": "크리에이티브팀", "emoji": "🎨", "color": "#F59E0B"},
    "editorial": {"name": "편집팀", "emoji": "📋", "color": "#EF4444"},
}

CATEGORY_INFO = {
    "ai_tech": {"label": "AI/기술", "emoji": "🔵", "color": "#3B82F6"},
    "health": {"label": "건강", "emoji": "🟢", "color": "#10B981"},
    "self_improvement": {"label": "자기계발", "emoji": "🟠", "color": "#F59E0B"},
}

PHASE_ORDER = ["plan", "article", "images_manifest", "metadata", "review"]


def get_all_content():
    """output 디렉토리에서 모든 콘텐츠 데이터 로드"""
    contents = []
    if not os.path.exists(OUTPUT_DIR):
        return contents

    for dirname in sorted(os.listdir(OUTPUT_DIR), reverse=True):
        content_dir = os.path.join(OUTPUT_DIR, dirname)
        if not os.path.isdir(content_dir):
            continue

        content = {"id": dirname, "dir": content_dir}

        for fname in ["summary.json", "plan.json", "metadata.json", "review.json", "images_manifest.json"]:
            fpath = os.path.join(content_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, encoding="utf-8") as f:
                    content[fname.replace(".json", "")] = json.load(f)

        article_path = os.path.join(content_dir, "article.html")
        if os.path.exists(article_path):
            with open(article_path, encoding="utf-8") as f:
                content["article"] = f.read()

        # 현재 담당 팀 결정
        content["current_team"] = _determine_current_team(content)

        contents.append(content)

    return contents


def get_tracker():
    """트래커 데이터 로드"""
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"posts": {}}


def _determine_current_team(content):
    """콘텐츠의 현재 담당 팀 결정"""
    has_review = "review" in content and content["review"].get("score")
    has_images = "images_manifest" in content
    has_article = "article" in content
    has_plan = "plan" in content

    if has_review:
        score = content["review"].get("score", 0)
        if score >= 80:
            return {"key": "done", "name": "발행 승인", "emoji": "✅", "color": "#22C55E"}
        else:
            return {"key": "editorial", **TEAMS["editorial"]}
    elif has_images:
        return {"key": "editorial", **TEAMS["editorial"]}
    elif has_article:
        return {"key": "creative", **TEAMS["creative"]}
    elif has_plan:
        return {"key": "writing", **TEAMS["writing"]}
    else:
        return {"key": "planning", **TEAMS["planning"]}


@app.route("/")
def index():
    contents = get_all_content()
    tracker = get_tracker()
    return render_template("index.html",
                           contents=contents,
                           tracker=tracker,
                           teams=TEAMS,
                           categories=CATEGORY_INFO,
                           phase_order=PHASE_ORDER)


@app.route("/content/<content_id>")
def content_detail(content_id):
    content_dir = os.path.join(OUTPUT_DIR, content_id)
    if not os.path.exists(content_dir):
        return "Not Found", 404

    content = {"id": content_id}
    for fname in ["summary.json", "plan.json", "metadata.json", "review.json", "images_manifest.json"]:
        fpath = os.path.join(content_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                content[fname.replace(".json", "")] = json.load(f)

    article_path = os.path.join(content_dir, "article.html")
    if os.path.exists(article_path):
        with open(article_path, encoding="utf-8") as f:
            content["article"] = f.read()

    content["current_team"] = _determine_current_team(content)

    tracker = get_tracker()
    content["tracking"] = tracker.get("posts", {}).get(content_id)

    return render_template("detail.html", content=content, teams=TEAMS, categories=CATEGORY_INFO)


@app.route("/api/contents")
def api_contents():
    return jsonify(get_all_content())


if __name__ == "__main__":
    print("🏢 Blog AI Studio Dashboard")
    print("http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
