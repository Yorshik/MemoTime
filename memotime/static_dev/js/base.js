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

document.addEventListener("DOMContentLoaded", () => {
	const themeToggleBtn = document.getElementById("theme-toggle-btn");
	const themeIcon = themeToggleBtn.querySelector("img");

	function setTheme(theme) {
		document.documentElement.setAttribute("data-theme", theme);
		document.cookie = `theme=${theme}; path=/; max-age=31536000`;

		const iconSrc =
			theme === "dark"
				? themeToggleBtn.dataset.light
				: themeToggleBtn.dataset.dark;
		themeIcon.src = iconSrc;
	}

	function getCookie(name) {
		const value = `; ${document.cookie}`;
		const parts = value.split(`; ${name}=`);
		if (parts.length === 2) return parts.pop().split(";").shift();
	}

	const savedTheme = getCookie("theme") || "light";
	setTheme(savedTheme);

	themeToggleBtn.addEventListener("click", () => {
		const currentTheme = document.documentElement.getAttribute("data-theme");
		const newTheme = currentTheme === "dark" ? "light" : "dark";
		setTheme(newTheme);
	});
});