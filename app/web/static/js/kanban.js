document.addEventListener('DOMContentLoaded', function () {
const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

let draggedCard = null;

// Навесим обработчики на все карточки и колонки
function initDragAndDrop() {
    document.querySelectorAll('.kanban-card').forEach(card => {
        card.addEventListener('dragstart', (e) => {
            draggedCard = card;
            setTimeout(() => card.classList.add('dragging'), 0);
        });
        card.addEventListener('dragend', (e) => {
            card.classList.remove('dragging');
            draggedCard = null;
        });
    });

    document.querySelectorAll('.kanban-column').forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        column.addEventListener('drop', (e) => {
            if (draggedCard) {
                const taskId = draggedCard.dataset.taskId;
                const newStatus = column.dataset.status;
                // Локально перемещаем карточку
                column.appendChild(draggedCard);
                // Отправляем через сокет
                socket.emit('move_task', {
                    task_id: taskId,
                    new_status: newStatus
                });
            }
        });
    });
}


socket.on('task_created', function(task) {
    // Определи колонку по статусу
    const column = document.querySelector(`.kanban-column[data-status="${task.status}"]`);
    if (!column) return;

    // Собери HTML для новой карточки (по аналогии с твоим шаблоном)
    const card = document.createElement('div');
    card.className = 'kanban-card project-card';
    card.setAttribute('draggable', 'true');
    card.dataset.taskId = task.id;
    card.innerHTML = `
        <div class="project-card-header">
            <div class="project-card-heading">${task.name}</div>
            <div class="project-card-actions">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-grey hover:text-grey-l20 active:text-grey-d20" type="ui"><path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"></path><path d="M12 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"></path><path d="M12 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"></path></svg>
            </div>
        </div>
        <div class="project-card-index">${task.index || ''}</div>
        <div class="employees-list">
            ${task.employees.map(emp =>
                `<div class="employee-bubble">${emp.index || emp.full_name}</div>`
            ).join('')}
            <div class="employee-bubble">...</div>
        </div>
    `;
    // Вставляем карточку
    column.appendChild(card);

    // Не забудь навесить обработчики drag&drop!
    card.addEventListener('dragstart', (e) => {
        draggedCard = card;
        setTimeout(() => card.classList.add('dragging'), 0);
    });
    card.addEventListener('dragend', (e) => {
        card.classList.remove('dragging');
        draggedCard = null;
    });
});

// При получении сигнала от сервера двигаем карточку
socket.on('task_moved', data => {
    const { task_id, new_status } = data;
    const card = document.querySelector(`.kanban-card[data-task-id="${task_id}"]`);
    const column = document.querySelector(`.kanban-column[data-status="${new_status}"]`);
    if (card && column) {
        column.appendChild(card);
    }
});

// Инициализация
initDragAndDrop();
});