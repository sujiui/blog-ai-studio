"""Blog AI 자동발행 설정"""

import os
from dotenv import load_dotenv

load_dotenv()

# WordPress REST API
WP_URL = os.getenv("WP_URL", "")  # 예: https://yourblog.com
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")  # WordPress 애플리케이션 비밀번호

# 블로그 카테고리 및 주제
TOPICS = {
    "ai_tech": {
        "name": "AI/기술",
        "keywords": ["인공지능", "머신러닝", "GPT", "자동화", "프로그래밍", "클라우드", "데이터"],
        "tone": "전문성은 유지하되, 독자에게 신기한 발견을 공유하는 친근한 톤",
    },
    "health": {
        "name": "건강",
        "keywords": ["운동", "식단", "수면", "멘탈헬스", "습관", "웰빙", "영양"],
        "tone": "따뜻하고 실용적으로, 직접 해본 사람이 알려주는 느낌",
    },
    "self_improvement": {
        "name": "자기계발",
        "keywords": ["생산성", "독서", "목표설정", "시간관리", "마인드셋", "성장", "루틴"],
        "tone": "현실적이고 공감되는 톤, 같이 성장하는 느낌",
    },
}

# 트렌드 큐레이션 소스
TREND_SOURCES = [
    "AI 뉴스레터 (The Rundown AI, Ben's Bites, TLDR AI)",
    "Reddit (r/ChatGPT, r/LocalLLaMA, r/cursor)",
    "X/트위터 (#builtwithAI, #vibecoding)",
    "유튜브 (AI로 만들어봤습니다 류)",
    "Product Hunt (신규 AI 도구 런칭)",
    "Hacker News (기술 커뮤니티 화제글)",
]

# 발행 스케줄 (월=0, 수=2, 금=4)
PUBLISH_DAYS = [0, 2, 4]

# 주제 로테이션 순서 (월: AI/기술, 수: 건강, 금: 자기계발)
DAY_TOPIC_MAP = {
    0: "ai_tech",
    2: "health",
    4: "self_improvement",
}

# 글 설정
POST_MIN_LENGTH = 1500  # 최소 글자 수
POST_MAX_LENGTH = 3000  # 최대 글자 수
POST_STATUS = "draft"   # draft(임시저장) 또는 publish(바로 발행)
