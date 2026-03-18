# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Blog AI Studio - 블로그 글을 자동 생성하는 AI 파이프라인. Claude Code CLI(Max 구독)를 AI 엔진으로 사용하며, WordPress로 발행한다.

- 콘텐츠 스타일: 7종 스타일 프리셋 자동 매칭 (주제에 따라 유연하게)
- 톤: 편안한 존댓말 (너무 캐주얼하지 않게, 너무 격식체도 아니게)

## Commands

```bash
# 성과 추적 (발행 후) — output/tracker.json에 로컬 저장
python -m src.tracker register <content_id> <wordpress_url>   # 글 등록
python -m src.tracker collect                                  # 조회수/댓글 수집
python -m src.tracker status [content_id]                      # 현황 확인
```

## Architecture

### Skill+Agent 시스템

```text
# 스킬 / 에이전트 정의
.claude/skills/blog/SKILL.md            → /blog 스킬 오케스트레이터 (8단계 워크플로우)
.claude/skills/diary/SKILL.md           → /diary 스킬 (Claude 1인칭 회고 일기, 미니/돌쇠 캐릭터)
.claude/agents/blog-researcher.md       → 리서치 에이전트 (트렌드 수집 + 기획서 생성)
.claude/agents/blog-writer.md           → 작성 에이전트 (글 작성 + 이미지 + 검수 + 발행)
.claude/skills/blog/references/         → 스타일 프리셋·이미지 전략 참조 문서

# 핵심 모듈 (스킬/에이전트가 직접 호출)
src/topic_interpreter.py   → 자연어 주제 입력 → TopicSpec 구조체 변환 (신뢰도 낮으면 웹 검색 폴백)
src/style_matcher.py       → TopicSpec 기반 최적 글쓰기 스타일 매칭 (3-Layer 가중 점수)
src/trend_collector.py     → 다중 소스 트렌드 수집 (Google/YouTube/Naver/RSS/WebSearch)
src/image_generator.py     → Gemini로 본문·썸네일 이미지 생성 (실패 시 구글 이미지 검색 폴백)
src/publisher.py           → WordPress REST API 발행 + 본문 이미지 자동 미디어 업로드
src/tracker.py             → 발행 후 1/2/3주차 조회수·댓글 수집 및 성과 등급 산정

# 설정
config/style_presets.py    → 7종 글쓰기 스타일 프리셋 정의 (구조·톤·길이·이미지 전략)
config/settings.py         → WordPress 접속 정보, 글 설정 (POST_STATUS 등)

```

### Templates

```text
templates/article.html          → 블로그 글 생성 템플릿 ({{PLACEHOLDER}} 변수 방식)
templates/node-archive-widget.html → WordPress Custom HTML 블록에 삽입 (메인 페이지 위젯)
templates/card-grid.html        → 독립형 카드 그리드 페이지 (card-grid.css 외부 참조)
templates/card-grid.css         → 카드 그리드 스타일 (사이드바, 검색, 반응형 포함)
```

**article.html 워크플로우**:
- blog-writer Agent가 `{{PLACEHOLDER}}` 변수를 실제 콘텐츠로 치환하여 `output/{date}_{topic}/article.html` 생성
- `publisher.py`가 생성된 HTML을 WordPress REST API로 발행 — Elementor에 올리지 않음
- CSS는 WordPress Admin → Appearance → Additional CSS에 붙여넣기하거나 인라인 스타일로 유지
- WordPress는 `<script>` 태그를 NinjaFirewall이 차단하므로 REST API 전송 전 제거 필수

**node-archive-widget.html**:
- 단일 파일에 HTML+CSS+JS 모두 포함 (외부 파일 참조 없음)
- WordPress Elementor → Custom HTML 블록에 직접 붙여넣기
- 전체 너비 구현: `width: 100vw; margin-left: calc(50% - 50vw)` (Elementor 컨테이너 탈출)

### /blog 워크플로우 (8단계)

```text
Step 1: 주제 선택 (자연어 입력 또는 트렌드 추천)
Step 2: 스타일 매칭 (7종 프리셋 자동 추천)
Step 3: 트렌드 수집 + 리서치 (blog-researcher Agent)
  → SEO 보강 리서치: 연관 검색어 조사 → 추가 섹션 제안
Step 4: 기획서 생성 (사용자 확인 체크포인트)
Step 5: 글 작성 (blog-writer Agent)
Step 6: 이미지 생성 (Gemini → Unsplash CDN 폴백) + 시각적 관련성 검수
Step 7: 편집 검수 + SEO (RankMath 100점 기준, 80점 이상 승인)
Step 8: WordPress 발행 (이미지 미디어 업로드 + draft 모드)
```

## Critical Patterns

### Claude CLI subprocess 호출

모든 Claude CLI 호출은 `CLAUDECODE` 환경변수를 제거해야 중첩 세션 에러를 피할 수 있다:

```python
env = {**os.environ}
env.pop("CLAUDECODE", None)
subprocess.run(["claude", "-p", prompt, "--output-format", "json"],
               capture_output=True, text=True, timeout=300, env=env)
```

### JSON 파싱

Claude CLI `--output-format json` 응답은 `{"result": "..."}` wrapper 안에 markdown code block으로 올 수 있다. `_parse_json_output()` / `_parse_output()`이 wrapper 해제 → code block 추출 → JSON 파싱 순으로 처리한다.

### 이미지 생성 (Gemini)

`google.genai` 라이브러리 (NOT deprecated `google.generativeai`) 사용. python3 subprocess로 호출:
- 본문: `gemini-3.1-flash-image-preview` (Nano Banana 2)
- 썸네일: `gemini-3-pro-image-preview` (Nano Banana Pro)
- 폴백: `gemini-2.5-flash-image`
- 최종 폴백: Claude CLI WebSearch (Pexels/Pixabay) → Wikimedia Commons API (무료, 주제 관련성 높음)
- `source.unsplash.com`은 deprecated — 사용 금지 (HTML 반환, 이미지 아님)
- 인포그래픽/차트/다이어그램은 AI 티가 나므로 절대 생성하지 않는다
- **이미지 관련성 검수**: blog-writer agent가 Read 도구로 이미지 파일을 직접 열어 주제 관련성을 시각적으로 확인. 무관한 이미지 발견 시 즉시 재생성 또는 Wikimedia 재검색.

### WordPress 인라인 스타일 필수

WordPress는 포스트 콘텐츠 내 `<style>` 블록이나 클래스 기반 CSS를 무시한다. 아래 요소들은 반드시 인라인 스타일을 적용해야 렌더링된다:

```html
<!-- article-tags -->
<div class="article-tags" style="display:flex;flex-wrap:wrap;gap:8px;margin:48px 0 40px;padding-top:32px;border-top:1px solid #e5e5e5;">
  <a class="article-tag" href="#" style="display:inline-block;font-size:12.5px;font-weight:600;color:#7c3aed;background:#ede9fe;padding:5px 12px;border-radius:999px;text-decoration:none;">태그명</a>
</div>

<!-- highlight-box -->
<div class="highlight-box" style="background:#111;color:#fff;padding:24px 28px;border-radius:12px;">
  <p style="color:#eee;font-size:1rem;font-weight:500;line-height:1.8;margin:0;">텍스트</p>
</div>
```

기존 발행 글에 일괄 적용할 경우 WP REST API `?context=edit`으로 raw 콘텐츠를 가져와 regex로 교체 후 재발행한다.

### WordPress 발행 + 미디어 업로드

`src/publisher.py`가 글 발행과 이미지 업로드를 모두 처리한다:

- `publish_post()`: 본문의 로컬 이미지를 자동으로 WordPress 미디어에 업로드하고 URL 교체 후 발행
- `upload_media()`: 개별 이미지 업로드 (alt text 설정 포함)
- `images_dir` 옵션: 여행 사진 등 폴더 통째로 업로드
- `thumbnail_path` 옵션: 대표 이미지(featured image) 설정
- 기본 `POST_STATUS = "draft"` — 사용자 확인 후 공개 전환

### Python 호환성

로컬 환경이 Python 3.9.6이므로 `str | None` 대신 `Optional[str]`, `list[str]` 대신 `list` 사용.

## Environment Variables

`.env` 파일에 설정:

- `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD` — WordPress REST API 인증
- `GEMINI_API_KEY` — 이미지 생성 (google.genai)

## WordPress

**사이트**: node-archive.kr

### 카테고리 ID

| slug | ID | 사이드바 그룹 |
|------|----|--------------|
| ai-tools | 50 | ⚡ AI 활용 |
| ai-concept | 51 | 🧠 AI 지식 |
| vibe-coding | 52 | 🧠 AI 지식 |
| ai-usage | 53 | ⚡ AI 활용 |
| review | 54 | 📝 리뷰·체험 |
| productivity | 55 | ⚡ AI 활용 |
| ai-research | 56 | 🧠 AI 지식 |
| insight | 57 | 💡 인사이트 |
| essay | 58 | ✍️ 에세이·관심사 |
| ai-diary | 66 | 📔 AI 일기 |

### publish_post() 주요 파라미터

```python
from src.publisher import publish_post

publish_post({
    "title": "...",
    "content": article_html,       # script 태그 제거 후 전달
    "excerpt": "메타 설명 (80~130자, Focus Keyword 포함)",
    "tags": ["태그1", "태그2"],
    "category_ids": [57],          # 위 ID 표 참조
    "thumbnail_path": "path/to/thumbnail.png",
    "images_dir": "path/to/images/",  # 본문 로컬 이미지 일괄 업로드
})
# 반환: {"id": WP_ID, "link": "...", "status": "draft", "uploaded_images": [...]}
```

글 상태 변경 (draft → publish):
```python
import requests
from requests.auth import HTTPBasicAuth
from config.settings import WP_URL, WP_USERNAME, WP_APP_PASSWORD

requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{WP_ID}",
              json={"status": "publish"},
              auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD))
```

## Content Strategy

**블로그 포지셔닝**: AI가 메인 주제. 트렌드 분석부터 실생활 적용까지 다양한 각도로 접근.

### 콘텐츠 기둥 (Content Pillars)

현재 6개 기둥 운영. SEO 전략에 따라 추가 가능.

| 기둥 | 설명 | 예시 주제 |
|------|------|----------|
| **AI × 산업** | AI가 각 분야를 어떻게 바꾸는지 | AI 신약개발, AI 법률 자동화, AI 교육 혁신 |
| **AI 활용법** | 실제 써보고 정리하는 실용 가이드 | ChatGPT로 업무 자동화, Claude 프롬프트 팁 |
| **AI 트렌드** | 최신 AI 모델·기업·정책 동향 분석 | GPT-5 정리, 오픈소스 AI 동향, AI 규제 |
| **AI × 실생활** | 일상 문제에 AI 적용 | ADHD 루틴 자동화, AI 수면 분석, 생산성 |
| **AI × 커리어** | AI 시대 직업·업무 변화 | AI가 바꾸는 직업, 프롬프트로 연봉 올리기 |
| **AI 도구 리뷰** | AI 앱 비교·추천 | ChatGPT vs Claude, 무료 AI 이미지 도구 5선 |

### SEO 전략 원칙

- 도메인 주제 일관성: 모든 글에 "AI"가 중심축
- 교차점 공략: "AI × [니치]" 형태가 경쟁 대비 노출 유리
- 기둥 추가 기준: AI와 명확히 연결되고, 검색 의도가 구체적인 주제

## Content Rules

- CTA에 존재하지 않는 서비스(뉴스레터, PDF 등)를 절대 언급하지 않는다
- 허용 CTA: 댓글 유도, 관련 글 추천, 블로그 구독, 공유하기
- 톤: 편안한 존댓말 (너무 캐주얼하지 않게, 너무 격식체도 아니게)

## Style Presets (7종)

정보전달형, 리뷰체험형, 에세이감성형, 리스트큐레이션형, 전문가분석형, 친근한대화형, 튜토리얼형 — `config/style_presets.py` 및 `.claude/skills/blog/references/style-presets.md` 참조.
