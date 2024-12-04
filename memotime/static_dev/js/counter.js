class RatingCounter {
  constructor(element) {
    this.element = element;
    this.counter = parseInt(this.element.getAttribute('data-counter'), 10);
    this.wordForms = JSON.parse(this.element.getAttribute('data-word-forms'));
  }

  getRatingWord(count) {
    if (count % 10 === 1 && count % 100 !== 11) {
      return this.wordForms[0];
    } else if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) {
      return this.wordForms[1];
    } else {
      return this.wordForms[2];
    }
  }

  updateElement() {
    const ratingWord = this.getRatingWord(this.counter);
    this.element.innerHTML = `<small class="text-muted">${this.counter} ${ratingWord}</small>`;
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const ratingElements = document.querySelectorAll('.rating-count');
  ratingElements.forEach(element => {
    const ratingCounter = new RatingCounter(element);
    ratingCounter.updateElement();
  });
});