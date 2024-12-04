class WordDeclension {
  constructor(element) {
    this.singularForm = element?.dataset.singular || 'Секунду';
    this.fewForm = element?.dataset.few || 'Секунды';
    this.pluralForm = element?.dataset.plural || 'Секунд';
  }
  getForm(time) {
    if (time % 10 === 1 && time % 100 !== 11) {
      return this.singularForm;
    } else if ([2, 3, 4].includes(time % 10) && ![12, 13, 14].includes(time % 100)) {
      return this.fewForm;
    } else {
      return this.pluralForm;
    }
  }
}

class RedirectionTimer {
  constructor(timerId, countdownSeconds, redirectUrl) {
    this.timerElement = document.getElementById(timerId);
    if (!this.timerElement) {
      console.error(`Element with ID ${timerId} not found.`);
      return;
    }
    this.counterElement = this.timerElement.querySelector('#countdown');
    this.secondsWordElement = this.timerElement.querySelector('#seconds-text');
    this.declension = this.secondsWordElement ? new WordDeclension(this.secondsWordElement) : null;
    this.redirectText = this.timerElement.dataset.redirectText || 'Переадресация...';
    this.timeLeft = countdownSeconds;
    this.redirectUrl = redirectUrl;
    this.startTimer();
  }

  startTimer() {
    const timerInterval = setInterval(() => {
      if (this.timeLeft <= 0) {
        clearInterval(timerInterval);
        this.timerElement.textContent = this.redirectText;
        window.location.href = this.redirectUrl;
      } else {
        if (this.counterElement) {
          this.counterElement.textContent = this.timeLeft;
        }
        if (this.secondsWordElement && this.declension) {
          this.secondsWordElement.textContent = this.declension.getForm(this.timeLeft);
        }
        this.timeLeft--;
      }
    }, 1000);
  }
}
