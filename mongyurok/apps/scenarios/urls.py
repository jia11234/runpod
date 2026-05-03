from django.urls import path
from . import views

app_name = "scenarios"

urlpatterns = [
    # GET /scenes/ : 전체 시나리오 목록 조회
    path("", views.main_scenarios, name="main_scenarios"), 
    
    # GET /scenes/1/ : 특정 시나리오 상세 조회
    path("<int:scene_id>/", views.scene_detail, name="scene_detail"), 

    # POST /scenes/1/rooms/ : 특정 시나리오에 방(room) 생성
    path("<int:scene_id>/chats/", views.room_create, name="room_create"),

    # GET /rooms/10/ : 특정 방 상세 화면 조회
    path("chats/<int:room_id>/", views.room_detail, name="room_detail"),

    # POST /rooms/10/persona/ : 특정 방에 페르소나 설정(생성)
    path("chats/<int:room_id>/persona/", views.setup_persona, name="setup_persona"),
    
    # POST /rooms/10/messages/ : 특정 방에 메시지 생성(채팅 전송)
    path("chats/<int:room_id>/messages/", views.send_chat, name="send_chat"),
]