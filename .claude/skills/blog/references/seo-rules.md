# SEO 규칙 — RankMath 100점 기준

블로그 글 작성 시 반드시 준수해야 할 SEO 규칙. RankMath SEO 플러그인 기준.
모든 글에 적용. 예외 없음.

> **출처**: RankMath 공식 가이드 (rankmath.com/kb/score-100-in-tests/)

---

## 필수 규칙 (Basic SEO — 미충족 시 100점 불가)

### 1. Focus Keyword 설정
- 글마다 **하나의 Focus Keyword** 결정 (예: "AI 신약개발", "바이브 코딩")
- 복합 명사 또는 2~3단어 구문 권장
- 이미 다른 글에서 쓴 키워드 중복 사용 금지 (키워드 카니발리제이션 방지)

### 2. 제목 (H1) 규칙 — RankMath 3개 기준 모두 충족

| 기준 | 설명 | 예시 |
|------|------|------|
| **Focus Keyword 위치** | 제목 앞 50% 이내 | "AI 신약개발이 바꾸는 미래 — 15년이 2년으로" |
| **Power Word** | 클릭을 유도하는 강력한 단어 포함 | "완벽 정리", "진짜", "지금 바로", "충분한 이유", "놀라운" |
| **감성 언어(Sentiment)** | 감정을 자극하는 언어 — 클릭베이트 아닌 진성 감동/호기심/공감 | "아무도 말해주지 않는다", "나는 몰랐다", "그제서야 알았다" |

- **숫자** 포함 권장 (예: "5가지", "2년", "80%") — 클릭률 향상
- 길이: 15~35자 (네이버 SEO) / 60자 이내 (구글 SEO)
- ✅ 좋은 예: "AI 신약개발이 바꾸는 미래 — 15년 걸리던 신약, 이제 2년이면 충분한 이유"
- ❌ 나쁜 예: "신약개발에 대한 AI의 영향과 미래 전망"

### 3. 콘텐츠 길이
- **2,500단어(영문) 이상** = RankMath 100점
- 한국어 기준: **5,000~7,000자** (영문 단어 수 기준 환산)
- 점수표:

| 영문 단어 수 | RankMath 점수 |
|------------|--------------|
| 2,500+ | 100% |
| 2,000~2,500 | 70% |
| 1,500~2,000 | 60% |
| 1,000~1,500 | 40% |
| 600~1,000 | 20% |
| 600 미만 | 0% |

### 4. Focus Keyword 배치
- **첫 문단 (전체 콘텐츠 앞 10% 이내, 또는 첫 300단어)** 에 자연스럽게 포함
- **H2 소제목 3개 이상**에 Focus Keyword 또는 연관 키워드 포함
- **본문 전체** 키워드 밀도: **1~1.5%** (2.5% 초과 시 경고)
- 키워드를 억지로 반복하지 말 것 — 자연스럽게 문맥에 녹여야 함

### 5. 이미지 alt 텍스트
- **최소 1장** 이상의 이미지 alt에 Focus Keyword 포함 (RankMath 최소 기준)
- 실전 권장: **모든 이미지** alt에 Focus Keyword 또는 연관 키워드 포함 (Best Practice)
- ✅ 좋은 예: `alt="AI 신약개발을 위한 분자 모델링 시각화"`
- ❌ 나쁜 예: `alt="이미지"`, `alt="분자 모델링"`

### 6. 이미지/미디어 수
- **4장 이상** (RankMath 100점 기준) / 최소 3장 (네이버 SEO)
- 본문 중간에 균등 배치 (도입부, 중간, 결론 앞)
- 이미지 또는 동영상 모두 카운트

### 7. URL 슬러그
- 영문, 하이픈 구분, **75자 이하**
- Focus Keyword의 영문 번역 포함
- ✅ 좋은 예: `ai-drug-discovery-2-years`
- ❌ 나쁜 예: `post-123`, `ai가-신약개발을`

### 8. 목차 (Table of Contents)
- **긴 글(5,000자 이상)에서 필수** — RankMath 별도 점수 항목
- "Jump To" 검색 결과 링크(Jump Links) 획득 가능
- 구현 방법:
  - HTML: `<nav class="toc">` + 앵커 링크
  - WordPress 플러그인: Rank Math ToC, Easy Table of Contents

---

## 링크 규칙

### 9. 내부 링크
- **최소 3개** 내부 링크 (같은 사이트 다른 글로)
- 글 주제와 연관된 글로만 링크 (억지스러운 연결 금지)
- 앵커 텍스트에 키워드 포함 권장

### 10. 외부 dofollow 링크
- **최소 2개** 외부 링크, 최소 1개는 dofollow (nofollow 금지)
- 권장 출처: Nature, Science, WHO, 정부 기관, 주요 대학 연구, 유명 기업 공식 발표
- `target="_blank" rel="noopener"` 필수 (rel="nofollow" 사용 금지)
- ✅ 좋은 예: `<a href="https://www.nature.com/articles/..." target="_blank" rel="noopener">AlphaFold 원본 논문</a>`

---

## 가독성 규칙

### 11. 문단 길이
- 각 문단 **120단어(영문) 이하** — 한국어 기준 약 200자 이하
- 3~4문장이 넘으면 문단 분리

### 12. H2/H3 구조
- H2 소제목 **최소 5개** 이상
- H3 소제목으로 세부 항목 구분 (필요 시)
- 소제목 순서: H1 → H2 → H3 (순서 건너뛰기 금지)

---

## 메타데이터 규칙

### 13. 메타 설명 (excerpt)
- **RankMath 기준**: Focus Keyword 반드시 포함 (Primary Focus Keyword only)
- **길이**: 한국어 80~130자 / 영문 120~160자 이내
  - 네이버 검색 최적화: 80~110자
  - 구글 검색 최적화: 110~130자 (155자 초과 시 잘림)
- 독자가 클릭하고 싶게 만드는 문장
- ✅ 좋은 예: "AI가 신약개발의 공식을 바꾸고 있습니다. 15년·1조원이 걸리던 과정을 2년·6500억원으로 줄이는 혁명, 실제 사례로 알아봅니다."

### 14. 태그
- **5~10개** 태그 설정
- Focus Keyword + 연관 키워드 포함

---

## WordPress 발행 시 주의사항

### JSON-LD 구조화 데이터
- article.html에는 `<script type="application/ld+json">` 포함해서 저장
- WordPress REST API 업로드 시에는 NinjaFirewall이 `<script>` 태그를 차단하므로 **반드시 제거 후 전송**:
  ```python
  import re
  content_no_script = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
  ```
- JSON-LD는 추후 WP Admin에서 RankMath 플러그인이 자동 생성함

### RankMath 메타 설정
- WordPress REST API로 RankMath 메타 필드 직접 수정 불가 (미등록 상태)
- **excerpt 필드**로 메타 설명 전달 → RankMath가 자동으로 사용
- Focus Keyword는 WP Admin에서 수동 입력 필요

---

## 체크리스트 (글 작성 완료 후 확인)

```
[ ] Focus Keyword 결정됨 (다른 글과 중복 없음)
[ ] 제목 앞 50%에 Focus Keyword 위치
[ ] 제목에 Power Word 포함
[ ] 제목에 감성 언어(Sentiment) 포함 — 공감·호기심·감동 유발
[ ] 제목에 숫자 포함 (권장)
[ ] 첫 문단(앞 10% 또는 첫 300단어)에 Focus Keyword 포함
[ ] 콘텐츠 2,500단어(영문) / 5,000자(한국어) 이상
[ ] 키워드 밀도 1~1.5% (2.5% 미만)
[ ] H2 5개 이상, Focus Keyword 또는 연관 키워드 포함
[ ] 이미지 4장 이상
[ ] 최소 1장 이상 이미지 alt에 Focus Keyword 포함 (전체 권장)
[ ] 내부 링크 3개 이상
[ ] 외부 dofollow 링크 2개 이상 (최소 1개 dofollow)
[ ] 목차(ToC) 포함 (긴 글 필수)
[ ] URL 슬러그 75자 이하, 영문, Focus Keyword 포함
[ ] 메타 설명 80~130자, Focus Keyword 포함
[ ] 태그 5~10개
[ ] 문단 200자(한국어) 이하
[ ] article.html에 JSON-LD 포함
[ ] WordPress 업로드 시 script 태그 제거
```
