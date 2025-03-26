document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll("#btn-del");
  const modal = document.getElementById("delete-modal");
  const confirmDeleteBtn = document.getElementById("btn_yes");
  const cancelDeleteBtn = document.getElementById("btn_no");
  const modalQuestion = modal.querySelector("h3");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetUrl = button.dataset.url;
      const question = button.dataset.question;

      // Проверяем, есть ли URL, чтобы избежать пустых запросов
      if (!targetUrl) {
        console.error("No target URL specified for this button.");
        return;
      }

      modal.style.display = "flex";
      modal.dataset.url = targetUrl;

      modalQuestion.textContent = question
        ? question
        : modalQuestion.dataset.defaultText
    });
  });

  confirmDeleteBtn.addEventListener("click", () => {
    const targetUrl = modal.dataset.url;

    if (targetUrl) {
      $.ajax({
        type: "POST",
        url: targetUrl,
        data: {
          csrfmiddlewaretoken: document.querySelector('[name="csrfmiddlewaretoken"]').value,
        },
        success: function (data) {
          if (data.status === "ok") {
            modal.style.display = "none";
            window.location.reload(); // Перезагрузка страницы
          } else {
            window.location.reload();
          }
        },
      });
    } else {
      console.error("No target URL found in modal dataset.");
      modal.style.display = "none";
    }
  });

  cancelDeleteBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  // Сохраняем стандартный текст вопроса при загрузке
  modal.querySelector("h3").dataset.defaultText = modal.querySelector("h3").textContent;
});
