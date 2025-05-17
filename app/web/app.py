from typing import Optional

from flask import Flask, render_template, request, redirect
from ..models import (
    db,
    Company,
    Department,
    Employee,
    Project,
    Task,
    Role,
    KnowledgeBase,
    KBRecord,
    HREvent
)
from .forms import (
    CompanyForm,
    DepartmentForm,
    ProjectForm,
    EmployeeForm
)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

with app.app_context():
    db.create_all()
    selected_company = Company.query.first()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/departments")
def departments():
    departments = Company.query.filter(Company.id == selected_company.id).first().departments
    return render_template('departments.html', departments=departments, active_page='departments')


@app.route("/create_department", methods=["GET", "POST"])
def create_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        department = Department(name=name, description=description, company_id=selected_company.id)
        db.session.add(department)
        db.session.commit()
        return redirect('/departments')
    return render_template('create_department.html', form=form)


@app.route("/create_company", methods=["GET", "POST"])
def create_company():
    form = CompanyForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        company = Company(name=name, description=description)
        db.session.add(company)
        db.session.commit()
        return redirect('/company')
    return render_template('create_company.html', form=form)


@app.route('/company/', defaults={'company_id': None})
@app.route("/company/<int:company_id>")
def company(company_id: Optional[int]):
    global selected_company
    if company_id:
        selected_company = Company.query.filter(Company.id == company_id).first()
    if selected_company:
        selected_company = Company.query.filter(Company.id == selected_company.id).first()
    return render_template('company.html',
        company=selected_company,
        active_page='company'
    )


@app.route("/calendar")
def calendar():
    return render_template('calendar.html', active_page='calendar')


@app.route("/companies")
def companies():
    companies = Company.query.all()
    return render_template('companies.html', companies=companies, active_page='companies')


@app.route("/projects")
def projects():
    projects = Project.query.filter(Project.company_id == selected_company.id).all()
    return render_template('projects.html', projects=projects, active_page='projects')


@app.route("/create_project", methods=["GET", "POST"])
def create_project():
    form = ProjectForm()
    departments = Company.query.filter(Company.id == selected_company.id).first().departments
    form.responsible_department_id.choices = [(d.id, d.name) for d in departments]
    employees = Employee.query.filter(Employee.company_id == selected_company.id).all()
    form.employees.choices = [(employee.id, employee.name) for employee in employees]
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        responsible_department_id = form.responsible_department_id.data
        employees_ids = form.employees.data
        project = Project(
            name=name,
            description=description,
            responsible_department_id=responsible_department_id,
            company_id=selected_company.id
        )
        db.session.add(project)
        db.session.commit()
        return redirect('/projects')
    return render_template('create_project.html', form=form)


@app.route("/employees")
def employees():
    employees = Employee.query.filter(Employee.company_id == selected_company.id).all()
    return render_template('employees.html', employees=employees, active_page='employees')


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
    return render_template('create_employee.html', form=form)