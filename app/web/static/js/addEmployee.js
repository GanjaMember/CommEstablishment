document.addEventListener('DOMContentLoaded', function() {
// Получаем элементы
const addEmployeeLink = document.getElementById('add-link');
const addModalOverlay = document.getElementById('addEmployeeModal');
const addCloseButton = addModalOverlay.querySelector('.close-button');
const addCancelButton = addModalOverlay.querySelector('.cancel-button');
const addEmployeeForm = document.getElementById('addEmployeeForm');

// Добавление слушателя события DOMContentLoaded
    // Функция для открытия модального окна
    function openModal() {
        addModalOverlay.style.display = 'flex'; // Используем flex для центрирования
    }

// Функция для закрытия модального окна
function closeModal() {
    addModalOverlay.style.display = 'none';
}

// Открытие модального окна при клике на ссылку
if (addEmployeeLink) {
    addEmployeeLink.addEventListener('click', function (event) {
        event.preventDefault(); // Предотвращаем переход по ссылке
        openModal();
    });
}

    // Закрытие модального окна при клике на крестик
    if (addCloseButton) {
        addCloseButton.addEventListener('click', closeModal);
    }

    // Закрытие модального окна при клике на кнопку "Отмена"
    if (addCancelButton) {
        addCancelButton.addEventListener('click', closeModal);
    }

    // Закрытие модального окна при клике вне формы (на оверлее)
    if (addModalOverlay) {
        addModalOverlay.addEventListener('click', function (event) {
            // Проверяем, был ли клик именно по оверлею, а не по содержимому модального окна
            if (event.target === addModalOverlay) {
                closeModal();
            }
        });
    }


    if (addEmployeeForm) {
        addEmployeeForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Предотвращаем стандартную отправку формы

            // Здесь будет код для сбора данных формы и отправки POST запроса
            console.log('Форма отправлена (имитация)');
            const formData = new FormData(addEmployeeForm);
            const employeeData = {};
            formData.forEach((value, key) => {
                employeeData[key] = value;
            });
            console.log('Данные сотрудника:', employeeData);
        });
    }
});