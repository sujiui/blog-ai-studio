"""토픽 해석기 — 자연어 입력을 구조화된 TopicSpec으로 변환"""

import json
import os
import subprocess
from dataclasses import dataclass, field, asdict
from typing import Optional

from config.settings import TOPICS, DAY_TOPIC_MAP


@dataclass
class TopicSpec:
    """주제 해석 결과"""
    original_input: str          # "두쫀쿠가 유행한다던데?"
    corrected_input: str = ""    # "두바이 쫀득 쿠키가 유행한다던데?"
    core_topic: str = ""         # "두바이 쫀득 쿠키"
    keywords: list = field(default_factory=list)
    category: str = ""           # ai_tech / health / self_improvement / other
    intent: str = ""             # inform / analyze / compare / howto / opinion
    search_queries: list = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""

    def to_dict(self):
        return asdict(self)


def interpret_topic(user_input, category_hint=None):
    # type: (str, Optional[str]) -> TopicSpec
    """자연어 입력을 TopicSpec으로 변환한다.

    Args:
        user_input: 사용자의 자연어 입력
        category_hint: 카테고리 힌트 (지정 시 자동 판별 건너뜀)

    Returns:
        TopicSpec: 구조화된 주제 정보
    """
    spec = TopicSpec(original_input=user_input)

    # Phase 1: LLM으로 1차 해석
    spec = _llm_interpret(spec)

    # Phase 2: 신뢰도 낮으면 웹 검색 폴백
    if spec.confidence < 0.7:
        spec = _search_fallback(spec)

    # Phase 3: 카테고리 결정
    if category_hint and category_hint in TOPICS:
        spec.category = category_hint
    elif not spec.category or spec.category not in list(TOPICS.keys()) + ["other"]:
        spec.category = _detect_category(spec)

    return spec


def _llm_interpret(spec):
    # type: (TopicSpec) -> TopicSpec
    """Claude CLI로 자연어를 해석한다."""
    prompt = f"""다음 사용자 입력을 분석해서 블로그 주제로 변환해줘.

사용자 입력: "{spec.original_input}"

JSON으로 응답해줘:
{{
  "corrected_input": "오타/줄임말 수정한 원문",
  "core_topic": "핵심 주제 (명사형)",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "category": "ai_tech 또는 health 또는 self_improvement 또는 other",
  "intent": "inform 또는 analyze 또는 compare 또는 howto 또는 opinion",
  "search_queries": ["검색어1", "검색어2"],
  "confidence": 0.0~1.0 사이 숫자 (이 해석에 대한 확신도),
  "reasoning": "이렇게 해석한 이유"
}}

주의:
- 신조어/줄임말/오타가 있으면 confidence를 낮게 (0.3~0.6)
- 명확한 주제면 confidence를 높게 (0.8~1.0)
- 모르는 단어가 있으면 솔직하게 confidence를 낮추고 reasoning에 명시"""

    result = _call_claude(prompt)
    if result:
        try:
            data = json.loads(result)
            spec.corrected_input = data.get("corrected_input", spec.original_input)
            spec.core_topic = data.get("core_topic", "")
            spec.keywords = data.get("keywords", [])
            spec.category = data.get("category", "other")
            spec.intent = data.get("intent", "inform")
            spec.search_queries = data.get("search_queries", [])
            spec.confidence = float(data.get("confidence", 0.5))
            spec.reasoning = data.get("reasoning", "")
        except (json.JSONDecodeError, ValueError, KeyError):
            spec.confidence = 0.3
            spec.reasoning = "LLM 응답 파싱 실패 — 검색 폴백 필요"

    return spec


def _search_fallback(spec):
    # type: (TopicSpec) -> TopicSpec
    """웹 검색으로 모르는 단어의 실제 의미를 파악한다."""
    search_query = spec.original_input
    if spec.search_queries:
        search_query = spec.search_queries[0]

    # 검색 결과를 Claude에게 다시 해석시킴
    prompt = f"""사용자가 "{spec.original_input}"라고 입력했는데,
이 입력의 의미를 정확히 모르겠어.

웹에서 "{search_query}"를 검색해서 이게 무엇인지 알아낸 후,
다시 블로그 주제로 변환해줘.

JSON으로 응답:
{{
  "corrected_input": "수정된 원문",
  "core_topic": "핵심 주제",
  "keywords": ["키워드1", "키워드2"],
  "category": "ai_tech/health/self_improvement/other",
  "intent": "inform/analyze/compare/howto/opinion",
  "confidence": 0.0~1.0,
  "reasoning": "검색 결과 기반 해석 이유"
}}"""

    result = _call_claude(prompt)
    if result:
        try:
            data = json.loads(result)
            spec.corrected_input = data.get("corrected_input", spec.corrected_input)
            spec.core_topic = data.get("core_topic", spec.core_topic)
            spec.keywords = data.get("keywords", spec.keywords)
            spec.category = data.get("category", spec.category)
            spec.intent = data.get("intent", spec.intent)
            spec.confidence = float(data.get("confidence", spec.confidence))
            spec.reasoning = "검색 폴백: " + data.get("reasoning", "")
        except (json.JSONDecodeError, ValueError, KeyError):
            spec.reasoning += " | 검색 폴백도 실패"

    return spec


def _detect_category(spec):
    # type: (TopicSpec) -> str
    """키워드 기반으로 카테고리를 판별한다."""
    scores = {}
    for cat_id, cat_info in TOPICS.items():
        score = 0
        cat_keywords = [k.lower() for k in cat_info["keywords"]]
        for kw in spec.keywords:
            if kw.lower() in cat_keywords:
                score += 1
        scores[cat_id] = score

    if max(scores.values(), default=0) > 0:
        return max(scores, key=scores.get)
    return "other"


def _call_claude(prompt):
    # type: (str) -> Optional[str]
    """Claude CLI subprocess를 호출한다."""
    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=60, env=env
        )
        if result.returncode == 0 and result.stdout.strip():
            return _parse_json_output(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _parse_json_output(raw_output):
    # type: (str) -> Optional[str]
    """Claude CLI JSON wrapper를 해제한다."""
    try:
        wrapper = json.loads(raw_output)
        if isinstance(wrapper, dict) and "result" in wrapper:
            content = wrapper["result"]
        else:
            content = raw_output
    except json.JSONDecodeError:
        content = raw_output

    # markdown code block 추출
    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        content = content[start:end].strip()
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        content = content[start:end].strip()

    return content
