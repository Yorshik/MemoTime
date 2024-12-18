document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll("#btn-del");
  const modal = document.getElementById("delete-modal");
  const confirmDeleteBtn = document.getElementById("btn_yes");
  const cancelDeleteBtn = document.getElementById("btn_no");
  deleteButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetUrl = button.dataset.url;
      modal.style.display = "flex";
      modal.dataset.url = targetUrl;
    });
  });
  confirmDeleteBtn.addEventListener("click", () => {
    const targetUrl = modal.dataset.url;

    if (targetUrl) {
      $.ajax({
        type: 'POST',
        url: targetUrl,
        data: {
          csrfmiddlewaretoken: document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        success: function (data) {
          if (data.status === 'ok') {
            modal.style.display = "none";
            window.location.reload();
          }
        }

      });
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
});