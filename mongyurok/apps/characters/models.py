from django.db import models
from apps.auths.models import User

class Persona(models.Model) :
    """
    사용자가 독대 모드 시작 전에 설정한 페르소나 정보
    """
    class SelectIdentity(models.TextChoices) :
        FARMER = "farmer", "농부"
        SCHOLAR = "scholar", "유생"
        OFFICIAL = "official", "관료"
        GENERAL = "general", "장수"
        MERCHANT = "merchant", "상인"
        PHYSICIAN = "physician", "의원"
        EUNUCH = "eunuch", "내관"
        
    # user를 참조하고 user가 삭제되면 이 데이터도 같이 삭제(on_delete))
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    personality = models.CharField(max_length=20, default="모든 행동에 민감하게 반응하는 성격", verbose_name="성격")
    identity = models.CharField(max_length=20, choices=SelectIdentity.choices, default=SelectIdentity.FARMER ,verbose_name="신분")
    values = models.CharField(max_length=500, default="밥 먹는 것이 최고고 모든 문제는 밥으로 해결 가능하다." ,verbose_name="가치관")
    first_scene = models.TextField(max_length=1000, default="밥 먹다가 왕에게 갑자기 호출됐다." ,verbose_name="최초 상황")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta :
        db_table = "char_persona"

    def __str__(self):
        return f"{self.user}의 페르소나"

class CharModeInfo(models.Model) :
    """
    독대 모드 목록 & 캐릭터 설정 정보
    """
    # 왕 정보
    kor_name = models.CharField(max_length=10, verbose_name="왕 이름")
    hanja_name = models.CharField(max_length=10, verbose_name="왕 한자 이름")
    birth_to_death = models.CharField(max_length=10, verbose_name="생애")

    # 왕 성격 키워드
    keyword1 = models.CharField(max_length=50, blank=True, null=True, verbose_name="키워드1")
    keyword2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="키워드2")
    keyword3 = models.CharField(max_length=50, blank=True, null=True, verbose_name="키워드3")

    # 왕 업적 요약
    summary = models.TextField(max_length=200, verbose_name="왕 정보 요약")

    # 왕 이미지 (characters/taejo.png) 이런식으로 저장
    img_url = models.ImageField(upload_to="characters/")

    class Meta :
        # 실제 db에 저장될 이름
        db_table = "char_mode_info"
        # 조회할 때 어떤 기준으로 정렬할 것인가.
        ordering = ["kor_name"]

    def __str__(self):
        return self.kor_name
    

class CharRoomSettings(models.Model) :
    """
    독대 모드 대화방 설정 정보
    """
    class MessageLength(models.TextChoices) :
        SHORT = 'short', "짧게"
        NORMAL = 'normal', "보통"
        LONG = 'long', "길게"
        VERY_LONG = 'very_long', "매우 길게"

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="유저 ID")
    character = models.ForeignKey(CharModeInfo, on_delete=models.CASCADE, verbose_name="캐릭터 ID")
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="적용된 페르소나 ID")
    
    king_state = models.CharField(max_length=20, default="평온함", verbose_name="왕의 기분을 표시")

    message_length = models.CharField(max_length=20, choices=MessageLength.choices, default=MessageLength.NORMAL, verbose_name="응답 길이")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")

    class Meta :
        db_table = "char_room_settings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.character} 대화방"

class CharMessages(models.Model) :
    """
    사용자가 작성한 메시지 & 답변 메시지
    """
    class MessageType(models.TextChoices):
        SITUATION = "situation", "상황"
        USER = "user", "사용자"
        CHARACTER = "character", "캐릭터"

    room = models.ForeignKey(
        CharRoomSettings,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        verbose_name="메시지 타입"
    )

    content = models.TextField(verbose_name="메시지 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "char_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.room} - {self.get_type_display()}"