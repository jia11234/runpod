from fastapi import FastAPI

from characters_llm.main import chat as character_chat
from characters_llm.main import ChatRequest as CharacterChatRequest

from scenarios_llm.main import chat_endpoint as scenario_chat
from scenarios_llm.scenario_model.schemas import ChatRequest as ScenarioChatRequest, ChatResponse

app = FastAPI()


@app.post("/characters/chats")
async def characters_chat(req: CharacterChatRequest):
    return await character_chat(req)


@app.post("/scenarios/chats", response_model=ChatResponse)
async def scenarios_chat(req: ScenarioChatRequest):
    return await scenario_chat(req)


@app.get("/health")
def health():
    return {"status": "ok"}