document.addEventListener('DOMContentLoaded', () => {
    const wheel = document.getElementById('wheel');
    const spinBtn = document.getElementById('spinBtn');
    const resultDiv = document.getElementById('result');
    const itemsList = document.getElementById('itemsList');
    const newItemText = document.getElementById('newItemText');
    const newItemChance = document.getElementById('newItemChance');
    const addBtn = document.getElementById('addBtn');

    let isSpinning = false;
    let items = [];

    function updateWheel() {
        wheel.innerHTML = '';

        if (items.length === 0) {
            wheel.style.background = '#ddd';
            return;
        }

        const totalChance = items.reduce((sum, item) => sum + item.chance, 0);
        let currentPercent = 0;
        const colors = ['#FF5733', '#33FF57', '#3357FF', '#F3FF33', '#FF33F3'];
        const radius = 90; // Оптимальный радиус для отображения

        const gradientParts = items.map((item, i) => {
            const percent = (item.chance / totalChance) * 100;
            const part = `${colors[i % colors.length]} ${currentPercent}% ${currentPercent + percent}%`;

            // Добавляем текст
            const label = document.createElement('div');
            label.className = 'wheel-label';
            label.textContent = item.text;
            const angle = (currentPercent + percent / 2) * 3.6; // Центральный угол сектора

            // Правильный поворот текста (последний символ к центру)
            label.style.transform = `
                rotate(${angle}deg)
                translateY(-${radius}px)
                rotate(${angle < 180 ? 90 : -90}deg)
            `;

            // Оптимальные настройки отображения
            label.style.width = `${Math.min(percent * 2.5, 120)}px`;
            label.style.left = `50%`;
            label.style.marginLeft = `-${Math.min(percent * 1.25, 60)}px`;
            label.style.fontSize = `${Math.max(10, Math.min(14, percent))}px`;

            wheel.appendChild(label);

            currentPercent += percent;
            return part;
        });

        wheel.style.background = `conic-gradient(${gradientParts.join(', ')})`;
    }

    function loadItems() {
        fetch('/get_items')
            .then(response => response.json())
            .then(data => {
                items = data;
                renderItems();
                updateWheel();
            });
    }

    function renderItems() {
        itemsList.innerHTML = items.map(item => `
            <li>
                ${item.text} (${item.chance}%)
                <button class="removeBtn" data-text="${item.text}">×</button>
            </li>
        `).join('');

        document.querySelectorAll('.removeBtn').forEach(btn => {
            btn.addEventListener('click', () => {
                fetch('/remove_item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: btn.dataset.text })
                }).then(loadItems);
            });
        });
    }

    addBtn.addEventListener('click', () => {
        const text = newItemText.value.trim();
        const chance = parseInt(newItemChance.value);

        if (!text || isNaN(chance)) {
            alert('Заполните все поля!');
            return;
        }

        fetch('/add_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, chance })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'OK') {
                newItemText.value = '';
                newItemChance.value = '';
                loadItems();
            } else {
                alert(data.message || 'Ошибка');
            }
        });
    });

    spinBtn.addEventListener('click', () => {
        if (isSpinning || items.length === 0) return;

        isSpinning = true;
        resultDiv.textContent = '';

        wheel.style.transition = 'none';
        wheel.style.transform = 'rotate(0deg)';

        setTimeout(() => {
            const totalChance = items.reduce((sum, item) => sum + item.chance, 0);
            const random = Math.random() * totalChance;
            let current = 0;
            let selectedIndex = 0;

            items.forEach((item, i) => {
                if (current <= random) {
                    selectedIndex = i;
                    current += item.chance;
                }
            });

            // Новый расчет угла с учетом положения стрелки (90 градусов сверху)
            const sectorAngle = 360 / totalChance * items[selectedIndex].chance;
            const degrees = 1800 + (360 / totalChance * current) - (sectorAngle / 2) - 90;

            wheel.style.transition = 'transform 4s cubic-bezier(0.36, 0.07, 0.19, 0.97)';
            wheel.style.transform = `rotate(${-degrees}deg)`; // Отрицательное значение для правильного направления

            setTimeout(() => {
                fetch('/spin', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        resultDiv.textContent = `Вы выиграли: ${data.result}!`;
                        isSpinning = false;
                        loadItems();
                    });
            }, 4000);
        }, 10);
    });

    loadItems();
});