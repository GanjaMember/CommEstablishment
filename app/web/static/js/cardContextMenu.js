document.addEventListener('DOMContentLoaded', function () {
    // Открытие/закрытие меню
    document.querySelectorAll('.project-card-actions').forEach(function (actionBlock) {
        const trigger = actionBlock.querySelector('.context-menu-trigger');
        const menu = actionBlock.querySelector('.context-menu');

        trigger.addEventListener('click', function (event) {
            event.stopPropagation();
            // Скрываем все другие меню
            document.querySelectorAll('.context-menu').forEach(m => { if(m !== menu) m.style.display = 'none'; });
            // Переключаем видимость текущего меню
            menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
        });

        // Клик вне меню закрывает меню
        document.addEventListener('click', function () {
            menu.style.display = 'none';
        });

        // Чтобы клик по самому меню не закрывал его сразу
        menu.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    });
});