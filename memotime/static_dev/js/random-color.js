// Функция для генерации случайного пастельного цвета
function generateRandomColor() {
  const r = Math.floor(Math.random() * 56) + 200; // Значения от 200 до 255
  const g = Math.floor(Math.random() * 56) + 200;
  const b = Math.floor(Math.random() * 56) + 200;
  const alpha = 0.75; // Прозрачность 75%
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Функция для затемнения цвета (уменьшение яркости)
function darkenColor(color, factor = 0.1) {
  const rgba = color.match(/\d+/g); // Получаем числа из rgba
  let r = parseInt(rgba[0]);
  let g = parseInt(rgba[1]);
  let b = parseInt(rgba[2]);

  // Затемняем каждый компонент цвета
  r = Math.max(0, r * factor);
  g = Math.max(0, g * factor);
  b = Math.max(0, b * factor);

  return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
}

// Применяем стили к каждому элементу time-schedule-item
document.addEventListener("DOMContentLoaded", function() {
  const timeScheduleItems = document.querySelectorAll('.time-schedule-item');

  timeScheduleItems.forEach(function(item) {
    const randomColor = generateRandomColor(); // Генерация случайного цвета

    // Устанавливаем случайный цвет фона
    item.style.backgroundColor = randomColor;

    // Получаем темный цвет для текста
    const darkTextColor = darkenColor(randomColor, 0.3); // Темнее на 30%

    // Устанавливаем темный цвет для текста
    const textElements = item.querySelectorAll('p, b');
    textElements.forEach(function(textElement) {
      textElement.style.color = darkTextColor;
    });
  });
});