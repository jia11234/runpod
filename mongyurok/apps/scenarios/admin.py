from django.contrib import admin
from .models import SceneCharInfo, SceneMessage, SceneModeInfo, SceneRoomSetting, SceneChapter

admin.site.register(SceneCharInfo)
admin.site.register(SceneChapter)
admin.site.register(SceneMessage)
admin.site.register(SceneModeInfo)
admin.site.register(SceneRoomSetting)