def route_intent(state):
    """의도 분석 결과에 따라 RAG 검색 노드로 갈지, 답변 노드로 갈지 결정"""
    if state.get('need_rag', False):
        return 'retrieve'
    return 'king'