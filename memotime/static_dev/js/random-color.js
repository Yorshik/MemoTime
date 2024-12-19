// Массив из 10 фиксированных цветов
const colors = [
  "rgba(255, 99, 132, 0.75)",  // Цвет для цифры 0
  "rgba(54, 162, 235, 0.75)",  // Цвет для цифры 1
  "rgba(255, 206, 86, 0.75)",  // Цвет для цифры 2
  "rgba(75, 192, 192, 0.75)",  // Цвет для цифры 3
  "rgba(153, 102, 255, 0.75)", // Цвет для цифры 4
  "rgba(255, 159, 64, 0.75)",  // Цвет для цифры 5
  "rgba(199, 199, 199, 0.75)", // Цвет для цифры 6
  "rgba(83, 102, 255, 0.75)",  // Цвет для цифры 7
  "rgba(255, 75, 105, 0.75)",  // Цвет для цифры 8
  "rgba(120, 159, 180, 0.75)"  // Цвет для цифры 9
];

// Функция для получения цвета на основе последней цифры id
function generateColorFromId(id) {
  // Получаем последнюю цифру из id
  const lastDigit = parseInt(id.slice(-1), 10);

  // Возвращаем цвет из массива цветов
  return colors[lastDigit];
}

// Функция для затемнения цвета (уменьшение яркости)
function darkenColor(color, factor = 0.7) {
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
    // Генерация цвета на основе id элемента
    const itemId = item.id;  // Получаем id элемента (например, 'timeschedule-123')
    const generatedColor = generateColorFromId(itemId); // Генерация цвета на основе id

    // Устанавливаем сгенерированный цвет фона
    item.style.backgroundColor = generatedColor;

    // Получаем темный цвет для текста
    const darkTextColor = darkenColor(generatedColor, 0.3); // Темнее на 30%

    // Устанавливаем темный цвет для текста
    const textElements = item.querySelectorAll('p, b');
    textElements.forEach(function(textElement) {
      textElement.style.color = darkTextColor;
    });
  });
});
