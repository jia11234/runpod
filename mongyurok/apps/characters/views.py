from django.shortcuts import render, get_object_or_404
from .models import Persona, CharModeInfo, CharRoomSettings, CharMessages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings

def character_list(request) :
    """
    독대 모드 캐릭터 전체 조회
    """
    characters = CharModeInfo.objects.all()

    return render(request, "characters/main.html", {
        "characters" : characters
    })


def character_detail(request, character_id) :
    """
    독대 모드 캐릭터 클릭 시 해당 캐릭터 상세보기.
    """
    character = get_object_or_404(CharModeInfo, id=character_id)

    return JsonResponse({
        "id" : character.id,
        "kor_name" : character.kor_name,
        "hanja_name" : character.hanja_name,
        "birth_to_death" : character.birth_to_death,
        "keywords" : [
            k for k in [
                character.keyword1,
                character.keyword2,
                character.keyword3
            ] if k
        ],
        "summary" : character.summary,
        "img_url": character.img_url.url if character.img_url else None
    })


@login_required(login_url="auths:login")
@require_POST
def persona_setting(request, character_id):
    """
    페르소나 설정 모달 POST 처리
    - 사용자가 대화 시작 전 모달에서 페르소나를 입력한다.
    - 입력값이 없으면 기본값을 사용한다.
    - 최종 페르소나를 저장한다.
    - 대화방을 생성한다.
    - 최초 상황 메시지를 저장한다.
    - 생성된 채팅방 URL을 JSON으로 반환한다.
    """

    # 어떤 왕과 대화할지 가져옴
    character = get_object_or_404(CharModeInfo, id=character_id)

    # 사용자가 아무것도 입력하지 않았을 때 사용할 기본값
    DEFAULT_PERSONALITY = "모든 행동에 민감하게 반응하는 성격"
    DEFAULT_IDENTITY = Persona.SelectIdentity.FARMER
    DEFAULT_VALUES = "밥 먹는 것이 최고고 모든 문제는 밥으로 해결 가능하다."
    DEFAULT_SCENE = "밥 먹다가 왕에게 갑자기 호출됐다."

    # 모달 폼에서 넘어온 값 가져오기
    req_personality = request.POST.get("personality", "").strip()
    req_identity = request.POST.get("identity", "").strip()
    req_values = request.POST.get("values", "").strip()
    req_first_scene = request.POST.get("first_scene", "").strip()

    # 입력값이 있으면 입력값 사용, 없으면 기본값 사용
    final_personality = req_personality or DEFAULT_PERSONALITY
    final_identity = req_identity or DEFAULT_IDENTITY
    final_values = req_values or DEFAULT_VALUES
    final_first_scene = req_first_scene or DEFAULT_SCENE

    # 이 채팅방에서 사용할 전용 페르소나 생성
    room_persona = Persona.objects.create(
        user=request.user,
        personality=final_personality,
        identity=final_identity,
        values=final_values,
        first_scene=final_first_scene
    )

    # 대화방 생성
    room = CharRoomSettings.objects.create(
        user=request.user,
        character=character,
        persona=room_persona
    )

    # 최초 상황을 메시지로 저장
    CharMessages.objects.create(
        room=room,
        type=CharMessages.MessageType.SITUATION,
        content=final_first_scene
    )

    return JsonResponse({
        "status": "success",
        "message": "페르소나가 설정되었습니다.",
        "room_id": room.id,
        "room_url": f"/chats/rooms/{room.id}/",
        "first_scene": final_first_scene
    })

@login_required(login_url="auths:login")
def char_room(request, room_id):
    """
    채팅방 입장 페이지
    - 생성된 대화방을 조회한다.
    - 해당 방의 메시지들을 가져온다.
    - char_room.html에 전달해서 채팅 화면을 보여준다.
    """


    room = get_object_or_404(
        CharRoomSettings,
        id=room_id,
        user=request.user
    )

    messages = room.messages.all()

    return render(request, "characters/chat_room.html", {
        "room": room,
        "messages": messages
    })

from asgiref.sync import sync_to_async
import httpx

@login_required(login_url="auths:login")
async def send_message(request, room_id):
    """
    채팅 메시지 비동기 전송
    - 사용자가 입력한 메시지를 DB에 저장한다.
    - 최근 대화 기록, 왕 정보, 사용자 페르소나를 모아서 FastAPI에 보낸다.
    - FastAPI에서 받은 AI 답변을 DB에 저장한다.
    - 새 메시지를 JSON으로 프론트에 반환한다.
    """

    # 프론트에서 보낸 사용자 입력값
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=400)

    user_text = request.POST.get("message", "").strip()

    if not user_text:
        return JsonResponse({"status": "error", "message": "내용을 입력해주세요."}, status=400)

    @sync_to_async
    def get_room_and_save_user_msg():
        """
        DB 작업 1
        - 채팅방 조회
        - 사용자 메시지 저장
        """


        room = get_object_or_404(
            CharRoomSettings,
            id=room_id,
            user=request.user
        )

        user_msg = CharMessages.objects.create(
            room=room,
            type=CharMessages.MessageType.USER,
            content=user_text
        )

        return room, {
            "type": user_msg.type,
            "content": user_msg.content,
            "created_at": user_msg.created_at.strftime("%Y-%m-%d %H:%M")
        }

    room, user_message = await get_room_and_save_user_msg()

    @sync_to_async
    def update_king_state(current_room, state):
        current_room.king_state = state
        current_room.save()

    @sync_to_async
    def build_payload(current_room):
        """
        DB 작업 2
        - 최근 메시지 10개 조회
        - 캐릭터 정보 조회
        - 페르소나 정보 조회
        - FastAPI에 보낼 payload 생성
        """
        

        recent_msgs = list(
            CharMessages.objects
            .filter(room=current_room)
            .order_by("-created_at")[:10]
        )

        history = [
            {
                "type": msg.type,
                "content": msg.content
            }
            for msg in reversed(recent_msgs)
        ]

        persona = current_room.persona
        character = current_room.character

        return {
            "user_message": user_text,
            "character": {
                "name": character.kor_name,
                "summary": character.summary
            },
            "persona": {
                "identity": persona.identity,
                "values": persona.values
            },
            "king_state" :current_room.king_state,
            "history": history
        }

    payload = await build_payload(room)

    fastapi_url = settings.CHARACTER_FASTAPI_URL

    try:
        # FastAPI 서버에 비동기 POST 요청
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(fastapi_url, json=payload)
            response.raise_for_status()

            # FastAPI 응답 JSON 파싱
            ai_data = response.json()

            # FastAPI가 {"reply": "..."} 형태로 준다고 가정
            ai_text = ai_data.get("reply", "")
        
            new_state = ai_data.get("king_state", room.king_state)

        @sync_to_async
        def save_ai_reply(current_room, content):
            """
            DB 작업 3
            - AI 답변을 캐릭터 메시지로 저장
            """


            char_msg = CharMessages.objects.create(
                room=current_room,
                type=CharMessages.MessageType.CHARACTER,
                content=content
            )

            return {
                "type": char_msg.type,
                "content": char_msg.content,
                "created_at": char_msg.created_at.strftime("%Y-%m-%d %H:%M")
            }

        character_message = await save_ai_reply(room, ai_text)
        king_state = await update_king_state(room, new_state)

        return JsonResponse({
            "status": "success",
            "character_message": character_message,
            "king_state" : king_state
        })

    except httpx.HTTPError as e:
        return JsonResponse({
            "status": "error",
            "message": f"AI 서버 통신 중 오류가 발생했습니다: {str(e)}"
        }, status=500)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"처리 중 오류가 발생했습니다: {str(e)}"
        }, status=500)