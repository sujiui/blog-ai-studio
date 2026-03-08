"""Blog AI Studio 클라우드 대시보드 (Notion API 기반)"""

import os
from flask import Flask, render_template
from dashboard.notion_reader import fetch_all_contents

app = Flask(__name__, template_folder="templates")

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


@app.route("/")
def index():
    contents = fetch_all_contents()
    return render_template("cloud_index.html",
                           contents=contents,
                           teams=TEAMS,
                           categories=CATEGORY_INFO)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
