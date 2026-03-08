"""Blog AI Studio 메인 실행 스크립트"""

import sys
import os
import logging
from typing import Optional
from datetime import datetime, date

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config.settings import PUBLISH_DAYS, DAY_TOPIC_MAP, TOPICS
from src.pipeline import run_pipeline

# 로깅 설정
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/{date.today().isoformat()}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run(topic_key: Optional[str] = None, keyword: Optional[str] = None):
    """블로그 파이프라인을 실행합니다.

    사용법:
        python -m src.main                          # 오늘 요일에 맞는 주제 자동 선택
        python -m src.main ai_tech                  # 카테고리 지정
        python -m src.main ai_tech "AI 코딩 도구 비교"  # 카테고리 + 키워드 직접 지정
    """
    today = datetime.now().weekday()

    # 주제 결정
    if topic_key:
        if topic_key not in TOPICS:
            logger.error(f"알 수 없는 주제: {topic_key}. 사용 가능: {list(TOPICS.keys())}")
            sys.exit(1)
    elif today in DAY_TOPIC_MAP:
        topic_key = DAY_TOPIC_MAP[today]
    else:
        logger.info(f"오늘({today})은 발행일이 아닙니다. (발행일: 월/수/금)")
        logger.info("주제를 직접 지정하려면: python -m src.main ai_tech")
        return

    topic = TOPICS[topic_key]

    # 키워드가 없으면 기본 키워드 사용
    if not keyword:
        keyword = f"{topic['name']} 블로그 주제"
        logger.info(f"키워드를 지정하지 않았습니다. 리서치팀이 자동으로 주제를 선정합니다.")

    logger.info(f"🏢 Blog AI Studio 시작")
    logger.info(f"📂 카테고리: {topic['name']}")
    logger.info(f"🔑 키워드: {keyword}")

    result = run_pipeline(keyword=keyword, category=topic_key)

    if result.get("approved"):
        logger.info("✅ 발행 준비 완료! 대시보드에서 확인 후 발행하세요.")
        logger.info("   대시보드: python dashboard/app.py → http://localhost:8080")
    else:
        logger.info("🔄 수정이 필요합니다. 대시보드에서 피드백을 확인하세요.")


if __name__ == "__main__":
    args = sys.argv[1:]
    topic = args[0] if len(args) >= 1 else None
    kw = args[1] if len(args) >= 2 else None
    run(topic, kw)
