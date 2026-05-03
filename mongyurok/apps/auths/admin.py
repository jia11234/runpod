from django.contrib import admin
from .models import User, UserManager, EmailVerification

admin.site.register(User)
admin.site.register(EmailVerification)