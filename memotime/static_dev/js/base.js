document.addEventListener('DOMContentLoaded', function () {
	const djangoNowElement = document.getElementById('django-now');
	const djangoNowString = djangoNowElement.getAttribute('data-django-now');
	const djangoNow = new Date(djangoNowString.replace(' ', 'T'));
	const jsNow = new Date();
	const differenceInMilliseconds = jsNow - djangoNow;
	if (differenceInMilliseconds / (60 * 60 * 1000) < 24) {
		djangoNowElement.textContent = jsNow.getFullYear();
	}
});

// theme-toggle.js

document.addEventListener("DOMContentLoaded", function () {
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const themeIcon = themeToggleBtn.querySelector("img");

  // Получаем сохранённую тему из localStorage или используем светлую по умолчанию
  const savedTheme = localStorage.getItem("theme") || "light";

  // Устанавливаем начальную тему и иконку при загрузке страницы
  function setInitialTheme() {
    document.documentElement.setAttribute("data-theme", savedTheme);  // Устанавливаем тему
    const iconSrc = savedTheme === "dark" ? themeToggleBtn.dataset.light : themeToggleBtn.dataset.dark;
    themeIcon.src = iconSrc;  // Устанавливаем картинку
  }

  setInitialTheme(); // Устанавливаем начальную тему и картинку

  // Функция для переключения темы
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark"; // Меняем тему

    // Сохраняем новую тему в localStorage
    localStorage.setItem("theme", newTheme);

    // Устанавливаем новую тему на странице
    document.documentElement.setAttribute("data-theme", newTheme);

    // Меняем картинку на кнопке
    const iconSrc = newTheme === "dark" ? themeToggleBtn.dataset.light : themeToggleBtn.dataset.dark;
    themeIcon.src = iconSrc;
  }

  // Добавляем обработчик клика на кнопку для переключения темы
  themeToggleBtn.addEventListener("click", toggleTheme);
});
