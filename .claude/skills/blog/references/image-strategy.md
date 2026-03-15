# 이미지 생성 전략

Gemini API(google.genai) 기본 + 구글 이미지 검색 폴백. 인포그래픽은 AI 티가 나므로 제외.

## 전략: Gemini 기본 → 검색 폴백

1. **Gemini Nano Banana 2** (`gemini-3.1-flash-image-preview`)로 이미지 생성 시도
2. 실패 시 **폴백 모델** (`gemini-2.5-flash-image`)로 재시도
3. 그래도 실패 시 **구글에서 관련 이미지 검색** (Unsplash/Pexels/Pixabay)
4. 최종 실패 시 placeholder 텍스트

## 모델 선택

| 용도 | 모델 | 특징 |
|------|------|------|
| 본문 이미지 | `gemini-3.1-flash-image-preview` | Nano Banana 2 — 4-8초, Pro급+Flash속도 |
| 썸네일 | `gemini-3-pro-image-preview` | Nano Banana Pro — 최고 품질 |
| 폴백 | `gemini-2.5-flash-image` | 초기 모델 — 안정성 높음 |

## 이미지 배치 전략 (리서치 기반)

1500-3000자 글에 **3-5장** 권장:
- **Hero**: 최상단 — SNS 미리보기, OG 이미지
- **섹션 시작**: 각 소제목 아래 — 가독성, 체류시간 향상
- **CTA**: 글 하단 — 액션 유도

## 스타일별 이미지 방향

**핵심 원칙: 인포그래픽/차트/다이어그램은 AI 티가 나므로 절대 생성하지 않는다.**

| 스타일 | 이미지 방향 | 피해야 할 것 |
|--------|------------|-------------|
| 정보전달형 | 제품/서비스 스크린샷 느낌, 현대적 | 인포그래픽, 차트 |
| 리뷰체험형 | 실사용 장면, 비교 레이아웃 | 만화, 추상 |
| 에세이감성형 | 따뜻한 일러스트, 파스텔 색감 | 기술적, 차가운 톤 |
| 리스트큐레이션형 | 밝은 사진, 라이프스타일 | 텍스트 많은 이미지 |
| 전문가분석형 | 비즈니스 사진, 모던 일러스트 | AI 생성 차트 |
| 친근한대화형 | 캐주얼 일상 사진 | 격식, 기업 느낌 |
| 튜토리얼형 | 단계별 가이드 일러스트 | 추상 아트 |

## 프롬프트 구성

```
[이미지 설명] + [스타일 힌트] + 품질 지시어 + NOT: [피해야 할 것]

예: "Developer using AI coding assistant on laptop.
modern, clean, product screenshot style, realistic.
high quality, detailed, professional blog image.
no text, no watermarks, no logos.
NOT: infographic, chart, diagram, text overlay"
```

## 비용 (리서치 기반)

- 글당: ~$0.15-0.77 (모델/장수에 따라)
- 월 12편: $1.80-9.24
- **무료 티어: Google AI Studio 하루 50회 (월 ~1,500회) — 충분**

## GEMINI_API_KEY

`.env` 파일의 `GEMINI_API_KEY` 환경변수를 사용. `src/image_generator.py` 참조.
