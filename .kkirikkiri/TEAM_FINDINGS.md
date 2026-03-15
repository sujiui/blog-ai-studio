# 발견 사항 & 공유 자료

## 프로젝트 컨텍스트 (사전 정보)
- 기존 프로젝트: blog-ai-studio (매주 월/수/금 블로그 자동 생성 파이프라인)
- 기존 구조: 기획팀 → 라이팅팀 → 크리에이티브 → 편집팀 (4 phase)
- 기존 이미지: Gemini 2.0 Flash로 생성
- 사용자 요구: 더 발전된 스킬/에이전트 형태로, 동적 스타일 프리셋 + 나노바나나 API 이미지 생성
- 핵심 차별점: 블로그 스타일 리서치 → 유형별 프리셋 → 동적 선택

---

## [리서처] 태스크 1: 기존 블로그 자동화 도구/서비스 분석

### 글로벌 주요 도구

| 도구 | 포지셔닝 | 핵심 기능 | 가격 | 강점 | 약점 |
|------|---------|----------|------|------|------|
| **Jasper AI** | B2B/엔터프라이즈 | Brand Voice, Content Pipelines, 100+ 에이전트 | $49/월~ | 브랜드 일관성, Surfer SEO 연동 | 반복적 콘텐츠, 프리미엄 가격 |
| **Copy.ai** | 소규모팀/솔로 | 90+ 템플릿, Brand Voice, 직관적 UI | 무료~$49 | 사용성, 가성비 | 장문 콘텐츠 약함 |
| **Writesonic** | SEO 중심 올인원 | 내장 SEO, 100+ 템플릿, 1000자/60초 | $20/월~ | 가성비 최고 | Brand Voice 정확도 낮음 |
| **RightBlogger** | 블로거 전용 | Content Planner→WordPress 자동 발행, autoblogging | - | 블로거 특화 | - |
| **Byword** | 프로그래매틱 SEO | CSV 키워드→배치 생성 | - | 대량 생성 | 스타일 커스터마이징 부족 |
| **Koala AI** | 원클릭 생성 | 키워드→SERP 분석→전체 글, 자동 이미지 | - | 간편함 | - |
| **StoryChief** | 올인원 CMP | AI William (전략+SEO+캠페인+소셜+비주얼) | - | 풀 파이프라인 | - |

### 국내 서비스

- **가제트 (gazet.ai)** — 30초 블로그 생성, 글+이미지+키워드 통합
- **알파블로그 (alphablogogo.com)** — ChatGPT/Gemini/Claude 3개 AI, SEO 대량 생성 (30개/회)
- **AI 스토리 플래너 (aistoryplanner.com)** — 트렌드 분석 + 키워드 지정 포스팅

### 2025-2026 트렌드

1. **에이전틱 AI** — 자율적 리서치→드래프트→최적화→배포 워크플로우 주류
2. **풀 파이프라인 자동화** — 데이터소스→AI에이전트→배포채널 end-to-end
3. **하이브리드 AI+인간** — 2.4x SEO 성과 (vs 순수 AI), 68% 시간 절약 (vs 인간만)
4. **브랜드 보이스 학습** — 기존 콘텐츠 분석 + 편집 피드백 루프
5. **60% 마케팅 팀** AI 워크플로우 사용 (2024년 35%→2025년 60%)

---

## [리서처] 태스크 2: 블로그 스타일 분석 방법론 + 프리셋 설계

### Nielsen Norman Group 4차원 톤 모델

1. 격식(Formal) ↔ 캐주얼(Casual)
2. 존중(Respectful) ↔ 파격(Irreverent)
3. 열정적(Enthusiastic) ↔ 사실적(Matter-of-fact)

### 톤 프리셋 카테고리 (8종)

- 격식/전문적 — 비즈니스, B2B
- 캐주얼/친근 — 라이프스타일
- 친절/따뜻한 — 건강, 자기계발
- 권위적 — 기술, 리뷰
- 유머러스 — 바이럴 콘텐츠
- 영감적 — 자기계발, 성공 사례
- 정보전달 — 튜토리얼, 가이드
- 스토리텔링 — 체험기, 케이스 스터디

### 글 구조 유형 (10종)

리스티클, 하우투, 비교, 리뷰, 큐레이션, 스토리텔링, 케이스 스터디, 의견, 뉴스, 궁극의 가이드

### 브랜드 보이스 프리셋 시스템 사례

- **Jasper**: 콘텐츠 업로드→AI 보이스 프로필 생성→자동 적용
- **Copy.ai**: 채널별 다른 톤/스타일/규칙 프리셋
- **Averi AI**: 편집 학습→Voice Guidelines 자동 생성→피드백 루프 (가장 발전된 패턴)

### 동적 프리셋 설계 패턴

1. 초기 설정: 기존 글→AI 톤/스타일/구조 분석
2. 프리셋 생성: 톤 축 값, 어휘 수준, 문장 길이 등 프로필 저장
3. 채널별 변형: 블로그/SNS/이메일별 미세 조정
4. 카테고리 매핑: 기술/건강/자기계발별 자동 매칭
5. 피드백 루프: 사용자 편집→학습→개선

---

## [리서처] 태스크 3: 나노바나나 API 및 이미지 전략

### 모델 라인업

| 모델 | ID | 속도 | 특징 | 가격/장 |
|------|-----|------|------|---------|
| Nano Banana (초기) | gemini-2.5-flash-image | 가장 빠름 | 대량생성, 저지연 | ~$0.039 |
| Nano Banana Pro | gemini-3-pro-image-preview | 10-20초 | 최고 품질, Thinking 추론 | $0.134~0.24 |
| **Nano Banana 2** | gemini-3.1-flash-image-preview | 4-8초 | Pro급+Flash속도, 4K, 웹검색 | $0.045~0.151 |

### Python SDK 사용법

```python
from google import genai
from PIL import Image
from io import BytesIO

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="Create an image of ...",
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    ),
)
for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("output.png")
```

### 이미지 배치 전략

- 1500-3000자 글: **5-10장** 권장 (200-300자당 1장)
- 썸네일/피처드: 최상단 Hero (SNS 미리보기, OG이미지)
- 인라인: 각 섹션 시작 (가독성, 체류시간)
- 다이어그램: 프로세스/비교 부분
- CTA 이미지: 글 하단

### 비용 추정

- 글당: $0.77 (공식) / $0.15-0.30 (서드파티)
- 월 12편: $9.24 (공식) / $1.80-3.60 (서드파티)
- **무료 티어: Google AI Studio 하루 50회 (월 ~1,500회) — 월 12편 충분히 커버**

---

## [전략가] Opportunity Solution Tree (OST)

**Desired Outcome:** 주제만 입력하면 스타일 매칭된 고품질 블로그 글 + 이미지가 10분 내 생성

| Opportunity | Score | 설명 |
|-------------|-------|------|
| 스타일 프리셋 부재 | 6.4 | 현재 단일 스타일만 지원, 주제별 최적 스타일 매칭 없음 |
| 리서치 품질 | 6.3 | 주제 리서치 깊이와 최신성이 글 품질을 좌우 |
| 이미지 불안정성 | 5.6 | Gemini 이미지 생성이 불안정, 스타일별 이미지 전략 없음 |
| 워크플로우 단절 | 3.6 | 기획→라이팅→이미지→편집 간 컨텍스트 전달 부족 |

각 기회별 솔루션:
- 스타일 프리셋: (A) 7종 기본 프리셋 + 자동 매칭, (B) URL 학습으로 커스텀 프리셋, (C) 사용자 피드백 루프
- 리서치 품질: (A) 멀티소스 리서치 에이전트, (B) 트렌딩 토픽 통합, (C) 팩트체크 에이전트
- 이미지: (A) 나노바나나 2 업그레이드, (B) 스타일별 이미지 전략 프리셋, (C) 레퍼런스 이미지 활용

---

## [전략가] Product Strategy Canvas

### 1. Vision
"주제를 던지면, 당신의 스타일로 완성된 블로그 글이 나온다 — 리서치부터 이미지까지"

### 2. Target Segments
- **Primary:** 바이브코더 & 1인 블로거 (Claude Code 생태계 사용자)
- **Secondary:** 소규모 콘텐츠 팀
- **NOT for:** 대규모 미디어, 영어 콘텐츠, 블로그 외 콘텐츠

### 3. Pain Points & Value
- 매번 같은 스타일로만 나옴 → 주제에 맞는 다양한 스타일
- 이미지 품질 불안정 → 나노바나나 2 + 스타일별 이미지 전략
- 주제 선정이 어려움 → 트렌딩 토픽 자동 추천

### 4. Value Propositions (JTBD)
- When 블로거가 주제를 떠올리면, they want 빠르게 고품질 글을 작성, so they can 일관된 발행 스케줄 유지
- When 주제 특성이 다르면, they want 자동으로 최적 스타일 매칭, so they can 독자 경험 극대화

### 5. Strategic Trade-offs (안 하는 것)
- SaaS가 아닌 Claude Code 스킬 (플랫폼 종속 수용)
- 블로그 특화 (범용 콘텐츠 X)
- 한국어 우선
- 이미지 API는 나노바나나 단일 (멀티 API X)

### 6. Key Metrics
- **North Star:** Auto-publish rate (수정 없이 발행된 글 비율)
- **Input Metrics:** 스타일 매칭 정확도, 리서치 소스 수, 이미지 생성 성공률
- **Health Metrics:** 글당 생성 시간, API 비용

### 7. Growth Engine
- 스타일 프리셋 축적 → 더 나은 매칭 → 더 높은 발행률
- 사용자 피드백 → 매칭 정확도 개선 → 만족도 증가

### 8. Core Capabilities
- **Build:** 파이프라인, 스타일 매칭, 프리셋 시스템
- **Buy/Partner:** 나노바나나(이미지), Claude(글 생성), 트렌드 소스 API

### 9. Defensibility
- 스타일 프리셋 축적 (사용할수록 풍부해짐)
- 파이프라인 노하우
- Claude Code 네이티브 통합

---

## [전략가] 스킬/에이전트 아키텍처 설계

### 파이프라인 흐름 (6 Phase)
```
Orchestrator
  → Phase 1: Research Agent (주제 리서치 + 트렌드)
  → Phase 2: Planning Agent (기획서 + 스타일 매칭)
  → Phase 3: Writing Agent (HTML 본문 작성)
  → Phase 4: Image Agent (나노바나나 이미지 생성/배치)
  → Phase 5: Editorial Agent (메타데이터 + 품질 검수)
  → Output (파일 저장 + Notion 동기화 + WordPress 발행)
```

### 기존 프로젝트와의 관계: Evolution (확장)
- **재사용:** notion_sync, publisher, dashboard, tracker
- **리팩토링:** pipeline.py → Orchestrator로 발전
- **교체:** Gemini 이미지 → 나노바나나 2
- **신규:** 스타일 프리셋, 자동 매칭, 트렌딩 토픽, URL 학습

### 스킬 진입점
- `.claude/commands/blog-write.md` — 메인 글 생성
- `.claude/commands/blog-analyze.md` — URL → 커스텀 프리셋 생성
- `.claude/commands/blog-preset.md` — 프리셋 관리

### 신규 모듈 구조
```
src/agents/         # 6개 에이전트 (research, planning, writing, image, editorial, orchestrator)
src/style/          # analyzer + preset_manager + matcher
config/presets/     # JSON 프리셋 파일
```

---

## [전략 보조] 스타일 자동 매칭 시스템 설계

### 1. 듀얼 모드 아키텍처
- **경로 A (직접 선택):** `--style howto_tutorial` → 바로 확정
- **경로 B (자동 매칭):** 키워드만 입력 → 3-Layer 분석 → 추천 + 신뢰도 → 사용자 확인

### 2. 기본 프리셋 7종

| ID | 이름 | 대표 사례 | 구조 | 이미지 |
|---|---|---|---|---|
| `howto_tutorial` | 하우투/튜토리얼형 | "파이썬 설치 방법" | 단계별 | 스크린샷 3-5장 |
| `list_curation` | 리스트/큐레이션형 | "제주도 카페 추천 10선" | 항목별 | 항목당 1장, 4-8장 |
| `analysis_explainer` | 분석/설명형 | "정부 정책 해설" | 논리적 | 차트/인포그래픽 2-3장 |
| `trend_intro` | 트렌드 소개형 (현재 기본) | "요즘 AI로 이런 것도" | 기존 5단계 | 2-4장 |
| `review_comparison` | 리뷰/비교형 | "ChatGPT vs Claude 비교" | 비교표 중심 | 제품샷 3-4장 |
| `story_experience` | 스토리/경험담형 | "퇴사 후 100일 회고" | 시간순 | 분위기샷 2-3장 |
| `problem_solution` | 문제 해결형 | "맥북 발열 해결법" | 증상→해결 | 비교샷 2-4장 |

### 3. 프리셋 데이터 구조 (6개 속성)

| 속성 | 내용 |
|---|---|
| `structure` | 섹션 흐름, 섹션 목록, min/max 섹션 수 |
| `tone` | voice, formality, sentence_style, avoid |
| `image_strategy` | count, types, placement, style_hint |
| `length` | min, max, ideal (글자 수) |
| `prompt_injection` | planning/writing용 LLM 지시문 |
| `match_signals` | keywords, intent_patterns, topic_affinity |

### 4. 자동 매칭 로직: 3-Layer 가중 합산

```
final_score = (키워드 매칭 * 0.2) + (LLM 의미 분석 * 0.6) + (카테고리 친화도 * 0.2)
```

- **Layer 1 (키워드, 0.2):** 프리셋별 `match_signals.keywords` 부분 문자열 매칭
- **Layer 2 (LLM, 0.6):** Claude CLI 1회 호출, 프리셋 요약 전달, top_match + confidence + reason 반환
- **Layer 3 (카테고리, 0.2):** `topic_affinity[category]` 값으로 보정

사용자에게: "추천 스타일: 하우투/튜토리얼형 (신뢰도 92%) — '파이썬 설치'는 단계별 따라하기가 필요한 주제라 튜토리얼형이 적합해요."

### 5. 피드백 루프
- `data/feedback_log.json`에 매 실행마다 기록 (keyword, recommended, user_accepted, user_selected)
- 50건+ 쌓이면 키워드별 오버라이드 테이블 자동 생성

### 6. 동적 확장
- **커스텀 프리셋:** base 프리셋 상속 + overrides로 부분 수정
- **URL 학습:** `--learn-style "URL"` → HTML 분석 → 자동 프리셋 생성

### 7. 신규 파일 구조
```
config/style_presets.py    # 7종 기본 프리셋
config/custom_presets.py   # 사용자 커스텀 프리셋
src/style_matcher.py       # 3-Layer 자동 매칭 엔진
src/style_registry.py      # 프리셋 로드/병합/검증
src/style_learner.py       # URL→프리셋 자동 생성
data/feedback_log.json     # 매칭 피드백 기록
```

### 8. 구현 우선순위
1. style_presets.py 7종 정의
2. style_registry.py
3. pipeline.py 프롬프트 주입
4. style_matcher.py Layer 1+2
5. main.py CLI 통합
6. 피드백 루프
7. custom_presets 상속
8. style_learner URL 분석

### 9. 하위호환
`style_id=None`이면 `trend_intro`(현재 기본 스타일)로 폴백. 기존 CLI 명령어 그대로 동작.

---

## [전략 보조 2] 자연어 주제 입력 + 트렌딩 토픽 추천 시스템

### 1. 자연어 주제 입력: Topic Interpreter (Phase 0)

새 모듈 `src/topic_interpreter.py`를 파이프라인 앞단에 추가:

```
사용자 자연어 입력 → [Phase 0: Topic Interpreter (Claude CLI 1회)] → TopicSpec → [사용자 확인] → 기존 Phase 1~6
```

#### TopicSpec 데이터 구조

```python
@dataclass
class TopicSpec:
    original_input: str       # 사용자 원본 ("두쫀쿠가 유행한다던데?")
    corrected_input: str      # 오타 교정 ("두족류가 유행한다던데?")
    core_topic: str           # 핵심 주제
    keywords: list            # SEO 키워드 3~5개
    category: str             # 카테고리 key (ai_tech, health, economy 등)
    intent: str               # inform/analyze/compare/howto/opinion
    style: str                # 자동 매칭된 스타일 ID
    search_queries: list      # 리서치용 검색 쿼리 (한국어 2 + 영어 1)
    confidence: float         # 해석 신뢰도 0.0~1.0
    reasoning: str            # 해석 근거
```

#### 카테고리 확장

기존 3개 유지 + 동적 카테고리:
- `economy` (경제/시사), `lifestyle` (라이프스타일/트렌드), `science` (과학/자연), `culture` (문화/엔터)
- 요일 스케줄은 기존 3개만, 사용자 직접 입력 시 동적 카테고리 가능

#### 검색 폴백 로직 (핵심 추가사항)

LLM 자체 지식으로 해석 불가한 신조어/줄임말/트렌드어 대응:

```
Step 1: Claude CLI로 1차 해석 시도
Step 2: confidence < 0.7 또는 "모르겠음" 판정 시
  → 네이버 검색 + 구글 검색 수행 (WebSearch)
  → 검색 결과에서 실제 의미 파악
Step 3: 검색 결과 기반으로 TopicSpec 재생성
```

예시:
- "두쫀쿠가 유행한다던데?" → LLM 모름 → 검색 → "두바이 쫀득 쿠키" 발견
  → core_topic: "두바이 쫀득 쿠키 유행", category: "lifestyle", style: "trend_intro"
- "챗지피티 쓰까" → LLM 해석 가능 → "ChatGPT 사용법", style: "howto_tutorial"

구현: `topic_interpreter.py`에서 confidence 기반 분기 → `WebSearch` 도구 호출 → 검색 결과를 Claude CLI에 재전달

#### 사용자 확인 UX

- confidence >= 0.8: "이렇게 이해했어요: [주제]. 맞으면 Enter"
- confidence 0.5~0.8: 위 + "혹시 다른 뜻이셨나요?" 대안 제시
- confidence < 0.5: 검색 폴백 실행 후 결과 제시, 여전히 불확실하면 "좀 더 구체적으로 알려주실래요?"

#### main.py 하위 호환

```python
# 입력 판별: 없음 → 요일 자동 | TOPICS key → 기존 | 그 외 → Topic Interpreter
```

### 2. 트렌딩 토픽 자동 추천: `src/trend_collector.py`

#### 소스별 전략

| 소스 | 방법 | API 키 | 가중치 |
|------|------|--------|--------|
| Google Trends | pytrends | 불필요 | 1.0 |
| 네이버 DataLab | REST API | 필요 | 1.0 |
| 뉴스 RSS | feedparser (조선IT, 전자신문, ZDNet, 블로터, AI타임스) | 불필요 | 0.7 |
| YouTube | Data API v3 | 필요 | 0.8 |
| Reddit/HN | JSON API | 불필요 | 0.6/0.5 |
| Twitter/X | 유료 ($100/월+) | - | **제외** |

#### 키워드 처리

- 유사 키워드 그룹핑 (LLM: "ChatGPT"/"챗GPT"/"챗지피티" 병합)
- 멀티소스 가중치 점수
- 카테고리별 필터링 → 상위 N개 → Claude CLI로 블로그 주제 변환
- 캐싱: 6시간 TTL, `cache/trends/` 디렉토리

### 3. 통합 CLI

```bash
python -m src.main                                    # 요일 자동 (기존)
python -m src.main ai_tech "Claude Code"              # 카테고리+키워드 (기존)
python -m src.main "두족류가 유행한다던데?"              # 자연어 (신규)
python -m src.main --trending                         # 트렌드 추천 (신규)
python -m src.main --trending --category ai_tech      # 카테고리별 트렌드 (신규)
```

### 4. 구현 우선순위

- **Phase A (MVP):** topic_interpreter.py + main.py 수정 + 카테고리 확장
- **Phase B (트렌드):** trend_collector.py (RSS+Reddit/HN 우선) → Google Trends → YouTube
- **Phase C (고도화):** 멀티소스 집계 + 캐싱 + 대시보드 트렌드 UI
- **새 패키지:** `pytrends>=4.9.0`, `feedparser>=6.0.0`, `google-api-python-client` (선택)

---

## [보조 리서처] 블로그 레퍼런스 수집 및 스타일 분석

### 실제 분석 완료 (WebFetch) - 3건

| 블로그 | URL | 톤 | 길이 | 이미지 | 구조 |
|--------|-----|-----|------|--------|------|
| Velog "AI 시대의 개발자" | velog.io/@teo/ai-and-developer | 존댓말+대화체 | 15,000자+ 초롱폼 | 40개+ | 에세이+논설문 |
| Velog "CES 2026 LLM 트렌드" | velog.io/@jejeong000/article01 | 전문가 톤 | 1,200자 숏폼 | 0개 | 리서치 요약 |
| GeekNews "2026 기술 트렌드" | news.hada.io/topic?id=26329 | 리포트 톤 | 15,000~18,000자 | 0개 | 주제별 분석 |

### 스타일 분류 체계

#### 구조 유형 (9종)

리스티클, 튜토리얼, 스토리텔링, 큐레이션, Q&A, 비교분석, 리서치 요약, 에세이, 트렌드 소개

#### 톤 유형 (6종)

전문가형, 친구형, 선생님형, 리포터형, 에세이형, **편안한 존댓말형**

#### 이미지 패턴 (5종)

- 텍스트 중심 (0~2장)
- 균형형 (3~7장)
- 이미지 풍부 (10~20장)
- 인포그래픽형 (5~10장)
- 밈/캡처형 (10~40장)

#### 길이 유형 (4종)

숏폼 (~1,500자), 미디엄 (2,000~4,000자), 롱폼 (5,000~10,000자), 초롱폼 (10,000자+)

### 카테고리별 권장 프리셋

| 카테고리 | 구조 | 톤 | 이미지 | 길이 |
|---------|------|-----|--------|------|
| **AI/기술** | 큐레이션 | 편안한 존댓말/리포터 | 균형형 3~5장 | 미디엄 2,500~3,500자 |
| **건강** | 리스티클/Q&A | 선생님/존댓말 | 균형~풍부 5~8장 | 미디엄 2,000~3,000자 |
| **자기계발** | 에세이/스토리텔링 | 에세이/존댓말 | 감성 2~4장 | 미디엄 2,000~3,000자 |

### 핵심 인사이트

1. 한국 블로그 톤 표준 = **"편안한 존댓말"** → 현재 Blog AI Studio 설정 적절
2. 이미지 밀도는 카테고리별로 다름 (기술=텍스트 중심, 건강=풍부, 자기계발=소수 감성)
3. **미디엄 (2,000~3,000자)이 범용 최적 길이** → 현재 설정 유지 권장
4. 프리셋은 카테고리 1:1 매핑보다 키워드/주제 기반 동적 선택이 필요

### 네이버 블로그 Playwright 스크래핑 전략

모바일 URL(`m.blog.naver.com`)로 변환 → headless Chromium → `.se-main-container` 셀렉터로 본문 추출. 코드 설계 완료.

### 접근 실패 사이트 (DEAD_ENDS 참조)

brunch.co.kr, yozm.wishket.com, toss.tech (WebFetch 거부), blog.naver.com (JS 렌더링 필요)

---

# DEAD_ENDS (시도했으나 실패한 접근)

- 이미지 분석 에이전트: WebFetch 권한 문제로 실제 블로그 이미지 크롤링 실패 → 전문 지식 기반 분석으로 전환
- 전략가/전략 보조: 파일 쓰기 권한 문제 → 메인 세션에서 대리 기록
- 보조 리서처: brunch.co.kr, yozm.wishket.com, toss.tech WebFetch 거부 → Velog/GeekNews 중심 분석
- 보조 리서처: blog.naver.com JS 렌더링 필요 → Playwright 스크래핑 전략 설계로 대체
