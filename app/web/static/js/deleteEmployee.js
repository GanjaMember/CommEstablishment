// Добавление слушателя события DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    const deleteEmployeeLink = document.getElementById('delete-link');
    const deleteModalOverlay = document.getElementById('deleteEmployeeModal');
    const deleteCloseButton = deleteModalOverlay.querySelector('.close-button');
    const deleteCancelButton = deleteModalOverlay.querySelector('.cancel-button');
    const deleteEmployeeForm = document.getElementById('deleteEmployeeForm');

// Функция для открытия модального окна
function openModal() {
    deleteModalOverlay.style.display = 'flex'; // Используем flex для центрирования
}

// Функция для закрытия модального окна
function closeModal() {
    deleteModalOverlay.style.display = 'none';
}

// Открытие модального окна при клике на ссылку
if (deleteEmployeeLink) {
    deleteEmployeeLink.addEventListener('click', function (event) {
        event.preventDefault(); // Предотвращаем переход по ссылке
        openModal();
    });
}

    // Закрытие модального окна при клике на крестик
    if (deleteCloseButton) {
        deleteCloseButton.addEventListener('click', closeModal);
    }

    // Закрытие модального окна при клике на кнопку "Отмена"
    if (deleteCancelButton) {
        deleteCancelButton.addEventListener('click', closeModal);
    }

    // Закрытие модального окна при клике вне формы (на оверлее)
    if (deleteModalOverlay) {
        deleteModalOverlay.addEventListener('click', function (event) {
            // Проверяем, был ли клик именно по оверлею, а не по содержимому модального окна
            if (event.target === deleteModalOverlay) {
                closeModal();
            }
        });
    }


    if (deleteEmployeeForm) {
        deleteEmployeeForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Предотвращаем стандартную отправку формы

            // Здесь будет код для сбора данных формы и отправки POST запроса
            console.log('Форма отправлена (имитация)');
            const formData = new FormData(deleteEmployeeForm);
            const employeeData = {};
            formData.forEach((value, key) => {
                employeeData[key] = value;
            });
            console.log('Данные сотрудника:', employeeData);
        });
    }
});