document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll("#btn-del");
  const modal = document.getElementById("delete-modal");
  const confirmDeleteBtn = document.getElementById("btn_yes");
  const cancelDeleteBtn = document.getElementById("btn_no");

  let targetUrl = ""; // Переменная для хранения ссылки

  // Обработчик для кнопок "Удалить"
  deleteButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Читаем ссылку из data-url атрибута
      targetUrl = button.dataset.url;

      // Показываем модальное окно
      modal.style.display = "flex";
    });
  });

  // Обработчик для кнопки "Да" в модальном окне
  confirmDeleteBtn.addEventListener("click", () => {
    console.log("Переход по ссылке:", targetUrl); // Проверка URL
    if (targetUrl) {
      window.location.href = targetUrl;
    }
  });

  // Обработчик для кнопки "Отмена"
  cancelDeleteBtn.addEventListener("click", () => {
    modal.style.display = "none"; // Скрыть модальное окно
    targetUrl = ""; // Сбросить сохранённый URL
  });

  // Закрытие модального окна при клике вне его содержимого
  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      targetUrl = "";
    }
  });
});