from typing import Optional, List, Dict
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from ..ai import TextGenerator
from ..models import (
    db,
    Company,
    Department,
    Employee,
    Project,
    Chat,
    Task,
    Role,
    KnowledgeBase,
    KBRecord,
    HREvent,
    Message,
    Status,
    User
)
from .forms import (
    CompanyForm,
    DepartmentForm,
    ProjectForm,
    ChatForm,
    DepartmentIdForm,
    ProjectIdForm,
    TaskForm,
    RegistrationForm,
    LoginForm
)
import config


socketio = SocketIO()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)
socketio.init_app(app, async_mode='threading')

with app.app_context():
    db.create_all()
    selected_company = Company.query.first()

login_manager = LoginManager(app)
login_manager.login_view = 'login'


text_generator = TextGenerator(
    model=config.model,
    key=config.key
)

histories: Dict[int, List[Dict[str, str]]] = {}
messages: Dict[int, List[Dict[str, str]]] = {}

def get_all_employees() -> List[str]:
    # This function fetches all employees and can be reused in routes
    return [str(i) for i in Employee.query.filter(Employee.company_id == selected_company.id).all()]

def get_all_projects() -> List[str]:
    # This function fetches all projects and can be reused in routes
    return [str(i) for i in Project.query.filter(Project.company_id == selected_company.id).all()]

def get_all_departments() -> List[str]:
    # This function fetches all departments and can be reused in routes
    return [str(i) for i in Department.query.filter(Department.company_id == selected_company.id).all()]

def get_all_tasks() -> List[str]:
    # This function fetches all tasks and can be reused in routes
    return [str(i) for i in Task.query.all()]


def get_chats():
    # This function fetches all chats and can be reused in routes
    return Chat.query.all()


def serialize_task(task):
    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "start_date": task.start_date.isoformat() if task.start_date else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
        # Можно добавить project/employee info, если нужно
    }


@socketio.on('user_message')
def handle_user_message(data):
    text = data.get('text', '')
    histories[current_user.id] = histories.get(current_user.id, [
        {"role": "system", "content": config.assistant_system_prompt},
        {"role": "system", "content": "Сотрудники" + str(get_all_employees())},
        {"role": "system", "content": "Проекты" + str(get_all_projects())},
        {"role": "system", "content": "Отделы" + str(get_all_departments())},
        {"role": "system", "content": "Задачи" + str(get_all_tasks())}
    ])
    messages[current_user.id] = messages.get(current_user.id, [])
    messages[current_user.id].append({"role": "user", "content": text})
    histories[current_user.id].append({"role": "user", "content": text})
    answer = text_generator.generate(histories[current_user.id])
    histories[current_user.id].append({"role": "assistant", "content": answer})
    messages[current_user.id].append({"role": "assistant", "content": answer})
    emit('assistant_message', {'text': answer})


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_now():
    return {'now': datetime.now}


@app.route('/assistant')
def assistant():
    return render_template(
        'assistant.html',
        chats=get_chats(),
        messages=messages.get(current_user.id, [])
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        surname = form.surname.data
        name = form.name.data
        patronymic = form.patronymic.data
        hire_date = form.hire_date.data
        birth_date = form.birth_date.data
        contacts = form.contact.data
        email = form.email.data
        employee = Employee(
            surname=surname,
            name=name,
            patronymic=patronymic,
            hire_date=hire_date,
            birth_date=birth_date,
            contacts=contacts,
            email=email,
            company_id=selected_company.id
        )
        employee.user = user
        db.session.add(employee)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect('/login')
    return render_template('registration_form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!')
            return redirect('/')
        else:
            flash('Invalid username or password.')
    return render_template('login_form.html', form=form)


@app.route('/me')
@login_required
def me():
    return render_template(
        'me.html',
        employee=current_user.employee,
        chats=get_chats()
    )

@app.route("/")
def index():
    return render_template(
        'index.html', chats=get_chats()
    )


@app.route("/departments")
def departments():
    departments = Company.query.filter(
        Company.id == selected_company.id
    ).first().departments  # type: ignore
    return render_template('departments.html', departments=departments, active_page='departments', chats=get_chats())


@app.route("/department/create", methods=["GET", "POST"])
def create_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        department = Department(
            name=name, description=description, company_id=selected_company.id  # type: ignore
        )
        db.session.add(department)
        db.session.commit()
        return redirect('/departments')
    return render_template(
        'department_form.html', form=form, active_page='departments', chats=get_chats()
    )


@app.route("/chat/create", methods=["GET", "POST"])
def create_chat():
    form = ChatForm()
    employees = Employee.query.filter(Employee.company_id == selected_company.id).all()
    form.employees.choices = [
        (employee.id, employee.full_name) for employee in employees
    ]
    if form.validate_on_submit():
        name = form.name.data
        chat = Chat(name=name)
        
        # Add selected employees to the chat
        selected_employee_ids = form.employees.data
        selected_employees = Employee.query.filter(
            Employee.id.in_(selected_employee_ids)
        ).all()
        chat.employees.extend(selected_employees)

        db.session.add(chat)
        db.session.commit()
        # Redirect to the newly created chat page
        return redirect(f'/chat/{chat.id}')  # type: ignore
    return render_template(
        'chat_form.html', form=form, chats=get_chats()
    )


@app.route('/chat/<int:chat_id>')
def chat(chat_id: int):
    chat = Chat.query.get_or_404(chat_id)
    messages = chat.messages.order_by(Message.timestamp).all()  # type: ignore
    # Pass the specific chat and all chats for the sidebar to the template
    return render_template(
        'chat.html', chat=chat, active_page=f'chat_{chat_id}', chats=get_chats(), messages=messages
    )


@app.route('/chat/<int:chat_id>/send_message', methods=['POST'])
def send_message(chat_id: int):
    chat = Chat.query.get_or_404(chat_id)
    content = request.form.get('message_content')
    # You will need to get the actual sender employee ID here.
    # For now, I'll use a placeholder (e.g., first employee found).
    # In a real application, this would come from the logged-in user's session.
    sender = Employee.query.first()  # Placeholder for sender

    if content and sender:
        message = Message(content=content, chat=chat, sender=sender)
        db.session.add(message)
        db.session.commit()
        print(f"Message sent successfully: {message.content}")  # Debug print
    else:
        print("Failed to send message: content or sender missing.")  # Debug print

    # Redirect back to the chat page
    return redirect(f'/chat/{chat_id}')


@app.route('/chat/<int:chat_id>/history', methods=['DELETE'])
def delete_chat_history(chat_id: int):
    chat = Chat.query.get_or_404(chat_id)
    # Delete all messages associated with the chat
    Message.query.filter_by(chat_id=chat.id).delete()  # type: ignore
    db.session.commit()
    return '', 204  # Return an empty response with status code 204 (No Content)


@app.route('/chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id: int):
    chat = Chat.query.get_or_404(chat_id)
    # Delete all messages associated with the chat
    Message.query.filter_by(chat_id=chat.id).delete()
    # Delete the chat itself
    db.session.delete(chat)
    db.session.commit()
    return '', 200 # Return success status code


@app.route("/company/create", methods=["GET", "POST"])
def create_company():
    form = CompanyForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        company = Company(name=name, description=description)
        db.session.add(company)
        db.session.commit()
        # Redirect to the new company page or companies list
        return redirect(f'/company/{company.id}')
    return render_template('company_form.html', form=form, chats=get_chats())


@app.route('/company/', defaults={'company_id': None})
@app.route("/company/<int:company_id>")
def company(company_id: Optional[int]):
    global selected_company
    if company_id:
        selected_company = Company.query.filter(Company.id == company_id).first()
    # Ensure selected_company is set if no ID is provided (e.g., first run)
    if not selected_company:
        # Or handle as an error/setup case
        selected_company = Company.query.first()
    if selected_company:
        selected_company = Company.query.filter(
            Company.id == selected_company.id
        ).first()
    # Pass chats to the template for the sidebar
    return render_template(
        'company.html',
        company=selected_company,
        active_page='company',
        chats=get_chats()
    )


@app.route('/tasks')
def tasks():
    company = Company.query.filter_by(id=selected_company.id).first()
    if not company:
        return "Company not found", 404

    form = ProjectIdForm(request.args)
    form.project_id.choices.extend(
        [(project.id, project.name) for project in company.projects]
    )

    tasks = []
    project_id = request.args.get('project_id', type=int)
    if project_id:
        project = Project.query.get_or_404(project_id)
        tasks = project.tasks
        form.project_id.data = project_id
    else:
        tasks = Task.query.join(Project).filter(
            Project.company_id == selected_company.id
        ).all()
    return render_template(
        'tasks.html',
        active_page='tasks',
        chats=get_chats(),
        tasks=tasks,
        form=form
    )


@app.route('/task/create', methods=['GET', 'POST'])
def create_task():
    form = TaskForm()
    projects = Project.query.filter(
        Project.company_id == selected_company.id
    ).all()
    form.project_id.choices = [(project.id, project.name) for project in projects]
    employees = Employee.query.filter(
        Employee.company_id == selected_company.id
    ).all()
    form.employees.choices = [(employee.id, employee.full_name) for employee in employees]
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        start_date = form.start_date.data
        due_date = form.due_date.data
        priority = form.priority.data
        project_id = form.project_id.data
        employees_ids = form.employees.data
        task = Task(
            name=name,
            description=description,
            start_date=start_date,
            due_date=due_date,
            priority=priority,
            status=Status.TODO,
        )
        project = Project.query.get(project_id)
        project.tasks.append(task)
        for employee_id in employees_ids:
            employee = Employee.query.get(employee_id)
            task.employees.append(employee)
        
        db.session.add(task)
        db.session.commit()

        task_data = {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "index": task.index,
            "employees": [
                {
                    "index": employee.index, 
                    "id": employee.id, 
                    "full_name": employee.full_name
                }
                for employee in task.employees
            ],
        }

        socketio.emit('task_created', task_data)

        return redirect('/tasks')
    return render_template(
        'task_form.html',
        form=form,
        chats=get_chats()
    )


@app.route('/calendar/', methods=['GET'])
def calendar():
    company = Company.query.filter_by(id=selected_company.id).first()
    if not company:
        return "Company not found", 404

    form = ProjectIdForm(request.args)
    form.project_id.choices.extend(
        [(project.id, project.name) for project in company.projects]
    )

    tasks = []
    project_id = request.args.get('project_id', type=int)
    if project_id:
        project = Project.query.get_or_404(project_id)
        tasks = project.tasks
        form.project_id.data = project_id
    else:
        tasks = Task.query.join(Project).filter(
            Project.company_id == selected_company.id
        ).all()

    return render_template(
        'calendar.html',
        active_page='calendar',
        chats=get_chats(),
        tasks=[serialize_task(task) for task in tasks],
        form=form
    )


@app.route("/companies")
def companies():
    companies = Company.query.all()
    # Pass chats to the template for the sidebar
    return render_template('companies.html', companies=companies, active_page='companies', chats=get_chats())


@app.route("/projects")
def projects():
    # Ensure selected_company is set
    if not selected_company:
        # Placeholder - add appropriate handling
        pass
    projects = Project.query.filter(
        Project.company_id == selected_company.id
    ).all()
    # Pass chats to the template for the sidebar
    return render_template('projects.html', projects=projects, active_page='projects', chats=get_chats())


@app.route("/project/create", methods=["GET", "POST"])
def create_project():
    form = ProjectForm()
    departments = Company.query.filter(Company.id == selected_company.id).first().departments
    form.responsible_department_id.choices = [(d.id, d.name) for d in departments]
    employees = Employee.query.filter(Employee.company_id == selected_company.id).all()
    form.employees.choices = [(employee.id, employee.full_name) for employee in employees]
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        responsible_department_id = form.responsible_department_id.data
        employees_ids = form.employees.data
        project = Project(
            name=name,
            description=description,
            responsible_dept_id=responsible_department_id,
            company_id=selected_company.id
        )
        db.session.add(project)
        for employee_id in employees_ids:
            employee = Employee.query.get(employee_id)
            project.employees.append(employee)
        db.session.commit()
        return redirect('/projects')
    return render_template('project_form.html', chats=get_chats(), form=form)


@app.route("/employees")
def employees():
    # Ensure selected_company is set
    if not selected_company:
        # Placeholder - add appropriate handling
        pass
    employees = Employee.query.filter(
        Employee.company_id == selected_company.id
    ).all()
    # Pass chats to the template for the sidebar
    return render_template('employees.html', employees=employees, active_page='employees', chats=get_chats())


@socketio.on('move_task')
def handle_move_task(data):
    task_id = int(data['task_id'])
    new_status = data['new_status']
    task = Task.query.get(task_id)
    task.status = Status(new_status)
    db.session.commit()
    if task:
        task.status = new_status
        db.session.commit()
        # Уведомляем всех, кроме отправителя
        emit('task_moved', {'task_id': task_id, 'new_status': new_status}, broadcast=True, include_self=False)


@app.route('/company/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    form = CompanyForm(obj=company)
    if form.validate_on_submit():
        company.name = form.name.data
        company.description = form.description.data
        db.session.commit()
        flash('Компания успешно обновлена.')
        return redirect(f'/company/{company.id}')
    return render_template('company_form.html', form=form, chats=get_chats())

@app.route('/company/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash('Компания удалена.')
    return redirect('/companies')


@app.route('/department/edit/<int:department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    department = Department.query.get_or_404(department_id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('Отдел успешно обновлен.')
        return redirect('/departments')
    return render_template('department_form.html', form=form, chats=get_chats())

@app.route('/department/delete/<int:department_id>', methods=['POST'])
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    flash('Отдел удален.')
    return redirect('/departments')


@app.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    # Не забудьте подгрузить choices!
    departments = get_all_departments()
    form.responsible_department_id.choices = [(d.id, d.name) for d in departments]
    employees = get_all_employees()
    form.employees.choices = [(e.id, e.full_name) for e in employees]
    if request.method == 'GET':
        form.employees.data = [e.id for e in project.employees]
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.responsible_dept_id = form.responsible_department_id.data
        project.employees = [Employee.query.get(eid) for eid in form.employees.data]
        db.session.commit()
        flash('Проект успешно обновлен.')
        return redirect('/projects')
    return render_template('project_form.html', form=form, chats=get_chats())

@app.route('/project/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Проект удалён.')
    return redirect('/projects')


@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    projects = get_all_projects()
    form.project_id.choices = [(p.id, p.name) for p in projects]
    employees = get_all_employees()
    form.employees.choices = [(e.id, e.full_name) for e in employees]
    if request.method == 'GET':
        form.employees.data = [e.id for e in task.employees]
        form.project_id.data = task.project_id
    if form.validate_on_submit():
        task.name = form.name.data
        task.description = form.description.data
        task.start_date = form.start_date.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.project_id = form.project_id.data
        task.employees = [Employee.query.get(eid) for eid in form.employees.data]
        db.session.commit()
        flash('Задача обновлена.')
        return redirect('/tasks')
    return render_template('task_form.html', form=form, chats=get_chats())

@app.route('/task/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена.')
    return redirect('/tasks')
