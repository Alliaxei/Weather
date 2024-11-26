from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
import locale
from babel.dates import format_date
def main_window(request):
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    city = request.GET.get('city', 'Москва')
    API_KEY = '076346f55592d4a002d75b2175ed273c'
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru"

    error_message = None
    weather_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        data = response.json()

        # Проверяем, что API вернул успешный ответ
        if data.get('cod') != '200':
            error_message = "Такое место не найдено."
        else:
            # Формируем данные о погоде
            for item in data['list'][::8]:
                date_obj = datetime.strptime(item['dt_txt'].split(' ')[0], '%Y-%m-%d')
                weather_data.append({
                    "date": format_date(date_obj, format='d MMMM y', locale='ru'),
                    "weekday": datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%A'),
                    "icon": item['weather'][0]['icon'],
                    "temp": round(item['main']['temp'],),
                    "description": item['weather'][0]['description'].capitalize(),
                })
    except requests.exceptions.RequestException as e:
        # Логируем ошибку и устанавливаем сообщение об ошибке
        print(f"Ошибка при запросе данных: {e}")
        error_message = "Ошибка при запросе данных."

    return render(request, 'weather/weather.html', {
        'weather_data': weather_data,
        'city': city,
        'error_message': error_message,
    })
def autocomplete_city(request):
    API_KEY = '076346f55592d4a002d75b2175ed273c'
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    api_url = f"https://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}&lang=ru"
    response = requests.get(api_url)

    if response.status_code == 200:
        cities = response.json()
        city_list = [{"name": city.get('name', 'Неизвестный город')} for city in cities]
        print("JSON-ответ:", city_list)
        return JsonResponse(city_list, safe=False)

    print("Ошибка запроса к API:", response.text)
    return JsonResponse([], safe=False)
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(main_window)
        else:
            messages.error(request, 'Username OR password is incorrect')
    return render(request, 'weather/authorization/login.html')
def register_view(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Пароли не совпадают")
            return render(request, 'weather/authorization/register.html')

        first_name = request.POST['first_name']
        username = request.POST['username']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким логином уже существует")
            return render(request, 'weather/authorization/register.html')

        try:
            user = User.objects.create_user(username=username, password=password, first_name=first_name)
            user.save()
            login(request, user)
            return redirect(main_window)
        except Exception as e:
            messages.error(request, "Ошибка при регистрации")
            return render(request, 'weather/authorization/register.html')

    return render(request, 'weather/authorization/register.html')
def logout_view(request):
    logout(request)
    return redirect(main_window)

def profile_view(request):
    return render(request, 'weather/profile.html')