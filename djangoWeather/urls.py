from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from weather.views import main_window, login_view, logout_view, register_view, autocomplete_city, profile_view, \
    edit_profile, delete_profile, get_weather_details

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('weather/')),
    path('weather/', main_window, name='weather'),
    path('weather/details/', get_weather_details, name='get_weather_details'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('autocomplete_city/', autocomplete_city, name='autocomplete_city'),
    path('profile/', profile_view, name='profile'),
    path('editProfile/', edit_profile, name='editProfile'),
    path('deleteProfile/', delete_profile, name='deleteProfile'),
]
