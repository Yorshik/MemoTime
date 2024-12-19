document.getElementById('week').addEventListener('change', function() {
  const showEven = this.checked;
  const items = document.querySelectorAll('.time-schedule-item');
  items.forEach(item => {
      const isEven = item.getAttribute('data-even').toLocaleLowerCase() === 'true';
      item.style.display = showEven ? (isEven ? 'flex' : 'none') : (!isEven ? 'flex' : 'none');
  });
});

// Initial filter on page load
const weekCheckbox = document.getElementById('week');
weekCheckbox.dispatchEvent(new Event('change'));