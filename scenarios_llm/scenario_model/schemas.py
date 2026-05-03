from pydantic import BaseModel
from typing import Optional, List, Dict

class Character(BaseModel):
    """등장인물 정보 스키마"""
    name: str
    summary: str

class Scenario(BaseModel):
    """시나리오 전체 정보 스키마"""
    title: str
    summary: str
    characters: List[Character]

class GameState(BaseModel):
    """현재 게임/유저의 상태 정보 스키마"""
    chapter: str = "prologue"
    chapter_context: str = ""
    time_remaining: int = 3
    food: int = 50
    morale: int = 50
    loyalty: int = 50
    faction_split: int = 0          # -100(주화) ~ +100(척화)
    flags: Dict = {}

class HistoryItem(BaseModel):
    """과거 대화 내역 단일 아이템 스키마"""
    type: str                        # "scene" | "user" | "character"
    content: str

class ChatRequest(BaseModel):
    """Django 서버에서 FastAPI로 보내는 채팅 생성 요청 스키마"""
    user_message: str
    msg_len: str = "normal"          # "short" | "normal" | "long" | "very_long"
    scenario: Scenario
    game_state: GameState
    history_summary: str
    history: List[HistoryItem] = []

class Reply(BaseModel):
    """AI가 생성한 개별 대사/상황 묘사 스키마"""
    type: str                        # "scene" | "character"
    char_name: Optional[str] = None
    content: str

class ChatResponse(BaseModel):
    """FastAPI에서 Django 서버로 돌려주는 최종 응답 스키마"""
    replies: List[Reply]
    state_changes: Dict = {}
    chapter_transition: Optional[str] = None
    history_summary: str