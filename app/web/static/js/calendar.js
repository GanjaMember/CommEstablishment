// ========== Utils ==========
function formatDateISO(date) {
    return date.toISOString().slice(0, 10); // 'YYYY-MM-DD'
}
function getDaysInMonth(month, year) {
    // month: 0..11
    return new Date(year, month + 1, 0).getDate();
}
function getFirstWeekdayOfMonth(month, year) {
    // Пн=0 ... Вс=6
    let day = new Date(year, month, 1).getDay();
    return day === 0 ? 6 : day - 1;
}
function isSameDay(d1, d2) {
    return d1.getFullYear() === d2.getFullYear() &&
           d1.getMonth() === d2.getMonth() &&
           d1.getDate() === d2.getDate();
}

// ========== Task mapping ==========
function buildEventsByDate(tasks) {
    // Группируем таски по датам (start_date..due_date)
    let events = {};
    tasks.forEach(task => {
        // Игнорируем если нет дат
        if (!task.start_date || !task.due_date) return;
        let cur = new Date(task.start_date);
        const end = new Date(task.due_date);
        while (cur <= end) {
            const key = formatDateISO(cur);
            if (!events[key]) events[key] = [];
            events[key].push(task);
            cur.setDate(cur.getDate() + 1);
        }
    });
    return events;
}

const eventsByDate = buildEventsByDate(tasks);

// ========== DOM elements ==========
const monthSelect = document.querySelector('.month-select');
const yearSelect = document.querySelector('.year-select');
const prevMonthBtn = document.querySelector('.prev-month');
const nextMonthBtn = document.querySelector('.next-month');
const calendarBody = document.querySelector('.ant-picker-content tbody');
const eventsPanel = document.querySelector('.events-panel');

// ========== Calendar state ==========
let today = new Date();
let selectedDate = {
    day: today.getDate(),
    month: today.getMonth(),
    year: today.getFullYear()
};

// ========== Init ==========
function initCalendar() {
    monthSelect.value = selectedDate.month;
    yearSelect.value = selectedDate.year;
    renderCalendar(selectedDate.month, selectedDate.year);

    monthSelect.addEventListener('change', handleMonthYearChange);
    yearSelect.addEventListener('change', handleMonthYearChange);
    prevMonthBtn.addEventListener('click', goToPrevMonth);
    nextMonthBtn.addEventListener('click', goToNextMonth);
    calendarBody.addEventListener('click', handleDayClick);
}

function handleMonthYearChange() {
    const month = parseInt(monthSelect.value);
    const year = parseInt(yearSelect.value);
    renderCalendar(month, year);
}
function goToPrevMonth() {
    let m = parseInt(monthSelect.value), y = parseInt(yearSelect.value);
    m--; if (m < 0) { m = 11; y--; }
    monthSelect.value = m; yearSelect.value = y;
    renderCalendar(m, y);
}
function goToNextMonth() {
    let m = parseInt(monthSelect.value), y = parseInt(yearSelect.value);
    m++; if (m > 11) { m = 0; y++; }
    monthSelect.value = m; yearSelect.value = y;
    renderCalendar(m, y);
}

function handleDayClick(e) {
    const cell = e.target.closest('.ant-picker-cell');
    if (!cell || cell.classList.contains('previous-month') || cell.classList.contains('next-month')) return;

    document.querySelectorAll('.ant-picker-cell.selected').forEach(el => el.classList.remove('selected'));
    cell.classList.add('selected');
    const day = parseInt(cell.querySelector('.ant-picker-cell-inner').textContent);
    const month = parseInt(monthSelect.value);
    const year = parseInt(yearSelect.value);
    selectedDate = { day, month, year };
    updateEventsPanel();
}

function renderCalendar(month, year) {
    const daysInMonth = getDaysInMonth(month, year);
    const firstWeekday = getFirstWeekdayOfMonth(month, year); // 0 = Пн

    // previous month days
    let prevDays = [];
    if (firstWeekday > 0) {
        const prevMonth = (month === 0) ? 11 : month - 1;
        const prevYear = (month === 0) ? year - 1 : year;
        const prevMonthDays = getDaysInMonth(prevMonth, prevYear);
        for (let i = prevMonthDays - firstWeekday + 1; i <= prevMonthDays; i++) {
            prevDays.push({ day: i, month: 'previous' });
        }
    }

    // current month days
    let currDays = [];
    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${(month+1).toString().padStart(2,'0')}-${d.toString().padStart(2,'0')}`;
        const hasEvents = !!eventsByDate[dateStr];
        const isWeekend = (firstWeekday + d - 1) % 7 >= 5;
        currDays.push({ day: d, month: 'current', hasEvents, isWeekend });
    }

    // next month days to fill 6 weeks
    let daysNeeded = 42 - (prevDays.length + currDays.length);
    let nextDays = [];
    for (let i = 1; i <= daysNeeded; i++) {
        nextDays.push({ day: i, month: 'next' });
    }

    // Split into weeks
    const allDays = [...prevDays, ...currDays, ...nextDays];
    let html = '';
    for (let w = 0; w < 6; w++) {
        html += '<tr>';
        for (let d = 0; d < 7; d++) {
            const day = allDays[w*7+d];
            const classes = [
                'ant-picker-cell',
                day.month === 'previous' ? 'previous-month' : '',
                day.month === 'next' ? 'next-month' : '',
                day.isWeekend ? 'weekend' : '',
                (day.month === 'current' &&
                 day.day === selectedDate.day &&
                 month === selectedDate.month &&
                 year === selectedDate.year) ? 'selected today' : '',
                day.hasEvents ? 'has-events' : ''
            ].filter(Boolean).join(' ');
            html += `<td class="${classes}">`;
            html += `<div class="ant-picker-cell-inner">${day.day}</div>`;

            // Dots for events
            if (day.month === 'current') {
                const dateStr = `${year}-${(month+1).toString().padStart(2,'0')}-${day.day.toString().padStart(2,'0')}`;
                if (eventsByDate[dateStr]) {
                    html += '<div class="cell-events">';
                    eventsByDate[dateStr].forEach(task => {
                        let type = 'info';
                        if (task.priority === 3) type = 'danger';
                        else if (task.priority === 2) type = 'warning';
                        else if (task.priority === 1) type = 'success';
                        html += `<div class="event-dot ${type}" title="${task.name}"></div>`;
                    });
                    html += '</div>';
                }
            }
            html += '</td>';
        }
        html += '</tr>';
    }
    calendarBody.innerHTML = html;
    updateEventsPanel();
}

function updateEventsPanel() {
    const day = selectedDate.day, month = selectedDate.month, year = selectedDate.year;
    const dateStr = `${year}-${(month+1).toString().padStart(2,'0')}-${day.toString().padStart(2,'0')}`;
    const tasks = eventsByDate[dateStr] || [];
    const monthNames = [
        'Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
        'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря'
    ];
    let html = `<h3>События на ${day} ${monthNames[month]}</h3>`;
    if (tasks.length > 0) {
        html += '<ul class="events">';
        tasks.forEach(task => {
            let type = 'info';
            if (task.priority === 3) type = 'danger';
            else if (task.priority === 2) type = 'warning';
            else if (task.priority === 1) type = 'success';
            html += `<li>
                <span class="ant-badge-status ant-badge-status-${type}">${task.name}</span>
                <span class="event-info">${task.description || ''}</span>
            </li>`;
        });
        html += '</ul>';
    } else {
        html += '<p>Нет событий на этот день</p>';
    }
    html += '<div class="add-event"><button class="add-event-btn">Добавить событие</button></div>';
    eventsPanel.innerHTML = html;
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', initCalendar);
