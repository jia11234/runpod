from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from scenarios_llm.scenario_model.schemas import ChatRequest, ChatResponse
from scenarios_llm.scenario_model.services import generate_chat_response

app = FastAPI()

@app.post("/scenarios/chats", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    클라이언트(Django)로부터 채팅 데이터를 받아 AI 답변을 생성합니다.
    모든 비즈니스 로직은 services.py에 위임합니다.
    """
    # services 모듈의 비즈니스 로직 호출
    result = await generate_chat_response(req)
    return result

@app.get("/health")
async def health_check():
    """
    서버가 정상적으로 구동되고 있는지 확인하는 헬스체크 엔드포인트입니다.
    """
    return {"status": "ok", "message": "FastAPI 서버가 정상 작동 중입니다."}