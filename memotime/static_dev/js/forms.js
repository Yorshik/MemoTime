class FormAnimator {
  constructor(formClass) {
    this.formClass = formClass;
    this.form = document.querySelector(`.${this.formClass}`);
    if (this.form) {
      this.init();
    }
  }
  init() {
    const formElements = this.form.querySelectorAll('.form-floating, .btn, .password-reset-link', '.form-control',);
    formElements.forEach((element, index) => {
      element.style.opacity = '0';
      element.style.transform = 'translateY(20px)';
      setTimeout(() => {
        element.style.transition = 'all 0.25s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
      }, 100 * index);
    });
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const formFields = document.querySelectorAll('form input:not([type="hidden"])');
  formFields.forEach(field => {
    field.classList.add('form-control');
    if (field.id) {
      const label = document.querySelector(`label[for="${field.id}"]`);
      if (label) {
        field.placeholder = label.textContent;
      }
    }
  });
  new FormAnimator('animate');
});