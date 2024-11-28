import profile
from datetime import datetime
from traceback import print_tb

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
import locale
from babel.dates import format_date, parse_date

MONTHS = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}
def convert_date(input_date):
    try:
        parts= input_date.strip().split()
        if len(parts) != 3:
            raise ValueError("Дата должна быть в формате 'день месяц год'.")
        day, month, year = parts
        month = MONTHS.get(month.lower())

        if not month:
            raise ValueError(f"Месяц '{month}' не распознан.")
        formatted_date = f"{year}-{month}-{day.zfill(2)}"
        return datetime.strptime(formatted_date, '%Y-%m-%d').date()
    except ValueError as e:
        return f'Ошибка: {e}'
def main_window(request):
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    city = request.GET.get('city')
    if not city:
        if request.user.is_authenticated:
            city = getattr(request.user.profile, 'city', "Москва")
        else:
            city = "Москва"

    API_KEY = '076346f55592d4a002d75b2175ed273c'
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru"

    error_message = None
    weather_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get('cod') != '200':
            error_message = "Такое место не найдено."
        else:
            print("Данные " + str(data))
            for item in data['list']:
                date_time = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                weather_data.append({
                    "date": format_date(date_time, format='d MMMM y', locale='ru'),
                    "time": date_time.strftime('%H:%M'),
                    "temp": round(item['main']['temp'],),
                    "icon": item['weather'][0]['icon'],
                    "description": item['weather'][0]['description'].capitalize(),
                })
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        error_message = "Ошибка при запросе данных."

    return render(request, 'weather/weather.html', {
        'weather_data': weather_data,
        'city': city,
        'error_message': error_message,
    })
def get_weather_details(request):
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    date = request.GET.get('date')
    weekday = request.GET.get('weekday')
    city = request.GET.get('city', 'Бали')
    API_KEY = '076346f55592d4a002d75b2175ed273c'
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()

        formatted_date = convert_date(date)
        min_temp = float('inf')
        max_temp = float('-inf')
        icon = None
        description = None
        humidity = None
        wind_speed = None

        # Итерация по погоде на несколько часов
        for item in data['list']:
            item_date = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S').date()
            if item_date == formatted_date:
                # Обновляем минимальную и максимальную температуру для этого дня
                min_temp = min(min_temp, item['main']['temp_min'])
                max_temp = max(max_temp, item['main']['temp_max'])

                if icon is None:
                    icon = item['weather'][0]['icon']
                    description = item['weather'][0]['description'].capitalize()
                    humidity = item['main']['humidity']
                    wind_speed = item['wind']['speed']

        if min_temp == float('inf') or max_temp == float('-inf'):
            return JsonResponse({"error": "Не удалось получить данные для указанной даты."})
        detailed_data = {
            "date": date,
            "weekday": weekday,
            "icon": icon,
            "temp": round(item['main']['temp'], 1),
            "temp_min": round(min_temp, 1),
            "temp_max": round(max_temp, 1),
            "description": description,
            "humidity": humidity,
            "wind_speed": wind_speed
        }

        print("Конечные данные " + str(detailed_data))
        return JsonResponse(detailed_data)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return JsonResponse({"error": "Ошибка при запросе данных."})
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
@login_required
def profile_view(request):
    user = request.user
    first_name = user.first_name
    username = user.username
    city = user.profile.city
    context = {
        "first_name": first_name,
        "username": username,
        "city": city,
    }

    return render(request, 'weather/profile.html', context)
def edit_profile(request):
    print("Метод " + request.method)
    if request.method == "POST":
        user = request.user
        old_password = request.POST['password_old']
        if not user.check_password(old_password):
            messages.error(request, "Старый пароль неверен")
            print(request.session.get('_messages'))
            return redirect(profile_view)
        try:
            name = request.POST['name']
            new_password = request.POST['password']
            city = request.POST['city']
            username = request.POST['username']
            user.username = username
            user.first_name = name
            if not new_password == "":
                user.set_password(new_password)

            if hasattr(user, 'profile'):  # Проверка, что профиль существует
                user.profile.city = city
                user.profile.save()
            else:
                user.profile = Profile.objects.create(user=user, city=city)

            user.save()
            login(request, user)
            messages.success(request, "Профиль успешно изменен!")
            print(request.session.get('_messages'))
        except Exception as e:
            print("Ошибка при изменении профиля" + str(e))
            messages.error(request, f"Ошибка при изменении профиля " + str(e))

        return redirect(profile_view)
    return redirect(main_window)
def delete_profile(request):
    user = request.user
    old_password = request.POST['password_old']
    if not user.check_password(old_password):
        messages.error(request, "Старый пароль неверен")
        return redirect(profile_view)
    user.delete()
    return redirect(main_window)
