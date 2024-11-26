document.addEventListener('DOMContentLoaded', function () {

    //Переключение темы
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) body.classList.add(savedTheme);
    themeToggle.addEventListener('click', () => {
        const isDarkTheme = body.classList.toggle('dark-theme');
        localStorage.setItem('theme', isDarkTheme ? 'dark-theme' : '');
    });

    const container = document.querySelector('.card-container.scrollable');
    container.addEventListener('wheel', function (event) {
        event.preventDefault();
        container.scrollBy({
            left: event.deltaY > 0 ? 100 : -100,
            behavior: 'smooth',
        });
    });

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

        document.addEventListener('click', (e) => {
            if (!suggestionsBox.contains(e.target) && e.target !== cityInput) {
                suggestionsBox.style.display = 'none';
            }
        });
});

function toggleDropdown() {
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
}