# SEO 규칙 — RankMath 100점 기준

블로그 글 작성 시 반드시 준수해야 할 SEO 규칙. RankMath SEO 플러그인 기준.
모든 글에 적용. 예외 없음.

---

## 필수 규칙 (Basic SEO — 미충족 시 100점 불가)

### 1. Focus Keyword 설정
- 글마다 **하나의 Focus Keyword** 결정 (예: "AI 신약개발", "바이브 코딩")
- 복합 명사 또는 2~3단어 구문 권장
- 이미 다른 글에서 쓴 키워드 중복 사용 금지

### 2. 제목 (H1) 규칙
- Focus Keyword가 **제목 앞 50% 이내**에 위치
- **Power Word** 반드시 포함 (예: "완벽 정리", "충분한 이유", "놀라운 변화", "지금 바로", "진짜", "실제로")
- **숫자** 포함 권장 (예: "5가지", "2년", "80%")
- 길이: 15~35자 (네이버 SEO) / 60자 이내 (구글 SEO)
- ✅ 좋은 예: "AI 신약개발이 바꾸는 미래 — 15년 걸리던 신약, 이제 2년이면 충분한 이유"
- ❌ 나쁜 예: "신약개발에 대한 AI의 영향과 미래 전망"

### 3. 콘텐츠 길이
- **최소 2,500단어** (영문 기준) — RankMath 100점
- 한국어 블로그는 영문 단어 수 기준이므로, 실질적으로 **5,000~7,000자 한국어** 분량 작성
- 1,500단어 미만은 절대 불가

### 4. Focus Keyword 배치
- **첫 문단 (전체 콘텐츠 앞 10% 이내)**에 Focus Keyword 자연스럽게 포함
- **H2 소제목 3개 이상**에 Focus Keyword 또는 연관 키워드 포함
- **본문 전체** 키워드 밀도: **1~1.5%** (2.5% 초과 금지)
- 키워드를 억지로 반복하지 말 것 — 자연스럽게 문맥에 녹여야 함

### 5. 이미지 alt 텍스트
- **모든 이미지**의 alt 속성에 Focus Keyword 포함 필수
- ✅ 좋은 예: `alt="AI 신약개발을 위한 분자 모델링 시각화"`
- ❌ 나쁜 예: `alt="이미지"`, `alt="분자 모델링"`

### 6. 이미지 수
- **최소 3장** (네이버 SEO) / **4장 이상** (RankMath 100점)
- 본문 중간에 균등 배치 (도입부, 중간, 결론 앞)

### 7. URL 슬러그
- 영문, 하이픈 구분, 75자 이하
- Focus Keyword의 영문 번역 포함
- ✅ 좋은 예: `ai-drug-discovery-2-years`
- ❌ 나쁜 예: `post-123`, `ai가-신약개발을`

---

## 링크 규칙

### 8. 내부 링크
- **최소 3개** 내부 링크 (같은 사이트 다른 글로)
- 글 주제와 연관된 글로만 링크 (억지스러운 연결 금지)
- 앵커 텍스트에 키워드 포함 권장

### 9. 외부 dofollow 링크
- **최소 2개** 외부 링크 (신뢰도 높은 출처)
- 권장 출처: Nature, Science, WHO, 정부 기관, 주요 대학 연구, 유명 기업 공식 발표
- `target="_blank" rel="noopener"` 필수 (nofollow 사용 금지)
- ✅ 좋은 예: `<a href="https://www.nature.com/articles/..." target="_blank" rel="noopener">AlphaFold 원본 논문</a>`

---

## 가독성 규칙

### 10. 문단 길이
- 각 문단 **120단어(영문) 이하** — 한국어 기준 약 200자 이하
- 3~4문장이 넘으면 문단 분리

### 11. H2/H3 구조
- H2 소제목 **최소 5개** 이상
- H3 소제목으로 세부 항목 구분 (필요 시)
- 소제목 순서: H1 → H2 → H3 (순서 건너뛰기 금지)

---

## 메타데이터 규칙

### 12. 메타 설명 (excerpt)
- **60~110자** (네이버) / 155자 이내 (구글)
- Focus Keyword 포함 필수
- 독자가 클릭하고 싶게 만드는 문장
- ✅ 좋은 예: "AI가 신약개발의 공식을 바꾸고 있습니다. 15년·1조원이 걸리던 과정을 2년·6500억원으로 줄이는 혁명, 실제 사례로 알아봅니다."

### 13. 태그
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
[ ] Focus Keyword 결정됨
[ ] 제목에 Power Word + 숫자 포함
[ ] 제목 앞 50%에 Focus Keyword 위치
[ ] 첫 문단에 Focus Keyword 포함
[ ] 콘텐츠 2,500단어(영문) 이상
[ ] 키워드 밀도 1~1.5%
[ ] H2 5개 이상, 키워드 포함
[ ] 이미지 4장 이상
[ ] 모든 이미지 alt에 Focus Keyword 포함
[ ] 내부 링크 3개 이상
[ ] 외부 dofollow 링크 2개 이상 (Nature, WHO 등 권위 출처)
[ ] 메타 설명 60~110자, Focus Keyword 포함
[ ] 태그 5~10개
[ ] 문단 200자(한국어) 이하
[ ] article.html에 JSON-LD 포함
[ ] WordPress 업로드 시 script 태그 제거
```
