from typing import Optional

from flask import Flask, render_template, request, redirect
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
    Message
)
from .forms import (
    CompanyForm,
    DepartmentForm,
    ProjectForm,
    EmployeeForm,
    ChatForm
)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

with app.app_context():
    db.create_all()
    selected_company = Company.query.first()

def get_chats():
    # This function fetches all chats and can be reused in routes
    return Chat.query.all()


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


@app.route("/create_department", methods=["GET", "POST"])
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
        'create_department.html', form=form, active_page='create_department', chats=get_chats()
    )


@app.route("/create_chat", methods=["GET", "POST"])
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
        'create_chat.html', form=form, active_page='create_chat', chats=get_chats()
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


@app.route("/create_company", methods=["GET", "POST"])
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
    return render_template('create_company.html', form=form, active_page='create_company', chats=get_chats())


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


@app.route("/calendar")
def calendar():
    # Pass chats to the template for the sidebar
    return render_template('calendar.html', active_page='calendar', chats=get_chats())


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


@app.route("/create_project", methods=["GET", "POST"])
def create_project():
    form = ProjectForm()
    # Ensure selected_company is set before querying
    if not selected_company:
        # Placeholder - add appropriate handling
        pass
    else:
        departments = Company.query.filter(
            Company.id == selected_company.id
        ).first().departments
        form.responsible_department_id.choices = [(d.id, d.name) for d in departments]
        employees = Employee.query.filter(
            Employee.company_id == selected_company.id
        ).all()
        form.employees.choices = [
            (employee.id, employee.name) for employee in employees
        ]
        if form.validate_on_submit():
            name = form.name.data
            description = form.description.data
            responsible_department_id = form.responsible_department_id.data
            employees_ids = form.employees.data  # Unused variable - can be removed
            project = Project(
                name=name,
                description=description,
                responsible_department_id=responsible_department_id,
                company_id=selected_company.id
            )
            db.session.add(project)
            db.session.commit()
            return redirect('/projects')
    # Pass chats to the template for the sidebar
    return render_template(
        'create_project.html', form=form, active_page='create_project', chats=get_chats()
    )


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


@app.route("/create_employee", methods=["GET", "POST"])
def create_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
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
        db.session.add(employee)
        db.session.commit()
        return redirect('/employees')
    # Pass chats to the template for the sidebar
    return render_template(
        'create_employee.html', form=form, active_page='create_employee', chats=get_chats()
    )