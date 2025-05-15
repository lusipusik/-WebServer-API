// Плавная анимация колеса
function spinWheel(degrees, duration) {
    const wheel = document.getElementById("wheel");
    wheel.style.transition = `transform ${duration}ms cubic-bezier(0.17, 0.67, 0.21, 0.99)`;
    wheel.style.transform = `rotate(${degrees}deg)`;
}

// Загрузка истории при старте
function loadHistory() {
    fetch("/history")
        .then(response => response.json())
        .then(data => {
            const historyList = document.getElementById("historyList");
            historyList.innerHTML = data.map(item =>
                `<li>${item.text} (${new Date(item.time).toLocaleString()})</li>`
            ).join("");
        });
}

document.addEventListener("DOMContentLoaded", loadHistory);

// Крутим колесо
document.getElementById("spinBtn").addEventListener("click", () => {
    const spinBtn = document.getElementById("spinBtn");
    spinBtn.disabled = true;

    // Анимация: 5 полных оборотов + случайный угол
    const degrees = 1800 + Math.random() * 360;
    spinWheel(degrees, 5000);

    // Запрос результата после анимации
    setTimeout(() => {
        fetch("/spin", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                document.getElementById("result").textContent = `Вы выиграли: ${data.result}!`;
                loadHistory(); // Обновляем историю
                spinBtn.disabled = false;
            });
    }, 5000);
});