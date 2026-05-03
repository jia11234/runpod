from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/pwd-change/', views.pwd_change, name='pwd_change'),
    path('mypage/delete-account/', views.delete_account, name='delete_account'),
]