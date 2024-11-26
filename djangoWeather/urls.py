import profile

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, re_path, include
from rest_framework.authtoken.views import obtain_auth_token

from weather.views import main_window, login_view, logout_view, register_view, autocomplete_city, profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('weather/')),
    path('weather/', main_window, name='weather'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),  # Регистрация
    path('logout/', logout_view, name='logout'),
    path('autocomplete_city/', autocomplete_city, name='autocomplete_city'),
    path('profile/', profile_view, name='profile'),
]
