from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage
from langchain_community.vectorstores import Chroma

from characters_llm.src.models import load_models, load_embeddings
from characters_llm.src.graph import build_graph
from characters_llm.src.config import KING_CONFIG_FALLBACK, DB_PATH


app = FastAPI()

runtime = None


def get_runtime():
    global runtime

    if runtime is None:
        models = load_models()

        llm_analyzer = models["analyzer"]
        llm_generator = models["generator"]

        embeddings = load_embeddings()

        vectorstore = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embeddings
        )

        graph = build_graph(
            llm_analyzer=llm_analyzer,
            llm_generator=llm_generator,
            vectorstore=vectorstore
        )

        runtime = {
            "graph": graph
        }

    return runtime


class CharacterInfo(BaseModel):
    name: str
    summary: str


class PersonaInfo(BaseModel):
    identity: str
    values: str


class HistoryMessage(BaseModel):
    type: str
    content: str


class ChatRequest(BaseModel):
    user_message: str
    character: CharacterInfo
    persona: PersonaInfo
    history: List[HistoryMessage]


@app.post("/characters/chats")
async def chat(req: ChatRequest):
    runtime = get_runtime()
    graph = runtime["graph"]
    king_name = req.character.name

    king_config = KING_CONFIG_FALLBACK.get(
        king_name,
        {
            "persona_summary": req.character.summary,
            "speech_style": "위엄 있고 단호한 조선 왕의 말투",
            "core_values": "왕권, 질서, 백성",
            "sensitive_topics": "왕권 훼손, 무례한 태도"
        }
    )

    state = {
        "messages": [HumanMessage(content=req.user_message)],
        "king_name": king_name,
        "persona_summary": king_config["persona_summary"],
        "speech_style": king_config["speech_style"],
        "core_values": king_config["core_values"],
        "sensitive_topics": king_config["sensitive_topics"],
        "user_role": req.persona.identity,
        "emotion" : "평온",
        "intent": "",
        "need_rag": False,
        "search_queries": [],
        "reasoning": "",
        "retrieved_context": "",
        "scenario": "",
    }

    result = await graph.ainvoke(state)

    messages = result.get("messages", [])
    reply = messages[-1].content if messages else "과인이 잠시 침묵하노라."

    scenario = result.get("scenario", "")

    return {
        "reply": reply,
        "scenario": scenario
    }