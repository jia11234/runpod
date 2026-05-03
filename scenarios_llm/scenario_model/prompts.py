import json
from scenarios_llm.scenario_model.schemas import ChatRequest, HistoryItem
from typing import List, Dict

# =====================================================================
# 프롬프트 템플릿 및 설정값
# =====================================================================

MSG_LEN_GUIDE = {
    "short": "2~3개의 블록으로 구성",
    "normal": "4~5개의 블록으로 구성",
    "long": "5~6개의 블록으로 구성하여 풍성하게",
    "very_long": "7~8개의 블록으로 구성하여 소설처럼 묘사를 충분히.",
}

SYSTEM_PROMPT_TEMPLATE = """
당신은 한국 역사 캐릭터 챗봇 「{title}」의 게임 마스터 겸 소설 작가입니다.

[시나리오 개요]
{summary}

[등장인물]
{characters}

[지난 이야기 요약]
{history_summary}

[현재 게임 상태]
- 챕터: {chapter}
- 챕터 상황: {chapter_context}
- 확보 시간: {time_remaining}일
- 식량: {food}/100
- 병사 사기: {morale}/100
- 백성 지지도: {loyalty}/100
- 조정 분열도: {faction_split} (-100=완전 주화파, +100=완전 척화파)
- 분기 플래그: {flags}

[답변 길이 가이드]
{msg_len_guide}

[규칙]
1. 반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
2. replies 배열의 순서와 구성(scene/character 비율)은 당신이 자유롭게 결정합니다.
   예) scene → character → character → scene → character 순서도 가능합니다.
3. 게임 상태 수치(식량, 사기 등)를 이야기에 반영하세요.
   - 식량 20 이하: 병사들이 굶주림을 호소
   - 사기 20 이하: 탈영 분위기, 김상헌도 목소리가 작아짐
   - faction_split > 50: 조정이 척화 일색으로 분열
4. 사용자 행동의 결과로 수치가 변해야 한다면 state_changes에 delta값으로 명시하세요.
   - 예) 식량이 10 줄어야 한다면: "food": -10
   - 절대값(예: "food": 30)으로 쓰지 마세요.
5. 챕터가 전환되어야 한다면 chapter_transition에 다음 챕터 이름을 넣으세요.
   챕터 순서: prologue → act1 → act2 → act3 → epilogue

[응답 JSON 형식]
{{
  "replies": [
    {{
      "type": "scene",
      "char_name": null,
      "content": "상황 묘사 텍스트"
    }},
    {{
      "type": "character",
      "char_name": "캐릭터 이름 (등장인물 목록에 있는 이름 그대로)",
      "content": "캐릭터 대사"
    }}
  ],
  "state_changes": {{
    "food": -5,
    "morale": 10
  }},
  "chapter_transition": null,
  "history_summary": "지금까지의 진황상황 요약"
}}
"""

# =====================================================================
# 프롬프트 조립 로직
# =====================================================================

def build_system_prompt(req: ChatRequest) -> str:
    """
    요청된 데이터를 바탕으로 AI에게 전달할 최종 시스템 프롬프트를 생성합니다.
    """
    characters_text = "\n".join(
        f"- {c.name}: {c.summary}" for c in req.scenario.characters
    )
    gs = req.game_state
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        title=req.scenario.title,
        summary=req.scenario.summary,
        characters=characters_text,
        chapter=gs.chapter,
        chapter_context=gs.chpater_context,
        history_summary = req.history_summary,
        time_remaining=gs.time_remaining,
        food=gs.food,
        morale=gs.morale,
        loyalty=gs.loyalty,
        faction_split=gs.faction_split,
        flags=json.dumps(gs.flags, ensure_ascii=False), # 딕셔너리를 문자열로 변환
        msg_len_guide=MSG_LEN_GUIDE.get(req.msg_len, MSG_LEN_GUIDE["normal"]),
    )

def build_history_messages(history: List[HistoryItem]) -> List[Dict[str, str]]:
    """
    Django에서 넘어온 대화 기록(history)을 OpenAI API 형식(role, content)으로 변환합니다.
    - user 타입 → role: user
    - 나머지(scene, character) → role: assistant
    """
    messages = []
    for item in history:
        if item.type == "user":
            messages.append({"role": "user", "content": item.content})
        else:
            # scene이나 character 메시지는 assistant 발화로 취급
            # 연속된 assistant 메시지는 하나의 턴으로 묶어서 토큰 최적화 및 문맥 유지
            if messages and messages[-1]["role"] == "assistant":
                messages[-1]["content"] += f"\n[{item.type}] {item.content}"
            else:
                messages.append({"role": "assistant", "content": f"[{item.type}] {item.content}"})
                
    return messages