from django.urls import path
from . import views

app_name = 'auths'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('send-code/', views.send_verification_code, name='send_code'),
    path('code-confirm/', views.code_confirm, name='code_confirm'),
    path('sign/', views.sign_view, name='sign'),
    path('sign/sign-form/', views.sign_form_view, name='sign_form'),
    path('sign/sign-up/', views.sign_up, name='sign_up'),
    path('find/', views.password_find, name='find'),
    path("find/reset/", views.password_reset, name="password_reset"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path('logout/', views.logout_view, name='logout'),
]