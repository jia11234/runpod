from django.contrib import admin
from .models import Persona, CharMessages, CharModeInfo, CharRoomSettings

admin.site.register(CharModeInfo)
admin.site.register(CharRoomSettings)
admin.site.register(CharMessages)
admin.site.register(Persona)