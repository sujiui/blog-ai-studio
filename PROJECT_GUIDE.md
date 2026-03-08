# Blog AI Studio - 프로젝트 가이드

## 개요
매주 **월/수/금** 블로그 글을 자동 생성하고 WordPress에 발행하는 AI 파이프라인 시스템.

| 요일 | 주제 | 톤 |
|------|------|----|
| 월 | AI/기술 | 신기한 발견을 공유하는 친근한 톤 |
| 수 | 건강 | 직접 해본 사람이 알려주는 느낌 |
| 금 | 자기계발 | 현실적이고 공감되는 톤 |

**콘텐츠 스타일**: 트렌드 큐레이션 ("누군가 이런 걸 만들었대!" 소개형)
**톤**: 편안한 존댓말 (너무 캐주얼하지 않게)

---

## 5팀 파이프라인

```
🔍 리서치팀 → 📐 기획팀 → ✍️ 라이팅팀 → 🎨 크리에이티브팀 → 📋 편집팀 → ✅ 발행 승인
```

| 팀 | 역할 | 컬러 |
|----|------|------|
| 🔍 리서치팀 | 8채널 키워드 리서치 | #3B82F6 |
| 📐 기획팀 | 트렌드 큐레이션 구조 기획 (🔥🤔🛠️💡📌) | #8B5CF6 |
| ✍️ 라이팅팀 | SEO 최적화 글 작성 (2000-3000자) | #10B981 |
| 🎨 크리에이티브팀 | Gemini 이미지 생성 | #F59E0B |
| 📋 편집팀 | 메타데이터 + 품질 검수 (점수제) | #EF4444 |

---

## 프로젝트 구조

```
Blog_AI/
├── config/settings.py      # 주제, 톤, 키워드, 발행 설정
├── src/
│   ├── main.py             # 진입점 (python -m src.main)
│   ├── pipeline.py         # 5팀 파이프라인 오케스트레이터
│   ├── generator.py        # Claude Code CLI 글 생성기 (단독용)
│   ├── notion_sync.py      # Notion DB 동기화
│   ├── publisher.py        # WordPress REST API 발행
│   └── tracker.py          # 발행 후 성과 추적 (1/2/3주차)
├── dashboard/
│   ├── app.py              # 로컬 대시보드 (localhost:8080)
│   ├── app_cloud.py        # 클라우드 대시보드 (Render)
│   ├── notion_reader.py    # Notion API 데이터 리더
│   └── templates/          # HTML 템플릿 (칸반보드 UI)
├── output/                 # 생성된 콘텐츠 저장 (gitignore)
├── .env                    # API 키 (gitignore)
├── Procfile                # Render 배포 설정
├── render.yaml             # Render 서비스 정의
└── requirements.txt        # Python 패키지
```

---

## 빠른 시작

### 1. 파이프라인 실행 (글 생성)
```bash
cd /Users/baosuji/Desktop/project/Blog_AI

# 주제 자동 선택 (요일 기반)
python -m src.main

# 특정 주제 지정
python -m src.main --topic ai_tech

# 특정 키워드로 실행
python -m src.main --topic ai_tech --keyword "GPT-5 활용법"
```

### 2. 로컬 대시보드 확인
```bash
python -m dashboard.app
# → http://localhost:8080
```

### 3. 성과 추적
```bash
# 발행된 글 등록
python -m src.tracker register <content_id> <wordpress_url>

# 통계 수집
python -m src.tracker collect

# 현황 확인
python -m src.tracker status
```

---

## 환경 변수 (.env)

```env
# Gemini (이미지 생성)
GEMINI_API_KEY=<your-key>

# Notion (파이프라인 동기화 & 클라우드 대시보드)
NOTION_API_KEY=<your-key>
NOTION_DATABASE_ID=9cd5aabbbbd644128abc34a58de7c2f2

# WordPress (발행) - 미설정
WP_URL=
WP_USERNAME=
WP_APP_PASSWORD=
```

---

## 배포 현황

| 서비스 | URL | 상태 |
|--------|-----|------|
| 클라우드 대시보드 | https://blog-ai-studio.onrender.com | ✅ 배포됨 |
| GitHub 레포 | https://github.com/sujiui/blog-ai-studio | ✅ 연결됨 |
| Notion DB | 콘텐츠 파이프라인 DB | ✅ 연동됨 |
| WordPress | - | ⏳ 미설정 |

---

## Notion 데이터베이스 정보

- **Database ID**: `9cd5aabbbbd644128abc34a58de7c2f2`
- **Data Source ID**: `a47e6f1d-657c-4c2b-bea1-66ac7ca2da86`
- **Parent Page ID**: `31d7bcb1-7e4d-816c-a726-ee0b70268660`

---

## 성과 등급 시스템

발행 후 1/2/3주차 조회수와 댓글을 추적하여 등급 부여:

| 등급 | 기준 (조회수 + 댓글×50) |
|------|------------------------|
| 🏆 S | 5,000 이상 |
| 🥇 A | 2,000 이상 |
| 🥈 B | 500 이상 |
| 🥉 C | 100 이상 |
| ❌ D | 100 미만 |

---

## CTA 규칙

글에 포함하면 안 되는 것:
- ❌ "뉴스레터 구독하세요" (뉴스레터 없음)
- ❌ "PDF 다운로드" (제공하지 않음)
- ❌ 존재하지 않는 서비스 언급

허용되는 CTA:
- ✅ "댓글로 의견 남겨주세요"
- ✅ "다른 글도 읽어보세요"
- ✅ "북마크 해두세요"

---

## 남은 작업

- [ ] WordPress 연결 (WP_URL, WP_USERNAME, WP_APP_PASSWORD 설정)
- [ ] 이미지 생성 Python 3.12 환경 확인 (로컬 Python 3.9 → 업그레이드 필요)
- [ ] 리서치팀 자동 키워드 수집 구현 (8채널 설계 완료, 코드 미구현)
- [ ] 자동 스케줄링 (월/수/금 자동 실행 - cron 또는 GitHub Actions)

---

## 기술 스택

- **AI 엔진**: Claude Code CLI (Max 구독, API 비용 없음)
- **이미지 생성**: Gemini 2.0 Flash
- **데이터베이스**: Notion API
- **웹 프레임워크**: Flask + Gunicorn
- **배포**: Render.com
- **발행 플랫폼**: WordPress REST API
- **형상관리**: GitHub (`sujiui/blog-ai-studio`)
