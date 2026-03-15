"""스타일 매칭 엔진 — 3-Layer 가중 점수로 최적 프리셋 선택"""

import json
import os
import subprocess
from typing import Optional

from config.style_presets import STYLE_PRESETS


def match_style(topic_spec_dict):
    # type: (dict) -> dict
    """TopicSpec에 가장 적합한 스타일 프리셋을 찾는다.

    3-Layer 매칭:
      final_score = keyword(0.2) + llm(0.6) + category(0.2)

    Args:
        topic_spec_dict: TopicSpec.to_dict() 결과

    Returns:
        dict: {"recommended": preset_id, "scores": {...}, "all_presets": [...]}
    """
    keywords = topic_spec_dict.get("keywords", [])
    category = topic_spec_dict.get("category", "other")
    core_topic = topic_spec_dict.get("core_topic", "")
    intent = topic_spec_dict.get("intent", "inform")

    scores = {}

    for preset_id, preset in STYLE_PRESETS.items():
        # Layer 1: Keyword score (0.2)
        kw_score = _keyword_score(keywords, preset["match_signals"])

        # Layer 2: LLM analysis score (0.6) — 배치로 한 번에 요청
        # (아래에서 일괄 처리)
        llm_score = 0.0

        # Layer 3: Category affinity (0.2)
        cat_score = preset["category_affinity"].get(category, 0.3)

        scores[preset_id] = {
            "keyword": kw_score,
            "llm": llm_score,
            "category": cat_score,
            "final": 0.0,
        }

    # LLM 분석 일괄 요청
    llm_scores = _llm_analysis(core_topic, intent, keywords)
    for preset_id in scores:
        scores[preset_id]["llm"] = llm_scores.get(preset_id, 0.5)

    # 최종 점수 계산
    for preset_id in scores:
        s = scores[preset_id]
        s["final"] = (s["keyword"] * 0.2) + (s["llm"] * 0.6) + (s["category"] * 0.2)

    # 정렬
    ranked = sorted(scores.items(), key=lambda x: x[1]["final"], reverse=True)
    recommended = ranked[0][0]

    # 0.1 이내 차이면 2개 추천
    alternatives = []
    if len(ranked) > 1 and (ranked[0][1]["final"] - ranked[1][1]["final"]) < 0.1:
        alternatives.append(ranked[1][0])

    return {
        "recommended": recommended,
        "recommended_name": STYLE_PRESETS[recommended]["name"],
        "alternatives": alternatives,
        "scores": scores,
        "preset": STYLE_PRESETS[recommended],
    }


def get_preset(preset_id):
    # type: (str) -> Optional[dict]
    """프리셋 ID로 프리셋 정보를 가져온다."""
    return STYLE_PRESETS.get(preset_id)


def list_presets():
    # type: () -> list
    """모든 프리셋 목록을 반환한다."""
    return [
        {"id": pid, "name": p["name"], "tone": p["tone"]}
        for pid, p in STYLE_PRESETS.items()
    ]


def _keyword_score(topic_keywords, match_signals):
    # type: (list, list) -> float
    """토픽 키워드와 프리셋 매칭 시그널의 겹침 비율."""
    if not topic_keywords or not match_signals:
        return 0.0

    topic_lower = [k.lower() for k in topic_keywords]
    signal_lower = [s.lower() for s in match_signals]

    matches = sum(1 for kw in topic_lower for sig in signal_lower if sig in kw or kw in sig)
    max_possible = max(len(topic_lower), 1)
    return min(matches / max_possible, 1.0)


def _llm_analysis(core_topic, intent, keywords):
    # type: (str, str, list) -> dict
    """Claude CLI로 주제-스타일 적합도를 일괄 분석한다."""
    preset_names = {pid: p["name"] for pid, p in STYLE_PRESETS.items()}

    prompt = f"""다음 블로그 주제에 대해 각 글쓰기 스타일의 적합도를 0.0~1.0으로 평가해줘.

주제: {core_topic}
의도: {intent}
키워드: {', '.join(keywords)}

스타일 목록:
{json.dumps(preset_names, ensure_ascii=False, indent=2)}

JSON으로 응답 (스타일 ID: 점수):
{{"howto_tutorial": 0.0, "list_curation": 0.0, ...}}

평가 기준:
- 주제의 특성(정보형/비교형/경험형 등)과 스타일의 구조가 얼마나 잘 맞는지
- 독자가 이 주제를 이 스타일로 읽었을 때 만족도
- intent와 스타일의 목적 일치도"""

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json"],
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode == 0:
            content = _parse_output(result.stdout)
            data = json.loads(content)
            # 값이 float인지 확인
            return {k: float(v) for k, v in data.items() if k in STYLE_PRESETS}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, FileNotFoundError):
        pass

    # 폴백: 기본값 0.5
    return {pid: 0.5 for pid in STYLE_PRESETS}


def _parse_output(raw):
    # type: (str) -> str
    """Claude CLI JSON wrapper 해제."""
    try:
        wrapper = json.loads(raw)
        if isinstance(wrapper, dict) and "result" in wrapper:
            content = wrapper["result"]
        else:
            return raw
    except json.JSONDecodeError:
        content = raw

    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        return content[start:end].strip()
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        return content[start:end].strip()
    return content
