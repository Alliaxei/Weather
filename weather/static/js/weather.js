document.addEventListener('DOMContentLoaded', function () {

    // Переключение темы
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) body.classList.add(savedTheme);
    themeToggle.addEventListener('click', () => {
        const isDarkTheme = body.classList.toggle('dark-theme');
        localStorage.setItem('theme', isDarkTheme ? 'dark-theme' : '');
    });

    // Горизонтальная прокрутка контейнера
    const container = document.querySelector('.card-container.scrollable');
    container.addEventListener('wheel', function (event) {
        event.preventDefault();
        container.scrollBy({
            left: event.deltaY > 0 ? 100 : -100,
            behavior: 'smooth',
        });
    });

    // Поиск города с автодополнением
    const cityInput = document.getElementById('city-search');
    const suggestionsBox = document.createElement('div');
    suggestionsBox.id = 'suggestions';
    suggestionsBox.classList.add('suggestions-box');
    document.body.appendChild(suggestionsBox);

    cityInput.addEventListener('input', () => {
        const query = cityInput.value;
        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        fetch(`/autocomplete_city/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                if (data.length === 0) {
                    suggestionsBox.style.display = 'none';
                    return;
                }

                suggestionsBox.style.display = 'block';
                const rect = cityInput.getBoundingClientRect();
                suggestionsBox.style.top = `${rect.bottom + window.scrollY}px`;
                suggestionsBox.style.left = `${rect.left + window.scrollX}px`;

                data.forEach(city => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.textContent = city.name;
                    suggestionItem.classList.add('suggestionItem');

                    suggestionItem.addEventListener('click', () => {
                        cityInput.value = city.name;
                        suggestionsBox.style.display = 'none';
                    });

                    suggestionsBox.appendChild(suggestionItem);
                });
            });
    });

    // Закрытие предложений при клике вне элемента
    document.addEventListener('click', (e) => {
        if (!suggestionsBox.contains(e.target) && e.target !== cityInput) {
            suggestionsBox.style.display = 'none';
        }
    });

});
// Функция для загрузки подробных данных о погоде
function loadWeatherDetails(date) {
    const city = document.getElementById('city-search').value;
    fetch(`/weather/details/?date=${date}&city=${city}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received data:", data);
            document.getElementById("modal-date").textContent = date;
            document.getElementById("modal-weekday").textContent = data.weekday;
            document.getElementById("modal-icon").src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
            document.getElementById("modal-temperature").textContent = data.temp;
            document.getElementById("modal-temp-min").textContent = data.temp_min;
            document.getElementById("modal-temp-max").textContent = data.temp_max;
            document.getElementById("modal-description").textContent = data.description;
            document.getElementById("modal-humidity").textContent = data.humidity;
            document.getElementById("modal-wind-speed").textContent = data.wind_speed;

            document.getElementById("weatherModal").style.display = "block";
        })
        .catch(error => {
            console.error("Error fetching weather details:", error);
        });
}

function toggleDropdown() {
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
}

function closeModal() {
    document.getElementById('weatherModal').style.display = 'none';
}
