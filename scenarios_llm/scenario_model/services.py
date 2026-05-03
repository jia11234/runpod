import json
from fastapi import HTTPException
from openai import AsyncOpenAI
from scenarios_llm.scenario_model.schemas import ChatRequest, ChatResponse, Reply
from scenarios_llm.scenario_model.prompts import build_system_prompt, build_history_messages

# OpenAI 클라이언트 초기화 (main.py에서 이미 load_dotenv를 실행했으므로 환경변수를 읽어옴)
client = AsyncOpenAI() 

async def generate_chat_response(req: ChatRequest) -> ChatResponse:
    """
    프롬프트를 조립하고 OpenAI API를 호출하여 최종 응답을 반환하는 서비스 함수.
    """
    # 1. 프롬프트 및 대화 기록 조립
    system_prompt = build_system_prompt(req)
    history_messages = build_history_messages(req.history)

    # 2. OpenAI API에 보낼 최종 메시지 배열 구성
    messages = [
        {"role": "system", "content": system_prompt},
        *history_messages,
        {"role": "user", "content": req.user_message},
    ]

    # 3. OpenAI API 호출
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"}, # JSON 출력을 강제함
            temperature=0.85,
            max_tokens=2000,
        )
    except Exception as e:
        # API 통신 장애 처리
        raise HTTPException(status_code=502, detail=f"OpenAI 호출 실패: {str(e)}")

    # 4. 결과 파싱 및 에러 핸들링
    raw = response.choices[0].message.content

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI 응답 파싱 실패 (JSON 포맷 에러)")

    # 5. replies 배열 검증 및 정제
    replies = []
    for block in result.get("replies", []):
        replies.append(Reply(
            type=block.get("type", "scene"),
            char_name=block.get("char_name"),
            content=block.get("content", ""),
        ))

    if not replies:
        raise HTTPException(status_code=500, detail="AI가 빈 응답(replies)을 반환했습니다.")

    # 6. 최종 정제된 Pydantic 모델로 반환
    return ChatResponse(
        replies=replies,
        state_changes=result.get("state_changes", {}),
        chapter_transition=result.get("chapter_transition"),
        history_summary=result.get("history_summary", req.history_summary)
    )