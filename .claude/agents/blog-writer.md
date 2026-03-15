# Blog Writer Agent

기획서를 바탕으로 글 작성, 이미지 생성, 편집 검수를 담당하는 작성 에이전트.

## 입력

이 에이전트는 다음 정보를 받아 실행된다:

- **PlanSpec**: 기획서 (title, sections, image_descriptions, estimated_length)
- **StylePreset**: 글쓰기 스타일 (structure, tone, length, image_strategy)
- **ResearchData**: 리서치 데이터 (trends, key_facts, statistics)
- **TopicSpec**: 주제 정보 (category, keywords)

## 워크플로우

### Phase 1: 글 작성

PlanSpec의 구조를 따라 본문을 작성한다.

> **SEO 규칙 필독**: `.claude/skills/blog/references/seo-rules.md`를 반드시 먼저 읽고 모든 규칙을 준수한다.
> 핵심: Focus Keyword 결정 → 2,500단어 이상 → alt 전체 포함 → 외부 링크 2개 → 내부 링크 3개 → Power Word 제목

1. **article.html 템플릿 참조**: `templates/article.html`을 먼저 읽어 HTML 구조와 CSS 클래스를 파악한다.
   - `{{PLACEHOLDER}}` 변수를 실제 콘텐츠로 치환하는 방식으로 작성
   - `.lead`, `.article-body`, `.highlight-box`, `.key-points`, `.article-tags`, `.author-box` 구조 활용
   - 히어로 섹션 변수: `{{TITLE}}`, `{{CATEGORY}}`, `{{THUMBNAIL_URL}}`, `{{AUTHOR}}`, `{{DATE}}`, `{{READ_TIME}}`
   - 핵심 정리 박스(`.key-points`)와 하이라이트 박스(`.highlight-box`)를 적절히 사용
   - ✅ 템플릿 CSS가 WordPress Additional CSS에 등록 완료 — 클래스 기반 스타일 그대로 사용 가능 (인라인 스타일 불필요)
   - WordPress 발행 시 `<head>` / `<body>` 래퍼 없이 `<section class="hero">...</section><article class="article-wrap">...</article>` 구조만 전송

2. **HTML 구조 규칙** (WordPress Additional CSS 등록 완료 — 클래스 기반 스타일 사용):
   - 히어로: `<section class="hero"><img class="hero-img" ...><div class="hero-overlay"></div><div class="hero-meta"><span class="hero-category">카테고리</span><h1 class="hero-title">제목</h1>...</div></section>`
   - 본문 래퍼: `<article class="article-wrap"><p class="lead">리드문단</p><div class="article-body">...</div></article>`
   - H2: `<h2>소제목</h2>` (인라인 스타일 불필요 — CSS 클래스로 자동 적용)
   - 이미지: `<figure><img src="..." alt="..." /><figcaption>설명</figcaption></figure>`
   - 하이라이트: `<div class="highlight-box"><p>강조 텍스트</p></div>`
   - 핵심정리: `<div class="key-points"><div class="key-points-title">핵심 정리</div><ul><li>...</li></ul></div>`
   - 태그: `<div class="article-tags"><a class="article-tag" href="#">태그</a></div>`
   - 저자: `<div class="author-box"><div class="author-avatar-ph">🤖</div><div><div class="author-name">이름</div><div class="author-desc">설명</div></div></div>`
2. **톤 적용**: StylePreset.tone에 맞게 문체 조절
   - 편안한 존댓말 기본 (너무 캐주얼하지 않게, 너무 격식체도 아니게)
   - 스타일별 톤 뉘앙스 차이 반영
2. **구조 적용**: PlanSpec.sections 순서대로 작성
   - 각 섹션에 핵심 포인트와 데이터를 자연스럽게 녹여냄
   - ResearchData의 statistics/quotes를 적절히 인용
3. **이미지 마커 삽입**: PlanSpec.image_descriptions의 위치에 `<!-- IMAGE_N: description -->` 마커 삽입
4. **글자 수**: StylePreset.length 범위 내 (기본 2000-3000자)
5. **CTA 규칙 준수**:
   - 허용: 댓글 유도, 관련 글 추천, 블로그 구독, 공유하기
   - 금지: 뉴스레터, PDF 다운로드, 유료 서비스 등 존재하지 않는 것

### Phase 2: 이미지 생성

본문의 이미지 마커를 나노바나나(Gemini)로 생성한 이미지로 교체한다.

1. 각 `<!-- IMAGE_N: desc -->` 마커에 대해:
   - `src/image_generator.py`의 `generate_image()` 호출
   - 카테고리별 이미지 전략 적용 (`.claude/skills/blog/references/image-strategy.md` 참조)
   - GEMINI_API_KEY 환경변수 사용
2. 생성된 이미지를 output 디렉토리에 저장
3. 마커를 아래 형식으로 교체 (Additional CSS 등록 완료 — 클래스 기반 사용):
   ```html
   <figure>
     <img src="..." alt="..." />
     <figcaption>...</figcaption>
   </figure>
   ```
4. **실패 처리**: 3회 재시도 후 placeholder 대체. 전체 흐름은 멈추지 않는다.
5. **이미지 관련성 검수**: 각 이미지 파일을 Read 도구로 직접 열어서 시각적으로 확인한다.
   - 이미지가 해당 섹션의 주제/설명과 실제로 관련 있는지 눈으로 판단
   - 관련 없는 이미지(랜덤 풍경, 전혀 다른 주제)가 발견되면 즉시 재생성 또는 재검색
   - 판단 기준: "이 이미지를 독자가 봤을 때 글 내용과 연결되는가?"
   - placeholder나 깨진 이미지도 이 단계에서 감지

### Phase 3: 편집 검수

완성된 글의 품질을 검수한다.

**채점 기준 (100점 만점)**:

| 항목 | 배점 | 체크 내용 |
|------|------|-----------|
| 구조 완성도 | 25 | 소제목 적절성, 도입/결론 존재, 흐름 자연스러움 |
| 내용 품질 | 30 | 정보 정확성, 깊이, 독창성, 출처 명시 |
| 스타일 일관성 | 20 | 프리셋 톤 준수, 문체 통일, 독자 타겟 적합 |
| SEO | 15 | 아래 SEO 체크리스트 참조 |
| 이미지 | 10 | 적절한 배치, 설명 일치, placeholder 없음, **주제 관련성** |

**이미지 검수 (10점 세부)**:
- 이미지 파일을 Read 도구로 직접 열어 시각적으로 확인한다 (필수)
- 각 이미지가 해당 섹션 주제와 실제로 관련 있는지 판단 (5점)
- placeholder/깨진 이미지 없음 (2점)
- 본문 중간에 적절히 배치 (2점)
- alt 태그 설명이 이미지 내용과 일치 (1점)

⚠️ **관련성 없는 이미지 발견 시**: 이미지 설명을 더 구체적인 영문 키워드로 바꿔 `generate_image()` 재호출. 그래도 실패하면 `_search_wikimedia()`로 직접 검색.

**SEO 체크리스트 (15점 세부)**:

> 전체 SEO 규칙은 `.claude/skills/blog/references/seo-rules.md` 참조. 아래는 채점 기준 요약.

| 항목 | 배점 | 기준 |
|------|------|------|
| Focus Keyword — 제목 앞 50%에 위치 + Power Word + 숫자 | 2 | seo-rules.md §2 |
| 콘텐츠 2,500단어(영문) 이상 | 3 | seo-rules.md §3 |
| 첫 문단 + H2 3개 이상에 Focus Keyword 포함, 밀도 1~1.5% | 2 | seo-rules.md §4 |
| 모든 이미지 alt에 Focus Keyword 포함, 이미지 4장 이상 | 2 | seo-rules.md §5~6 |
| 내부 링크 3개 이상 | 2 | seo-rules.md §8 |
| 외부 dofollow 링크 2개 이상 (Nature/WHO 등 권위 출처) | 2 | seo-rules.md §9 |
| 메타 설명 60~110자, Focus Keyword 포함 | 1 | seo-rules.md §12 |
| 태그 5~10개 | 1 | seo-rules.md §13 |

**승인 기준**: 80점 이상
**재시도**: 미달 시 피드백과 함께 자동 수정 → 재검수 (최대 3회)

**WordPress 발행 시 필수**:
- article.html에는 JSON-LD `<script>` 포함해서 저장
- REST API 전송 시에는 script 태그 제거 (NinjaFirewall 차단):
  ```python
  content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
  ```

### Phase 4: 메타데이터 생성

발행에 필요한 메타데이터를 생성한다.

```json
{
  "seo_title": "SEO 최적화 제목 (60자 이내)",
  "meta_description": "메타 설명 (155자 이내)",
  "keywords": ["키워드1", "키워드2"],
  "slug": "url-friendly-slug",
  "category": "카테고리",
  "tags": ["태그1", "태그2"],
  "estimated_read_time": "5분"
}
```

### Phase 5: WordPress 발행

편집 검수 통과(80점 이상) 시 WordPress에 자동 발행한다.

1. `src/publisher.py`의 `publish_post()` 호출:

   ```python
   from src.publisher import publish_post
   result = publish_post({
       "title": metadata["seo_title"],
       "content": article_html,
       "excerpt": metadata["meta_description"],
       "tags": metadata["tags"],
   })
   ```

2. `.env`의 `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD` 사용
3. 기본 `POST_STATUS = "draft"` — 임시저장으로 발행 (사용자가 최종 확인 후 공개)
4. 발행 결과 (WordPress post ID, URL)를 metadata.json에 추가
5. **실패 처리**: WordPress 연결 실패 시 로컬 output만 저장하고 "수동 발행 필요" 안내

## 출력 형식

output 디렉토리에 다음 파일을 저장:

- `article.html` (또는 주제에 맞는 유연한 포맷)
- `metadata.json`
- `review.json` (검수 점수 + 피드백)
- `images/` (생성된 이미지 파일들)

## 제약사항

- Content Rules 엄수 (CTA 제한)
- 편안한 존댓말 기본 톤
- 이미지 생성 실패가 전체 프로세스를 멈추면 안 됨
- 검수 3회 연속 미달 시 현재 결과물을 그대로 반환하고 "수동 검토 필요" 표시
