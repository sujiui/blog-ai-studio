"""블로그 스타일 프리셋 정의 — 7종 글쓰기 스타일

리서치 기반 분류:
- 구조 유형 9종 (리스티클, 튜토리얼, 스토리텔링, 큐레이션, Q&A, 비교분석, 리서치요약, 에세이, 트렌드소개)
- 톤 유형 6종 (전문가형, 친구형, 선생님형, 리포터형, 에세이형, 편안한 존댓말형)
이를 조합하여 7종 프리셋으로 구성.
"""

STYLE_PRESETS = {
    "info_delivery": {
        "name": "정보전달형",
        "description": "핵심 정보를 빠르고 명확하게 전달. 트렌드 소개, 뉴스 요약, 새 기능 소개 등.",
        "structure": ["화제 소개", "핵심 정보 정리", "왜 중요한지", "실생활 적용", "마무리"],
        "tone": "편안한 존댓말, 리포터처럼 명확하게",
        "length": (2000, 2500),
        "match_signals": [
            "소개", "정보", "알려줘", "뉴스", "요약", "정리",
            "트렌드", "유행", "화제", "요즘", "최신", "신상",
            "뭐야", "어떤거", "나왔다", "출시",
        ],
        "category_affinity": {"ai_tech": 0.9, "health": 0.6, "self_improvement": 0.5, "other": 0.6},
        "image_strategy": "modern_screenshot",
        "prompt_injection": "핵심 정보를 빠르게 전달하되, 독자가 '왜 이게 중요한지'를 느끼게 한다. 불필요한 서론 최소화.",
    },
    "review_experience": {
        "name": "리뷰 체험형",
        "description": "직접 써보고/해보고 솔직하게 리뷰. 장단점, 실사용 경험, 비교 포함.",
        "structure": ["제품/서비스 소개", "직접 써본 경험", "장점", "단점/아쉬운 점", "비교 (있으면)", "종합 평가"],
        "tone": "솔직하고 객관적, 직접 해본 사람의 신뢰감",
        "length": (2500, 3000),
        "match_signals": [
            "리뷰", "후기", "써봤", "해봤", "체험", "사용기",
            "비교", "vs", "장단점", "평가", "추천", "솔직",
            "어떤게 나은", "차이", "review",
        ],
        "category_affinity": {"ai_tech": 0.8, "health": 0.7, "self_improvement": 0.4, "other": 0.5},
        "image_strategy": "product_screenshot",
        "prompt_injection": "실제 사용한 사람의 시점으로 작성. 마케팅 느낌이 나지 않도록. 장점뿐 아니라 단점도 솔직하게.",
    },
    "essay_emotional": {
        "name": "에세이 감성형",
        "description": "개인적 생각과 감성을 담은 에세이. 공감과 여운이 남는 글.",
        "structure": ["에피소드/장면", "느낀 점", "생각의 확장", "깨달음", "여운 있는 마무리"],
        "tone": "따뜻하고 사색적, 에세이스트의 감성",
        "length": (2000, 2500),
        "match_signals": [
            "에세이", "감성", "느낀", "생각", "일상", "사색",
            "마음", "변화", "도전", "성장", "회고", "돌아보니",
            "경험", "이야기", "story", "깨달음",
        ],
        "category_affinity": {"ai_tech": 0.2, "health": 0.7, "self_improvement": 0.9, "other": 0.5},
        "image_strategy": "emotional_illustration",
        "prompt_injection": "정보 전달보다 감정과 생각의 흐름에 집중. 독자가 공감하고 자신을 돌아보게 하는 글. 결론을 강요하지 않고 여운을 남긴다.",
    },
    "list_curation": {
        "name": "리스트 큐레이션형",
        "description": "여러 항목을 정리해서 소개. 베스트/추천/모음 등.",
        "structure": ["도입 (왜 이 리스트인지)", "항목별 소개 (5-10개)", "비교/요약표", "최종 추천"],
        "tone": "가볍고 읽기 쉬운 큐레이터",
        "length": (2000, 3000),
        "match_signals": [
            "추천", "모음", "베스트", "리스트", "top", "best",
            "선정", "정리", "골라봤", "필수", "개", "가지",
        ],
        "category_affinity": {"ai_tech": 0.6, "health": 0.8, "self_improvement": 0.7, "other": 0.6},
        "image_strategy": "infographic",
        "prompt_injection": "각 항목을 간결하게, 스캔하기 쉽게. 번호나 소제목으로 명확히 구분. 항목당 200-300자.",
    },
    "expert_analysis": {
        "name": "전문가 분석형",
        "description": "데이터와 논리로 주제를 깊이 분석. 정책, 경제, 기술 트렌드 해설.",
        "structure": ["화제 소개", "배경 설명", "데이터/근거 기반 분석", "시사점", "전망/예측"],
        "tone": "전문적이지만 이해하기 쉬운 해설자",
        "length": (2500, 3000),
        "match_signals": [
            "분석", "이유", "왜", "영향", "의미", "전망",
            "해설", "데이터", "통계", "정책", "경제", "시장",
            "깊이", "원인", "전문", "analysis",
        ],
        "category_affinity": {"ai_tech": 0.8, "health": 0.5, "self_improvement": 0.3, "other": 0.5},
        "image_strategy": "data_visualization",
        "prompt_injection": "주장에는 반드시 데이터나 출처를 제시. '~라고 합니다'보다 '~에 따르면' 형태. 독자가 스스로 판단할 수 있는 근거 제공.",
    },
    "friendly_chat": {
        "name": "친근한 대화형",
        "description": "친구에게 말하듯 편하게 풀어쓰는 스타일. Q&A, 꿀팁 공유, 일상 정보.",
        "structure": ["상황 공감 (너도 이런 적 있지?)", "핵심 정보/꿀팁", "왜 이게 좋은지", "주의할 점", "친근한 마무리"],
        "tone": "친구처럼 편안한 반말+존댓말 믹스, 대화하는 느낌",
        "length": (1500, 2500),
        "match_signals": [
            "꿀팁", "알려줄게", "이거 해봤어", "진짜", "ㅋㅋ",
            "대화", "친구", "편하게", "쉽게", "간단", "빠르게",
            "꿀잼", "개꿀", "레알", "솔직히",
        ],
        "category_affinity": {"ai_tech": 0.4, "health": 0.8, "self_improvement": 0.6, "other": 0.7},
        "image_strategy": "casual_meme",
        "prompt_injection": "딱딱한 정보 전달 금지. 친구랑 카톡하는 느낌으로. 이모티콘/감탄사 적절히. 하지만 핵심 정보는 정확하게.",
    },
    "tutorial_howto": {
        "name": "튜토리얼/하우투형",
        "description": "따라하면 되는 단계별 가이드. 설치, 설정, 만들기 등.",
        "structure": ["뭘 만들/할 건지", "준비물/사전 조건", "단계별 실행 (Step 1-N)", "결과 확인", "트러블슈팅/팁"],
        "tone": "친절한 선생님, 명확하고 정확하게",
        "length": (2500, 3000),
        "match_signals": [
            "방법", "하는법", "설치", "설정", "만들기", "따라하기",
            "시작하기", "가이드", "how to", "tutorial", "step",
            "단계", "순서", "초보", "입문",
        ],
        "category_affinity": {"ai_tech": 0.9, "health": 0.4, "self_improvement": 0.5, "other": 0.4},
        "image_strategy": "step_by_step",
        "prompt_injection": "각 단계를 명확히 번호 매겨서. 스크린샷/코드가 들어갈 위치 표시. 초보자도 따라할 수 있는 수준으로.",
    },
}
