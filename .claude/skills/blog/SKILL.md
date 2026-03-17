---
name: blog
description: This skill should be used when the user asks to "블로그 글 써줘", "블로그 작성", "blog write", "글 자동 작성", "블로그 포스팅", "/blog", "주제로 글 써줘", "트렌드 글 써줘", "리서치해서 글 써줘". Use this skill whenever the user wants to create a blog post, write an article on a topic, or generate blog content — even if they phrase it casually like "두쫀쿠 글 써줘" or "AI 트렌드 정리해줘". This skill orchestrates research, planning, writing, image generation, and editorial review to produce publish-ready blog posts.
---

# Blog Auto-Writer

> 주제 하나만 던지면 리서치부터 이미지까지 — 발행 가능한 블로그 글을 자동 생성합니다.

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

이 문서는 실행 지시서다. 워크플로우를 즉시 시작한다.

---

## 워크플로우

### Step 1: 주제 선택 + 토픽 해석
**타입**: prompt + api_mcp

주제를 입력받거나, 트렌드 분석으로 주제를 추천한다.

**경로 A — 사용자가 주제를 직접 입력한 경우** (`/blog 두쫀쿠가 유행한다던데?`):
1. `src/topic_interpreter.py`의 로직을 따라 자연어를 파싱한다
2. LLM 신뢰도(confidence) 계산
3. **신뢰도 < 0.7이면 웹 검색 폴백**: WebSearch 도구로 입력어를 검색하여 실제 의미를 파악
   - "두쫀쿠" → 검색 → "두바이 쫀득 쿠키" 확인

**경로 B — 주제 없이 `/blog`만 입력한 경우**:
1. **트렌드 분석**으로 주제를 자동 추천한다:
   - Google Trends: 실시간 인기 검색어
   - YouTube Trends: 인기 급상승 동영상 주제
   - 네이버 블로그: 인기 키워드/주제
   - News RSS: 최신 화제 뉴스
2. 수집된 트렌드에서 블로그 주제로 적합한 5개를 선별
3. AskUserQuestion으로 추천 주제를 보여준다:
   - "이런 주제는 어때요?" + 추천 5개 목록
   - 사용자가 선택하거나, "Other"로 직접 입력

**카테고리**: 고정하지 않는다. 주제 특성에 따라 자동 판별되되, 어떤 주제든 자유롭게 가능.

**출력**: TopicSpec (core_topic, keywords, category, intent, confidence)

---

### Step 2: 스타일 매칭
**타입**: prompt + rag

TopicSpec의 특성에 맞는 글쓰기 스타일을 자동 추천한다.

1. `references/style-presets.md`에서 7종 프리셋을 로드한다.
2. 3-Layer 매칭 수행:
   - **keyword score (0.2)**: TopicSpec.keywords와 프리셋 match_signals 비교
   - **LLM analysis (0.6)**: 주제 특성(intent, 복잡도)을 분석하여 적합도 판단
   - **category affinity (0.2)**: 카테고리별 선호 스타일 가중치 (`config/style_presets.py` 참조)
3. `final_score = keyword(0.2) + llm(0.6) + category(0.2)` — 최고점 프리셋 1개를 추천한다.
4. 사용자에게 추천 결과를 보여주고 AskUserQuestion으로 확인:
   - "트렌드 소개형 (추천)" / "다른 스타일 선택" / "자동으로 진행"

**출력**: 선택된 StylePreset (structure, tone, length, image_strategy)

---

### Step 3: 트렌드 수집 + 리서치
**타입**: api_mcp + script

**blog-researcher Agent를 스폰**하여 리서치를 수행한다.

Agent 프롬프트에 포함할 내용:
- TopicSpec (Step 1 결과)
- StylePreset (Step 2 결과)
- `src/trend_collector.py`의 수집 로직 참조
- 트렌드 소스: Google Trends(pytrends), News RSS(feedparser), YouTube, Naver DataLab
- 웹 검색으로 최신 정보 보강

**실패 처리**: 트렌드 소스 2개 이상 성공해야 진행. 전멸 시 사용자에게 키워드 직접 입력 요청.

**출력**: ResearchData (trends, sources, key_facts, statistics)

---

### Step 4: 기획서 생성
**타입**: prompt

blog-researcher Agent가 리서치 결과를 바탕으로 기획서를 생성한다.

기획서 포함 내용:
- 제목 (SEO 최적화)
- 소제목 구성 (스타일 프리셋의 structure 따름)
- 섹션별 핵심 포인트
- 이미지 설명 (2-4장, 각 위치와 설명)
- 예상 글자 수

**체크포인트**: 기획서를 사용자에게 보여주고 AskUserQuestion 호출:
- "이대로 진행 (추천)" / "수정할 부분 있어" / "주제 바꿀래"

**출력**: PlanSpec (title, sections, image_descriptions, estimated_length)

---

### Step 5: 글 작성
**타입**: prompt

**blog-writer Agent를 스폰**하여 글을 작성한다.

Agent 프롬프트에 포함할 내용:
- PlanSpec (Step 4 결과)
- StylePreset (Step 2 결과)
- ResearchData (Step 3 결과)
- 톤/구조 지침 (`references/style-presets.md` 해당 프리셋)
- Content Rules: CTA 제한사항 (허용: 댓글 유도, 관련 글 추천, 구독, 공유)
- `<!-- IMAGE_N: description -->` 마커를 본문에 삽입

**출력**: 본문 텍스트 (HTML 또는 Markdown, 주제에 따라 유연하게) + 이미지 마커

---

### Step 6: 이미지 생성
**타입**: script

blog-writer Agent가 나노바나나(Gemini)로 이미지를 생성한다.

1. `src/image_generator.py`와 `references/image-strategy.md`를 참조한다.
2. 본문의 `<!-- IMAGE_N: desc -->` 마커별로 이미지 생성:
   - 1차: Nano Banana 2 (`gemini-3.1-flash-image-preview`) — 본문 이미지
   - 2차 폴백: `gemini-2.5-flash-image` — 안정성 높은 모델
   - 3차 폴백: 구글에서 관련 이미지 검색 (Unsplash/Pexels/Pixabay)
   - 썸네일: Nano Banana Pro (`gemini-3-pro-image-preview`)
3. **스타일별 이미지 전략 적용** — 인포그래픽/차트/다이어그램은 AI 티가 나므로 절대 생성하지 않는다. 자연스러운 일러스트/사진 스타일 위주.
4. 생성된 이미지를 output 디렉토리에 저장
5. 본문의 마커를 `<figure>` 태그로 교체

**실패 처리**: Gemini 실패 → Unsplash CDN 직접 다운로드 (`https://images.unsplash.com/photo-{id}?w=1200&q=80&fm=jpg`) → 그래도 실패 시 placeholder. 이미지 실패가 전체 흐름을 멈추지 않는다.
⚠️ **구글 이미지 검색 폴백 절대 금지**: 주제와 무관한 이미지를 가져오는 사례 발생. Unsplash CDN 직접 URL을 사용할 것.

**이미지 생성 토글**: 사용자가 Step 2에서 "이미지 없이"를 선택하면 이 단계를 건너뛴다.

**출력**: 이미지 파일들 + 이미지가 삽입된 최종 본문

---

### Step 7: 편집 검수 + SEO 최적화 + 출력
**타입**: review + generate

blog-writer Agent가 품질 검수를 수행하고 최종 출력한다.

> **SEO 규칙 필독**: `references/seo-rules.md`를 반드시 먼저 읽고 모든 규칙을 준수한다. (RankMath 100점 기준)

1. **메타데이터 생성**: SEO 제목, 설명, 키워드, 슬러그
2. **품질 검수** (100점 만점):
   - 구조 완성도 (25점): 소제목, 도입/결론
   - 내용 품질 (30점): 정보 정확성, 깊이
   - 스타일 일관성 (20점): 프리셋 톤 준수
   - SEO (15점): `references/seo-rules.md` 체크리스트 기준 (아래 참조)
   - 이미지 (10점): 적절한 배치, 설명, 주제 관련성

**SEO 체크 (15점 — RankMath 100점 기준)**:

| 항목 | 배점 | 기준 |
|------|------|------|
| Focus Keyword — 제목 앞 50%에 위치 + Power Word + 감성 언어(Sentiment) | 2 | seo-rules.md §2 |
| 콘텐츠 2,500단어(영문) 이상 → 한국어 5,000~7,000자 | 3 | seo-rules.md §3 |
| 첫 문단(앞 10% 또는 첫 300단어) + H2 3개 이상에 Focus Keyword 포함, 밀도 1~1.5% | 2 | seo-rules.md §4 |
| 이미지 4장 이상, 최소 1장 alt에 Focus Keyword 포함 (전체 권장) | 2 | seo-rules.md §5~6 |
| 목차(ToC) 포함 (긴 글 필수) | 1 | seo-rules.md §8 |
| 내부 링크 3개 이상 | 1 | seo-rules.md §9 |
| 외부 dofollow 링크 2개 이상 (최소 1개 dofollow, Nature/WHO 등 권위 출처) | 2 | seo-rules.md §10 |
| 메타 설명 80~130자, Focus Keyword 포함 | 1 | seo-rules.md §13 |
| 태그 5~10개 | 1 | seo-rules.md §14 |

3. **80점 이상**: 승인 → WordPress 발행 → 최종 출력
4. **80점 미만**: 피드백과 함께 자동 수정 → 재검수 (최대 3회)
5. 3회 미달 시 사용자에게 "수동 검토 필요" 안내 + 현재 결과물 제공

---

### Step 8: WordPress 발행
**타입**: script

검수 통과 후 WordPress에 자동 발행한다.

1. `src/publisher.py`의 `publish_post()` 호출
2. `.env`의 WordPress 설정 사용 (`WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`)
3. 기본 `POST_STATUS = "draft"` — 임시저장으로 올림 (사용자가 확인 후 공개 전환)
4. 발행 결과(post ID, URL)를 metadata.json에 기록
5. **실패 처리**: WordPress 연결 실패 시 로컬 output만 저장 + "수동 발행 필요" 안내
6. Notion 동기화는 발행 완료 후에만 수행 (별도 트리거)

**최종 출력**:
- `output/{date}_{topic}/` 디렉토리에 결과물 저장
- plan.json, article (유연한 포맷), metadata.json, review.json, images/
- WordPress draft URL 안내

---

## References

- **`references/style-presets.md`** — 7종 스타일 프리셋 상세 (structure, tone, match_signals, image_strategy)
- **`references/image-strategy.md`** — 나노바나나 이미지 생성 전략 (카테고리별 프롬프트, 모델 선택, 실패 처리)
- **`references/seo-rules.md`** — RankMath 100점 기준 SEO 규칙 전체 (Focus Keyword, 제목, 링크, 메타 등)

## Settings

| 설정 | 기본값 | 변경 방법 |
|------|--------|-----------|
| 스타일 | 자동 매칭 | Step 2에서 AskUserQuestion으로 변경 |
| 카테고리 | 자동 판별 | `/blog --category health`로 지정 |
| 이미지 생성 | on | Step 2에서 "이미지 없이" 선택 |
| 출력 포맷 | 주제별 유연 | 스타일 프리셋에 따름 |
| 편집 검수 기준 | 80점 | 고정 (변경 불가) |
| 최대 재시도 | 3회 | 고정 |
| WordPress 발행 | draft | config/settings.py POST_STATUS 변경 |
| SEO 체크 | 네이버+구글 | 자동 (편집 검수에 포함) |
