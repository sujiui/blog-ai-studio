# Blog Quick — 비인터랙티브 블로그 생성

자동화/cron 환경에서 사용자 입력 없이 블로그 글을 생성하는 커맨드.

## 사용법

```
/blog-quick [category] [keyword]
/blog-quick ai_tech "Claude Code"
/blog-quick health
/blog-quick                        # 오늘 요일 기반 자동
```

## 동작

`/blog` 스킬과 동일한 7단계 워크플로우를 실행하되, 모든 사용자 확인(AskUserQuestion)을 건너뛴다.

### 자동 결정 규칙

| 단계 | 인터랙티브(/blog) | 비인터랙티브(/blog-quick) |
|------|-------------------|---------------------------|
| Step 1: 토픽 | 사용자 입력 | 인수에서 추출 또는 요일 기반 |
| Step 2: 스타일 | 추천 후 선택 | 자동 최고점 프리셋 |
| Step 4: 기획서 | 프리뷰 확인 | 자동 승인 |
| Step 7: 검수 | 결과 표시 | 80점 이상 자동 승인, 미달 시 3회 재시도 |

### 카테고리 미지정 시 요일 매핑

```
월(0) → ai_tech
수(2) → health
금(4) → self_improvement
기타 → ai_tech (기본값)
```

### 키워드 미지정 시

트렌드 수집 결과에서 최고 관심도 키워드를 자동 선택한다.

## 출력

`output/{date}_{category}/` 디렉토리에 결과물 저장.
성공 시 stdout에 결과 요약 JSON 출력:

```json
{
  "status": "success",
  "title": "글 제목",
  "category": "ai_tech",
  "style": "trend_intro",
  "score": 85,
  "output_dir": "output/20260312_ai_tech/",
  "files": ["article.html", "metadata.json", "review.json", "images/"]
}
```

## 실패 처리

- 트렌드 전멸: stderr에 에러 출력, exit code 1
- 검수 3회 미달: 현재 결과물 저장 + stderr 경고, exit code 0 (결과물은 사용 가능)
- 이미지 전체 실패: 텍스트만 저장, stderr 경고, exit code 0
