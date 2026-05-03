from langgraph.graph import StateGraph, END

from characters_llm.src.state import KingState

from characters_llm.src.nodes.emotion import emotion_node
from characters_llm.src.nodes.intent import intent_node
from characters_llm.src.nodes.retrieval import retrieve_node
from characters_llm.src.nodes.king import king_node
from characters_llm.src.nodes.scene import scene_node
from characters_llm.src.nodes.routers import route_intent

def build_graph(llm_analyzer, llm_generator, vectorstore):
    workflow = StateGraph(KingState)
    
    # 노드 추가 (람다 함수를 사용해 외부 모델/DB를 노드 안으로 주입)
    workflow.add_node('emotion', lambda state: emotion_node(state, llm_analyzer))
    workflow.add_node('intent', lambda state: intent_node(state, llm_analyzer))
    workflow.add_node('retrieve', lambda state: retrieve_node(state, vectorstore))
    workflow.add_node('king', lambda state: king_node(state, llm_generator))
    workflow.add_node('scene', lambda state: scene_node(state, llm_generator))
    
    # 엣지 연결 (대화 흐름 정의)
    workflow.set_entry_point('emotion')

    workflow.add_edge("emotion", "intent")

    workflow.add_conditional_edges(
        'intent',
        route_intent,
        {
            'retrieve': 'retrieve',
            'king': 'king'
        }
    )
    workflow.add_edge('retrieve', 'king')
    workflow.add_edge('king', 'scene')
    workflow.add_edge('scene', END)
    
    return workflow.compile()