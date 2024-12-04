document.addEventListener('DOMContentLoaded', function () {
	const djangoNowElement = document.getElementById('django-now');
	const djangoNowString = djangoNowElement.getAttribute('data-django-now');
	const djangoNow = new Date(djangoNowString.replace(' ', 'T'));
	const jsNow = new Date();
	const differenceInMilliseconds = jsNow - djangoNow;
	if (differenceInMilliseconds / (60 * 60 * 1000) < 24) {
		djangoNowElement.textContent = jsNow.getFullYear();
	}
	const dropdowns = document.querySelectorAll('.nav-item.dropdown');
	dropdowns.forEach(dropdown => {
		const menu = dropdown.querySelector('.dropdown-menu');
		const toggle = dropdown.querySelector('.dropdown-toggle');
		let isClickOpened = false;
		toggle.addEventListener('click', (e) => {
			e.preventDefault();
			e.stopPropagation();

			isClickOpened = !isClickOpened;
			if (isClickOpened) {
				menu.classList.add('show', 'force-show');
				toggle.classList.add('active');
			} else {
				menu.classList.remove('force-show');
				setTimeout(() => {
					if (!menu.matches(':hover')) {
						menu.classList.remove('show');
						toggle.classList.remove('active');
					}
				}, 200);
			}
		});
		document.addEventListener('click', (e) => {
			if (!dropdown.contains(e.target)) {
				isClickOpened = false;
				menu.classList.remove('force-show');
				toggle.classList.remove('active');
				setTimeout(() => {
					if (!menu.matches(':hover')) {
						menu.classList.remove('show');
					}
				}, 200);
			}
		});
	});
});
