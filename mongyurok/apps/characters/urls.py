from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
    path('', views.character_list, name='main'),
    # 캐릭터 목록 페이지
    path("characters/",views.character_list,name="character_list"),

    # 캐릭터 상세보기 (모달용 JSON)
    path("characters/<int:character_id>/detail/",views.character_detail,name="character_detail"),

    # 페르소나 설정 (모달 POST)
    path("characters/<int:character_id>/persona/",views.persona_setting,name="persona_setting"),

    # 채팅방 입장
    path("rooms/<int:room_id>/",views.char_room,name="char_room"),

    # 메시지 비동기 전송
    path("rooms/<int:room_id>/send/",views.send_message,name="send_message"),
]