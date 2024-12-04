let lastClickTime = 0;
let clickCount = 0;
const maxClicks = 3;
const warningTimeout = 5000;

function show_notification_from_button(button) {
  const title = button.getAttribute("data-title");
  const text = button.getAttribute("data-text");
  const warning = button.getAttribute("data-warning");

  show_notification(title, text, warning);
}

function show_notification(title, text, warning) {
  const currentTime = Date.now();

  if (currentTime - lastClickTime < 1000) {
    clickCount++;
  } else {
    clickCount = 1;
  }

  lastClickTime = currentTime;

  if (clickCount > maxClicks) {
    show_warning_modal(warning);
    return;
  }
  var popup = document.createElement('div');
  popup.className = 'popup';

  var closeButton = document.createElement('button');
  closeButton.className = 'close-btn';
  closeButton.innerText = 'X';
  closeButton.onclick = function () {
    popup.classList.remove('show');
    setTimeout(function () {
      popup.style.display = 'none';
    }, 500);
  };

  var heading = document.createElement('h3');
  heading.innerText = title;

  var content = document.createElement('p');
  content.innerText = text;

  popup.appendChild(closeButton);
  popup.appendChild(heading);
  popup.appendChild(content);

  document.body.appendChild(popup);

  setTimeout(function () {
    popup.classList.add('show');
  }, 0);

  setTimeout(function () {
    popup.classList.remove('show');
    setTimeout(function () {
      popup.style.display = 'none';
    }, 500);
  }, 3000);
}

function show_warning_modal(warningText) {
  const modal = document.createElement('div');
  modal.className = 'fullscreen-modal';
  modal.innerText = warningText;
  document.body.appendChild(modal);
  setTimeout(function () {
    modal.remove();
    clickCount = 0;
  }, warningTimeout);
}
