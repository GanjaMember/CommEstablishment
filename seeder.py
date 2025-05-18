from flask import Flask
from datetime import date, datetime, timedelta
from app.models import db  # Импортируй свой db, если путь другой
from app.models import (  # Импортируй все твои модели правильно!
    Company, Department, Role, Employee, Project, Task,
    KnowledgeBase, KBRecord, HREvent, Chat, Message, Status, EventType
)
import random


def seed_data():
    db.drop_all()
    db.create_all()

    # --- Company ---
    company = Company(name="Techify Inc", description="IT Solutions for Business")
    db.session.add(company)

    # --- Departments ---
    departments = [
        Department(name="Development", description="Dev department", company=company),
        Department(name="HR", description="Human Resources", company=company),
        Department(name="Design", description="Design department", company=company),
        Department(name="QA", description="Quality Assurance", company=company),
    ]
    db.session.add_all(departments)

    # --- Roles ---
    roles = [
        Role(name="Backend Developer", grade="Middle", description="Backend developer"),
        Role(name="Frontend Developer", grade="Junior", description="Frontend developer"),
        Role(name="HR Manager", grade="Middle", description="HR specialist"),
        Role(name="QA Engineer", grade="Senior", description="QA engineer"),
        Role(name="UI/UX Designer", grade="Middle", description="Designer"),
    ]
    db.session.add_all(roles)

    # --- Employees ---
    employees = [
        Employee(
            surname="Ivanov",
            name="Ivan",
            patronymic="Ivanovich",
            hire_date=date(2022, 1, 15),
            birth_date=date(1995, 4, 20),
            contacts="Telegram: @ivanov, Phone: 111-222-3333",
            email="ivanov@techify.com",
            company=company,
            role=roles[0],
        ),
        Employee(
            surname="Petrova",
            name="Anna",
            patronymic=None,
            hire_date=date(2023, 3, 1),
            birth_date=date(1998, 9, 17),
            contacts="Telegram: @annap, Phone: 222-333-4444",
            email="petrova@techify.com",
            company=company,
            role=roles[2],
        ),
        Employee(
            surname="Sidorov",
            name="Petr",
            patronymic="Sergeevich",
            hire_date=date(2020, 6, 10),
            birth_date=date(1990, 2, 7),
            contacts="Telegram: @psidorov, Phone: 333-444-5555",
            email="sidorov@techify.com",
            company=company,
            role=roles[1],
        ),
        Employee(
            surname="Vasiliev",
            name="Vasiliy",
            patronymic=None,
            hire_date=date(2021, 9, 25),
            birth_date=date(1992, 7, 11),
            contacts="Telegram: @vasvas, Phone: 444-555-6666",
            email="vasiliev@techify.com",
            company=company,
            role=roles[3],
        ),
        Employee(
            surname="Smirnova",
            name="Olga",
            patronymic="Dmitrievna",
            hire_date=date(2023, 2, 18),
            birth_date=date(1997, 11, 30),
            contacts="Telegram: @osmira, Phone: 555-666-7777",
            email="smirnova@techify.com",
            company=company,
            role=roles[4],
        ),
    ]
    db.session.add_all(employees)
    db.session.flush()  # Чтобы появились id

    # Привязка сотрудников к отделам (произвольно)
    departments[0].employees.extend([employees[0], employees[2]])
    departments[1].employees.append(employees[1])
    departments[2].employees.append(employees[4])
    departments[3].employees.append(employees[3])
    employees[0].departments.append(departments[0])
    employees[1].departments.append(departments[1])
    employees[2].departments.append(departments[0])
    employees[3].departments.append(departments[3])
    employees[4].departments.append(departments[2])

    # --- Projects ---
    projects = [
        Project(
            name="Corporate Portal",
            description="Intranet web portal for employees.",
            status=Status.IN_PROGRESS,
            company=company,
            responsible_dept=departments[0],
        ),
        Project(
            name="Mobile App",
            description="Mobile application for clients.",
            status=Status.TODO,
            company=company,
            responsible_dept=departments[0],
        ),
        Project(
            name="Recruitment Automation",
            description="Automation for HR recruitment pipeline.",
            status=Status.REVIEW,
            company=company,
            responsible_dept=departments[1],
        ),
    ]
    db.session.add_all(projects)
    db.session.flush()

    # Привязка сотрудников к проектам
    projects[0].employees.extend([employees[0], employees[2], employees[4]])
    projects[1].employees.extend([employees[2], employees[3]])
    projects[2].employees.extend([employees[1]])

    # --- Tasks ---
    tasks = [
        Task(
            name="Backend API",
            description="Develop REST API for portal",
            start_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            priority=2,
            status=Status.IN_PROGRESS,
            project=projects[0],
        ),
        Task(
            name="UI Design",
            description="Create design mockups",
            start_date=date.today(),
            due_date=date.today() + timedelta(days=10),
            priority=1,
            status=Status.TODO,
            project=projects[0],
        ),
        Task(
            name="Testing",
            description="Manual and auto tests",
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
            priority=2,
            status=Status.TODO,
            project=projects[1],
        ),
        Task(
            name="HR Bot Integration",
            description="Integrate HR bot with Telegram",
            start_date=date.today(),
            due_date=date.today() + timedelta(days=12),
            priority=3,
            status=Status.REVIEW,
            project=projects[2],
        ),
    ]
    db.session.add_all(tasks)
    db.session.flush()

    # Привязка задач к сотрудникам
    tasks[0].employees.extend([employees[0], employees[2]])
    tasks[1].employees.append(employees[4])
    tasks[2].employees.append(employees[3])
    tasks[3].employees.append(employees[1])

    # --- KnowledgeBase ---
    kb = KnowledgeBase(company=company)
    db.session.add(kb)
    db.session.flush()

    kb_records = [
        KBRecord(
            kb=kb,
            creator=employees[0],
            content="How to request a vacation: Go to HR portal...",
            importance=70
        ),
        KBRecord(
            kb=kb,
            creator=employees[1],
            content="Tech stack for mobile app: Flutter, Python, PostgreSQL",
            importance=50
        ),
    ]
    db.session.add_all(kb_records)

    # --- HR Events ---
    events = [
        HREvent(
            name="Team Building 2024",
            description="Annual corporate team building event.",
            starts_at=datetime.now() + timedelta(days=15),
            ends_at=datetime.now() + timedelta(days=15, hours=5),
            type=EventType.TEAM_BUILDING,
            location="Forest Park",
            organizer=employees[1],
        ),
        HREvent(
            name="Corporate Birthday",
            description="Celebration of company's founding.",
            starts_at=datetime.now() + timedelta(days=30),
            ends_at=datetime.now() + timedelta(days=30, hours=3),
            type=EventType.CORPORATE,
            location="Office HQ",
            organizer=employees[0],
        ),
    ]
    db.session.add_all(events)
    db.session.flush()
    # Привязка сотрудников к событиям
    events[0].attendees.extend(employees)
    events[1].attendees.extend(employees[:3])

    # --- Chats ---
    chat1 = Chat(name="General")
    chat2 = Chat(name="Developers")
    db.session.add_all([chat1, chat2])
    db.session.flush()
    chat1.employees.extend(employees)
    chat2.employees.extend([employees[0], employees[2], employees[3]])

    # --- Messages ---
    messages = [
        Message(content="Welcome to the general chat!", chat=chat1, sender=employees[0]),
        Message(content="Don't forget the deadline next week.", chat=chat2, sender=employees[2]),
        Message(content="Designs are ready!", chat=chat2, sender=employees[4]),
    ]
    db.session.add_all(messages)

    db.session.commit()
    print("Database seeded!")

# Пример вызова (убедись, что это вне основного app):
# from your_seeder_file import seed_data
# seed_data()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

with app.app_context():
    seed_data()
    print("Data seeded successfully!")