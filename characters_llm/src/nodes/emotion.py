import re
from langchain_core.prompts import PromptTemplate

def emotion_node(state, llm):
    print('🎭 [감정 판정] 왕의 기분 변화를 계산 중입니다...')
    user_input = state['messages'][-1].content
    king_name = state.get('king_name', '세조')
    core_values = state.get('core_values', '강력한 왕권과 법치')
    sensitive_topics = state.get('sensitive_topics', '단종 폐위, 계유정난')

    ALLOWED_EMOTIONS = ["평온", "슬픔", "분노", "기쁨", "당황"]

    EMOTION_JUDGE_PROMPT = """
    당신은 조선 왕 캐릭터 챗봇의 감정 판정기이다.
    사용자의 발화를 보고, 현재 왕이 느낄 감정을 하나만 판단하라.

    [현재 왕 정보]
    - 왕 이름: {king_name}
    - 핵심 가치: {core_values}
    - 민감 주제: {sensitive_topics}

    [감정 후보]
    - 평온
    - 슬픔
    - 분노
    - 기쁨
    - 당황

    [판정 기준]
    - 평온: 중립적 질문, 일반적인 대화, 공손한 요청
    - 슬픔: 죽음, 상실, 후회, 비극적 사건을 언급할 때
    - 분노: 무례함, 조롱, 비난, 왕권/정통성 공격, 민감 주제 공격
    - 기쁨: 칭찬, 존경, 업적 인정, 긍정적 반응
    - 당황: 예상 밖 질문, 시대에 맞지 않는 질문, 이해하기 어려운 현대적 표현

    [규칙]
    - 반드시 감정 후보 중 하나만 출력한다.
    - 설명, 이유, 문장부호를 쓰지 않는다.
    - 출력 예: 평온

    사용자 발화:
    {user_input}
    """

    prompt = PromptTemplate.from_template(EMOTION_JUDGE_PROMPT)
    chain = prompt | llm  
    
    try:
        res = chain.invoke({
            'king_name': king_name,
            'core_values': core_values,
            'sensitive_topics': sensitive_topics,
            'user_input': user_input
        })
        
        raw_output = res.content.strip() if hasattr(res, "content") else str(res).strip()
        
        if raw_output in ALLOWED_EMOTIONS:
            emotion = raw_output
        else:
            emotion = "평온"

    except Exception as e:
        print(f"⚠️ [감정 판정 오류]: {e}")
        emotion = "평온"

    print(f"↳ [현재 감정] {emotion}")

    return {
        "emotion": emotion
    }