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
    CompanyForm
)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

with app.app_context():
    db.create_all()
    company = Company.query.first()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/departments")
def departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments, active_page='departments')


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
    global company
    if company_id:
        company = Company.query.filter(Company.id == company_id).first()
    return render_template('company.html',
        company=company,
        active_page='company'
    )


@app.route("/calendar")
def calendar():
    return render_template('calendar.html', active_page='calendar')


@app.route("/companies")
def companies():
    companies = Company.query.all()
    return render_template('companies.html', companies=companies, active_page='companies')