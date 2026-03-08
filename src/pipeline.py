"""Blog AI 전체 파이프라인 오케스트레이터"""

import json
import os
import sys
import subprocess
import logging
from datetime import date, datetime

from config.settings import TOPICS, POST_STATUS
from src.notion_sync import update_notion_status

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def ensure_output_dir(content_id: str) -> str:
    """콘텐츠별 출력 디렉토리 생성"""
    path = os.path.join(OUTPUT_DIR, content_id)
    os.makedirs(path, exist_ok=True)
    return path


def run_pipeline(keyword: str, category: str, publish_date: str = None):
    """전체 파이프라인을 순차 실행합니다."""

    content_id = f"{date.today().isoformat()}_{category}"
    out_dir = ensure_output_dir(content_id)
    publish_date = publish_date or date.today().isoformat()

    logger.info(f"{'='*50}")
    logger.info(f"Blog AI Pipeline 시작")
    logger.info(f"키워드: {keyword}")
    logger.info(f"카테고리: {category}")
    logger.info(f"{'='*50}")

    # ─── Phase 1: 📐 기획팀 ───
    logger.info("\n📐 [Phase 1] 기획팀 작업 시작...")
    update_notion_status(keyword, "planning", "planning")
    plan = run_phase_planning(keyword, category, out_dir)
    logger.info("📐 기획팀 완료!")

    # ─── Phase 2: ✍️ 라이팅팀 ───
    logger.info("\n✍️ [Phase 2] 라이팅팀 작업 시작...")
    update_notion_status(keyword, "writing", "writing",
                         content="## ✍️ 라이팅팀\n본문 작성 중...")
    article = run_phase_writing(plan, out_dir)
    logger.info("✍️ 라이팅팀 완료!")

    # ─── Phase 3+4: 🎨 크리에이티브팀 ───
    logger.info("\n🎨 [Phase 3+4] 크리에이티브팀 작업 시작...")
    update_notion_status(keyword, "creative", "creative",
                         content="## 🎨 크리에이티브팀\n이미지 생성 중...")
    images = run_phase_creative(plan, article, out_dir)
    logger.info("🎨 크리에이티브팀 완료!")

    # ─── Phase 5+6: 📋 편집팀 ───
    logger.info("\n📋 [Phase 5+6] 편집팀 작업 시작...")
    update_notion_status(keyword, "review", "editorial",
                         content="## 📋 편집팀\n최종 검수 중...")
    result = run_phase_editorial(plan, article, out_dir)

    # 검수 결과에 따른 처리
    score = result.get("score", 0)
    if score >= 80:
        logger.info(f"📋 편집팀: {score}점 → ✅ 발행 승인!")
        update_notion_status(keyword, "approved", "editorial",
                             score=score,
                             content=f"## 📋 편집팀 검수 결과\n- **점수**: {score}점 ✅\n- **판정**: 발행 승인")
    else:
        logger.info(f"📋 편집팀: {score}점 → 🔄 수정 필요")
        update_notion_status(keyword, "revision", "editorial",
                             score=score,
                             content=f"## 📋 편집팀 검수 결과\n- **점수**: {score}점 ❌\n- **판정**: 수정 필요\n- **수정사항**: {result.get('feedback', '')}")

    # 결과 요약 저장
    summary = {
        "content_id": content_id,
        "keyword": keyword,
        "category": category,
        "publish_date": publish_date,
        "score": score,
        "approved": score >= 80,
        "output_dir": out_dir,
        "created_at": datetime.now().isoformat(),
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    logger.info(f"\n{'='*50}")
    logger.info(f"Pipeline 완료! 결과: {out_dir}")
    logger.info(f"{'='*50}")

    return summary


def run_phase_planning(keyword: str, category: str, out_dir: str) -> dict:
    """Phase 1: 기획팀 — 콘텐츠 기획서 생성"""
    topic = TOPICS.get(category, {})

    prompt = f"""당신은 AI/기술 트렌드 큐레이션 블로그 기획 전문가입니다.

## 콘텐츠 방향
이 블로그는 "요즘 AI로 이런 것도 된다고?" 같은 트렌드 큐레이션 채널입니다.
뉴스레터, Reddit, X(트위터), 유튜브, Product Hunt 등에서 화제가 된 AI 활용 사례를 소개하고,
직접 따라해보며 독자에게 실용적인 인사이트를 전달합니다.

## 작업
'{keyword}' 주제로 트렌드 큐레이션 블로그 기획서를 작성하세요.

## 조건
- 분야: {topic.get('name', category)}
- 어조: {topic.get('tone', '친근하고 전문적인 톤')}

## 글 구조 (이 흐름을 따르세요)
1. 🔥 화제 소개 — 최근 온라인에서 화제가 된 사례/도구/뉴스를 흥미롭게 소개
2. 🤔 뭐가 대단한 건데? — 왜 이게 주목받는지 맥락과 의미 분석
3. 🛠️ 직접 해보니 — 실제로 따라해본 과정, 되는 것/안 되는 것/꿀팁
4. 💡 이걸로 뭘 할 수 있을까 — 독자가 자기 상황에 적용할 수 있는 방법
5. 📌 마무리 — 핵심 요약 + 독자 참여 유도

## 수행할 작업
1. 검색 의도 분석 (이 주제에 관심 있는 사람이 정말 알고 싶은 것)
2. 상위 경쟁 글 분석 (강점, 약점, 빠진 내용)
3. 차별화 전략 (단순 소개가 아닌 "직접 해보고 솔직하게 알려주는" 포지션)
4. H태그 구조 설계 (H1 1개, H2 3~5개, H3 세부 — 위의 글 구조 반영)
5. 섹션별 핵심 포인트 (각 H2 아래 다룰 내용 3줄)
6. CTA 전략 — 중요: 존재하지 않는 서비스(뉴스레터, PDF, 체크리스트 등)를 만들지 마세요. 블로그 내 실현 가능한 CTA만 사용 (관련 글 추천, 댓글 유도, 블로그 구독, 공유하기 등)
7. 이미지 기획 (2~4장, 유형과 설명)
8. 톤/스타일 지시 — 전문성은 유지하되 독자에게 신기한 발견을 알려주는 친근한 톤. 너무 격식체도, 너무 반말체도 아닌 편안한 존댓말.

## 출력
JSON 형식으로만 출력하세요:
{{"keyword":"{keyword}","search_intent":"...","target_reader":"...","differentiation":"...","trending_hook":"화제가 된 사례나 뉴스 한 줄 요약","structure":{{"h1":"...","sections":[{{"h2":"...","points":["..."],"h3":["..."]}}]}},"cta":{{"position":"...","type":"...","tone":"..."}},"images":[{{"type":"...","desc":"..."}}],"tone":"..."}}"""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)  # 중첩 세션 방지 우회

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True, text=True, timeout=300, env=env,
    )

    plan = _parse_json_output(result.stdout, "plan")

    with open(os.path.join(out_dir, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    return plan


def run_phase_writing(plan: dict, out_dir: str) -> str:
    """Phase 2: 라이팅팀 — SEO 본문 작성"""
    prompt = f"""당신은 AI/기술 트렌드 큐레이션 블로그 작가입니다.

## 블로그 성격
이 블로그는 온라인에서 화제가 된 AI 활용 사례를 소개하고, 직접 따라해보며
독자에게 실용적인 인사이트를 전달하는 트렌드 큐레이션 채널입니다.

## 기획서
{json.dumps(plan, ensure_ascii=False)}

## 작성 규칙
1. 기획서의 H태그 구조를 정확히 따를 것
2. 메인 키워드 '{plan.get("keyword", "")}' 밀도 2~3%
3. LSI 키워드 5~7개 자연스럽게 분산
4. 도입부에서 "요즘 이런 게 화제인데요" 식으로 자연스럽게 시작
5. 문단 3~4줄, 불릿 포인트, 볼드 강조 활용
6. CTA는 기획서 전략에 따라 자연스럽게. 존재하지 않는 서비스(뉴스레터, PDF 등)를 언급하지 말 것
7. 이미지 삽입 위치에 <!-- IMAGE_N: 설명 --> 마커 반드시 포함 (최소 2개)
8. HTML 태그 사용 (h2, h3, p, ul, li, strong)
9. 2,000~3,000자

## 톤 가이드
- 전문성은 유지하되, 독자에게 재미있는 발견을 공유하는 느낌
- 너무 격식체(~하였습니다)도, 너무 반말체(~했어)도 아닌 편안한 존댓말
- 예시: "이거 보셨나요?", "직접 해보니 생각보다 괜찮았어요", "한번 따라해보시면 느낌이 올 거예요"
- 딱딱한 보고서가 아니라, 옆 자리 동료가 "야 이거 대박인데" 하고 알려주는 느낌 (다만 존댓말로)

## 출력
HTML 본문만 출력하세요. 다른 설명 없이 HTML만."""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True, text=True, timeout=300, env=env,
    )

    article = _extract_text(result.stdout)

    with open(os.path.join(out_dir, "article.html"), "w", encoding="utf-8") as f:
        f.write(article)

    return article


def run_phase_creative(plan: dict, article: str, out_dir: str) -> list:
    """Phase 3+4: 크리에이티브팀 — 이미지 + 썸네일 생성 (Gemini)"""
    images_dir = os.path.join(out_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    image_plans = plan.get("images", [])
    generated = []

    for i, img_plan in enumerate(image_plans):
        prompt = f"""Generate a clean, professional blog illustration:
- Type: {img_plan.get('type', 'illustration')}
- Description: {img_plan.get('desc', 'blog image')}
- Style: Modern, minimal, suitable for a Korean tech/lifestyle blog
- Colors: Professional palette
- No text in the image
- 16:9 aspect ratio"""

        try:
            result = subprocess.run(
                ["python3", "-c", f"""
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.ImageGenerationModel("gemini-2.0-flash-exp")

response = model.generate_images(
    prompt='''{prompt}''',
    number_of_images=1,
)

for j, img in enumerate(response.images):
    img.save('{images_dir}/image_{i+1}.png')
    print(f'Saved: image_{i+1}.png')
"""],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "")},
            )
            if result.returncode == 0:
                generated.append(f"image_{i+1}.png")
                logger.info(f"  이미지 {i+1}/{len(image_plans)} 생성 완료")
            else:
                logger.warning(f"  이미지 {i+1} 생성 실패: {result.stderr[:200]}")
        except Exception as e:
            logger.warning(f"  이미지 {i+1} 생성 오류: {e}")

    # 썸네일 생성
    keyword = plan.get("keyword", "blog")
    category_colors = {"ai_tech": "blue", "health": "green", "self_improvement": "orange"}

    try:
        thumb_prompt = f"""Generate a blog thumbnail image:
- Title concept: {keyword}
- Style: Clean, modern, eye-catching
- Color tone: {category_colors.get(plan.get('category', ''), 'blue')} accent
- 1200x630px ratio (OG image)
- Minimal text, focus on visual impact"""

        result = subprocess.run(
            ["python3", "-c", f"""
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.ImageGenerationModel("gemini-2.0-flash-exp")

response = model.generate_images(
    prompt='''{thumb_prompt}''',
    number_of_images=1,
)

for img in response.images:
    img.save('{images_dir}/thumbnail.png')
    print('Saved: thumbnail.png')
"""],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "")},
        )
        if result.returncode == 0:
            generated.append("thumbnail.png")
            logger.info("  썸네일 생성 완료")
    except Exception as e:
        logger.warning(f"  썸네일 생성 오류: {e}")

    with open(os.path.join(out_dir, "images_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": generated, "total_planned": len(image_plans)}, f, indent=2)

    return generated


def run_phase_editorial(plan: dict, article: str, out_dir: str) -> dict:
    """Phase 5+6: 편집팀 — 메타데이터 + 최종 검수"""

    # Phase 5: 메타데이터 생성
    meta_prompt = f"""당신은 SEO 메타데이터 전문가입니다.

## 기획서 키워드
{plan.get('keyword', '')}

## 본문 (일부)
{article[:1000]}

## 생성할 것
JSON 형식으로만 출력:
{{"seo_title":"60자 이내, 키워드 앞배치","meta_description":"155자 이내","slug":"영문 소문자 URL","tags":["태그1","태그2","태그3"],"og_title":"소셜 공유용 제목","og_description":"소셜 공유용 설명"}}"""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    meta_result = subprocess.run(
        ["claude", "-p", meta_prompt, "--output-format", "json"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    metadata = _parse_json_output(meta_result.stdout, "metadata")

    with open(os.path.join(out_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Phase 6: 최종 검수
    review_prompt = f"""당신은 블로그 콘텐츠 품질 검수 편집장입니다.

## 기획서
{json.dumps(plan, ensure_ascii=False)[:500]}

## 본문
{article[:2000]}

## 검수 항목 (각 항목 100점 만점)
1. SEO: 키워드 밀도, H태그 구조, 메타 길이
2. 가독성: 문단 길이, 문장 복잡도
3. 팩트 체크: 통계/수치 신뢰성
4. CTA: 자연스러운 배치
5. 이미지: 마커 존재 확인

## 출력
JSON 형식으로만:
{{"score":87,"pass":true,"checks":{{"seo":{{"score":90,"notes":"..."}},"readability":{{"score":85,"notes":"..."}},"fact_check":{{"score":80,"notes":"..."}},"cta":{{"score":92,"notes":"..."}},"images":{{"score":88,"notes":"..."}}}},"feedback":"종합 피드백"}}"""

    review_result = subprocess.run(
        ["claude", "-p", review_prompt, "--output-format", "json"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    review = _parse_json_output(review_result.stdout, "review")

    with open(os.path.join(out_dir, "review.json"), "w", encoding="utf-8") as f:
        json.dump(review, f, ensure_ascii=False, indent=2)

    return review


def _parse_json_output(output: str, label: str) -> dict:
    """Claude CLI JSON 응답 파싱"""
    try:
        response = json.loads(output)
        text = response.get("result", output)
    except (json.JSONDecodeError, TypeError):
        text = output

    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning(f"{label} JSON 파싱 실패, 기본값 반환")
        return {"error": "parse_failed", "raw": text[:500]}


def _extract_text(output: str) -> str:
    """Claude CLI 응답에서 텍스트 추출"""
    try:
        response = json.loads(output)
        return response.get("result", output)
    except (json.JSONDecodeError, TypeError):
        return output
